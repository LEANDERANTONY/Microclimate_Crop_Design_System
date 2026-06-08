# ADR-006 — First real-data integration: SAFE Project (Borneo) microclimate

- **Status:** Accepted
- **Date:** 2026-06

## Context

Layer 1 had only ever trained on synthetic data. We wired in the first real
labels to prove the end-to-end pipeline and the Earth Engine feature fetch on
genuine measurements.

## Decision / what was done

- **Labels:** SAFE Project "Forest microclimate – 1st order sites" (Zenodo
  1228188, CC-BY) — sub-canopy air temperature + RH at forest plots in Sabah,
  Borneo, 2011–2012. Plot coordinates from the SAFE Gazetteer (Zenodo 3906082).
  `scripts/build_safe_labels.py` streams the 481k-row workbook → 2,202 plot-month
  rows over 245 plots (monthly mean of daily-max / daily-mean sub-canopy temp, RH).
- **Features:** `scripts/build_real_dataset.py` fetches ERA5-Land monthly ambient
  + ETH canopy height + MODIS LAI/FPAR/NDVI + Copernicus DEM/slope + SoilGrids
  (clay, soc) via Earth Engine, computes offsets, and writes
  `data/processed/labelled_offsets.parquet` (config schema). EE verified by
  `scripts/ee_smoke_test.py` (SoilGrids clay 36% independently matched ADR-005).
- **Run:** `DATA_SOURCE=real` (now env-switchable). LOSO over 245 sites:
  dT_mean MAE **0.29 °C**, dT_max MAE **1.13 °C**, dVPD MAE **0.085 kPa**;
  conformal coverage 0.83–0.86 (target 0.80). Top dT_max feature = **lai_x_height**
  — canopy structure drives the offset, as theory predicts.

## Known limitations (important)

1. **Ambient reference is ERA5-Land 2 m**, which over dense rainforest is itself
   canopy-influenced and runs cool (~27.5 °C monthly max vs a true ~32 °C free-air
   max). So `dT_max` comes out near-zero/positive instead of the expected negative
   cooling offset. **The next refinement: pair against a true free-air macroclimate
   reference (CHELSA, or ERA5 — not ERA5-Land — at reference height), as ForestTemp
   does.** Until then, absolute offset magnitudes are biased; the canopy→offset
   *relationship* and the pipeline mechanics are sound.
2. **Single landscape** (~5 km, one ERA5 pixel) → rich canopy-structure / temporal
   variation but ~no cross-macroclimate spread. LOSO here tests transfer to a
   held-out plot in the same climate, not across climates. Breadth needs multiple
   landscapes (SoilTemp network — next data source).
3. The crop-suitability demo under `DATA_SOURCE=real` mixes real offset models with
   a synthetic macro context, so those crop scores are not recommendations — only
   the offset models + LOSO are the real result here.

## Consequences

- The real-data path is proven: data → GEE features → offsets → LOSO, end to end.
- Data files live in `data/` (gitignored); the build scripts and `loso_metrics.json`
  are committed. Reproducible via the two scripts + EE auth.
- Next: (a) fix the ambient reference; (b) add SoilTemp multi-landscape labels for
  genuine cross-macroclimate transfer.
