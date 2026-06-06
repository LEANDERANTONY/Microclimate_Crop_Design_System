"""Disease layer -- mechanistic infection risk from microclimate (no incidence
data needed). Implements: leaf-wetness-duration estimate, a generic temperature
response, per-disease environmental pressure, and the
  realized_risk = environmental_pressure x variety_susceptibility
decomposition (the disease triangle: host x pathogen x environment).

CONFIDENCE: this whole layer is v1 mechanistic with literature-shaped parameters.
Treat comparisons (wet vs dry timing, variety A vs B) as more reliable than any
absolute probability. Calibrate against observed incidence later.
"""
from agroforestry.config import (DISEASES, VARIETY_SUSCEPTIBILITY, RESISTANCE_SCALE,
                    DEFAULT_SUSCEPTIBILITY)


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def estimate_lwd(rh, rain_mm_day):
    """Crude DAILY leaf-wetness hours from daily RH + rain.

    Operational models use hourly RH>90% or dew-point depression <2C; we lack
    hourly data at screening stage, so approximate from daily aggregates. LOW
    confidence -- the first thing to upgrade with hourly/sensor data.
    """
    wet = max(0.0, (rh - 80) / 20.0) * 12.0       # up to ~12 h from humidity alone
    if rain_mm_day > 0:
        wet += min(8.0, 4.0 + 0.2 * rain_mm_day)  # rain adds wetness hours
    return min(24.0, wet)


def _temp_response(T, tmin, topt, tmax):
    """Generic beta-shaped infection response, 0 outside [tmin, tmax], 1 at topt."""
    if T <= tmin or T >= tmax:
        return 0.0
    a = (tmax - T) / (tmax - topt)
    b = (T - tmin) / (topt - tmin)
    expo = (topt - tmin) / (tmax - topt)
    return _clamp(a * (b ** expo))


def disease_pressure(d, T, lwd, rh, rain_mm_day):
    """Environmental favourability for one disease, 0..1 (variety-independent)."""
    if d["type"] == "heat":
        thr = d["t_threshold"]
        return _clamp((T - (thr - 4)) / 4.0)      # ramps up approaching/over threshold

    tr = _temp_response(T, d["t_min"], d["t_opt"], d["t_max"])
    if d["type"] == "wetness":
        wr = _clamp((lwd - d["lwd_min"]) / (d["lwd_sat"] - d["lwd_min"]))
        p = tr * wr
    else:  # humidity or soil
        rh_min, rh_sat = d.get("rh_min", 60), d.get("rh_sat", 90)
        wr = _clamp((rh - rh_min) / (rh_sat - rh_min))
        p = tr * wr

    if d.get("rain_driven") and rain_mm_day <= 0:
        p *= 0.6                                   # splash dispersal reduced when dry
    return _clamp(p)


def _susceptibility(crop, variety, disease_name):
    table = VARIETY_SUSCEPTIBILITY.get(crop, {})
    rating = table.get(variety, {}).get(disease_name)
    if rating is None:
        return DEFAULT_SUSCEPTIBILITY
    return RESISTANCE_SCALE[rating]


def crop_disease_risk(crop, micro, variety=None, rain_mm_day=0.0):
    """Realized risk per disease for a crop under a microclimate.

    micro must provide t_mean (infection temp proxy, often the cool wet period)
    and rh. Returns dict: per-disease realized risk + the worst one.
    """
    diseases = DISEASES.get(crop, [])
    if not diseases:
        return {"per_disease": {}, "max": 0.0, "worst": None}

    T = micro.get("t_mean", micro.get("t_max"))
    rh = micro["rh"]
    lwd = estimate_lwd(rh, rain_mm_day)

    per = {}
    for d in diseases:
        pressure = disease_pressure(d, T, lwd, rh, rain_mm_day)
        susc = _susceptibility(crop, variety, d["name"])
        per[d["name"]] = _clamp(pressure * susc)

    worst = max(per, key=per.get) if per else None
    return {"per_disease": per, "max": per[worst] if worst else 0.0,
            "worst": worst, "lwd_hours": round(lwd, 1)}
