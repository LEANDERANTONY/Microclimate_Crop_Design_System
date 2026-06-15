# Devlog

Chronological build log. Newest first.

## 2026-06-15 — External within-climate validation data + repo hosting hygiene

- **Validation-data strategy firmed up (ADR-016).** Split validation into within-climate
  (independent humid-tropical + Mediterranean sets, de-duplicated by site coords vs training)
  and the semi-arid deployment gap (few-shot + own sensors). Register:
  `docs/external_validation_datasets.md`.
- **Cocoa-agroforestry set downloaded** (Zenodo 1185579, Alto Beni; humid-tropical; T/RH +
  stand structure + PAR/LAI) as the primary, in-hand within-climate test — via new
  `scripts/fetch_validation_data.py` → `data/raw/cocoa_altobeni/` (gitignored).
- **SoilTemp / MDB data-use request submitted** through the formal MEB request form
  (committee review ~2–3 weeks). Shortlist drawn from the 82k-row MDB metadata: Mediterranean
  (`AngeloRita_Astroni_Oct`/`_Oct`, `JosepPenuelas_1.0`, `LuciaSantoianni_Oct`), Tamil-Nadu
  savanna for few-shot/cross-climate (`RajasekaranMurugan_Oct` + `RaphaelVonBuren_Oct`),
  French-Guiana humid-tropical (`Jean-YvesGoret_1.0`); SAFE-Borneo-overlapping sets excluded.
- **Repo hosting hygiene.** The public repo hosts code, ADRs, figures, reports and shared
  docs only; non-code working documents and the operator briefing (`AGENTS.md`) are kept
  local-only / out of version control. Merged the two agent files into a single `AGENTS.md`;
  removed the unused empty `notebooks/`.

## 2026-06-15 — Modular three-paper program + external-validation data register (ADR-015)

- **Strategy pivot:** carve the all-in-one manuscript into three focused papers
  (microclimate prediction / suitability+inverse-design / economics), sharing one
  tested core. Economics pruned from the lead paper. Rationale and consequences in
  **ADR-015**.
- **Repo modularity (non-destructive):** added `papers/` with `paper1_microclimate/`,
  `paper2_suitability/`, `paper3_economics/`, each a README mapping the paper to
  the existing core modules / scripts / report snapshots (no code moved or forked).
  Overview in `papers/README.md`.
- **External validation data hunt:** confirmed **no open under-canopy dataset exists
  for tropical/semi-arid South India** — same-region open validation is impossible.
  Registered held-out climatic analogues in `docs/external_validation_datasets.md`
  (pan-tropical understory TMS via SoilTemp — preferred; cocoa-agroforestry Zenodo —
  downloadable fallback; OzFlux semi-arid — above-canopy ambient only). Adopted a
  **pre-registration rule**: freeze one external test before scoring.
- ROADMAP updated with the modular program and Paper-1 blockers.

## 2026-06-11 — Manuscript build, journal formatting, submission package, doc sync

- **Manuscript drafted and matured** (`docs/manuscript/manuscript.md`): literature-review
  introduction (§1.1–1.5, forest/agroforestry microclimate, crop-suitability ML, disease, conformal
  + digital twins), **Materials and methods** reorg (study site → data → layers → validation),
  single **Results** umbrella, **Conclusion**, Nomenclature, declarations. References verified with
  DOIs (PubMed + publisher records). **22 numbered equations** (incl. 5 mechanistic ones from the
  code: windbreak penalty, disease beta-response, LWD, waterlogging index, bearing-ramp). **8 tables**
  and **12 figures** (5 new: site map, feature-space/OOD, LOCO heatmap, few-shot curve, crop-envelope
  overlay, benchmark; `make_paper_figures.py`; all 300 dpi). Headline crops sourced to ECOCROP/PROSEA
  (sharpened the pick to pepper). Abstract trimmed to 248 words; Highlights to 5; figures/tables
  renumbered to appearance order; "Materials and methods" kept (correct heading, not "Methodology").
