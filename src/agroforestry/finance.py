"""Layer 5b -- multi-year financial model: cash-flow, NPV, IRR, payback.

Upgrades the single-year `economics.crop_margin` into a proper financial comparison
that respects TIMING: crops have a gestation (no income for N years) and a bearing
ramp; timber pays a single lump at harvest. This is what makes coconut (steady annual
cash) vs timber (one far-off payout) an honest comparison rather than naive annualising.

All money INR per acre. Profiles (gestation / full-bearing / economic life / costs) are
standard horticulture figures (TNAU/ICAR/NHB) -- editable, MODERATE confidence. Revenue
magnitudes reuse `economics` (site-adjusted yield x price band).
"""
import numpy as np
from agroforestry.economics import (CROP_ECON, OVERSTOREY_ECON, SPECIES_TO_OVERSTOREY,
                                     attainable_yield)

DISCOUNT = 0.08      # real discount rate (editable); India farm hurdle ~8-12% real
HORIZON = 25         # years
# Maintenance scales with the garden's bearing: juvenile years cost a FRACTION of the
# full bearing-phase maintenance (TNAU coconut: ~Rs 8k/yr juvenile vs ~Rs 39k bearing).
# Charging full maintenance during gestation was the bug that made coconut look doomed.
JUVENILE_MAINT_FRAC = 0.3

# crop financial timing/costs (Rs/acre). establish = yr1 planting; maintain = annual.
# gestation = first-yield year; full = full-bearing year; life = economic life (yrs).
# Costs VALIDATED June 2026 (NHB DPRs, agrifarming/croplibrary project reports, TN
# district studies). For crops grown here as a COCONUT INTERCROP (pepper, nutmeg,
# cocoa, vanilla) establishment uses the palms as standards + shared irrigation, so it
# is far below standalone (pepper standalone ~Rs 1-1.5L vs intercrop ~Rs 30k). Full-sun
# crops (pomegranate, grapes, dragon) carry their own drip/trellis/fencing. See ADR-011.
CROP_FIN = {
    "Black pepper": {"establish": 30000,  "maintain": 35000, "gestation": 3, "full": 7,  "life": 20},  # intercrop
    "Nutmeg":       {"establish": 50000,  "maintain": 40000, "gestation": 7, "full": 15, "life": 40},  # intercrop
    "Cocoa":        {"establish": 35000,  "maintain": 30000, "gestation": 3, "full": 7,  "life": 30},  # intercrop
    "Vanilla":      {"establish": 80000,  "maintain": 60000, "gestation": 3, "full": 6,  "life": 12},  # labour-intensive
    "Pomegranate":  {"establish": 180000, "maintain": 90000, "gestation": 3, "full": 5,  "life": 18},  # drip+fence+borewell
    "Guava":        {"establish": 50000,  "maintain": 25000, "gestation": 2, "full": 5,  "life": 20},
    "Mango":        {"establish": 40000,  "maintain": 20000, "gestation": 5, "full": 10, "life": 40},
    "Grapes":       {"establish": 200000, "maintain": 90000, "gestation": 2, "full": 4,  "life": 20},
    "Dragon fruit": {"establish": 300000, "maintain": 50000, "gestation": 2, "full": 4,  "life": 18},  # concrete poles
    # annual / quick-cycle crops: bear every year, no gestation lock-up
    "Ginger":       {"establish": 0, "maintain": 150000, "gestation": 1, "full": 1, "life": HORIZON, "annual": True},  # seed-rhizome heavy
    "Banana":       {"establish": 0, "maintain": 130000, "gestation": 1, "full": 1, "life": HORIZON, "annual": True},  # TC+drip, NHB/TN ~1.3L
}

# overstorey financial timing. coconut = annual income; timber = lump at harvest.
OVERSTOREY_FIN = {
    # establish excludes land (owned); ~planting+fencing+prep. maintain = full BEARING
    # cost (Salem ~Rs 39k); juvenile years auto-scaled by JUVENILE_MAINT_FRAC.
    "coconut":    {"kind": "annual", "establish": 40000, "maintain": 39000, "gestation": 6, "full": 10, "life": HORIZON},
    "silver_oak": {"kind": "timber", "establish": 15000, "maintain": 3000,  "harvest": 18},
    "mahogany":   {"kind": "timber", "establish": 20000, "maintain": 4000,  "harvest": 15},
    "teak":       {"kind": "timber", "establish": 20000, "maintain": 4000,  "harvest": 18},
    "none":       {"kind": "none"},
}


