# Roadmap

Build priorities for the agroforestry microclimate → crop → profit system.
Philosophy unchanged: build what the available data can honestly support, defer
what it cannot, label confidence everywhere.

## Done (all six layers built, validated, runnable — 35 tests)

- **Repo**: `uv` env + lockfile, `src/` package, ADRs 001–019, DEVLOG, tests.
- **Layer 1 — microclimate**: Beer–Lambert light + shelterbelt wind (physics);
  XGBoost quantile temp/VPD offsets + conformal intervals; **OOD flag** (ADR-007);
  design→feature mapping grounded on real TN satellite values (ADR-013).
- **Real data integrated**: SAFE Borneo + La Jarda Spain forest loggers (two
  macroclimates) + SAFE oil-palm rasters (open-canopy regime). Earth Engine features
  (ERA5, SoilGrids, DEM, MODIS, ETH canopy). Ambient-reference fix (ERA5 atmospheric) ADR-006.
- **Transfer validated honestly (ADR-012)**: skill-scored LOSO (within-climate dT_mean
  +27% skill, MAE 0.28–0.33 °C) **and** leave-one-CLIMATE-out (cross-climate skill goes
  negative on a held-out climate; intervals lose calibration). A physics-prior+residual
  **hybrid** was built + tested — competitive in-distribution, does NOT rescue cross-climate;
  pure quantile model stays default. `scripts/run_validation.py` → loso/loco_metrics.json.
- **Few-shot conformal recalibration**: ~5–25 in-regime calibration points restore
  out-of-climate interval coverage (0.08 → ~0.80) — **by widening the intervals, not by
  predicting better** (**ADR-018**; e.g. dT_max Mediterranean Spain 0.409 @ width 5.605 → 0.860 @
  **10.931**). `scripts/mondrian_conformal.py` → `reports/mondrian_metrics.json`. Reframed as
  few-shot domain adaptation. Quote the width with the coverage, always.
- **Model-family benchmark (packaged + tested)**: Ridge / Random Forest / Gaussian process /
  mixture-of-experts vs the XGBoost-quantile + physics-hybrid, under LOCO + in-distribution
  holdout. Finding: transfer failure is a data-regime property, not an estimator flaw — only
  the distance-aware GP stays calibrated out-of-climate. `src/agroforestry/models_benchmark.py`,
  `scripts/benchmark_models.py` → `reports/benchmark_metrics.json`.
- **Manuscript drafted**: literature-review introduction, 22 numbered equations, 8 tables,
  12 figures, declarations, verified references; submission `.docx`, venue analysis, cover
  letter and EarthArXiv checklist in `docs/manuscript/`. Figures: `make_paper_figures.py`;
  Word build: `build_docx.py`.
- **Layer 2 — disease**: two axes (foliar air + soil-water/waterlogging), variety
  susceptibility, drainage lever; literature-calibrated (ADR-003/004), waterlogging
  data-calibrated (ADR-005).
- **Layer 3 — suitability**: fuzzy limiting-factor `viability()`.
- **Layer 4 — economics**: yield × growth × (1−disease) × banded price − validated cost;
  coconut + timber overstorey; costs validated vs NHB DPRs/TNAU, prices vs live Agmarknet
  (ADR-010/011, `reports/economics_qa.md`).
- **Layer 5 — finance**: 25-yr cash-flow with gestation/bearing/harvest timing; NPV/IRR/payback.
- **Layer 6 — uncertainty**: Monte Carlo → NPV distribution + P(loss).
- **Inverse design**: profit objective over overstorey/canopy/windbreak/drainage.
- **Real-site application**: Anaikadu (GD Home Stay pin) end-to-end; sensitivity shows the
  intercrop shortlist is robust to the temperature uncertainty.
- **Deliverables**: interactive preprint report (`reports/anaikadu_preprint.html`),
  README with figures, reproducible `export_results.py` → `make_figures.py` / `build_dashboard.py`.

## Next: firm the two soft layers with data (not blocking)

- **Temperature offset under coconut** (currently extrapolation): the leave-one-climate-out
  test (ADR-012) showed neither the tree nor the physics-prior hybrid transfers to a
  held-out climate, so the fix is **data, not a cleverer model** — add a palm/open-canopy
  or warm-night-tropical training source: SoilTemp raw loggers (request emailed) and/or
  the pan-tropical understory maps (30 m South-Asia subset requested from authors). With
  a warm-climate source in-set, the hybrid's backbone would interpolate rather than
  extrapolate. The definitive fix is still the user's **own plot logger (year 1)**, but be precise
  about **what it buys and how** (**ADR-018**, restating this claim):
  - *as **calibration** data* — few-shot / Mondrian recalibration (implemented; `mondrian_conformal.py`)
    makes the intervals **honest**, by **widening** them until the stated coverage is true. It does
    **not** improve the point prediction and does **not** narrow uncertainty. A truthful **±~4.4 °C**
    interval on dT_mean is not design-useful on its own.
  - *as **in-regime training** data* — folding a local source into training and retraining is the
    only route that can genuinely **narrow** the interval. This is ADR-012's "the fix is data, not a
    cleverer model" (ADR-008/009/012/014), and it is a well-grounded expectation, not yet a measured
    result.
  Do **not** say a season of logger data would "collapse" the offset uncertainty.
