"""EXTERNAL VALIDATION — J Lelis Caatinga dry-forest deposit, Brazil (ADR-016).

Independent, pre-registered external test of the trained canopy -> microclimate
offset model on the SoilTemp/MDB deposit `JLelis` (`data/raw/.../JLelis.xlsx`):
41 declared sensor channels over 17 Caatinga dry-forest / semi-arid sites in NE
Brazil (lat -8.166..-7.365, lon -37.178..-36.281), study period 2017-2021,
EPSG 4326. Intended as an independent humid-tropical / semi-arid corroboration of
the canopy->dT_max/dT_mean mapping, with real per-site feature spread across many
sites (the thing cocoa/Murugan/Astroni could not test).

The pre-registration (docs/external_validation_datasets.md, ADR-016) designated the
**+150 cm shielded air-temperature sensor (Raw_data_identifier suffix `_T1`,
Vantage Pro2 ISS w/ radiation shield)** as the sub-canopy air reference — the only
above-ground air sensor in the deposit. dT_max / dT_mean only (no relative humidity
is recorded, so dVPD is not computable and is NOT manufactured via any amb_rh
fallback — same refusal as the Murugan/Astroni runs).

Two stages, run separately and IN THIS ORDER so the test set is built blind:

    uv run python scripts/run_jlelis_validation.py --stage freeze   # (would need Earth Engine)
    uv run python scripts/run_jlelis_validation.py --stage score    # offline, ONCE

  freeze -> data/processed/jlelis_external_test.parquet  (gitignored)
            data/processed/jlelis_test_manifest.json
  score  -> reports/jlelis_external_metrics.json         (mirrors cocoa/astroni)

Conventions that WOULD be replicated EXACTLY from the training pipeline (labels =
build_safe/lajarda; ambient = ERA5 atmospheric free-air rebuilt from ERA5/HOURLY at
the ERA5/DAILY grid node per run_murugan_fewshot/run_astroni_validation; features =
ETH canopy height + MODIS LAI/FPAR/NDVI + Copernicus DEM/slope/TWI + SoilGrids
clay/soc; offsets per src/agroforestry/data/load.py).

--------------------------------------------------------------------------------
DELIVERY-GAP BLOCKER (discovered at the freeze stage, pre-EE, pre-scoring)
--------------------------------------------------------------------------------
The `Raw time series data` sheet delivers usable values for ONLY the `_T3` sensor
(declared Sensor_height -10 cm / -6 cm = SOIL / ground-temperature probe,
"Multi-Purpose Temperature Probe"), for 17 sites, 779,678 hourly rows, 2017-2021.

The pre-committed sub-canopy AIR reference — the +150 cm `_T1` sensor — was NOT
delivered: each of the 12 declared `_T1` channels appears as a SINGLE placeholder
row with an empty (NaN) `clim_ts_values`. The `_Soil moisture` channels are
likewise empty (12 placeholder NaN rows). The `clim_ts_values` column is native
float64, so this is a genuine absence of data, not a decimal-parsing artefact.

Consequence: there is NO above-ground air temperature to form the training-
convention offset (sub-canopy AIR minus ERA5 free-air). The only delivered
temperature is a -10 cm SOIL probe — a physically DIFFERENT quantity from the
canopy-buffered air temperature the model was trained on. Substituting it would
manufacture a non-comparable label (the same reason the pseudo-VPD was refused for
Murugan/Astroni), which ADR-016 pre-registration and the ADR-006 ambient
convention forbid.

This is a declared-vs-delivered delivery defect — exactly the failure mode AGENTS.md
§11 flagged: "Future delivery validation must check declared vs delivered coverage."
The 12 sites whose canopy features were pre-verified are precisely the 12 `_T1`
sites; their geospatial features exist, but their air-temperature time series does
not. The freeze therefore HALTS here: it does not call Earth Engine, does not build
a frozen test set from soil temperature, and does not score. It writes a blocker
manifest + a null metrics JSON documenting the defect and characterising, model-free,
what WAS delivered.
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

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "data", "raw", "soiltemp_mdb_data")
JLELIS_XLSX = os.path.join(RAW, "JLelis.xlsx")
TRAIN_SITES = os.path.join(ROOT, "data", "processed", "all_label_sites.csv")
FROZEN = os.path.join(ROOT, "data", "processed", "jlelis_external_test.parquet")
MANIFEST = os.path.join(ROOT, "data", "processed", "jlelis_test_manifest.json")
METRICS = os.path.join(ROOT, "reports", "jlelis_external_metrics.json")

DATA_SOURCE = "JLelis"
EE_PROJECT = "microclimate-crop-design-sys"
DEDUP_KM = 1.0
MIN_DAYS_PER_MONTH = 5            # identical to the SAFE / La Jarda / cocoa builders
AIR_SUFFIX = "T1"                # pre-committed +150 cm shielded air sensor
AIR_HEIGHT_CM = 150              # the deposit's only above-ground air sensor
SOIL_SUFFIX = "T3"              # -10 cm soil / ground probe (delivered, NOT scored)
PLAUSIBLE_C = (-40.0, 65.0)
# nearest training site is ~thousands of km away (Borneo + Spain + oil palm);
# reported precisely at freeze if the set were built.
BRAZIL_BOX = dict(lat=(-9.0, -6.5), lon=(-38.0, -35.5))

SCORED_TARGETS = ["dT_max", "dT_mean"]   # dVPD impossible (no RH), NOT manufactured


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = p2 - p1
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def read_metadata_and_map() -> dict:
    """Parse the JLelis workbook, apply the coordinate-frame guard, and map every
    Raw_data_identifier to (site, suffix, measurement, height, coords). Then run the
    declared-vs-delivered check on the pre-committed +150 cm `_T1` air sensor."""
    md = pd.read_excel(JLELIS_XLSX, sheet_name="Metadata")
    ts = pd.read_excel(JLELIS_XLSX, sheet_name="Raw time series data")

    md["rid"] = md["Raw_data_identifier"].astype(str)
    ts["rid"] = ts["Raw_data_identifier"].astype(str)
    ts["val"] = pd.to_numeric(ts["clim_ts_values"], errors="coerce")
    for c in ("Year", "Month", "Day"):
        ts[c] = pd.to_numeric(ts[c], errors="coerce")

    ts_ids = set(ts["rid"].unique())
    # dedup metadata rows per rid (duplicate rows differ only by declared end date)
    u = md.drop_duplicates("rid").copy()
    u = u[u["rid"].isin(ts_ids)].copy()
    u["suffix"] = u["rid"].str.rsplit("_", n=1).str[1]
    u["site"] = u["rid"].str.rsplit("_", n=1).str[0]

    # coordinate-frame guard (guard against the projected-coordinate trap)
    epsg = set(int(x) for x in u["EPSG"].dropna().unique())
    lat_ok = u["Latitude"].between(-90, 90).all()
    lon_ok = u["Longitude"].between(-180, 180).all()
    med_lat, med_lon = float(u["Latitude"].median()), float(u["Longitude"].median())
    in_brazil = (BRAZIL_BOX["lat"][0] < med_lat < BRAZIL_BOX["lat"][1]
                 and BRAZIL_BOX["lon"][0] < med_lon < BRAZIL_BOX["lon"][1])
    if epsg != {4326} or not (lat_ok and lon_ok and in_brazil):
        raise SystemExit(f"COORD GUARD failed: EPSG={epsg}, lat_ok={lat_ok}, "
                         f"lon_ok={lon_ok}, median=({med_lat},{med_lon})")

    # delivered-value counts per rid
    delivered = (ts.groupby("rid")
                 .agg(total_rows=("val", "size"), nonnull=("val", "count"),
                      vmin=("val", "min"), vmax=("val", "max"),
                      ymin=("Year", "min"), ymax=("Year", "max"))
                 .reset_index())
    u = u.merge(delivered, on="rid", how="left")

    air = u[u["suffix"] == AIR_SUFFIX].copy()
    soil = u[u["suffix"] == SOIL_SUFFIX].copy()

    prov = {
        "coord_frame_guard": (f"PASSED (EPSG 4326, median lat/lon "
                              f"({round(med_lat,3)},{round(med_lon,3)}) inside Brazil box)"),
        "epsg": sorted(epsg),
        "study_lat_range": [round(float(u["Latitude"].min()), 4),
                            round(float(u["Latitude"].max()), 4)],
        "study_lon_range": [round(float(u["Longitude"].min()), 4),
                            round(float(u["Longitude"].max()), 4)],
        "n_distinct_rids": int(len(u)),
        "n_distinct_sites": int(u["site"].nunique()),
        "channels_by_suffix_measurement_height": (
            u.groupby(["suffix", "Microclimate_measurement", "Sensor_height"])
            .size().reset_index(name="n").to_dict("records")),
        "pre_committed_air_sensor": {
            "suffix": AIR_SUFFIX, "declared_height_cm": AIR_HEIGHT_CM,
            "declared_measurement": "Temperature",
            "n_declared_channels": int(len(air)),
            "n_channels_with_ANY_delivered_value": int((air["nonnull"] > 0).sum()),
            "delivered_nonnull_total": int(air["nonnull"].fillna(0).sum()),
            "per_channel": [
                {"rid": r.rid, "site": r.site, "height_cm": float(r.Sensor_height),
                 "total_rows": int(r.total_rows), "nonnull": int(r.nonnull)}
                for r in air.itertuples()],
        },
        "delivered_soil_sensor": {
            "suffix": SOIL_SUFFIX, "declared_measurement": "Temperature",
            "declared_height_cm": sorted(soil["Sensor_height"].unique().tolist()),
            "note": "SOIL / ground probe (negative height), physically distinct from "
                    "the canopy-buffered AIR temperature the model was trained on",
            "n_channels": int(len(soil)),
            "n_channels_with_delivered_values": int((soil["nonnull"] > 0).sum()),
            "delivered_nonnull_total": int(soil["nonnull"].fillna(0).sum()),
        },
        "clim_ts_values_dtype": str(ts["clim_ts_values"].dtype),
        "declared_vs_delivered": (
            "clim_ts_values is native float64; the +150 cm _T1 air channels and the "
            "_Soil moisture channels each appear as a SINGLE placeholder NaN row -- a "
            "genuine data absence, not a decimal-parsing artefact"),
    }
    return {"u": u, "ts": ts, "air": air, "soil": soil, "prov": prov}


def characterise_delivered_soil(m: dict) -> dict:
    """Model-free description of the ONLY delivered temperature channel (_T3 soil).

    Purely descriptive (raw magnitudes + coverage). No ambient reference, no offset,
    no model -- this is characterisation of the delivered data, NOT a substitute test.
    """
    ts, soil = m["ts"], m["soil"]
    soil_ids = set(soil["rid"])
    d = ts[ts["rid"].isin(soil_ids) & ts["val"].between(*PLAUSIBLE_C)].copy()
    d["site"] = d["rid"].str.rsplit("_", n=1).str[0]
    d["dt"] = pd.to_datetime(dict(year=d.Year, month=d.Month, day=d.Day), errors="coerce")
    d = d[d["dt"].notna()].copy()
    daily = (d.groupby(["site", "dt"])
             .agg(t_max=("val", "max"), t_mean=("val", "mean")).reset_index())
    daily["ym"] = daily["dt"].dt.strftime("%Y-%m")
    monthly = (daily.groupby(["site", "ym"])
               .agg(soil_t_max=("t_max", "mean"), soil_t_mean=("t_mean", "mean"),
                    n_days=("dt", "count")).reset_index())
    monthly = monthly[monthly["n_days"] >= MIN_DAYS_PER_MONTH]
    per_site = {
        s: {"months_ge5days": int(g["ym"].nunique()),
            "soil_t_max_mean_C": round(float(g["soil_t_max"].mean()), 2),
            "soil_t_mean_mean_C": round(float(g["soil_t_mean"].mean()), 2)}
        for s, g in monthly.groupby("site")}
    return {
        "sensor": "_T3 soil / ground temperature at -10 cm (declared)",
        "n_sites_with_data": int(monthly["site"].nunique()),
        "n_site_months_ge5days": int(len(monthly)),
        "period": [str(monthly["ym"].min()), str(monthly["ym"].max())],
        "soil_t_max_mean_C_overall": round(float(monthly["soil_t_max"].mean()), 2),
        "soil_t_mean_mean_C_overall": round(float(monthly["soil_t_mean"].mean()), 2),
        "per_site": per_site,
        "interpretation": (
            "This is SOIL/ground temperature, not sub-canopy AIR temperature. It cannot "
            "be scored against an air-temperature offset model without manufacturing a "
            "non-comparable label; reported for completeness only."),
    }


def dedup_air_sites(m: dict) -> dict:
    """ADR-016 de-dup on the pre-committed air-sensor coordinates (the 12 _T1 sites),
    reported even though the air series is empty, to document independence."""
    air = m["air"].drop_duplicates("site")
    tr = pd.read_csv(TRAIN_SITES).drop_duplicates("site_id")
    d = haversine_km(air["Latitude"].values[:, None], air["Longitude"].values[:, None],
                     tr["lat"].values[None, :], tr["lon"].values[None, :])
    nearest = d.min(axis=1)
    return {
        "rule": f"drop external sites within {DEDUP_KM} km of any training site",
        "air_sites_checked": int(len(air)),
        "training_sites_checked": int(len(tr)),
        "min_distance_km": round(float(np.min(nearest)), 1),
        "rows_dropped": int((nearest < DEDUP_KM).sum()),
        "note": "independence is clean, but the _T1 air series carries zero delivered "
                "values, so no air-offset test can be frozen from these sites",
    }


def stage_freeze() -> None:
    m = read_metadata_and_map()
    prov = m["prov"]
    air_info = prov["pre_committed_air_sensor"]
    print(json.dumps({"coord_guard": prov["coord_frame_guard"],
                      "n_sites": prov["n_distinct_sites"],
                      "air_channels": air_info["n_declared_channels"],
                      "air_channels_with_data": air_info["n_channels_with_ANY_delivered_value"],
                      "soil_channels_with_data":
                          prov["delivered_soil_sensor"]["n_channels_with_delivered_values"]},
                     indent=2))

    air_has_data = air_info["n_channels_with_ANY_delivered_value"] > 0
    if air_has_data:
        # If a future re-delivery ships the _T1 air series, the full freeze/EE/score
        # path (mirroring run_astroni_validation.py) would run here. It intentionally
        # does not, because as delivered there is no air temperature to build labels.
        raise SystemExit(
            "UNEXPECTED: _T1 air channels now carry delivered values -- this script's "
            "blocker path assumes they are empty (as in the audited delivery). Extend "
            "the freeze to build air-temperature labels before proceeding.")

    soil = characterise_delivered_soil(m)
    dedup = dedup_air_sites(m)

    blocker = {
        "status": "BLOCKED_AT_FREEZE",
        "reason": "declared-vs-delivered delivery defect",
        "detail": (
            f"The pre-committed sub-canopy AIR reference (+{AIR_HEIGHT_CM} cm _T1 "
            f"shielded sensor) has ZERO delivered values: all "
            f"{air_info['n_declared_channels']} declared _T1 channels appear as single "
            f"placeholder NaN rows. The only delivered temperature is the _T3 soil probe "
            f"(-10 cm), a physically distinct quantity. No training-convention air-offset "
            f"label can be formed; substituting soil temperature is refused under ADR-016 "
            f"(comparability) and the ADR-006 ambient convention."),
        "dVPD": "not computable (no relative-humidity channel) and NOT manufactured",
        "earth_engine": "NOT called -- there is no scoreable test set to build features for",
    }

    manifest = {
        "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "data_source": DATA_SOURCE,
        "blocker": blocker,
        "provenance": prov,
        "dedup_air_sites": dedup,
        "delivered_soil_characterisation": soil,
        "convention_that_would_apply": {
            "labels": "sub-daily -> daily(max/mean) -> monthly mean of dailies, >=5 days, "
                      "YYYY-MM-15 (SAFE/La Jarda)",
            "reference_height_cm": AIR_HEIGHT_CM,
            "ambient": "ERA5 atmospheric free-air rebuilt from ERA5/HOURLY at the "
                       "ERA5/DAILY grid node (ADR-006); solar from ERA5-Land",
            "scored_targets": SCORED_TARGETS,
            "dVPD": "impossible -- no RH; NOT manufactured via amb_rh fallback",
        },
    }
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2, default=str)

    # Null metrics JSON (mirrors the cocoa/astroni NULL structure). No frozen parquet
    # is written because no comparable test set can be built; nothing is scored.
    metrics = {
        "_meta": {
            "scored_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "experiment": "independent Caatinga dry-forest (Brazil) external validation "
                          "of the canopy->offset model (ADR-016 discipline)",
            "data_source": DATA_SOURCE,
            "result": "NULL -- BLOCKED AT FREEZE (delivery defect)",
            "scored_targets": SCORED_TARGETS,
            "headline": blocker["detail"],
            "manifest": os.path.relpath(MANIFEST, ROOT),
            "frozen_test_set": None,
            "scored": False,
        },
        "blocker": blocker,
        "provenance": prov,
        "dedup_air_sites": dedup,
        "delivered_soil_characterisation": soil,
    }
    os.makedirs(os.path.dirname(METRICS), exist_ok=True)
    with open(METRICS, "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    print(f"-> {MANIFEST}")
    print(f"-> {METRICS}")
    print("\n=== BLOCKER ===")
    print(json.dumps(blocker, indent=2))
    print("\n=== DELIVERED SOIL CHARACTERISATION (model-free, NOT scored) ===")
    print(json.dumps({k: soil[k] for k in
                      ["sensor", "n_sites_with_data", "n_site_months_ge5days", "period",
                       "soil_t_max_mean_C_overall", "soil_t_mean_mean_C_overall"]}, indent=2))
    print("\n=== DE-DUP (air-sensor coordinates) ===")
    print(json.dumps(dedup, indent=2))


def stage_score() -> None:
    if not os.path.exists(METRICS):
        raise SystemExit("run --stage freeze first")
    out = json.load(open(METRICS))
    if not out["_meta"].get("scored", False):
        print("NOTHING TO SCORE: the freeze stage was BLOCKED by a delivery defect "
              "(the +150 cm air sensor carries zero delivered values). See:")
        print(f"  {os.path.relpath(METRICS, ROOT)}")
        print(json.dumps(out["_meta"], indent=2, default=str))
        return


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["freeze", "score"], required=True)
    a = ap.parse_args()
    stage_freeze() if a.stage == "freeze" else stage_score()
