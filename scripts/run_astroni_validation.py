"""EXTERNAL VALIDATION — Astroni crater reserve, Naples, Italy (ADR-016).

Independent, pre-registered, within-climate (Mediterranean) external test of the
trained canopy -> microclimate-offset model. Scores the model that
`scripts/run_validation.py` validates internally (LOSO/LOCO), on data it has never
seen: AngeloRita "Astroni_monitoring", Astroni crater reserve (Quercus ilex forest
stand), near Naples, Italy (SoilTemp/MDB deposit `AngeloRita_Astroni`, CC-BY).

This is the INDEPENDENT MEDITERRANEAN VPD leg of Paper 1. The model was trained
partly on Mediterranean La Jarda (Cadiz, Spain), so an independent Mediterranean
site is a legitimate within-climate positive test. It is the ONLY external set so
far that carries relative humidity AT the reference height (+15 cm), so it is the
only one that can test `dVPD`, not just temperature.

Two stages, run separately and IN THIS ORDER, so the test set is built blind:

    uv run python scripts/run_astroni_validation.py --stage freeze   # needs Earth Engine
    uv run python scripts/run_astroni_validation.py --stage score    # offline, ONCE

  freeze -> data/processed/astroni_external_test.parquet  (gitignored)
            data/processed/astroni_test_manifest.json
  score  -> reports/astroni_external_metrics.json         (mirrors cocoa_external_metrics.json)

The pre-registration rule (docs/external_validation_datasets.md, ADR-016) is that
the frozen set is built without looking at model performance, de-duplicated by site
coordinates against data/processed/all_label_sites.csv, and scored exactly once.
Nothing here may be re-tuned after the numbers are seen (ADR-016).

Conventions replicated EXACTLY from the training pipeline (do not "improve" them
here -- comparability is the whole point):
  * labels  : scripts/build_safe_labels.py + scripts/build_lajarda_labels.py
              sub-daily -> daily (daily max / daily mean / daily mean-RH) ->
              monthly mean of the dailies, months with >= 5 logged days only,
              date stamped YYYY-MM-15.
  * ambient : scripts/build_real_dataset.py -- ERA5 *atmospheric* (free-air,
              ~31 km), NOT ERA5-Land (canopy-coupled, ADR-006). Solar only from
              ERA5-Land (radiation is top-of-canopy). Astroni is 2023 and GEE's
              `ECMWF/ERA5/DAILY` stops at 2020-07-09, so the identical fields are
              rebuilt from `ECMWF/ERA5/HOURLY` on the ERA5/DAILY grid node
              (scripts/run_murugan_fewshot.py method) and verified to reproduce
              ERA5/DAILY to <1e-3 K on pre-2020 overlap months at this location.
  * features: ETH canopy height + MODIS LAI/FPAR/NDVI + Copernicus DEM/slope/TWI
              + SoilGrids clay/soc, same bands, scalings and reducer. MODIS window
              = the observation year (2023), the rule the training build used.
  * offsets : src/agroforestry/data/load.py convention --
              dT_max = sub_t_max - amb_t_max, dT_mean = sub_t_mean - amb_t_mean,
              dVPD = es(sub_t_max)*(1-sub_rh/100) - es(amb_t_max)*(1-amb_rh/100).

SENSORS (verified from the deposit -- see module comments in build_labels):
  * The 4 sites each carry a +15 cm shielded AIR-temperature sensor (the SAFE ~15 cm
    / La Jarda ~30 cm analogue). AS02/AS03/AS04 are TOMST TMS-4 (T at +15/+2/-6 cm);
    AS01 is a T+RH+dew-point logger at +15 cm.
  * RELATIVE HUMIDITY exists at ONE site only (AS01, +15 cm). dT_max/dT_mean are
    therefore computed at all 4 sites; dVPD is computed at AS01 only. dVPD is NOT
    manufactured for the RH-less sites via `build_real_dataset.py`'s amb_rh fallback
    (that would create a temperature-only pseudo-VPD -- deliberately refused, exactly
    as scripts/run_murugan_fewshot.py refused it).

ADR-017 orographic screen: PASSED before freezing (site ~85 m vs ~31 km ERA5 box
mean ~35 m, diff ~-51 m; worst single site |diff| 71 m, under the 100 m threshold;
low relief). The orographic failure that invalidated the cocoa run does not apply.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd

from agroforestry.config import RAW_FEATURES, TARGETS, GROUP_COL
from agroforestry.features import engineer
from agroforestry.models import QuantileModel, HybridQuantileModel
from agroforestry.validation import _metrics

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "data", "raw", "soiltemp_mdb_data")
ASTRONI_XLSX = os.path.join(RAW, "AngeloRita_Astroni.xlsx")
TRAIN_PARQUET = os.path.join(ROOT, "data", "processed", "labelled_offsets.parquet")
TRAIN_SITES = os.path.join(ROOT, "data", "processed", "all_label_sites.csv")
FROZEN = os.path.join(ROOT, "data", "processed", "astroni_external_test.parquet")
MANIFEST = os.path.join(ROOT, "data", "processed", "astroni_test_manifest.json")
METRICS = os.path.join(ROOT, "reports", "astroni_external_metrics.json")

DATA_SOURCE = "AngeloRita_Astroni"
EE_PROJECT = "microclimate-crop-design-sys"
DEDUP_KM = 1.0
MIN_DAYS_PER_MONTH = 5            # identical to the SAFE / La Jarda / cocoa builders
REF_HEIGHT_CM = 15               # the sub-canopy reference height (SAFE ~15 cm analogue)
# Sentinel screen: plausible near-surface air temperatures. The verified deposit
# range is 0.94..42.31 C, comfortably inside this window (nothing expected dropped).
PLAUSIBLE_C = (-40.0, 65.0)
PLAUSIBLE_RH = (0.0, 100.0)
# nearest training site (La Jarda ~36.57 N / -5.60 E) is ~1,770 km away
NAPLES_REF = (40.84, 14.15)

SCORED_TARGETS = TARGETS         # dT_max, dT_mean, dVPD (dVPD scored on AS01 only)
# Training feature-completeness rule (scripts/build_real_dataset.py line ~118): rows
# missing ANY of these are dropped from the training set, so the model never sees a NaN
# in them. Replicating the convention exactly means applying the SAME drop to the test.
CANOPY_COMPLETE_COLS = ["lai", "canopy_height", "ndvi", "elevation", "clay", "soc"]

ERA_BANDS = ["mean_2m_air_temperature", "maximum_2m_air_temperature",
             "minimum_2m_air_temperature", "dewpoint_2m_temperature",
             "u_component_of_wind_10m", "v_component_of_wind_10m",
             "total_precipitation"]


# --------------------------------------------------------------------------
# shared helpers (verbatim from scripts/build_real_dataset.py / run_cocoa_validation.py)
# --------------------------------------------------------------------------
def es(t_c):                       # saturation vapour pressure kPa (Tetens)
    return 0.6108 * math.exp(17.27 * t_c / (t_c + 237.3))


def rh_from(t_c, td_c):            # RH % from temp + dewpoint (Magnus)
    a, b = 17.625, 243.04
    return 100 * math.exp(a * td_c / (b + td_c)) / math.exp(a * t_c / (b + t_c))


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = p2 - p1
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def era5_daily_grid_node(lat, lon):
    """NW corner of the `ECMWF/ERA5/DAILY` pixel containing (lat, lon).

    ERA5/DAILY (1979..2020-07-09) and ERA5/HOURLY (1940..present) sit on grids with a
    HALF-CELL offset. Sampling HOURLY at the ERA5/DAILY pixel's NW node reproduces the
    ERA5/DAILY value to <1e-3 K; naive HOURLY sampling at the site silently shifts the
    ~31 km reference cell. See scripts/run_murugan_fewshot.py (verbatim method).
    """
    lon_w = math.floor((lon + 180.0) / 0.25) * 0.25 - 180.0
    lat_n = 90.0 - math.floor((90.0 - lat) / 0.25) * 0.25
    return round(lat_n, 4), round(lon_w, 4)


# --------------------------------------------------------------------------
# STAGE 1 -- freeze the external test set (blind to performance)
# --------------------------------------------------------------------------
def read_metadata_and_map() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Parse the Astroni workbook, join the time series to the metadata on the exact
    Raw_data_identifier, and pick the +15 cm air-T sensor per site plus the (single)
    +15 cm RH sensor.

    IMPORTANT structural fact (verified): the Metadata sheet contains placeholder /
    duplicate rows that re-list each logger under a second Site_id with a swapped
    measurement set. Those placeholder identifiers have NO matching time series, so
    the join to the actual `Raw time series data` identifiers is authoritative and
    resolves every real sensor to exactly one (Site_id, measurement, height).
    """
    md = pd.read_excel(ASTRONI_XLSX, sheet_name="Metadata")
    ts = pd.read_excel(ASTRONI_XLSX, sheet_name="Raw time series data")
    ts["rid"] = ts["Raw_data_identifier"].astype(str)
    ts["val"] = pd.to_numeric(ts["clim_ts_values"], errors="coerce")
    for c in ("Year", "Month", "Day"):
        ts[c] = pd.to_numeric(ts[c], errors="coerce")

    md["rid"] = md["Raw_data_identifier"].astype(str)
    ts_ids = set(ts["rid"].unique())
    real = md[md["rid"].isin(ts_ids)].copy()   # only metadata rows with actual data

    # coordinate-frame guard: this deposit is EPSG:4326 (lat/lon), unlike the VonBuren
    # file. Verify explicitly and confirm the values are geographic degrees, not a
    # projected CRS accidentally read as lat/lon.
    epsg = set(int(x) for x in real["EPSG"].dropna().unique())
    lat_ok = real["Latitude"].between(-90, 90).all()
    lon_ok = real["Longitude"].between(-180, 180).all()
    med_lat, med_lon = real["Latitude"].median(), real["Longitude"].median()
    if epsg != {4326} or not (lat_ok and lon_ok) or not (40 < med_lat < 41 and 14 < med_lon < 15):
        raise SystemExit(f"COORD GUARD failed: EPSG={epsg}, lat_ok={lat_ok}, "
                         f"lon_ok={lon_ok}, median=({med_lat},{med_lon})")

    # +15 cm air temperature per site (the sub-canopy reference height)
    airT = real[(real["Microclimate_measurement"] == "Temperature")
                & (real["Sensor_height"] == REF_HEIGHT_CM)].copy()
    # +15 cm RH (AS01 only)
    rh = real[(real["Microclimate_measurement"] == "RH")
              & (real["Sensor_height"] == REF_HEIGHT_CM)].copy()

    prov = {
        "epsg": sorted(epsg),
        "coord_frame_guard": "PASSED (EPSG 4326, lat/lon in [40,41]x[14,15])",
        "n_sites": int(airT["Site_id"].nunique()),
        "air_T_ref_height_cm": REF_HEIGHT_CM,
        "sensor_map": [
            {"site_id": r.Site_id, "raw_data_identifier": r.rid,
             "measurement": r.Microclimate_measurement, "height_cm": float(r.Sensor_height),
             "shielding": str(r.Sensor_shielding), "logger": str(r.Logger_type),
             "time_difference_h": float(r.Time_difference),
             "lat": float(r.Latitude), "lon": float(r.Longitude), "elev_m": float(r.Elevation)}
            for r in airT.itertuples()],
        "rh_sites": [{"site_id": r.Site_id, "raw_data_identifier": r.rid,
                      "height_cm": float(r.Sensor_height)} for r in rh.itertuples()],
        "measurement_ranges": {
            m: {"n": int(g["val"].count()), "min": round(float(g["val"].min()), 3),
                "max": round(float(g["val"].max()), 3)}
            for m, g in ts[ts["rid"].isin(set(real["rid"]))]
            .assign(meas=lambda d: d["rid"].map(real.set_index("rid")["Microclimate_measurement"]))
            .groupby("meas")},
    }
    return real, ts, {"airT": airT, "rh": rh, "prov": prov}


