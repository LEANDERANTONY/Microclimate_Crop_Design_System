# ADR-001 — Decompose into layers; predict offsets; physics-first

- **Status:** Accepted
- **Date:** 2026-06

## Context

The naive approach is one model: design → crop success. With little data, several
distinct physical processes, and a need to explain recommendations, a monolith is
fragile and uninterpretable.

## Decision

1. **Decompose** into a chain of layers (microclimate → disease → viability →
   yield → profit), each modelled with the simplest method its physics/data allow.
2. **Predict the offset** (sub-canopy − ambient), not the raw microclimate,
   because offsets transfer across macroclimates.
3. **Physics-first**: light (Beer–Lambert) and wind (shelterbelt) are computed
   mechanistically (HIGH confidence, no labels). Only temperature and VPD — which
   genuinely need it — use ML (XGBoost gradient boosting on tabular small data).
4. **Do not start with PINNs/GNNs/deep nets**; reserve them for when data justifies.

## Consequences

- Interpretable, debuggable, and honest about per-layer confidence.
- Two of four microclimate variables need no training data at all.
- Validation must be leave-one-site-out, and intervals conformalised, to defend
  the transfer claim (the project's central contribution).
- The novelty lives in the question, dataset, and disease coupling — not in
  exotic architecture.
