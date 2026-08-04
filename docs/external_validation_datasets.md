# External validation datasets (Paper 1)

How Paper 1's validation data is organised, and the pre-registration that keeps it
honest. Two distinct questions, two distinct data needs:

- **(A) Within-climate generalization** — does the model work on *new, independent
  sites in the climates it was trained on* (humid-tropical, Mediterranean)? This is
  the legitimate **positive** claim. **Status 2026-08-04: no passing external test** —
  **four** independent external sets have now been taken through the ADR-016 discipline
  and **all four returned nulls, each for a different data-adequacy reason** (see the
  "External-validation attempts to date" summary and the dated sections below). None is
  a model failure; the outcome is a **data-availability limitation** of the open datasets,
  now gated going forward by the **ADR-019** pre-freeze data-adequacy checklist.
- **(B) Cross-climate transfer / deployment gap** — does it transfer to an *unseen*
  climate (semi-arid Pattukkottai/Anaikadu)? This is the **honest negative** /
  deferred-deployment story. No same-region open data exists.

Validating in (A) does **not** validate (B). Paper 1's claim is "generalizes within
trained climates"; the semi-arid farm relevance waits for the user's own sensors or
for adding a semi-arid source to *training*.

---

## External-validation attempts to date (2026-08-04): four attempts, four nulls

Four independent external sets have been taken through the ADR-016 pre-registration
discipline. **All four returned nulls, each for a *different* data-adequacy reason
discovered only at or after freeze.** None is a model deficiency; each is a property of
what the open dataset delivers versus what its metadata declares. This is the evidence
base for **ADR-019** (the pre-freeze data-adequacy checklist).

| # | Set (date) | Climate arm | Failure mode | Independence |
|---|---|---|---|---|
| 1 | **Cocoa, Alto Beni** (2026-07-23) | Humid-tropical | Single station coordinate → degenerate feature matrix; **and** ERA5 free-air cold-biased ~7.5 °C at a high-relief valley, flipping the label sign (ADR-017) | Clean, 8,685 km |
| 2 | **Murugan, Tamil Nadu** (2026-07-23) | Cross-climate / few-shot | Declared 2022-08→2023-08; only **1 month delivered**; single site → too thin (n=1 monthly row) | Clean, 4,191 km |
| 3 | **Astroni, Naples** (2026-08-04) | Mediterranean (intended dVPD test) | **MODIS LAI/FPAR masked crater-wide**; the dominant canopy predictor is null at all 4 pixels, and the RH/dVPD site (AS01) is among the masked | Clean, 1,773 km |
| 4 | **JLelis, Caatinga** (2026-08-04) | Humid-tropical | Declared **+150 cm air** sensor delivered **zero values**; only **−10 cm soil** delivered → no comparable air-offset label | Clean, 5,840 km |

The five distinct requirements behind these modes — per-plot coordinates, an
orographically representative ERA5 cell, retrievable canopy features, delivered (not just
declared) channel coverage, and a reference-height air sensor — are exactly the items of
the **ADR-019 pre-freeze checklist**. Screening for any subset does not catch the others,
which is why each set failed differently. **Bottom line: Paper 1 has NO passing external
validation; this is a characterised data-availability limitation, not a model failure.**

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
| **Cocoa agroforestry, Alto Beni** (Zenodo 1185579) | Humid tropical (≈ Borneo regime) | Canopy openness, light, throughfall, **T, RH**; mono vs agroforestry | Yes — agroforestry design contrast | **Clean.** Bolivia (~15.4 °S, 67.5 °W) — different continent, study and decade from SAFE; de-dup min distance **8,685 km**, 0 sites dropped | Open download (Zenodo) ✅ — **scored 2026-07-23: NULL result, methodologically invalid** (see below) |
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

