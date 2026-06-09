"""End-to-end run for the REAL Pattukkottai site (option 3).

Trains the offset models on the real labelled data, fetches Pattukkottai's REAL,
correctly-scaled features from Earth Engine (ERA5 macro, SoilGrids g/kg, DEM), then
predicts under-canopy microclimate and scores crop suitability for candidate
overstoreys -- with honest OOD/confidence flags (coconut = extrapolation for the
ML offset; physics light/wind stay HIGH).

Run:  uv run python scripts/pattukkottai_run.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import ee
import pandas as pd

from agroforestry.features import engineer
from agroforestry.models import QuantileModel
from agroforestry.predict import Predictor
from agroforestry.suitability import viability
from agroforestry.config import TARGETS, WATERLOGGING_WET

ee.Initialize(project="microclimate-crop-design-sys")
PT = ee.Geometry.Point([79.32, 10.43])            # Pattukkottai
YR0, YR1 = "2019-01-01", "2020-01-01"


def rh_from(t, td):
    a, b = 17.625, 243.04
    return 100 * math.exp(a * td / (b + td)) / math.exp(a * t / (b + t))


# ---- 1. train offset models on the real labelled data ----
df = pd.read_parquet("data/processed/labelled_offsets.parquet")
X, feats = engineer(df)
models = {t: QuantileModel().fit(X[feats].values, df[t].values, feature_names=feats)
          for t in TARGETS}
predictor = Predictor(models, feats)
print(f"trained on {len(df)} real rows ({df.shape[0]} site-months)")

# ---- 2. fetch REAL Pattukkottai features (correct scales) ----
era = (ee.ImageCollection("ECMWF/ERA5/DAILY").filterDate(YR0, YR1)
       .select(["mean_2m_air_temperature", "maximum_2m_air_temperature",
                "minimum_2m_air_temperature", "dewpoint_2m_temperature",
                "u_component_of_wind_10m", "v_component_of_wind_10m",
                "total_precipitation"]).mean()
       .reduceRegion(ee.Reducer.mean(), PT, 1000).getInfo())
solar = (ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterDate(YR0, YR1)
         .select("surface_solar_radiation_downwards_sum").mean()
         .reduceRegion(ee.Reducer.mean(), PT, 1000).getInfo()["surface_solar_radiation_downwards_sum"])
dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic().rename("elevation")
terr = (dem.addBands(ee.Terrain.slope(dem).rename("slope"))
        .reduceRegion(ee.Reducer.mean(), PT, 30).getInfo())
clay = ee.Image("projects/soilgrids-isric/clay_mean").select("clay_0-5cm_mean").reduceRegion(
    ee.Reducer.mean(), PT, 250).getInfo()["clay_0-5cm_mean"]
soc = ee.Image("projects/soilgrids-isric/soc_mean").select("soc_0-5cm_mean").reduceRegion(
    ee.Reducer.mean(), PT, 250).getInfo()["soc_0-5cm_mean"]

t_mean = era["mean_2m_air_temperature"] - 273.15
t_max = era["maximum_2m_air_temperature"] - 273.15
t_min = era["minimum_2m_air_temperature"] - 273.15
rh = rh_from(t_mean, era["dewpoint_2m_temperature"] - 273.15)
wind = math.hypot(era["u_component_of_wind_10m"], era["v_component_of_wind_10m"])
slope = terr.get("slope") or 0.0
macro = dict(t_mean=t_mean, t_max=t_max, t_min=t_min, rh=rh, wind=wind,
             solar=solar / 1e6, rainfall=max(0.0, era["total_precipitation"]) * 1000 * 365)
context = dict(elevation=terr.get("elevation"), slope=slope,
               twi=math.log(1.0 / (math.tan(math.radians(slope)) + 0.01)),
               soc=soc, clay=clay)                # clay/soc in g/kg, matching training

print("\n=== REAL Pattukkottai macroclimate (ERA5 2019) ===")
print(f"  t_mean {macro['t_mean']:.1f}C  t_max {macro['t_max']:.1f}C  t_min {macro['t_min']:.1f}C  "
      f"RH {macro['rh']:.0f}%  wind {macro['wind']:.1f} m/s  rain {macro['rainfall']:.0f} mm/yr")
print(f"  soil: clay {context['clay']:.0f} g/kg  soc {context['soc']:.0f} g/kg  "
      f"elev {context['elevation']:.0f} m  (real scales, matching training)")

# ---- 3. predict microclimate under candidate overstoreys ----
print("\n=== Under-canopy microclimate at Pattukkottai (per overstorey) ===")
designs = {
    "Open field":     {"species": "none",          "lai": 0.0, "wb_height": 10, "wb_porosity": 0.45},
    "Coconut wide":   {"species": "coconut_wide",   "lai": 1.0, "wb_height": 10, "wb_porosity": 0.45},
    "Coconut close":  {"species": "coconut_close",  "lai": 1.7, "wb_height": 10, "wb_porosity": 0.45},
    "Silver oak":     {"species": "silver_oak",     "lai": 1.3, "wb_height": 10, "wb_porosity": 0.45},
}
micros = {}
for name, d in designs.items():
    m = predictor.predict_micro(d, macro, context)
    micros[name] = m
    print(f"  {name:13s} shade {m['shade']:3.0f}%  t_max {m['t_max']:4.1f}C  rh {m['rh']:3.0f}%  "
          f"wind {m['wind']:.1f}  | offset {m['offset_confidence']} (ood {m['ood_score']})")
print("  NOTE: light/wind = physics (HIGH conf); temp/VPD offset flagged where coconut is")
print("        out-of-distribution vs the forest training data (ADR-007).")

# ---- 4. crop suitability UNDER COCONUT (the intercrop decision) ----
print("\n=== Intercrop viability UNDER coconut (wide) at Pattukkottai ===")
mc = micros["Coconut wide"]
for crop in ["Black pepper", "Cocoa", "Nutmeg", "Vanilla", "Ginger", "Banana", "Pomegranate"]:
    v = viability(crop, mc, rain_mm_day=0.0, waterlogging=WATERLOGGING_WET)
    print(f"  {crop:13s} growth {v['growth']:3d}  disease {v['disease_risk']:3d} "
          f"({v['worst_disease']})  => VIABILITY {v['viability']:3d}/100  (limiting {v['growth_limiting']})")
print("  (shade/wind from physics are the trustworthy levers here; temp offset is")
print("   extrapolation under coconut until palm-canopy data / local sensors land.)")
