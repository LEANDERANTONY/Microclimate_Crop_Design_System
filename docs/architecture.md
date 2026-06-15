# Architecture

The system is a **chain of six layers**, each matched to the simplest method its
physics and data support. Decomposition (not one monolithic model) is the core
design decision — see `ADR-001`. Every layer carries an explicit confidence level
and the learned parts are validated for transfer and flagged when extrapolating.

```
Macroclimate + Farm design
        │   (design = controllable: overstorey, spacing/LAI, windbreak, drainage, variety, timing)
        ▼
[1] Microclimate   ──► shade/light, under-canopy temp, humidity/VPD, wind, leaf-wetness
        │              physics HIGH · learned offset MODERATE (OOD-flagged)
        ▼
[2] Disease        ──► realized risk = environmental pressure × variety susceptibility (two axes)
        ▼
[3] Viability      ──► growth fit (limiting factor) × (1 − disease risk)
        ▼
[4] Economics      ──► reference yield × growth × (1 − disease) × banded price − validated cost
        ▼
[5] Finance        ──► 25-yr cash-flow (gestation/bearing/harvest timing) → NPV / IRR / payback
        ▼
[6] Uncertainty    ──► Monte Carlo over offset+yield+price+timber bands → NPV distribution, P(loss)

Inverse design: search overstorey/canopy/windbreak/drainage to maximise risk-aware profit.
```

## Layer 1 — Microclimate (`physics.py`, `models.py`, `predict.py`)

Predict the **offset** from the ambient macroclimate, because offsets transfer across
climates. Light and wind are mechanistic (Beer–Lambert; shelterbelt aerodynamics) —
HIGH confidence, no ML. Temperature and VPD offsets are learned with **XGBoost quantile
regressors** (`reg:quantileerror`) + **conformalised quantile regression** for calibrated
intervals. `QuantileModel` stores training feature ranges and exposes an **`ood_score`**;
`Predictor` returns `extrapolating` / `offset_confidence` so a design outside the training
cloud (e.g. open coconut canopy vs closed-forest training) is flagged LOW rather than
silently extrapolated (ADR-007). The design→feature mapping emits **real Tamil Nadu
satellite values** per canopy type (`CANOPY_FEATURES_TN`) rather than fabricated proxies —
this confirmed the coconut OOD is genuine, not an artefact (ADR-013). Trained on real SAFE
Borneo + La Jarda Spain loggers plus SAFE oil-palm rasters (ADR-006/008); ambient reference
is ERA5 *atmospheric* free-air, not ERA5-Land (ADR-006). A physics-prior (extrapolating
linear backbone) + ML-residual **hybrid** (`HybridQuantileModel`) was built and tested; it
ties the pure tree in-distribution but does not improve cross-climate transfer, so the pure
quantile model remains the default (ADR-012).

## Layer 2 — Disease (`disease.py`)

`realized_risk = environmental_pressure × variety_susceptibility`, across **two independent
axes** (ADR-004): an **air-microclimate axis** (foliar; temperature × leaf-wetness or
humidity, with rain-splash) and a **soil-water axis** (soil-borne wilt/foot-rot; temperature
× effective waterlogging = site waterlogging × drainage mitigation, *not* air RH). Drainage
is a design lever; waterlogging is data-calibrated and seasonal (wet 0.70 / dry 0.36, ADR-005).
Parameters literature-sourced (ADR-003), MODERATE until field-calibrated.

## Layer 3 — Viability (`suitability.py`)

Growth fit = fuzzy trapezoidal membership against crop envelopes aggregated by the
**limiting factor** (Liebig). `viability = growth × (1 − disease_risk)`.

## Layer 4 — Economics (`economics.py`)

Staged, transparent, **not trained**: `attainable_yield = reference × growth × (1−disease)`;
banded price − validated annual cost; coconut (annual nut income) and **timber** (teak/
mahogany/silver-oak, annualised over rotation) as overstoreys; `system_margin` = overstorey
+ intercrop. Yields/prices from TNAU/ICAR/NHB + live Agmarknet; costs validated vs NHB DPRs
(ADR-010/011).

## Layer 5 — Finance (`finance.py`)

Multi-year cash-flow that respects **timing**: gestation + bearing ramp per crop, coconut
annual income, timber single harvest lump; maintenance scales with the bearing ramp
(`JUVENILE_MAINT_FRAC` — the fix for the coconut gestation-cost bug, ADR-010). `npv` (8% real
default), `irr` (bisection), `payback`, `system_finance`.

## Layer 6 — Uncertainty (`monte_carlo.py`)

Samples the genuinely uncertain inputs (temperature offset band, yield, price, timber
volume/price) and pushes each draw through the same chain → an NPV **distribution** with
P10/P50/P90, mean, and probability of loss. Honest by construction: a high-mean/fat-tail
design is shown as risky, not "best".

## Validation (`validation.py`)

Two protocols, every metric reported against a **mean-offset baseline** (skill = 1 −
MAE/baseline), so a low MAE on a low-variance target is not mistaken for skill. **Leave-one-
site-out (`loso`)** holds out an entire site per fold — full-LOSO within-climate transfer is
skilful (dT_mean MAE 0.41 °C, **+49% skill**; dT_max +48%; dVPD +56%), conformal calibration
is **group-aware** so coverage holds (~0.76–0.82). **Leave-one-climate-out (`loco`)** holds
out an entire macroclimate / canopy regime (Borneo forest / Mediterranean Spain / oil-palm
open) — the honest macroclimate-transfer test: skill is strong for held-out forest, modest
for open canopy, and **negative for the held-out Mediterranean climate**, with interval
coverage collapsing to ~0.1–0.5. This quantifies why the warm-night semi-arid target is
genuine extrapolation (ADR-012). Regenerate via `scripts/run_validation.py` →
`reports/loso_metrics.json` + `reports/loco_metrics.json`.

## Few-shot recalibration & model-family benchmark (`models_benchmark.py`, `scripts/`)

Out-of-climate interval coverage is recovered by **few-shot conformal recalibration**: the
conformal width is re-estimated on ~5–25 points from the target regime, restoring dT_mean
coverage from ~0.08 to ~0.80 (`scripts/mondrian_conformal.py` → `reports/mondrian_metrics.json`;
ADR-014) — a data-light, non-parametric few-shot domain adaptation of the uncertainty model.
To test whether the transfer failure is estimator-specific, a **six-family benchmark**
(`src/agroforestry/models_benchmark.py`: Ridge, Random Forest, a distance-aware **Gaussian
process**, a non-neural **mixture-of-experts**, plus the XGBoost-quantile and physics-hybrid
adapters) is run under the same folds (`scripts/benchmark_models.py` →
`reports/benchmark_metrics.json`). All families are skilful in-distribution; under LOCO only
the Gaussian process keeps non-negative cross-climate skill and the best out-of-climate
coverage — so transfer failure is a **data-regime property, not an estimator flaw**, and
XGBoost-quantile remains the production model with the GP as the transfer-honest reference
(ADR-014). Neural variants (domain-adversarial, neural residual) are out of scope until more
regimes exist.

## Data (`data/load.py`, `scripts/`)

Real labels assembled from SAFE/La Jarda loggers + SAFE oil-palm rasters; features from
Earth Engine (ERA5, SoilGrids, DEM, MODIS, ETH canopy). `DATA_SOURCE` env switch; a synthetic
generator (`data/synth.py`) remains for smoke-testing with identical columns. Offsets
(sub-canopy − free-air) are the supervised targets.
