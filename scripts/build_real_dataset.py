"""Assemble the real labelled-offsets dataset from SAFE labels + Earth Engine.

Inputs : data/processed/safe_label_sites.csv (sub-canopy temp/RH per plot-month)
Outputs: data/processed/labelled_offsets.parquet (config schema: RAW_FEATURES +
         TARGETS + site_id), ready for DATA_SOURCE="real".

Features: ERA5-Land monthly ambient (the offset's reference) + Sentinel/MODIS
canopy + Copernicus DEM + SoilGrids. Because the SAFE landscape (~5 km) is far
smaller than the ERA5 pixel (~9 km), ambient ERA5 is fetched once per month at the
landscape centroid and shared across plots; static features are fetched per plot.
"""
import math
import sys

import ee
import pandas as pd

ee.Initialize(project="microclimate-crop-design-sys")

labels = pd.read_csv("data/processed/safe_label_sites.csv")
labels["date"] = pd.to_datetime(labels["date"])
labels["ym"] = labels["date"].dt.strftime("%Y-%m")
plots = labels.drop_duplicates("site_id")[["site_id", "lat", "lon"]].reset_index(drop=True)
print(f"{len(labels)} label rows, {len(plots)} plots, {labels['ym'].nunique()} months")


def es(t_c):                       # saturation vapour pressure kPa (Tetens)
    return 0.6108 * math.exp(17.27 * t_c / (t_c + 237.3))


def rh_from(t_c, td_c):            # RH % from temp + dewpoint (Magnus)
    a, b = 17.625, 243.04
    return 100 * math.exp(a * td_c / (b + td_c)) / math.exp(a * t_c / (b + t_c))


# ---- static per-plot features via one reduceRegions call ----
fc = ee.FeatureCollection([
    ee.Feature(ee.Geometry.Point([float(r.lon), float(r.lat)]), {"site_id": r.site_id})
    for r in plots.itertuples()
])
dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic().rename("elevation")
slope = ee.Terrain.slope(dem).rename("slope")
modveg = (ee.ImageCollection("MODIS/061/MOD15A2H")
          .filterDate("2011-01-01", "2013-01-01").select(["Lai_500m", "Fpar_500m"]).mean())
static = (ee.Image("users/nlang/ETH_GlobalCanopyHeight_2020_10m_v1").rename("canopy_height")
          .addBands(dem).addBands(slope)
          .addBands(ee.Image("projects/soilgrids-isric/clay_mean").select("clay_0-5cm_mean").rename("clay"))
          .addBands(ee.Image("projects/soilgrids-isric/soc_mean").select("soc_0-5cm_mean").rename("soc"))
          .addBands(modveg.select("Lai_500m").multiply(0.1).rename("lai"))
          .addBands(modveg.select("Fpar_500m").multiply(0.01).rename("fapar"))
          .addBands(ee.ImageCollection("MODIS/061/MOD13Q1").filterDate("2011-01-01", "2013-01-01")
                    .select("NDVI").mean().multiply(0.0001).rename("ndvi")))
print("fetching static features ...")
sf = static.reduceRegions(fc, ee.Reducer.mean(), 250).getInfo()
stat = {f["properties"]["site_id"]: f["properties"] for f in sf["features"]}

# ---- ERA5-Land monthly ambient at the landscape centroid ----
cen = ee.Geometry.Point([float(plots.lon.mean()), float(plots.lat.mean())])
era_bands = ["temperature_2m", "temperature_2m_max", "temperature_2m_min",
             "dewpoint_temperature_2m", "u_component_of_wind_10m",
             "v_component_of_wind_10m", "surface_solar_radiation_downwards_sum",
             "total_precipitation_sum"]
era = {}
for ym in sorted(labels["ym"].unique()):
    y, m = map(int, ym.split("-"))
    start = ee.Date.fromYMD(y, m, 1)
    img = (ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
           .filterDate(start, start.advance(1, "month")).select(era_bands).mean())
    era[ym] = img.reduceRegion(ee.Reducer.mean(), cen, 1000).getInfo()
    print(f"  ERA5 {ym}: t2m={era[ym].get('temperature_2m')}")

# ---- assemble rows ----
out = []
for r in labels.itertuples():
    s = stat.get(r.site_id, {})
    e = era.get(r.ym, {})
    if not e or e.get("temperature_2m") is None:
        continue
    amb_tmean = e["temperature_2m"] - 273.15
    amb_tmax = e["temperature_2m_max"] - 273.15
    amb_tmin = e["temperature_2m_min"] - 273.15
    amb_td = e["dewpoint_temperature_2m"] - 273.15
    amb_rh = rh_from(amb_tmean, amb_td)
    wind = math.hypot(e["u_component_of_wind_10m"], e["v_component_of_wind_10m"])
    solar = e["surface_solar_radiation_downwards_sum"] / 1e6          # J/m2/day -> MJ/m2/day
    rainfall = max(0.0, e["total_precipitation_sum"]) * 1000 * 365    # m/day -> mm/yr
    slope_deg = s.get("slope") or 0.0
    twi = math.log(1.0 / (math.tan(math.radians(slope_deg)) + 0.01))   # local wetness proxy
    sub_rh = r.sub_rh if pd.notna(r.sub_rh) else amb_rh
    row = {
        "site_id": r.site_id,
        # ambient (ERA5) = the macro features
        "t_mean": amb_tmean, "t_max": amb_tmax, "t_min": amb_tmin, "rh": amb_rh,
        "wind": wind, "solar": solar, "rainfall": rainfall,
        # canopy / terrain / soil
        "lai": s.get("lai"), "canopy_height": s.get("canopy_height"),
        "ndvi": s.get("ndvi"), "fapar": s.get("fapar"),
        "elevation": s.get("elevation"), "slope": slope_deg, "twi": twi,
        "soc": s.get("soc"), "clay": s.get("clay"),
        # targets (sub-canopy minus ambient)
        "dT_max": r.sub_t_max - amb_tmax,
        "dT_mean": r.sub_t_mean - amb_tmean,
        "dVPD": es(r.sub_t_max) * (1 - sub_rh / 100) - es(amb_tmax) * (1 - amb_rh / 100),
    }
    out.append(row)

df = pd.DataFrame(out)
# drop rows with missing canopy/soil (e.g. MODIS gaps); report
before = len(df)
df = df.dropna(subset=["lai", "canopy_height", "ndvi", "elevation", "clay", "soc"])
print(f"rows: {before} -> {len(df)} after dropping feature-NaN")
df.to_parquet("data/processed/labelled_offsets.parquet", index=False)
print("wrote data/processed/labelled_offsets.parquet")
print(df[["t_max", "dT_max", "dT_mean", "dVPD", "lai", "canopy_height", "clay"]].describe().round(2).T[["mean", "min", "max"]])
