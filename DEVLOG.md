# Devlog

Chronological build log. Newest first.

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
