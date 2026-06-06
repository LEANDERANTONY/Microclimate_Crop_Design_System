"""Layer 3 -- inverse design. Search designs to maximise a crop's suitability.

Grid search by default (transparent, fast). swap in Bayesian optimisation /
NSGA-II later for larger design spaces -- same objective function.
"""
import numpy as np
from agroforestry.config import SPECIES
from agroforestry.suitability import score_crop, viability


def optimise(predictor, crop, macro, context,
             objective="growth", variety=None, rain_mm_day=0.0,
             species_list=None, lai_grid=None,
             porosity_grid=(0.3, 0.4, 0.45, 0.5, 0.6),
             height_grid=(5, 10, 15)):
    """objective: "growth" (microclimate fit only) or "viability"
    (growth AND disease risk -- needs variety + the disease-window rainfall)."""
    if species_list is None:
        species_list = list(SPECIES)   # include "none" so full-sun crops can reach 0% shade
    if lai_grid is None:
        lai_grid = np.arange(0.5, 3.01, 0.25)

    best = {"score": -1}
    for sp in species_list:
        for lai in lai_grid:
            for por in porosity_grid:
                for h in height_grid:
                    design = {"species": sp, "lai": float(lai),
                              "wb_height": h, "wb_porosity": por}
                    micro = predictor.predict_micro(design, macro, context)
                    if objective == "viability":
                        v = viability(crop, micro, variety=variety, rain_mm_day=rain_mm_day)
                        val = v["viability"]
                        extra = {"micro": micro, "growth": v["growth"],
                                 "disease_risk": v["disease_risk"],
                                 "worst_disease": v["worst_disease"],
                                 "limiting": v["growth_limiting"]}
                    else:
                        s = score_crop(crop, micro)
                        val = s["score"]
                        extra = {"micro": micro, "limiting": s["limiting"],
                                 "confidence": s["confidence"]}
                    if val > best["score"]:
                        best = {"score": val, "design": design, **extra}
    return best
