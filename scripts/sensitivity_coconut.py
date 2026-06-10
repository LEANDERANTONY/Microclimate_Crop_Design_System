"""Sensitivity test: does the UNCERTAIN coconut temperature offset change the
intercrop ranking at Anaikadu?

The model flags the under-coconut temperature offset as LOW confidence (extrapolation).
Everything else under coconut -- shade (Beer-Lambert), wind (shelterbelt), humidity --
is physics/known. So we hold those fixed and sweep ONLY the temperature across its
plausible band, then watch whether the top intercrops stay on top. If the ranking is
stable, the pending data does not change the decision and we can act now.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pandas as pd
from agroforestry.features import engineer
from agroforestry.models import QuantileModel
from agroforestry.predict import Predictor
from agroforestry.suitability import viability
from agroforestry.config import TARGETS, WATERLOGGING_WET

# ---- train offset models on the real labelled data ----
df = pd.read_parquet("data/processed/labelled_offsets.parquet")
X, feats = engineer(df)
models = {t: QuantileModel().fit(X[feats].values, df[t].values, feature_names=feats) for t in TARGETS}
predictor = Predictor(models, feats)

# ---- real Anaikadu inputs (ERA5 2019 + SoilGrids, from run_site.py) ----
macro = dict(t_mean=29.3, t_max=34.3, t_min=25.9, rh=71, wind=0.4, solar=21.0, rainfall=926)
context = dict(elevation=23, slope=1.0, twi=4.0, soc=328, clay=355)
coconut = {"species": "coconut_wide", "lai": 1.0, "wb_height": 10, "wb_porosity": 0.45}

micro = predictor.predict_micro(coconut, macro, context)
base_tmax = micro["t_max"]
lo, hi = micro["intervals"]["dT_max"]
print(f"Coconut-wide @ Anaikadu: base under-canopy t_max {base_tmax:.1f}C, shade {micro['shade']:.0f}%, "
      f"rh {micro['rh']:.0f}%  (offset confidence: {micro['offset_confidence']})")
print(f"  model dT_max 80% band: [{lo:+.1f}, {hi:+.1f}] C  -> t_max plausibly {base_tmax+ (lo-(lo+hi)/2):.1f}..{base_tmax+(hi-(lo+hi)/2):.1f}\n")

CROPS = ["Black pepper", "Cocoa", "Nutmeg", "Vanilla", "Ginger", "Banana", "Pomegranate"]
# sweep temperature deltas around the model's prediction (cool extrapolation -> hot extrapolation)
scenarios = {"cooler -3C": -3, "cooler -1.5C": -1.5, "model median": 0.0,
             "warmer +1.5C": 1.5, "warmer +3C": 3.0}

rankings = {}
for label, d in scenarios.items():
    m = {**micro, "t_max": micro["t_max"] + d, "t_mean": micro["t_mean"] + d}
    scores = []
    for crop in CROPS:
        v = viability(crop, m, rain_mm_day=0.0, waterlogging=WATERLOGGING_WET)
        scores.append((crop, v["viability"], v["growth"], v["growth_limiting"]))
    scores.sort(key=lambda x: -x[1])
    rankings[label] = scores
    top = ", ".join(f"{c}({v})" for c, v, *_ in scores[:4])
    print(f"{label:14s} (t_max {m['t_max']:.1f}C):  {top}")

# stability check: does the top-3 SET stay the same across scenarios?
top3_sets = [frozenset(c for c, *_ in sc[:3]) for sc in rankings.values()]
stable = all(s == top3_sets[0] for s in top3_sets)
print("\nTop-3 intercrop SET stable across the whole temperature band?  ", "YES" if stable else "NO")
order_sets = [tuple(c for c, *_ in sc[:3]) for sc in rankings.values()]
order_stable = all(o == order_sets[0] for o in order_sets)
print("Exact top-3 ORDER identical across the band?                    ", "YES" if order_stable else "NO")
print("\nInterpretation: if the SET is stable, the data gap does not change WHICH crops")
print("are best under coconut -- only their absolute scores -- so the decision is robust now.")
