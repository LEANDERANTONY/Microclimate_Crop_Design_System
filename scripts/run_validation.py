"""Regenerate transfer-validation metrics with skill scores, for BOTH the pure
quantile model and the physics-guided hybrid.

Outputs:
  reports/loco_metrics.json   leave-one-CLIMATE-out (Borneo forest / Spain / oil-palm)
  reports/loso_metrics.json   leave-one-SITE-out (representative sample; --full for all)

The headline for the paper is LOCO: it is the honest macroclimate-transfer test and
directly compares how the pure tree model vs the extrapolating hybrid hold up when an
entire climate/canopy regime is unseen.
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np, pandas as pd
from agroforestry.features import engineer
from agroforestry.models import QuantileModel, HybridQuantileModel
from agroforestry.validation import loso, loco, climate_zone
from agroforestry.config import TARGETS, GROUP_COL

ap = argparse.ArgumentParser()
ap.add_argument("--loso-folds", type=int, default=150, help="cap LOSO folds (speed); 0 = all")
ap.add_argument("--skip-loso", action="store_true")
ap.add_argument("--skip-loco", action="store_true")
ap.add_argument("--pure-only", action="store_true", help="LOSO with the pure model only (full-run speed)")
ap.add_argument("--loso-out", default="reports/loso_metrics.json")
args = ap.parse_args()

df = pd.read_parquet("data/processed/labelled_offsets.parquet")
X, feats = engineer(df)
Xv = X[feats].values
groups = df[GROUP_COL].astype(str).values
zones = climate_zone(groups)

print(f"rows {len(df)} | sites {pd.Series(groups).nunique()} | zones {dict(pd.Series(zones).value_counts())}")

MODELS = {"pure_xgb": QuantileModel} if args.pure_only else {"pure_xgb": QuantileModel, "hybrid": HybridQuantileModel}

# ---- leave-one-climate-out (cheap, headline) ----
if not args.skip_loco:
    loco_out = {}
    for tgt in TARGETS:
        y = df[tgt].values
        loco_out[tgt] = {}
        for name, factory in MODELS.items():
            t0 = time.time()
            r = loco(Xv, y, zones, feats, site_groups=groups, model_factory=factory)
            r["seconds"] = round(time.time() - t0, 1)
            loco_out[tgt][name] = r
            pz = {z: f"{v['MAE']:.2f}(skill {v['skill_vs_baseline']*100:.0f}%)"
                  for z, v in r["per_zone"].items()}
            print(f"[LOCO] {tgt:8s} {name:9s} MAE {r['MAE']:.3f} skill {r['skill_vs_baseline']*100:5.1f}% "
                  f"cov {r['interval_coverage']:.2f} | {pz}")
    with open("reports/loco_metrics.json", "w") as f:
        json.dump(loco_out, f, indent=2)
    print("-> reports/loco_metrics.json")

# ---- leave-one-site-out (representative or full) ----
if not args.skip_loso:
    cap = None if args.loso_folds == 0 else args.loso_folds
    loso_out = {}
    for tgt in TARGETS:
        y = df[tgt].values
        loso_out[tgt] = {}
        for name, factory in MODELS.items():
            t0 = time.time()
            r = loso(Xv, y, groups, feats, max_folds=cap, model_factory=factory)
            r["seconds"] = round(time.time() - t0, 1)
            r["scope"] = "all sites" if cap is None else f"{cap}-site sample"
            loso_out[tgt][name] = r
            print(f"[LOSO] {tgt:8s} {name:9s} MAE {r['MAE']:.3f} skill {r['skill_vs_baseline']*100:5.1f}% "
                  f"R2 {r['R2_oos']:.2f} cov {r['interval_coverage']:.2f} ({r['scope']})")
    with open(args.loso_out, "w") as f:
        json.dump(loso_out, f, indent=2)
    print(f"-> {args.loso_out}")

print("done")
