"""Build open-canopy (oil-palm regime) offset labels from the SAFE landscape rasters.

The SAFE microclimate rasters (Zenodo 7893600; Jucker/Hardwick) are modelled daily
sub-canopy T_max/T_mean/VPD at 50 m over Borneo, INCLUDING oil-palm plantation and
cleared land. Forest cells are tall/high-LAI; oil-palm/cleared cells are short/low-LAI.
By sampling points across the landscape and attaching each point's REAL canopy
structure (ETH canopy height, MODIS LAI/NDVI) + ERA5 free-air macro, the low-canopy
points populate the OPEN-canopy regime that coconut needs to be in-distribution.

These are MODEL-DERIVED sub-canopy values (not raw loggers) -- documented in ADR-008.
Offsets are computed against ERA5 free-air exactly as the forest labels (ADR-006).

Usage:
  uv run python scripts/build_oilpalm_labels.py --inspect   # raster metadata + unit check
  uv run python scripts/build_oilpalm_labels.py             # full build + EE + integrate
"""
import math
import os
import sys

import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform as warp_transform

RAW = "data/raw"
PROC = "data/processed"
# Geographic extent from the Zenodo record metadata.
LAT0, LAT1 = 4.50, 5.07
LON0, LON1 = 116.75, 117.82
PERIOD0, PERIOD1 = "2013-05-01", "2015-03-01"
GRID = 34          # 34x34 candidate points over the bbox
MAX_POINTS = 320   # cap valid points sent to Earth Engine


def es(t_c):       # saturation vapour pressure kPa (Tetens)
    return 0.6108 * math.exp(17.27 * t_c / (t_c + 237.3))


def rh_from(t_c, td_c):
    a, b = 17.625, 243.04
    return 100 * math.exp(a * td_c / (b + td_c)) / math.exp(a * t_c / (b + t_c))


def open_r(name):
    return rasterio.open(os.path.join(RAW, name + ".tif"))


def band_mean_at(ds, xs, ys):
    """Period-mean per point (mean over bands, nodata->nan). xs,ys in raster CRS."""
    nod = ds.nodata
    vals = []
    for samp in ds.sample(list(zip(xs, ys))):
        a = np.asarray(samp, dtype="float64")
        if nod is not None:
            a[a == nod] = np.nan
        a[a < -1e30] = np.nan
        vals.append(np.nanmean(a) if np.isfinite(a).any() else np.nan)
    return np.array(vals)


def fix_temp(v):    # Kelvin -> Celsius if needed
    return v - 273.15 if np.nanmedian(v) > 100 else v


def fix_vpd(v, t_max):  # -> kPa. VPD must be < es(t); if not, raster is hPa -> /10.
    es_kpa = 0.6108 * np.exp(17.27 * t_max / (t_max + 237.3))
    return v / 10.0 if np.nanmedian(v) > np.nanmedian(es_kpa) else v


