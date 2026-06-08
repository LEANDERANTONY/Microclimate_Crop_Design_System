# Devlog

Chronological build log. Newest first.

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
  **−1.0 °C** (canopy cooling, matches De Frenne). Single landscape remains the
  limitation → SoilTemp multi-landscape is the next data source.

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
