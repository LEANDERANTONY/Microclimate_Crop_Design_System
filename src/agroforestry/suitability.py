"""Layer 2 -- fuzzy, limiting-factor crop suitability (Liebig's minimum).

Mirrors the interactive app: trapezoidal membership per variable, score = the
worst-matched factor. Reports the limiting variable and its confidence.
"""
from agroforestry.config import CROPS, CONFIDENCE


def _trap(x, lo, hi, tlo, thi):
    if lo <= x <= hi:
        return 1.0
    if x < tlo or x > thi:
        return 0.0
    if x < lo:
        return (x - tlo) / (lo - tlo)
    return (thi - x) / (thi - hi)


def _one_sided(x, ideal, tol):  # lower is better (wind)
    if x <= ideal:
        return 1.0
    if x >= tol:
        return 0.0
    return (tol - x) / (tol - ideal)


def score_crop(crop, micro):
    """micro = dict(t_max=, shade=, rh=, wind=)."""
    c = CROPS[crop]
    m = {
        "t":     _trap(micro["t_max"], *c["t"]),
        "shade": _trap(micro["shade"], *c["shade"]),
        "rh":    _trap(micro["rh"], *c["rh"]),
        "wind":  _one_sided(micro["wind"], *c["wind"]),
    }
    lim = min(m, key=m.get)
    names = {"t": "temperature", "shade": "shade/light", "rh": "humidity", "wind": "wind"}
    return {
        "score": round(100 * m[lim]),
        "limiting": names[lim],
        "confidence": CONFIDENCE[lim],
        "memberships": m,
    }


def score_all(micro):
    return {crop: score_crop(crop, micro) for crop in CROPS}


def viability(crop, micro, variety=None, rain_mm_day=0.0,
              waterlogging=None, drainage="none"):
    """Two-axis crop assessment: growth fit AND disease risk -> viability.

    viability = growth_score * (1 - disease_risk). A crop can have ideal growth
    conditions but collapse to low viability under high disease pressure -- the
    pomegranate-in-the-monsoon case. Disease spans two axes: foliar (air
    microclimate) and soil-borne (waterlogging x drainage mitigation).
    """
    from agroforestry.disease import crop_disease_risk     # local import to avoid cycles
    g = score_crop(crop, micro)
    dr = crop_disease_risk(crop, micro, variety=variety, rain_mm_day=rain_mm_day,
                           waterlogging=waterlogging, drainage=drainage)
    penalty = dr["max"]
    return {
        "growth": g["score"],
        "growth_limiting": g["limiting"],
        "growth_conf": g["confidence"],
        "disease_risk": round(100 * penalty),
        "worst_disease": dr["worst"],
        "lwd_hours": dr.get("lwd_hours"),
        "waterlogging_eff": dr.get("waterlogging_eff"),
        "viability": round(g["score"] * (1 - penalty)),
    }
