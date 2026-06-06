"""Earth Engine feature extraction for microclimate label sites.

ONE-TIME PREREQS (you must do these -- they need YOUR Google account):
  1. Sign up for Google Earth Engine (free for research): https://earthengine.google.com
  2. Create / pick a Google Cloud project with the Earth Engine API enabled.
  3. uv add earthengine-api          # adds the GEE client to this project
  4. uv run earthengine authenticate # opens a browser, stores a token

INPUT  : CSV with columns site_id, lat, lon, date (YYYY-MM-DD)
OUTPUT : parquet of the config.RAW_FEATURES predictors at each site/date, to be
         merged with the offset targets (see src/agroforestry/data/load.py).

NOTE: asset ids / band names below are the standard public collections but should
be VERIFIED against the live GEE catalog when you run this -- ids occasionally
change. This is a template, not a guaranteed-current script.
"""
import argparse
import pandas as pd


def _init(project: str | None = None):
    import ee
    ee.Initialize(project=project) if project else ee.Initialize()
    return ee


def extract(sites: pd.DataFrame, project: str | None = None) -> pd.DataFrame:
    ee = _init(project)
    rows = []
    for _, s in sites.iterrows():
        pt = ee.Geometry.Point([float(s.lon), float(s.lat)])
        date = ee.Date(str(s.date))
        win_start = date.advance(-15, "day")

        # macroclimate -- ERA5-Land daily aggregate (ambient drivers)
        era = (ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
               .filterDate(win_start, date.advance(1, "day")).mean())
        # canopy -- MODIS LAI/FPAR (swap for Sentinel-2 SNAP LAI for 10-20 m)
        lai = (ee.ImageCollection("MODIS/061/MOD15A2H")
               .filterDate(win_start, date.advance(1, "day"))
               .select(["Lai_500m", "Fpar_500m"]).mean())
        ndvi = (ee.ImageCollection("MODIS/061/MOD13Q1")
                .filterDate(date.advance(-30, "day"), date).select("NDVI").mean())
        height = ee.Image("users/nlang/ETH_GlobalCanopyHeight_2020_10m_v1")
        dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic()
        slope = ee.Terrain.slope(dem)
        soc = ee.Image("projects/soilgrids-isric/soc_mean").select("soc_0-5cm_mean")
        clay = ee.Image("projects/soilgrids-isric/clay_mean").select("clay_0-5cm_mean")

        img = (era.addBands(lai).addBands(ndvi).addBands(height)
               .addBands(dem).addBands(slope).addBands(soc).addBands(clay))
        vals = img.reduceRegion(ee.Reducer.mean(), pt, scale=500).getInfo()
        vals["site_id"] = s.site_id
        rows.append(vals)
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", required=True, help="CSV: site_id,lat,lon,date")
    ap.add_argument("--out", default="data/processed/site_features.parquet")
    ap.add_argument("--project", default=None, help="GEE cloud project id")
    args = ap.parse_args()
    sites = pd.read_csv(args.sites)
    feats = extract(sites, project=args.project)
    feats.to_parquet(args.out)
    print(f"wrote {len(feats)} rows -> {args.out}")


if __name__ == "__main__":
    main()
