"""FEW-SHOT CONFORMAL RECALIBRATION on real Tamil Nadu data (ADR-014 x ADR-016).

Extends the ADR-014 few-shot conformal result -- which was demonstrated on
*held-out training climates* (`scripts/mondrian_conformal.py`) -- to REAL local
data near the deployment site: SoilTemp/MDB deposit
`SoilTemp2.0_1.0_RajasekaranMurugan`, "Vishar_restoration site", site TN01,
12.8202 N / 79.6434 E, Tamil Nadu savanna, ~268 km from Anaikadu.

The question: Tamil Nadu is out-of-climate relative to training (humid-tropical
Borneo + Mediterranean Spain), so a cold score should reproduce the ADR-012
cross-climate failure. Do ~5-25 genuinely local calibration points restore
conformal interval coverage toward nominal?

Two stages, run separately and IN THIS ORDER, so the test set is built blind:

    uv run python scripts/run_murugan_fewshot.py --stage freeze   # needs Earth Engine
    uv run python scripts/run_murugan_fewshot.py --stage score    # offline, ONCE

  freeze -> data/processed/murugan_monthly_test.parquet  (PRIMARY, gitignored)
            data/processed/murugan_daily_test.parquet    (SECONDARY, gitignored)
  score  -> reports/murugan_fewshot_metrics.json         (mirrors mondrian_metrics.json)

Conventions replicated EXACTLY from the training pipeline (do not "improve" them
here -- comparability is the whole point):
  * labels  : scripts/build_safe_labels.py + scripts/build_lajarda_labels.py
              sub-daily -> daily (max / mean) -> monthly mean of dailies,
              months with >= 5 logged days only, date stamped YYYY-MM-15.
  * ambient : scripts/build_real_dataset.py -- ERA5 *atmospheric* (free-air,
              ~31 km), NOT ERA5-Land (canopy-coupled, ADR-006).
              CAVEAT, see AMBIENT NOTE below: GEE's `ECMWF/ERA5/DAILY` stops at
              2020-07-09 and this deposit is 2022, so the identical fields are
              rebuilt from `ECMWF/ERA5/HOURLY` on the ERA5/DAILY grid registration
              and verified to reproduce ERA5/DAILY to <1e-3 K on overlap months.
  * features: ETH canopy height + MODIS LAI/FPAR/NDVI + Copernicus DEM/slope/TWI
              + SoilGrids clay/soc, same bands, scalings and reducer. MODIS window
              = the observation period's calendar year (the rule the training build
              used for SAFE 2011-2013 and the cocoa run used for 2013-2015).
  * offsets : src/agroforestry/data/load.py convention --
              dT_max = sub_t_max - amb_t_max, dT_mean = sub_t_mean - amb_t_mean.

NO dVPD. This deposit contains ZERO relative-humidity rows, so `dVPD` cannot be
computed. Note that `build_real_dataset.py` falls back to `sub_rh = amb_rh` when
sub-canopy RH is missing, which would silently manufacture a temperature-only
pseudo-VPD; that fallback is deliberately NOT used here. dVPD is simply absent.

SENSOR: the deposit is a single TOMST TMS-4 with T1 = -15 cm (soil), T2 = 0 cm
(surface), T3 = +10 cm (air). Only T3 is an above-ground air sensor, so T3 is the
only defensible analogue of the training labels (SAFE ~15 cm, La Jarda ~30 cm) and
is pre-committed here. T3 is recorded as UNSHIELDED (`Sensor_shielding = NO`).

ADR-017 screen: PASSED (site 94.3 m vs ~31 km ERA5 box mean 92.3 m, -2.0 m, across
77.1 m relief). The orographic failure that invalidated the cocoa run does not apply.
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

from agroforestry.config import RAW_FEATURES, GROUP_COL
from agroforestry.features import engineer
from agroforestry.models import QuantileModel, HybridQuantileModel
from agroforestry.validation import _metrics

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "data", "raw", "soiltemp_mdb_data")
TS_PARQUET = os.path.join(RAW, "SoilTemp xlsx.parquet")
META_XLSX = os.path.join(RAW, "Metadata people SoilTemp  xlsx.xlsx")
TRAIN_PARQUET = os.path.join(ROOT, "data", "processed", "labelled_offsets.parquet")
TRAIN_SITES = os.path.join(ROOT, "data", "processed", "all_label_sites.csv")
FROZEN_M = os.path.join(ROOT, "data", "processed", "murugan_monthly_test.parquet")
FROZEN_D = os.path.join(ROOT, "data", "processed", "murugan_daily_test.parquet")
MANIFEST = os.path.join(ROOT, "data", "processed", "murugan_test_manifest.json")
METRICS = os.path.join(ROOT, "reports", "murugan_fewshot_metrics.json")

DATA_SOURCE = "SoilTemp2.0_1.0_RajasekaranMurugan"
AIR_SENSOR_CODE = "T3"          # +10 cm, the only above-ground sensor (pre-committed)
EE_PROJECT = "microclimate-crop-design-sys"
DEDUP_KM = 1.0
MIN_DAYS_PER_MONTH = 5          # identical to the SAFE / La Jarda / cocoa builders
# Sentinel screen: MDB QC found Murugan values up to 34,130 C. Plausible near-surface
# air/soil temperatures anywhere on Earth sit well inside this window.
PLAUSIBLE_C = (-40.0, 65.0)
ANAIKADU = (10.4019, 79.3545)

# Scored targets. dVPD is impossible (no RH in the deposit) -- see module docstring.
SCORED_TARGETS = ["dT_max", "dT_mean"]

# Few-shot sweep (the DESIGNED experiment, per ADR-014 / mondrian_conformal.py).
KS = [0, 5, 10, 25]
N_DRAWS = 50                    # repeated random calibration draws, seeds 0..N-1
TARGET_COV = 0.8                # nominal = QUANTILES[-1] - QUANTILES[0]

ERA_BANDS = ["mean_2m_air_temperature", "maximum_2m_air_temperature",
             "minimum_2m_air_temperature", "dewpoint_2m_temperature",
             "u_component_of_wind_10m", "v_component_of_wind_10m",
             "total_precipitation"]


# --------------------------------------------------------------------------
# shared helpers (verbatim from scripts/build_real_dataset.py)
# --------------------------------------------------------------------------
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

    AMBIENT NOTE. GEE hosts ERA5 atmospheric on two grids with a HALF-CELL offset:
      ECMWF/ERA5/DAILY  transform origin (-180   , 90   )  [1979-01-02 .. 2020-07-09]
      ECMWF/ERA5/HOURLY transform origin (-180.125, 90.125) [1940 .. present]
    The training set (SAFE 2011-13, La Jarda 2004-06) used ERA5/DAILY, which is not
    available for this 2022 deposit. Sampling ERA5/HOURLY at the *site* would silently
    change the ~31 km reference cell (verified: up to 3 C difference at a coastal
    training site). Sampling ERA5/HOURLY at the ERA5/DAILY pixel's NW node reproduces
    the ERA5/DAILY value to <1e-3 K -- verified in `_verify_ambient_equivalence()` and
    recorded in the manifest. This keeps the ADR-006 ambient convention intact.
    """
    lon_w = math.floor((lon + 180.0) / 0.25) * 0.25 - 180.0
    lat_n = 90.0 - math.floor((90.0 - lat) / 0.25) * 0.25
    return lat_n, lon_w


