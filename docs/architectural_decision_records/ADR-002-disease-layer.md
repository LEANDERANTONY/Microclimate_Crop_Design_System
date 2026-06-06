# ADR-002 — Add a mechanistic disease layer between microclimate and viability

- **Status:** Accepted
- **Date:** 2026-06

## Context

Profitability is often governed not by whether a crop *grows* but by whether
disease takes hold — and foliar/bacterial disease is driven by the same
microclimate variables (leaf wetness, humidity, temperature, rain) the system
already predicts. Plant pathology already has operational, microclimate-driven
infection models, so this layer can be mechanistic rather than data-hungry.

## Decision

1. Insert a disease layer: `realized_risk = environmental_pressure(microclimate)
   × variety_susceptibility` (the disease triangle: host × pathogen ×
   environment).
2. Add **leaf-wetness duration** as a layer-1 microclimate output (daily proxy
   now; hourly RH>90% / dew-point models later).
3. Make crop scoring **two-axis**: `viability = growth × (1 − disease_risk)`.
4. Variety enters as an **ordinal susceptibility multiplier** (lookup table, no
   incidence data needed), and becomes a decision variable in the optimiser.
5. Keep infection parameters literature-shaped and clearly **LOW confidence**
   until calibrated against observed incidence.

## Consequences

- The optimiser now faces the real growth-vs-disease trade-off (e.g. shade and
  shelter help growth but lengthen leaf wetness and raise disease) — the most
  valuable, non-obvious part of the system.
- Fruiting-time (bahar) becomes a first-class lever: keeping fruiting out of the
  humid NE-monsoon window is often the difference between viable and not.
- Absolute disease probabilities are indicative; comparisons (timing, variety,
  design) are the trustworthy outputs.
