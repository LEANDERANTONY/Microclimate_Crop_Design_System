# ADR-008 — Add an open-canopy (oil-palm) regime so coconut is in-distribution

- **Status:** Accepted
- **Date:** 2026-06
- **Follows:** [[ADR-006]] (real data, free-air reference), [[ADR-007]] (OOD flag)

## Context

ADR-007 established that our offset models, trained only on **closed forest**
(SAFE Borneo + La Jarda Spain), extrapolate when applied to **coconut** — a tall,
sparse, open palm canopy. Coconut designs flagged OOD ≈ 0.5 (most features outside
the training range), so the learned temperature/VPD offset under coconut was LOW
confidence. The fix flagged in ADR-007 was to add an **open-canopy training regime**.

The original Hardwick et al. (2015) raw oil-palm dataloggers have no cleanly
downloadable open deposit (PMC captcha-walled; the EFForTS Sumatra loggers are a
one-week Elsevier/Mendeley set). The reliably available, same-lineage source is the
**SAFE landscape microclimate raster** (Zenodo 7893600; Jucker, Hardwick et al.,
*Glob. Change Biol.* 2018 / 10.1111/gcb.14415).

## Decision

Use the SAFE landscape raster as the open-canopy regime, sampled to points:

- Modelled daily sub-canopy **T_max / T_mean / VPD_max** at 50 m across the SAFE
  landscape (2013-05 → 2015-03), which spans **closed forest → logged → oil-palm →
  cleared**. Forest cells are tall/high-LAI; oil-palm and cleared cells are
  short/low-LAI — exactly the open-canopy feature space coconut occupies.
- `scripts/build_oilpalm_labels.py` samples a 34×34 lon/lat grid, takes each point's
  **period-mean** sub-canopy value (mean over daily bands, nodata-masked), then
  attaches that point's **real** canopy structure and terrain/soil from Earth Engine
  (ETH canopy height, MODIS LAI/FPAR/NDVI, Copernicus DEM/slope, SoilGrids clay/soc)
  and **ERA5 free-air** macroclimate for the same period.
- Offsets are computed against ERA5 free-air exactly as the forest labels
  (`dT_max`, `dT_mean`, `dVPD`), per ADR-006. Rows carry `site_id = "OP_*"`.
- Integration is idempotent: the original forest table is preserved as
  `labelled_offsets_forest.parquet`; the canonical `labelled_offsets.parquet`
  becomes `forest ⧺ palm`, so all downstream training/validation picks it up.

## Honesty / limitations

- These sub-canopy values are **model-derived** (LiDAR + datalogger projection),
  not raw loggers — so the palm regime is a *plausibility-and-coverage* anchor, not
  ground truth. This is weaker than the forest labels (raw loggers) and is the
  reason the user's own coconut-farm sensors (year 2) remain the definitive fix.
- The SAFE landscape is small vs the ERA5 pixel, so macro is near-constant across
  points; the across-point offset signal is therefore driven by **canopy structure**,
  which is the intended relationship.
- Physics (light via Beer–Lambert, wind via shelterbelt) stays HIGH confidence and
  is unaffected — this ADR only concerns the learned temperature/VPD offset.

## Result (after build + retrain — 2026-06-09)

320 palm/open-canopy points added → combined **2,444 forest + 320 palm = 2,764 rows**.
The palm regime carries **real open-canopy offsets up to dT_max = +6.6 °C** (vs free
air) — matching Hardwick's "+6.5 °C oil palm vs forest" — and extends the training
canopy axis down to **LAI 1.6 / canopy height 9 m** (forest-only started ≈ LAI 3+).

**But the coconut OOD score barely moved (≈ 0.58 → 0.54), still flagged.** A per-feature
decomposition (`scripts/diag_ood.py`) shows *why*, and it is the important finding:

- The **dominant OOD driver is Pattukkottai's macroclimate/soil**, not canopy:
  `t_mean 29.3` (train max 27.3), `t_min 25.9` (train max 22.2), low `elevation 23 m`,
  low `soc`, plus `gdd_proxy` — i.e. **warm-night semi-arid tropical Tamil Nadu has no
  analog** in humid Borneo (~2600 mm) or Mediterranean Spain. This is a climate-transfer
  gap, not a canopy gap.
- A **secondary** driver: coconut at design `LAI 1.0` is still *below* the palm training
  minimum (1.61). The sampled oil-palm LAI reads high partly from MODIS 500 m mixed
  pixels in a forest-dominated landscape, so even oil palm wasn't as sparse as coconut.

So adding palm data was **necessary but not sufficient**: it fixed the open-canopy
*offset realism* and partially the canopy feature axis, but Pattukkottai stays OOD
because of its macroclimate. The honest takeaway is unchanged and now precisely
attributed — physics (light/wind) remains the trustworthy lever under coconut.

## Next (revised)

1. **Macroclimate transfer gap is now the priority**, not canopy: add a training site
   in a monsoonal / semi-arid tropical climate (SoilTemp Indian/South-Asian loggers,
   or Indian agroforestry microclimate data) so warm-night tropical macro is covered.
2. Emit a realistic coconut `LAI ≈ 1.2–1.5` from `build_feature_row` and treat MODIS
   LAI mixed-pixel inflation when sampling open canopies.
3. Ultimate fix unchanged: the user's own coconut-farm sensors (year 2).
