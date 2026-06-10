"""Validation utilities + hybrid model: interface and transfer-protocol checks."""
import numpy as np

from agroforestry.models import QuantileModel, HybridQuantileModel
from agroforestry.validation import loso, loco, climate_zone


def _synth(n_sites=8, per=40, seed=0):
    rng = np.random.default_rng(seed)
    feats = ["canopy_cover", "cover_x_solar", "cover_x_vpd", "x4"]
    rows, y, groups = [], [], []
    for s in range(n_sites):
        cover = rng.uniform(0.3, 0.95, per)
        solar = rng.uniform(10, 25, per)
        vpd = rng.uniform(0.5, 2.5, per)
        x4 = rng.normal(0, 1, per)
        # offset is a (noisy) function of canopy cover + interaction
        off = -3.0 * cover - 0.05 * cover * solar + rng.normal(0, 0.2, per)
        X = np.column_stack([cover, cover * solar, cover * vpd, x4])
        rows.append(X); y.append(off); groups += [f"S{s}"] * per
    return np.vstack(rows), np.concatenate(y), np.array(groups), feats


def test_climate_zone_tags():
    z = climate_zone(["LJ_1", "OP_3", "E_196", "VJR_2"])
    assert list(z) == ["med_spain", "oilpalm_open", "borneo_forest", "borneo_forest"]


def test_hybrid_predict_interface_and_intervals():
    X, y, groups, feats = _synth()
    hm = HybridQuantileModel().fit(X, y, feature_names=feats, groups=groups)
    out = hm.predict(X[:5])
    assert set(out) == {"median", "lower", "upper"}
    assert np.all(out["lower"] <= out["upper"])
    # OOD: a point far outside the training cloud flags all features out of range
    assert hm.ood_score(np.array([[9999.0, 9999.0, 9999.0, 9999.0]]))[0] == 1.0


def test_hybrid_backbone_clips_offset_in_range():
    """The linear backbone must not predict an offset far beyond the observed
    range, even for wildly out-of-range inputs (the safeguard against the linear
    overshoot that made an unclipped hybrid worse than the tree out-of-climate)."""
    X, y, groups, feats = _synth()
    hm = HybridQuantileModel().fit(X, y, feature_names=feats, groups=groups)
    extreme = np.array([[50.0, 500.0, 500.0, 50.0]])
    backbone = hm._backbone_predict(extreme)[0]
    assert hm._y_lo <= backbone <= hm._y_hi


def test_loso_and_loco_report_skill():
    X, y, groups, feats = _synth()
    r = loso(X, y, groups, feats, max_folds=4)
    assert "skill_vs_baseline" in r and "R2_oos" in r and r["folds"] == 4
    # build two pseudo-climates and check LOCO returns a per-zone breakdown
    zones = np.where(np.isin(groups, ["S0", "S1", "S2", "S3"]), "A", "B")
    rc = loco(X, y, zones, feats, site_groups=groups)
    assert set(rc["per_zone"]) == {"A", "B"}
