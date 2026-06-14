"""Model-family benchmark under leave-one-climate-out (the honest macroclimate-transfer
test) plus an in-distribution grouped site-holdout reference.

Compares, on the same offset-prediction task and the same folds:
  ridge        linear baseline (homoscedastic interval)
  rf           random forest (per-tree spread interval)
  gp           Gaussian process (distance-aware predictive sigma -> interval)
  moe          mixture-of-experts: one expert per training regime + distance gate;
               uncertainty from expert disagreement (the 'far from all experts' signal)
  xgb          the paper's XGBoost quantile + conformal model
  hybrid       physics-prior (Ridge backbone) + XGBoost residual

The question it answers: can any model family learn canopy->microclimate offset
relationships that survive a macroclimate shift? Output: reports/benchmark_metrics.json.
NN-based variants (domain-adversarial, neural residual) are out of scope (no torch;
and a 3-regime dataset overfits them) and are discussed as future work.
"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np, pandas as pd
from agroforestry.features import engineer
from agroforestry.models_benchmark import BENCHMARK_FACTORIES as FACTORIES
from agroforestry.validation import climate_zone
from agroforestry.config import TARGETS, GROUP_COL

RNG = np.random.default_rng(0)


def _metrics(y, pred, y_tr_mean):
    med, lo, hi = pred["median"], pred["lower"], pred["upper"]
    mae = float(np.mean(np.abs(y - med)))
    base = float(np.mean(np.abs(y - y_tr_mean)))
    cov = float(np.mean((y >= lo) & (y <= hi)))
    return {"MAE": round(mae, 3), "baseline_MAE": round(base, 3),
            "skill": round(1 - mae / base, 3) if base > 0 else None,
            "coverage": round(cov, 3), "width": round(float(np.mean(hi - lo)), 3)}


def run():
    df = pd.read_parquet("data/processed/labelled_offsets.parquet")
    X, feats = engineer(df); Xv = X[feats].values
    sites = df[GROUP_COL].astype(str).values
    zones = climate_zone(sites)
    uniq = sorted(set(zones.tolist()))
    out = {"loco": {}, "in_distribution": {}}

    for tgt in TARGETS:
        y = df[tgt].values
        out["loco"][tgt] = {}; out["in_distribution"][tgt] = {}
        # in-distribution reference: hold out 20% of sites at random (grouped)
        usites = np.unique(sites); RNG.shuffle(usites)
        te_sites = set(usites[: max(1, int(0.2 * len(usites)))].tolist())
        idm = np.array([s in te_sites for s in sites])
        for name, fac in FACTORIES.items():
            t0 = time.time()
            # ---- LOCO: average over held-out climates + per-zone ----
            per_zone = {}
            for z in uniq:
                te = zones == z; tr = ~te
                m = fac().fit(Xv[tr], y[tr], feature_names=feats, groups=zones[tr])
                per_zone[z] = _metrics(y[te], m.predict(Xv[te]), np.mean(y[tr]))
            agg = {k: round(float(np.mean([per_zone[z][k] for z in per_zone if per_zone[z][k] is not None])), 3)
                   for k in ["MAE", "skill", "coverage", "width"]}
            agg["per_zone"] = per_zone; agg["seconds"] = round(time.time() - t0, 1)
            out["loco"][tgt][name] = agg
            # ---- in-distribution ----
            m2 = fac().fit(Xv[~idm], y[~idm], feature_names=feats, groups=zones[~idm])
            out["in_distribution"][tgt][name] = _metrics(y[idm], m2.predict(Xv[idm]), np.mean(y[~idm]))
            print(f"{tgt:8s} {name:7s}  LOCO skill {agg['skill']:+.2f} cov {agg['coverage']:.2f} | "
                  f"in-dist skill {out['in_distribution'][tgt][name]['skill']:+.2f} "
                  f"cov {out['in_distribution'][tgt][name]['coverage']:.2f}")

    os.makedirs("reports", exist_ok=True)
    json.dump(out, open("reports/benchmark_metrics.json", "w"), indent=2)
    print("-> reports/benchmark_metrics.json")


if __name__ == "__main__":
    run()
