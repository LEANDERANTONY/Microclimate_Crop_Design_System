# ADR-012 — Skill-scored transfer validation + physics-guided hybrid (tested)

- **Status:** Accepted
- **Date:** 2026-06-10
- **Follows:** [[ADR-006]] (real-data LOSO), [[ADR-007]] (OOD flag), [[ADR-008]]/[[ADR-009]] (the macroclimate-transfer gap)

## Context

A review flagged two gaps in how the offset models were validated and reported:

1. **No baseline.** We reported LOSO MAE (e.g. dT_mean 0.28 °C) but never against a
   naive baseline, so it was impossible to tell whether the model was learning
   structure or merely recovering a near-constant offset (dT_mean's offset has SD
   ~1.0 °C, so a small MAE can be unimpressive).
2. **Only within-climate transfer was tested.** LOSO holds out a *site* but the
   other sites are usually the *same climate*. The project's actual claim — and its
   actual application (semi-arid warm-night Tamil Nadu) — is transfer ACROSS
   macroclimates, which LOSO never isolates.

A third question: would a **physics-guided hybrid** (a linear/extrapolating backbone
+ ML on the residual) transfer better than the pure tree, since tree models cannot
extrapolate beyond the training range (they go flat)?

## Decision / what was done

- **`validation.py` rewritten** to report, every fold: skill vs a train-mean
  baseline (`1 − MAE_model/MAE_baseline`), out-of-sample R², and the fold-MAE
  distribution (p10/p50/p90). Added **`loco` (leave-one-climate-out)** and a
  `climate_zone()` tagger (Borneo humid forest / Mediterranean Spain / Borneo
  oil-palm open canopy, from site_id prefixes). `loso`/`loco` take a `model_factory`
  so any model can be swapped in.
- **`HybridQuantileModel`** added (`models.py`): a standardised **Ridge backbone on a
  parsimonious, in-range, physically-signed feature set** (default: `canopy_cover`
  alone — the core De Frenne buffering term) + XGBoost quantile regressors on the
  residual, with **physical clipping** of the backbone to the observed offset range
  (±25 % pad) and group-aware CQR. Drop-in for `QuantileModel`.
- Metrics regenerated: `reports/loso_metrics.json`, `reports/loco_metrics.json`
  (`scripts/run_validation.py`), both models, all targets. 26 tests pass.

## Findings (the important part)

**Within-climate (LOSO, 80-site sample) — the model genuinely learns.**

| target | model | MAE | skill vs baseline | R²_oos | coverage |
|---|---|---|---|---|---|
| dT_mean | pure XGB | 0.329 | **+27 %** | 0.23 | 0.75 |
| dT_mean | hybrid   | 0.325 | **+28 %** | 0.24 | 0.79 |
| dT_max  | pure XGB | 1.40  | +19 % | −0.02 | 0.77 |
| dVPD    | pure XGB | 0.085 | +33 % | 0.04 | 0.76 |

Skill is solidly positive → the model is not just recovering a constant offset.
But R² is low (≈0 for dT_max), so the *daily/site-level* offset remains hard;
the value is real but modest, and should be reported as such.

**Cross-climate (LOCO) — transfer degrades, and fails for the most dissimilar regime.**

| held-out regime | pure-XGB dT_mean skill | coverage |
|---|---|---|
| Borneo forest | +22 % | — |
| oil-palm open canopy | −19 % | — |
| **Mediterranean Spain** | **−16 % (worse than baseline)** | — |

Interval coverage **collapses from ~0.77 (LOSO) to 0.24–0.46 (LOCO)** — the conformal
intervals, calibrated within-climate, badly under-cover out-of-climate.

**The hybrid does NOT rescue cross-macroclimate transfer.** It ties/marginally beats
the pure tree *in-distribution* (dT_mean LOSO 0.325 vs 0.329; Borneo-forest LOCO 0.47
vs 0.51), but on the held-out cool Mediterranean climate it is **worse** (dT_max 6.3
vs 3.2): the offset *magnitude* is regime-dependent, so a tropical-trained linear
backbone overshoots into a cool climate. Clipping and a single-feature backbone bound
the damage but do not remove it. The tree's flat extrapolation is safer there.

## Consequences

- **`QuantileModel` stays the default.** `HybridQuantileModel` is kept as a tested,
  documented alternative — competitive in-distribution, and likely useful **once a
  warm-night / dry-zone training source is added** (its backbone can then interpolate
  rather than extrapolate). It is not adopted as default because it does not improve —
  and slightly harms — the cross-climate direction that matters for Anaikadu.
- **Honest headline for the paper:** within-climate transfer works (positive skill,
  calibrated intervals); cross-macroclimate transfer is currently unsolved with open
  data (negative skill + coverage collapse on a held-out climate). This *quantifies*
  why the warm-night semi-arid target is genuine extrapolation and why an on-plot
  logger (or a dry-zone tropical training site) is the gating item — not a nice-to-have.
- Report **skill + R² + LOCO**, not bare MAE, going forward. The 0.28 °C two-climate
  full LOSO (ADR-006) remains valid as the within-/between-forest-climate number; LOCO
  is the stricter regime-holdout companion.

## Next

- Fold a warm-night / semi-arid or South-Asian dry-zone source into train+test
  (SoilTemp India request; the user's plot logger) and re-run LOCO — the one change
  that could move cross-climate skill positive and let the hybrid interpolate.
- Group/Mondrian-conformal calibration *per climate* to restore out-of-climate coverage.
