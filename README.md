# Agroforestry Microclimate → Suitability → Design

A research codebase that predicts the **microclimate a planned agroforestry
design will create**, scores **crop suitability and disease risk** under that
microclimate, and **optimises the farm design** (overstorey, spacing, windbreak,
variety, fruiting timing) to make a target crop viable.

It is built for a real site — **Pattukkottai, Thanjavur, Tamil Nadu** (hot
semi-arid delta, NE-monsoon rainfall) — but the method is general.

## Why this exists

Conventional crop-recommendation uses *regional* climate. But an agroforestry
system creates its **own** microclimate, and that microclimate — not the
regional average — decides what grows and, crucially, what **diseases** take
hold. The causal chain that actually governs profitability is:

```
Macroclimate + Farm design → Microclimate → Disease risk → Crop viability
                                   ↑                              ↓
                          (design is controllable)      (inverse-design optimiser)
```

## Pipeline (five layers, staged by data-readiness)

| Layer | What | Method | Status |
|---|---|---|---|
| 1 | Macroclimate + design → **microclimate** (incl. leaf-wetness) | Beer–Lambert + shelterbelt physics; XGBoost quantile models for temp/VPD offset | **Built** |
| 2 | → **disease risk** (two axes: air-microclimate foliar + soil-water for soil-borne) | Mechanistic infection models × variety susceptibility; drainage a design lever | **Built** |
| 3 | Growth fit + disease → **crop viability** | Fuzzy limiting-factor + two-axis `viability()` | **Built** |
| 4 | Viability → **yield band** | reference-yield × suitability × (1−disease loss) | Designed (`docs/economics_layer.md`) |
| 5 | Yield + price + market → **profitability** | trailing-price band + surplus/distance penalty | Designed |

Inverse design (Bayesian/grid search) wraps layers 1–3 to recommend the best
design for a target crop.

## Install & run (uv)

```bash
uv sync                                   # create env from uv.lock
uv run python scripts/run_pipeline.py     # train → validate (LOSO) → predict → score → optimise
uv run pytest                             # tests
```

Out of the box it runs on synthetic "borrowed-label" data (realistic
stress-test) so the whole pipeline executes today. Swap to real data by wiring
`src/agroforestry/data/load.py` and setting `DATA_SOURCE = "real"`.

## Repo layout

See [`folder_structure.txt`](folder_structure.txt). In short: code in
`src/agroforestry/`, tests in `tests/`, written docs in `docs/`, generated
artifacts (catalogs, dashboards, metrics) in `reports/`, roadmap in
[`ROADMAP.md`](ROADMAP.md), running log in [`DEVLOG.md`](DEVLOG.md).

## Confidence & honest limits

Physics layers (light, wind) are HIGH confidence. Temperature offset is MODERATE
(borrowed-label ML, leave-one-site-out validated, conformal intervals).
Humidity/VPD and the disease parameters are LOW — now literature-*sourced*
(ADR-003) and the soil-water/waterlogging axis data-calibrated from SoilGrids+CGWB
(ADR-005), but still not locally field-calibrated. Treat **comparisons** (design
A vs B, dry vs wet timing, variety A vs B, drainage on/off) as reliable and
absolute numbers as indicative. Local sensors (year 2) calibrate the MODERATE/LOW
layers. Decisions are recorded in `docs/architectural_decision_records/` (ADR-001–005).

## Status

Active development. Layers 1–3 implemented, calibrated, and runnable (11 tests
passing); layers 4–5 designed and staged. Earth Engine authenticated and the
real-data scaffold is ready. Next: run the real-data fetch (Zenodo labels + Earth
Engine features) into layer 1 and retrain with leave-one-site-out.
