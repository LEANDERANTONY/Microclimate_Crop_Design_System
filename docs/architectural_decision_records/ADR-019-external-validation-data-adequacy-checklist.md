# ADR-019 — Pre-freeze data-adequacy checklist for external validation

- **Status:** Accepted
- **Date:** 2026-08-04
- **Extends (does not supersede):** [[ADR-016]] (external within-climate validation + pre-registration/independence protocol)
- **Incorporates as one item:** [[ADR-017]] (ERA5 free-air ambient-reference orographic screen)
- **Follows:** [[ADR-006]] (ERA5-atmospheric ambient-reference convention; sub-canopy air-T reference height)

## Context

Under ADR-016 an external within-climate validation set is **pre-registered and frozen
before it is scored**, and reported honestly regardless of outcome. Four independent
external sets have now been taken through that discipline. **All four returned nulls, and
each failed for a *different* data-adequacy reason that was invisible until the freeze
step — or, in one case, until a full run had already been executed.** None is a model
deficiency; every one is a property of what the available open datasets actually contain
versus what their metadata declares.

This ADR records that pattern and adopts a mandatory checklist that must clear **before**
any external set is frozen and scored. It **extends** ADR-016's pre-registration protocol
with an explicit data-adequacy gate and **folds ADR-017's orographic screen in as one of
its items**; it does **not** retract or supersede either. ADR-016's independence/de-dup
rule and ADR-017's ambient-reference rule remain in force exactly as written.

### The four nulls (evidence base)

| # | Set (date) | Climate arm | Failure mode discovered | Where caught |
|---|---|---|---|---|
| 1 | **Cocoa, Alto Beni** (2026-07-23) | Humid-tropical | Single station coordinate → degenerate feature matrix (all plots one vector); **and** ERA5 free-air cold-biased ~7.5 °C at a high-relief valley, flipping the label sign (ADR-017) | After freeze + scoring |
| 2 | **Murugan, Tamil Nadu** (2026-07-23) | Cross-climate / few-shot | Declared 2022-08→2023-08; only **1 month delivered**; single site → too thin (n=1 monthly row) | After freeze + scoring |
| 3 | **Astroni, Naples** (2026-08-04) | Mediterranean (the intended dVPD test) | Dominant canopy predictor **MODIS LAI/FPAR masked crater-wide** (null at all 4 pixels); the one RH/dVPD site is among the masked | At/after freeze |
| 4 | **JLelis, Caatinga** (2026-08-04) | Humid-tropical | Declared **+150 cm air** sensor delivered **zero values**; only **−10 cm soil** delivered → no comparable air-offset label | At freeze (before scoring) |

Runs 1–2 are recorded in ADR-016/017/018 and the register; runs 3–4 are documented in
`reports/astroni_external_metrics.json`, `reports/jlelis_external_metrics.json`, the
2026-08-04 DEVLOG entry and `docs/external_validation_datasets.md`.

The salient point is **mode diversity**: an orographic-reference failure, a
single-coordinate degeneracy, a declared-but-undelivered temporal span, a masked dominant
predictor, and a delivered-but-wrong-height (soil, not air) sensor are five distinct
requirements, and each defeated one set. Screening for any subset of them does not catch
the others. The Astroni and JLelis runs make this concrete: the pre-freeze check that
preceded them screened LAI-retrievability, orography, coordinates and *declared*
measurements, but **not** delivered-vs-declared per-channel time-series coverage — the exact
gap the Murugan run had already surfaced — which is why JLelis reached a full run before the
missing air channel was found. The checklist below closes that gap and consolidates the rest.

## Decision

**Adopt a mandatory PRE-FREEZE DATA-ADEQUACY CHECKLIST.** Every item must clear before an
external validation set is frozen and scored under ADR-016. A set that fails any item is
**not** frozen as a test; the failure is recorded (as these four are) rather than scored.

1. **Coordinates present, correct CRS, per-plot not per-station.** Coordinates must be
   present and in EPSG 4326 (convert if projected — guard the projected-coordinate trap),
   and the source must publish **distinct per-plot coordinates**, not one station coordinate
   for many plots. Multiple distinct site coordinates are required so the canopy feature
   matrix is non-degenerate and the canopy→offset mapping can actually vary across plots.
   *(Cocoa: one station coordinate → degenerate; also single-coordinate at Murugan.)*
