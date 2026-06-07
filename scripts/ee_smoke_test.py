"""Smoke-test the Earth Engine data sources used by fetch_earth_engine.py.

Verifies each asset id / band resolves and returns a value at a sample point,
so we catch catalog drift before a full fetch. Run:
    uv run python scripts/ee_smoke_test.py
"""
import ee

ee.Initialize(project="microclimate-crop-design-sys")

pt = ee.Geometry.Point([79.32, 10.43])      # Pattukkottai
d0, d1 = "2023-06-01", "2023-06-30"


def check(name, fn):
    try:
        print(f"OK   {name}: {fn()}")
    except Exception as e:
        print(f"FAIL {name}: {str(e)[:140]}")


check("ERA5_LAND temp_2m", lambda: ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
      .filterDate(d0, d1).select("temperature_2m").mean()
      .reduceRegion(ee.Reducer.mean(), pt, 1000).getInfo())

check("MODIS LAI/FPAR", lambda: ee.ImageCollection("MODIS/061/MOD15A2H")
      .filterDate(d0, d1).select(["Lai_500m", "Fpar_500m"]).mean()
      .reduceRegion(ee.Reducer.mean(), pt, 500).getInfo())

check("MODIS NDVI", lambda: ee.ImageCollection("MODIS/061/MOD13Q1")
      .filterDate("2023-05-01", d1).select("NDVI").mean()
      .reduceRegion(ee.Reducer.mean(), pt, 250).getInfo())

check("ETH canopy height", lambda: ee.Image("users/nlang/ETH_GlobalCanopyHeight_2020_10m_v1")
      .reduceRegion(ee.Reducer.mean(), pt, 10).getInfo())

check("Copernicus DEM GLO30", lambda: ee.ImageCollection("COPERNICUS/DEM/GLO30")
      .select("DEM").mosaic().reduceRegion(ee.Reducer.mean(), pt, 30).getInfo())

check("SoilGrids clay", lambda: ee.Image("projects/soilgrids-isric/clay_mean")
      .select("clay_0-5cm_mean").reduceRegion(ee.Reducer.mean(), pt, 250).getInfo())

check("Sentinel-2 SR (cloud-masked NDVI source)", lambda: ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
      .filterDate(d0, d1).filterBounds(pt).first().select("B8", "B4")
      .reduceRegion(ee.Reducer.mean(), pt, 10).getInfo())
