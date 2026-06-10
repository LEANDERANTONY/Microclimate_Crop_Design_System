"""Tests for the Monte Carlo uncertainty layer."""
import numpy as np
import pandas as pd
from agroforestry.features import engineer
from agroforestry.models import QuantileModel
from agroforestry.predict import Predictor
from agroforestry.monte_carlo import simulate
from agroforestry.config import TARGETS

MACRO = dict(t_mean=29.3, t_max=34.3, t_min=25.9, rh=71, wind=0.4, solar=21.0, rainfall=926)
CTX = dict(elevation=23, slope=1.0, twi=4.0, soc=328, clay=355)


def _predictor():
    df = pd.read_parquet("data/processed/labelled_offsets.parquet")
    X, feats = engineer(df)
    models = {t: QuantileModel().fit(X[feats].values, df[t].values, feature_names=feats) for t in TARGETS}
    return Predictor(models, feats)


def test_simulate_shapes_and_bounds():
    p = _predictor()
    r = simulate(p, MACRO, CTX, "coconut_wide", 1.0, "Nutmeg", n=300, seed=1)
    assert len(r["npvs"]) == 300
    assert 0.0 <= r["prob_loss"] <= 1.0
    assert r["p10"] <= r["p50"] <= r["p90"]


def test_simulate_is_deterministic_with_seed():
    p = _predictor()
    a = simulate(p, MACRO, CTX, "coconut_wide", 1.0, "Nutmeg", n=300, seed=7)
    b = simulate(p, MACRO, CTX, "coconut_wide", 1.0, "Nutmeg", n=300, seed=7)
    assert a["mean"] == b["mean"] and a["prob_loss"] == b["prob_loss"]


def test_intercrop_changes_distribution():
    # adding an intercrop must change the NPV distribution vs coconut alone
    p = _predictor()
    base = simulate(p, MACRO, CTX, "coconut_wide", 1.0, None, n=300, seed=1)
    inter = simulate(p, MACRO, CTX, "coconut_wide", 1.0, "Nutmeg", n=300, seed=1)
    assert inter["p90"] > base["p90"]          # intercrop adds upside
    assert 0.0 <= base["prob_loss"] <= 1.0
