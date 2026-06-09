# ADR-007 — Out-of-distribution flag for off-canopy-type designs (coconut)

- **Status:** Accepted
- **Date:** 2026-06

## Context

The offset models are trained on *observed* forest microclimate + remote-sensing
features (SAFE Borneo + La Jarda Spain). The intended *application* is intercropping
under **coconut** — a tall, sparse, open palm canopy that is architecturally unlike
the closed forest in the training data (Hardwick 2015: oil palm runs up to 6.5 °C
warmer than forest). Predicting the learned offset for coconut is extrapolation.

## Decision

Add an **out-of-distribution (OOD) flag**:

- `QuantileModel` stores training feature ranges (`feat_lo/feat_hi`) and exposes
  `ood_score(X)` = fraction of features outside the training range.
- `Predictor.predict_micro` returns `ood_score`, `extrapolating` (> 0.15), and
  `offset_confidence` ("LOW (extrapolation)" vs "MODERATE"). Physics (light/wind)
  stays HIGH confidence regardless — it is mechanistic, not learned.

## Finding (important)

On the real forest-trained model, a coconut design flags `ood ≈ 0.58`; even a
dense design flags `≈ 0.33`. The over-flagging is itself informative: it exposes a
**design→feature mismatch** — `predict.build_feature_row` fabricates a design's
features with crude proxies (`canopy_height = LAI × 5` → 5–15 m; NDVI/FAPAR from
cover), while the model learned from **real satellite features** (forest canopy
13–55 m). So a model trained on *observed* features cannot yet be trusted to score
*hypothetical designs* until the design→feature mapping emits realistic per-canopy
values.

Fixing the height proxy (realistic per-species `height_m`) keeps coconut flagged
(genuine: sparse low-LAI palm, ood ≈ 0.5) but exposed a second mismatch: the
**synthetic demo context is on different scales than the real training features** —
most concretely `clay` is passed as percent (~35) while the SoilGrids training
feature is g/kg (281–419); `soc`, `elevation`, `wind` likewise. So real-trained
models require **real, correctly-scaled Pattukkottai inputs** (ERA5 macro, SoilGrids
clay in g/kg, real elevation, realistic canopy) — not the synthetic demo defaults.
That is the precondition for the Pattukkottai end-to-end ("option 3") run.

## Consequences

- The LOSO result (predicting at observed sites) stands — that validation is sound.
- Applying the model to hypothetical designs is flagged honestly; coconut is
  genuine extrapolation and the ML offset there is LOW confidence.
- For the coconut **intercrop** decision, rely on the **physics layer** (light via
  Beer–Lambert, wind via shelterbelt) — HIGH confidence and design-appropriate.

## Next

1. Add **oil-palm / palm-canopy training data** (Hardwick 2015 SAFE forest+oil-palm
   loggers) so the open-palm regime is in-distribution.
2. Improve `build_feature_row` to emit **realistic per-canopy feature values**
   (coconut ≈ LAI 1.5, height ~18 m, NDVI ~0.6) instead of crude proxies.
3. Ultimate fix: the user's own coconut-farm sensors (year 2).
