# External validation datasets (Paper 1)

How Paper 1's validation data is organised, and the pre-registration that keeps it
honest. Two distinct questions, two distinct data needs:

- **(A) Within-climate generalization** — does the model work on *new, independent
  sites in the climates it was trained on* (humid-tropical, Mediterranean)? This is
  the legitimate **positive** claim. Data available now.
- **(B) Cross-climate transfer / deployment gap** — does it transfer to an *unseen*
  climate (semi-arid Pattukkottai/Anaikadu)? This is the **honest negative** /
  deferred-deployment story. No same-region open data exists.

Validating in (A) does **not** validate (B). Paper 1's claim is "generalizes within
trained climates"; the semi-arid farm relevance waits for the user's own sensors or
for adding a semi-arid source to *training*.

---

## What we trained on (the baseline for independence)

| Source | Climate | Region / coords | Period | Sites |
|---|---|---|---|---|
| SAFE Project (Borneo) | Humid tropical rainforest + oil-palm | Sabah, Malaysia ~4.69 °N, 117.58 °E | 2011–2012 | `E_*` (e.g. E_196, E_224, E_198), oil-palm rasters |
| La Jarda (Spain) | Mediterranean | SW Spain (Cádiz) ~36.57 °N, −5.60 °E | 2005–2006 | `LJ_*` (DOWN/UP_*) |

Any validation site must be **disjoint** from these by study, location and time.

---

## (A) Independent within-climate validation — available now

| Dataset | Climate (matches) | Variables | Canopy/structure | Independent of training? | Access |
|---|---|---|---|---|---|
| **Cocoa agroforestry, Alto Beni** (Zenodo 1185579) | Humid tropical (≈ Borneo regime) | Canopy openness, light, throughfall, **T, RH**; mono vs agroforestry | Yes — agroforestry design contrast | **Clean.** Bolivia (~15.4 °S, 67.5 °W) — different continent, study and decade from SAFE | Open download (Zenodo) ✅ |
| Pan-tropical understory TMS (Nat. Comms. 2024) | Humid tropical | Near-surface T (TMS), hourly | Forest | ⚠️ **Contamination risk** — spans South/SE Asia and may include SAFE/Bornean loggers; must de-dup by site coords before use | Raw via SoilTemp request |
| SoilTemp Iberian/Mediterranean in-situ | Mediterranean (≈ La Jarda regime) | Sub-canopy **air T** <100 cm, ≥4 h, RH/soil where available | Site metadata | The **correct systematic source**; exclude La Jarda by coords | Requested → **delivered 2026-07-22, 7 of 10 in hand** ⚠️ (see below) |
| Aleppo-pine shrub-layer gradient (AgForMet 2020) | Mediterranean (lowland — **best climatic match**) | **T, RH, VPD, solar, soil moisture** across a dense/medium/low/open cover gradient ± shrub | Vegetation-cover gradient = controllable design | Clean (S. France/Med, not La Jarda) | On request to authors (HAL article only) ⏳ |
| ForestTemp / ForestClim (Europe) | Mediterranean/temperate | **Modelled** 25 m offset maps | n/a | n/a — model *output*, not in-situ truth | Figshare (open) ❌ as truth |

### Mediterranean vetting verdict (2026-06-15)

No **immediately-open, clean, sub-canopy air-temperature in-situ** Mediterranean set
exists that matches lowland Cádiz and is independent of La Jarda. Per-candidate:

- **Montseny (NE Spain)** — ❌ wrong variables. It's a long-term *hydrological /
  biogeochemical* catchment record (streamflow, water chemistry, N deposition,
  1978–2018), not sub-canopy microclimate loggers.
- **SENTHYMED/MEDOAK (Montpellier, FR)** — ⚠️ partial only. Has canopy structure
  (PAI, LiDAR) + **soil** moisture/temperature, one season, remote-sensing focus; no
  clear sub-canopy **air**-T offset. Usable as a structure/soil-temp auxiliary, not
  the air-T validation.
- **Fagus treeline (Italy, Sci. Rep. 2021)** — ❌ for now. Does measure below-canopy
  near-ground air T, but data are "available from the corresponding author on
  reasonable request" (not deposited), and it's a mountain treeline (cooler, weak
  match to lowland Cádiz).
- **Aleppo-pine shrub-layer (AgForMet 2020)** — ⭐ best *scientific* fit (cover
  gradient → T/RH/VPD/solar, exactly our design→microclimate structure) but data
  openness unconfirmed — likely on-request (HAL hosts the paper, not a data deposit).
- **ForestTemp/ForestClim** — ❌ as ground truth: it is a *gridded modelled* product.

