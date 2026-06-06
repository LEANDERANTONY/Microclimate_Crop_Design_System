"""Mechanistic layer for the variables that do NOT need ML.

Light (Beer-Lambert) and wind (shelterbelt aerodynamics) are physics, so we
compute them directly rather than learning them. These are the HIGH-confidence
predictions.
"""
import math
from agroforestry.config import SPECIES


def light_fraction(lai, k):
    """Fraction of above-canopy PAR reaching the floor (Beer-Lambert)."""
    return math.exp(-k * lai)


def canopy_cover(lai, k):
    """Fractional canopy cover f = 1 - transmittance."""
    return 1.0 - light_fraction(lai, k)


def shade_pct(lai, k):
    return 100.0 * canopy_cover(lai, k)


def windbreak_reduction(height_m, porosity):
    """Average in-field wind reduction fraction from a perimeter windbreak.

    Average field shelter peaks at ~0.45 porosity: denser barriers cut wind hard
    immediately behind but create turbulence and a short shelter zone, while more
    porous barriers leak. A Gaussian centred on 0.45 captures this so the
    optimiser cannot 'win' by choosing a solid wall. Height gates effectiveness
    (~>=10 m for full effect at typical field scales).
    """
    height_fac = min(1.0, height_m / 10.0)
    peak = math.exp(-((porosity - 0.45) / 0.18) ** 2)   # 1.0 at 0.45, falls off both ways
    return 0.5 * peak * height_fac


def predict_wind(ambient_wind, species, lai, wb_height, wb_porosity):
    sp = SPECIES[species]
    f = canopy_cover(lai, sp["k"])
    r_wb = windbreak_reduction(wb_height, wb_porosity)
    return ambient_wind * (1.0 - sp["drag"] * f) * (1.0 - r_wb)
