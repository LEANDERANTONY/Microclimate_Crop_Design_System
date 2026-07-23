# Roadmap

Build priorities for the agroforestry microclimate → crop → profit system.
Philosophy unchanged: build what the available data can honestly support, defer
what it cannot, label confidence everywhere.

## Done (all six layers built, validated, runnable — 35 tests)

- **Repo**: `uv` env + lockfile, `src/` package, ADRs 001–014, DEVLOG, tests.
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
  out-of-climate interval coverage (0.08 → ~0.80); `scripts/mondrian_conformal.py` →
  `reports/mondrian_metrics.json`. Reframed as few-shot domain adaptation.
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
  extrapolate. The definitive fix is the user's **own plot logger (year 1)** — a single
  season would collapse the offset uncertainty (ADR-008/009/012). (Few-shot / Mondrian
  conformal recalibration is already implemented and shows ~5–25 local points restore
  out-of-climate coverage — done.)
- **Economics prices to HIGH**: CEDA-Ashoka 3-yr monthly Agmarknet series (site is
  bot-blocked from this environment → user-side CSV export), plus TNAU per-crop cost line
  items for the high-input crops.

## Publication program: modular three-paper split (ADR-015)

The all-in-one manuscript is being **carved into three focused papers** sharing
one tested core (see `papers/` and `papers/README.md`). Each has one defensible
claim and its own validation protocol. Economics is pruned from the lead paper.

- **Paper 1 — uncertainty-aware microclimate prediction** (foundation; target AFM
  IF 5.7 / Ecological Informatics IF 7.3). External-validation strategy set (ADR-016,
  `docs/external_validation_datasets.md`). **Honest position as of 2026-07-23: Paper 1 has
  NO passing external validation.** Both legs are down — the Mediterranean leg is **blocked**
  (missing AngeloRita sets) and the humid-tropical leg is **methodologically void** (cocoa,
  below). What exists instead is a characterised failure mode (**ADR-017**) plus independent
  confirmation that the physical signal is real. The **SoilTemp/MDB delivery arrived 2026-07-22
  with 7 of the 10 pre-registered datasets** (per-dataset detail:
  `data/raw/soiltemp_mdb_data/_validation_report.csv`). Current status:
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
  - 🧪 **New gate before any future freeze (ADR-017).** Screen every candidate external-validation
    site *before* freezing it: reject sites where the ~31 km ERA5 cell is unrepresentative
    (high-relief terrain / valley position — check site elevation vs box mean and box relief),
    and confirm the source publishes **per-plot coordinates** so the feature matrix is not
    degenerate. Recorded in `docs/external_validation_datasets.md` (pre-registration rule 5).
  - 🚫 **Independent Mediterranean VPD validation is BLOCKED.** Both `AngeloRita` sets —
    the only pre-registered Mediterranean sources with RH at 15 cm air — are not yet in hand
    (followed up with the MDB team). The Mediterranean data we do have (Peñuelas 5 cm,
    Santoianni 10 cm) carries temperature only, and even a dT-only test would rest on sensors
    below our 15 cm reference. **Open decision** (proceed without it / substitute a source /
    wait for the outstanding sets) — a follow-up **ADR will likely be needed**; ADR-016 is
    unamended.
  - ⚠️ **Scope control:** one dataset outside our approved selection sits inside the
    SAFE-Borneo **training** extent and is excluded under the ADR-016 independence rule. The
    de-dup rule must stay **coordinate-first** — release tags differ between request and
    delivery, so name matching alone would not have caught it.
  - ⚠️ **Tamil-Nadu few-shot is thin, not lost.** `RaphaelVonBuren_Oct` is absent but was a
    co-deposit at the same coordinates as `RajasekaranMurugan_Oct`, so the site survives —
    1 site / 2,232 temperature readings, marginal for the ~5–25-point few-shot recalibration
    and our closest analogue to Anaikadu.
  - ⚠️ **Humid-tropical arm usable** (Powers 15 cm, Goret 12 cm, Lelis 150 cm, Zavaleta 100 cm),
    but `site_selection.csv` marks these four "train + validation" — the train-vs-validate role
    split must be settled before scoring, or the ADR-016 independence claim is compromised.
  - ➡️ **Next actionable steps** (the cocoa run is no longer among them — it is done):
    settle the Mediterranean open decision with the MDB team (re-request / substitute /
    proceed without), settle the train-vs-validate role split on the four humid-tropical sets,
    and screen any replacement humid-tropical candidate under the ADR-017 gate before freezing
    it. Then: warm-tropical training source; draft Paper 1 from existing material — with the
    external-validation section written as the honest null it currently is.
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
