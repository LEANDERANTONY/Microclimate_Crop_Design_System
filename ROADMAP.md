# Roadmap

Build priorities for the agroforestry microclimate → suitability → design
system. Mirrors the staged, data-readiness-gated philosophy: build what the
available data can honestly support, defer what it cannot.

## Now: Align repo + harden the layer 1–3 core

Current baseline:

- `uv`-managed environment and lockfile, `src/` package layout
- physics layer (Beer–Lambert light, shelterbelt wind) — mechanistic, HIGH confidence
- XGBoost quantile models for temperature/VPD offsets with conformalised intervals
- leave-one-site-out validation (transferability test)
- disease layer on **two axes** (air-microclimate foliar + soil-water for soil-borne),
  with drainage as a design lever (ADR-004)
- envelopes + disease/variety params literature-calibrated (ADR-003); waterlogging
  data-calibrated & seasonal from SoilGrids+CGWB (ADR-005)
- two-axis suitability (`viability`) and inverse-design optimiser
- crop/disease/variety catalog anchored to Pattukkottai; ADRs 001–005

Highest-priority remaining work:

- keep documentation aligned with the repo's real state (done through ADR-005)
- expand the test baseline (now 11 tests) beyond smoke tests
- keep the confidence labelling honest (physics HIGH, borrowed-ML MODERATE, disease LOW)
- future extension: model coastal salinity (flagged in ADR-005)

Status: Layer 1–3 core calibrated; pivoting to real data

## Next: Real data for layer 1

- wire `src/agroforestry/data/load.py` to assemble borrowed microclimate labels
  (SoilTemp / ForestTemp / agroforestry datasets) + Earth Engine features
  (ERA5, Sentinel-2 LAI, SoilGrids, DEM)
- compute offsets (sub-canopy − ambient) as the supervised targets
- re-run leave-one-site-out / leave-one-climate-out to measure real transferability
- recalibrate the physics extinction coefficients for coconut/timber overstoreys

Status: In progress (planned next)

## Later: Disease calibration + economics layer

- replace literature-shaped infection parameters with values fitted to observed
  incidence once field/extension data is available
- upgrade leaf-wetness from the daily proxy to hourly RH>90% / dew-point models
- implement `src/agroforestry/economics.py` (layers 4–5) per `docs/economics_layer.md`:
  reference-yield × suitability × (1−disease loss); trailing-price band; surplus
  + market-distance penalty; risk-adjusted profit

Status: Designed, not started

## Future: Field validation and research extensions

- year-2 TMS-4 sensor campaign to locally validate/calibrate the MODERATE/LOW layers
- group-aware uncertainty tooling under `src/agroforestry/uncertainty/`
- Bayesian-optimisation / NSGA-II inverse design replacing the grid search
- physics-informed (PINN) coupled energy/water balance once data justifies it
- spatial (GNN) within-field microclimate gradients if multi-node sensing arrives

Status: Deferred until layer-1 real data and reproducibility work is stable
