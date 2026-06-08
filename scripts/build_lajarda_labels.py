"""Build label-sites from the La Jarda (Cadiz, Spain) microclimate dataset, and
combine with the SAFE labels into one multi-landscape label table.

La Jarda = Mediterranean near-surface (30 cm) air temp + RH, 2004-2006. Different
macroclimate from SAFE (Borneo tropical), giving the cross-climate spread the
transfer claim needs. Output matches safe_label_sites.csv columns; site_ids are
prefixed "LJ_" to avoid collision. Also writes the concatenated all_label_sites.csv.
"""
import pandas as pd

RAW, PROC = "data/raw", "data/processed"

df = pd.read_csv(f"{RAW}/LaJarda_microclimate_revised.csv")
coords = pd.read_csv(f"{RAW}/point_coordinates.csv")            # Point, Latitude, Longitude
df = df.dropna(subset=["Temperature"])

# daily -> monthly per point (monthly mean of daily max / daily mean / RH)
daily = (df.groupby(["Point", "Year", "Month", "Day"])
         .agg(tmax=("Temperature", "max"), tmean=("Temperature", "mean"),
              rh=("RH", "mean")).reset_index())
monthly = (daily.groupby(["Point", "Year", "Month"])
           .agg(sub_t_max=("tmax", "mean"), sub_t_mean=("tmean", "mean"),
                sub_rh=("rh", "mean"), n_days=("Day", "count")).reset_index())
monthly = monthly[monthly.n_days >= 5]
m = monthly.merge(coords, on="Point", how="inner")

lj = pd.DataFrame({
    "site_id": "LJ_" + m.Point.astype(str),
    "lat": m.Latitude.round(6), "lon": m.Longitude.round(6),
    "date": m.apply(lambda r: f"{int(r.Year):04d}-{int(r.Month):02d}-15", axis=1),
    "sub_t_max": m.sub_t_max.round(3), "sub_t_mean": m.sub_t_mean.round(3),
    "sub_rh": m.sub_rh.round(2), "n_days": m.n_days,
})
lj.to_csv(f"{PROC}/lajarda_label_sites.csv", index=False)
print(f"La Jarda: {len(lj)} rows, {lj.site_id.nunique()} plots, {lj.date.nunique()} months")

# combine with SAFE
safe = pd.read_csv(f"{PROC}/safe_label_sites.csv")
allrows = pd.concat([safe, lj], ignore_index=True)
allrows.to_csv(f"{PROC}/all_label_sites.csv", index=False)
print(f"combined: {len(allrows)} rows, {allrows.site_id.nunique()} plots "
      f"(SAFE {safe.site_id.nunique()} + La Jarda {lj.site_id.nunique()})")
print(lj.head(3).to_string(index=False))