> **Superseded in part (2026-07-23):** the cocoa test was run and returned a **null result for
> methodological reasons** — see "Cocoa (Alto Beni) — test executed and scored once" below.
> The rest of this verdict (the Mediterranean per-candidate assessment) still stands.

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
| `AngeloRita_Astroni_Oct` | Mediterranean — **primary** (15 cm air + RH → VPD) | later supplied as `AngeloRita_Astroni.xlsx` | ⚠️ Subsequently in hand (4 sites AS01–AS04, 2023 Feb–Oct, 15 cm shielded air; AS01 also RH at 15 cm). **Run 2026-08-04 → METHODOLOGICAL NULL:** MODIS LAI/FPAR masked crater-wide, so the canopy→offset mapping is untestable and the dVPD site (AS01) is among the masked (see below) |
| `AngeloRita_Oct` | Mediterranean (15 cm air + RH → VPD) | — | ❌ **MISSING from delivery** |
| `JosepPenuelas_1.0` | Mediterranean | `SoilTemp2.0_Jun_JosepPenuelas` | ⚠️ Present (48 sites), CC-BY — but nearest air sensor **5 cm**, **no RH** (no VPD); version suffix differs |
| `LuciaSantoianni_Oct` | Mediterranean — secondary | `SoilTemp2.0_Jun_LuciaSantoianni` | ⚠️ Present (50 sites), CC-BY — max air sensor **10 cm**, **no RH** (no VPD); version suffix differs |
| `JenniferPowers_Oct` | Humid-tropical (CR dry forest) | `SoilTemp2.0_1.0_JenniferPowers` | ✅ Present (24 sites), CC-BY, air at **15 cm**; version suffix differs |
| `Jean-YvesGoret_1.0` | Humid-tropical (French Guiana) | `SoilTemp2.0_Jun_Jean-YvesGoret` | ✅ Present (64 sites), CC-BY, air at **12 cm**; release tag differs |
| `JLelis_1.0` | Humid-tropical / Caatinga bridge | `SoilTemp2.0_1.0_JLelis` (relicensed `JLelis.xlsx`) | ❌ **Run 2026-08-04 → NULL, blocked at freeze.** 17 sites (the "41" was 41 *channels*); the declared +150 cm `_T1` air sensor delivered **zero values**, only −10 cm `_T3` **soil** delivered → no comparable air-offset label (see below). Licence field still reads "No" |
| `DiegoZavaleta_Oct` | Humid-tropical (PE, has RH) | `SoilTemp2.0_1.0_DiegoZavaleta` | ✅ Present (21 sites), CC-BY, air at **100 cm**, RH present; release tag differs |
| `RajasekaranMurugan_Oct` | Tamil Nadu — closest analogue to the deployment site | `SoilTemp2.0_1.0_RajasekaranMurugan` | ⚠️ Present but **thin: 1 site / 2,232 temperature readings**, air at 10 cm (unshielded), **no RH**; release tag differs. Delivered series covers **August 2022 only (31 days, hourly)** against a declared 2022-08 → 2023-08 deployment. **Few-shot leg run 2026-07-23 → too thin to answer the question** (see below) |
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
  **Updated 2026-07-23:** the leg was run and the set proved **too thin to answer the question** —
  see "Tamil Nadu savanna (Murugan)" below. The declared coverage in the metadata (13 months) is
  not the delivered coverage (1 month); future delivery validation must reconcile the two.
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

## Cocoa (Alto Beni) — test executed and scored once (2026-07-23): NULL result

Governing decisions: **ADR-016** (pre-registration / independence) and **ADR-017** (ambient-reference
applicability). Run: `scripts/run_cocoa_validation.py`; metrics:
**`reports/cocoa_external_metrics.json`**.

**Status: run, frozen, scored once — and the result is NULL for methodological reasons.** It is
neither a validation nor a model failure: the dataset as published cannot test the quantity we
pre-registered it to test.

- **Frozen set.** `data/processed/cocoa_external_test.parquet` (gitignored) — **192 rows / 18 plots
  / 22 months (2013-03 → 2014-12)**, Sara Ana station, Alto Beni, Bolivia (−15.4602, −67.4724,
  380 m).
- **Independence: clean.** Coordinate de-duplication vs training sites gives **minimum distance
  8,685 km, 0 sites dropped**.

