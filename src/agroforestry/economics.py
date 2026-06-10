"""Layer 4-5 -- economics (staged, transparent, NOT trained).

Per docs/economics_layer.md: reuse the growth + disease outputs as multipliers on
reference yield, represent everything as a BAND, and surface the margin-vs-market-risk
trade-off. Nothing here is a trained model; all constants are editable and confidence-
flagged. Crop yields/prices come from reports/economics_inputs_sourced.md; coconut and
timber from web-sourced Tamil Nadu / India figures (LOW confidence -- farm timber prices
vary widely; treat as order-of-magnitude, refine with local quotes).

Money in INR. Yields per ACRE per YEAR (timber annualised over its rotation).
"""

# ---- intercrop economics: yield kg/acre (lo, central, hi); price Rs/kg (lo, hi) ----
# yields/prices: reports/economics_inputs_sourced.md (TNAU/ICAR/NHB/Agmarknet bands).
# annual_cost Rs/acre/yr is a rough variable+amortised-establishment figure (LOW conf).
CROP_ECON = {
    "Black pepper": {"yield": (250, 400, 600),   "price": (300, 700),    "cost": 40000, "perishable": False, "market": "very favourable", "risk": "moderate"},
    "Nutmeg":       {"yield": (250, 400, 700),   "price": (600, 900),    "cost": 30000, "perishable": False, "market": "neutral-favourable", "risk": "moderate"},
    "Cocoa":        {"yield": (250, 350, 500),   "price": (250, 600),    "cost": 40000, "perishable": False, "market": "strongly favourable", "risk": "moderate"},
    "Vanilla":      {"yield": (60, 100, 150),    "price": (4000, 12000), "cost": 60000, "perishable": False, "market": "undersupplied", "risk": "very high"},
    "Ginger":       {"yield": (6000, 8000, 12000), "price": (30, 160),   "cost": 120000, "perishable": False, "market": "favourable", "risk": "high (volatile)"},
    "Banana":       {"yield": (12000, 20000, 25000), "price": (8, 25),   "cost": 90000, "perishable": True,  "market": "high local surplus", "risk": "low (low margin)"},
    "Pomegranate":  {"yield": (4000, 5000, 7000), "price": (40, 120),    "cost": 90000, "perishable": False, "market": "favourable (TN deficit)", "risk": "moderate"},
    "Guava":        {"yield": (7000, 10000, 15000), "price": (15, 40),   "cost": 40000, "perishable": True,  "market": "moderate surplus", "risk": "low"},
    "Mango":        {"yield": (3000, 4500, 7000), "price": (25, 80),     "cost": 35000, "perishable": True,  "market": "seasonal surplus", "risk": "moderate"},
    "Grapes":       {"yield": (5000, 7000, 8000), "price": (30, 90),     "cost": 150000, "perishable": True, "market": "neutral-favourable", "risk": "moderate"},
    "Dragon fruit": {"yield": (4000, 8000, 10000), "price": (80, 200),   "cost": 120000, "perishable": True, "market": "amber (supply growing)", "risk": "high (price falling)"},
}

# ---- overstorey economics ----
# Coconut: annual nut income. ~70 tall palms/acre x ~70-80 nuts = ~5000 nuts/acre/yr
# (TN state avg ~4,659 nuts/acre; well-managed higher). Price Rs/nut farm-gate, volatile
# (2024 spike to ~Rs 11-15/nut; historic Rs 7-12). Source: TNAU, procurementresource 2024.
# Timber: annualised value = cft/tree x Rs/cft / rotation_yr, x trees/acre. Farm-grown
# prices are well below forest auction; values here are CONSERVATIVE and LOW confidence.
OVERSTOREY_ECON = {
    # nuts/acre and bearing-phase cost VALIDATED: TNAU cost-of-cultivation + Salem
    # District study 2023-24 (6,500-7,000 nuts/acre; bearing maintenance ~Rs 39k;
    # net ~Rs 15.5k/acre at ~Rs 8/nut; BCR 1.39). Price band widened for 2024-25 highs
    # (copra ~Rs 140-153/kg; farm-gate nuts ~Rs 15-18+). See QA note / ADR-010.
    "coconut": {"kind": "annual", "nuts_acre": (4800, 6000, 7500), "price_per_nut": (8, 18), "cost": 39000},
    # timber: (cft/tree lo,c,hi), Rs/cft (lo,hi), rotation yr, default trees/acre as overstorey
    "silver_oak": {"kind": "timber", "cft_tree": (6, 10, 15),  "price_cft": (300, 700),   "rotation": 18, "trees_acre": 120, "cost": 8000},
    "mahogany":   {"kind": "timber", "cft_tree": (12, 20, 30), "price_cft": (1000, 1500), "rotation": 15, "trees_acre": 120, "cost": 12000},
    "teak":       {"kind": "timber", "cft_tree": (10, 14, 18), "price_cft": (1500, 3000), "rotation": 18, "trees_acre": 120, "cost": 12000},
    "none":       {"kind": "none"},
}

