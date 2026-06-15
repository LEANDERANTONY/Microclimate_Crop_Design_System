# ADR-016 — External within-climate validation datasets and independence rule

**Status:** Accepted
**Date:** 2026-06-15
**Builds on:** ADR-012 (transfer validation), ADR-015 (modular papers; pre-register external validation)

## Context

Paper 1's claim is two-sided: the canopy→microclimate offset **generalises within the
climates seen in training**, and it **does not yet transfer across macroclimates** (the
honest limit, ADR-012). Training data are SAFE Borneo (humid tropical) + La Jarda
(Mediterranean Spain) + SAFE oil-palm. To support the positive claim we need *independent*
hold-out data from the **same** climates — not reused training sites. The deployment site
(semi-arid Tamil Nadu) is a different regime with **no open under-canopy dataset** (confirmed
against SoilTemp/MDB and the literature), so it stays the cross-climate / deployment-gap test,
addressed by few-shot recalibration and, ultimately, the user's own plot sensors.

## Decision

1. **Validate within-climate on independent datasets** (humid-tropical + Mediterranean),
   **de-duplicated by site coordinates** against `data/processed/all_label_sites.csv` —
   exclude La Jarda (~36.57 N, −5.60 E) and the SAFE Borneo sites (~4.7 N, 117.6 E).
2. **Pre-register / freeze** each external test set *before* scoring it; report honestly
   regardless of outcome.
3. **Acquisition:**
   - *Primary, in hand:* open cocoa-agroforestry microclimate (Zenodo 1185579, Alto Beni,
     Bolivia; humid-tropical; T/RH + stand structure + PAR/LAI) — downloaded via
     `scripts/fetch_validation_data.py` to `data/raw/cocoa_altobeni/` (gitignored).
   - *Via SoilTemp/MDB formal data-use request* (committee review ~2–3 weeks): Mediterranean
     = `AngeloRita_Astroni_Oct` (lowland Csa, T+RH/VPD), `AngeloRita_Oct`, `JosepPenuelas_1.0`,
     `LuciaSantoianni_Oct`; South-India few-shot/cross-climate = `RajasekaranMurugan_Oct` +
     `RaphaelVonBuren_Oct` (Tamil Nadu savanna, ~12.82 N, TMS4); humid-tropical =
     `Jean-YvesGoret_1.0` (French Guiana). All CC-BY.
   - **Excluded for SAFE-Borneo overlap (contamination):** `TommasoJucker_1.0`,
     `MartinSvatek_1.0`, `JosephWilliamson_Jun`.

The register (climate match, variables, access, caveats) is `docs/external_validation_datasets.md`.

## Consequences

- Paper 1 gains a credible **independent external test now** (cocoa), with more added when the
  MDB request clears — strengthening the within-climate claim beyond internal LOSO.
- Semi-arid deployment relevance remains deferred to few-shot recalibration + the user's own
  sensors; this is stated as a limitation, not hidden.
- Citation obligations: cite the MDB database paper + each dataset DOI (CC-BY); courtesy
  co-authorship where a dataset is central.
- Operational request artefacts (proposal, emails) are kept local (not version-controlled).
