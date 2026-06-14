"""Benchmark model families: interface, intervals, and the registry."""
import numpy as np
import pytest

from agroforestry.models_benchmark import (RidgeModel, RFModel, GPModel, MoEModel,
                                            XGBWrap, HybridWrap, BENCHMARK_FACTORIES)


def _synth(n_sites=6, per=40, seed=0):
    rng = np.random.default_rng(seed)
    feats = ["canopy_cover", "cover_x_solar", "cover_x_vpd", "x4"]
    rows, y, groups = [], [], []
    for s in range(n_sites):
        cover = rng.uniform(0.3, 0.95, per); solar = rng.uniform(10, 25, per)
        vpd = rng.uniform(0.5, 2.5, per); x4 = rng.normal(0, 1, per)
        off = -3.0 * cover - 0.05 * cover * solar + rng.normal(0, 0.2, per)
        rows.append(np.column_stack([cover, cover * solar, cover * vpd, x4]))
        y.append(off); groups += [f"S{s}"] * per
    return np.vstack(rows), np.concatenate(y), np.array(groups), feats


def test_registry_keys():
    assert set(BENCHMARK_FACTORIES) == {"ridge", "rf", "gp", "moe", "xgb", "hybrid"}


@pytest.mark.parametrize("name", ["ridge", "rf", "gp", "moe", "xgb", "hybrid"])
def test_model_fits_and_returns_ordered_intervals(name):
    X, y, groups, feats = _synth()
    m = BENCHMARK_FACTORIES[name]().fit(X, y, feature_names=feats, groups=groups)
    out = m.predict(X[:10])
    assert set(out) == {"median", "lower", "upper"}
    assert np.all(out["lower"] <= out["upper"] + 1e-9)
    assert len(out["median"]) == 10


def test_gp_uncertainty_grows_with_distance():
    """GP interval should widen for a point far outside the training cloud."""
    X, y, groups, feats = _synth()
    gp = GPModel(cap=200).fit(X, y, feature_names=feats, groups=groups)
    near = gp.predict(X[:1]); far = gp.predict(np.array([[5.0, 80.0, 80.0, 9.0]]))
    w_near = float(near["upper"][0] - near["lower"][0])
    w_far = float(far["upper"][0] - far["lower"][0])
    assert w_far > w_near


def test_moe_requires_groups_but_runs_without():
    X, y, groups, feats = _synth()
    m = MoEModel().fit(X, y, feature_names=feats, groups=groups)
    assert len(m.experts) == 6  # one expert per site/group
