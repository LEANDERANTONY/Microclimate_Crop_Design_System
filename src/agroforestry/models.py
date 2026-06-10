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
        self.feat_lo = None       # training feature ranges, for OOD detection
        self.feat_hi = None

    def fit(self, X, y, feature_names=None, groups=None, calib_frac=0.2, seed=0):
        self.feature_names = feature_names
        X = np.asarray(X); y = np.asarray(y)
        self.feat_lo = X.min(axis=0)
        self.feat_hi = X.max(axis=0)
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

    def ood_score(self, X):
        """Out-of-distribution score per row: fraction of features falling outside
        the training feature range. ~0 = in-distribution; high = extrapolation
        (e.g. a coconut design's tall-but-sparse canopy vs forest training data),
        where the learned offset should NOT be trusted.
        """
        X = np.asarray(X)
        if self.feat_lo is None:
            return np.zeros(len(X))
        outside = (X < self.feat_lo) | (X > self.feat_hi)
        return outside.mean(axis=1)

    def importances(self):
        m = self.models.get(0.5) or list(self.models.values())[0]
        imp = getattr(m, "feature_importances_", None)
        if imp is None or self.feature_names is None:
            return []
        pairs = sorted(zip(self.feature_names, imp), key=lambda p: -p[1])
        return pairs


