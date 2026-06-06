# Data acquisition guide (layer 1 real data)

How to replace the synthetic generator with real borrowed-label data. Everything
here lands in `data/` (gitignored) and produces
`data/processed/labelled_offsets.parquet`, after which the pipeline runs
unchanged with `DATA_SOURCE = "real"` in `cli/run_pipeline.py`.

## The three data sources

| Need | Source | Access | Notes |
|---|---|---|---|
| Microclimate labels (targets) | **ForestTemp** (figshare), **SoilTemp** network, agroforestry field datasets (e.g. cocoa Zenodo) | ForestTemp = direct download; SoilTemp = request/contribute | Provide paired sub-canopy + ambient temp/RH per site/time |
| Predictor features | **Google Earth Engine** (ERA5-Land, MODIS/Sentinel-2 LAI, ETH canopy height, Copernicus DEM, SoilGrids) | Free GEE research account | Pulled by `scripts/fetch_earth_engine.py` |
| Ambient pairing | nearest ERA5-Land cell or station, if the label set lacks an ambient series | GEE | Used to compute offsets when only sub-canopy is measured |

## Steps

1. **Assemble label sites** into a CSV: `site_id, lat, lon, date` plus the paired
   measurements `sub_t_max, amb_t_max, sub_t_mean, amb_t_mean, sub_rh, amb_rh`.
   Start with the tropical / agroforestry subset (closest to Pattukkottai); the
   temperate-forest bulk is fine for pretraining.
2. **Authenticate GEE** (one-time):
   ```
   uv add earthengine-api
   uv run earthengine authenticate
   ```
3. **Fetch features**:
   ```
   uv run python scripts/fetch_earth_engine.py --sites data/raw/label_sites.csv \
       --out data/processed/site_features.parquet --project <your-gee-project>
   ```
   Verify the asset ids / band names against the current GEE catalog first.
4. **Compute offsets + join** (small script or notebook):
   ```python
   import pandas as pd
   from agroforestry.data.load import compute_offset_targets
   labels   = pd.read_csv("data/raw/label_sites.csv")
   feats    = pd.read_parquet("data/processed/site_features.parquet")
   labels   = compute_offset_targets(labels)          # adds dT_max, dT_mean, dVPD
   merged   = feats.merge(labels, on="site_id")
   # rename GEE band columns to config.RAW_FEATURES names here
   merged.to_parquet("data/processed/labelled_offsets.parquet")
   ```
5. **Switch + run**: set `DATA_SOURCE = "real"` and
   `uv run python scripts/run_pipeline.py`. `load_real` validates the schema and
   raises if any required column is missing.

## Validation reminder

Keep `site_id` as one id per spatial site so leave-one-site-out (and ideally
leave-one-climate-zone-out) CV measures real transfer. Expect the borrowed,
mostly-temperate labels to under-perform on tropical agroforestry until the
year-2 local sensors fine-tune layer 1 -- that gap is itself a result.