- **Submission package**: `build_docx.py` (markdown→docx with embedded figures) → `submission/*.docx`;
  `JOURNAL_VETTING.md` (venue shortlist + readiness), `cover_letter.md`, `PREPRINT_SUBMISSION.md`
  (EarthArXiv checklist), Mendeley `.ris`. python-docx + pypdf pip-installed into `.venv`.
- **Docs synced** to current state: README (badge 35, benchmark finding, manuscript, run/layout),
  ROADMAP, AGENT.md, PROJECT_CONTEXT.md.

## 2026-06-11 — Model-family benchmark under climate shift

- `scripts/benchmark_models.py` → `reports/benchmark_metrics.json`: six families on the same
  offset task/folds — Ridge, Random Forest, Gaussian process (distance-aware variance),
  non-neural mixture-of-experts (regime experts + distance gate), XGBoost-quantile (ours),
  physics-prior hybrid. Skill + interval coverage under grouped site holdout and LOCO.
- **Finding:** in-distribution all families are skilful; under leave-one-climate-out, Ridge and
  MoE collapse (skill ≈ −324%, −82%), tree models are bounded but lose skill (≈ −7 to −19%),
  and **only the Gaussian process keeps non-negative cross-climate skill (≈ +7%) with the best
  out-of-climate coverage (≈0.62)** — distance-aware variance widens away from training. Confirms
  transfer failure is a data-regime property, not an estimator flaw; validates elevating the GP
  and the conformal/few-shot story. Neural variants (domain-adversarial, neural residual) left as
  future work (no torch; 3 regimes overfit them).
- Manuscript: new §2.10 (benchmark methods) + §3.4 (results, Table 8) + Fig. 12; few-shot reframed
  as few-shot domain adaptation; Discussion/Conclusion/Highlights updated. Anaikadu→§3.5,
  economics→§3.6 (cross-refs fixed). docx regenerated (9 tables, 12 figures). 26 tests pass.
- **Promoted** the benchmark model wrappers from the script into the package:
  `src/agroforestry/models_benchmark.py` (Ridge/RF/GP/MoE + XGB/Hybrid adapters, `BENCHMARK_FACTORIES`
  registry); `scripts/benchmark_models.py` now imports them. Added `tests/test_benchmark.py`
  (interface, ordered intervals, GP-uncertainty-grows-with-distance, MoE experts). 35 tests pass.

## 2026-06-10 (later 3) — Pre-submission pass: manuscript, citations, Mondrian, methods figure, sourced envelopes

- **Manuscript drafted** (`docs/manuscript/manuscript.md`) + venue plan (`VENUE_AND_PLAN.md`):
  recommend EarthArXiv preprint → Agricultural Systems → Agroforestry Systems.
- **Full 596-site LOSO** (`reports/loso_full_metrics.json`): dT_mean +48.7% skill (MAE 0.41C),
  dT_max +48.1%, dVPD +55.8%, coverage 0.76–0.82. (per-site R² unstable → report skill.)
- **Citations verified** via PubMed + publisher records (DOIs for De Frenne 2019/2021, Haesen,
  Lembrechts, Zellweger, Hardwick, Pylianidis, Romano CQR, Chen&Guestrin); all [verify] removed.
- **Mondrian / few-shot conformal** (`scripts/mondrian_conformal.py` → `reports/mondrian_metrics.json`,
  §6.1): ~5–25 calibration points from a held-out climate restore interval coverage from 0.08 → ~0.80.
  Quantifies the value of on-plot sensing; coverage collapse is calibration-transfer, not a broken model.
- **Methods schematic** `figures/fig0_pipeline.png` (`scripts/make_pipeline_figure.py`).
- **Headline-crop envelopes sourced** to FAO ECOCROP (pepper id 1714: opt 22–35C/abs 10–40C, RH 65–95%)
  + PROSEA (nutmeg: opt 25–32C, flowering impaired >35C) → `reports/crop_envelopes_ecocrop.md`.
  **Material result change:** pepper now the robust clear pick (growth 67; NPV ₹565k / IRR 33% /
  payback 7 / P(loss) 12%; top across the ENTIRE temp sweep). Nutmeg downgraded to conditional
  (opt-max 32C → Anaikadu at its thermal edge; leads only at the cool end; NPV ₹127k / P(loss) 41%).
  README/PROJECT_CONTEXT/dashboard/abstract all updated to reflect pepper-as-pick, nutmeg-as-conditional.
  26 tests pass; results/figures/dashboard regenerated.