class HybridQuantileModel:
    """Physics-guided hybrid: a smooth, EXTRAPOLATING linear backbone + XGBoost
    quantile regressors on the residual.

    Why this exists -- tree models (the pure ``QuantileModel``) cannot extrapolate:
    outside the training feature range they predict the boundary value, flat. The
    target application (semi-arid Tamil Nadu, warm nights t_min ~26 C) sits beyond
    the humid-forest training edge, so the pure offset is pinned to the training
    boundary there. A standardised Ridge backbone on physically-motivated features
    (canopy cover, radiation load, ambient VPD, diurnal range) extrapolates
    *gracefully* into that regime; the trees then only learn the bounded residual,
    so the model degrades sensibly OOD instead of going flat.

    Drop-in for ``QuantileModel``: same ``fit / predict / ood_score / importances``
    interface, so it slots into ``validation.loso/loco`` and ``Predictor`` unchanged.
    """

    # Parsimonious, physically-motivated backbone features. These are the canopy
    # *structure / radiation-load* terms that drive buffering (De Frenne et al.):
    # they stay roughly IN-RANGE across climates (canopy cover ~0.5-1 everywhere),
    # so a linear fit on them extrapolates sanely -- unlike a kitchen-sink Ridge on
    # raw temperature/VPD features, which blows up out-of-climate (tested: it does).
    DEFAULT_BACKBONE_FEATURES = ("canopy_cover",)

    def __init__(self, quantiles=QUANTILES, ridge_alpha=50.0, backbone_features=None):
        self.quantiles = quantiles
        self.ridge_alpha = ridge_alpha
        self.backbone_features = (backbone_features if backbone_features is not None
                                  else self.DEFAULT_BACKBONE_FEATURES)
        self.models = {}            # residual quantile regressors
        self.conformal_offset = 0.0
        self.feature_names = None
        self.feat_lo = None
        self.feat_hi = None
        self._backbone = None
        self._scaler = None
        self._bb_idx = None         # column indices of backbone features
        self._y_lo = None           # observed offset bounds (clip backbone OOD)
        self._y_hi = None

    def _backbone_predict(self, X):
        Xb = np.asarray(X)[:, self._bb_idx]
        Xs = self._scaler.transform(Xb)
        pred = self._backbone.predict(Xs)
        # Physical bound: the buffering offset cannot exceed what was ever observed.
        # Clipping stops the linear backbone from overshooting wildly when a feature
        # is far out of range (e.g. a held-out cool Mediterranean climate), which is
        # what made an unclipped linear extrapolation worse than a flat tree.
        if self._y_lo is not None:
            pred = np.clip(pred, self._y_lo, self._y_hi)
        return pred

    def fit(self, X, y, feature_names=None, groups=None, calib_frac=0.2, seed=0):
        from sklearn.linear_model import Ridge
        from sklearn.preprocessing import StandardScaler
        self.feature_names = feature_names
        X = np.asarray(X); y = np.asarray(y)
        self.feat_lo = X.min(axis=0)
        self.feat_hi = X.max(axis=0)
        rng = np.random.default_rng(seed)
        n = len(y)
        # group-aware calibration split (same logic as QuantileModel)
        if groups is not None:
            groups = np.asarray(groups)
            uniq = rng.permutation(np.unique(groups))
            n_cal_g = max(1, int(round(calib_frac * len(uniq))))
            cal_set = set(uniq[:n_cal_g].tolist())
            cal_mask = np.array([g in cal_set for g in groups])
            if cal_mask.all() or (~cal_mask).all():
                cal_mask = rng.random(n) < calib_frac
        else:
            cal_mask = rng.random(n) < calib_frac
        tr_mask = ~cal_mask
        Xtr, ytr = X[tr_mask], y[tr_mask]
        Xcal, ycal = X[cal_mask], y[cal_mask]

        # resolve backbone feature column indices (fall back to all features if
        # names are unavailable or unmatched)
        if feature_names is not None:
            self._bb_idx = [feature_names.index(f) for f in self.backbone_features
                            if f in feature_names]
        if not self._bb_idx:
            self._bb_idx = list(range(X.shape[1]))

        # 1) extrapolating linear backbone on a PARSIMONIOUS, in-range feature set
        self._scaler = StandardScaler().fit(Xtr[:, self._bb_idx])
        self._backbone = Ridge(alpha=self.ridge_alpha).fit(
            self._scaler.transform(Xtr[:, self._bb_idx]), ytr)
        # observed offset bounds (small pad) for physical clipping of the backbone
        pad = 0.25 * (ytr.max() - ytr.min())
        self._y_lo = float(ytr.min() - pad)
        self._y_hi = float(ytr.max() + pad)
        # 2) residual quantile regressors
        rtr = ytr - self._backbone_predict(Xtr)
        for q in self.quantiles:
            m = _make_quantile_regressor(q)
            m.fit(Xtr, rtr)
            self.models[q] = m
        # 3) CQR on the calibration set, on the FINAL prediction (backbone+residual)
        base_cal = self._backbone_predict(Xcal)
        lo = base_cal + self.models[self.quantiles[0]].predict(Xcal)
        hi = base_cal + self.models[self.quantiles[-1]].predict(Xcal)
        scores = np.maximum(lo - ycal, ycal - hi)
        target_cov = self.quantiles[-1] - self.quantiles[0]
        self.conformal_offset = float(np.quantile(scores, target_cov, method="higher"))
        return self

    def predict(self, X):
        X = np.asarray(X)
        base = self._backbone_predict(X)
        qmed = 0.5 if 0.5 in self.models else self.quantiles[len(self.quantiles) // 2]
        med = base + self.models[qmed].predict(X)
        lo = base + self.models[self.quantiles[0]].predict(X) - self.conformal_offset
        hi = base + self.models[self.quantiles[-1]].predict(X) + self.conformal_offset
        return {"median": med, "lower": lo, "upper": hi}

    def ood_score(self, X):
        X = np.asarray(X)
        if self.feat_lo is None:
            return np.zeros(len(X))
        outside = (X < self.feat_lo) | (X > self.feat_hi)
        return outside.mean(axis=1)

    def backbone_coef(self):
        """Standardised Ridge coefficients per backbone feature (interpretability)."""
        if self._backbone is None or self.feature_names is None:
            return []
        names = [self.feature_names[i] for i in self._bb_idx]
        return sorted(zip(names, self._backbone.coef_), key=lambda p: -abs(p[1]))

    def importances(self):
        m = self.models.get(0.5) or list(self.models.values())[0]
        imp = getattr(m, "feature_importances_", None)
        if imp is None or self.feature_names is None:
            return []
        return sorted(zip(self.feature_names, imp), key=lambda p: -p[1])
