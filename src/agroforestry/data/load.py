"""Real-data loader -- wire this to your borrowed labels + remote sensing.

Must return a pandas DataFrame with EXACTLY the columns the synthetic generator
produces: config.RAW_FEATURES + config.TARGETS + config.GROUP_COL.

Suggested assembly (all free, mostly via Google Earth Engine):
  1. Microclimate labels (targets): SoilTemp / ForestTemp / agroforestry datasets.
     - Compute offsets: under-canopy minus nearest ambient (ERA5/station).
       dT_max = T_max_subcanopy - T_max_ambient, etc.
  2. Macro features: ERA5-Land or NASA POWER at each label site/time.
  3. Canopy features: Sentinel-2 LAI/FAPAR, ETH/Meta canopy height, NDVI.
  4. Terrain: Copernicus DEM derivatives (slope, TWI).
  5. Soil: SoilGrids (soc, clay).
  6. site_id: one id per spatial site (drives leave-one-site-out CV).
"""
import pandas as pd
from agroforestry.config import RAW_FEATURES, TARGETS, GROUP_COL


def load_real(path="data/labelled_offsets.parquet"):
    df = pd.read_parquet(path)
    required = set(RAW_FEATURES + TARGETS + [GROUP_COL])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"data is missing required columns: {sorted(missing)}")
    return df
