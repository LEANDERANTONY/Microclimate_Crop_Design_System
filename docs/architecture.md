# Architecture

The system is a **chain of five layers**, each matched to the simplest method
its physics and data support. Decomposition (not one monolithic model) is the
core design decision — see `ADR-001`.

```
Macroclimate + Farm design
        │   (design = controllable: overstorey, spacing, LAI, windbreak, variety, fruiting timing)
        ▼
[1] Microclimate prediction  ──► shade, light, under-canopy temp, humidity/VPD,
        │                         wind, leaf-wetness duration
        ▼
[2] Disease risk             ──► per-disease realized risk = environmental
        │                         pressure × variety susceptibility
        ▼
[3] Crop viability           ──► growth fit (limiting factor) AND disease →
        │                         viability = growth × (1 − disease_risk)
        ▼
[4] Yield band   (designed)  ──► reference_yield × growth × (1 − disease loss)
        ▼
[5] Profitability (designed) ──► yield band × price band − costs (risk-adjusted)

Inverse design: search designs to maximise layer 3 for a target crop.
```

## Layer 1 — Microclimate (`physics.py`, `models.py`, `predict.py`)

Predict the **offset** from the ambient macroclimate, because offsets transfer
across climates. Light and wind are mechanistic (Beer–Lambert; shelterbelt
aerodynamics) — HIGH confidence, no ML. Temperature and VPD offsets are learned
with **XGBoost quantile regressors** (`reg:quantileerror`) plus **conformalised
quantile regression** for calibrated intervals. Leaf-wetness duration is derived
from RH/rain (the bridge into layer 2).

## Layer 2 — Disease (`disease.py`)

The disease triangle: `realized_risk = environmental_pressure × variety_susceptibility`,
across **two independent axes** (ADR-004):

- **Air-microclimate axis** — foliar diseases, driven by a temperature response ×
  leaf-wetness (`wetness`) or humidity (`humidity`), with a rain-splash factor.
- **Soil-water axis** — soil-borne diseases (wilt, foot rot), driven by temperature
  × **effective waterlogging** = site waterlogging × drainage-mitigation, *not* air
  RH. Drainage is a design lever; waterlogging is data-calibrated and seasonal for
  the delta site (wet 0.70 / dry 0.36 — ADR-005).

Variety enters as an ordinal susceptibility multiplier. No incidence data needed to
start — parameters are literature-*sourced* (ADR-003), still LOW confidence until
field-calibrated.

## Layer 3 — Viability (`suitability.py`)

Growth fit uses fuzzy trapezoidal membership against crop envelopes, aggregated
by the **limiting factor** (Liebig's minimum). `viability = growth × (1 −
disease_risk)`. A crop with ideal growth but high disease collapses — the
pomegranate-in-the-monsoon case.

## Layers 4–5 — Economics (`docs/economics_layer.md`)

Staged and uncalibrated: yield = reference × suitability × (1 − disease loss);
price = trailing-average band + trend; saleability = production surplus +
market-distance penalty; profit reported as a risk-adjusted band. Not trained
models.

## Validation

**Leave-one-site-out** (and ideally leave-one-climate-out) cross-validation —
random splits would let the model memorise a site and overstate transfer.
Conformal calibration is **group-aware** (held-out sites) so interval coverage
holds under transfer.

## Data

Synthetic borrowed-label generator (`data/synth.py`) lets the whole pipeline run
today; `data/load.py` is the hook for real SoilTemp/ForestTemp labels + Earth
Engine features. Columns are identical, so swapping changes nothing downstream.