**Cause 1 — degenerate feature matrix.** The dataset publishes **one coordinate for the entire
station**; per-plot coordinates are not distributed. All 18 plots therefore collapse to a single
feature vector — `lai`, `canopy_height`, `ndvi`, `fapar`, `elevation`, `slope`, `twi`, `soc`, `clay`
each hold **exactly one unique value**, and only 22 distinct feature rows (the months) sit behind
192 label rows. The **canopy→offset mapping cannot vary across plots and so cannot be tested here**.

**Cause 2 — ambient-reference cold bias flips the label sign.** The ~31 km ERA5 free-air cell
(ADR-006) straddles the Andean front at this site and is cold-biased **~7.5 °C on daily max** vs the
local Sapecho station climatology. Observed offsets therefore came out **positive** (`dT_max`
**+3.63 °C**, `dT_mean` **+1.09 °C**) against training means of **−2.04 / −1.01 °C** — an artefact
of the reference, not of the stands. The resulting applicability rule (ERA5 free-air is valid over
low-relief terrain, invalid at valley sites in high-relief terrain) is **ADR-017**.

**Metrics — read them correctly.** They quantify ERA5 bias plus a constant feature vector, **not
canopy skill**. `pure_xgb`, nominal coverage 0.80: dT_max MAE **5.458 °C** / skill **+3.7 %** /
coverage **0.04**; dT_mean MAE **2.421 °C** / skill **−15.1 %** / coverage **0.01**; dVPD MAE
**0.322 kPa** / skill **−46.8 %** / coverage **0.30**. The OOD flag behaved as designed: mean
`ood_score` **0.144**, **25.5 % of rows above the 0.15 flag** (borderline-to-out-of-distribution) —
the model declined to assert confidence rather than asserting false confidence.

**What the run did establish.**
- A **quantified boundary condition on the ADR-006 ambient-reference convention** (ADR-017).
- **The physics, confirmed independently of the model, in the raw data:** sub-canopy T_max sits
  **~3.5 °C below** the local open-air station max, and observed plot-mean `dT_max` correlates
  **+0.55 with in-situ canopy openness** and **−0.49 with in-situ LAI4** (open monoculture warmest,
  closed fallow coolest). The buffering signal is present and correctly signed in an independent
  humid-tropical agroforestry dataset.
- **Deployment site unaffected.** The orographic mechanism does not operate in the flat Cauvery
  delta: Anaikadu sits **22.8 m vs a 14.7 m ~31 km box mean (−8.1 m) across 42.7 m of relief**, and
  the Tamil Nadu savanna site 94.3 vs 92.3 m (−2.0 m) across 77.1 m — versus cocoa's **+277.6 m
  across 1,570.7 m of relief** (training references: SAFE Borneo +89.6 m / 1,094 m; La Jarda
  −109.1 m / 1,045 m). **Existing Anaikadu results stand.**

**Dataset note (technical, needed to reproduce).** The published `date` string column labels
June-2014 and November-2014 as year 2013, yielding 25,938 duplicate plot-timestamps. The separate
`year` / `month` / `day` columns are self-consistent and were used instead.

**What would make this dataset testable.** **Per-plot coordinates** are required before it can ever
test the canopy→offset mapping; without them the feature matrix is degenerate by construction. A
valid ambient reference for the site (ADR-017 screening) would additionally be needed.

## Tamil Nadu savanna (Murugan) — few-shot leg executed (2026-07-23): too thin to answer

Governing decisions: **ADR-014** (few-shot conformal method), **ADR-016** (independence /
pre-registration), **ADR-017** (ambient-reference screen), **ADR-018** (what recalibration
actually delivers). Run: `scripts/run_murugan_fewshot.py`; metrics:
**`reports/murugan_fewshot_metrics.json`**.

This was the **Tamil-Nadu few-shot leg** — the first test of the ADR-014 few-shot result on
**real data near the deployment site**, not a within-climate validation. Dataset
`SoilTemp2.0_1.0_RajasekaranMurugan`, 1 site at **12.8202 °N / 79.6434 °E**, **270.7 km from
Anaikadu**.

