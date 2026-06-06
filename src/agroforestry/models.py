"""XGBoost quantile models + conformalized prediction intervals.

One set of quantile regressors per target (dT_max, dT_mean, dVPD). Lower/median/
upper quantiles give native intervals; CQR (conformalized quantile regression)
calibrates them so the stated coverage is statistically honest -- essential given
borrowed, not-yet-local data.
"""
import numpy as np
from agroforestry.config import QUANTILES

try:
    from xgboost import XGBRegressor
    _HAS_XGB = True
except Exception:  # pragma: no cover
    _HAS_XGB = False
    from sklearn.ensemble import GradientBoostingRegressor


def _make_quantile_regressor(alpha):
    """XGBoost >=2.0 native quantile loss; fall back to sklearn GBR."""
    if _HAS_XGB:
        try:
            return XGBRegressor(
                objective="reg:quantileerror", quantile_alpha=alpha,
                n_estimators=400, max_depth=4, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8, random_state=0,
            )
        except TypeError:
            pass  # older xgboost without quantile support -> sklearn
    from sklearn.ensemble import GradientBoostingRegressor
    return GradientBoostingRegressor(loss="quantile", alpha=alpha,
                                     n_estimators=400, max_depth=3,
                                     learning_rate=0.05, subsample=0.8,
                                     random_state=0)


class QuantileModel:
    """Lower/median/upper quantile regressors for a single target, with CQR."""

    def __init__(self, quantiles=QUANTILES):
        self.quantiles = quantiles
        self.models = {}
        self.conformal_offset = 0.0
        self.feature_names = None

    def fit(self, X, y, feature_names=None, groups=None, calib_frac=0.2, seed=0):
        self.feature_names = feature_names
        X = np.asarray(X); y = np.asarray(y)
        rng = np.random.default_rng(seed)
        n = len(y)
        # Conformal calibration on held-out SITES when groups are given, so the
        # interval width reflects cross-site transfer error (fixes LOSO under-
        # coverage). Falls back to a random row split otherwise.
        if groups is not None:
            groups = np.asarray(groups)
            uniq = rng.permutation(np.unique(groups))
            n_cal_g = max(1, int(round(calib_frac * len(uniq))))
            cal_set = set(uniq[:n_cal_g].tolist())
            cal_mask = np.array([g in cal_set for g in groups])
            if cal_mask.all() or (~cal_mask).all():     # guard tiny group counts
                cal_mask = rng.random(n) < calib_frac
        else:
            cal_mask = rng.random(n) < calib_frac
        tr_mask = ~cal_mask
        Xtr, ytr = X[tr_mask], y[tr_mask]
        Xcal, ycal = X[cal_mask], y[cal_mask]
        for q in self.quantiles:
            m = _make_quantile_regressor(q)
            m.fit(Xtr, ytr)
            self.models[q] = m
        # CQR calibration on held-out calib set
        lo = self.models[self.quantiles[0]].predict(Xcal)
        hi = self.models[self.quantiles[-1]].predict(Xcal)
        scores = np.maximum(lo - ycal, ycal - hi)
        target_cov = self.quantiles[-1] - self.quantiles[0]
        self.conformal_offset = float(np.quantile(scores, target_cov, method="higher"))
        return self

    def predict(self, X):
        X = np.asarray(X)
        med = self.models[0.5].predict(X) if 0.5 in self.models else \
            self.models[self.quantiles[len(self.quantiles) // 2]].predict(X)
        lo = self.models[self.quantiles[0]].predict(X) - self.conformal_offset
        hi = self.models[self.quantiles[-1]].predict(X) + self.conformal_offset
        return {"median": med, "lower": lo, "upper": hi}

    def importances(self):
        m = self.models.get(0.5) or list(self.models.values())[0]
        imp = getattr(m, "feature_importances_", None)
        if imp is None or self.feature_names is None:
            return []
        pairs = sorted(zip(self.feature_names, imp), key=lambda p: -p[1])
        return pairs
