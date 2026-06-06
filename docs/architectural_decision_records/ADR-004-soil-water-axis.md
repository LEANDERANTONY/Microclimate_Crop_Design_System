# ADR-004 — Two-axis disease model: separate soil-water axis from air microclimate

- **Status:** Accepted
- **Date:** 2026-06
- **Supersedes:** the "soil disease on air-RH proxy" treatment flagged in ADR-003 (#1)

## Context

ADR-003 flagged that soil-borne diseases — pomegranate **wilt** (*Ceratocystis
fimbriata*) and pepper **foot rot** (*Phytophthora capsici*) — were keyed to the
**air-RH** axis, with RH as a stand-in for what actually drives them: **root-zone
waterlogging**. That is wrong in two ways: (a) the canopy-driven air microclimate
barely affects soil pathogens, and (b) the real driver (drainage / soil moisture)
is a *controllable* input we already decided to keep out of the air-microclimate
prediction. Timing the air (bahar) cannot fix a soil-water problem.

The site makes this material: Pattukkottai sits in the **Cauvery delta** — heavy
alluvial clay, poor internal drainage, seasonally shallow groundwater — i.e.
waterlogging-prone. For pepper and pomegranate this may be the *dominant* control
on survival.

## Decision

Model disease on **two independent axes**:

1. **Air-microclimate axis** (canopy-driven, predicted) — foliar diseases via
   leaf-wetness (`wetness`) or humidity (`humidity`).
2. **Soil-water axis** (site + management) — soil-borne diseases (`soil` type) via
   **effective waterlogging = site_waterlogging × drainage_mitigation**, *not* air RH.

Implementation:

- `config.WATERLOGGING_DEFAULT = 0.70` — Med-High for the delta clay site (MANUAL,
  LOW confidence; to be calibrated from SoilGrids clay + CGWB water-table depth).
- `config.DRAINAGE_MITIGATION` — multipliers for mitigation **design levers**
  (organic matter, ridges, raised beds, subsurface drains, combinations).
- `config.WATERLOGGING_TARGET = 0.35` — the agronomic band to design/manage into.
- `disease.crop_disease_risk(..., waterlogging=None, drainage="none")` — soil
  diseases now read effective waterlogging; foliar diseases unchanged.
- `optimize.optimise(..., objective="viability")` searches **drainage** as a
  design lever, so it can recommend raised beds / drains for soil-disease-prone
  crops. Pomegranate wilt and pepper foot rot moved to `type="soil"`.

## Consequences

- **Timing and drainage become distinct levers for distinct diseases.** The demo
  shows it: dry-season bahar cuts foliar blight, but wilt persists on the delta's
  waterlogging-prone clay until drainage is added.
- Soil-disease risk no longer (incorrectly) drops just because the air is dry.
- The waterlogging default is a placeholder; a sub-chat is sourcing regional
  CGWB groundwater + NBSS&LUP/SoilGrids drainage data for Thanjavur to replace it.
  Until then the value is LOW confidence and should be read as "delta clay, assume
  waterlogging-prone unless drained."
- Open: foot rot also has an aerial splash phase (kept `rain_driven` on the soil
  axis as a partial proxy); banana Sigatoka set to **yellow (*M. musicola*)** per
  the local-prevalence decision.