- **Delivered coverage.** The delivered time series covers **August 2022 only — 31 days, hourly,
  2,232 temperature readings** — while the deposit metadata declares a **2022-08 → 2023-08**
  deployment; **~12 of the 13 declared months are not present in the delivery**. Recorded as a
  factual property of the files in hand.
- **Independence: clean.** Minimum distance to any training site **4,191.2 km**; **0 rows and
  0 sites dropped** (ADR-016 rule 3).
- **ADR-017 screen: PASSED.** Site **94.8 m** vs a **~31 km ERA5 box mean of 92.3 m** — the
  orographic failure mode that invalidated the cocoa run does not operate here.
- **Verdict: the dataset is too thin to answer the question. This is NOT "recalibration failed".**
  Under the training (monthly) convention the primary set is **n = 1 row** and the experiment
  cannot be run at all. A clearly-labelled **secondary daily** analysis gives n = 31 — but 31
  consecutive days at one site in one month, sharing **one feature vector**, strongly
  autocorrelated, leaving only **6 evaluation points at k=25**, with **draw-to-draw spread
  (±0.13–0.18) the same size as the effect claimed**. Pre-committed sufficiency threshold:
  **n_test ≥ max(k)+10 = 35** independent rows.
- **Numbers, for the record only (secondary daily, n=31, `pure_xgb`, nominal 0.80).** Cold:
  dT_max MAE **3.674** / skill **+39.1 %** / coverage **0.81** / width **11.41**; dT_mean MAE
  **1.964** / skill **+12.4 %** / coverage **0.39**. **The positive skill is an artefact** —
  observed offsets came out **positive** (dT_max **+3.53**, dT_mean **+0.27 °C**) against training
  means **−2.04 / −1.01 °C**, so the training-mean baseline is a badly wrong constant locally and a
  biased model still beats it. dT_max cold coverage 0.81 is accidental — the interval is very wide.
  Few-shot curve, dT_mean coverage (width): k=0 **0.39 (2.58)**, k=5 **0.81 ± 0.14 (8.86 ± 3.47)**,
  k=10 **0.83 ± 0.13 (8.74 ± 2.70)**, k=25 **0.80 ± 0.17 (7.18 ± 0.55)**.
- **Why the offsets flipped sign here — a different cause from cocoa.** Not the ambient reference.
  **Site physics:** **LAI 0.767** vs a training minimum of **1.607**; open savanna; canopy height
  **9 m** at the training minimum; and an **unshielded sensor at +10 cm** reading a surface-heated
  layer (sub-canopy monthly `t_max` **37.0 °C** vs ERA5 **33.5 °C**). Physically expected — but
  **not the canopy-buffering quantity the model was trained on**.
- **OOD flag behaved as designed, strongly.** Mean `ood_score` **0.460** (cocoa 0.144), **100 % of
  rows flagged**, **16 of 24** engineered features outside the training box — the most
  out-of-distribution external site tested so far.

**What it does show.** (a) The ADR-017 screen and the ADR-016 independence rule are runnable and
were passed cleanly; (b) the OOD flag correctly refuses confidence at an open-savanna site far
outside the training envelope; (c) qualitatively, the few-shot curve moves the way ADR-014's
Mediterranean arm does — restored coverage bought with **wider intervals** (ADR-018).

**What it does not show.** It is **not** evidence that few-shot recalibration works — or fails —
on real local data; the sample cannot support that either way. It does **not** validate the
canopy→offset mapping (one coordinate, one feature vector — the cocoa limitation again), and it is
**not** a within-climate validation of any kind.

**Two methodological catches recorded here for reuse.** (1) `ECMWF/ERA5/DAILY` **ends 2020-07-09**,
so post-2020 external sets must rebuild the ambient reference from `ERA5/HOURLY` **sampled at the
ERA5/DAILY grid node** — the two collections sit on a **half-cell-offset grid**, and naive HOURLY
sampling silently shifts the ~31 km reference cell (measured up to **3.0 °C** on monthly `t_max` at
La Jarda). Verified to **<3e-4 K** against ERA5/DAILY on overlap months. (2) `build_real_dataset.py`
falls back to ambient RH when sub-canopy RH is missing; here that would have **manufactured a
temperature-only pseudo-VPD**, so it was deliberately not used — this deposit has **zero RH rows**
and **dVPD is simply absent** from the frozen sets and from scoring.