2. **Orographic representativeness (the ADR-017 screen).** The ~31 km ERA5 free-air cell
   must be elevation-representative of the site: |box-mean elevation − site elevation| ≲ 100 m
   (≳ 150 m fails), with relief as an aggravating secondary term and a station-climatology
   comparison where available. High-relief valley positions are rejected. *(Cocoa: +277.6 m
   across 1,570.7 m relief → failed. This item is ADR-017, unchanged.)*
3. **Canopy-feature retrievability.** The dominant learned predictors — **MODIS LAI/FPAR
   (MOD15A2H, 500 m) especially**, whose `lai_x_height` interaction is the top dT_max feature
   (ADR-006) — must be **actually non-null at the sites**, not merely nominally available. A
   set where the canopy features are masked cannot test the canopy→offset mapping even if
   every other item passes, because the training build drops NaN-LAI rows. *(Astroni: LAI/FPAR
   masked at all four crater pixels while 250 m NDVI resolved normally.)*
4. **Declared-vs-delivered coverage.** The required channels must carry **actual delivered
   values with adequate temporal span**, verified against the delivered time series — not
   inferred from metadata declarations. Check per channel: number of non-null delivered
   values, and the delivered date span versus the declared deployment period. *(Murugan:
   1 of 13 declared months delivered → n=1 monthly row. JLelis: the +150 cm air channel
   declared but delivered zero values.)*
5. **Reference-height match.** The above-ground **air** sensor must sit near the training
   reference height (~15–30 cm). A delivered sensor that is **soil** (−10 cm) or **far above**
   the canopy-buffered layer (150 cm) is not a comparable label and must not be substituted
   for the air reference under ADR-006/ADR-016. *(JLelis: only −10 cm soil delivered — refused
   rather than scored against an air-offset model.)*
6. **Licence actually usable.** The dataset licence must permit the intended use and
   citation. Confirm the licence and citation terms on the delivered file, not only the
   request. *(JLelis: the file's `Licence` field still reads "No"; the re-share was
   permission-level and did not change the file metadata — a neutral technical fact to note
   before publication.)*

Items 3–5 also require **RH channel presence** wherever VPD (dVPD) is a scored target: no
sub-canopy RH at the reference height means dVPD is not scoreable and must not be
manufactured from an ambient-RH fallback (ADR-018 methodological catch).

**Options considered**

- **(a) Keep only ADR-016's independence/pre-registration rule and ADR-017's orographic
  screen** — rejected; between them they catch two of the five observed modes (independence,
  orography) and would have passed Murugan, Astroni and JLelis, each of which then failed for
  a mode neither rule tests.
- **(b) Add checks reactively, one mode per new null** — rejected; this is what happened
  ad hoc, and it let JLelis reach a full run for a coverage gap the Murugan run had already
  identified. The lesson is to consolidate the modes into one gate applied up front.
- **(c) Adopt a single consolidated pre-freeze checklist covering all five observed modes** —
  **adopted.**

## Consequences

- **The checklist runs before freezing.** It is a gate for admitting a set as a test, applied
  in the pre-registration step of ADR-016, before any freeze and before any Earth Engine
  feature build or scoring. A set failing any item is documented as a data-adequacy null, not
  scored.
- **The four nulls are the evidence base**, and the checklist is derived from them item by
  item. It is **indicative, not calibrated** — five sites (four sets, with cocoa carrying two
  modes) cannot calibrate thresholds; the thresholds it inherits from ADR-017 carry that same
  LOW/indicative confidence label.
- **Paper 1 currently has NO passing external validation**, and this is characterised as a
  **data-availability limitation of the open datasets**, not a model failure. The design→
  microclimate offset model has been defeated dataset-by-dataset by data-adequacy
  requirements invisible until freeze; the model's own within-training LOSO results
  (ADR-006/012) are unaffected, and the OOD flag behaved as designed on every external set.
- **The strategic response is an OPEN DECISION for the project owner and is NOT decided
  here.** The options — **(A)** reframe Paper 1 around the within-training results plus the
  characterised failure modes as a methods contribution; **(B)** keep hunting for a
  checklist-passing external source; **(C)** lean on the deployment plot logger (as
  calibration and eventually in-regime training data, ADR-018) — are a project-owner call.
  This ADR adopts the checklist and records the evidence; it does not choose the fork.

## Next

- Apply the checklist to any future external candidate before freezing it; prefer sources
  that publish per-plot coordinates, sit on low-relief terrain, carry non-masked canopy
  features, deliver an air sensor near the reference height with verified temporal span, and
  a usable licence.
- Revisit the thresholds (especially items 2–4) once more sets exist; the current evidence
  base is four nulls.
- Surface the A/B/C strategic fork to the project owner as the live decision it is.
