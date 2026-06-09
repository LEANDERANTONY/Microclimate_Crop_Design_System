# ADR-009 — Sourcing regional data to narrow the Borneo/Spain transfer gap

- **Status:** Accepted (partial — SBIO integrated as reference; understory maps identified)
- **Date:** 2026-06
- **Follows:** [[ADR-008]] (oil-palm regime; found Pattukkottai OOD is macro-driven)

## Context

ADR-008 showed the dominant out-of-distribution driver for Pattukkottai/Anaikadu is
its **macroclimate/soil** (warm tropical nights, semi-arid), with no analog in the
humid-Borneo + Mediterranean-Spain training set. We searched for openly available
regional data to narrow that gap.

## What is available online (assessed)

1. **SoilTemp global soil-temperature maps** (Lembrechts et al. 2022, *Glob. Change
   Biol.*) — **live on Earth Engine** (`projects/crowtherlab/soil_bioclim/SBIO_v2_0_5cm`
   / `_5_15cm`), 1 km, global incl. Tamil Nadu; GeoTIFFs also on Zenodo 7134169.
   Variable = near-surface **soil** temperature (bioclim aggregates), *not* canopy air.
2. **Pan-tropical forest understory temperature maps** (Ismaeel & Maeda 2024, *Nat.
   Commun.*; Finnish Fairdata DOI 10.23729/dd3de08e-39a1-46b0-b28a-7bc577b6c914) —
   monthly day/night/daily understory air temp at 15 cm, 300 m, 2000–2021, pan-tropical
   incl. South India. **Best variable match.** Open (embargo expired Mar 2024) but
   **154 files / 38 GB**, tiled; 30 m available on request. Forest understory (humid).
3. **SoilTemp raw logger database** — gold-standard raw sub-canopy loggers; gated
   (access request already emailed). Best raw data, not yet granted.
4. **EFForTS Sumatra oil-palm loggers** (Mendeley) — real open-canopy tropical, but
   humid Indonesia, one week.

## Decision

- **SBIO → integrated as a REGIONAL REFERENCE / cross-check**, not as air-offset
  training labels (variable mismatch: soil ≠ canopy air; feeding it as dT labels would
  pollute the model). `scripts/region_reference.py` quantifies the transfer gap.
- **Tropical understory maps → identified as the variable-correct next ingestion**,
  but NOT bulk-downloaded (38 GB over a slow link is poor value, and humid-forest
  understory still won't capture semi-arid Pattukkottai). Path: fetch the index map +
  the South-India tile only, or request the 30 m India subset from the authors.
- **SoilTemp raw** remains the gold standard pending access.

## Evidence — regional transfer gap (SBIO near-surface soil temp, °C)

| site | annual mean | warm-month max | cold-month min | warm qtr | cold qtr |
|---|---|---|---|---|---|
| Anaikadu (target, TN) | 29.4 | 38.9 | 25.2 | 32.2 | 25.8 |
| SAFE Borneo (train)   | 21.8 | 22.3 | 19.6 | 22.3 | 21.3 |
| La Jarda Spain (train)| 14.2 | 36.7 |  5.8 | 22.3 |  7.9 |

Anaikadu's thermal regime — especially its warm minima — sits well above both training
regions, confirming the gap with real regional data.

## Consequences / next

- The honest takeaway is unchanged and now data-backed: open humid-tropical/forest
  products narrow but do not close the **semi-arid warm-night** gap. The definitive
  fixes remain (a) SoilTemp raw access (incl. any South-Asian dry-zone loggers) and
  (b) the user's own plot sensors.
- Concrete next ingestion: South-India tile of the Ismaeel/Maeda understory maps
  (index map → one tile), sampled into offset rows like the SAFE raster (ADR-008).

## Update — understory maps scoped precisely (2026-06-09)

The Fairdata Metax file API (`scripts/fairdata_files.py`) lists all 154 files. The set
is tiled **by continent** and there is a dedicated **`South_asia`** tile (covers Tamil
Nadu), in three products — `Data_Daily`, `Data_Daytime`, `Data_Nighttime` — at **309 MB
per month** (12 months each). So the relevant subset is ~3.7 GB per product, not 38 GB.
Also present: a 0.6 MB `Index_map/Tile_Index.shp`, 24 calibration sensor CSVs +
`Sensor_location.shp`, and predictor rasters (`Codes/02ImageData`).

Blocker: the Fairdata **download endpoint requires their tokenized authorization flow**
(plain GET to `download.fairdata.fi` returns 400) — not a one-line urlretrieve like
Zenodo. Variable note: these are *daytime/daily/nighttime MEAN* understory temps (not
Tmax), so they map to `dT_mean`/night offsets cleanly and to `dT_max` only as a
daytime-mean proxy.

## Update 2 — download flow investigated; scripted bulk pull not worthwhile (2026-06-09)

Probed the download service (`scripts/probe_fairdata_api.py`, `fairdata_download.py`):
root REST paths (`/authorize`, `/requests`) return **404**; only a `/download` endpoint
exists and needs a token. The Etsin UI reveals why — downloading requires **server-side
"package generation"** ("may take minutes or even hours", with optional email-notify),
generated per folder, *then* a tokenized download. There is **no clean per-file API** to
script cheaply. Combined with: 38 GB folder (or ~3.7 GB per product even for `South_asia`
alone), a slow link, and the *humid-forest-understory* variable being only a partial fit
for semi-arid Tamil Nadu — a scripted bulk pull is **not worth it**.

**Decision:** route (a) supersedes (b). A data-request email to the corresponding author
(Dr Eduardo Maeda, eduardo.maeda@helsinki.fi) for the **30 m South-Asia subset** was
drafted (Gmail draft, 2026-06-09) — that yields strictly better data than the 300 m bulk
tiles and avoids the package-generation/download burden. The downloader scaffold
(`fairdata_download.py`) is kept for the day a direct package URL is available. If the
300 m tiles are ever wanted before the author replies, generate a `South_asia`-only
package via the Etsin UI with email-notify, then point `fairdata_download.py` at the URL.
