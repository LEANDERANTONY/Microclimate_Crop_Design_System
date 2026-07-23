# ADR-017 — Applicability limits of the ERA5 free-air ambient reference (orographic screening)

- **Status:** Accepted
- **Date:** 2026-07
- **Scopes (does not supersede):** [[ADR-006]] (ERA5-atmospheric ambient-reference convention)
- **Follows:** [[ADR-016]] (external within-climate validation + pre-registration rule)

## Context

ADR-006 established the convention that sub-canopy offsets are computed against
**ERA5 *atmospheric*** (free-air, `ECMWF/ERA5/DAILY`, ~31 km) rather than ERA5-Land,
because ERA5-Land 2 m over dense canopy is itself canopy-coupled and produced spurious
positive offsets. That convention is correct for the training sites and remains in force.

The first pre-registered external validation under ADR-016 — cocoa agroforestry at
Alto Beni, Bolivia (Zenodo 1185579) — exposed a site where the convention **fails**, and
made it clear the convention has an unstated precondition. This ADR records that
precondition explicitly. It **scopes** ADR-006; it does not retract or supersede it.

## Findings (evidence)

**1. The reference is badly biased at Alto Beni.** The ~31 km ERA5 cell straddles the
Andean front. Against the local Sapecho station climatology, ERA5 is **cold-biased by
~7.5 °C on daily maximum** (ERA5 annual-mean `t_max` 27.6 °C vs station 35.0 °C).

**2. The bias flips the sign of the offsets**, so they are not comparable to the
training labels and no metric computed from them tests model skill:

| Offset | Cocoa Alto Beni (computed) | Training mean |
|---|---|---|
| `dT_max` | **+3.63 °C** | −2.04 °C |
| `dT_mean` | **+1.09 °C** | −1.01 °C |

**3. Root cause is elevation representativeness of the ERA5 cell**, not the canopy.
Copernicus DEM, site elevation vs mean elevation inside the ~31 km box, and total relief:

| Site | Site elev | Box-mean elev | Box-mean − site | Relief (max−min) |
|---|---|---|---|---|
| Cocoa Alto Beni (failed) | 372.6 m | 650.1 m | **+277.6 m** | **1,570.7 m** |
| SAFE Borneo (training) | 321.8 m | 411.4 m | +89.6 m | 1,094.2 m |
| La Jarda Spain (training) | 449.7 m | 340.6 m | −109.1 m | 1,045.4 m |
| **Anaikadu (deployment)** | 22.8 m | 14.7 m | **−8.1 m** | **42.7 m** |
| RajasekaranMurugan (TN savanna) | 94.3 m | 92.3 m | −2.0 m | 77.1 m |

**4. Honest nuance — a lapse rate does not explain the magnitude.** A dry-lapse proxy
(6.5 °C/km) applied to the +277.6 m elevation offset predicts only ~+1.8 °C, against a
measured ~7.5 °C bias on daily max. The cell is mixing Andean and lowland air masses and
the effect is much stronger on daily maximum than on the mean. **Elevation
representativeness and relief are therefore diagnostic indicators, not a calibrated
correction** — the lapse-rate figure must not be presented as a fix.

**5. Independent second defect at the same site (context, not decided here).** The cocoa
dataset publishes a single coordinate for the whole station, so all 18 plots collapse to
one feature vector (every canopy/terrain/soil feature had exactly 1 unique value; 22
distinct feature rows for 192 label rows). The canopy→offset mapping was untestable there
regardless of the reference problem. That is a dataset-suitability issue for ADR-016's
register, not an ambient-reference issue.

## Decision

**Adopt an explicit applicability rule for the ADR-006 ambient reference.** Before ERA5
free-air is used as the ambient reference at any site, screen the ERA5 cell for elevation
representativeness and relief; a site that fails the screen requires a different reference
(a site-local open-air record) or is treated as out of scope for offset computation.

**Proposed screening indicator — indicative, not calibrated (evidence base = 5 sites):**

- *Primary:* |box-mean elevation − site elevation| within the ERA5 cell. **≲ 100 m → pass;
  ≳ 150 m → fail.** This is the discriminating term in the table above.
- *Secondary / aggravating:* total relief in the cell. Note honestly that relief **alone is
  not disqualifying** — both training sites sit at ~1,050–1,100 m relief and behave
  correctly. Relief ≳ 1,500 m combined with a large elevation offset is the failure
  signature.
- *Authoritative check where available:* compare the ERA5 `t_max` climatology against a
  nearby station or site-local open-air record. A multi-degree bias overrides the DEM
  indicators in either direction.

**Options considered**

- **(a) Keep ERA5 free-air unconditionally** — rejected; demonstrably wrong at high-relief
  sites, and wrong in a way that silently inverts the label.
- **(b) Lapse-rate-correct to site elevation** — rejected as insufficient; explains ~1.8 °C
  of a ~7.5 °C bias, and would give false confidence in a corrected reference.
- **(c) Use a site-local open-air reference where one exists** — accepted as the remedy for
  sites that fail the screen, contingent on such a record being available.
- **(d) Restrict the convention to low-relief sites and screen candidates up front** —
  **adopted** as the default posture, in combination with (c).

**Screening precedes freezing.** Under ADR-016 an external validation set is pre-registered
and frozen before it is scored; the elevation/relief screen (and the station comparison
where possible) is added as a step **before** that freeze, so a site is not pre-registered
and then found unusable after the fact.

## Consequences

- **Existing Anaikadu results are unaffected.** The deployment site's ERA5 cell mean sits
  within **8 m** of true site elevation across **43 m** of relief (vs cocoa's +278 m across
  1,571 m). The mechanism does not operate in the flat Cauvery delta. The Tamil Nadu savanna
  site (−2.0 m, 77.1 m relief) is likewise clear. This is a **scoping limitation on where
  the convention may be applied, not a retraction of prior results.**
- The SAFE Borneo and La Jarda training sites pass the screen, so ADR-006's LOSO/LOCO
  numbers and the ADR-012/ADR-014 validation results stand unchanged.
- **The cocoa Alto Beni run yields no usable skill metric** and must be reported as a failed
  test of the *reference convention*, not as evidence about model skill. Reporting it as a
  poor score would be misleading in both directions.
- Confidence labelling: the screen is **LOW/indicative confidence** — a threshold inferred
  from five sites, with no calibrated bias model behind it. It is a gate for admitting sites,
  not a correction applied to data.
- Paper 1's external-validation section must state this limitation explicitly: the first
  independent within-climate test could not be scored, for a reference-representativeness
  reason discovered and quantified here.

## Next

- Apply the screen to the remaining ADR-016 candidates (SoilTemp/MDB Mediterranean, French
  Guiana, Tamil Nadu) before any of them is frozen; prefer low-relief candidates.
- Prefer datasets that publish **per-plot** coordinates and, where possible, a paired
  open-air control — this removes both defects seen at Alto Beni at once.
- Revisit the threshold once more sites exist; five points cannot calibrate it.