## 2026-06-10 (later 2) — Grounded design->feature mapping with real TN satellite features (ADR-013)

- Replaced the fabricated NDVI/FAPAR/height proxies in `predict.build_feature_row`
  with **real Tamil Nadu satellite features** per canopy type (MODIS LAI/FPAR/NDVI +
  ETH height, regional medians: coconut NDVI 0.47/height 7.6 m; timber 0.68/16.7 m;
  `scripts/fetch_canopy_features.py` -> `reports/canopy_features_tn.json`,
  `config.CANOPY_FEATURES_TN`). **Finding:** coconut OOD stays ~0.58 -> the
  extrapolation is **genuine, not a proxy artefact** (resolves the ADR-007 worry).
  Strengthens the honest story: the TN coconut canopy really is unlike the humid-forest
  training set. **ADR-013.**

## 2026-06-10 (later) — Skill-scored transfer validation + physics-guided hybrid (ADR-012)

- **Review-driven hardening of the validation.** Rewrote `validation.py` to report,
  per fold: **skill vs a train-mean baseline**, out-of-sample R², and the fold-MAE
  distribution (p10/50/90); added **leave-one-CLIMATE-out (`loco`)** + a
  `climate_zone()` tagger (Borneo forest / Med Spain / oil-palm open) and a
  `model_factory` hook. New `scripts/run_validation.py`; metrics in
  `reports/loso_metrics.json` + `reports/loco_metrics.json`.
- **Built `HybridQuantileModel`** (physics-guided): extrapolating Ridge backbone on a
  parsimonious in-range feature (`canopy_cover`, the De Frenne buffering term) +
  XGBoost quantile residual, with **backbone clipping** to the observed offset range
  and group-aware CQR. Drop-in for `QuantileModel`.
- **Findings (honest, paper-grade):** within-climate LOSO the model **genuinely learns**
  — dT_mean **+27 % skill** over baseline (MAE 0.33, cov 0.75), dVPD +33 %, dT_max +19 %
  (though R²≈0 for dT_max — daily offset is hard). **Cross-climate LOCO degrades and
  FAILS on the held-out Mediterranean climate** (negative skill), and interval coverage
  **collapses 0.77 → 0.24–0.46** out-of-climate. The **hybrid does not rescue
  cross-macroclimate transfer** — it ties in-distribution but overshoots into the cool
  held-out climate (magnitude is regime-dependent); the tree's flat extrapolation is
  safer there. **Decision:** keep `QuantileModel` default; keep the hybrid as a tested
  alternative for when warm-night training data is added. This quantifies *why* the
  warm-night Anaikadu target is genuine extrapolation and the plot logger is the gating
  item. 26 tests pass. **ADR-012.**

## 2026-06-10 — Preprint-grade interactive dashboard/report

- `scripts/export_results.py` -> `reports/results.json` (real pipeline output: dataset,
  documented LOSO, Anaikadu microclimate per overstorey, intercrop viability + sensitivity,
  finance NPV/IRR/payback + cashflow, Monte Carlo distributions). `scripts/build_dashboard.py`
  inlines it into **`reports/anaikadu_preprint.html`** — a self-contained, publication-style
  interactive report (abstract, 6-layer pipeline, methods, cross-climate transfer, microclimate
  selector, crop suitability + sensitivity, economics + cashflow chart, Monte Carlo histograms,
  limitations, recommendation, reproducibility). Chart.js from CDN; opens with no server.
  Static-validated (`scripts/check_dashboard.py`). Headline: coconut+pepper NPV ₹234k, IRR ~20%.

## 2026-06-09 (later 8) — Crop costs validated + reconciled (ADR-011)