def main():
    inspect = "--inspect" in sys.argv
    tmax, tmean, vpd = open_r("T_max"), open_r("T_mean"), open_r("VPD_max")
    print("CRS", tmax.crs, "| bands", tmax.count, "| nodata", tmax.nodata)
    print("bounds", [round(b, 3) for b in tmax.bounds])

    # candidate grid in the raster's OWN CRS (UTM) so points land inside the
    # irregular data footprint; convert the valid ones to lon/lat for Earth Engine.
    b = tmax.bounds
    gx = np.linspace(b.left + 25, b.right - 25, GRID)
    gy = np.linspace(b.bottom + 25, b.top - 25, GRID)
    mx, my = np.meshgrid(gx, gy)
    mx, my = mx.ravel(), my.ravel()

    s_tmax = fix_temp(band_mean_at(tmax, mx, my))
    s_tmean = fix_temp(band_mean_at(tmean, mx, my))
    s_vpd = fix_vpd(band_mean_at(vpd, mx, my), s_tmax)

    valid = np.isfinite(s_tmax) & np.isfinite(s_tmean) & np.isfinite(s_vpd)
    print(f"valid points: {valid.sum()} / {len(valid)}")
    if valid.sum():
        print("sub_t_max  ", np.round(np.nanpercentile(s_tmax[valid], [5, 50, 95]), 2))
        print("sub_t_mean ", np.round(np.nanpercentile(s_tmean[valid], [5, 50, 95]), 2))
        print("sub_vpd_max", np.round(np.nanpercentile(s_vpd[valid], [5, 50, 95]), 2))
    if inspect:
        return

    idx = np.where(valid)[0]
    if len(idx) > MAX_POINTS:
        idx = idx[np.linspace(0, len(idx) - 1, MAX_POINTS).astype(int)]
    sel_lon, sel_lat = warp_transform(tmax.crs, "EPSG:4326", list(mx[idx]), list(my[idx]))
    pts = pd.DataFrame({
        "site_id": [f"OP_{i}" for i in range(len(idx))],
        "lon": np.array(sel_lon), "lat": np.array(sel_lat),
        "sub_t_max": s_tmax[idx], "sub_t_mean": s_tmean[idx], "sub_vpd": s_vpd[idx],
    })
    print(f"sending {len(pts)} points to Earth Engine")

    import ee
    ee.Initialize(project="microclimate-crop-design-sys")
    fc = ee.FeatureCollection([
        ee.Feature(ee.Geometry.Point([float(r.lon), float(r.lat)]), {"site_id": r.site_id})
        for r in pts.itertuples()])

    dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic().rename("elevation")
    slope = ee.Terrain.slope(dem).rename("slope")
    modveg = (ee.ImageCollection("MODIS/061/MOD15A2H")
              .filterDate("2013-05-01", "2015-03-01").select(["Lai_500m", "Fpar_500m"]).mean())
    static = (ee.Image("users/nlang/ETH_GlobalCanopyHeight_2020_10m_v1").rename("canopy_height")
              .addBands(dem).addBands(slope)
              .addBands(ee.Image("projects/soilgrids-isric/clay_mean").select("clay_0-5cm_mean").rename("clay"))
              .addBands(ee.Image("projects/soilgrids-isric/soc_mean").select("soc_0-5cm_mean").rename("soc"))
              .addBands(modveg.select("Lai_500m").multiply(0.1).rename("lai"))
              .addBands(modveg.select("Fpar_500m").multiply(0.01).rename("fapar"))
              .addBands(ee.ImageCollection("MODIS/061/MOD13Q1").filterDate("2013-05-01", "2015-03-01")
                        .select("NDVI").mean().multiply(0.0001).rename("ndvi")))
    print("fetching static features ...")
    sf = static.reduceRegions(fc, ee.Reducer.mean(), 250).getInfo()
    stat = {f["properties"]["site_id"]: f["properties"] for f in sf["features"]}

    era_bands = ["mean_2m_air_temperature", "maximum_2m_air_temperature",
                 "minimum_2m_air_temperature", "dewpoint_2m_temperature",
                 "u_component_of_wind_10m", "v_component_of_wind_10m", "total_precipitation"]
    img = (ee.ImageCollection("ECMWF/ERA5/DAILY").filterDate(PERIOD0, PERIOD1)
           .select(era_bands).mean())
    sol = (ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterDate(PERIOD0, PERIOD1)
           .select("surface_solar_radiation_downwards_sum").mean().rename("solar_jm2"))
    print("fetching ERA5 free-air macro (period mean) ...")
    er = img.addBands(sol).reduceRegions(fc, ee.Reducer.mean(), 1000).getInfo()
    era = {f["properties"]["site_id"]: f["properties"] for f in er["features"]}

    out = []
    for r in pts.itertuples():
        s, e = stat.get(r.site_id, {}), era.get(r.site_id, {})
        if not e or e.get("mean_2m_air_temperature") is None:
            continue
        amb_tmean = e["mean_2m_air_temperature"] - 273.15
        amb_tmax = e["maximum_2m_air_temperature"] - 273.15
        amb_tmin = e["minimum_2m_air_temperature"] - 273.15
        amb_rh = rh_from(amb_tmean, e["dewpoint_2m_temperature"] - 273.15)
        wind = math.hypot(e["u_component_of_wind_10m"], e["v_component_of_wind_10m"])
        solar = (e.get("solar_jm2") or 0.0) / 1e6
        rainfall = max(0.0, e["total_precipitation"]) * 1000 * 365
        slope_deg = s.get("slope") or 0.0
        twi = math.log(1.0 / (math.tan(math.radians(slope_deg)) + 0.01))
        amb_vpd = es(amb_tmax) * (1 - amb_rh / 100)
        out.append({
            "site_id": r.site_id,
            "t_mean": amb_tmean, "t_max": amb_tmax, "t_min": amb_tmin, "rh": amb_rh,
            "wind": wind, "solar": solar, "rainfall": rainfall,
            "lai": s.get("lai"), "canopy_height": s.get("canopy_height"),
            "ndvi": s.get("ndvi"), "fapar": s.get("fapar"),
            "elevation": s.get("elevation"), "slope": slope_deg, "twi": twi,
            "soc": s.get("soc"), "clay": s.get("clay"),
            "dT_max": r.sub_t_max - amb_tmax,
            "dT_mean": r.sub_t_mean - amb_tmean,
            "dVPD": r.sub_vpd - amb_vpd,
        })
    palm = pd.DataFrame(out).dropna(
        subset=["lai", "canopy_height", "ndvi", "elevation", "clay", "soc"])
    print(f"palm rows: {len(palm)}")
    os.makedirs(PROC, exist_ok=True)
    palm.to_parquet(os.path.join(PROC, "oilpalm_offsets.parquet"), index=False)

    # ---- integrate: forest backup + palm -> labelled_offsets.parquet (idempotent) ----
    canon = os.path.join(PROC, "labelled_offsets.parquet")
    forest_bk = os.path.join(PROC, "labelled_offsets_forest.parquet")
    if not os.path.exists(forest_bk):
        pd.read_parquet(canon).to_parquet(forest_bk, index=False)
        print("backed up forest labels -> labelled_offsets_forest.parquet")
    forest = pd.read_parquet(forest_bk)
    combined = pd.concat([forest, palm[forest.columns]], ignore_index=True)
    combined.to_parquet(canon, index=False)
    print(f"combined dataset: {len(forest)} forest + {len(palm)} palm = {len(combined)} rows")
    print(palm[["t_max", "dT_max", "dT_mean", "dVPD", "lai", "canopy_height"]].describe().round(2).T[["mean", "min", "max"]])


if __name__ == "__main__":
    main()