def _ramp(t, gestation, full, life):
    """Bearing fraction in year t (1-indexed)."""
    if t < gestation or t > life:
        return 0.0
    if t >= full:
        return 1.0
    return (t - gestation + 1) / (full - gestation + 1)


def crop_cashflow(crop, growth, disease, horizon=HORIZON, full_rev=None):
    """Year-by-year net cash (Rs/acre) for an intercrop at this site.
    full_rev overrides the full-bearing gross revenue (used by Monte Carlo)."""
    fin = CROP_FIN[crop]
    if full_rev is None:
        _, yc, _ = attainable_yield(crop, growth, disease)     # site-adjusted central yield
        plo, phi = CROP_ECON[crop]["price"]
        full_rev = yc * (plo + phi) / 2
    cf = np.zeros(horizon)
    for i in range(horizon):
        t = i + 1
        ramp = _ramp(t, fin["gestation"], fin["full"], fin["life"])
        maint = fin["maintain"] * max(JUVENILE_MAINT_FRAC, ramp) if t <= fin["life"] else 0
        cost = (fin["establish"] if t == 1 else 0) + maint
        cf[i] = full_rev * ramp - cost
    return cf


def overstorey_cashflow(species_key, horizon=HORIZON, trees_acre=None,
                        nut_price=None, timber_cft=None, timber_price=None):
    """Overstorey net cash. Optional overrides (nut_price Rs/nut; timber_cft per tree;
    timber_price Rs/cft) let Monte Carlo sample the price/volume bands."""
    ok = SPECIES_TO_OVERSTOREY.get(species_key, "none")
    fin = OVERSTOREY_FIN[ok]
    cf = np.zeros(horizon)
    if fin["kind"] == "none":
        return cf
    if fin["kind"] == "annual":   # coconut
        e = OVERSTOREY_ECON["coconut"]
        nlo, nc, nhi = e["nuts_acre"]; plo, phi = e["price_per_nut"]
        full_rev = nc * (nut_price if nut_price is not None else (plo + phi) / 2)
        for i in range(horizon):
            t = i + 1
            ramp = _ramp(t, fin["gestation"], fin["full"], fin["life"])
            maint = fin["maintain"] * max(JUVENILE_MAINT_FRAC, ramp) if t <= fin["life"] else 0
            cost = (fin["establish"] if t == 1 else 0) + maint
            cf[i] = full_rev * ramp - cost
        return cf
    # timber: maintain each year, lump revenue at harvest year(s) within horizon
    e = OVERSTOREY_ECON[ok]
    n = trees_acre or e["trees_acre"]
    clo, cc, chi = e["cft_tree"]; plo, phi = e["price_cft"]
    cft = timber_cft if timber_cft is not None else cc
    pcft = timber_price if timber_price is not None else (plo + phi) / 2
    lump = n * cft * pcft
    for i in range(horizon):
        t = i + 1
        cost = (fin["establish"] if t == 1 else 0) + fin["maintain"]
        rev = lump if (t % fin["harvest"] == 0) else 0.0   # replanting cycle within horizon
        cf[i] = rev - cost
    return cf


def npv(cf, rate=DISCOUNT):
    return float(sum(c / (1 + rate) ** (i + 1) for i, c in enumerate(cf)))


def irr(cf):
    """Internal rate of return via bisection; None if no sign change / no root."""
    if npv(cf, 0.0) <= 0:           # never profitable undiscounted -> no positive IRR
        return None
    lo, hi = 0.0, 2.0
    if npv(cf, hi) > 0:             # extremely profitable; cap
        return hi
    for _ in range(100):
        mid = (lo + hi) / 2
        (lo, hi) = (mid, hi) if npv(cf, mid) > 0 else (lo, mid)
    return round((lo + hi) / 2, 4)


def payback(cf):
    """Simple (undiscounted) payback year; None if never recovers."""
    cum = np.cumsum(cf)
    idx = np.where(cum >= 0)[0]
    return int(idx[0] + 1) if len(idx) else None


def system_finance(species_key, intercrop, growth, disease, horizon=HORIZON,
                   rate=DISCOUNT, trees_acre=None):
    ov = overstorey_cashflow(species_key, horizon, trees_acre)
    ic = crop_cashflow(intercrop, growth, disease, horizon) if intercrop else np.zeros(horizon)
    sys = ov + ic
    return {
        "cashflow": sys, "overstorey_cf": ov, "intercrop_cf": ic,
        "npv": round(npv(sys, rate)), "irr": irr(sys), "payback_yr": payback(sys),
        "npv_overstorey": round(npv(ov, rate)), "npv_intercrop": round(npv(ic, rate)),
        "rate": rate, "horizon": horizon,
    }
