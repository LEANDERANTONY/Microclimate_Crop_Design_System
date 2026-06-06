"""Feature engineering: derive physically-motivated predictors from raw columns.

Cast wide here (the catalog philosophy); prune later via feature importance.
Returns (X dataframe, feature_name_list).
"""
import numpy as np
import pandas as pd
from agroforestry.config import RAW_FEATURES


def _tetens_es(t):
    return 0.6108 * np.exp(17.27 * t / (t + 237.3))


def engineer(df):
    X = df[RAW_FEATURES].copy()

    # canopy cover proxy (Beer-Lambert with nominal k)
    X["canopy_cover"] = 1 - np.exp(-0.55 * df["lai"])
    # diurnal temperature range
    X["diurnal_range"] = df["t_max"] - df["t_min"]
    # ambient VPD (kPa)
    es = _tetens_es(df["t_max"])
    X["vpd_ambient"] = es * (1 - df["rh"] / 100)
    # growing-degree-day proxy (base 10C on mean)
    X["gdd_proxy"] = np.maximum(df["t_mean"] - 10, 0)
    # structural interactions (drivers of buffering)
    X["lai_x_height"] = df["lai"] * df["canopy_height"]
    X["cover_x_solar"] = X["canopy_cover"] * df["solar"]
    X["cover_x_vpd"] = X["canopy_cover"] * X["vpd_ambient"]
    # aridity-ish
    X["rain_per_temp"] = df["rainfall"] / (df["t_mean"] + 1)

    feats = list(X.columns)
    return X, feats
