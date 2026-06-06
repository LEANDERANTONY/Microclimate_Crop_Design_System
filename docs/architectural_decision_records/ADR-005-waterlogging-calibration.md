# ADR-005 — Data-calibrated waterlogging index (seasonal) for the delta site

- **Status:** Accepted
- **Date:** 2026-06
- **Builds on:** ADR-004 (soil-water axis)

## Context

ADR-004 introduced the soil-water axis with a *manual* `WATERLOGGING_DEFAULT = 0.70`
flagged for replacement by regional data. A sourcing pass
(`reports/soil_water_thanjavur.md`) gathered measurable inputs for Pattukkottai /
Thanjavur: **SoilGrids surface clay ≈ 36.1%** and **CGWB depth-to-water-table**
(post-monsoon ≈ 0.5–2 m in the canal command; pre-monsoon ≈ 2–5 m).

## Decision

1. **Validate and keep `0.70`** as the wet-season baseline — it is now evidence-backed,
   not a guess.
2. **Add a seasonal split**: `WATERLOGGING_WET = 0.70`, `WATERLOGGING_DRY = 0.36`.
   The dry-season value (pre-monsoon water table ~3 m) sits near `WATERLOGGING_TARGET`,
   which mechanistically explains why **dry-season bahar eases the soil axis too** —
   tying the timing lever (foliar) to the soil axis. The pipeline demo now passes the
   seasonal value per window.
3. **Add `waterlogging_index(clay_pct, dtw_m)`** implementing
   `WLI = 0.5·min(1, clay/50) + 0.5·max(0, 1 − dtw/3)`, so that when per-plot
   `clay_pct` and `dtw_m` arrive (SoilGrids + CGWB / local probe), site WLI is
   computed rather than defaulted. `clay` is already a model feature; `dtw_m` is a
   future per-site input to add in `data/load.py`.

## Consequences

- The pomegranate demo now shows dry-season bahar lifting soil-disease viability on
  its own (lower seasonal waterlogging), with drainage pushing it further — the two
  levers (timing, drainage) and two axes (air, soil) all visible.
- `WATERLOGGING_DEFAULT` stays 0.70 (== wet baseline) for callers that don't specify.
- **Confidence: MEDIUM.** Inputs are district-level (CGWB 2006–09) and a single
  SoilGrids ensemble point; the formula weights are equal pending local calibration.
  Drainage multipliers remain LOW (literature-shaped).
- **Not modelled (flagged):** coastal **salinity** — CGWB reports medium–high salinity
  hazard from shallow groundwater, and subsurface-drain discharge can mobilise salt.
  A future extension; for now drainage is treated as purely beneficial.