**Other limitations.** Sensor at +10 cm unshielded vs training ~15 cm (SAFE) / ~30 cm (La Jarda);
savanna is a canopy regime absent from training; **2 sentinel rows dropped** (34,130 °C and
29,130 °C, neither in the scored sensor); metadata declares `Timezone = UTC` while the diurnal
cycle indicates IST (daily max/mean insensitive either way, no shift applied); metadata declares
15-minute resolution, delivered hourly.

**What would make this leg answerable.** The remaining ~12 declared months of the deployment (or
any second Tamil-Nadu deposit), so the monthly convention yields ≥ 35 independent rows across more
than one month — and, for the canopy→offset mapping, more than one coordinate.

## Astroni (Naples crater) — Mediterranean dVPD attempt (2026-08-04): METHODOLOGICAL NULL

Governing decisions: **ADR-016** (independence / pre-registration), **ADR-017** (ambient-reference
screen), **ADR-019** (pre-freeze data-adequacy checklist). Run:
`scripts/run_astroni_validation.py`; metrics: **`reports/astroni_external_metrics.json`**; frozen
set `data/processed/astroni_external_test.parquet` (gitignored).

This was intended as the **only independent Mediterranean dVPD test**. Dataset
`data/raw/soiltemp_mdb_data/AngeloRita_Astroni.xlsx` — an independent Mediterranean holm-oak crater
near Naples, Italy; **4 sites (AS01–AS04)** at 40.84–40.85 °N, 14.15–14.16 °E, **2023 (Feb–Oct)**;
**35 site-months / 4 sites**, with **dVPD rows = 8 (AS01 only)**, air at **15 cm shielded**.

- **Independence: clean.** Minimum distance to any training site **1,773 km** (nearest: La Jarda),
  0 rows / 0 sites dropped. EPSG 4326 verified (not the projected-coordinate trap).
- **Cause of the null: MODIS LAI/FPAR (MOD15A2H, 500 m) is masked crater-wide.** Null retrieval at
  **all four** Astroni pixels in 2023 (independently re-verified: LAI null at all four, while the
  250 m NDVI resolves normally at 0.64–0.81, and LAI is non-null at both training sites). The
  `lai_x_height` interaction is the model's **top dT_max feature** (ADR-006), and the training build
  drops NaN-LAI rows, so the **canopy→offset mapping is untestable here**. Critically, **AS01 — the
  only site carrying RH at +15 cm, i.e. the dVPD site — is among the masked**, so the intended
  independent Mediterranean dVPD validation **cannot be delivered from this set**. This is a
  mechanistically new failure mode: a masked dominant predictor (checklist item 3, ADR-019).
- **ADR-017 orographic screen: PASSED.** Site 85 m vs a ~31 km ERA5 box mean of 35 m (diff −51 m),
  under the 100 m threshold — so the null is **not** an orographic-reference failure.
- **Offset sign — read carefully.** `dT_mean` came out **−1.005 °C**, matching the training mean
  (−1.01) almost exactly (per-site −0.90 to −1.22), with **calibrated coverage 0.89 (≥ 0.80
  nominal)**. But **R² < 0 and LAI is masked**, so this reflects the near-constant buffering
  *magnitude* transferring, **not** demonstrated canopy skill. `dT_max` came out **+2.97 °C
  (positive, inverted vs training −2.04)** — a near-surface point-sensor-vs-coarse-free-air-max
  scale effect, the same as the prior externals, **not** orographic.
- **Metrics: scored once but degenerate / non-comparable.** NaN LAI was fed to XGBoost's native
  missing-value handling for a "secondary" all-sites view; the convention-exact primary view
  collapsed to AS04's 9 rows on an artefactual edge-bled LAI. Report them as measuring **buffering
  transfer + LAI absence, not canopy skill**. The OOD flag fired on **100 % of rows**.