def build_labels(real, ts, mapping) -> tuple[pd.DataFrame, dict]:
    """Long-format time series -> daily -> monthly, SAFE/La Jarda convention.

    daily : daily max T, daily mean T, daily mean RH
    month : monthly mean of the dailies, months with >= 5 logged days, stamp YYYY-MM-15
    RH is present at AS01 only; sub_rh stays NaN elsewhere (no amb_rh fallback).
    """
    airT, rh, prov = mapping["airT"], mapping["rh"], mapping["prov"]
    air_ids = dict(zip(airT["rid"], airT["Site_id"]))
    rh_by_site = dict(zip(rh["Site_id"], rh["rid"]))
    coords = airT.set_index("Site_id")[["Latitude", "Longitude", "Elevation"]].to_dict("index")

    # sentinel screen (verified deposit range is well inside PLAUSIBLE_C; nothing expected)
    used_ids = set(air_ids) | set(rh["rid"])
    used = ts[ts["rid"].isin(used_ids)].copy()
    is_temp = used["rid"].isin(air_ids)
    bad_t = is_temp & (~used["val"].between(*PLAUSIBLE_C) | used["val"].isna())
    is_rh = used["rid"].isin(set(rh["rid"]))
    bad_rh = is_rh & (~used["val"].between(*PLAUSIBLE_RH) | used["val"].isna())
    prov["sentinel_screen"] = {
        "plausible_T_window_C": list(PLAUSIBLE_C), "plausible_RH_window_pct": list(PLAUSIBLE_RH),
        "temp_rows_dropped": int(bad_t.sum()), "rh_rows_dropped": int(bad_rh.sum()),
    }

    # timezone diagnostic (reported, not applied). Aggregation uses the stamped
    # calendar day as-is -- the same thing the SAFE / La Jarda builders do.
    tzdiag = {}
    for rid, site in air_ids.items():
        d = ts[(ts["rid"] == rid) & ts["val"].between(*PLAUSIBLE_C)].copy()
        d["hour"] = d["Time (24H)"].astype(str).str.slice(0, 2).astype(int)
        bh = d.groupby("hour")["val"].mean()
        tzdiag[site] = {"raw_data_identifier": rid,
                        "metadata_time_difference_h": float(
                            airT.loc[airT["rid"] == rid, "Time_difference"].iloc[0]),
                        "peak_stamp_hour": int(bh.idxmax()), "min_stamp_hour": int(bh.idxmin())}
    prov["timezone_diagnostic"] = {
        "note": "metadata Timezone=UTC for all; Time_difference=0 for AS02/03/04 (TMS-4) "
                "and =2 for AS01. Solar noon at 14.15 E is ~11:03 UTC. Daily max/mean over "
                "a full stamped day are insensitive to a 2 h stamp offset; used as-is.",
        "per_site": tzdiag}

    # --- temperature: sub-daily -> daily -> monthly, per site ---
    frames = []
    for rid, site in air_ids.items():
        d = ts[(ts["rid"] == rid) & ts["val"].between(*PLAUSIBLE_C)].copy()
        d["dt"] = pd.to_datetime(dict(year=d.Year, month=d.Month, day=d.Day))
        daily = (d.groupby("dt").agg(sub_t_max=("val", "max"), sub_t_mean=("val", "mean"),
                                     n_obs=("val", "size")).reset_index())
        daily["y"] = daily.dt.dt.year
        daily["m"] = daily.dt.dt.month
        mon = (daily.groupby(["y", "m"])
               .agg(sub_t_max=("sub_t_max", "mean"), sub_t_mean=("sub_t_mean", "mean"),
                    n_days=("dt", "count")).reset_index())
        mon = mon[mon.n_days >= MIN_DAYS_PER_MONTH].copy()
        mon["site_id"] = "AST_" + site
        mon["lat"] = float(coords[site]["Latitude"])
        mon["lon"] = float(coords[site]["Longitude"])
        mon["meta_elev_m"] = float(coords[site]["Elevation"])
        frames.append(mon)
    labels = pd.concat(frames, ignore_index=True)

    # --- RH: same convention, AS01 only ---
    rh_monthly = {}   # (site_id, y, m) -> sub_rh
    for site, rid in rh_by_site.items():
        d = ts[(ts["rid"] == rid) & ts["val"].between(*PLAUSIBLE_RH)].copy()
        d["dt"] = pd.to_datetime(dict(year=d.Year, month=d.Month, day=d.Day))
        daily = d.groupby("dt").agg(rh=("val", "mean"), n_obs=("val", "size")).reset_index()
        daily["y"] = daily.dt.dt.year
        daily["m"] = daily.dt.dt.month
        mon = (daily.groupby(["y", "m"]).agg(sub_rh=("rh", "mean"),
                                             n_days=("dt", "count")).reset_index())
        mon = mon[mon.n_days >= MIN_DAYS_PER_MONTH]
        for r in mon.itertuples():
            rh_monthly[(f"AST_{site}", r.y, r.m)] = float(r.sub_rh)

    labels["sub_rh"] = [rh_monthly.get((s, y, m), np.nan)
                        for s, y, m in zip(labels.site_id, labels.y, labels.m)]
    labels["date"] = labels.apply(lambda r: f"{int(r.y):04d}-{int(r.m):02d}-15", axis=1)
    labels["ym"] = labels.apply(lambda r: f"{int(r.y):04d}-{int(r.m):02d}", axis=1)

    prov["label_summary"] = {
        "dT_site_month_rows": int(len(labels)),
        "sites": sorted(labels.site_id.unique().tolist()),
        "months_range": [labels.ym.min(), labels.ym.max()],
        "rh_site_month_rows": int(labels["sub_rh"].notna().sum()),
        "rh_site": sorted(labels.loc[labels["sub_rh"].notna(), "site_id"].unique().tolist()),
        "per_site_months": {s: int(g.ym.nunique()) for s, g in labels.groupby("site_id")},
    }
    return labels, prov


