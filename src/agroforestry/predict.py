"""Unified predictor: combine ML offsets (temp, VPD) with physics (light, wind)
into one under-canopy microclimate for a given design.

This is the bridge from trained models to the suitability/optimiser layers.
"""
import numpy as np
import pandas as pd
from agroforestry.config import RAW_FEATURES, SPECIES
from agroforestry.features import engineer, _tetens_es
from agroforestry.physics import shade_pct, predict_wind, canopy_cover


def build_feature_row(design, macro, context):
    """design: dict(species, lai, wb_height, wb_porosity)
       macro:  dict(t_mean,t_max,t_min,rh,wind,solar,rainfall)
       context:dict(elevation,slope,twi,soc,clay)
    Returns a 1-row DataFrame with RAW_FEATURES (canopy proxies derived from design).
    """
    sp = SPECIES[design["species"]]
    lai = design["lai"]
    cover = canopy_cover(lai, sp["k"])
    row = dict(macro)
    row.update(context)
    row["lai"] = lai
    row["canopy_height"] = lai * 5.0          # crude proxy; replaced by GEDI/Meta height later
    row["ndvi"] = float(np.clip(0.3 + 0.6 * cover, 0, 1))
    row["fapar"] = float(np.clip(0.9 * cover, 0, 1))
    return pd.DataFrame([{k: row[k] for k in RAW_FEATURES}])


class Predictor:
    def __init__(self, models, feature_names):
        self.models = models            # dict target -> QuantileModel
        self.feature_names = feature_names

    def predict_micro(self, design, macro, context):
        X, _ = engineer(build_feature_row(design, macro, context))
        Xv = X[self.feature_names].values
        out = {t: self.models[t].predict(Xv) for t in self.models}

        # out-of-distribution check: is this design's canopy/feature combo within
        # the training cloud? (e.g. coconut = tall + sparse, unlike forest training)
        ood = float(next(iter(self.models.values())).ood_score(Xv)[0])
        extrapolating = ood > 0.15
        offset_conf = "LOW (extrapolation)" if extrapolating else "MODERATE"

        # physics layer
        sp = SPECIES[design["species"]]
        shade = shade_pct(design["lai"], sp["k"])
        wind = predict_wind(macro["wind"], design["species"], design["lai"],
                            design["wb_height"], design["wb_porosity"])

        # assemble under-canopy values from offsets
        t_max_u = macro["t_max"] + float(out["dT_max"]["median"][0])
        t_mean_u = macro["t_mean"] + float(out["dT_mean"]["median"][0])
        es = float(_tetens_es(pd.Series([macro["t_max"]]))[0])
        vpd_amb = es * (1 - macro["rh"] / 100)
        vpd_u = max(0.01, vpd_amb + float(out["dVPD"]["median"][0]))
        es_u = float(_tetens_es(pd.Series([t_max_u]))[0])
        rh_u = float(np.clip(100 * (1 - vpd_u / es_u), 0, 99))

        return {
            "t_max": t_max_u, "t_mean": t_mean_u, "shade": shade,
            "rh": rh_u, "wind": wind, "vpd": vpd_u,
            "ood_score": round(ood, 2),
            "extrapolating": extrapolating,        # learned offset off-distribution?
            "offset_confidence": offset_conf,      # physics (light/wind) stays HIGH regardless
            "intervals": {
                "dT_max": (float(out["dT_max"]["lower"][0]), float(out["dT_max"]["upper"][0])),
                "dVPD":   (float(out["dVPD"]["lower"][0]),   float(out["dVPD"]["upper"][0])),
            },
        }