- **Provenance note (methodological, for reuse).** The ERA5-2023 ambient reference was
  reconstructed from `ERA5/HOURLY` sampled at the `ERA5/DAILY` grid node (the ADR-006 post-2020
  convention, since `ECMWF/ERA5/DAILY` ends 2020-07-09), verified to **9e-5 K** against ERA5/DAILY
  on pre-2020 overlap months.

**What would make this set testable.** Non-masked canopy features at the crater pixels (a finer LAI
product, or in-situ LAI/openness), which the 500 m MOD15A2H algorithm does not provide for this
urban-embedded forest crater. Without them the dominant predictor is absent and the dVPD site with
it.

## JLelis (Caatinga dry forest) — humid-tropical dT attempt (2026-08-04): NULL, blocked at freeze

Governing decisions: **ADR-016** (independence / pre-registration), **ADR-006** (air-reference
convention), **ADR-019** (pre-freeze data-adequacy checklist). Run:
`scripts/run_jlelis_validation.py`; metrics: **`reports/jlelis_external_metrics.json`**;
`data/processed/jlelis_test_manifest.json` (gitignored). **No frozen parquet — 0 scoreable rows.**

Dataset `data/raw/soiltemp_mdb_data/JLelis.xlsx` (the relicensed file) — Caatinga dry forest,
Brazil; **17 sites** (the earlier "41" was 41 *channels* = 17 sites × up to 3 declared channels),
−8.17 to −7.37 °N, −37.18 to −36.28 °E, 2017–2021.

- **Independence: clean.** Minimum distance to any training site **5,840 km**, 0 dropped. EPSG 4326
  verified.
- **Cause of the null: a declared-vs-delivered channel defect.** The pre-registered sub-canopy air
  reference — the `_T1` sensor **declared at +150 cm** — carries **zero delivered values** (12
  placeholder rows, all empty; independently re-verified). The only delivered temperature is the
  `_T3` channel at **−10 cm — soil** (779,678 values). Building an air-offset label from soil
  temperature would be non-comparable and is **refused under ADR-016 / ADR-006**. The run halted
  **before Earth Engine and before scoring**. There is no RH channel either, so dVPD is impossible
  regardless. This exercises checklist items 4 (declared-vs-delivered coverage) and 5
  (reference-height match) of ADR-019.
- **Neutral technical notes** (stated without blame): metadata `Elevation` blank;
  `Timezone = Local`, `Time_difference = −3`; the file's `Licence` field still reads "No" (the
  re-share was permission-level; the file metadata was unchanged); the `_T1` (+150 cm air) and
  `_Soil moisture` channels are declared in metadata but were not delivered.

**What would make this set testable.** Delivery of the declared +150 cm air channel with actual
values (still above the ~15–30 cm training reference height, so height comparability would remain a
caveat), plus a usable licence on the delivered file.

## (B) Cross-climate / deployment gap — deferred

| Dataset | Role |
|---|---|
| OzFlux/TERN semi-arid (Alice Mulga) & savanna (Howard Springs/Litchfield/Fletcherview) | Best semi-arid analogue, but **above-canopy** flux-tower met — validates the ambient driver, not the under-canopy offset |
| Indian gridded soil-T/moisture; ERA5-Land, NASA POWER, IMD | Model **inputs/features** for our region — not independent labels |
| **User's own plot loggers (year 2)** | The definitive semi-arid fix, by **two distinct routes** (**ADR-018**): as *calibration* data (~5–25 local points) it makes the intervals **honest** — restored coverage, but **wider** intervals, not narrower; as *in-regime **training** data* (retrain with a local source) it is the only route that can **narrow** them (ADR-012: "the fix is data, not a cleverer model") |

There is **no open under-canopy logger dataset for tropical/semi-arid South India** —
same-region open validation is impossible; (B) is a characterized limitation, not a gap
to paper over.

---

## Pre-registration rule