- Validated per-crop costs vs NHB DPRs + TN district studies. **Key finding:** cost
  depends on production SYSTEM — pepper/nutmeg/cocoa as *coconut intercrops* (palms as
  standards, shared irrigation) establish far cheaper than standalone; full-sun crops
  (pomegranate Rs 180k, dragon Rs 300k, banana Rs 130k, ginger Rs 150k) cost more than my
  estimates. Updated `CROP_FIN`; reconciled `CROP_ECON.cost = maintain + establish/life`.
- **Anaikadu result holds & sharpens:** coconut+nutmeg +Rs 200k/14%, coconut+pepper
  +Rs 199k/**18%** — **pepper now marginally more robust** (bears yr 3 vs nutmeg yr 7 ->
  payback 9 yr, P(loss) 23% vs 40%). Banana firmly uneconomic under coconut. 22 tests pass.

## 2026-06-09 (later 7) — QA: audited ALL crop economic inputs (no other bug)

- After the coconut fix, audited every crop (`scripts/qa_crop_economics.py`,
  `reports/economics_qa.md`). **No other crop has the coconut-class manufactured-loss
  bug** — the gestation maintenance fix (`JUVENILE_MAINT_FRAC`) already covers all
  perennials; at ideal suitability every crop is clearly positive.
- **Unit discipline verified:** TNAU tables are per-hectare, our model per-acre; banana
  (20 MT/acre vs TNAU 75 MT/ha) and others confirmed correctly per-acre — no ha/acre slip.
- **Confidence:** yields/prices MODERATE (sourced doc; not stale like coconut was — pepper
  mid Rs 500 vs 2024-25 Rs 600-950, nutmeg Rs 600-900 current). Costs LOW (my estimates,
  realistic ranges). The two RECOMMENDED crops (pepper, nutmeg) are well-calibrated, so the
  recommendation doesn't rest on shaky numbers.
- Next validation: TNAU/NHB per-acre cost line items for the high-input crops + Agmarknet
  3-yr price pull; reconcile `CROP_ECON.cost` with `CROP_FIN`.

## 2026-06-09 (later 6) — QA: coconut economics fixed (gestation-cost bug) — ADR-010

- **User-caught error:** model said coconut monoculture = guaranteed loss, contradicting
  reality. Root cause: **full bearing maintenance (~Rs 38k) charged during the 6-yr
  gestation** (TNAU shows juvenile upkeep ~Rs 7-8k), plus nuts/acre too low (5,000 vs
  validated 6,500-7,000) and a stale nut-price band (Rs 7-12 vs 2024-25 Rs 15-18+).
- **Validated** against TNAU cost-of-cultivation + Salem District study 2023-24
  (net Rs 15,486/acre, BCR 1.39). Fixes: `JUVENILE_MAINT_FRAC=0.3` (maintenance now ramps
  with bearing, crops + overstorey); coconut nuts (4800,6000,7500), price (8,18),
  establish Rs 40k. **ADR-010.**
- **Result now matches reality:** coconut-only NPV **+Rs 129k, IRR 17%, payback 10 yr,
  MC P(loss) 3%** (was 100% loss). Coconut+nutmeg +Rs 313k / 18%; +pepper +Rs 243k / 19%.
  Framework was sound; inputs/gestation-handling were the bug. 22 tests pass.

## 2026-06-09 (later 5) — Monte Carlo uncertainty (layer 6)

- **`src/agroforestry/monte_carlo.py`:** propagates the genuinely-uncertain inputs —
  canopy temperature offset (the LOW-conf band), attainable yield, crop price, coconut
  nut price, timber volume+price — through microclimate->viability->yield/price->finance,
  n=3000 draws, to an **NPV distribution** per design (P10/P50/P90, mean, P(loss),
  P(>250k)). `finance` got optional sampled overrides (backward-compatible). matplotlib
  added; histogram -> `reports/monte_carlo_npv.png`. 3 tests (22 total pass).
- **Anaikadu result (8% real, 25 yr):** coconut-only P(loss) **100%**. **Coconut+nutmeg**
  is **bimodal** — P10 -465k / P50 -98k / P90 +951k, mean +84k, **P(loss) 54%**: a near
  coin-flip whose two regimes are the hot-temp draws (nutmeg fails) vs cool draws (it
  pays well). Coconut+pepper worse (P(loss) 74%). Timber shows P(loss) 0% / mean ~+Rs1.3M
  **but only because its bands omit market/mortality/harvest-timing risk** (flagged
  optimistic). The dominant swing factor for the coconut systems is the nut price + the
  uncertain temp offset — i.e. exactly the data we're waiting on -> quantifies the value
  of the year-1 sensor.

## 2026-06-09 (later 4) — Financial model (NPV / IRR / payback)

- **`src/agroforestry/finance.py`:** multi-year cash-flow that respects TIMING —
  gestation + bearing ramp per crop, coconut annual income, timber single harvest lump.
  `npv` (8% real default), `irr` (bisection), `payback`, `system_finance`. Profiles
  (gestation/full/life/cost) are standard TNAU/ICAR horticulture, editable. 7 new tests
  (19 total pass).
- **Anaikadu finance (`scripts/finance_anaikadu.py`):** at a conservative nut price
  (Rs 9.5) + 8% hurdle, **coconut monoculture is NPV-negative (-Rs 190k, never pays back)**
  — nut income alone can't cover its 6-yr gestation drag. Coconut+nutmeg lifts NPV by
  +Rs 83k but stays marginal (IRR 5%). **Nut-price sensitivity:** coconut+nutmeg NPV goes
  -107k (Rs9.5) -> +44k (Rs15) -> +127k (Rs18); break-even ~Rs 13-14/nut, i.e. positive at
  2024-25 prices. **Timber** (mahogany+nutmeg NPV +Rs1.31M, IRR 28%; teak block +Rs885k,
  IRR 31%) dominates on paper but is LOW confidence and concentrates all risk in one
  harvest spike at yr 15-18 (cash-flow timeline makes this explicit).
- Honest takeaways: coconut viability hinges on the volatile nut price; the intercrop is
  essential, not optional; timber is a high-return but high-concentration, long-lock-up,
  low-confidence play. The model now compares them on sound financial footing.

## 2026-06-09 (later 3) — Sensitivity + economics (layers 4-5) + profit inverse design

- **Sensitivity (`scripts/sensitivity_coconut.py`, `reports/sensitivity_coconut.md`):**
  swept the LOW-confidence coconut temperature offset across its band at Anaikadu. The
  intercrop **shortlist (nutmeg/pepper/banana) is robust**; only the absolute viability
  level moves. So the pending data changes *how well*, not *what* to plant — decision is
  actionable now. Physics (shade) favours the cooler, more-viable end.
- **Economics layer (`src/agroforestry/economics.py`):** staged, banded, NOT trained
  (per docs/economics_layer.md). `attainable_yield = ref x growth x (1-disease)`;
  `crop_margin` (expected/downside/upside); `overstorey_margin` for coconut (annual nuts)
  and **timber** (teak/mahogany/silver oak, annualised over rotation, LOW conf);
  `system_margin` = overstorey + intercrop. Crop bands from economics_inputs_sourced.md;
  coconut + timber web-sourced (TN).
- **Findings at Anaikadu:** coconut nuts alone ~break-even (~Rs 8k/acre/yr); the
  **intercrop is the margin** — coconut+**nutmeg** ~Rs 92k/yr with a *positive downside*
  (robust), coconut+pepper ~Rs 26k (riskier: foot-rot + price), coconut+banana negative
  (low-margin/heat-limited). Timber overstorey shows large *annualised* Rs but is a
  15-18 yr cash lock-up (flagged).
- **Profit inverse design (`optimize.py` objective="profit"; `scripts/inverse_anaikadu.py`):**
  risk-aware (0.7 expected + 0.3 downside) search over overstorey/canopy/windbreak/drainage.
  Full-space optimum favours timber (annualised Rs dominates); coconut-constrained row is
  the trustworthy annual-cash design. Recommendation: **coconut + nutmeg for yearly income,
  a teak/mahogany block or boundary for long-horizon capital + windbreak.** Timber is fully
  wired as overstorey AND windbreak (config SPECIES + economics). 12 tests pass.

## 2026-06-09 (later 2) — Understory data: author request drafted; Fairdata flow probed

- **(a)** Drafted a data-request email (Gmail draft) to Dr Eduardo Maeda
  (corresponding author) for the **30 m South-Asia subset** of the Tropical Forest
  Microclimate Maps — the data-availability note says 30 m is available on request.
- **(b)** Probed the Fairdata download service (`scripts/fairdata_files.py`,
  `fairdata_download.py`, `probe_fairdata_api.py`): the file API lists all 154 files
  and confirms a dedicated **`South_asia`** tile (309 MB/month × Daily/Daytime/Nighttime),
  but downloads require Etsin **server-side package generation** ("minutes to hours" +
  email-notify), not a clean file URL (root REST paths 404). Scripted bulk pull judged
  not worthwhile vs the 30 m request; scaffold kept for when a package URL exists. ADR-009.

## 2026-06-09 (later) — Anaikadu point run + regional-transfer data sourcing

- Ran the real pipeline at the **exact Anaikadu plot** (GD Home Stay pin,
  10.4019 N, 79.3545 E) via a new parametrized `scripts/run_site.py`. ERA5 climate
  is identical to Pattukkottai (same ~31 km pixel); only SoilGrids differs at the
  village point (clay 355 g/kg, SOC 328). Confirms satellite/reanalysis can't resolve
  village-scale climate — ground sensors needed.
- **Sourced regional data to narrow the Borneo/Spain gap (ADR-009).** Verified the
  **SoilTemp global soil-temperature maps are live on Earth Engine**
  (`crowtherlab/soil_bioclim/SBIO_v2`) — integrated as a regional reference
  (`scripts/region_reference.py`), not as air labels (soil≠canopy-air mismatch).
  Quantified the gap: Anaikadu near-surface annual mean **29.4 °C** / cold-month min
  **25.2 °C** vs Borneo 21.8/19.6 and Spain 14.2/5.8 — Anaikadu's warm regime sits
  well above both training regions.
- Identified the **pan-tropical understory air-temp maps** (Ismaeel & Maeda 2024,
  Fairdata) as the variable-correct next ingestion — open but 38 GB tiled; plan is the
  South-India tile only / 30 m subset on request. SoilTemp raw loggers remain the
  gold standard (access pending).


## 2026-06-09 — Oil-palm open-canopy regime added (SAFE landscape rasters)

- **Got the palm data.** Downloaded the SAFE landscape microclimate rasters (Zenodo
  7893600; Jucker/Hardwick lineage): modelled daily sub-canopy T_max/T_mean/VPD_max at
  50 m over Borneo, spanning forest → logged → **oil palm** → cleared. ~950 MB, resumable
  parallel fetch (`scripts/fetch_safe_rasters.py`).
- `scripts/build_oilpalm_labels.py`: sampled a UTM grid (356 valid pts → 320), took each
  point's **period-mean** sub-canopy value (668 daily bands, nodata-masked), attached
  real EE canopy/terrain/soil + ERA5 free-air macro, computed offsets. VPD raster found
  to be **hPa** (physics check: VPD > es(T) impossible in kPa) → /10. Integrated
  idempotently: forest backed up to `labelled_offsets_forest.parquet`; canonical
  dataset now **2,444 forest + 320 palm = 2,764 rows**. **ADR-008.**
- Palm regime carries **real open-canopy offsets up to dT_max +6.6 °C** (matches
  Hardwick "+6.5 °C oil palm vs forest") and extends the canopy axis to **LAI 1.6 /
  height 9 m**.
- **Key honest finding** (`scripts/diag_ood.py`): coconut OOD barely fell (0.58→0.54).
  Decomposition shows the dominant driver is **Pattukkottai's macroclimate/soil**
  (warm tropical nights t_min 25.9 / t_mean 29.3, low elevation/SOC) having **no analog
  in humid Borneo or Med Spain** — a climate-transfer gap, not a canopy gap. Coconut
  (LAI 1.0) is also still below the palm min (1.61; MODIS 500 m mixed-pixel inflation).
  Palm data was necessary but not sufficient; next priority is a **warm-night tropical
  training site** (SoilTemp India). Physics (light/wind) stays the trustworthy lever.
- 12 tests still pass.

## 2026-06-08 — Coconut OOD handling + real Pattukkottai end-to-end (option 3)

- **Coconut canopy concern (user-raised):** forest-trained model extrapolates to
  coconut (tall + sparse, unlike closed forest; Hardwick 2015: oil palm +6.5 °C vs
  forest). Added an **OOD flag** (`QuantileModel.ood_score`, `Predictor` returns
  `extrapolating` / `offset_confidence`) — ADR-007. Gave each overstorey a realistic
  `height_m`; OOD then reflects genuine canopy novelty and exposed a context-scale
  mismatch (clay % vs g/kg).
- **Option 3 — real Pattukkottai run** (`scripts/pattukkottai_run.py`): fetched the
  site's REAL features (ERA5 2019 macro: 29.3 °C mean / 34.3 °C max / 71% RH /
  926 mm; SoilGrids clay 361 g/kg; DEM 23 m), trained offsets on the real labelled
  data, predicted under-canopy microclimate per overstorey, and scored intercrops.
  Physics shade reliable (coconut wide 39%, close 57%); temp offset flagged LOW
  (extrapolation). Intercrop ranking under coconut: **nutmeg 63, pepper 36, banana
  32** (matches real Kerala coconut-agroforestry practice); pomegranate correctly
  excluded (wants full sun). Honest end-to-end real-site output with confidence flags.

## 2026-06-07 (later) — First REAL data: SAFE Borneo microclimate trained end-to-end

- Verified the Earth Engine fetch (`scripts/ee_smoke_test.py`): ERA5, MODIS,
  Copernicus DEM, SoilGrids, Sentinel-2 all resolve; SoilGrids clay 36% matched
  the ADR-005 soil-water report independently.
- Pulled real labels: **SAFE Project** sub-canopy microclimate (Zenodo 1228188,
  Borneo) + the SAFE Gazetteer for coordinates (Zenodo 3906082), via the browser.
  `build_safe_labels.py` → 2,202 plot-month rows over 245 plots.
- `build_real_dataset.py` fetched ERA5-Land ambient + canopy/terrain/soil features
  via EE, computed offsets → `data/processed/labelled_offsets.parquet`.
- `DATA_SOURCE=real` (env-switchable) LOSO over 245 sites: **dT_mean MAE 0.29 °C,
  dT_max MAE 1.13 °C, dVPD MAE 0.085 kPa**, conformal coverage 0.83–0.86. Top
  dT_max feature = **lai_x_height** — canopy structure drives the offset, recovered
  from real data. **ADR-006** records it.
- **Ambient reference fixed:** ERA5-Land (canopy-coupled, ~2-3 °C too cool) → ERA5
  atmospheric free-air. Offsets now physically correct: dT_max **−2.3 °C**, dT_mean
  **−1.0 °C** (canopy cooling, matches De Frenne).
- **Second climate added (cross-macroclimate transfer demonstrated):** La Jarda,
  Cádiz, Spain (Mediterranean, Zenodo 18913503) via `build_lajarda_labels.py`.
  Combined = **2,444 rows / 276 plots across two climates** (t_max 14–34 °C). LOSO
  across both: **dT_mean MAE 0.28 °C**, intervals 0.80–0.84 — the offset relationship
  transfers across climates on real data (NDVI/canopy height dominant). SoilTemp
  proposal emailed for broader multi-landscape breadth.

## 2026-06-07 — Calibration, two-axis disease, soil-water axis; Earth Engine set up

- **Parallel research integrated** (3 sub-chats → `reports/`): applied
  literature-sourced crop envelopes and disease/variety params to `config.py`
  (**ADR-003**); fixed the inverted pomegranate Ganesh/Bhagwa blight ratings.
  Key envelope fix: pomegranate RH-ideal 85→65% couples growth to disease reality
  (monsoon humidity now correctly scores poor for growth, not just disease).
- **Two-axis disease model (ADR-004):** soil-borne diseases (pomegranate wilt,
  pepper foot rot) moved off the air-RH axis onto a new **soil-water axis** =
  effective waterlogging (site × drainage-mitigation). Drainage added as a design
  lever in the optimiser. Timing now fixes foliar disease, drainage fixes soil
  disease — different levers, different diseases.
- **Waterlogging data-calibrated (ADR-005):** sub-chat sourced SoilGrids clay
  (~36%) + CGWB water table → validated the 0.70 default and added a seasonal split
  (wet 0.70 / dry 0.36) plus a `waterlogging_index(clay, dtw)` formula. Dry-season
  bahar eases the soil axis too. Salinity flagged as a future extension.
- **Earth Engine authenticated** (project `microclimate-crop-design-sys`);
  `earthengine-api` added; real-data scaffold (`fetch_earth_engine.py`, `load.py`,
  `data_acquisition.md`) ready. `.env.example` added; token lives in `~/.config`.
- Banana Sigatoka set to **yellow (*M. musicola*)** (local prevalence).
- Repo renamed Agriculture → **Microclimate_Crop_Design_System**, pushed to GitHub.
  Tests now **11 passing**. Docs (README, ROADMAP, architecture, AGENT, PROJECT_CONTEXT)
  refreshed to match.

## 2026-06-06 — Repo aligned to house style; layer 1–3 core verified

- Restructured into the standard `uv` + `src/` research-repo layout used across
  the sibling projects (Multimodal Cancer Detection template): `pyproject.toml`,
  `.python-version`, `uv.lock`, `src/agroforestry/`, `tests/`, `docs/`,
  `reports/`, `ROADMAP.md`, `DEVLOG.md`, `folder_structure.txt`, `AGENT.md`.
- Code moved into `src/agroforestry/` as a package: `config`, `physics`,
  `features`, `models` (XGBoost quantile + CQR), `validation` (LOSO), `predict`,
  `suitability` (+ two-axis `viability`), `disease`, `optimize`,
  `data/{synth,load}`, `cli/run_pipeline`. Research artifacts (catalogs,
  dashboards, blueprint, economics notes) moved to `reports/` and `docs/`.
- Verified the full pipeline runs end-to-end (synthetic stress-test data):
  LOSO MAE dT_max ≈ 0.72 °C; conformal interval coverage 0.80/0.83/0.80 after
  switching to **group-aware (cross-site) conformal calibration** (fixed earlier
  0.62–0.78 under-coverage).
- Disease layer validated on the pomegranate bahar-timing demo: viability 81
  (dry) vs 14–23 (wet), with wet-tolerant Ganesh beating Bhagwa — the
  microclimate→disease→viability chain working as designed.

## Earlier (pre-repo-alignment) — modelling milestones

- Built layer 1–3 pipeline: physics (Beer–Lambert light, shelterbelt wind) +
  XGBoost quantile offset models + fuzzy limiting-factor suitability + grid
  inverse-design optimiser. Realistic synthetic generator with site-clustered,
  non-linear, heteroscedastic structure and an unobserved site latent.
- Added the disease layer: leaf-wetness-duration estimate, mechanistic infection
  models (bacterial blight, mildews, anthracnose, Sigatoka, foot rot, sunburn),
  variety-susceptibility decomposition (host × pathogen × environment), wired
  into a two-axis `viability` score and a disease-aware optimiser objective.
- Fixes after first real run: group-aware conformal calibration; stronger
  windbreak-porosity penalty (optimum ~0.45, no more solid-wall gaming);
  open-field option for full-sun crops; weak features made genuinely
  uninformative so importance/pruning is a fair test.
- Compiled the crop/disease/variety catalog and data-source catalog; anchored
  suitability verdicts to the Pattukkottai climate baseline.