**Recommendation:** the Mediterranean leg is access-gated, not impossible. Two
parallel requests (same effort class as the pan-tropical raw): (1) **SoilTemp** data
request for Iberian/Mediterranean sub-canopy air-T loggers, de-duplicated against La
Jarda; (2) email the **Aleppo-pine** authors for their gradient data. Until one
arrives, the only immediately-runnable independent external test is the humid-tropical
**cocoa Zenodo** set — so it is fine to produce the first external-validation result on
cocoa and add the Mediterranean leg when the request clears. Do **not** substitute
Montseny (wrong variable) or ForestTemp (modelled) to fill the gap.

## SoilTemp/MDB delivery — status of the 10 requested datasets (2026-07-22)

Governing decision: **ADR-016** (independence + pre-registration rule; the exclusion list).
The MDB data-use request was delivered on 2026-07-22 (CC-BY) to
`data/raw/soiltemp_mdb_data/`. It was validated against the frozen request list
`docs/correspondence/soiltemp_mdb/site_selection.csv`.

**Status: 7 of the 10 pre-registered datasets are in hand; the Mediterranean VPD leg is blocked
pending the outstanding sets.** Per-dataset detail (machine-checked):
`data/raw/soiltemp_mdb_data/_validation_report.csv`.

| Requested dataset | Role | Delivered as | Status |
|---|---|---|---|
| `AngeloRita_Astroni_Oct` | Mediterranean — **primary** (15 cm air + RH → VPD) | — | ❌ **MISSING from delivery** |
| `AngeloRita_Oct` | Mediterranean (15 cm air + RH → VPD) | — | ❌ **MISSING from delivery** |
| `JosepPenuelas_1.0` | Mediterranean | `SoilTemp2.0_Jun_JosepPenuelas` | ⚠️ Present (48 sites), CC-BY — but nearest air sensor **5 cm**, **no RH** (no VPD); version suffix differs |
| `LuciaSantoianni_Oct` | Mediterranean — secondary | `SoilTemp2.0_Jun_LuciaSantoianni` | ⚠️ Present (50 sites), CC-BY — max air sensor **10 cm**, **no RH** (no VPD); version suffix differs |
| `JenniferPowers_Oct` | Humid-tropical (CR dry forest) | `SoilTemp2.0_1.0_JenniferPowers` | ✅ Present (24 sites), CC-BY, air at **15 cm**; version suffix differs |
| `Jean-YvesGoret_1.0` | Humid-tropical (French Guiana) | `SoilTemp2.0_Jun_Jean-YvesGoret` | ✅ Present (64 sites), CC-BY, air at **12 cm**; release tag differs |
| `JLelis_1.0` | Humid-tropical / Caatinga bridge | `SoilTemp2.0_1.0_JLelis` | ✅ Present (41 sites), air at **150 cm**; confirm citation/licence terms before publication |
| `DiegoZavaleta_Oct` | Humid-tropical (PE, has RH) | `SoilTemp2.0_1.0_DiegoZavaleta` | ✅ Present (21 sites), CC-BY, air at **100 cm**, RH present; release tag differs |
| `RajasekaranMurugan_Oct` | Tamil Nadu — closest analogue to the deployment site | `SoilTemp2.0_1.0_RajasekaranMurugan` | ⚠️ Present but **thin: 1 site / 2,232 temperature readings**, air at 10 cm; release tag differs |
| `RaphaelVonBuren_Oct` | Tamil Nadu — co-deposit at the **same** coords (12.820 °N, 79.643 °E) | — | ❌ **Not in delivery** (the *site* is not lost — Murugan covers it — but the extra records are) |
| *(outside our selection)* | — | one additional dataset | 🚫 **Excluded** under the ADR-016 independence rule — its sites fall inside the SAFE-Borneo extent used in our **training** data, so it takes no part in any analysis. Caught by the **coordinate-based** de-dup rule, not by name. |

La Jarda cross-check: **clean** (0 delivered sites near ~36.57 °N, −5.60 °E).

**What is sound.** All 7 in-hand datasets match `site_selection.csv` coordinates (no >0.1°
mismatch); all have an above-ground air sensor; units are as expected (°C / %). Routine screening
of sentinel values and duplicate timestamps is applied on load, as for any logger archive.
Release tags differ from the request (`_Jun`/`_1.0` vs `_Oct`) on 6 datasets — presumed MDB
re-versioning; **cite the tag actually used** for reproducibility. Per-dataset citation details
should be confirmed with the provider before publication.