1. **Primary within-climate test (humid-tropical): cocoa Zenodo 1185579** — frozen,
   confirmed geographically/temporally disjoint from SAFE (de-dup min distance 8,685 km).
   **EXECUTED and scored once on 2026-07-23. Outcome: invalid for methodological reasons**
   (degenerate single-coordinate feature matrix; ERA5 ambient-reference cold bias flipping the
   label sign — ADR-017). Metrics: `reports/cocoa_external_metrics.json`. This test is **spent**:
   the frozen set `data/processed/cocoa_external_test.parquet` **must not be re-scored**, and any
   future re-test of this dataset requires a **new frozen set** built once these limitations are addressed.
   The dataset can only ever test the canopy→offset mapping if **per-plot coordinates** become
   available; a valid ambient reference for the site is a further prerequisite.
2. **Secondary (Mediterranean):** the Astroni RH-bearing set was subsequently supplied and
   **run once on 2026-08-04 → METHODOLOGICAL NULL** — MODIS LAI/FPAR masked crater-wide, and
   the one dVPD site (AS01) among the masked, so no independent Mediterranean dVPD test can be
   delivered from it (see the Astroni section above). With the humid-tropical legs (cocoa,
   JLelis) also void, **Paper 1 has no passing external validation across all four attempts** —
   a data-availability limitation, not a model failure (**ADR-019**; see `ROADMAP.md`).
3. For any SoilTemp-derived set (pan-tropical TMS included), **de-duplicate by site
   coordinates against `data/processed/all_label_sites.csv`** before scoring; drop any
   site within ~1 km of a training site. **In the 2026-07-22 delivery this rule excludes one
   dataset in its entirety** (SAFE-Borneo extent). Note the rule must stay **coordinate-first**:
   release tags vary between the request and the delivery, so name matching alone would not
   have caught it.
4. Declare the held-out sites in methods and compute external metrics **once**, after
   freezing. Report honestly regardless of outcome.
5. **Clear the ADR-019 pre-freeze data-adequacy checklist before freezing.** The four external
   nulls each failed a *different* data-adequacy requirement invisible until freeze, so a single
   consolidated checklist (which folds in the ADR-017 orographic screen as one item) must clear
   **before** any set is frozen and scored:
   1. **Per-plot coordinates, correct CRS** (EPSG 4326 or convert — guard the projected-coordinate
      trap); distinct per-plot coordinates so the feature matrix is non-degenerate. *(Cocoa,
      Murugan.)*
   2. **Orographic representativeness (ADR-017)** — reject sites where the ~31 km ERA5 free-air
      cell is unrepresentative (|box-mean − site elevation| ≳ 150 m / high-relief valley
      positions). *(Cocoa.)*
   3. **Canopy-feature retrievability** — the dominant predictors (MODIS LAI/FPAR especially) must
      be **actually non-null** at the sites, not merely nominally available. *(Astroni.)*
   4. **Declared-vs-delivered coverage** — the required channels must carry actual delivered
      values with adequate temporal span, verified against the delivered time series, not the
      metadata. *(Murugan, JLelis.)*
   5. **Reference-height match** — the above-ground **air** sensor near the ~15–30 cm training
      reference, not soil (−10 cm) or far above (150 cm). *(JLelis.)*
   6. **Licence actually usable** — confirmed on the delivered file, not only the request.
      *(JLelis.)*
   A set failing any item cannot test the canopy→offset mapping (or is non-comparable) and is
   recorded as a data-adequacy null rather than frozen as a test.

## Sources

- Cocoa agroforestry microclimate (Zenodo): https://zenodo.org/record/1185579
- Pan-tropical understory temperatures (Nat. Comms. 2024): https://www.nature.com/articles/s41467-024-44734-0
- ForestTemp – European sub-canopy temperatures (Figshare): https://figshare.com/articles/dataset/ForestTemp_sub-canopy_microclimate_temperatures_of_European_forests/14618235
- Montseny long-term dataset: https://onlinelibrary.wiley.com/doi/abs/10.1002/hyp.14887
- SENTHYMED/MEDOAK Mediterranean oak dataset: https://www.sciencedirect.com/science/article/pii/S2352340924001562
- OzFlux/TERN: https://www.tern.org.au/natt-the-backbone-of-nt-research/
- SoilTemp (tropics underrepresented): https://onlinelibrary.wiley.com/doi/abs/10.1111/gcb.15123
