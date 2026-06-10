"""Cross-validation for the offset models -- the right tests for transferability.

Two complementary protocols:

* **loso** -- leave-one-SITE-out. Holds out an entire site each fold; measures
  "does the offset learned on these sites transfer to an unseen one." Random
  splits would let the model memorise a site and flatter the metrics.
* **loco** -- leave-one-CLIMATE-out. Holds out an entire macroclimate / canopy
  regime (Borneo humid forest, Mediterranean Spain, Borneo oil-palm open canopy).
  This is the honest test of the project's actual claim -- transfer ACROSS
  macroclimates -- and the one a reviewer cares about most, because the target
  application (semi-arid Tamil Nadu) is a different regime again.

Every metric is reported against a **naive baseline** (predict the training-mean
offset). The skill score = 1 - MAE_model / MAE_baseline answers "is the model
actually learning structure, or just recovering a near-constant offset?" -- the
first question any reviewer asks. R2 is reported for the same reason.
"""
import numpy as np
from sklearn.model_selection import LeaveOneGroupOut
from agroforestry.models import QuantileModel


# ---------------------------------------------------------------------------
# Climate / canopy regime tagging (derived from site_id prefixes)
# ---------------------------------------------------------------------------
def climate_zone(site_ids):
    """Map each site_id to its macroclimate / canopy regime.

    LJ*  -> Mediterranean Spain (La Jarda)
    OP*  -> Borneo oil-palm OPEN canopy (the open-canopy regime; warming offsets)
    else -> Borneo humid closed/logged forest (SAFE blocks A-F, LF, LFE, VJR, OG)
    """
    out = []
    for s in np.asarray(site_ids).astype(str):
        if s.startswith("LJ"):
            out.append("med_spain")
        elif s.startswith("OP"):
            out.append("oilpalm_open")
        else:
            out.append("borneo_forest")
    return np.array(out)


def _metrics(y, pred, y_train_mean):
    """Point + interval + skill metrics for one fold.

    y_train_mean is the naive baseline prediction (mean offset of the training
    fold) -- skill is measured against it so a low MAE on a low-variance target
    is not mistaken for a strong model.
    """
    med, lo, hi = pred["median"], pred["lower"], pred["upper"]
    mae = float(np.mean(np.abs(y - med)))
    rmse = float(np.sqrt(np.mean((y - med) ** 2)))
    coverage = float(np.mean((y >= lo) & (y <= hi)))
    width = float(np.mean(hi - lo))
    mae_base = float(np.mean(np.abs(y - y_train_mean)))
    # SS residual vs total (about the training mean) -> out-of-sample R2
    ss_res = float(np.sum((y - med) ** 2))
    ss_tot = float(np.sum((y - y_train_mean) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return mae, rmse, coverage, width, mae_base, r2


def _aggregate(maes, rmses, covs, widths, base_maes, r2s, n_folds):
    maes = np.asarray(maes); base_maes = np.asarray(base_maes)
    mae_mean = float(maes.mean())
    base_mean = float(base_maes.mean())
    return {
        "folds": int(n_folds),
        "MAE": mae_mean,
        "MAE_std": float(maes.std()),
        "MAE_p10": float(np.percentile(maes, 10)),
        "MAE_p50": float(np.percentile(maes, 50)),
        "MAE_p90": float(np.percentile(maes, 90)),
        "RMSE": float(np.mean(rmses)),
        "interval_coverage": float(np.mean(covs)),
        "interval_width": float(np.mean(widths)),
        "baseline_MAE": base_mean,                       # predict train-mean offset
        "skill_vs_baseline": float(1.0 - mae_mean / base_mean) if base_mean > 0 else float("nan"),
        "R2_oos": float(np.mean(r2s)),                   # out-of-sample R2 (mean over folds)
    }


def _run_folds(X, y, folds, feature_names, groups, model_factory):
    maes, rmses, covs, widths, base_maes, r2s = [], [], [], [], [], []
    for tr, te in folds:
        qm = model_factory().fit(X[tr], y[tr], feature_names=feature_names,
                                 groups=groups[tr] if groups is not None else None)
        pred = qm.predict(X[te])
        y_train_mean = np.full(len(te), float(np.mean(y[tr])))
        mae, rmse, cov, width, mae_base, r2 = _metrics(y[te], pred, y_train_mean)
        maes.append(mae); rmses.append(rmse); covs.append(cov)
        widths.append(width); base_maes.append(mae_base); r2s.append(r2)
    return maes, rmses, covs, widths, base_maes, r2s


def loso(X, y, groups, feature_names, max_folds=None, model_factory=QuantileModel):
    """Leave-one-site-out CV. Set max_folds to subsample folds for speed; leave
    None for the full (uncapped) run used in the paper. model_factory lets the
    hybrid model be swapped in for the pure quantile model."""
    X = np.asarray(X); y = np.asarray(y); groups = np.asarray(groups)
    folds = list(LeaveOneGroupOut().split(X, y, groups))
    if max_folds:
        folds = folds[:max_folds]
    res = _run_folds(X, y, folds, feature_names, groups, model_factory)
    return _aggregate(*res, n_folds=len(folds))


def loco(X, y, zones, feature_names, site_groups=None, model_factory=QuantileModel):
    """Leave-one-climate-out CV. `zones` is the per-row regime label (see
    climate_zone). Returns aggregate + a per-held-out-zone breakdown, the honest
    macroclimate-transfer test. site_groups (if given) drives the conformal
    calibration split inside each fold."""
    X = np.asarray(X); y = np.asarray(y); zones = np.asarray(zones)
    uniq = sorted(set(zones.tolist()))
    per_zone = {}
    maes, rmses, covs, widths, base_maes, r2s = [], [], [], [], [], []
    for z in uniq:
        te = np.where(zones == z)[0]
        tr = np.where(zones != z)[0]
        if len(tr) == 0 or len(te) == 0:
            continue
        grp = site_groups[tr] if site_groups is not None else None
        qm = model_factory().fit(X[tr], y[tr], feature_names=feature_names, groups=grp)
        pred = qm.predict(X[te])
        y_train_mean = np.full(len(te), float(np.mean(y[tr])))
        mae, rmse, cov, width, mae_base, r2 = _metrics(y[te], pred, y_train_mean)
        maes.append(mae); rmses.append(rmse); covs.append(cov)
        widths.append(width); base_maes.append(mae_base); r2s.append(r2)
        per_zone[z] = {
            "held_out": z, "n_test": int(len(te)), "n_train": int(len(tr)),
            "MAE": mae, "RMSE": rmse, "interval_coverage": cov,
            "interval_width": width, "baseline_MAE": mae_base,
            "skill_vs_baseline": float(1.0 - mae / mae_base) if mae_base > 0 else float("nan"),
            "R2_oos": r2,
        }
    agg = _aggregate(maes, rmses, covs, widths, base_maes, r2s, n_folds=len(per_zone))
    agg["per_zone"] = per_zone
    return agg