**Structure (for the loader).** Neither parquet is a metadata table — **both are long-format
time-series** (`Data_source`, `Raw data identifier`, Year/Month/Day/Time, `clim_ts_values`).
**All** metadata (Site_id, coordinates, `Sensor_height`, `Microclimate_measurement`, dates,
`Habitat_type`, `Licence`) lives in the two xlsx `metadata` sheets, paired by original format
(`prqt` ↔ `prqt.xlsx`, `xlsx` ↔ `xlsx.xlsx`).

### Consequence for the validation legs

- **Mediterranean — VPD validation currently IMPOSSIBLE.** Both AngeloRita sets were the only
  independent Mediterranean sources carrying RH at 15 cm air. What remains (Peñuelas 5 cm,
  Santoianni 10 cm) has **no RH at all**, and even a dT-only test would rest on near-surface
  sensors *below* our 15 cm target. This is a **Paper-1 blocker** (see `ROADMAP.md`).
- **Tamil Nadu few-shot — thin but alive.** 1 site / 2,232 temperature readings is marginal for
  the ~5–25-point few-shot conformal recalibration, and it is our closest analogue to Anaikadu.
- **Humid-tropical — usable.** Powers / Goret / Lelis / Zavaleta all have above-ground air
  sensors (15 / 12 / 150 / 100 cm). Note `site_selection.csv` marks these four as
  "train + validation" — using the same sets for training *and* independent external validation
  would conflict with the ADR-016 independence claim, so the role split must be settled
  explicitly before this arm is scored.

### ⚠️ OPEN DECISION — follow-up ADR likely required

Whether to (a) proceed with Paper 1 **without** independent Mediterranean VPD validation,
(b) substitute another Mediterranean source, or (c) re-request the missing AngeloRita sets from
MDB, is an **open decision for the project owner**. It is deliberately **not** taken in this
register. ADR-016 stands unamended — nothing here changes the independence or pre-registration
rule; a **new ADR** should record whichever course is chosen.

## (B) Cross-climate / deployment gap — deferred

| Dataset | Role |
|---|---|
| OzFlux/TERN semi-arid (Alice Mulga) & savanna (Howard Springs/Litchfield/Fletcherview) | Best semi-arid analogue, but **above-canopy** flux-tower met — validates the ambient driver, not the under-canopy offset |
| Indian gridded soil-T/moisture; ERA5-Land, NASA POWER, IMD | Model **inputs/features** for our region — not independent labels |
| **User's own plot loggers (year 2)** | The definitive semi-arid fix — collapses the deployment gap; few-shot recalibration already shown to work with ~5–25 local points |

There is **no open under-canopy logger dataset for tropical/semi-arid South India** —
same-region open validation is impossible; (B) is a characterized limitation, not a gap
to paper over.

---

## Pre-registration rule

1. **Primary within-climate test (humid-tropical): cocoa Zenodo 1185579** — frozen,
   confirmed geographically/temporally disjoint from SAFE.
2. **Secondary (Mediterranean):** the SoilTemp/MDB request was delivered 2026-07-22, but the
   two RH-bearing sets are not yet in hand, so **no independent Mediterranean VPD test is
   currently available**. The leg is **blocked pending an owner decision**, not silently
   dropped. Still not a blocker for the first (cocoa, humid-tropical) result.
3. For any SoilTemp-derived set (pan-tropical TMS included), **de-duplicate by site
   coordinates against `data/processed/all_label_sites.csv`** before scoring; drop any
   site within ~1 km of a training site. **In the 2026-07-22 delivery this rule excludes one
   dataset in its entirety** (SAFE-Borneo extent). Note the rule must stay **coordinate-first**:
   release tags vary between the request and the delivery, so name matching alone would not
   have caught it.
4. Declare the held-out sites in methods and compute external metrics **once**, after
   freezing. Report honestly regardless of outcome.

## Sources

- Cocoa agroforestry microclimate (Zenodo): https://zenodo.org/record/1185579
- Pan-tropical understory temperatures (Nat. Comms. 2024): https://www.nature.com/articles/s41467-024-44734-0
- ForestTemp – European sub-canopy temperatures (Figshare): https://figshare.com/articles/dataset/ForestTemp_sub-canopy_microclimate_temperatures_of_European_forests/14618235
- Montseny long-term dataset: https://onlinelibrary.wiley.com/doi/abs/10.1002/hyp.14887
- SENTHYMED/MEDOAK Mediterranean oak dataset: https://www.sciencedirect.com/science/article/pii/S2352340924001562
- OzFlux/TERN: https://www.tern.org.au/natt-the-backbone-of-nt-research/
- SoilTemp (tropics underrepresented): https://onlinelibrary.wiley.com/doi/abs/10.1111/gcb.15123
