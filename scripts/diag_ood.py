"""Decompose the coconut OOD score: which features are out-of-range, and is the
CANOPY axis now in-distribution after adding the palm regime?"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np, pandas as pd
from agroforestry.features import engineer
from agroforestry.models import QuantileModel
from agroforestry.predict import build_feature_row
from agroforestry.config import TARGETS

df = pd.read_parquet("data/processed/labelled_offsets.parquet")
X, feats = engineer(df)
m = QuantileModel().fit(X[feats].values, df["dT_max"].values, feature_names=feats)
lo, hi = m.feat_lo, m.feat_hi

def report(label, design, macro, context):
    Xr, _ = engineer(build_feature_row(design, macro, context))
    xv = Xr[feats].values[0]
    out = (xv < lo) | (xv > hi)
    print(f"\n{label}: OOD = {out.mean():.2f}  ({out.sum()}/{len(feats)} features out)")
    for i, f in enumerate(feats):
        if out[i]:
            print(f"   OUT {f:16s} {xv[i]:8.2f}  train[{lo[i]:.2f}, {hi[i]:.2f}]")

coco = {"species": "coconut_wide", "lai": 1.0, "wb_height": 10, "wb_porosity": 0.45}
patt_macro = dict(t_mean=29.3, t_max=34.3, t_min=25.9, rh=71, wind=0.4, solar=21.0, rainfall=926)
patt_ctx = dict(elevation=23, slope=1.0, twi=4.0, soc=310, clay=361)
report("Coconut @ Pattukkottai (semi-arid TN)", coco, patt_macro, patt_ctx)

# Borneo-like macro/soil, same coconut canopy -> isolates the canopy axis
born_macro = dict(t_mean=26.5, t_max=30.0, t_min=23.0, rh=88, wind=1.0, solar=18.0, rainfall=2600)
born_ctx = dict(elevation=200, slope=8.0, twi=2.5, soc=60, clay=400)
report("Coconut @ Borneo-like macro/soil", coco, born_macro, born_ctx)
