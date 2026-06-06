"""Layer 3 -- inverse design. Search designs to maximise a crop's suitability.

Grid search by default (transparent, fast). swap in Bayesian optimisation /
NSGA-II later for larger design spaces -- same objective function.
"""
import numpy as np
from agroforestry.config import SPECIES
from agroforestry.suitability import score_crop, viability


def optimise(predictor, crop, macro, context,
             objective="growth", variety=None, rain_mm_day=0.0,
             waterlogging=None,
             species_list=None, lai_grid=None,
             porosity_grid=(0.3, 0.4, 0.45, 0.5, 0.6),
             height_grid=(5, 10, 15),
             drainage_grid=("none", "raised_beds", "raised_beds+drains")):
    """objective: "growth" (microclimate fit only) or "viability"
    (growth AND disease risk -- needs variety + the disease-window rainfall).

    For "viability", drainage mitigation is searched as a design lever (it lowers
    the soil-water/waterlogging disease axis); for "growth" it is irrelevant.
    """
    if species_list is None:
        species_list = list(SPECIES)   # include "none" so full-sun crops can reach 0% shade
    if lai_grid is None:
        lai_grid = np.arange(0.5, 3.01, 0.25)
    drainages = drainage_grid if objective == "viability" else ("none",)

    best = {"score": -1}
    for sp in species_list:
        for lai in lai_grid:
            for por in porosity_grid:
                for h in height_grid:
                    design = {"species": sp, "lai": float(lai),
                              "wb_height": h, "wb_porosity": por}
                    micro = predictor.predict_micro(design, macro, context)
                    if objective == "viability":
                        for drn in drainages:
                            v = viability(crop, micro, variety=variety,
                                          rain_mm_day=rain_mm_day,
                                          waterlogging=waterlogging, drainage=drn)
                            if v["viability"] > best["score"]:
                                best = {"score": v["viability"],
                                        "design": {**design, "drainage": drn},
                                        "micro": micro, "growth": v["growth"],
                                        "disease_risk": v["disease_risk"],
                                        "worst_disease": v["worst_disease"],
                                        "limiting": v["growth_limiting"]}
                    else:
                        s = score_crop(crop, micro)
                        if s["score"] > best["score"]:
                            best = {"score": s["score"], "design": design,
                                    "micro": micro, "limiting": s["limiting"],
                                    "confidence": s["confidence"]}
    return best
