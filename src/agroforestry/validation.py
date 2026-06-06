"""Leave-one-site-out cross-validation -- the right test for transferability.

Random splits would let the model memorise a site and flatter the metrics.
LOSO holds out an entire site each fold, directly measuring "does the offset
learned on these sites transfer to an unseen one" -- the project's core claim.
"""
import numpy as np
from sklearn.model_selection import LeaveOneGroupOut
from agroforestry.models import QuantileModel


def _metrics(y, pred):
    med, lo, hi = pred["median"], pred["lower"], pred["upper"]
    mae = float(np.mean(np.abs(y - med)))
    rmse = float(np.sqrt(np.mean((y - med) ** 2)))
    coverage = float(np.mean((y >= lo) & (y <= hi)))
    width = float(np.mean(hi - lo))
    return mae, rmse, coverage, width


def loso(X, y, groups, feature_names, max_folds=None):
    """Run LOSO; returns per-fold + aggregate metrics."""
    X = np.asarray(X); y = np.asarray(y); groups = np.asarray(groups)
    logo = LeaveOneGroupOut()
    maes, rmses, covs, widths = [], [], [], []
    folds = list(logo.split(X, y, groups))
    if max_folds:
        folds = folds[:max_folds]
    for tr, te in folds:
        qm = QuantileModel().fit(X[tr], y[tr], feature_names=feature_names,
                                 groups=groups[tr])
        pred = qm.predict(X[te])
        mae, rmse, cov, width = _metrics(y[te], pred)
        maes.append(mae); rmses.append(rmse); covs.append(cov); widths.append(width)
    return {
        "folds": len(folds),
        "MAE": float(np.mean(maes)),
        "MAE_std": float(np.std(maes)),
        "RMSE": float(np.mean(rmses)),
        "interval_coverage": float(np.mean(covs)),  # should approach target (e.g. 0.8)
        "interval_width": float(np.mean(widths)),
    }
