# External validation datasets (Paper 1)

How Paper 1's validation data is organised, and the pre-registration that keeps it
honest. Two distinct questions, two distinct data needs:

- **(A) Within-climate generalization** — does the model work on *new, independent
  sites in the climates it was trained on* (humid-tropical, Mediterranean)? This is
  the legitimate **positive** claim. Data available now.
- **(B) Cross-climate transfer / deployment gap** — does it transfer to an *unseen*
  climate (semi-arid Pattukkottai/Anaikadu)? This is the **honest negative** /
  deferred-deployment story. No same-region open data exists.

Validating in (A) does **not** validate (B). Paper 1's claim is "generalizes within
trained climates"; the semi-arid farm relevance waits for the user's own sensors or
for adding a semi-arid source to *training*.

---

## What we trained on (the baseline for independence)

| Source | Climate | Region / coords | Period | Sites |
|---|---|---|---|---|
| SAFE Project (Borneo) | Humid tropical rainforest + oil-palm | Sabah, Malaysia ~4.69 °N, 117.58 °E | 2011–2012 | `E_*` (e.g. E_196, E_224, E_198), oil-palm rasters |
| La Jarda (Spain) | Mediterranean | SW Spain (Cádiz) ~36.57 °N, −5.60 °E | 2005–2006 | `LJ_*` (DOWN/UP_*) |

Any validation site must be **disjoint** from these by study, location and time.

---

## (A) Independent within-climate validation — available now

| Dataset | Climate (matches) | Variables | Canopy/structure | Independent of training? | Access |
|---|---|---|---|---|---|
| **Cocoa agroforestry, Alto Beni** (Zenodo 1185579) | Humid tropical (≈ Borneo regime) | Canopy openness, light, throughfall, **T, RH**; mono vs agroforestry | Yes — agroforestry design contrast | **Clean.** Bolivia (~15.4 °S, 67.5 °W) — different continent, study and decade from SAFE | Open download (Zenodo) ✅ |
| Pan-tropical understory TMS (Nat. Comms. 2024) | Humid tropical | Near-surface T (TMS), hourly | Forest | ⚠️ **Contamination risk** — spans South/SE Asia and may include SAFE/Bornean loggers; must de-dup by site coords before use | Raw via SoilTemp request |
| SoilTemp Iberian/Mediterranean in-situ | Mediterranean (≈ La Jarda regime) | Sub-canopy **air T** <100 cm, ≥4 h, RH/soil where available | Site metadata | The **correct systematic source**; exclude La Jarda by coords | Gated (data request) ⏳ |
| Aleppo-pine shrub-layer gradient (AgForMet 2020) | Mediterranean (lowland — **best climatic match**) | **T, RH, VPD, solar, soil moisture** across a dense/medium/low/open cover gradient ± shrub | Vegetation-cover gradient = controllable design | Clean (S. France/Med, not La Jarda) | On request to authors (HAL article only) ⏳ |
| ForestTemp / ForestClim (Europe) | Mediterranean/temperate | **Modelled** 25 m offset maps | n/a | n/a — model *output*, not in-situ truth | Figshare (open) ❌ as truth |

### Mediterranean vetting verdict (2026-06-15)

No **immediately-open, clean, sub-canopy air-temperature in-situ** Mediterranean set
exists that matches lowland Cádiz and is independent of La Jarda. Per-candidate:

- **Montseny (NE Spain)** — ❌ wrong variables. It's a long-term *hydrological /
  biogeochemical* catchment record (streamflow, water chemistry, N deposition,
  1978–2018), not sub-canopy microclimate loggers.
- **SENTHYMED/MEDOAK (Montpellier, FR)** — ⚠️ partial only. Has canopy structure
  (PAI, LiDAR) + **soil** moisture/temperature, one season, remote-sensing focus; no
  clear sub-canopy **air**-T offset. Usable as a structure/soil-temp auxiliary, not
  the air-T validation.
- **Fagus treeline (Italy, Sci. Rep. 2021)** — ❌ for now. Does measure below-canopy
  near-ground air T, but data are "available from the corresponding author on
  reasonable request" (not deposited), and it's a mountain treeline (cooler, weak
  match to lowland Cádiz).
- **Aleppo-pine shrub-layer (AgForMet 2020)** — ⭐ best *scientific* fit (cover
  gradient → T/RH/VPD/solar, exactly our design→microclimate structure) but data
  openness unconfirmed — likely on-request (HAL hosts the paper, not a data deposit).
- **ForestTemp/ForestClim** — ❌ as ground truth: it is a *gridded modelled* product.

**Recommendation:** the Mediterranean leg is access-gated, not impossible. Two
parallel requests (same effort class as the pan-tropical raw): (1) **SoilTemp** data
request for Iberian/Mediterranean sub-canopy air-T loggers, de-duplicated against La
Jarda; (2) email the **Aleppo-pine** authors for their gradient data. Until one
arrives, the only immediately-runnable independent external test is the humid-tropical
**cocoa Zenodo** set — so it is fine to produce the first external-validation result on
cocoa and add the Mediterranean leg when the request clears. Do **not** substitute
Montseny (wrong variable) or ForestTemp (modelled) to fill the gap.

## (B) Cross-climate / deployment gap — deferred

| Dataset | Role |
|---|---|
| OzFlux/TERN semi-arid (Alice Mulga) & savanna (Howard Springs/Litchfield/Fletcherview) | Best semi-arid analogue, but **above-canopy** flux-tower met — validates the ambient driver, not the under-canopy offset |
| Indian gridded soil-T/moisture; ERA5-Land, NASA POWER, IMD | Model **inputs/features** for our region — not independent labels |
| **User's own plot loggers (year 2)** | The definitive semi-arid fix — collapses the deployment gap; few-shot recalibration already shown to work with ~5–25 local points |

There is **no open under-canopy logger dataset for tropical/semi-arid South India** —
same-region open validation is impossible; (B) is a characterized limitation, not a gap
to paper over.

---

## Pre-registration rule

1. **Primary within-climate test (humid-tropical): cocoa Zenodo 1185579** — frozen,
   confirmed geographically/temporally disjoint from SAFE.
2. **Secondary (Mediterranean):** access-gated (see vetting verdict). Request
   SoilTemp Iberian/Mediterranean in-situ (sites ≠ La Jarda) and the Aleppo-pine
   gradient data; add this leg once it clears. Not a blocker for the first result.
3. For any SoilTemp-derived set (pan-tropical TMS included), **de-duplicate by site
   coordinates against `data/processed/all_label_sites.csv`** before scoring; drop any
   site within ~1 km of a training site.
4. Declare the held-out sites in methods and compute external metrics **once**, after
   freezing. Report honestly regardless of outcome.

## Sources

- Cocoa agroforestry microclimate (Zenodo): https://zenodo.org/record/1185579
- Pan-tropical understory temperatures (Nat. Comms. 2024): https://www.nature.com/articles/s41467-024-44734-0
- ForestTemp – European sub-canopy temperatures (Figshare): https://figshare.com/articles/dataset/ForestTemp_sub-canopy_microclimate_temperatures_of_European_forests/14618235
- Montseny long-term dataset: https://onlinelibrary.wiley.com/doi/abs/10.1002/hyp.14887
- SENTHYMED/MEDOAK Mediterranean oak dataset: https://www.sciencedirect.com/science/article/pii/S2352340924001562
- OzFlux/TERN: https://www.tern.org.au/natt-the-backbone-of-nt-research/
- SoilTemp (tropics underrepresented): https://onlinelibrary.wiley.com/doi/abs/10.1111/gcb.15123
