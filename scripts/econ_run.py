"""Economics demo at the real Anaikadu site: overstorey options (coconut vs timber)
and intercrop margins under coconut. Layer 4-5 on top of the existing viability."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pandas as pd
from agroforestry.features import engineer
from agroforestry.models import QuantileModel
from agroforestry.predict import Predictor
from agroforestry.suitability import viability
from agroforestry.economics import overstorey_margin, crop_margin, system_margin
from agroforestry.config import TARGETS, WATERLOGGING_WET

df = pd.read_parquet("data/processed/labelled_offsets.parquet")
X, feats = engineer(df)
models = {t: QuantileModel().fit(X[feats].values, df[t].values, feature_names=feats) for t in TARGETS}
predictor = Predictor(models, feats)

macro = dict(t_mean=29.3, t_max=34.3, t_min=25.9, rh=71, wind=0.4, solar=21.0, rainfall=926)
context = dict(elevation=23, slope=1.0, twi=4.0, soc=328, clay=355)


def money(x):
    return f"Rs {x/1000:,.0f}k"


print("=== Overstorey income at Anaikadu (Rs/acre/yr; timber annualised over rotation) ===")
for sp, label in [("coconut_wide", "Coconut (main crop)"), ("teak_leaf", "Teak"),
                  ("mahogany", "Mahogany"), ("silver_oak", "Silver oak"), ("none", "Open field")]:
    o = overstorey_margin(sp)
    print(f"  {label:20s} expected {money(o['expected']):>10s}  (downside {money(o['downside']):>9s})  | {o['note']}")
print("  NOTE: timber values are LOW confidence (farm prices vary widely); coconut nut price is volatile.\n")

print("=== Intercrop system margin UNDER coconut (wide) at Anaikadu ===")
coconut = {"species": "coconut_wide", "lai": 1.0, "wb_height": 10, "wb_porosity": 0.45}
micro = predictor.predict_micro(coconut, macro, context)
rows = []
for crop in ["Black pepper", "Nutmeg", "Cocoa", "Vanilla", "Ginger", "Banana", "Pomegranate"]:
    v = viability(crop, micro, rain_mm_day=0.0, waterlogging=WATERLOGGING_WET)
    s = system_margin("coconut_wide", crop, v["growth"], v["disease_risk"])
    rows.append((crop, v["growth"], v["disease_risk"], s["intercrop"]["expected"],
                 s["intercrop"]["downside"], s["system_expected"], s["intercrop"]["risk"]))
rows.sort(key=lambda r: -r[5])
print(f"  {'crop':13s} {'growth':>6s} {'disease':>7s} {'intercrop_exp':>13s} {'downside':>9s} {'SYSTEM_exp':>11s}  risk")
for c, g, d, ie, idn, se, rk in rows:
    print(f"  {c:13s} {g:6d} {d:7d} {money(ie):>13s} {money(idn):>9s} {money(se):>11s}  {rk}")
print("\n  system_exp = coconut overstorey income + intercrop margin. Note the temp offset")
print("  under coconut is LOW confidence (sensitivity: shortlist robust, level uncertain),")
print("  so intercrop margins here are indicative -- the ranking is the trustworthy signal.")
