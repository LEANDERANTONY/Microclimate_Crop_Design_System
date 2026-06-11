"""Per-climate (Mondrian) + few-shot conformal recalibration under leave-one-climate-out.

LOCO showed interval coverage collapses out-of-climate (calibrated on the training
climates, applied to an unseen one). Standard conformal cannot fix this without data
from the target regime. This experiment quantifies the honest fix: how many
calibration points from the held-out climate are needed to RESTORE ~0.8 coverage?

For each held-out climate we train the quantile model on the other climates, then
recalibrate the conformal width on k points sampled from the held-out climate
(k = 0, 5, 10, 25, 50, 100) and measure coverage + width on the remaining held-out
points. k=0 reproduces the LOCO collapse; the curve in k is the value-of-local-data
result that motivates the on-plot logger. Averaged over seeds.

Output: reports/mondrian_metrics.json
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np, pandas as pd
from agroforestry.features import engineer
from agroforestry.models import QuantileModel
from agroforestry.validation import climate_zone
from agroforestry.config import TARGETS, GROUP_COL

KS = [0, 5, 10, 25, 50, 100]
SEEDS = [0, 1, 2, 3, 4]
TARGET_COV = 0.8

df = pd.read_parquet("data/processed/labelled_offsets.parquet")
X, feats = engineer(df)
Xv = X[feats].values
sites = df[GROUP_COL].astype(str).values
zones = climate_zone(sites)
uniq = sorted(set(zones.tolist()))
zlab = {"borneo_forest": "Borneo humid forest", "med_spain": "Mediterranean Spain",
        "oilpalm_open": "Borneo oil-palm (open)"}

out = {}
for tgt in TARGETS:
    y = df[tgt].values
    out[tgt] = {}
    for z in uniq:
        te = np.where(zones == z)[0]
        tr = np.where(zones != z)[0]
        if len(te) < max(KS) + 20 or len(tr) == 0:
            continue
        # train on the other climates; group-aware base conformal (k=0 = LOCO collapse)
        qm = QuantileModel().fit(Xv[tr], y[tr], feature_names=feats, groups=sites[tr])
        lo_raw = qm.models[qm.quantiles[0]].predict(Xv[te])
        hi_raw = qm.models[qm.quantiles[-1]].predict(Xv[te])
        base_off = qm.conformal_offset
        yte = y[te]
        per_k = {}
        for k in KS:
            covs, widths = [], []
            for seed in SEEDS:
                rng = np.random.default_rng(seed)
                if k == 0:
                    off = base_off
                    ev = np.arange(len(te))
                else:
                    cal = rng.choice(len(te), size=k, replace=False)
                    scores = np.maximum(lo_raw[cal] - yte[cal], yte[cal] - hi_raw[cal])
                    off = float(np.quantile(scores, TARGET_COV, method="higher"))
                    ev = np.setdiff1d(np.arange(len(te)), cal)
                lo = lo_raw[ev] - off
                hi = hi_raw[ev] + off
                covs.append(float(np.mean((yte[ev] >= lo) & (yte[ev] <= hi))))
                widths.append(float(np.mean(hi - lo)))
            per_k[k] = {"coverage": round(float(np.mean(covs)), 3),
                        "width": round(float(np.mean(widths)), 3)}
        out[tgt][z] = {"label": zlab.get(z, z), "n_test": int(len(te)), "by_k": per_k}
        cov0 = per_k[0]["coverage"]
        cov25 = per_k[25]["coverage"]
        print(f"{tgt:8s} {z:14s} cov@k0 {cov0:.2f} -> cov@k25 {cov25:.2f} (target {TARGET_COV})")

os.makedirs("reports", exist_ok=True)
with open("reports/mondrian_metrics.json", "w") as f:
    json.dump({"target_coverage": TARGET_COV, "ks": KS, "seeds": SEEDS, "results": out}, f, indent=2)
print("-> reports/mondrian_metrics.json")
