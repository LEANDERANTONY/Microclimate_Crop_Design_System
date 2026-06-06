# Project Context

Single-file briefing for any chat picking up this project (mirrors AGENT.md, but
tracked in git so it travels with the repo and the Cowork project folder).

## What this is
An agroforestry decision-support system. Core question: "If I turn this field
into an agroforestry system with a given canopy + windbreak + irrigation + crop
variety + fruiting timing, what microclimate emerges, which crops become viable
(accounting for disease), and what design makes a target crop work?"

## Site
Pattukkottai, Thanjavur district, Tamil Nadu — hot semi-arid delta. ~28C mean
(40C May, 20C Jan nights), RH ~70-73%, ~900-1000mm rain concentrated in the NE
monsoon (Oct-Dec), hot dry summers, alluvial/clay soils. KEY LEVER: the humid
disease window is Oct-Dec while summers are hot/dry, so fruiting-time (bahar) is
as powerful a control as canopy or windbreaks. The user plans to farm their own
land here; a strong version is also publishable.

## Architecture (five layers; inverse-design optimiser wraps layers 1-3)
1. Macroclimate + farm design -> microclimate (incl. leaf-wetness duration).
   Beer-Lambert light + shelterbelt wind (physics, HIGH conf); XGBoost quantile
   models for temp/VPD offsets with conformal intervals. BUILT.
2. Microclimate + variety -> disease risk. Mechanistic infection models x variety
   susceptibility (disease triangle). Leaf-wetness is the bridge variable.
   Literature-shaped, LOW conf. BUILT.
3. Growth fit (fuzzy limiting-factor / Liebig minimum) + disease ->
   viability = growth x (1 - disease_risk). Two-axis. BUILT.
4. Yield band = reference_yield x suitability x (1 - disease loss). DESIGNED only.
5. Profitability = yield band x price band - costs; price = trailing-average band
   + trend + production-surplus/market-distance penalty. DESIGNED only
   (docs/economics_layer.md). Not trained models.

## Stack & conventions
uv-managed, Python 3.11, src/ layout. Package `agroforestry`: config, physics,
features, models (XGBoost quantile + CQR), validation (LOSO), predict,
suitability (viability), disease, optimize, data/{synth,load}, cli/run_pipeline.
Tests in tests/ (9 passing). Docs in docs/; generated catalogs + loso_metrics.json
in reports/. Mirrors sibling repos (AI_Job_Application_Agent,
HelpmateAI_RAG_QA_System, Multimodal_Cancer_Detection): uv + src + docs/ROADMAP/
DEVLOG/folder_structure/AGENT.md.

Run on the Windows host (the Cowork Linux sandbox cannot train —
HYPERVISOR_VIRT_DISABLED): `uv sync`, `uv run python scripts/run_pipeline.py`,
`uv run pytest`. Long runs: background to a log and poll.

## Discipline (load-bearing)
- Confidence labels: physics (light, wind) = HIGH; temperature offset = MODERATE
  (borrowed-label ML, leave-one-site-out validated); humidity/VPD and ALL disease
  infection parameters = LOW / literature-shaped, not locally calibrated. Present
  comparisons (design A vs B, dry vs wet bahar, variety A vs B) as trustworthy and
  absolute numbers as indicative.
- Synthetic data (data/synth.py) is fabricated; its metrics prove the machinery,
  not real results. Real science begins at data/load.py.
- Validation is leave-one-site-out (never random split); conformal calibration is
  group-aware (cross-site).
- Layers 4-5 are transparent user-editable estimates with bands, not trained models.
- Write an ADR for significant decisions; append to DEVLOG.md after changes.

## Data status
Running on synthetic borrowed-label data now. Real data (NOT yet wired) = borrowed
microclimate labels (SoilTemp, ForestTemp, agroforestry datasets) + Earth Engine
features (ERA5, Sentinel-2 LAI, SoilGrids, DEM), with offsets (sub-canopy - ambient)
as targets. Own field sensors (TMS-4) are ~a year away — for local validation/
calibration, not year-1 training.

## Crop set
Spices (vanilla, cocoa, black pepper, nutmeg, ginger) + fruits (pomegranate, guava,
mango, sapota, banana, papaya, custard apple, fig, dragon fruit, grapes, acid lime,
amla, moringa; avocado kept as a negative/unsuitable example — needs altitude).
Focus = the "engineerable" group (pomegranate, dragon fruit, grapes, ginger,
pepper) where microclimate/variety/timing tips marginal crops into viability.

## Current state (2026-06)
Layers 1-3 implemented, verified, committed. Next: wire
src/agroforestry/data/load.py to real SoilTemp/ForestTemp + Earth Engine sources.
