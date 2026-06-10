"""Financial comparison of candidate agroforestry systems at Anaikadu:
NPV / IRR / payback over a 25-year horizon. Shows WHY steady annual cash (coconut+spice)
and a far-off timber lump are different financial animals, not comparable by annual margin.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np, pandas as pd
from agroforestry.features import engineer
from agroforestry.models import QuantileModel
from agroforestry.predict import Predictor
from agroforestry.suitability import viability
from agroforestry.finance import system_finance, DISCOUNT, HORIZON
from agroforestry.config import TARGETS, WATERLOGGING_WET

df = pd.read_parquet("data/processed/labelled_offsets.parquet")
X, feats = engineer(df)
models = {t: QuantileModel().fit(X[feats].values, df[t].values, feature_names=feats) for t in TARGETS}
predictor = Predictor(models, feats)
macro = dict(t_mean=29.3, t_max=34.3, t_min=25.9, rh=71, wind=0.4, solar=21.0, rainfall=926)
context = dict(elevation=23, slope=1.0, twi=4.0, soc=328, clay=355)


def gd(species, lai, intercrop):
    if intercrop is None:
        return 100, 0
    micro = predictor.predict_micro({"species": species, "lai": lai, "wb_height": 10, "wb_porosity": 0.45},
                                    macro, context)
    v = viability(intercrop, micro, rain_mm_day=0.0, waterlogging=WATERLOGGING_WET)
    return v["growth"], v["disease_risk"]


systems = [
    ("Coconut only",        "coconut_wide", 1.0, None),
    ("Coconut + Nutmeg",    "coconut_wide", 1.0, "Nutmeg"),
    ("Coconut + Pepper",    "coconut_wide", 1.0, "Black pepper"),
    ("Coconut + Banana",    "coconut_wide", 1.0, "Banana"),
    ("Mahogany + Nutmeg",   "mahogany",     0.5, "Nutmeg"),
    ("Teak block (timber)", "teak_leaf",    2.0, None),
]

print(f"Anaikadu | discount {DISCOUNT:.0%} real | horizon {HORIZON} yr | Rs/acre\n")
print(f"{'system':22s} {'NPV':>10s} {'IRR':>7s} {'payback':>8s}   {'NPV(over)':>10s} {'NPV(crop)':>10s}")
results = {}
for label, sp, lai, ic in systems:
    g, d = gd(sp, lai, ic)
    f = system_finance(sp, ic, g, d)
    results[label] = f
    irr = f"{f['irr']*100:.0f}%" if f["irr"] is not None else "  n/a"
    pb = f"{f['payback_yr']}y" if f["payback_yr"] else " never"
    print(f"{label:22s} {f['npv']/1000:9,.0f}k {irr:>7s} {pb:>8s}   {f['npv_overstorey']/1000:9,.0f}k {f['npv_intercrop']/1000:9,.0f}k")

print("\n-- cash-flow shape (Rs/acre, years 1-12 then 15,18,20,25) --")
yrs = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 18, 20, 25]
print(f"{'year':22s}" + "".join(f"{y:>7d}" for y in yrs))
for label in ["Coconut + Nutmeg", "Mahogany + Nutmeg", "Teak block (timber)"]:
    cf = results[label]["cashflow"]
    print(f"{label:22s}" + "".join(f"{cf[y-1]/1000:>7.0f}" for y in yrs))
print("\n(k = thousand Rs). Note timber shows years of small outflow then a big harvest spike")
print("-> high NPV on paper but late payback and all risk concentrated at harvest (LOW conf).")

# coconut is highly sensitive to the (volatile) nut price -- show it
import agroforestry.economics as ec
print("\n-- coconut economics is NUT-PRICE sensitive (coconut+nutmeg NPV) --")
orig = ec.OVERSTOREY_ECON["coconut"]["price_per_nut"]
g, d = gd("coconut_wide", 1.0, "Nutmeg")
for pn in [9.5, 12, 15, 18]:
    ec.OVERSTOREY_ECON["coconut"]["price_per_nut"] = (pn, pn)
    f = system_finance("coconut_wide", "Nutmeg", g, d)
    pb = f"{f['payback_yr']}y" if f["payback_yr"] else "never"
    irr = f"{f['irr']*100:.0f}%" if f["irr"] is not None else "n/a"
    print(f"  Rs {pn:>4}/nut -> NPV {f['npv']/1000:>7,.0f}k  IRR {irr:>4}  payback {pb}")
ec.OVERSTOREY_ECON["coconut"]["price_per_nut"] = orig
print("  (2024 TN nut prices spiked to ~Rs 13-15/nut; the system flips clearly positive there.)")
