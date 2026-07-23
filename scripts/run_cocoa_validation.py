"""FIRST EXTERNAL VALIDATION — cocoa agroforestry, Alto Beni, Bolivia (ADR-016).

Independent, pre-registered, within-climate (humid-tropical) external test of the
trained canopy -> microclimate-offset model. Scores the model that
`scripts/run_validation.py` validates internally (LOSO/LOCO), on data it has never
seen: Niether et al. (Zenodo 1185579), Sara Ana field station, Alto Beni, Bolivia.

Two stages, run separately and IN THIS ORDER, so the test set is built blind:

    uv run python scripts/run_cocoa_validation.py --stage freeze   # needs Earth Engine
    uv run python scripts/run_cocoa_validation.py --stage score    # offline, ONCE

  freeze -> data/processed/cocoa_external_test.parquet   (gitignored)
  score  -> reports/cocoa_external_metrics.json          (mirrors loso_metrics.json)

The pre-registration rule (docs/external_validation_datasets.md, ADR-016) is that
the frozen set is built without looking at model performance, is de-duplicated by
site coordinates against data/processed/all_label_sites.csv, and is scored exactly
once. Nothing here may be re-tuned after the numbers are seen.

Conventions replicated EXACTLY from the training pipeline (do not "improve" them
here — comparability is the whole point):
  * labels  : scripts/build_safe_labels.py + scripts/build_lajarda_labels.py
              sub-daily -> daily (max / mean / mean-RH) -> monthly mean of dailies,
              months with >= 5 logged days only, date stamped YYYY-MM-15.
  * ambient : scripts/build_real_dataset.py — ERA5 *atmospheric* ECMWF/ERA5/DAILY
              (free-air, ~31 km), NOT ERA5-Land (canopy-coupled, ADR-006). Solar
              only from ERA5-Land (radiation is top-of-canopy).
  * features: ETH canopy height + MODIS LAI/FPAR/NDVI + Copernicus DEM/slope/TWI
              + SoilGrids clay/soc, same bands, scalings and reducer.
  * offsets : src/agroforestry/data/load.py convention —
              dT_max = sub_t_max - amb_t_max, dT_mean = sub_t_mean - amb_t_mean,
              dVPD = es(sub_t_max)*(1-sub_rh/100) - es(amb_t_max)*(1-amb_rh/100).
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
RAW = os.path.join(ROOT, "data", "raw", "cocoa_altobeni",
                   "Microclimate in cocoa production systems Data")
PLOTS_CSV = os.path.join(RAW, "ClimatePlots1.csv")
CO13_CSV = os.path.join(RAW, "CO13m2.csv")          # in-situ canopy openness / LAI (cross-check only)
TRAIN_PARQUET = os.path.join(ROOT, "data", "processed", "labelled_offsets.parquet")
TRAIN_SITES = os.path.join(ROOT, "data", "processed", "all_label_sites.csv")
FROZEN = os.path.join(ROOT, "data", "processed", "cocoa_external_test.parquet")
METRICS = os.path.join(ROOT, "reports", "cocoa_external_metrics.json")

# Sara Ana field station, Alto Beni, Bolivia — the ONLY coordinate the dataset
# publishes (metadata PDF s.1: 380 m a.s.l., 15 deg 27' 36.60" S, 67 deg 28' 20.65" W).
# Per-plot coordinates are not distributed; PAR1.csv lat/long are truncated to whole
# degrees. All 18 experimental plots therefore share one location.
SITE_LAT = -(15 + 27 / 60 + 36.60 / 3600)     # -15.460167
SITE_LON = -(67 + 28 / 60 + 20.65 / 3600)     # -67.472403
EE_PROJECT = "microclimate-crop-design-sys"
DEDUP_KM = 1.0
MIN_DAYS_PER_MONTH = 5                        # identical to the SAFE / La Jarda builders


# --------------------------------------------------------------------------
# shared helpers (verbatim from scripts/build_real_dataset.py)
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


# --------------------------------------------------------------------------
# STAGE 1 — freeze the external test set (blind to performance)
# --------------------------------------------------------------------------
def build_labels() -> pd.DataFrame:
    """ClimatePlots1.csv (hourly logger T/RH per plot) -> plot-month sub-canopy stats.

    NOTE on dates: the file carries BOTH a `date` string and year/month/day columns.
    The `date` string is defective — for June-2014 and November-2014 it repeats the
    2013 year (12,960 + 12,960 rows), which collides those months onto the 2013
    record and produces 25,938 duplicate plot-timestamps. The year/month/day columns
    are mutually consistent and yield a clean 2013-03..2014-12 calendar, so they are
    authoritative here.
    """
    df = pd.read_csv(PLOTS_CSV)
    month_num = pd.to_datetime(df["month"], format="%B").dt.month
    df["d"] = pd.to_datetime(dict(year=df["year"], month=month_num, day=df["day"]))

    # sub-daily -> daily (SAFE/La Jarda convention: daily max, daily mean, daily mean RH)
    daily = (df.dropna(subset=["T"])
               .groupby(["plot", "treatment", "system", "div", "d"])
               .agg(tmax=("T", "max"), tmean=("T", "mean"), rh=("RH", "mean"))
               .reset_index())
    daily["y"] = daily["d"].dt.year
    daily["m"] = daily["d"].dt.month

    monthly = (daily.groupby(["plot", "treatment", "system", "div", "y", "m"])
                    .agg(sub_t_max=("tmax", "mean"), sub_t_mean=("tmean", "mean"),
                         sub_rh=("rh", "mean"), n_days=("d", "count"))
                    .reset_index())
    monthly = monthly[monthly.n_days >= MIN_DAYS_PER_MONTH].copy()

    monthly["site_id"] = "COC_" + monthly["plot"].astype(int).astype(str).str.zfill(2)
    monthly["lat"] = SITE_LAT
    monthly["lon"] = SITE_LON
    monthly["date"] = monthly.apply(lambda r: f"{int(r.y):04d}-{int(r.m):02d}-15", axis=1)
    monthly["ym"] = monthly.apply(lambda r: f"{int(r.y):04d}-{int(r.m):02d}", axis=1)
    return monthly


def dedup_report(labels: pd.DataFrame) -> dict:
    """ADR-016 rule 3: drop any external site within ~1 km of a TRAINING site."""
    tr = pd.read_csv(TRAIN_SITES).drop_duplicates("site_id")
    d = haversine_km(labels["lat"].values[:, None], labels["lon"].values[:, None],
                     tr["lat"].values[None, :], tr["lon"].values[None, :])
    nearest_km = d.min(axis=1)
    nearest_idx = d.argmin(axis=1)
    labels["nearest_train_km"] = nearest_km
    labels["nearest_train_site"] = tr["site_id"].values[nearest_idx]
    drop = nearest_km < DEDUP_KM
    return {
        "rule": f"drop external sites within {DEDUP_KM} km of any training site",
        "training_sites_checked": int(len(tr)),
        "external_sites_checked": int(labels["site_id"].nunique()),
        "min_distance_km": float(np.min(nearest_km)),
        "nearest_training_site": str(labels["nearest_train_site"].iloc[int(np.argmin(nearest_km))]),
        "rows_dropped": int(drop.sum()),
        "sites_dropped": int(labels.loc[drop, "site_id"].nunique()),
    }, labels.loc[~drop].copy()


def fetch_features(months: list[str]) -> tuple[dict, dict]:
    """Earth Engine features at the Sara Ana point. Same assets/bands/scalings as
    scripts/build_real_dataset.py. Raises on any failure — never substituted."""
    import ee
    ee.Initialize(project=EE_PROJECT)
    fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([SITE_LON, SITE_LAT]),
                                          {"site_id": "COC"})])

    # --- static: canopy / terrain / soil ---
    # MODIS window = the cocoa observation period (2013-2015), the same rule the
    # training build applied to its own study period (2011-2013 for SAFE).
    dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic().rename("elevation")
    slope = ee.Terrain.slope(dem).rename("slope")
    modveg = (ee.ImageCollection("MODIS/061/MOD15A2H")
              .filterDate("2013-01-01", "2015-01-01")
              .select(["Lai_500m", "Fpar_500m"]).mean())
    static = (ee.Image("users/nlang/ETH_GlobalCanopyHeight_2020_10m_v1").rename("canopy_height")
              .addBands(dem).addBands(slope)
              .addBands(ee.Image("projects/soilgrids-isric/clay_mean")
                        .select("clay_0-5cm_mean").rename("clay"))
              .addBands(ee.Image("projects/soilgrids-isric/soc_mean")
                        .select("soc_0-5cm_mean").rename("soc"))
              .addBands(modveg.select("Lai_500m").multiply(0.1).rename("lai"))
              .addBands(modveg.select("Fpar_500m").multiply(0.01).rename("fapar"))
              .addBands(ee.ImageCollection("MODIS/061/MOD13Q1")
                        .filterDate("2013-01-01", "2015-01-01")
                        .select("NDVI").mean().multiply(0.0001).rename("ndvi")))
    print("fetching static features ...")
    stat = static.reduceRegions(fc, ee.Reducer.mean(), 250).getInfo()["features"][0]["properties"]

    # --- ERA5 ATMOSPHERIC monthly ambient (ADR-006) + ERA5-Land solar ---
    era_bands = ["mean_2m_air_temperature", "maximum_2m_air_temperature",
                 "minimum_2m_air_temperature", "dewpoint_2m_temperature",
                 "u_component_of_wind_10m", "v_component_of_wind_10m", "total_precipitation"]
    era = {}
    for ym in months:
        y, m = map(int, ym.split("-"))
        start = ee.Date.fromYMD(y, m, 1)
        end = start.advance(1, "month")
        img = (ee.ImageCollection("ECMWF/ERA5/DAILY")
               .filterDate(start, end).select(era_bands).mean())
        sol = (ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterDate(start, end)
               .select("surface_solar_radiation_downwards_sum").mean().rename("solar_jm2"))
        res = img.addBands(sol).reduceRegions(fc, ee.Reducer.mean(), 1000).getInfo()
        era[ym] = res["features"][0]["properties"]
        print(f"  ERA5 {ym}: ok")
    return stat, era


def stage_freeze() -> None:
    labels = build_labels()
    print(f"label rows {len(labels)} | plots {labels.site_id.nunique()} "
          f"| months {labels.ym.nunique()} ({labels.ym.min()}..{labels.ym.max()})")

    dedup, labels = dedup_report(labels)
    print("de-dup vs training sites:", json.dumps(dedup))
    if labels.empty:
        raise SystemExit("all external sites de-duplicated away — nothing to score")

    try:
        stat, era = fetch_features(sorted(labels.ym.unique()))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            "BLOCKER: Earth Engine feature fetch failed — features must NOT be "
            f"approximated or substituted (ADR-016 comparability). Cause: {exc!r}")

    slope_deg = stat.get("slope") or 0.0
    twi = math.log(1.0 / (math.tan(math.radians(slope_deg)) + 0.01))

    rows = []
    for r in labels.itertuples():
        e = era.get(r.ym, {})
        if not e or e.get("mean_2m_air_temperature") is None:
            continue
        amb_tmean = e["mean_2m_air_temperature"] - 273.15
        amb_tmax = e["maximum_2m_air_temperature"] - 273.15
        amb_tmin = e["minimum_2m_air_temperature"] - 273.15
        amb_rh = rh_from(amb_tmean, e["dewpoint_2m_temperature"] - 273.15)
        wind = math.hypot(e["u_component_of_wind_10m"], e["v_component_of_wind_10m"])
        solar = (e.get("solar_jm2") or 0.0) / 1e6
        rainfall = max(0.0, e["total_precipitation"]) * 1000 * 365
        sub_rh = r.sub_rh if pd.notna(r.sub_rh) else amb_rh
        rows.append({
            "site_id": r.site_id,
            "t_mean": amb_tmean, "t_max": amb_tmax, "t_min": amb_tmin, "rh": amb_rh,
            "wind": wind, "solar": solar, "rainfall": rainfall,
            "lai": stat.get("lai"), "canopy_height": stat.get("canopy_height"),
            "ndvi": stat.get("ndvi"), "fapar": stat.get("fapar"),
            "elevation": stat.get("elevation"), "slope": slope_deg, "twi": twi,
            "soc": stat.get("soc"), "clay": stat.get("clay"),
            "dT_max": r.sub_t_max - amb_tmax,
            "dT_mean": r.sub_t_mean - amb_tmean,
            "dVPD": es(r.sub_t_max) * (1 - sub_rh / 100) - es(amb_tmax) * (1 - amb_rh / 100),
            # provenance / diagnostics (NOT model inputs)
            "date": r.date, "ym": r.ym, "lat": r.lat, "lon": r.lon,
            "treatment": r.treatment, "system": r.system, "div": r.div,
            "n_days": r.n_days, "sub_t_max": r.sub_t_max, "sub_t_mean": r.sub_t_mean,
            "sub_rh": sub_rh, "amb_t_max": amb_tmax, "amb_t_mean": amb_tmean,
            "amb_rh": amb_rh,
        })

    df = pd.DataFrame(rows)
    before = len(df)
    df = df.dropna(subset=RAW_FEATURES + TARGETS)
    print(f"rows: {before} -> {len(df)} after dropping feature/target-NaN")

    os.makedirs(os.path.dirname(FROZEN), exist_ok=True)
    df.to_parquet(FROZEN, index=False)
    meta = {
        "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "rows": int(len(df)), "sites": int(df.site_id.nunique()),
        "months": int(df.ym.nunique()), "period": [df.ym.min(), df.ym.max()],
        "dedup": dedup,
        "static_features": {k: v for k, v in stat.items() if k != "site_id"},
    }
    with open(FROZEN.replace(".parquet", "_manifest.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(f"-> {FROZEN}")
    print(json.dumps(meta, indent=2, default=str))
    print(df[TARGETS + ["t_max", "sub_t_max", "sub_rh"]].describe().round(3).T.to_string())


# --------------------------------------------------------------------------
# STAGE 2 — score ONCE
# --------------------------------------------------------------------------
def stage_score() -> None:
    train = pd.read_parquet(TRAIN_PARQUET)
    test = pd.read_parquet(FROZEN)
    Xtr, feats = engineer(train)
    Xte, _ = engineer(test)
    Xtr_v, Xte_v = Xtr[feats].values, Xte[feats].values
    groups = train[GROUP_COL].astype(str).values
    print(f"train rows {len(train)} sites {pd.Series(groups).nunique()} | "
          f"external rows {len(test)} sites {test.site_id.nunique()}")

    models = {"pure_xgb": QuantileModel, "hybrid": HybridQuantileModel}
    out = {
        "_meta": {
            "scored_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "test_set": os.path.relpath(FROZEN, ROOT),
            "test_rows": int(len(test)), "test_sites": int(test.site_id.nunique()),
            "test_period": [test.ym.min(), test.ym.max()],
            "train_rows": int(len(train)), "train_sites": int(pd.Series(groups).nunique()),
            "protocol": "external hold-out; model fit on ALL training rows "
                        "(group-aware conformal calibration), scored once",
            "baseline": "training-mean offset (identical to validation.py)",
        }
    }

    for tgt in TARGETS:
        ytr = train[tgt].values
        yte = test[tgt].values
        y_train_mean = np.full(len(yte), float(np.mean(ytr)))
        out[tgt] = {}
        for name, factory in models.items():
            t0 = time.time()
            qm = factory().fit(Xtr_v, ytr, feature_names=feats, groups=groups)
            pred = qm.predict(Xte_v)
            mae, rmse, cov, width, mae_base, r2 = _metrics(yte, pred, y_train_mean)
            res = {
                "n_test": int(len(yte)),
                "MAE": mae, "RMSE": rmse,
                "interval_coverage": cov, "interval_nominal": 0.80,
                "interval_width": width,
                "baseline_MAE": mae_base,
                "skill_vs_baseline": float(1.0 - mae / mae_base) if mae_base > 0 else float("nan"),
                "R2_oos": r2,
                "obs_mean": float(np.mean(yte)), "obs_std": float(np.std(yte)),
                "pred_mean": float(np.mean(pred["median"])),
                "pred_std": float(np.std(pred["median"])),
                "bias_pred_minus_obs": float(np.mean(pred["median"] - yte)),
                "seconds": round(time.time() - t0, 1),
            }
            # diagnostics from the SAME single scoring pass (no re-fitting)
            resid = pd.DataFrame({"site": test.site_id.values,
                                  "treatment": test.treatment.values,
                                  "ae": np.abs(yte - pred["median"]),
                                  "cov": ((yte >= pred["lower"]) & (yte <= pred["upper"])).astype(float)})
            res["per_treatment"] = {
                k: {"n": int(v["ae"].size), "MAE": float(v["ae"].mean()),
                    "interval_coverage": float(v["cov"].mean())}
                for k, v in resid.groupby("treatment")}
            res["per_site_MAE"] = {k: float(v["ae"].mean())
                                   for k, v in resid.groupby("site")}
            if name == "pure_xgb":
                ood = qm.ood_score(Xte_v)
                ood_tr = qm.ood_score(Xtr_v)
                res["ood"] = {
                    "definition": "fraction of engineered features outside the "
                                  "training min/max box (models.QuantileModel.ood_score)",
                    "flag_threshold": 0.15,
                    "external_mean": float(ood.mean()),
                    "external_min": float(ood.min()), "external_max": float(ood.max()),
                    "external_frac_flagged": float((ood > 0.15).mean()),
                    "train_mean": float(ood_tr.mean()),
                    "features_out_of_range": sorted(
                        {feats[j] for j in np.where(
                            ((Xte_v < qm.feat_lo) | (Xte_v > qm.feat_hi)).any(axis=0))[0]}),
                }
            out[tgt][name] = res
            print(f"[EXT] {tgt:8s} {name:9s} MAE {mae:.3f} RMSE {rmse:.3f} "
                  f"skill {res['skill_vs_baseline']*100:6.1f}% R2 {r2:.2f} cov {cov:.2f}")

    os.makedirs(os.path.dirname(METRICS), exist_ok=True)
    with open(METRICS, "w") as f:
        json.dump(out, f, indent=2)
    print(f"-> {METRICS}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["freeze", "score"], required=True)
    a = ap.parse_args()
    stage_freeze() if a.stage == "freeze" else stage_score()