def dedup_report(labels: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """ADR-016 rule 3: drop any external site within ~1 km of a TRAINING site."""
    tr = pd.read_csv(TRAIN_SITES).drop_duplicates("site_id")
    d = haversine_km(labels["lat"].values[:, None], labels["lon"].values[:, None],
                     tr["lat"].values[None, :], tr["lon"].values[None, :])
    nearest_km = d.min(axis=1)
    nearest_idx = d.argmin(axis=1)
    labels = labels.copy()
    labels["nearest_train_km"] = nearest_km
    labels["nearest_train_site"] = tr["site_id"].values[nearest_idx]
    drop = nearest_km < DEDUP_KM
    rep = {
        "rule": f"drop external sites within {DEDUP_KM} km of any training site",
        "training_sites_checked": int(len(tr)),
        "external_sites_checked": int(labels["site_id"].nunique()),
        "min_distance_km": round(float(np.min(nearest_km)), 1),
        "nearest_training_site": str(labels["nearest_train_site"].iloc[int(np.argmin(nearest_km))]),
        "rows_dropped": int(drop.sum()),
        "sites_dropped": int(labels.loc[drop, "site_id"].nunique()),
    }
    return rep, labels.loc[~drop].copy()


# --------------------------------------------------------------------------
# Earth Engine
# --------------------------------------------------------------------------
def _ee_daily_from_hourly(ee, start, end):
    """Rebuild ECMWF/ERA5/DAILY's bands from ECMWF/ERA5/HOURLY over [start, end)."""
    n = end.difference(start, "day")

    def one(i):
        d0 = start.advance(ee.Number(i), "day")
        d1 = d0.advance(1, "day")
        h = ee.ImageCollection("ECMWF/ERA5/HOURLY").filterDate(d0, d1)
        t = h.select("temperature_2m")
        return (t.mean().rename("mean_2m_air_temperature")
                .addBands(t.max().rename("maximum_2m_air_temperature"))
                .addBands(t.min().rename("minimum_2m_air_temperature"))
                .addBands(h.select("dewpoint_temperature_2m").mean()
                          .rename("dewpoint_2m_temperature"))
                .addBands(h.select("u_component_of_wind_10m").mean()
                          .rename("u_component_of_wind_10m"))
                .addBands(h.select("v_component_of_wind_10m").mean()
                          .rename("v_component_of_wind_10m"))
                .addBands(h.select("total_precipitation").sum()
                          .rename("total_precipitation"))
                .set("d", d0.format("YYYY-MM-dd")))

    return ee.ImageCollection(ee.List.sequence(0, n.subtract(1)).map(one))


def _verify_ambient_equivalence(ee, node_pt, site_pt) -> dict:
    """Prove the HOURLY-rebuild reproduces ERA5/DAILY on pre-2020 months where BOTH
    collections exist (Astroni is 2023, so there is no 2023 overlap; the method is
    verified at THIS location on historical months)."""
    out = {}
    for ym in ["2013-06", "2019-08"]:
        y, m = map(int, ym.split("-"))
        start = ee.Date.fromYMD(y, m, 1)
        end = start.advance(1, "month")
        a = (ee.ImageCollection("ECMWF/ERA5/DAILY").filterDate(start, end)
             .select(ERA_BANDS).mean()
             .reduceRegion(ee.Reducer.mean(), site_pt, 1000).getInfo())
        b = (_ee_daily_from_hourly(ee, start, end).mean()
             .reduceRegion(ee.Reducer.mean(), node_pt, 1000).getInfo())
        out[ym] = {k: round(float(b[k]) - float(a[k]), 6) for k in ERA_BANDS}
    return out


def _static_image(ee):
    dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic().rename("elevation")
    slope = ee.Terrain.slope(dem).rename("slope")
    modveg = (ee.ImageCollection("MODIS/061/MOD15A2H")
              .filterDate("2023-01-01", "2024-01-01").select(["Lai_500m", "Fpar_500m"]).mean())
    return (ee.Image("users/nlang/ETH_GlobalCanopyHeight_2020_10m_v1").rename("canopy_height")
            .addBands(dem).addBands(slope)
            .addBands(ee.Image("projects/soilgrids-isric/clay_mean")
                      .select("clay_0-5cm_mean").rename("clay"))
            .addBands(ee.Image("projects/soilgrids-isric/soc_mean")
                      .select("soc_0-5cm_mean").rename("soc"))
            .addBands(modveg.select("Lai_500m").multiply(0.1).rename("lai"))
            .addBands(modveg.select("Fpar_500m").multiply(0.01).rename("fapar"))
            .addBands(ee.ImageCollection("MODIS/061/MOD13Q1")
                      .filterDate("2023-01-01", "2024-01-01")
                      .select("NDVI").mean().multiply(0.0001).rename("ndvi")))


def fetch_features(sites: pd.DataFrame, months: list[str]) -> dict:
    """Per-site static features + ERA5-atmospheric monthly ambient (rebuilt from
    HOURLY at the shared ERA5/DAILY node) + per-site ERA5-Land solar. Same assets /
    bands / scalings / reducer as scripts/build_real_dataset.py. Raises on any
    failure -- features are never approximated or substituted (ADR-016)."""
    import ee
    ee.Initialize(project=EE_PROJECT)

    static_img = _static_image(ee)
    # MOD15A2H LAI retrieval diagnostic: count of valid 2023 composites at each pixel.
    lai_count_img = (ee.ImageCollection("MODIS/061/MOD15A2H")
                     .filterDate("2023-01-01", "2024-01-01").select("Lai_500m")
                     .count().rename("lai_valid_count"))
    lai_mean_img = (ee.ImageCollection("MODIS/061/MOD15A2H")
                    .filterDate("2023-01-01", "2024-01-01").select("Lai_500m")
                    .mean().multiply(0.1).rename("lai_native"))

    # per-site static features + node assignment
    static = {}
    node_of = {}
    box_elev = {}
    lai_masking = {}
    for r in sites.itertuples():
        pt = ee.Geometry.Point([r.lon, r.lat])
        fc = ee.FeatureCollection([ee.Feature(pt, {"site_id": r.site_id})])
        print(f"fetching static features for {r.site_id} ...")
        static[r.site_id] = (static_img.reduceRegions(fc, ee.Reducer.mean(), 250)
                             .getInfo()["features"][0]["properties"])
        # LAI masking evidence: valid-composite count + native-pixel value (reduceRegion,
        # the point-exact sample) contrasted with the reduceRegions value actually used.
        lai_masking[r.site_id] = {
            "lai_valid_composites_2023": lai_count_img.reduceRegion(
                ee.Reducer.mean(), pt, 500).getInfo().get("lai_valid_count"),
            "lai_native_pixel_reduceRegion": lai_mean_img.reduceRegion(
                ee.Reducer.mean(), pt, 500).getInfo().get("lai_native"),
            "lai_used_reduceRegions_scale250": static[r.site_id].get("lai"),
            "fapar_used_reduceRegions_scale250": static[r.site_id].get("fapar"),
            "ndvi_used": static[r.site_id].get("ndvi"),
        }
        node_of[r.site_id] = era5_daily_grid_node(r.lat, r.lon)
        # ADR-017 record: mean DEM elevation inside the ~31 km ERA5 cell vs site elev
        node_lat, node_lon = node_of[r.site_id]
        cell = ee.Geometry.Rectangle([node_lon, node_lat - 0.25, node_lon + 0.25, node_lat])
        be = (static_img.select("elevation").reduceRegion(ee.Reducer.mean(), cell, 250)
              .getInfo().get("elevation"))
        box_elev[r.site_id] = be

    # ERA5 atmospheric monthly at each unique node (shared -> fetched once per node)
    uniq_nodes = sorted(set(node_of.values()))
    era_node = {n: {} for n in uniq_nodes}
    node_pts = {n: ee.Geometry.Point([n[1], n[0]]) for n in uniq_nodes}
    for n in uniq_nodes:
        for ym in months:
            y, m = map(int, ym.split("-"))
            start = ee.Date.fromYMD(y, m, 1)
            end = start.advance(1, "month")
            era_node[n][ym] = (_ee_daily_from_hourly(ee, start, end).mean()
                               .reduceRegion(ee.Reducer.mean(), node_pts[n], 1000).getInfo())
        print(f"ERA5 atmospheric monthly done for node {n}: {len(era_node[n])} months")

    # per-site solar (ERA5-Land, top-of-canopy) at the site point
    solar = {r.site_id: {} for r in sites.itertuples()}
    for r in sites.itertuples():
        pt = ee.Geometry.Point([r.lon, r.lat])
        for ym in months:
            y, m = map(int, ym.split("-"))
            start = ee.Date.fromYMD(y, m, 1)
            end = start.advance(1, "month")
            sol = (ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterDate(start, end)
                   .select("surface_solar_radiation_downwards_sum").mean()
                   .reduceRegion(ee.Reducer.mean(), pt, 1000).getInfo()
                   .get("surface_solar_radiation_downwards_sum"))
            solar[r.site_id][ym] = sol
        print(f"ERA5-Land solar done for {r.site_id}")

    # equivalence verification (once, at the first site's node vs site)
    r0 = sites.iloc[0]
    print("verifying ERA5 HOURLY-rebuild == ERA5/DAILY on pre-2020 overlap months ...")
    equiv = _verify_ambient_equivalence(
        ee, node_pts[node_of[r0.site_id]], ee.Geometry.Point([r0.lon, r0.lat]))
    worst = max(abs(v) for d in equiv.values()
                for k, v in d.items() if k.endswith("air_temperature"))
    print(f"  max |diff| on the temperature bands: {worst:.2e} K")

    return {"static": static, "node_of": node_of, "era_node": era_node,
            "solar": solar, "box_elev": box_elev, "equivalence_check": equiv,
            "lai_masking": lai_masking}


def _row(site_id, r, e, stat, solar_jm2):
    slope_deg = stat.get("slope") or 0.0
    twi = math.log(1.0 / (math.tan(math.radians(slope_deg)) + 0.01))
    amb_tmean = e["mean_2m_air_temperature"] - 273.15
    amb_tmax = e["maximum_2m_air_temperature"] - 273.15
    amb_tmin = e["minimum_2m_air_temperature"] - 273.15
    amb_rh = rh_from(amb_tmean, e["dewpoint_2m_temperature"] - 273.15)
    wind = math.hypot(e["u_component_of_wind_10m"], e["v_component_of_wind_10m"])
    solar = (solar_jm2 or 0.0) / 1e6
    rainfall = max(0.0, e["total_precipitation"]) * 1000 * 365
    # dVPD: computed ONLY where real sub-canopy RH exists (AS01). No amb_rh fallback --
    # a temperature-only pseudo-VPD is deliberately refused (ADR-006 / Murugan precedent).
    sub_rh = r.sub_rh
    if pd.notna(sub_rh):
        dvpd = es(r.sub_t_max) * (1 - sub_rh / 100) - es(amb_tmax) * (1 - amb_rh / 100)
    else:
        dvpd = np.nan
    return {
        "site_id": site_id,
        "t_mean": amb_tmean, "t_max": amb_tmax, "t_min": amb_tmin, "rh": amb_rh,
        "wind": wind, "solar": solar, "rainfall": rainfall,
        "lai": stat.get("lai"), "canopy_height": stat.get("canopy_height"),
        "ndvi": stat.get("ndvi"), "fapar": stat.get("fapar"),
        "elevation": stat.get("elevation"), "slope": slope_deg, "twi": twi,
        "soc": stat.get("soc"), "clay": stat.get("clay"),
        "dT_max": r.sub_t_max - amb_tmax,
        "dT_mean": r.sub_t_mean - amb_tmean,
        "dVPD": dvpd,
        # provenance / diagnostics (NOT model inputs)
        "date": r.date, "ym": r.ym, "lat": r.lat, "lon": r.lon,
        "n_days": r.n_days, "sub_t_max": r.sub_t_max, "sub_t_mean": r.sub_t_mean,
        "sub_rh": sub_rh, "amb_t_max": amb_tmax, "amb_t_mean": amb_tmean, "amb_rh": amb_rh,
    }


def stage_freeze() -> None:
    real, ts, mapping = read_metadata_and_map()
    labels, prov = build_labels(real, ts, mapping)
    print(f"label rows {len(labels)} | sites {labels.site_id.nunique()} "
          f"| months {labels.ym.min()}..{labels.ym.max()} "
          f"| RH rows {labels['sub_rh'].notna().sum()}")

    dedup, labels = dedup_report(labels)
    print("de-dup vs training sites:", json.dumps(dedup))
    if labels.empty:
        raise SystemExit("all external sites de-duplicated away -- nothing to score")

    sites = (labels[["site_id", "lat", "lon", "meta_elev_m"]]
             .drop_duplicates("site_id").reset_index(drop=True))
    months = sorted(labels.ym.unique())
    try:
        ee_out = fetch_features(sites, months)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            "BLOCKER: Earth Engine feature fetch failed -- features must NOT be "
            f"approximated or substituted (ADR-016 comparability). Cause: {exc!r}")

    rows = []
    for r in labels.itertuples():
        node = ee_out["node_of"][r.site_id]
        e = ee_out["era_node"][node].get(r.ym)
        if not e or e.get("mean_2m_air_temperature") is None:
            continue
        rows.append(_row(r.site_id, r, e, ee_out["static"][r.site_id],
                         ee_out["solar"][r.site_id].get(r.ym)))

    df = pd.DataFrame(rows)
    before = len(df)
    # Keep every row with a valid dT label + complete AMBIENT/terrain/soil features.
    # LAI/FPAR are NOT in this drop list on purpose: MOD15A2H is masked over the whole
    # crater (evidence below), so dropping on lai (as the training build does) would
    # collapse the set to one site and erase the RH/dVPD site. The training-convention
    # completeness is instead recorded per row via `canopy_complete`, and the score
    # stage reports BOTH the convention-exact subset and the full LAI-masked set.
    essential = ["t_mean", "t_max", "t_min", "rh", "wind", "solar", "rainfall", "twi",
                 "dT_max", "dT_mean"]
    df = df.dropna(subset=essential)
    df["canopy_complete"] = df[CANOPY_COMPLETE_COLS].notna().all(axis=1)
    print(f"rows: {before} -> {len(df)} (essential-complete) | "
          f"canopy_complete (training convention) = {int(df['canopy_complete'].sum())} | "
          f"dVPD rows = {int(df['dVPD'].notna().sum())}")

    # LAI masking evidence -- the decisive dataset-suitability finding
    lai_mask = ee_out["lai_masking"]
    n_valid_lai_sites = sum(
        1 for v in lai_mask.values()
        if v.get("lai_valid_composites_2023") not in (None, 0))
    lai_evidence = {
        "product": "MODIS/061/MOD15A2H Lai_500m/Fpar_500m (500 m), 2023 annual mean",
        "per_site": lai_mask,
        "sites_with_ANY_valid_lai_pixel": int(n_valid_lai_sites),
        "verdict": ("MOD15A2H LAI/FPAR has ZERO valid retrievals at every Astroni pixel "
                    "in 2023 (urban-embedded forest crater; the 500 m LAI algorithm masks "
                    "these pixels). NDVI (MOD13Q1 250 m) resolves normally. Any non-NaN "
                    "lai a reduceRegions call returns is an edge artifact bled from a "
                    "neighbouring pixel, NOT a site measurement."),
    }

    # feature-spread honesty (ADR-017 lesson): how many DISTINCT feature vectors?
    static_feats = ["lai", "canopy_height", "ndvi", "fapar", "elevation", "slope", "twi",
                    "soc", "clay"]
    Xte_all, feats = engineer(df)
    spread = {
        "n_rows": int(len(df)), "n_sites": int(df.site_id.nunique()),
        "n_unique_full_feature_rows_all": int(Xte_all.fillna(-999).drop_duplicates().shape[0]),
        "n_unique_by_static_feature": {c: int(df[c].nunique(dropna=True)) for c in static_feats},
        "canopy_complete_rows": int(df["canopy_complete"].sum()),
        "canopy_complete_sites": sorted(df.loc[df["canopy_complete"], "site_id"].unique().tolist()),
        "static_feature_values_per_site": {
            s: {c: (None if pd.isna(g[c].iloc[0]) else round(float(g[c].iloc[0]), 5))
                for c in static_feats}
            for s, g in df.groupby("site_id")},
        "note": ("canopy_height, ndvi, elevation, soc DO vary across the 4 sites (4 distinct "
                 "vectors) -- a real improvement over cocoa's single vector -- but lai/fapar, "
                 "and hence the lai_x_height interaction (the dominant dT_max feature in "
                 "training, ADR-006), are MASKED at every site."),
    }

    # RAW (model-free) offset diagnostics -- the physical signal, independent of the model
    raw = {
        "dT_all_sites": {
            "n": int(len(df)), "sites": int(df.site_id.nunique()),
            "dT_max_mean": round(float(df["dT_max"].mean()), 3),
            "dT_mean_mean": round(float(df["dT_mean"].mean()), 3),
            "training_means": {"dT_max": -2.04, "dT_mean": -1.01},
            "per_site": {s: {"n": int(len(g)),
                             "dT_max_mean": round(float(g["dT_max"].mean()), 3),
                             "dT_mean_mean": round(float(g["dT_mean"].mean()), 3)}
                         for s, g in df.groupby("site_id")},
        },
        "dVPD_AS01": ({
            "n": int(df["dVPD"].notna().sum()),
            "dVPD_mean_kPa": round(float(df.loc[df["dVPD"].notna(), "dVPD"].mean()), 4),
            "dVPD_min_kPa": round(float(df.loc[df["dVPD"].notna(), "dVPD"].min()), 4),
            "dVPD_max_kPa": round(float(df.loc[df["dVPD"].notna(), "dVPD"].max()), 4),
            "sub_rh_mean_pct": round(float(df.loc[df["dVPD"].notna(), "sub_rh"].mean()), 2),
        } if df["dVPD"].notna().any() else {"n": 0}),
    }

    os.makedirs(os.path.dirname(FROZEN), exist_ok=True)
    df.to_parquet(FROZEN, index=False)

    # ADR-017 elevation-representativeness record (recorded, not gating -- pre-screen PASSED)
    adr017 = {
        "status": "PASSED at pre-screen (recorded, not re-run as a gate)",
        "per_site": {r.site_id: {
            "site_meta_elev_m": float(r.meta_elev_m),
            "site_dem_elev_m": ee_out["static"][r.site_id].get("elevation"),
            "era5_cell_mean_dem_elev_m": ee_out["box_elev"][r.site_id],
            "cell_mean_minus_site_dem_m": (
                None if ee_out["box_elev"][r.site_id] is None
                or ee_out["static"][r.site_id].get("elevation") is None
                else round(ee_out["box_elev"][r.site_id]
                           - ee_out["static"][r.site_id].get("elevation"), 1)),
        } for r in sites.itertuples()},
        "threshold_m": 100,
    }

    manifest = {
        "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "data_source": DATA_SOURCE,
        "rows": int(len(df)), "sites": int(df.site_id.nunique()),
        "months": int(df.ym.nunique()), "period": [df.ym.min(), df.ym.max()],
        "canopy_complete_rows": int(df["canopy_complete"].sum()),
        "dVPD_rows": int(df["dVPD"].notna().sum()),
        "dVPD_sites": sorted(df.loc[df["dVPD"].notna(), "site_id"].unique().tolist()),
        "lai_masking_evidence": lai_evidence,
        "raw_offset_diagnostics": raw,
        "convention": {
            "labels": "sub-daily -> daily(max/mean/mean-RH) -> monthly mean of dailies, "
                      ">=5 days, YYYY-MM-15 (SAFE/La Jarda)",
            "ambient": "ERA5 atmospheric free-air rebuilt from ERA5/HOURLY at the "
                       "ERA5/DAILY grid node (ADR-006); solar from ERA5-Land",
            "offsets": "dT_max=sub_t_max-amb_t_max, dT_mean=sub_t_mean-amb_t_mean, "
                       "dVPD=es(sub_t_max)(1-sub_rh/100)-es(amb_t_max)(1-amb_rh/100)",
            "reference_height_cm": REF_HEIGHT_CM,
            "dVPD_note": "computed only where real +15 cm RH exists (AS01); NOT "
                         "manufactured via amb_rh fallback for RH-less sites",
        },
        "provenance": prov,
        "dedup": dedup,
        "feature_spread": spread,
        "adr017_orographic": adr017,
        "modis_window": ["2023-01-01", "2024-01-01"],
        "era5_daily_grid_node_per_site": {k: list(v) for k, v in ee_out["node_of"].items()},
        "ambient_equivalence_check": ee_out["equivalence_check"],
        "static_features_per_site": {
            s: {k: v for k, v in ee_out["static"][s].items() if k != "site_id"}
            for s in ee_out["static"]},
    }
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"-> {FROZEN}\n-> {MANIFEST}")
    print("\n=== LAI MASKING EVIDENCE (decisive) ===")
    print(json.dumps(lai_evidence, indent=2, default=str))
    print("\n=== FROZEN SET SUMMARY ===")
    print(json.dumps({"rows": manifest["rows"], "sites": manifest["sites"],
                      "canopy_complete_rows": manifest["canopy_complete_rows"],
                      "months": manifest["months"], "period": manifest["period"],
                      "dVPD_rows": manifest["dVPD_rows"], "dedup": dedup,
                      "feature_spread": spread, "adr017": adr017,
                      "raw_offset_diagnostics": raw,
                      "equivalence_worst_K": max(
                          abs(v) for d in ee_out["equivalence_check"].values()
                          for kk, v in d.items() if kk.endswith("air_temperature"))},
                     indent=2, default=str))
    print("\n=== OFFSET SIGN SANITY (training means: dT_max -2.04, dT_mean -1.01) ===")
    print(df[["dT_max", "dT_mean", "dVPD", "sub_t_max", "amb_t_max", "sub_rh"]]
          .describe().round(3).T.to_string())


