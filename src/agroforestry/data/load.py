"""Real-data loader + offset computation.

Produces / validates ``data/processed/labelled_offsets.parquet`` -- the file the
pipeline reads when ``DATA_SOURCE = "real"``. It must contain exactly
``config.RAW_FEATURES + config.TARGETS + config.GROUP_COL``.

End-to-end recipe (see docs/data_acquisition.md for the full guide):

  1. LABEL SITES -- assemble paired sub-canopy + ambient microclimate records
     from SoilTemp / ForestTemp / agroforestry field datasets. Each row needs:
     site_id, lat, lon, date, and paired measurements
     (sub_t_max, amb_t_max, sub_t_mean, amb_t_mean, sub_rh, amb_rh).
  2. FEATURES -- run ``scripts/fetch_earth_engine.py`` to attach macro + canopy +
     terrain + soil predictors at each site/date.
  3. OFFSETS  -- ``compute_offset_targets`` turns the paired measurements into the
     dT_max / dT_mean / dVPD targets.
  4. JOIN + SAVE -- merge features + offsets on site_id (+ date) and write parquet.
"""
import numpy as np
import pandas as pd

from agroforestry.config import RAW_FEATURES, TARGETS, GROUP_COL

# Columns the raw paired-measurement table must provide (before offsets).
PAIRED_COLUMNS = [
    "sub_t_max", "amb_t_max",
    "sub_t_mean", "amb_t_mean",
    "sub_rh", "amb_rh",
]


def _tetens_es(t):
    """Saturation vapour pressure (kPa) via Tetens."""
    return 0.6108 * np.exp(17.27 * t / (t + 237.3))


def compute_offset_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Add dT_max, dT_mean, dVPD (sub-canopy minus ambient) from paired columns.

    Predicting the *offset* (not raw sub-canopy values) is what transfers across
    macroclimates -- the project's central modelling choice (ADR-001).
    """
    missing = set(PAIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"paired measurements missing columns: {sorted(missing)}")
    out = df.copy()
    out["dT_max"] = out["sub_t_max"] - out["amb_t_max"]
    out["dT_mean"] = out["sub_t_mean"] - out["amb_t_mean"]
    vpd_sub = _tetens_es(out["sub_t_max"]) * (1 - out["sub_rh"] / 100.0)
    vpd_amb = _tetens_es(out["amb_t_max"]) * (1 - out["amb_rh"] / 100.0)
    out["dVPD"] = vpd_sub - vpd_amb
    return out


def load_real(path: str = "data/processed/labelled_offsets.parquet") -> pd.DataFrame:
    """Load the final labelled-offsets table and validate the schema."""
    df = pd.read_parquet(path)
    required = set(RAW_FEATURES + TARGETS + [GROUP_COL])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"data is missing required columns: {sorted(missing)}")
    return df
