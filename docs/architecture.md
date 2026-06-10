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
silently extrapolated (ADR-007). Trained on real SAFE Borneo + La Jarda Spain loggers plus
SAFE oil-palm rasters (ADR-006/008); ambient reference is ERA5 *atmospheric* free-air, not
ERA5-Land (ADR-006).

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

**Leave-one-site-out** cross-validation — an entire site held out per fold, the honest test
of transfer (random splits would let the model memorise a site). Conformal calibration is
**group-aware** so interval coverage holds under transfer. Recorded: LOSO dT_mean MAE 0.28 °C
across two macroclimates (ADR-006).

## Data (`data/load.py`, `scripts/`)

Real labels assembled from SAFE/La Jarda loggers + SAFE oil-palm rasters; features from
Earth Engine (ERA5, SoilGrids, DEM, MODIS, ETH canopy). `DATA_SOURCE` env switch; a synthetic
generator (`data/synth.py`) remains for smoke-testing with identical columns. Offsets
(sub-canopy − free-air) are the supervised targets.