# --------------------------------------------------------------------------
# STAGE 2 -- score ONCE
# --------------------------------------------------------------------------
def _score_one(train, sub, tgt, feats, Xtr_v, groups, models):
    """Fit each model on ALL training rows (group-aware conformal), score `sub` once."""
    Xte, _ = engineer(sub)
    Xte_v = Xte[feats].values
    yte = sub[tgt].values
    ytr = train[tgt].values
    y_train_mean = np.full(len(yte), float(np.mean(ytr)))
    block = {
        "n_test": int(len(yte)), "n_sites": int(sub.site_id.nunique()),
        "n_unique_feature_rows": int(Xte.fillna(-999).drop_duplicates().shape[0]),
        "obs_offset_mean": float(np.mean(yte)), "obs_offset_std": float(np.std(yte)),
    }
    for name, factory in models.items():
        t0 = time.time()
        qm = factory().fit(Xtr_v, ytr, feature_names=feats, groups=groups)
        pred = qm.predict(Xte_v)
        mae, rmse, cov, width, mae_base, r2 = _metrics(yte, pred, y_train_mean)
        res = {
            "n_test": int(len(yte)), "MAE": mae, "RMSE": rmse,
            "interval_coverage": cov, "interval_nominal": 0.80, "interval_width": width,
            "baseline_MAE": mae_base,
            "skill_vs_baseline": float(1.0 - mae / mae_base) if mae_base > 0 else float("nan"),
            "R2_oos": r2,
            "obs_mean": float(np.mean(yte)), "obs_std": float(np.std(yte)),
            "pred_mean": float(np.mean(pred["median"])), "pred_std": float(np.std(pred["median"])),
            "bias_pred_minus_obs": float(np.mean(pred["median"] - yte)),
            "seconds": round(time.time() - t0, 1),
        }
        resid = pd.DataFrame({"site": sub.site_id.values,
                              "ae": np.abs(yte - pred["median"]),
                              "cov": ((yte >= pred["lower"]) & (yte <= pred["upper"])).astype(float)})
        res["per_site"] = {
            k: {"n": int(v["ae"].size), "MAE": float(v["ae"].mean()),
                "interval_coverage": float(v["cov"].mean())}
            for k, v in resid.groupby("site")}
        if name == "pure_xgb":
            ood = qm.ood_score(Xte_v)
            res["ood"] = {
                "definition": "fraction of engineered features outside the training "
                              "min/max box (models.QuantileModel.ood_score)",
                "flag_threshold": 0.15,
                "external_mean": float(ood.mean()),
                "external_min": float(ood.min()), "external_max": float(ood.max()),
                "external_frac_flagged": float((ood > 0.15).mean()),
                "train_mean": float(qm.ood_score(Xtr_v).mean()),
                "features_out_of_range": sorted(
                    {feats[j] for j in np.where(
                        ((Xte_v < qm.feat_lo) | (Xte_v > qm.feat_hi)).any(axis=0))[0]}),
                "caveat": "NaN features (masked lai/fapar) compare False and are counted "
                          "IN-range, so ood_score UNDER-counts on the LAI-masked set",
            }
        block[name] = res
        print(f"    {name:9s} n={len(yte):3d} MAE {mae:.3f} RMSE {rmse:.3f} "
              f"skill {res['skill_vs_baseline']*100:6.1f}% R2 {r2:.2f} "
              f"cov {cov:.2f} width {width:.2f}")
    return block


