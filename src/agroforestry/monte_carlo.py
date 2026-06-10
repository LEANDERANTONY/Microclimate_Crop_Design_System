"""Layer 6 -- Monte Carlo uncertainty propagation.

Turns every point estimate into a distribution. Per draw we sample the genuinely
uncertain inputs and push them through the SAME chain (microclimate -> viability ->
yield/price -> finance):

  * temperature offset under the canopy  (the LOW-confidence extrapolation band)
  * attainable yield                      (reference-yield band x suitability)
  * crop price                            (mandi price band)
  * coconut nut price / timber volume+price (overstorey bands)

Output: NPV distribution per design -> P10/P50/P90, mean, and probability of loss.
Honest by construction: a design with high mean NPV but a fat negative tail is shown
as risky, not just "best".
"""
import numpy as np
from agroforestry.suitability import viability
from agroforestry.economics import CROP_ECON, OVERSTOREY_ECON, SPECIES_TO_OVERSTOREY, attainable_yield
from agroforestry.finance import crop_cashflow, overstorey_cashflow, npv, irr, DISCOUNT, HORIZON


def _tri(lo, mode, hi, rng):
    """Triangular sample, robust to degenerate (collapsed) bounds."""
    if hi <= lo:
        return lo
    mode = min(max(mode, lo), hi)
    return float(rng.triangular(lo, mode, hi))


def simulate(predictor, macro, context, species, lai, intercrop,
             n=3000, seed=0, rate=DISCOUNT, waterlogging=0.70):
    rng = np.random.default_rng(seed)
    design = {"species": species, "lai": lai, "wb_height": 10, "wb_porosity": 0.45}
    micro = predictor.predict_micro(design, macro, context)
    over_key = SPECIES_TO_OVERSTOREY.get(species, "none")

    # temperature band -> absolute under-canopy t_max bounds
    dlo, dhi = micro["intervals"]["dT_max"]
    tmax_lo = macro["t_max"] + dlo
    tmax_hi = macro["t_max"] + dhi
    base_tmax, base_tmean = micro["t_max"], micro["t_mean"]

    npvs = np.empty(n)
    for k in range(n):
        # 1. temperature draw -> shift micro -> viability
        tmax_draw = _tri(tmax_lo, base_tmax, tmax_hi, rng)
        delta = tmax_draw - base_tmax
        m = {**micro, "t_max": base_tmax + delta, "t_mean": base_tmean + delta}
        if intercrop:
            v = viability(intercrop, m, rain_mm_day=0.0, waterlogging=waterlogging)
            g, d = v["growth"], v["disease_risk"]
            ylo, yc, yhi = attainable_yield(intercrop, g, d)     # site-adjusted band
            Y = _tri(ylo, yc, yhi, rng)
            plo, phi = CROP_ECON[intercrop]["price"]
            P = _tri(plo, (plo + phi) / 2, phi, rng)
            ic_cf = crop_cashflow(intercrop, g, d, horizon=HORIZON, full_rev=Y * P)
        else:
            ic_cf = np.zeros(HORIZON)

        # 2. overstorey draws
        if over_key == "coconut":
            nlo, nhi = OVERSTOREY_ECON["coconut"]["price_per_nut"]
            ov_cf = overstorey_cashflow(species, nut_price=_tri(nlo, (nlo + nhi) / 2, nhi, rng))
        elif OVERSTOREY_ECON.get(over_key, {}).get("kind") == "timber":
            e = OVERSTOREY_ECON[over_key]
            clo, cc, chi = e["cft_tree"]; plo, phi = e["price_cft"]
            ov_cf = overstorey_cashflow(species, timber_cft=_tri(clo, cc, chi, rng),
                                        timber_price=_tri(plo, (plo + phi) / 2, phi, rng))
        else:
            ov_cf = np.zeros(HORIZON)

        sys = ov_cf + ic_cf
        npvs[k] = npv(sys, rate)

    p10, p50, p90 = np.percentile(npvs, [10, 50, 90])
    # NPV>0 at the hurdle rate is equivalent to IRR>hurdle for these cashflows,
    # so prob_profit = 1 - prob_loss (no separate, inconsistent IRR filter).
    return {
        "npvs": npvs, "mean": float(npvs.mean()), "p10": float(p10), "p50": float(p50),
        "p90": float(p90), "prob_loss": float((npvs < 0).mean()),
        "prob_strong": float((npvs > 250_000).mean()),   # chance of a clearly good outcome
        "n": n, "rate": rate,
    }