# --------------------------------------------------------------------------
# STAGE 1 -- freeze (blind to performance)
# --------------------------------------------------------------------------
def read_metadata() -> pd.DataFrame:
    md = pd.read_excel(META_XLSX, sheet_name="metadata")
    md = md[md["Data_source"] == DATA_SOURCE]
    keep = ["Site_id", "Latitude", "Longitude", "Elevation", "Habitat_type",
            "Sensor_code", "Sensor_height", "Sensor_shielding",
            "Microclimate_measurement", "Raw_data_identifier", "Temporal_resolution",
            "Timezone", "Time_difference", "Licence",
            "Start_date_year", "Start_date_month", "Start_date_day",
            "End_date_year", "End_date_month", "End_date_day"]
    return md[keep].reset_index(drop=True)


def build_labels(meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Long-format time series -> daily -> monthly, SAFE/La Jarda convention."""
    ts = pd.read_parquet(TS_PARQUET)
    ts = ts[ts["Data_source"] == DATA_SOURCE].copy()
    prov = {"rows_in_deposit": int(len(ts))}

    for c in ("Year", "Month", "Day"):
        ts[c] = pd.to_numeric(ts[c], errors="coerce")
    ts["val"] = pd.to_numeric(ts["clim_ts_values"], errors="coerce")

    temp_ids = set(meta.loc[meta["Microclimate_measurement"].astype(str)
                            .str.lower().eq("temperature"), "Raw_data_identifier"])
    temps = ts[ts["Raw data identifier"].isin(temp_ids)].copy()
    prov["temperature_rows"] = int(len(temps))

    # --- sentinel screen (MDB QC: values up to 34,130 C in this deposit) ---
    bad = ~temps["val"].between(*PLAUSIBLE_C) | temps["val"].isna()
    prov["sentinel_screen"] = {
        "plausible_window_C": list(PLAUSIBLE_C),
        "rows_dropped": int(bad.sum()),
        "dropped_detail": [
            {"sensor": r["Raw data identifier"],
             "date": f"{int(r.Year):04d}-{int(r.Month):02d}-{int(r.Day):02d}",
             "time": r["Time (24h)"], "value": float(r["val"])}
            for _, r in temps[bad].iterrows()],
    }
    temps = temps[~bad].copy()

    air_id = meta.loc[meta["Sensor_code"] == AIR_SENSOR_CODE,
                      "Raw_data_identifier"].iloc[0]
    air = temps[temps["Raw data identifier"] == air_id].copy()
    prov["air_sensor"] = {
        "sensor_code": AIR_SENSOR_CODE, "raw_data_identifier": str(air_id),
        "height_cm": float(meta.loc[meta["Sensor_code"] == AIR_SENSOR_CODE,
                                    "Sensor_height"].iloc[0]),
        "shielding": str(meta.loc[meta["Sensor_code"] == AIR_SENSOR_CODE,
                                  "Sensor_shielding"].iloc[0]),
        "rows_after_screen": int(len(air)),
    }

    air["hour"] = air["Time (24h)"].astype(str).str.slice(0, 2).astype(int)
    air["d"] = pd.to_datetime(dict(year=air.Year, month=air.Month, day=air.Day))

    # TIME-ZONE DIAGNOSTIC (reported, not applied). Metadata declares Timezone=UTC,
    # Time_difference=0. At 79.64 E, solar noon is ~06:41 UTC, so a genuinely-UTC
    # series would peak ~08-10 UTC. The observed peak hour tells us what the stamps
    # really are. Aggregation uses the stamped calendar day either way -- the same
    # thing the SAFE/La Jarda builders do with their loggers' own stamps.
    by_hour = air.groupby("hour")["val"].mean()
    prov["timezone_diagnostic"] = {
        "metadata_timezone": str(meta["Timezone"].iloc[0]),
        "metadata_time_difference": float(meta["Time_difference"].iloc[0]),
        "mean_T_by_stamp_hour": {int(h): round(float(v), 2) for h, v in by_hour.items()},
        "peak_stamp_hour": int(by_hour.idxmax()),
        "min_stamp_hour": int(by_hour.idxmin()),
        "expected_peak_hour_if_UTC": "08-10 (solar noon 06:41 UTC at 79.64 E)",
        "expected_peak_hour_if_IST": "13-14",
        "treatment": "stamped calendar day used as-is (no shift applied)",
    }

    # --- sub-daily -> daily (daily max, daily mean) ---
    daily = (air.groupby("d")
                .agg(sub_t_max=("val", "max"), sub_t_mean=("val", "mean"),
                     n_obs=("val", "size"))
                .reset_index())
    daily["y"] = daily["d"].dt.year
    daily["m"] = daily["d"].dt.month

    # --- daily -> monthly (monthly mean of dailies, >= 5 logged days) ---
    monthly = (daily.groupby(["y", "m"])
                    .agg(sub_t_max=("sub_t_max", "mean"),
                         sub_t_mean=("sub_t_mean", "mean"),
                         n_days=("d", "count"))
                    .reset_index())
    prov["months_before_min_days_rule"] = int(len(monthly))
    monthly = monthly[monthly.n_days >= MIN_DAYS_PER_MONTH].copy()

    site = meta.iloc[0]
    for frame in (monthly, daily):
        frame["site_id"] = f"MUR_{site['Site_id']}"
        frame["lat"] = float(site["Latitude"])
        frame["lon"] = float(site["Longitude"])
    monthly["date"] = monthly.apply(lambda r: f"{int(r.y):04d}-{int(r.m):02d}-15", axis=1)
    monthly["ym"] = monthly.apply(lambda r: f"{int(r.y):04d}-{int(r.m):02d}", axis=1)
    daily["date"] = daily["d"].dt.strftime("%Y-%m-%d")
    daily["ym"] = daily["d"].dt.strftime("%Y-%m")

    prov["declared_deployment"] = (
        f"{int(site.Start_date_year)}-{int(site.Start_date_month):02d}-{int(site.Start_date_day):02d}"
        f" .. {int(site.End_date_year)}-{int(site.End_date_month):02d}-{int(site.End_date_day):02d}")
    prov["delivered_period"] = [str(daily["date"].min()), str(daily["date"].max())]
    prov["delivered_days"] = int(len(daily))
    prov["delivered_months"] = int(daily["ym"].nunique())
    prov["km_from_anaikadu"] = round(float(haversine_km(
        float(site["Latitude"]), float(site["Longitude"]), *ANAIKADU)), 1)
    return monthly, daily, prov


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
    """Prove the HOURLY-rebuild reproduces ERA5/DAILY on months where BOTH exist."""
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


def fetch_features(lat, lon, months, modis_window) -> dict:
    """Same assets / bands / scalings / reducer as scripts/build_real_dataset.py.
    Raises on any failure -- features are never approximated or substituted."""
    import ee
    ee.Initialize(project=EE_PROJECT)
    site_pt = ee.Geometry.Point([lon, lat])
    node_lat, node_lon = era5_daily_grid_node(lat, lon)
    node_pt = ee.Geometry.Point([node_lon, node_lat])
    fc = ee.FeatureCollection([ee.Feature(site_pt, {"site_id": "MUR"})])

    # --- static: canopy / terrain / soil ---
    dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic().rename("elevation")
    slope = ee.Terrain.slope(dem).rename("slope")
    modveg = (ee.ImageCollection("MODIS/061/MOD15A2H")
              .filterDate(*modis_window).select(["Lai_500m", "Fpar_500m"]).mean())
    static = (ee.Image("users/nlang/ETH_GlobalCanopyHeight_2020_10m_v1").rename("canopy_height")
              .addBands(dem).addBands(slope)
              .addBands(ee.Image("projects/soilgrids-isric/clay_mean")
                        .select("clay_0-5cm_mean").rename("clay"))
              .addBands(ee.Image("projects/soilgrids-isric/soc_mean")
                        .select("soc_0-5cm_mean").rename("soc"))
              .addBands(modveg.select("Lai_500m").multiply(0.1).rename("lai"))
              .addBands(modveg.select("Fpar_500m").multiply(0.01).rename("fapar"))
              .addBands(ee.ImageCollection("MODIS/061/MOD13Q1")
                        .filterDate(*modis_window)
                        .select("NDVI").mean().multiply(0.0001).rename("ndvi")))
    print("fetching static features ...")
    stat = static.reduceRegions(fc, ee.Reducer.mean(), 250).getInfo()["features"][0]["properties"]

    print("verifying ERA5 HOURLY-rebuild == ERA5/DAILY on overlap months ...")
    equiv = _verify_ambient_equivalence(ee, node_pt, site_pt)
    worst = max(abs(v) for d in equiv.values()
                for k, v in d.items() if k.endswith("air_temperature"))
    print(f"  max |diff| on the temperature bands: {worst:.2e} K")

    # --- ambient: monthly (PRIMARY) and daily (SECONDARY) ---
    era_month, era_day = {}, {}
    for ym in months:
        y, m = map(int, ym.split("-"))
        start = ee.Date.fromYMD(y, m, 1)
        end = start.advance(1, "month")
        dcol = _ee_daily_from_hourly(ee, start, end)
        sol_col = (ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterDate(start, end)
                   .select("surface_solar_radiation_downwards_sum"))

        era_month[ym] = dcol.mean().reduceRegion(
            ee.Reducer.mean(), node_pt, 1000).getInfo()
        era_month[ym]["solar_jm2"] = sol_col.mean().reduceRegion(
            ee.Reducer.mean(), site_pt, 1000).getInfo().get(
                "surface_solar_radiation_downwards_sum")

        daily_fc = dcol.map(lambda im: ee.Feature(
            None, im.reduceRegion(ee.Reducer.mean(), node_pt, 1000)).set("d", im.get("d")))
        for f in daily_fc.getInfo()["features"]:
            era_day[f["properties"]["d"]] = dict(f["properties"])
        sol_fc = sol_col.map(lambda im: ee.Feature(
            None, im.reduceRegion(ee.Reducer.mean(), site_pt, 1000))
            .set("d", im.date().format("YYYY-MM-dd")))
        for f in sol_fc.getInfo()["features"]:
            d = f["properties"]["d"]
            if d in era_day:
                era_day[d]["solar_jm2"] = f["properties"].get(
                    "surface_solar_radiation_downwards_sum")
        print(f"  ERA5 {ym}: monthly + {len(era_day)} daily")

    return {"static": stat, "era_month": era_month, "era_day": era_day,
            "equivalence_check": equiv,
            "era5_daily_grid_node": [node_lat, node_lon]}


def _macro_row(e, stat, slope_deg, twi):
    amb_tmean = e["mean_2m_air_temperature"] - 273.15
    amb_tmax = e["maximum_2m_air_temperature"] - 273.15
    amb_tmin = e["minimum_2m_air_temperature"] - 273.15
    amb_rh = rh_from(amb_tmean, e["dewpoint_2m_temperature"] - 273.15)
    return {
        "t_mean": amb_tmean, "t_max": amb_tmax, "t_min": amb_tmin, "rh": amb_rh,
        "wind": math.hypot(e["u_component_of_wind_10m"], e["v_component_of_wind_10m"]),
        "solar": (e.get("solar_jm2") or 0.0) / 1e6,
        "rainfall": max(0.0, e["total_precipitation"]) * 1000 * 365,
        "lai": stat.get("lai"), "canopy_height": stat.get("canopy_height"),
        "ndvi": stat.get("ndvi"), "fapar": stat.get("fapar"),
        "elevation": stat.get("elevation"), "slope": slope_deg, "twi": twi,
        "soc": stat.get("soc"), "clay": stat.get("clay"),
        "amb_t_max": amb_tmax, "amb_t_mean": amb_tmean, "amb_rh": amb_rh,
    }


def stage_freeze() -> None:
    meta = read_metadata()
    print(meta.to_string(index=False))
    monthly, daily, prov = build_labels(meta)

    print(f"\nPRIMARY (training monthly convention): {len(monthly)} label rows, "
          f"{monthly.site_id.nunique()} site(s), months {sorted(monthly.ym)}")
    print(f"SECONDARY (daily, NOT the training convention): {len(daily)} rows")
    print("sentinel screen:", json.dumps(prov["sentinel_screen"], indent=2))

    dedup, monthly = dedup_report(monthly)
    _, daily = dedup_report(daily)
    print("de-dup vs training sites:", json.dumps(dedup))
    if monthly.empty:
        raise SystemExit("all external sites de-duplicated away -- nothing to score")

    lat, lon = float(monthly.lat.iloc[0]), float(monthly.lon.iloc[0])
    obs_year = int(monthly.y.iloc[0])
    modis_window = (f"{obs_year}-01-01", f"{obs_year + 1}-01-01")
    try:
        ee_out = fetch_features(lat, lon, sorted(monthly.ym.unique()), modis_window)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            "BLOCKER: Earth Engine feature fetch failed -- features must NOT be "
            f"approximated or substituted (ADR-016 comparability). Cause: {exc!r}")

    stat = ee_out["static"]
    slope_deg = stat.get("slope") or 0.0
    twi = math.log(1.0 / (math.tan(math.radians(slope_deg)) + 0.01))

    rows_m = []
    for r in monthly.itertuples():
        e = ee_out["era_month"].get(r.ym)
        if not e or e.get("mean_2m_air_temperature") is None:
            continue
        row = _macro_row(e, stat, slope_deg, twi)
        row.update({"site_id": r.site_id, "date": r.date, "ym": r.ym,
                    "lat": r.lat, "lon": r.lon, "n_days": r.n_days,
                    "sub_t_max": r.sub_t_max, "sub_t_mean": r.sub_t_mean,
                    "dT_max": r.sub_t_max - row["amb_t_max"],
                    "dT_mean": r.sub_t_mean - row["amb_t_mean"]})
        rows_m.append(row)

    rows_d = []
    for r in daily.itertuples():
        e = ee_out["era_day"].get(r.date)
        if not e or e.get("mean_2m_air_temperature") is None:
            continue
        row = _macro_row(e, stat, slope_deg, twi)
        row.update({"site_id": r.site_id, "date": r.date, "ym": r.ym,
                    "lat": r.lat, "lon": r.lon, "n_obs": r.n_obs,
                    "sub_t_max": r.sub_t_max, "sub_t_mean": r.sub_t_mean,
                    "dT_max": r.sub_t_max - row["amb_t_max"],
                    "dT_mean": r.sub_t_mean - row["amb_t_mean"]})
        rows_d.append(row)

    dfm = pd.DataFrame(rows_m).dropna(subset=RAW_FEATURES + SCORED_TARGETS)
    dfd = pd.DataFrame(rows_d).dropna(subset=RAW_FEATURES + SCORED_TARGETS)
    print(f"PRIMARY rows after feature/target NaN drop: {len(dfm)}")
    print(f"SECONDARY rows after feature/target NaN drop: {len(dfd)}")

    os.makedirs(os.path.dirname(FROZEN_M), exist_ok=True)
    dfm.to_parquet(FROZEN_M, index=False)
    dfd.to_parquet(FROZEN_D, index=False)

    manifest = {
        "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "data_source": DATA_SOURCE,
        "site": {"site_id": str(monthly.site_id.iloc[0]), "lat": lat, "lon": lon,
                 "metadata_elevation_m": float(meta["Elevation"].iloc[0]),
                 "dem_elevation_m": stat.get("elevation"),
                 "habitat_type_code": float(meta["Habitat_type"].iloc[0]),
                 "licence": str(meta["Licence"].iloc[0])},
        "provenance": prov,
        "dedup": dedup,
        "primary": {"convention": "training monthly (SAFE/La Jarda): daily max & mean "
                                  "-> monthly mean of dailies, >=5 logged days, "
                                  "ambient = ERA5 atmospheric monthly (ADR-006)",
                    "rows": int(len(dfm)), "sites": int(dfm.site_id.nunique()),
                    "months": sorted(dfm.ym.unique().tolist()) if len(dfm) else []},
        "secondary": {"convention": "DAILY aggregation -- NOT the training convention; "
                                    "labels are daily sub-canopy vs daily ERA5, so they "
                                    "carry more variance than the monthly training labels",
                      "rows": int(len(dfd)),
                      "period": [str(dfd.date.min()), str(dfd.date.max())] if len(dfd) else []},
        "targets": {"scored": SCORED_TARGETS,
                    "dVPD": "NOT COMPUTED -- deposit has zero relative-humidity rows"},
        "modis_window": list(modis_window),
        "era5_daily_grid_node": ee_out["era5_daily_grid_node"],
        "ambient_equivalence_check": ee_out["equivalence_check"],
        "static_features": {k: v for k, v in stat.items() if k != "site_id"},
    }
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"-> {FROZEN_M}\n-> {FROZEN_D}\n-> {MANIFEST}")
    print(json.dumps(manifest, indent=2, default=str))


# --------------------------------------------------------------------------
# STAGE 2 -- score ONCE
# --------------------------------------------------------------------------
def _cold_block(qm, Xte_v, yte, ytr, feats, extra=None):
    pred = qm.predict(Xte_v)
    base = np.full(len(yte), float(np.mean(ytr)))
    mae, rmse, cov, width, mae_base, r2 = _metrics(yte, pred, base)
    res = {
        "n_test": int(len(yte)),
        "MAE": mae, "RMSE": rmse,
        "interval_coverage": cov, "interval_nominal": TARGET_COV,
        "interval_width": width,
        "baseline_MAE": mae_base,
        "skill_vs_baseline": float(1.0 - mae / mae_base) if mae_base > 0 else float("nan"),
        "R2_oos": r2,
        "obs_mean": float(np.mean(yte)), "obs_std": float(np.std(yte)),
        "pred_mean": float(np.mean(pred["median"])), "pred_std": float(np.std(pred["median"])),
        "bias_pred_minus_obs": float(np.mean(pred["median"] - yte)),
    }
    if extra:
        res.update(extra)
    return res, pred


def _ood_block(qm, Xte_v, Xtr_v, feats):
    ood = qm.ood_score(Xte_v)
    return {
        "definition": "fraction of engineered features outside the training min/max "
                      "box (models.QuantileModel.ood_score)",
        "flag_threshold": 0.15,
        "external_mean": float(ood.mean()),
        "external_min": float(ood.min()), "external_max": float(ood.max()),
        "external_frac_flagged": float((ood > 0.15).mean()),
        "train_mean": float(qm.ood_score(Xtr_v).mean()),
        "features_out_of_range": sorted(
            {feats[j] for j in np.where(
                ((Xte_v < qm.feat_lo) | (Xte_v > qm.feat_hi)).any(axis=0))[0]}),
    }


def _fewshot_sweep(qm, Xte_v, yte) -> dict:
    """ADR-014 / mondrian_conformal.py method: recalibrate the conformal width on k
    points drawn from the target regime, evaluate on the remaining points.
    k = 0 reproduces the cold (LOCO-style) collapse. Repeated draws, seeds 0..N-1."""
    lo_raw = qm.models[qm.quantiles[0]].predict(Xte_v)
    hi_raw = qm.models[qm.quantiles[-1]].predict(Xte_v)
    base_off = qm.conformal_offset
    n = len(yte)
    per_k = {}
    for k in KS:
        if k >= n:
            per_k[k] = {"skipped": f"k={k} >= n_test={n}"}
            continue
        covs, widths = [], []
        draws = 1 if k == 0 else N_DRAWS
        for seed in range(draws):
            rng = np.random.default_rng(seed)
            if k == 0:
                off, ev = base_off, np.arange(n)
            else:
                cal = rng.choice(n, size=k, replace=False)
                scores = np.maximum(lo_raw[cal] - yte[cal], yte[cal] - hi_raw[cal])
                off = float(np.quantile(scores, TARGET_COV, method="higher"))
                ev = np.setdiff1d(np.arange(n), cal)
            lo, hi = lo_raw[ev] - off, hi_raw[ev] + off
            covs.append(float(np.mean((yte[ev] >= lo) & (yte[ev] <= hi))))
            widths.append(float(np.mean(hi - lo)))
        per_k[k] = {
            "n_eval": int(n - k), "n_draws": draws,
            "coverage_mean": round(float(np.mean(covs)), 3),
            "coverage_sd": round(float(np.std(covs)), 3),
            "coverage_p10": round(float(np.percentile(covs, 10)), 3),
            "coverage_p90": round(float(np.percentile(covs, 90)), 3),
            "width_mean": round(float(np.mean(widths)), 3),
            "width_sd": round(float(np.std(widths)), 3),
            "width_p10": round(float(np.percentile(widths, 10)), 3),
            "width_p90": round(float(np.percentile(widths, 90)), 3),
        }
    return per_k


def stage_score() -> None:
    train = pd.read_parquet(TRAIN_PARQUET)
    dfm = pd.read_parquet(FROZEN_M)
    dfd = pd.read_parquet(FROZEN_D)
    manifest = json.load(open(MANIFEST))

    Xtr, feats = engineer(train)
    Xtr_v = Xtr[feats].values
    groups = train[GROUP_COL].astype(str).values

    sets = {"primary_monthly": dfm, "secondary_daily": dfd}
    out = {
        "_meta": {
            "scored_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "experiment": "few-shot conformal recalibration on real Tamil Nadu "
                          "savanna data (ADR-014 method, ADR-016 discipline)",
            "data_source": DATA_SOURCE,
            "train_rows": int(len(train)), "train_sites": int(pd.Series(groups).nunique()),
            "scored_targets": SCORED_TARGETS,
            "dVPD": "NOT COMPUTED -- the deposit has zero relative-humidity rows",
            "ks": KS, "n_draws": N_DRAWS, "target_coverage": TARGET_COV,
            "protocol": "model fit on ALL training rows with group-aware conformal "
                        "calibration, then scored once; few-shot sweep recalibrates "
                        "ONLY the conformal width on k local points (no retraining)",
            "baseline": "training-mean offset (identical to validation.py)",
            "manifest": os.path.relpath(MANIFEST, ROOT),
            "sufficiency_verdict": None,   # filled below
        },
        "provenance": manifest["provenance"],
        "dedup": manifest["dedup"],
        "site": manifest["site"],
        "ambient_equivalence_check": manifest["ambient_equivalence_check"],
    }

    # --- pre-committed sufficiency test (stated before any metric is read) ---
    n_primary = len(dfm)
    min_useful = max(KS) + 10
    verdict = {
        "primary_rows": int(n_primary),
        "secondary_rows": int(len(dfd)),
        "requirement": f"a meaningful few-shot curve needs n_test >= max(k)+10 = "
                       f"{min_useful} INDEPENDENT label rows",
        "primary_sufficient": bool(n_primary >= min_useful),
        "secondary_sufficient_by_count": bool(len(dfd) >= min_useful),
        "secondary_independent": False,
        "note": "the secondary daily rows are 31 consecutive days at ONE site in ONE "
                "month; they are strongly autocorrelated and share one feature vector, "
                "so they are not independent draws from the target regime",
    }
    out["_meta"]["sufficiency_verdict"] = verdict
    print(json.dumps(verdict, indent=2))

    for sname, test in sets.items():
        if test.empty:
            out[sname] = {"n_test": 0, "note": "empty"}
            continue
        Xte, _ = engineer(test)
        Xte_v = Xte[feats].values
        block = {"n_test": int(len(test)), "n_sites": int(test.site_id.nunique()),
                 "period": [str(test.date.min()), str(test.date.max())],
                 "n_unique_feature_rows": int(Xte.drop_duplicates().shape[0])}
        for tgt in SCORED_TARGETS:
            ytr, yte = train[tgt].values, test[tgt].values
            block[tgt] = {}
            for name, factory in {"pure_xgb": QuantileModel,
                                  "hybrid": HybridQuantileModel}.items():
                t0 = time.time()
                qm = factory().fit(Xtr_v, ytr, feature_names=feats, groups=groups)
                res, pred = _cold_block(qm, Xte_v, yte, ytr, feats)
                res["seconds"] = round(time.time() - t0, 1)
                if name == "pure_xgb":
                    res["ood"] = _ood_block(qm, Xte_v, Xtr_v, feats)
                    block[tgt]["fewshot_by_k"] = _fewshot_sweep(qm, Xte_v, yte)
                if len(test) <= 5:
                    res["per_row"] = [
                        {"date": d, "obs": float(o), "pred": float(p),
                         "lower": float(l), "upper": float(u),
                         "in_interval": bool(l <= o <= u)}
                        for d, o, p, l, u in zip(test.date, yte, pred["median"],
                                                 pred["lower"], pred["upper"])]
                    res["metrics_are_not_estimates"] = (
                        f"n={len(test)} -- MAE/RMSE/coverage/skill here are single "
                        "observations, not statistical estimates; do not report them "
                        "as validation metrics")
                block[tgt][name] = res
                print(f"[{sname}] {tgt:8s} {name:9s} n={len(test):3d} MAE {res['MAE']:.3f} "
                      f"RMSE {res['RMSE']:.3f} skill {res['skill_vs_baseline']*100:7.1f}% "
                      f"cov {res['interval_coverage']:.2f}")
            fs = block[tgt].get("fewshot_by_k", {})
            for k in KS:
                v = fs.get(k) or fs.get(str(k))
                if v and "coverage_mean" in v:
                    print(f"    k={k:3d}  cov {v['coverage_mean']:.2f} +/- {v['coverage_sd']:.2f} "
                          f"  width {v['width_mean']:.2f} +/- {v['width_sd']:.2f}  "
                          f"(n_eval {v['n_eval']}, {v['n_draws']} draws)")
        out[sname] = block

    os.makedirs(os.path.dirname(METRICS), exist_ok=True)
    with open(METRICS, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"-> {METRICS}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["freeze", "score"], required=True)
    a = ap.parse_args()
    stage_freeze() if a.stage == "freeze" else stage_score()
