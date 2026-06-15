# Paper 1 — Uncertainty-aware agroforestry microclimate prediction

**Central claim (one sentence).** Controllable agroforestry design variables plus
macroclimate predict under-canopy microclimate (temperature, VPD, light, wind)
with calibrated uncertainty, and the framework *explicitly detects when it is
extrapolating across climates* — with a few local observations sufficient to
restore calibration.

This is the foundation paper. It makes **no** crop, disease, or economic claims —
those are Papers 2 and 3.

## Scope

- Forward predictor: design + macroclimate → {under-canopy T_mean/T_max, VPD,
  light/PAR, in-field wind}.
- Light = Beer–Lambert, wind = shelterbelt aerodynamics (physics, HIGH
  confidence). Temperature/VPD offsets = gradient-boosted quantile models
  (MODERATE), with a physics-prior+residual hybrid as a tested comparator.
- Uncertainty: conformal intervals; group-aware (cross-site) calibration;
  few-shot Mondrian recalibration for out-of-climate coverage.
- Transfer honesty: OOD flag; leave-one-climate-out demonstrating where transfer
  fails; model-family benchmark showing failure is a data-regime property, not an
  estimator flaw.

## Datasets

- **Training (in-set):** SAFE Borneo + La Jarda Spain forest loggers (two
  macroclimates) + SAFE oil-palm open-canopy rasters; Earth Engine features
  (ERA5, SoilGrids, DEM, MODIS, ETH canopy height).
- **To add (closes the warm-night-tropical gap):** a warm-tropical training
  source — SoilTemp raw loggers and/or the pan-tropical understory TMS set.
- **Pre-registered external held-out test:** one frozen warm-climate analogue,
  chosen and locked *before* scoring. Candidates and access terms in
  `docs/external_validation_datasets.md`.

## Maps to core (do not duplicate here)

- Modules: `physics.py`, `features.py`, `models.py`, `models_benchmark.py`,
  `validation.py`, `predict.py`, `data/`, `config.py`.
- Scripts: `run_pipeline.py`, `run_validation.py`, `benchmark_models.py`,
  `mondrian_conformal.py`, `build_real_dataset.py`, `make_paper_figures.py`.
- Result snapshots: `reports/loso_full_metrics.json`, `reports/loco_metrics.json`,
  `reports/mondrian_metrics.json`, `reports/benchmark_metrics.json`.
- Decisions: ADR-001, 006–009, 012, 013, 014.

## Validation protocol (the paper's spine)

1. Within-climate LOSO (skill-scored).
2. Leave-one-climate-out (the honest negative: transfer degrades; intervals lose
   calibration).
3. Few-shot recalibration: ~5–25 in-regime points restore out-of-climate
   coverage.
4. **Frozen external test** on the pre-registered warm-climate dataset.

## Target venues

Agricultural and Forest Meteorology (IF 5.7, Q1) — best scope fit; or Ecological
Informatics (IF 7.3, Q1) — best fit if foregrounding ML/UQ/transfer. The novelty
carried here is the *agroforestry design-as-controllable-variable framing + OOD-
aware transfer*, not the offset method itself.

## Open items

- [ ] Acquire a warm-tropical training source (SoilTemp request / pan-tropical TMS).
- [ ] Pre-register + freeze the external test dataset.
- [ ] Carve Paper-1 sections out of the all-in-one `docs/manuscript/manuscript.md`.
- [ ] `configs/` — freeze the exact run configs that produced the snapshots.
