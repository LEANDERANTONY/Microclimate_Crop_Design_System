# ADR-014 — Model-family benchmark, keeping XGBoost, and few-shot conformal recalibration

- **Status:** Accepted
- **Date:** 2026-06-11
- **Follows:** [[ADR-012]] (LOSO/LOCO transfer validation + physics-prior hybrid)

## Context

ADR-012 showed cross-macroclimate transfer fails for the XGBoost-quantile offset model and
that a physics-prior hybrid does not rescue it, and flagged two open questions:
(a) is the failure specific to gradient boosting, or a property of the data regime? and
(b) ADR-012 named "per-climate (Mondrian) conformal calibration" as a next step to restore
out-of-climate interval coverage. A subsequent design discussion also raised whether other
model families — domain-adversarial nets, mixture-of-experts, Gaussian processes,
meta-learning — could close the gap. This ADR records the decisions taken in response.

## Decision

**1. Benchmark six model families under the same validation, and keep XGBoost as the
pipeline default.** We implemented and packaged (`src/agroforestry/models_benchmark.py`,
tested in `tests/test_benchmark.py`) a common-interface comparison — Ridge, Random Forest,
a **Gaussian process** (ARD-RBF + white noise, distance-aware predictive variance), a
non-neural **mixture-of-experts** (one Ridge expert per training regime + a softmax distance
gate, uncertainty from expert disagreement), the production **XGBoost-quantile** model, and
the **physics-prior hybrid** — scored by skill and interval coverage under both a grouped
site holdout (in-distribution) and leave-one-climate-out (`scripts/benchmark_models.py` →
`reports/benchmark_metrics.json`).

**2. Neural variants are out of scope** (domain-adversarial representation learning, neural
residual networks): a three-regime dataset overfits them, domain-invariant representations
risk erasing genuinely regime-dependent buffering, and the host has no deep-learning stack.
They are recorded as future work, to revisit once more climate regimes exist.

**3. Few-shot conformal recalibration is the adopted out-of-climate uncertainty fix**
(`scripts/mondrian_conformal.py` → `reports/mondrian_metrics.json`): recalibrate the
conformal width on a few points drawn from the target regime, rather than retrain. This is
the practical, data-light form of the "Mondrian conformal" step ADR-012 deferred, and it is
framed as non-parametric few-shot domain adaptation.

## Findings (evidence)

**Model-family benchmark** (skill vs mean-offset baseline / out-of-climate interval coverage,
averaged over dT_max, dT_mean, dVPD):

| Model | In-distribution skill | LOCO skill | LOCO coverage |
|---|---|---|---|
| Ridge (linear) | +34 % | **−324 %** | 0.31 |
| Random forest | +42 % | −7 % | 0.31 |
| **Gaussian process** | +36 % | **+7 %** | **0.62** |
| Mixture-of-experts | +19 % | −82 % | 0.63 |
| XGBoost (default) | +8 % | −17 % | 0.49 |
| Physics-prior hybrid | +9 % | −19 % | 0.58 |

- **In-distribution every family is skilful** → the within-climate signal is real and
  estimator-agnostic. (The in-distribution column is a single grouped 20 % site holdout for
  *between-model* comparison; the robust within-climate figure is the full LOSO of ADR-012 /
  manuscript Table 3, XGBoost dT_mean +49 %.)
- **Under climate shift the families diverge**: linear and mixture-of-experts extrapolate
  catastrophically; tree models are bounded but lose nearly all skill; **only the Gaussian
  process keeps non-negative cross-climate skill and the best-calibrated out-of-climate
  intervals**, because its predictive variance grows with distance from the training data.
  The mixture-of-experts reaches comparable coverage only by inflating intervals through
  expert disagreement, not by predicting better.
- **No family transfers across the warm-night gap** → the limitation is the **data regime,
  not the estimator**. This is the benchmark's headline and the scientific justification for
  the honesty-first posture.

**Few-shot recalibration**: ~5–25 in-regime calibration points restore dT_mean out-of-climate
coverage from ~0.08 to ~0.80 across held-out climates.

## Consequences

- **XGBoost-quantile + CQR remains the production offset model.** It is bounded out-of-climate
  (unlike linear/MoE), already drives the whole economics/finance chain, and swapping it would
  ripple through every downstream number for no decision benefit. The **Gaussian process is
  retained as the transfer-honest reference** in the benchmark (and is the natural candidate
  to revisit if/when an in-regime training source is added).
- The benchmark + few-shot result strengthen the paper: manuscript §2.10 (methods), §3.4
  (results, Table 6, Fig. 7), §3.3 (few-shot, Table 5, Fig. 6), Discussion and Conclusion.
- The decisive remedy is unchanged and now triply supported (ADR-008/009/012/014): **in-regime
  data** (warm-night/dry-zone source, or the user's own plot logger) — no model choice
  substitutes for it.

## Next

- Re-run the benchmark once a warm-night/dry-zone regime is in the training set; expect the GP
  (and the hybrid's backbone) to benefit most as the target moves from extrapolation toward
  interpolation.
- Revisit meta-learning / neural processes only when the number of regimes is large enough to
  meta-train.
