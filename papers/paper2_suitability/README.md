# Paper 2 — Microclimate-aware crop suitability & inverse design

**Central claim.** Predicted under-canopy microclimate (from Paper 1) can be
translated into robust, interpretable crop-suitability rankings, and an inverse
optimizer can identify the canopy/windbreak/management design that produces
conditions suitable for a chosen crop. Disease enters as **one modifier** of
suitability, not the endpoint.

Depends on Paper 1 being accepted/validated — it consumes Paper 1's predictions
and inherits their uncertainty.

## Scope

- Suitability: fuzzy limiting-factor `viability()` against literature/ECOCROP
  envelopes (decision support, not yield prediction).
- Disease: two-axis (foliar-air + soil-water/waterlogging) mechanistic pressure ×
  variety susceptibility (disease triangle). LOW confidence / literature-shaped.
- Inverse design: search overstorey × canopy × windbreak (× drainage) to reach a
  crop's target envelope; **must carry intervals and refuse confident
  recommendations in OOD regions**.

## Maps to core

- Modules: + `suitability.py`, `disease.py`, `optimize.py`.
- Scripts: `inverse_anaikadu.py`, `pattukkottai_run.py`, `run_site.py`.
- Reports: `crop_canopy_reachability.*`, `crop_catalog_*`, `crop_envelopes_*`,
  `disease_params_sourced.md`, `soil_water_thanjavur.md`.
- Decisions: ADR-002, 003, 004, 005.

## Validation targets

Published disease observations, agronomic suitability datasets, extension
recommendations, independent field studies. Frame as decision support; do not
claim actual yield or farm success.

## Target venues

Computers and Electronics in Agriculture / Ecological Informatics / Smart
Agricultural Technology.

## Open items

- [ ] Validate suitability rankings against an independent source.
- [ ] Replace grid-search inverse design with Bayesian-opt / NSGA-II (later).
- [ ] Carry Paper-1 prediction intervals through into suitability scores.
