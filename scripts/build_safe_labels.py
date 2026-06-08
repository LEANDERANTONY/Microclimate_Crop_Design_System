"""Build a label-sites table from the SAFE Project 1st-order microclimate data.

Joins sub-canopy air-temperature / RH records (data/raw/template_Hardwick1stOrder.xlsx)
to plot coordinates from the SAFE gazetteer (data/raw/gazetteer.geojson), and
aggregates the sub-daily stream to per-plot, per-month statistics:

    sub_t_max  = monthly mean of daily maximum sub-canopy temperature
    sub_t_mean = monthly mean of daily mean sub-canopy temperature
    sub_rh     = monthly mean RH

Output: data/processed/safe_label_sites.csv with
    site_id, lat, lon, date, sub_t_max, sub_t_mean, sub_rh, n_days
These are the SUB-CANOPY measurements; the AMBIENT pairing (ERA5) and the offset
targets are computed downstream (see data/load.compute_offset_targets).
"""
import csv
import datetime as dt
import json
import os
from collections import defaultdict

import openpyxl

RAW = "data/raw"
OUT = "data/processed/safe_label_sites.csv"

# ---- 1. plot -> (lat, lon) from the gazetteer ----
gaz = json.load(open(f"{RAW}/gazetteer.geojson", encoding="utf-8"))
coords = {}
for f in gaz["features"]:
    p = f.get("properties") or {}
    loc, cx, cy = p.get("location"), p.get("centroid_x"), p.get("centroid_y")
    if loc and cx is not None and cy is not None:
        coords[str(loc)] = (float(cy), float(cx))   # (lat, lon)
print(f"gazetteer locations: {len(coords)}")

# ---- 2. stream the Data sheet, accumulate per (plot, day) ----
wb = openpyxl.load_workbook(f"{RAW}/template_Hardwick1stOrder.xlsx",
                            read_only=True, data_only=True)
ws = wb["Data"]
col, header_seen = {}, False
daily = defaultdict(lambda: {"tmax": -1e9, "tsum": 0.0, "tn": 0, "rhsum": 0.0, "rhn": 0})

for row in ws.iter_rows(values_only=True):
    if not header_seen:
        if row and row[0] == "field_name":
            for idx, nm in enumerate(row):
                if nm in ("Plot", "time", "Temp", "RH"):
                    col[nm] = idx
            header_seen = True
        continue
    plot = row[col["Plot"]] if col.get("Plot") is not None else None
    t = row[col["time"]] if col.get("time") is not None else None
    if plot is None or t is None:
        continue
    if isinstance(t, dt.datetime):
        d = t.date()
    else:
        try:
            d = dt.datetime.strptime(str(t), "%d/%m/%Y %H:%M").date()
        except ValueError:
            continue
    temp = row[col["Temp"]] if col.get("Temp") is not None else None
    rh = row[col["RH"]] if col.get("RH") is not None else None
    rec = daily[(str(plot), d)]
    if temp is not None:
        try:
            temp = float(temp)
            rec["tmax"] = max(rec["tmax"], temp); rec["tsum"] += temp; rec["tn"] += 1
        except (TypeError, ValueError):
            pass
    if rh is not None:
        try:
            rec["rhsum"] += float(rh); rec["rhn"] += 1
        except (TypeError, ValueError):
            pass

print(f"plot-days accumulated: {len(daily)}")

# ---- 3. daily -> monthly per plot ----
month = defaultdict(lambda: {"tmax_s": 0.0, "tmax_n": 0, "tmean_s": 0.0,
                             "tmean_n": 0, "rh_s": 0.0, "rh_n": 0, "days": 0})
for (plot, d), rec in daily.items():
    if rec["tn"] == 0:
        continue
    m = month[(plot, d.year, d.month)]
    m["tmax_s"] += rec["tmax"]; m["tmax_n"] += 1
    m["tmean_s"] += rec["tsum"] / rec["tn"]; m["tmean_n"] += 1
    if rec["rhn"] > 0:
        m["rh_s"] += rec["rhsum"] / rec["rhn"]; m["rh_n"] += 1
    m["days"] += 1

# ---- 4. write label rows (require >=5 days/month and known coords) ----
rows, missing = [], set()
for (plot, y, mo), m in month.items():
    if plot not in coords:
        missing.add(plot); continue
    if m["days"] < 5:
        continue
    lat, lon = coords[plot]
    rows.append({
        "site_id": plot, "lat": round(lat, 6), "lon": round(lon, 6),
        "date": f"{y:04d}-{mo:02d}-15",
        "sub_t_max": round(m["tmax_s"] / m["tmax_n"], 3),
        "sub_t_mean": round(m["tmean_s"] / m["tmean_n"], 3),
        "sub_rh": round(m["rh_s"] / m["rh_n"], 2) if m["rh_n"] else "",
        "n_days": m["days"],
    })

os.makedirs("data/processed", exist_ok=True)
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["site_id", "lat", "lon", "date",
                                      "sub_t_max", "sub_t_mean", "sub_rh", "n_days"])
    w.writeheader(); w.writerows(rows)

print(f"label rows: {len(rows)} | plots: {len({r['site_id'] for r in rows})} "
      f"| months: {len({r['date'] for r in rows})}")
print(f"plots missing coords: {len(missing)} {sorted(missing)[:8]}")
for r in rows[:3]:
    print(r)
