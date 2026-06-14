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
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel
from agroforestry.features import engineer
from agroforestry.models import QuantileModel, HybridQuantileModel
from agroforestry.validation import climate_zone
from agroforestry.config import TARGETS, GROUP_COL

Z = 1.2816   # 80% two-sided normal quantile
RNG = np.random.default_rng(0)


# ---- common wrapper interface: fit(X,y,feature_names,groups) ; predict -> dict ----
class _Scaled:
    def _fit_scaler(self, X):
        self.scaler = StandardScaler().fit(X); return self.scaler.transform(X)


class RidgeModel(_Scaled):
    def fit(self, X, y, feature_names=None, groups=None):
        Xs = self._fit_scaler(np.asarray(X)); self.m = Ridge(alpha=10.0).fit(Xs, y)
        self.sigma = float(np.std(y - self.m.predict(Xs))); return self
    def predict(self, X):
        mu = self.m.predict(self.scaler.transform(np.asarray(X)))
        return {"median": mu, "lower": mu - Z * self.sigma, "upper": mu + Z * self.sigma}


class RFModel:
    def fit(self, X, y, feature_names=None, groups=None):
        self.m = RandomForestRegressor(n_estimators=300, max_depth=None, min_samples_leaf=3,
                                       n_jobs=-1, random_state=0).fit(np.asarray(X), y); return self
    def predict(self, X):
        X = np.asarray(X)
        per = np.stack([t.predict(X) for t in self.m.estimators_], axis=1)
        return {"median": per.mean(1), "lower": np.quantile(per, 0.1, axis=1),
                "upper": np.quantile(per, 0.9, axis=1)}


class GPModel(_Scaled):
    def fit(self, X, y, feature_names=None, groups=None, cap=1000):
        X = np.asarray(X); y = np.asarray(y)
        if len(X) > cap:
            idx = RNG.choice(len(X), cap, replace=False); X, y = X[idx], y[idx]
        Xs = self._fit_scaler(X)
        k = ConstantKernel(1.0) * RBF(length_scale=np.ones(X.shape[1])) + WhiteKernel(0.1)
        self.m = GaussianProcessRegressor(kernel=k, normalize_y=True, n_restarts_optimizer=0,
                                          random_state=0).fit(Xs, y); return self
    def predict(self, X):
        mu, sd = self.m.predict(self.scaler.transform(np.asarray(X)), return_std=True)
        return {"median": mu, "lower": mu - Z * sd, "upper": mu + Z * sd}


class MoEModel(_Scaled):
    """One Ridge expert per training regime + softmax distance gate; interval from
    weighted expert disagreement (the honest 'far from all experts' uncertainty)."""
    def fit(self, X, y, feature_names=None, groups=None):
        X = np.asarray(X); y = np.asarray(y); self.zones = np.asarray(groups)
        self.scaler = StandardScaler().fit(X); Xs = self.scaler.transform(X)
        self.experts, self.centroids = {}, {}
        for z in np.unique(self.zones):
            mk = self.zones == z
            self.experts[z] = Ridge(alpha=10.0).fit(Xs[mk], y[mk])
            self.centroids[z] = Xs[mk].mean(0)
        self.sigma = float(np.std(y - self.predict_raw(X)[0])); return self
    def _weights(self, Xs):
        d = np.stack([np.linalg.norm(Xs - self.centroids[z], axis=1) for z in self.experts], 1)
        w = np.exp(-d / (d.mean() + 1e-9)); return w / w.sum(1, keepdims=True)
    def predict_raw(self, X):
        Xs = self.scaler.transform(np.asarray(X)); w = self._weights(Xs)
        preds = np.stack([self.experts[z].predict(Xs) for z in self.experts], 1)
        mu = (w * preds).sum(1)
        disagree = np.sqrt((w * (preds - mu[:, None]) ** 2).sum(1))
        return mu, disagree
    def predict(self, X):
        mu, dis = self.predict_raw(X)
        half = Z * np.sqrt(dis ** 2 + getattr(self, "sigma", 0.0) ** 2)
        return {"median": mu, "lower": mu - half, "upper": mu + half}


# QuantileModel/HybridQuantileModel already match fit(...groups=)/predict; adapt signature
class XGBWrap:
    def fit(self, X, y, feature_names=None, groups=None):
        self.m = QuantileModel().fit(X, y, feature_names=feature_names, groups=groups); return self
    def predict(self, X): return self.m.predict(X)

class HybridWrap:
    def fit(self, X, y, feature_names=None, groups=None):
        self.m = HybridQuantileModel().fit(X, y, feature_names=feature_names, groups=groups); return self
    def predict(self, X): return self.m.predict(X)


FACTORIES = {"ridge": RidgeModel, "rf": RFModel, "gp": GPModel, "moe": MoEModel,
             "xgb": XGBWrap, "hybrid": HybridWrap}


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
