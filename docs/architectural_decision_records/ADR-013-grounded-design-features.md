# ADR-013 — Grounding the design->feature mapping with real TN satellite features

- **Status:** Accepted
- **Date:** 2026-06-10
- **Resolves the open concern in:** [[ADR-007]] (was the coconut OOD a proxy artefact?)

## Context

`predict.build_feature_row` turned a hypothetical design into model inputs by
**fabricating** NDVI / FAPAR / canopy_height from LAI with crude proxies
(`ndvi = 0.3 + 0.6·cover`, etc.), while the offset models were trained on **real**
satellite features. ADR-007 flagged that the coconut OOD score (~0.58) might therefore
be partly an artefact of made-up features rather than genuine canopy novelty.

## Decision

Sample **real Tamil Nadu satellite features** per canopy type and feed those instead:
`scripts/fetch_canopy_features.py` pulls MODIS LAI/FPAR (MCD15A3H), MODIS NDVI
(MOD13Q1) and ETH canopy height (2020) over coconut-belt (Pollachi/Coimbatore +
Cauvery delta incl. Pattukkottai) and timber/wooded sites, takes the regional median,
and writes `reports/canopy_features_tn.json`. `config.CANOPY_FEATURES_TN` +
`SPECIES_CANOPY_TYPE` hold the values; `build_feature_row` now emits them for
coconut/timber designs (LAI stays the design variable the optimiser sweeps; open field
keeps the proxies).

Regional medians obtained:

| canopy | LAI | NDVI | FAPAR | height (m) |
|---|---|---|---|---|
| coconut (7 sites) | 0.78 | 0.47 | 0.37 | 7.6 |
| timber  (4 sites) | 1.00 | 0.68 | 0.40 | 16.7 |

## Finding (important, and honest)

With real features, the coconut OOD score is **essentially unchanged (~0.58, LOW
extrapolation)**. So the OOD was **not** a proxy artefact — it is **genuine**: the TN
coconut canopy (NDVI ~0.47, height ~8 m, sparse) is real-and-truly unlike the humid
closed-forest training set (NDVI ~0.8, canopy 13–55 m), on top of the warm-night
semi-arid macroclimate gap (ADR-008/009). This *strengthens* the honest story rather
than weakening it: we can now state the extrapolation is real, measured against real
regional features, not an implementation quirk.

## Consequences

- The ML offset under coconut remains correctly flagged **LOW**; the decision continues
  to rest on the **physics** (shade/wind, HIGH) and the offset-robust crop ranking.
- Credibility lift: hypothetical designs are now scored on real regional features, so a
  reviewer can't dismiss the coconut result as "fed made-up inputs."
- Confidence MODERATE: regional remote sensing, mixed 250–500 m pixels (coconut belt is
  intercropped/gappy, hence the low LAI/NDVI). The user's own plot sensors + a
  high-res (Sentinel-2 10 m / PlanetScope) pure-coconut sample remain the upgrade path.