def stage_score() -> None:
    train = pd.read_parquet(TRAIN_PARQUET)
    test = pd.read_parquet(FROZEN)
    manifest = json.load(open(MANIFEST))
    Xtr, feats = engineer(train)
    Xtr_v = Xtr[feats].values
    groups = train[GROUP_COL].astype(str).values
    print(f"train rows {len(train)} sites {pd.Series(groups).nunique()} | "
          f"frozen rows {len(test)} sites {test.site_id.nunique()} "
          f"(canopy_complete {int(test.canopy_complete.sum())})")

    models = {"pure_xgb": QuantileModel, "hybrid": HybridQuantileModel}
    # Two frozen views, decided BEFORE scoring (mirrors run_murugan_fewshot primary/secondary):
    #  * primary_convention_exact : rows passing the training feature-completeness rule
    #    (canopy_complete). This is the ONLY comparable view. LAI is masked crater-wide,
    #    so it reduces to whichever site reduceRegions gave an (artefact) LAI to.
    #  * secondary_lai_masked_all_sites : all 4 sites, lai/fapar = NaN passed to XGBoost's
    #    native missing-value handling. NOT the training convention (the model was never
    #    trained on NaN lai); non-comparable, reported for completeness so the 4-site dT
    #    and the AS01 dVPD signal are visible.
    strict = test[test.canopy_complete].reset_index(drop=True)
    out = {
        "_meta": {
            "scored_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "experiment": "independent Mediterranean within-climate external validation "
                          "(Astroni crater, Naples) of the canopy->offset model "
                          "(ADR-016 discipline); intended as the only external dVPD test",
            "data_source": DATA_SOURCE,
            "test_set": os.path.relpath(FROZEN, ROOT),
            "frozen_rows": int(len(test)), "frozen_sites": int(test.site_id.nunique()),
            "canopy_complete_rows": int(test.canopy_complete.sum()),
            "test_period": [test.ym.min(), test.ym.max()],
            "train_rows": int(len(train)), "train_sites": int(pd.Series(groups).nunique()),
            "protocol": "external hold-out; model fit on ALL training rows "
                        "(group-aware conformal calibration), scored once",
            "baseline": "training-mean offset (identical to validation.py)",
            "scored_targets": SCORED_TARGETS,
            "headline": "METHODOLOGICAL NULL -- MOD15A2H LAI/FPAR (the dominant canopy "
                        "predictor) has ZERO valid retrievals crater-wide, so no site has a "
                        "valid canopy feature vector; the canopy->offset mapping is untestable "
                        "and the intended dVPD validation cannot be delivered. See "
                        "lai_masking_evidence and raw_offset_diagnostics.",
            "manifest": os.path.relpath(MANIFEST, ROOT),
        },
        "lai_masking_evidence": manifest["lai_masking_evidence"],
        "raw_offset_diagnostics": manifest["raw_offset_diagnostics"],
        "provenance": manifest["provenance"],
        "dedup": manifest["dedup"],
        "feature_spread": manifest["feature_spread"],
        "adr017_orographic": manifest["adr017_orographic"],
        "ambient_equivalence_check": manifest["ambient_equivalence_check"],
    }

    for tgt in SCORED_TARGETS:
        out[tgt] = {}
        for view_name, base in [("primary_convention_exact", strict),
                                ("secondary_lai_masked_all_sites", test)]:
            sub = base[base[tgt].notna()].reset_index(drop=True)
            print(f"[{tgt}] {view_name}: n={len(sub)} sites={sub.site_id.nunique() if len(sub) else 0}")
            if len(sub) == 0:
                out[tgt][view_name] = {
                    "n_test": 0,
                    "not_scoreable": (
                        "dVPD needs +15 cm RH (AS01 only); AS01 fails the training "
                        "canopy-completeness rule (masked lai) so it is absent from the "
                        "convention-exact view -- dVPD is not model-scoreable under the "
                        "training convention. See raw_offset_diagnostics.dVPD_AS01."
                        if tgt == "dVPD" else "no rows"),
                }
                continue
            # The LAI-masked view carries NaN features; the HybridQuantileModel's Ridge
            # backbone cannot accept NaN, so only the NaN-native pure_xgb is scored there.
            view_models = ({"pure_xgb": QuantileModel}
                           if view_name == "secondary_lai_masked_all_sites"
                           and not sub["canopy_complete"].all() else models)
            blk = _score_one(train, sub, tgt, feats, Xtr_v, groups, view_models)
            if view_models is not models:
                blk["hybrid"] = {"skipped": "HybridQuantileModel Ridge backbone rejects "
                                            "NaN (masked lai/fapar); only pure_xgb scored"}
            out[tgt][view_name] = blk

    os.makedirs(os.path.dirname(METRICS), exist_ok=True)
    with open(METRICS, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"-> {METRICS}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["freeze", "score"], required=True)
    a = ap.parse_args()
    stage_freeze() if a.stage == "freeze" else stage_score()