# map config SPECIES keys -> overstorey economics keys
SPECIES_TO_OVERSTOREY = {
    "coconut_wide": "coconut", "coconut_close": "coconut",
    "silver_oak": "silver_oak", "mahogany": "mahogany",
    "teak_leaf": "teak", "teak_bare": "teak", "none": "none",
}


def attainable_yield(crop, growth, disease):
    """Reference yield bent by suitability + disease (docs/economics_layer.md).
    growth, disease in 0..100. Returns (lo, central, hi) kg/acre/yr."""
    lo, c, hi = CROP_ECON[crop]["yield"]
    f = (growth / 100.0) * (1 - disease / 100.0)
    return (lo * f, c * f, hi * f)


def crop_margin(crop, growth, disease):
    """Risk-aware intercrop margin: expected and downside (Rs/acre/yr).
    expected = central_yield x mid_price - cost.  downside = lo_yield x lo_price - cost."""
    e = CROP_ECON[crop]
    ylo, yc, yhi = attainable_yield(crop, growth, disease)
    plo, phi = e["price"]
    pmid = (plo + phi) / 2
    expected = yc * pmid - e["cost"]
    downside = ylo * plo - e["cost"]
    upside = yhi * phi - e["cost"]
    return {"expected": round(expected), "downside": round(downside), "upside": round(upside),
            "yield_central": round(yc), "price_mid": round(pmid, 1),
            "market": e["market"], "risk": e["risk"], "perishable": e["perishable"]}


def overstorey_margin(species_key, trees_acre=None):
    """Annual (or annualised-timber) overstorey income, Rs/acre/yr: expected + band."""
    ok = SPECIES_TO_OVERSTOREY.get(species_key, "none")
    o = OVERSTOREY_ECON[ok]
    if o["kind"] == "none":
        return {"expected": 0, "downside": 0, "upside": 0, "kind": "none", "note": "open field / no overstorey income"}
    if o["kind"] == "annual":   # coconut
        nlo, nc, nhi = o["nuts_acre"]; plo, phi = o["price_per_nut"]; cost = o["cost"]
        return {"expected": round(nc * (plo + phi) / 2 - cost), "downside": round(nlo * plo - cost),
                "upside": round(nhi * phi - cost), "kind": "coconut",
                "note": f"~{nc:.0f} nuts/acre x Rs{(plo+phi)/2:.0f}/nut - cost"}
    # timber: annualised over rotation
    n = trees_acre or o["trees_acre"]
    clo, cc, chi = o["cft_tree"]; plo, phi = o["price_cft"]; rot = o["rotation"]; cost = o["cost"]
    ann = lambda cft, p: (cft * p * n) / rot - cost
    return {"expected": round(ann(cc, (plo + phi) / 2)), "downside": round(ann(clo, plo)),
            "upside": round(ann(chi, phi)), "kind": "timber",
            "note": f"{n} trees/acre x {cc:.0f} cft x Rs{(plo+phi)/2:.0f}/cft / {rot}yr (annualised), LOW conf"}


def system_margin(species_key, intercrop, growth, disease, trees_acre=None):
    """Whole agroforestry system: overstorey income + intercrop margin (Rs/acre/yr)."""
    ov = overstorey_margin(species_key, trees_acre)
    ic = crop_margin(intercrop, growth, disease) if intercrop else {"expected": 0, "downside": 0, "upside": 0}
    return {"overstorey": ov, "intercrop": ic,
            "system_expected": ov["expected"] + ic["expected"],
            "system_downside": ov["downside"] + ic["downside"]}
