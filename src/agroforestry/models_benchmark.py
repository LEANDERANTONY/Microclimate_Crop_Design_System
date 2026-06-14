"""Alternative offset-model families for the leave-one-climate-out benchmark.

These are NOT the pipeline's production model (that stays the XGBoost-quantile +
conformal model in `models.py`). They exist to answer the benchmark question — *can
any model family learn canopy->microclimate offsets that survive a macroclimate
shift?* — and are kept here, packaged and tested, so the comparison is reproducible.

All wrappers share the same minimal interface as `QuantileModel`:
    fit(X, y, feature_names=None, groups=None) -> self
    predict(X) -> {"median", "lower", "upper"}   (80% interval)
so they slot into `validation.loso/loco` and `scripts/benchmark_models.py` unchanged.

Finding (see manuscript §3.4): in-distribution all families are skilful; under
leave-one-climate-out, linear and mixture-of-experts collapse, tree models are bounded
but lose skill, and only the distance-aware Gaussian process keeps non-negative
cross-climate skill with the best out-of-climate interval coverage. Neural variants
(domain-adversarial, neural residual) are out of scope (a three-regime dataset overfits
them; domain-invariant representations can erase regime-dependent buffering).
"""
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel

from agroforestry.models import QuantileModel, HybridQuantileModel

Z80 = 1.2816   # two-sided 80% normal quantile
_RNG = np.random.default_rng(0)


class RidgeModel:
    """Standardised Ridge with a homoscedastic residual-std interval."""

    def __init__(self, alpha=10.0):
        self.alpha = alpha

    def fit(self, X, y, feature_names=None, groups=None):
        X = np.asarray(X); y = np.asarray(y)
        self.scaler = StandardScaler().fit(X)
        self.m = Ridge(alpha=self.alpha).fit(self.scaler.transform(X), y)
        self.sigma = float(np.std(y - self.m.predict(self.scaler.transform(X))))
        return self

    def predict(self, X):
        mu = self.m.predict(self.scaler.transform(np.asarray(X)))
        return {"median": mu, "lower": mu - Z80 * self.sigma, "upper": mu + Z80 * self.sigma}


class RFModel:
    """Random forest; interval from the 10th/90th percentile of per-tree predictions."""

    def __init__(self, n_estimators=300, min_samples_leaf=3, random_state=0):
        self.kw = dict(n_estimators=n_estimators, min_samples_leaf=min_samples_leaf,
                       n_jobs=-1, random_state=random_state)

    def fit(self, X, y, feature_names=None, groups=None):
        self.m = RandomForestRegressor(**self.kw).fit(np.asarray(X), np.asarray(y))
        return self

    def predict(self, X):
        X = np.asarray(X)
        per = np.stack([t.predict(X) for t in self.m.estimators_], axis=1)
        return {"median": per.mean(1), "lower": np.quantile(per, 0.1, axis=1),
                "upper": np.quantile(per, 0.9, axis=1)}


class GPModel:
    """Gaussian process (ARD RBF + white noise). Predictive sigma grows with distance
    from training data, giving the distance-aware interval that stays best-calibrated
    out-of-climate (§3.4). Training is subsampled to `cap` rows for tractability."""

    def __init__(self, cap=1000, seed=0):
        self.cap = cap; self.seed = seed

    def fit(self, X, y, feature_names=None, groups=None):
        X = np.asarray(X); y = np.asarray(y)
        rng = np.random.default_rng(self.seed)
        if len(X) > self.cap:
            idx = rng.choice(len(X), self.cap, replace=False); X, y = X[idx], y[idx]
        self.scaler = StandardScaler().fit(X)
        k = ConstantKernel(1.0) * RBF(length_scale=np.ones(X.shape[1])) + WhiteKernel(0.1)
        self.m = GaussianProcessRegressor(kernel=k, normalize_y=True,
                                          n_restarts_optimizer=0, random_state=self.seed)
        self.m.fit(self.scaler.transform(X), y)
        return self

    def predict(self, X):
        mu, sd = self.m.predict(self.scaler.transform(np.asarray(X)), return_std=True)
        return {"median": mu, "lower": mu - Z80 * sd, "upper": mu + Z80 * sd}


class MoEModel:
    """Mixture-of-experts: one Ridge expert per training regime (group) with a softmax
    distance gate; uncertainty from weighted expert disagreement (the 'far from all
    experts' signal). Needs `groups` (the regime label per row) at fit time."""

    def __init__(self, alpha=10.0):
        self.alpha = alpha

    def fit(self, X, y, feature_names=None, groups=None):
        X = np.asarray(X); y = np.asarray(y)
        self.groups = np.asarray(groups) if groups is not None else np.zeros(len(X))
        self.scaler = StandardScaler().fit(X); Xs = self.scaler.transform(X)
        self.experts, self.centroids = {}, {}
        for g in np.unique(self.groups):
            mk = self.groups == g
            self.experts[g] = Ridge(alpha=self.alpha).fit(Xs[mk], y[mk])
            self.centroids[g] = Xs[mk].mean(0)
        self.sigma = float(np.std(y - self._raw(X)[0]))
        return self

    def _weights(self, Xs):
        d = np.stack([np.linalg.norm(Xs - self.centroids[g], axis=1) for g in self.experts], 1)
        w = np.exp(-d / (d.mean() + 1e-9))
        return w / w.sum(1, keepdims=True)

    def _raw(self, X):
        Xs = self.scaler.transform(np.asarray(X)); w = self._weights(Xs)
        preds = np.stack([self.experts[g].predict(Xs) for g in self.experts], 1)
        mu = (w * preds).sum(1)
        disagree = np.sqrt((w * (preds - mu[:, None]) ** 2).sum(1))
        return mu, disagree

    def predict(self, X):
        mu, dis = self._raw(X)
        half = Z80 * np.sqrt(dis ** 2 + getattr(self, "sigma", 0.0) ** 2)
        return {"median": mu, "lower": mu - half, "upper": mu + half}


class XGBWrap:
    """Adapter so the production QuantileModel matches the benchmark factory signature."""

    def fit(self, X, y, feature_names=None, groups=None):
        self.m = QuantileModel().fit(X, y, feature_names=feature_names, groups=groups)
        return self

    def predict(self, X):
        return self.m.predict(X)


class HybridWrap:
    """Adapter for the physics-prior hybrid."""

    def fit(self, X, y, feature_names=None, groups=None):
        self.m = HybridQuantileModel().fit(X, y, feature_names=feature_names, groups=groups)
        return self

    def predict(self, X):
        return self.m.predict(X)


# Registry used by scripts/benchmark_models.py
BENCHMARK_FACTORIES = {
    "ridge": RidgeModel, "rf": RFModel, "gp": GPModel, "moe": MoEModel,
    "xgb": XGBWrap, "hybrid": HybridWrap,
}
