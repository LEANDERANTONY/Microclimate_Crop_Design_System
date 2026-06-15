# External validation datasets (Paper 1)

Register of open microclimate label sources for held-out validation, with access
terms and climate match to the deployment region (Pattukkottai / Anaikadu,
Thanjavur — hot tropical, semi-arid delta, ~28 °C mean, NE-monsoon rainfall).

## Honest headline

**No open under-canopy microclimate logger dataset exists for tropical / semi-arid
South India.** SoilTemp itself states hot tropical climates — tropical seasonal
forest / savanna, and Asia in particular — are largely underrepresented. What
exists *for our exact region* is only the macroclimate / gridded layer used as
model **inputs** (ERA5-Land, NASA POWER, IMD, the Indian gridded soil-temperature
/ soil-moisture product), not the under-canopy **labels** we need.

Consequence: same-region validation is not available from open data. The credible
strategy is a **pre-registered held-out climatic analogue** (chosen and frozen
before scoring), with the user's own plot loggers as the year-2 local
calibration/validation.

## Candidate held-out sources (priority order)

| # | Dataset | Climate match | Variables | Canopy/structure | Access | Role |
|---|---|---|---|---|---|---|
| 1 | Pan-tropical understory TMS (*Patterns of tropical forest understory temperatures*, Nat. Comms. 2024) | Warm tropical, 3 continents (incl. tropical Asia) | Near-surface air/surface/soil T (TOMST TMS), hourly, 2015–2022 | Forest canopy; paired to ERA5-Land | **Modelled** outputs open on Finnish Fairdata; **raw logger labels via the SoilTemp platform** (request/collaboration, not one-click). 30 m South-Asia subset already requested from authors. | Best warm-climate held-out test (temperature/offset) |
| 2 | Cocoa agroforestry microclimate (Zenodo, Alto Beni, Bolivia) | Humid tropical (not semi-arid) | Canopy openness, light, throughfall, T, RH; mono vs agroforestry | Agroforestry — directly relevant design contrast | Open download (Zenodo) | Agroforestry-specific held-out; tests design→microclimate contrast |
| 3 | OzFlux / TERN semi-arid + savanna (Alice Mulga ≈ semi-arid; Howard Springs / Litchfield / Fletcherview ≈ savanna) | **Best semi-arid analogue** to Pattukkottai | Eddy-covariance met (T, RH, radiation, wind), QA/QC L1–L6 | **Above-canopy** flux towers | Open (TERN/OzFlux portal) | Validates ambient/macroclimate side; NOT under-canopy offset |
| — | SoilTemp global database | Mostly temperate; tropics sparse | Near-surface T loggers | Mixed | Contributory platform; request access | Broad borrowed pre-training (already in use) |
| — | Indian gridded soil T / soil moisture (Sci. Data 2018); ERA5-Land, NASA POWER, IMD | Same region | Gridded reanalysis T/moisture/met | n/a | Open | Model **inputs / features**, sanity checks — not independent labels |

Already integrated as in-set training (not held-out): SAFE Borneo + La Jarda
Spain forest loggers, SAFE oil-palm rasters.

## Pre-registration rule

Pick **one** held-out dataset (recommended: #1 pan-tropical TMS once raw access
clears; fall back to #2 cocoa Zenodo, which is immediately downloadable), declare
it in the manuscript methods, and freeze it **before** computing any external
metric. Report its performance honestly even if mediocre — a predefined,
honestly-reported external test is worth more than a cherry-picked flattering one.

## Caveats that travel with each

- #1 access is the rate-limiter; the open Fairdata layer is *modelled* maps, the
  raw point labels need the SoilTemp request.
- #2 is humid not semi-arid — good for the agroforestry design contrast, weaker as
  a Pattukkottai climate analogue.
- #3 is above-canopy, so it validates the ambient driver, not the offset that is
  the paper's core claim.

## Sources

- SoilTemp — global near-surface temperature database (tropics underrepresented):
  https://onlinelibrary.wiley.com/doi/abs/10.1111/gcb.15123 ,
  https://www.soiltempproject.com/
- Pan-tropical understory temperatures (Nat. Comms. 2024), data via SoilTemp +
  Fairdata: https://www.nature.com/articles/s41467-024-44734-0
- Cocoa agroforestry microclimate (Zenodo): https://zenodo.org/record/1185579
- OzFlux / TERN semi-arid & savanna:
  https://www.tern.org.au/natt-the-backbone-of-nt-research/
- Indian gridded soil moisture/temperature (Sci. Data 2018):
  https://www.nature.com/articles/sdata2018264