- **Economics prices to HIGH**: CEDA-Ashoka 3-yr monthly Agmarknet series (site is
  bot-blocked from this environment → user-side CSV export), plus TNAU per-crop cost line
  items for the high-input crops.

## Publication program: modular three-paper split (ADR-015)

The all-in-one manuscript is being **carved into three focused papers** sharing
one tested core (see `papers/` and `papers/README.md`). Each has one defensible
claim and its own validation protocol. Economics is pruned from the lead paper.

- **Paper 1 — uncertainty-aware microclimate prediction** (foundation; target AFM
  IF 5.7 / Ecological Informatics IF 7.3). External-validation strategy set (ADR-016,
  `docs/external_validation_datasets.md`). **Honest position as of 2026-08-04: Paper 1 has
  NO passing external validation — four external attempts, four nulls, each a *different*
  data-adequacy failure** (cocoa, Murugan, Astroni, JLelis; summary table in
  `docs/external_validation_datasets.md`). **None is a model failure**; the outcome is a
  **data-availability limitation** of the open datasets, now gated going forward by the
  **ADR-019** pre-freeze data-adequacy checklist. What exists instead is a set of characterised
  failure modes (ADR-017 orographic; ADR-019 checklist) plus independent confirmation that the
  physical signal is real (cocoa raw data). The **strategic response is an OPEN DECISION for the
  project owner** (see the fork below). The **SoilTemp/MDB delivery arrived 2026-07-22 with 7 of
  the 10 pre-registered datasets** (per-dataset detail:
  `data/raw/soiltemp_mdb_data/_validation_report.csv`); the Astroni set was supplied later.
  Current status:
  - ✅ **Cocoa (Alto Beni) external run is DONE — and returned a NULL result.** Executed and
    scored once on 2026-07-23 (`scripts/run_cocoa_validation.py` →
    `reports/cocoa_external_metrics.json`; frozen set 192 rows / 18 plots / 22 months;
    independence clean, de-dup min distance 8,685 km / 0 sites dropped). **Not a model failure
    and not a validation** — two independent methodological limitations each prevent this dataset
    as a test: (i) the published data carry **one coordinate for the whole station**, so all 18
    plots share one feature vector and the canopy→offset mapping cannot vary, let alone be
    tested; (ii) the ~31 km ERA5 free-air ambient reference is cold-biased ~7.5 °C on daily max
    at this Andean-front valley site, **flipping the observed offsets positive** (+3.63 / +1.09 °C
    vs training means −2.04 / −1.01 °C). The scored metrics therefore measure ERA5 bias plus a
    constant feature vector, not canopy skill. The OOD flag behaved as designed (25.5 % of rows
    flagged). **Genuine gains:** a quantified boundary condition on the ADR-006 ambient reference
    (**ADR-017**), and confirmation *in the raw data* that the buffering signal is real and
    correctly signed (sub-canopy T_max ~3.5 °C below the local open-air station; plot-mean dT_max
    correlates +0.55 with canopy openness, −0.49 with LAI4). **Anaikadu is unaffected** — the
    orographic mechanism does not operate in the flat Cauvery delta (site 22.8 m vs 14.7 m box
    mean across 42.7 m relief, vs cocoa's +277.6 m across 1,570.7 m), so existing Anaikadu
    results stand.
  - ❌ **Astroni (Mediterranean dVPD attempt) is DONE — and returned a METHODOLOGICAL NULL.** Run
    once on 2026-08-04 (`scripts/run_astroni_validation.py` → `reports/astroni_external_metrics.json`;
    frozen 35 site-months / 4 sites AS01–AS04, 2023 Feb–Oct; independence clean, 1,773 km). This
    was the **only intended independent Mediterranean dVPD test**. **MODIS LAI/FPAR is masked
    crater-wide** — null at all four pixels while 250 m NDVI resolves — so the dominant canopy
    predictor (`lai_x_height`, ADR-006) is absent and the canopy→offset mapping is untestable; the
    **RH/dVPD site (AS01) is among the masked**, so dVPD cannot be delivered. The ADR-017 orographic
    screen **passed** (−51 m), so this is a canopy-feature-retrievability failure, not orographic.
    `dT_mean −1.005 °C` matches the training mean and coverage is 0.89, but with R² < 0 and LAI
    masked this is buffering *magnitude* transferring, **not** canopy skill; metrics scored once are
    non-comparable; OOD flagged 100 % of rows.
  - ❌ **JLelis (humid-tropical dT attempt) is DONE — NULL, blocked at freeze.** Run once on
    2026-08-04 (`scripts/run_jlelis_validation.py` → `reports/jlelis_external_metrics.json`; no
    frozen parquet, 0 scoreable rows; independence clean, 5,840 km; 17 sites, Caatinga, Brazil). The
    declared **+150 cm air** `_T1` sensor delivered **zero values**; the only delivered temperature
    is the **−10 cm soil** `_T3` channel, so no comparable air-offset label can be formed and
    substituting soil temperature is refused (ADR-016/ADR-006). Halted before Earth Engine and
    scoring. No RH channel → dVPD impossible regardless. Licence field still reads "No".
  - 🧪 **New gate before any future freeze — ADR-019 pre-freeze data-adequacy checklist** (extends
    ADR-016; incorporates the ADR-017 orographic screen as one item). Every candidate must clear,
    *before* freezing: (1) per-plot coordinates in the right CRS (non-degenerate matrix); (2) the
    ADR-017 orographic screen; (3) canopy-feature retrievability (MODIS LAI/FPAR actually non-null);
    (4) declared-vs-delivered channel coverage; (5) reference-height match (air near ~15–30 cm, not
    soil or 150 cm); (6) licence usable. The four nulls are its evidence base. Recorded in
    `docs/external_validation_datasets.md` (pre-registration rule 5).
  - 🔀 **OPEN DECISION for the owner — the strategic fork (NOT decided here).** With no passing
    external validation across four attempts, the response is a project-owner call between:
    **(A)** reframe Paper 1 around the within-training results + the characterised failure modes as
    a methods contribution; **(B)** keep hunting for an ADR-019-checklist-passing external source;
    **(C)** lean on the deployment plot logger (as calibration and eventually in-regime training
    data, ADR-018). ADR-019 adopts the checklist and records the evidence; it does not choose the
    fork.
  - 🚫 **Independent Mediterranean VPD validation could NOT be delivered.** The Astroni
    RH-bearing set was later supplied and **run once (2026-08-04) → METHODOLOGICAL NULL** (LAI/FPAR
    masked crater-wide; the dVPD site AS01 among the masked — see the Astroni bullet above). The
    other Mediterranean data (Peñuelas 5 cm, Santoianni 10 cm) carries temperature only, below our
    15 cm reference. So the intended independent Mediterranean dVPD test does not exist from the
    available sources. This now folds into the four-null pattern and the ADR-019 checklist rather
    than remaining a standalone blocker.
  - ⚠️ **Scope control:** one dataset outside our approved selection sits inside the
    SAFE-Borneo **training** extent and is excluded under the ADR-016 independence rule. The
    de-dup rule must stay **coordinate-first** — release tags differ between request and
    delivery, so name matching alone would not have caught it.
  - ⚠️ **Tamil-Nadu few-shot leg is DONE and INCONCLUSIVE — the dataset is too thin to answer,
    which is not the same as "recalibration failed".** Run once on 2026-07-23
    (`scripts/run_murugan_fewshot.py` → `reports/murugan_fewshot_metrics.json`), site
    12.8202 °N / 79.6434 °E, **270.7 km from Anaikadu**, our closest analogue to the deployment
    site. **Independence clean** (min distance 4,191.2 km, 0 sites dropped) and the **ADR-017
    screen passes** (94.8 m site vs 92.3 m box mean). But the delivered series covers **August 2022
    only** (31 days, hourly, 2,232 readings) against a declared 2022-08 → 2023-08 deployment, so
    under the training monthly convention the primary set is **n = 1 row** and the experiment
    cannot be run; a labelled secondary daily analysis (n = 31) is 31 consecutive days at one site
    in one month sharing one feature vector, leaving **6 evaluation points at k=25** with
    draw-to-draw spread the size of the effect (sufficiency threshold was n ≥ 35). The site is also
    far outside the training envelope — **LAI 0.767** vs training minimum 1.607, open savanna,
    unshielded sensor at +10 cm — and the **OOD flag caught it hard** (mean `ood_score` **0.460**,
    **100 % of rows flagged**, 16 of 24 features out of box). Details:
    `docs/external_validation_datasets.md`. **Not** a validation of the canopy→offset mapping
    (single coordinate, as at cocoa).
  - 📏 **Delivery-validation lesson.** The MDB validation reported per-dataset periods from the
    metadata's **declared** Start/End fields without reconciling them against the **delivered
    rows**. Future delivery checks must compare declared vs delivered coverage per dataset.
  - ⚠️ **Humid-tropical arm usable** (Powers 15 cm, Goret 12 cm, Lelis 150 cm, Zavaleta 100 cm),
    but `site_selection.csv` marks these four "train + validation" — the train-vs-validate role
    split must be settled before scoring, or the ADR-016 independence claim is compromised.
  - ➡️ **Next actionable steps** (none of the four external runs is among them — all are done):
    **resolve the A/B/C strategic fork with the project owner** (the live decision), then whatever
    it implies — for (B), screen any replacement external candidate under the **ADR-019 pre-freeze
    checklist** before freezing it (per-plot coords, orography, non-masked canopy features,
    delivered-vs-declared coverage, air reference height, licence); settle the train-vs-validate
    role split on the four humid-tropical sets; ask the MDB team about the remaining ~12 declared
    months of the Murugan deployment and the delivery of JLelis's declared +150 cm air channel.
    Then: warm-tropical training source; draft Paper 1 from existing material — with the
    external-validation section written as the honest four-null it currently is (data-availability
    limitation, not model failure), and the few-shot section written per **ADR-018** (restored
    coverage at **increased width**, never "collapsed" uncertainty).
- **Paper 2 — microclimate-aware suitability + inverse design** (disease as a
  modifier). Needs suitability validation against an independent source.
- **Paper 3 — risk-aware economics** (transparent/uncalibrated). Prices → HIGH.

Data reality (confirmed): **no open under-canopy dataset exists for our exact
semi-arid site**; the play is pre-registered climatic analogues — cocoa-agroforestry
(downloaded) for humid-tropical, independent Mediterranean + a Tamil-Nadu savanna point
(~12.82 N, via the MDB request) for cross-climate/few-shot — plus year-2 own-plot loggers.
**Update 2026-07-22:** the MDB delivery only partly materialised this play — the Tamil-Nadu
point survives but is thin, and the Mediterranean leg has no VPD-capable data at all.
**Update 2026-07-23:** the humid-tropical analogue did not survive contact either — the cocoa
set was scored once and is methodologically void (single station coordinate; unrepresentative
ERA5 ambient reference at a high-relief site — ADR-017). The play now rests on finding an
ADR-017-screenable replacement analogue and, ultimately, on the year-2 own-plot loggers.
**Update 2026-07-23 (second):** the Tamil-Nadu few-shot leg was run on the delivered Murugan
deposit and is **inconclusive — the delivered month of data is too thin to answer the question**
(not a failure of recalibration). And per **ADR-018**, the own-plot loggers deliver on two separate
routes: as *calibration* data they make intervals **honest but wider**; only as *in-regime
training* data can they **narrow** them.
**Update 2026-08-04:** two more external sets were run — **Astroni** (Mediterranean dVPD attempt)
and **JLelis** (humid-tropical dT attempt) — and **both returned nulls**, for a masked dominant
canopy predictor (MODIS LAI/FPAR, crater-wide) and a declared-but-undelivered +150 cm air channel
(only −10 cm soil delivered) respectively. That makes **four external attempts, four nulls, four
distinct data-adequacy failure modes** — none a model failure. The pattern is recorded as
**ADR-019** (a mandatory pre-freeze data-adequacy checklist extending ADR-016 and folding in the
ADR-017 orographic screen). **Paper 1 has no passing external validation; this is a characterised
data-availability limitation.** The strategic response (A reframe / B keep hunting / C plot logger)
is an **open decision for the owner**.

## Next: submit

- **Post the preprint** (EarthArXiv): register ORCID, confirm the four Zenodo dataset
  "Cite as" depositor names, Mendeley-format the references to the target style, Save-as-PDF.
  Then submit the journal version (primary target per `docs/manuscript/JOURNAL_VETTING.md`:
  Ecological Informatics / Agricultural Systems / Smart Agricultural Technology).

## Later: depth

- **Multi-crop portfolio** optimisation (a mix, not one intercrop) and a **spatial planting
  layout** (windbreak placement, row design).
- Bayesian-opt / NSGA-II inverse design replacing the grid search.
- Disease parameters fitted to observed incidence once field data exists; hourly
  leaf-wetness model; coastal salinity axis (flagged ADR-005).

## Future research extensions

- Physics-informed (PINN) coupled energy/water balance once data justifies it.
- Spatial (GNN) within-field microclimate gradients if multi-node sensing arrives.
