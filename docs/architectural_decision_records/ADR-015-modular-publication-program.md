# ADR-015 — Split into a modular three-paper program; pre-register external validation

**Status:** Accepted
**Date:** 2026-06-15
**Supersedes:** none (refines the publication strategy behind the all-in-one manuscript)

## Context

The drafted manuscript bundles six layers (microclimate → disease → suitability →
yield → economics → uncertainty) into one submission. External review feedback and
our own assessment converge: the binding constraint is **validation relative to
ambition**, not novelty or writing. An all-in-one paper forces simultaneous
validation of six claims spanning ML, ecology, plant pathology, agronomy and
economics — reviewers attack the weakest link, and the deployment case study
(Anaikadu, Tamil Nadu) is an acknowledged out-of-distribution setting without
local empirical validation.

Separately, we confirmed (`docs/external_validation_datasets.md`) that **no open
under-canopy microclimate dataset exists for our region**; same-region validation
from open data is not possible. The realistic path is a held-out climatic
analogue.

## Decision

1. **Publish as three focused papers** sharing one tested core package, each with
   a single defensible empirical claim:
   - Paper 1 — uncertainty-aware microclimate prediction + honest cross-climate
     transfer (foundation).
   - Paper 2 — microclimate-aware crop suitability + inverse design (disease as a
     modifier).
   - Paper 3 — risk-aware economics (transparent, uncalibrated tier).
2. **Prune economics from Paper 1/2 scope** — it is the least validatable layer
   from environmental data and invites a separate reviewer community.
3. **Monorepo, non-destructive modularity:** keep `src/agroforestry/` single-
   sourced and tested; add `papers/paperN_*/` folders holding only per-paper
   configs, frozen result snapshots, figures and a manuscript pointer. No code is
   forked or moved per paper.
4. **Pre-register and freeze one external held-out warm-climate dataset before
   scoring it**, declared in methods, reported honestly regardless of outcome.
   Preferred: pan-tropical understory TMS (raw via SoilTemp request); fallback:
   cocoa agroforestry Zenodo (immediately downloadable).

## Consequences

- Each paper gets a clean evaluation protocol; weakest-link risk drops.
- Paper 1 can target Q1 (AFM IF 5.7 / Ecological Informatics IF 7.3) on the
  strength of design-as-controllable-variable + OOD-aware transfer.
- The all-in-one `manuscript.md` is retained but becomes the source to carve
  Paper 1 from; it is no longer the submission target as-is.
- Acquiring a warm-tropical training source + the frozen external test becomes the
  top priority for Paper 1 (see ROADMAP).
- Reaching top-tier (IF 10+) still requires the user's own local sensor data and a
  demonstrated transfer-success result — out of scope for Paper 1.
