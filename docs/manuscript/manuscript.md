# From canopy design to crop profit: an uncertainty-aware agroforestry microclimate model with explicit transfer limits

**Leo Antony**
Independent research · Anaikadu (Pattukkottai), Thanjavur District, Tamil Nadu, India

*Manuscript draft — v0.3, June 2026. All numbers trace to the committed pipeline (`scripts/export_results.py` → `reports/results.json`; transfer metrics `reports/loso_full_metrics.json`, `reports/loco_metrics.json`, `reports/mondrian_metrics.json`). References carry DOIs in §References. Pre-submission manual steps: confirm Zenodo depositor names on each dataset "Cite as" line; finalise a few flagged DOIs; export all figures at journal DPI.*

---

## Highlights

- A six-layer model chains agroforestry **design → microclimate → disease → crop viability → profit** under propagated uncertainty.
- Canopy temperature/VPD offsets are learned (gradient-boosted, quantile) with conformal intervals and an out-of-distribution flag; light and wind are mechanistic.
- Offsets transfer **within** climate (leave-one-site-out skill +49 %) but **fail across** macroclimates (leave-one-climate-out skill negative; intervals lose calibration).
- ~5–25 local calibration points restore out-of-climate interval coverage from 0.08 to ~0.80 — quantifying the value of on-plot sensing.
- For a real Tamil Nadu farm, coconut + black pepper is the robust, profitable pick; the model flags rather than over-claims its extrapolations.

---

## Abstract

An agroforestry system creates its own microclimate, and that microclimate — not the regional average used by conventional crop-recommendation tools — governs which crops are viable, what diseases establish, and whether a planting pays. We present an end-to-end, confidence-labelled decision pipeline chaining six layers: (1) design → microclimate, combining mechanistic physics (Beer–Lambert light, shelterbelt wind) with machine-learned (gradient-boosted, quantile) temperature and vapour-pressure-deficit *offsets* carrying conformalised prediction intervals and an out-of-distribution flag; (2) microclimate → disease risk via a two-axis mechanistic model scaled by variety susceptibility; (3) growth + disease → crop viability by fuzzy limiting-factor aggregation; (4) viability → economics; (5) → 25-year discounted cash-flow (NPV, IRR, payback); and (6) → Monte-Carlo propagation to a profit distribution and probability of loss, wrapped by an inverse-design optimiser. Trained on real sub-canopy loggers from tropical Borneo and Mediterranean Spain plus a Borneo oil-palm regime (596 sites, 2,764 site-months), the learned offset is skilful within climate (full leave-one-site-out dT_mean MAE ≈ 0.41 °C, +49 % skill over a mean-offset baseline; calibrated coverage 0.76–0.82). A stricter leave-one-climate-out test, however, shows cross-macroclimate transfer fails (negative skill on a held-out climate; coverage collapsing to ~0.1–0.5), and a physics-prior hybrid does not rescue it; the model therefore flags the target — semi-arid, warm-night Tamil Nadu under an open coconut canopy — as out-of-distribution. We further show that ~5–25 in-regime calibration points restore interval coverage to near 0.80. Applied to a real farm in Anaikadu, a coconut overstorey with a black pepper intercrop is the temperature-robust, profitable pick (NPV ≈ ₹565k/acre, IRR ≈ 33 %, payback 7 yr, P(loss) ≈ 12 %), whereas nutmeg is viable only if a cooler microclimate is confirmed. The contribution is methodological: a transparent, uncertainty-propagating design→profit chain whose honest quantification of *where transfer breaks* is itself the result.

**Keywords:** agroforestry; microclimate; temperature offset; machine learning; transferability; conformal prediction; crop suitability; decision support; coconut; Tamil Nadu.

---

## Nomenclature

**Symbols**

| Symbol | Meaning | Unit |
|---|---|---|
| ΔX | microclimate offset, X_sub-canopy − X_ambient (X = T_max, T_mean or VPD) | — |
| dT_max, dT_mean | maximum- and mean-temperature offset | °C |
| dVPD | vapour-pressure-deficit offset | kPa |
| T_max, T_mean, T_min | mean daily max / mean / min air temperature | °C |
| VPD | vapour-pressure deficit | kPa |
| RH | relative humidity | % |
| I, I₀ | under-canopy and open-field light | fraction |
| k_ext | Beer–Lambert extinction coefficient | — |
| LAI | leaf area index | — |
| s_i, q̂_α | conformal nonconformity score; conformal offset at coverage 1−α | target units |
| n_cal | number of in-regime (few-shot) calibration points | — |
| M, m | number of Monte-Carlo draws; draw index | — |
| C_t | net cash flow in year t | ₹ acre⁻¹ yr⁻¹ |
| r | real discount rate (0.08) | yr⁻¹ |
| H | finance horizon (25 yr) | yr |
| NPV, IRR | net present value; internal rate of return | ₹ acre⁻¹; — |
| P(loss) | probability that NPV < 0 | — |

**Abbreviations**

CQR conformalised quantile regression · ERA5 ECMWF Reanalysis v5 · FAPAR fraction of absorbed PAR · GIS-MCDA GIS multi-criteria decision analysis · LOCO leave-one-climate-out · LOSO leave-one-site-out · LWD leaf-wetness duration · MAE mean absolute error · NDVI normalized difference vegetation index · OOD out-of-distribution · PI prediction interval · VPD vapour-pressure deficit.

---

## 1. Introduction

Smallholders and plantation planners deciding how to lay out an agroforestry system face a chain of coupled questions that existing tools answer only piecemeal: *if I plant this overstorey at this density, with this windbreak and this drainage, what microclimate will emerge under the canopy? which intercrops then become viable once disease pressure is accounted for? and will the result actually be profitable, with what risk?* Conventional crop-suitability and recommendation systems answer the first question with the **regional** climate — gridded temperature, rainfall and humidity — and stop there. But a managed canopy is a microclimate engine: it buffers temperature extremes, raises humidity, cuts wind, and reshapes leaf-wetness duration, and those shifts — not the regional average — decide both crop performance and disease establishment (De Frenne et al., 2019; De Frenne et al., 2021). Two farms with identical regional climates can therefore support very different crops.

### 1.1 Forest and agroforestry microclimate: the offset paradigm

A substantial body of forest-microclimate ecology has established that the **offset** between sub-canopy and free-air conditions is a coherent, learnable function of canopy structure, topography and macroclimate. De Frenne et al. (2019) compared understory and open-site temperatures at 98 sites across five continents and showed that canopies act as thermal insulators — cooling hot extremes and warming cold ones, with leaf area index a primary control — and later reviewed the drivers and research agenda for forest microclimates (De Frenne et al., 2021). Zellweger et al. (2019) set out how remote sensing of canopy structure and thermal conditions advances microclimate mapping, and the community-curated SoilTemp database (Lembrechts et al., 2020) now aggregates more than 7,500 near-surface sensors worldwide. Building on these, Haesen et al. (2021) operationalised the paradigm as **ForestTemp**, predicting the monthly sub-canopy temperature offset across Europe from ~1,200 in-situ series with boosted regression trees — the methodological precedent closest to the present work. In parallel, mechanistic microclimate models have matured: Maclean et al. (2019) released the *microclima* R package for meso- and microclimate, and Kearney and Porter (2017) the NicheMapR biophysical model, both deriving sub-canopy conditions from energy balance, terrain and vegetation.

The same buffering operates in managed canopies, which is what makes it agriculturally relevant. Hardwick et al. (2015) found tropical primary forest up to 6.5 °C cooler than adjacent oil-palm plantations, with leaf area index driving the difference. In agroforestry specifically, Blaser et al. (2018) showed that shade trees and pruning reshape throughfall and microclimate in cocoa systems; subsequent work found the buffering effect depends on shade-tree canopy height and species. Most directly analogous to our approach, coffee-agroforestry studies have estimated the under-canopy microclimate from full-sun weather data plus shade-tree characteristics — that is, they predict the agroforestry microclimate from the open-field climate and canopy structure, exactly the offset logic adopted here. What this literature does *not* do is treat the canopy as a set of **design variables a farmer controls** (species, spacing, pruning, windbreaks, drainage, fruiting time), nor chain the predicted microclimate to disease, crop viability and profit.

### 1.2 Crop suitability modelling

Crop-suitability assessment has moved from FAO ECOCROP-style envelope matching to GIS multi-criteria and machine-learning approaches. GIS-MCDA frameworks (e.g. AgriSuit) and ML classifiers — Random Forest and gradient boosting prominently — now dominate, with recent studies reporting high suitability-classification accuracy for staple crops (e.g. wheat and pearl millet in arid India) and global Random-Forest suitability surfaces for 17 crops at ~1 km resolution; ML suitability has also been applied to agroforestry (e.g. olive–maize land-suitability classification). These approaches, however, operate at *regional/landscape* scale on macroclimate and soil and therefore cannot represent the within-farm microclimate a chosen canopy creates — the gap this work targets.

### 1.3 Disease as a microclimate-driven layer

Plant pathology has long shown that foliar-disease establishment is governed by microclimate, especially **leaf-wetness duration (LWD)** and temperature. Operational disease-warning systems estimate LWD from weather and trigger management when infection conditions occur; empirical models using hours with relative humidity ≥ ~90 % (or small dew-point depression) predict LWD about as well as machine-learning models and are deployed for many crops. A microclimate predictor can thus be chained to disease risk through established, data-light infection models — yet crop-suitability tools rarely close this loop, despite disease often being the true determinant of whether a climatically-suitable crop is profitable (e.g. humidity- and rain-driven bacterial blight in pomegranate).

### 1.4 Uncertainty, transfer, and agricultural digital twins

As ecological and agricultural ML moves toward decision support, calibrated uncertainty and honest transfer have become central. Conformal prediction — and conformalised quantile regression in particular (Romano et al., 2019) — gives distribution-free, finite-sample prediction intervals around any model, and has been applied to crop-production decision support and earth-observation regression; group-conditional ("Mondrian") variants adapt coverage to subpopulations. Separately, **agricultural digital twins** have been proposed as integrative decision platforms (Pylianidis et al., 2021), and agroforestry-specific decision-support systems are emerging — though reviews note most "twins" remain monitoring/simulation tools rather than calibrated, validated models, and few quantify *when* their predictions cease to transfer.

### 1.5 Research gap and objectives

The individual pieces therefore exist — offset modelling, crop-suitability ML, microclimate-driven disease models, conformal uncertainty, and digital-twin framings — but they have **not been joined into a single, design-driven, uncertainty-propagated decision chain**, and the **transferability** of a microclimate model trained in one region to a different macroclimate has rarely been tested or reported honestly. The present work addresses this gap. Its objectives are to: (i) build an end-to-end pipeline mapping *controllable* agroforestry design to microclimate, disease risk, crop viability and risk-adjusted profit, with an explicit confidence level on every layer; (ii) confine machine learning to the variables that need it (temperature and VPD offsets), with conformal intervals and an out-of-distribution flag, while using mechanistic physics for light and wind; (iii) test transfer rigorously — within-site and, critically, **across macroclimates** — and report where it fails; and (iv) demonstrate the chain on a real smallholder site, propagating uncertainty to a planting decision. The integrating contribution is the chain

`Macroclimate + controllable design → microclimate offset → disease risk → crop viability → economics → risk-adjusted profit`,

end-to-end, with an explicit confidence level on every layer and uncertainty propagated to the decision (Fig. 2).

---

## 2. Materials and methods

The system is a chain of six layers (Fig. 2), each matched to the simplest method its physics and data support. Decomposition rather than one monolithic model is the central design decision: it lets mechanistic physics carry the variables it governs exactly, confines machine learning to the variables that genuinely need it, keeps every step interpretable, and lets uncertainty be attached and propagated layer by layer (Table 2).

### 2.1 Study site

The system is developed for and applied to a real farm at **Anaikadu (10.4019° N, 79.3545° E), Pattukkottai taluk, Thanjavur District, Tamil Nadu, India** — a hot semi-arid pocket of the Cauvery delta (Fig. 1). ERA5 (2019) at the plot gives a mean air temperature of 29.3 °C, mean daily maximum 34.3 °C, and — importantly — a mean daily **minimum of 25.9 °C** (warm nights), relative humidity ≈ 71 %, and ≈ 926 mm annual rainfall concentrated in the October–December north-east monsoon. SoilGrids indicates heavy alluvial clay (≈ 355 g kg⁻¹). Two site features shape the modelling. First, the warm-night, semi-arid regime is unlike the humid, cool-night forest sites in the training data — a transfer gap quantified in §3.2. Second, the humidity/disease-risk window is the NE-monsoon quarter while summers are hot and dry, which makes **fruiting-time (bahar) selection** as powerful a controllable lever as canopy or windbreaks. A practical caveat: a ~31 km ERA5 reanalysis pixel cannot resolve the village from the surrounding town, motivating on-plot sensing (§5).

### 2.2 Data sources and feature construction

Microclimate labels (offsets) come from three open sources spanning two macroclimates plus an open-canopy regime (Table 1): SAFE Project sub-canopy loggers in Sabah, Borneo, with coordinates from the SAFE Gazetteer; La Jarda, Cádiz, Spain, a Mediterranean forest network; and SAFE landscape microclimate rasters spanning forest → logged → oil-palm → cleared, which contribute the open-canopy regime (offsets up to +6.6 °C, matching Hardwick et al., 2015). The assembled dataset is **2,764 site-months over 596 sites**. Offsets are sub-canopy minus ambient (Eq. 1), with ambient taken as ERA5 **atmospheric** (free-air) rather than ERA5-Land, which over dense canopy is canopy-coupled and ~2–3 °C too cool. Predictor features are drawn from Google Earth Engine — ERA5/ERA5-Land macroclimate; MODIS LAI/FPAR/NDVI; ETH 10 m canopy height; Copernicus DEM (elevation, slope, derived topographic wetness); SoilGrids (clay, organic carbon) — and engineered into physically-motivated terms (canopy cover, radiation load, ambient VPD, diurnal range, structural interactions). Economics inputs are from NHB Detailed Project Reports, TNAU cost-of-cultivation, a Salem-District coconut study (2023–24), and live data.gov.in Agmarknet mandi prices. The training feature space and the target site's position in it are shown in Fig. 3.

**Table 1.** Data sources, regimes and roles in the pipeline.

| Source | Region / regime | Role | Sites / rows | Confidence |
|---|---|---|---|---|
| SAFE loggers + Gazetteer (Zenodo) | Borneo, humid tropical forest | offset labels | ~245 sites | high (in-situ) |
| La Jarda network (Zenodo) | Cádiz, Spain, Mediterranean | offset labels | ~276 plots (2-climate) | high (in-situ) |
| SAFE landscape rasters (Zenodo) | Borneo, forest→oil-palm | offset labels (open canopy) | 320 rows | moderate (modelled raster) |
| Google Earth Engine (ERA5, MODIS, ETH, DEM, SoilGrids) | global | predictor features | all sites | moderate |
| NHB / TNAU / Salem study / Agmarknet | India / Tamil Nadu | economics inputs | — | moderate |
| FAO ECOCROP / PROSEA | global | crop envelopes (headline crops) | — | moderate |

### 2.3 Model overview and confidence labelling

Every layer carries an explicit confidence level (Table 2): mechanistic physics is HIGH; learned offsets are MODERATE and flagged LOW when extrapolating; rule-based disease and staged economics are MODERATE; uncertainty is propagated rather than asserted.

**Table 2.** Model layers, methods and confidence labels.

| Layer | Method | Output | Validation / source | Confidence |
|---|---|---|---|---|
| 1 Microclimate (light, wind) | Beer–Lambert; shelterbelt aerodynamics | shade, in-field wind | mechanistic physics | HIGH |
| 1 Microclimate (T, VPD offset) | XGBoost quantile + CQR; OOD flag | dT_max, dT_mean, dVPD + intervals | LOSO / LOCO | MODERATE (LOW if OOD) |
| 2 Disease | mechanistic infection × variety susceptibility | foliar + soil-borne risk | literature-shaped | MODERATE |
| 3 Viability | fuzzy limiting-factor | growth × (1−disease) | agronomic envelopes | MODERATE |
| 4–5 Economics, finance | banded yield/price − cost; 25-yr DCF | NPV, IRR, payback | NHB/TNAU/Agmarknet | MODERATE (timber LOW) |
| 6 Uncertainty | Monte Carlo | NPV distribution, P(loss) | propagated | propagated |

### 2.4 Layer 1 — design → microclimate

We predict the **offset** from ambient macroclimate, not the raw under-canopy value, because the offset is the quantity that transfers across climates (De Frenne et al., 2019; Haesen et al., 2021):

`ΔX = X_sub-canopy − X_ambient`,  for X ∈ {T_max, T_mean, VPD}   (1)

*Light and wind (mechanistic, HIGH confidence).* Under-canopy light follows the Beer–Lambert law,

`I / I₀ = exp(−k_ext · LAI)`   (2)

with an extinction coefficient k_ext per overstorey. In-field wind reduction combines canopy drag with a perimeter-windbreak term whose average shelter is a Gaussian in porosity φ, peaking near 45 % (so a solid wall cannot "win") and gated by barrier height h:

`r_wb = 0.5 · exp[ −((φ − 0.45)/0.18)² ] · min(1, h/10)`   (3)

— standard shelterbelt aerodynamics. These need no training data.

*Temperature and VPD offsets (learned, MODERATE; OOD-flagged).* dT_max, dT_mean and dVPD are learned with **XGBoost quantile regressors** (`reg:quantileerror`; lower/median/upper quantiles) on the engineered features. Prediction intervals are calibrated by **conformalised quantile regression** (Romano et al., 2019) with a group-aware (whole-site) calibration split, so coverage reflects site-transfer error. The model stores its training feature ranges and exposes an **out-of-distribution score**,

`OOD(x) = (1/p) Σⱼ 1[ xⱼ < min_train,ⱼ  or  xⱼ > max_train,ⱼ ]`   (4)

(p = number of features), returning an `extrapolating` flag (OOD > 0.15) and an `offset_confidence` label, so a design unlike the training cloud (e.g. an open coconut canopy versus closed forest) is flagged LOW rather than silently extrapolated. For a hypothetical design, NDVI/FAPAR/canopy-height are not fabricated from LAI but set to **real regional satellite values** per canopy type (MODIS + ETH height over Tamil Nadu coconut/timber sites). Because tree models cannot extrapolate beyond their training range, we also implemented a physics-guided hybrid (an extrapolating Ridge backbone on the canopy-cover buffering term, clipped to the observed offset range, plus XGBoost on the residual), evaluated in §3.2.

### 2.5 Layer 2 — microclimate → disease risk

Disease risk follows the disease triangle, decomposed as

`realized_risk = environmental_pressure(microclimate) × variety_susceptibility`   (5)

across **two independent axes**. On the *foliar / air-microclimate* axis the temperature response is a beta function with cardinal temperatures (T_min, T_opt, T_max),

`g(T) = [(T_max − T)/(T_max − T_opt)] · [(T − T_min)/(T_opt − T_min)]^{(T_opt − T_min)/(T_max − T_opt)}`   (6)

(zero outside [T_min, T_max]), modulated by a leaf-wetness-duration proxy estimated from daily RH and rainfall,

`LWD = min{ 24,  12·max(0, (RH − 80)/20) + 1[rain>0]·min(8, 4 + 0.2·rain) }`  (h)   (7)

The *soil-water* axis for soil-borne pathogens is driven by effective waterlogging instead of air RH,

`effective_waterlogging = site_waterlogging × drainage_mitigation`   (8)

with the site term estimated from soil texture and depth-to-water-table d_wt,

`WLI = 0.5·min(1, clay/50) + 0.5·max(0, 1 − d_wt/3)`   (9)

(clay in %, d_wt in m). Variety susceptibility enters as an ordinal multiplier (R/MR/MS/S → 0.2/0.5/0.8/1.0) from published cultivar screening. The two controllable levers are explicit: fruiting-time (bahar) suppresses the foliar axis by avoiding the wet window; drainage suppresses the soil axis.

### 2.6 Layer 3 — viability

Growth fit is a fuzzy trapezoidal membership of each predicted microclimate variable against the crop's envelope, aggregated by the **limiting factor** (Liebig's law of the minimum). Viability combines growth and disease:

`viability = growth_fit × (1 − disease_risk)`   (10)

so a crop with ideal growth conditions but high disease pressure correctly collapses. Envelopes for the headline intercrops (black pepper, nutmeg) are sourced from FAO ECOCROP and PROSEA; the remaining crops use screening-grade extension values.

### 2.7 Layers 4–5 — economics and finance

These are staged, transparent and **not trained**. Attainable yield bends a reference yield by the pipeline's own suitability and disease outputs:

`attainable_yield = reference_yield × growth_fit × (1 − disease_risk)`   (11)

`crop_margin = attainable_yield × price − cost`   (12)

with banded mandi prices and costs validated against NHB DPRs and TNAU. Maintenance scales with a bearing ramp so juvenile years cost only a fraction f_juv = 0.3 of full upkeep,

`ramp(t) = 0  (t < gestation or t > life);  1  (t ≥ full);  (t − gestation + 1)/(full − gestation + 1)  otherwise`,   `maint(t) = maintain · max(f_juv, ramp(t))`   (13)

(charging full maintenance during gestation was a bug we caught by reality-checking against measured coconut economics — a validation-discipline illustration, §3.5). Overstorey income is modelled for coconut (annual nuts) and timber (annualised over rotation). A 25-year discounted cash-flow respects timing (gestation, bearing ramp, single-harvest timber):

`NPV = Σ_{t=1}^{H} C_t / (1 + r)^t`,   `0 = Σ_{t=1}^{H} C_t / (1 + IRR)^t`   (14, 15)

with r = 0.08 real and H = 25 yr.

### 2.8 Layer 6 — uncertainty and inverse design

Monte-Carlo (M = 2,000–3,000 draws) samples the genuinely uncertain inputs — the temperature-offset band, attainable yield, crop price, and overstorey bands — and pushes each draw through the same chain:

`NPV⁽ᵐ⁾ = f(offset⁽ᵐ⁾, yield⁽ᵐ⁾, price⁽ᵐ⁾, overstorey⁽ᵐ⁾)`   (16)

`P(loss) = (1/M) Σ_{m=1}^{M} 1[ NPV⁽ᵐ⁾ < 0 ]`   (17)

The inverse-design optimiser searches overstorey, canopy density (LAI), windbreak height/porosity and drainage to maximise a risk-aware objective,

`objective = 0.7 · E[system_margin] + 0.3 · system_margin_downside`   (18)

reusing layers 1–5 (the downside term is the low-band system margin, not a Monte-Carlo percentile).

### 2.9 Validation protocol

Because the central claim is transferability, we validate with two holdouts and report skill against a naive baseline (predict the training-mean offset),

`MAE = (1/n) Σᵢ |yᵢ − ŷᵢ|`,   `skill = 1 − MAE_model / MAE_baseline`   (19, 20)

the metric that distinguishes a learned signal from a near-constant offset: (a) **leave-one-site-out (LOSO)** — an entire site held out per fold (within-climate transfer); (b) **leave-one-climate-out (LOCO)** — an entire macroclimate / canopy regime held out (Borneo humid forest / Mediterranean Spain / Borneo oil-palm open canopy) — the honest test of cross-macroclimate transfer. Out-of-sample R² is reported only where the holdout makes it numerically stable (it is unreliable under single-site holdout, where within-site offset variance is near-zero). For out-of-climate calibration we recalibrate the conformal width on n_cal points drawn from the held-out climate, using the nonconformity score

`sᵢ = max( q_lo(xᵢ) − yᵢ ,  yᵢ − q_hi(xᵢ) )`,   `q̂_α = Quantile_{0.80}({sᵢ})`   (21, 22)

and the recalibrated interval `PI(x) = [ q_lo(x) − q̂_α , q_hi(x) + q̂_α ]`.

---

## 3. Results

### 3.1 Within-site transfer is skilful

Under full leave-one-site-out across all 596 sites, the learned offset is genuinely skilful, not a recovered constant (Table 3; Fig. 4). Skill over the mean-offset baseline is **+48.7 % for dT_mean** (MAE 0.41 °C), **+48.1 % for dT_max** (MAE 1.10 °C) and **+55.8 % for dVPD** (MAE 0.15 kPa); conformal interval coverage is calibrated near the 0.8 target (0.76–0.82). Absolute MAE is somewhat higher than a forest-only subset (a documented two-climate forest LOSO gives dT_mean 0.28 °C) precisely because the full test set includes the harder open oil-palm sites — yet the model's *skill* over baseline rises. We report skill rather than per-fold R², which is numerically unstable under single-site holdout. Canopy-structure interactions (cover × radiation, LAI × height, NDVI) dominate feature importance, recovering the physical expectation that canopy buffering is structure-driven.

**Table 3.** Full leave-one-site-out (596 sites). Skill is defined in Eq. (20).

| Target | MAE | Baseline MAE | Skill | Interval coverage |
|---|---|---|---|---|
| dT_max  | 1.10 °C | 2.11 °C | **+48.1 %** | 0.82 |
| dT_mean | 0.41 °C | 0.80 °C | **+48.7 %** | 0.76 |
| dVPD    | 0.15 kPa | 0.33 kPa | **+55.8 %** | 0.77 |

### 3.2 Cross-climate transfer and out-of-distribution behaviour

The stricter leave-one-climate-out test is the paper's pivotal result (Table 4; Fig. 5). Holding out an entire regime, transfer is **strong for the held-out humid forest** (dT_mean skill ≈ +22 %), **modest for the open oil-palm canopy**, and **fails for the held-out Mediterranean climate** (skill turns negative, ≈ −16 %), with prediction-interval coverage collapsing from ~0.8 (LOSO) to ~0.1–0.5 (LOCO). The offset's *magnitude* is regime-dependent: a model trained in one thermal regime mis-scales the buffering in a sufficiently different one. The physics-guided hybrid does **not** rescue this — it ties the pure tree in-distribution but is worse on the held-out cool climate, because its linear backbone, trained tropical, overshoots when extrapolated there. The limitation is therefore **data, not model**.

**Table 4.** Leave-one-climate-out transfer (held-out regime, dT_mean shown; full grid in Fig. 5).

| Held-out regime | dT_mean MAE | Skill | Coverage | Interpretation |
|---|---|---|---|---|
| Borneo humid forest | 0.51 °C | +22 % | 0.48 | transfers |
| Borneo oil-palm (open) | 1.65 °C | −19 % | 0.17 | weak |
| Mediterranean Spain | 2.26 °C | −16 % | 0.08 | fails |

Applied to Anaikadu, the coconut design is flagged **OOD (score ≈ 0.58, offset confidence LOW)** — and Fig. 3 shows why: the warm-night macroclimate and the sparse open palm canopy both lie outside the training cloud. Grounding the design features on real Tamil-Nadu satellite values left the flag essentially unchanged, confirming the extrapolation is genuine rather than an artefact of fabricated inputs.

### 3.3 Few-shot conformal recalibration

The out-of-climate coverage collapse is recoverable, and cheaply (Table 5; Fig. 6). Recalibrating the conformal width (Eqs. 21–22) on n_cal points drawn from the held-out climate, averaged over five seeds: at n_cal = 0 (the LOCO collapse) dT_mean coverage on the held-out Mediterranean climate is 0.08; with just **5–10 local points it returns to ~0.85–0.89 and stabilises near the 0.80 target by n_cal ≈ 25**, across all targets and climates. This is the quantitative case for the on-plot logger: the learned *point* prediction needs a full local season to retrain, but its *uncertainty* — the quantity that makes the tool honest — is restored by on the order of ten local measurements. It also shows the failure in §3.2 is one of calibration transfer, not a broken model.

**Table 5.** dT_mean interval coverage (target 0.80) under LOCO, recalibrated on n_cal points from the held-out climate.

| Held-out climate | n=0 | n=5 | n=10 | n=25 | n=50 |
|---|---|---|---|---|---|
| Borneo humid forest | 0.48 | 0.84 | 0.85 | 0.84 | 0.81 |
| Mediterranean Spain | 0.08 | 0.87 | 0.89 | 0.77 | 0.75 |
| Borneo oil-palm (open) | 0.17 | 0.84 | 0.89 | 0.83 | 0.78 |

### 3.4 Anaikadu case study: microclimate and crop ranking

Under a wide-spaced coconut overstorey the physics layer predicts ≈ 39 % shade and a modest in-field wind reduction (HIGH confidence; Fig. 7); the temperature/VPD offset is reported with its LOW-confidence flag. Scoring candidate intercrops against the ECOCROP/PROSEA-sourced envelopes (Fig. 8), all candidates are temperature-limited at this hot site. Sweeping the *uncertain* temperature offset across its full plausible band (Table 6) is revealing: **black pepper is the top intercrop at every point in the sweep** — its lead is robust to the temperature uncertainty — whereas **nutmeg leads only at the cool end** (offset −3 °C) and collapses at the central and warm estimates, because Anaikadu sits at the upper edge of nutmeg's flowering optimum (~32 °C). The model thus makes two distinct, differently-confident claims: pepper is the actionable pick now; nutmeg is conditionally viable, contingent on a cooler microclimate that on-plot sensing would confirm.

**Table 6.** Top-3 intercrop by viability as the (LOW-confidence) temperature offset is swept; under-canopy T_max in parentheses.

| Offset | T_max | Top 3 (viability) |
|---|---|---|
| −3 °C | 33.7 | Nutmeg 72 · Pepper 66 · Banana 63 |
| −1.5 °C | 35.2 | **Pepper 66** · Nutmeg 47 · Banana 47 |
| 0 (central) | 36.7 | **Pepper 50** · Nutmeg 22 · Banana 22 |
| +1.5 °C | 38.2 | **Pepper 31** · Nutmeg 0 · Banana 0 |
| +3 °C | 39.7 | **Pepper 7** · Nutmeg 0 · Banana 0 |

### 3.5 Economics, finance and risk

Converting viability to profit (Eqs. 11–17) turns "can the crop grow?" into "is the system worth planting under uncertainty?" (Table 7; Figs. 9–11). Over 25 years at an 8 % real hurdle, coconut + **black pepper** clears it decisively (NPV ≈ ₹565k/acre, IRR ≈ 33 %, payback 7 yr) with the **lowest probability of loss** among the intercrops (P(loss) ≈ 12 %); it is the strongest annual-cash system because it bears early, stays viable across the temperature band, and has lower loss probability than nutmeg. Coconut + nutmeg is marginal at the central estimate (NPV ≈ ₹127k, IRR ≈ 13 %, P(loss) ≈ 41 %) — its wide loss probability reflecting exactly the thermal-edge sensitivity of §3.4. Coconut alone is positive but modest (≈ ₹129k, P(loss) ≈ 3 %); banana under mature coconut is uneconomic. Timber overstoreys (mahogany, teak) show high *annualised* return but concentrate all risk in a single distant harvest at 15–18 yr and rest on LOW-confidence farm-gate prices. As a validation-discipline note, an early run mislabelled coconut monoculture as a guaranteed loss; the cause was full bearing-phase maintenance charged during the multi-year gestation, corrected by ramping maintenance with bearing and validating yields/prices against TNAU and the Salem study — an illustration that reality-checking model verdicts is part of the method.

**Table 7.** Anaikadu system finance and risk (25 yr, 8 % real).

| System | NPV (₹/ac) | IRR | Payback | P(loss) | Main limitation |
|---|---|---|---|---|---|
| Coconut + black pepper | ~565k | ~33 % | 7 yr | ~12 % | offset uncertainty (robust) |
| Coconut + nutmeg | ~127k | ~13 % | 11 yr | ~41 % | thermal-edge sensitivity |
| Coconut only | ~129k | ~17 % | 10 yr | ~3 % | nut-price volatility |
| Coconut + banana | negative | — | — | ~62 % | heat/shade-limited |
| Mahogany + nutmeg | ~1,091k | ~26 % | 13 yr | ~0 % | single distant harvest, LOW-conf price |
| Teak block | ~885k | ~31 % | 18 yr | ~0 % | long lock-up, LOW-conf price |

---

## 4. Discussion

The contribution is a **transparent, uncertainty-propagating chain from controllable farm design to risk-adjusted profit**, with two features under-served in agricultural decision tools. First, **disease is coupled to the engineered microclimate**, surfacing a genuine two-sided trade-off — the humidity, shade and shelter that favour shade-loving intercrops also favour foliar pathogens — that a one-axis suitability score misses, turning canopy/windbreak/bahar choices into a balance rather than a maximisation. Second, **uncertainty is first-class**: every layer is confidence-labelled, the learned layer is validated for transfer *and flagged when extrapolating*, and downstream economics propagate that uncertainty to a probability of loss instead of a single deceptive figure.

The negative transfer result deserves emphasis rather than burial. The forest-ecology offset paradigm transfers well *within* a climatic regime, consistent with ForestTemp's European success, but our leave-one-climate-out test shows it does not transfer to a sufficiently different macroclimate — and that a popular "add a physics prior" fix does not help when the prior itself is fit out-of-regime. For a decision tool this is the difference between honesty and harm: a system that confidently extrapolated the learned offset into warm-night Tamil Nadu would mislead exactly the user it is meant to serve. Building the OOD flag and reporting the coverage collapse converts an unfalsifiable claim into a falsifiable, improvable one — and the few-shot recalibration result shows the fix is small and local.

The practical upshot for the farm is clear. Where the science is mechanistic and regime-independent (light, wind), the predictions are trustworthy and decide the big structural choices; where it is learned and out-of-regime (the temperature/VPD offset), it is flagged and the decision is routed through a ranking shown to be robust to that uncertainty. The recommendation a planner can act on now is coconut + **black pepper**, with windbreak and dry-season bahar — adding nutmeg only if the cooler end of the microclimate is confirmed.

## 5. Limitations and future work

1. **Cross-macroclimate extrapolation.** The headline application is out-of-distribution on both macroclimate (warm-night semi-arid) and canopy type (open palm); the learned offset there is LOW-confidence by construction. The decisive remedy is **in-regime data**: a warm-night/dry-zone tropical training source (SoilTemp raw loggers; pan-tropical understory maps) and, definitively, **on-plot loggers** for one season — which would collapse the offset uncertainty and let the hybrid's backbone interpolate.
2. **Interval calibration out-of-climate.** Conformal coverage holds within climate but collapses across climates (§3.2); we show (§3.3) this is recoverable with ~5–25 calibration points from the target regime; full point-prediction accuracy in a new macroclimate still requires in-regime training data.
3. **Disease and suitability are mechanistic, not yet incidence-calibrated.** Leaf-wetness is a daily approximation; envelopes and variety ratings are screening-grade. Comparisons (wet vs dry timing, variety A vs B, design A vs B) are more reliable than absolute probabilities.
4. **Economics are MODERATE confidence**; timber prices LOW. A clean multi-year mandi price series and per-crop cost line items would firm them.
5. **"Suitable" ≠ "profitable and reliable."** The model predicts environmental viability; pests, pollination, labour and market depth enter only partially.

## 6. Conclusion

This work presents a confidence-labelled agroforestry design-to-profit framework linking controllable canopy and management decisions to microclimate offsets, disease risk, crop viability and risk-adjusted finance. Across 596 borrowed-label sites the learned offset model is skilful within observed regimes (leave-one-site-out dT_mean MAE ≈ 0.41 °C, +49 % skill), but strict leave-one-climate-out validation shows that cross-macroclimate transfer remains unresolved and that prediction intervals lose calibration out of regime. Rather than hiding this, the framework exposes it through out-of-distribution flags and propagated uncertainty, while few-shot conformal recalibration quantifies how a small number of local observations (≈ 5–25) restores interval honesty. Applied to Anaikadu, the physics-supported and sensitivity-robust result favours coconut with black pepper as the current actionable system, while nutmeg remains conditional on local sensing confirming a cooler under-canopy microclimate. The next decisive step is in-regime field data, which would turn this honest decision framework into a locally calibrated digital twin.

---

## Data and code availability

All code, build scripts and the architectural decision records are openly available in the project repository (a tagged release will accompany submission). The pipeline reproduces every figure and table from openly-sourced inputs: microclimate labels from Zenodo (refs 11–14); remote-sensing features via Google Earth Engine; economics from NHB DPRs, TNAU, a Salem-District study, and data.gov.in Agmarknet. Raw third-party data are not redistributed; the build scripts that fetch and assemble them are committed. An interactive version of all results is provided as a self-contained HTML report.

## Author contributions

L.A. conceived the study, developed the model and software, performed the analysis, and wrote the manuscript.

## Funding

This research received no external funding.

## Conflicts of interest

The author declares no competing financial interest. The study site is the author's prospective farm; the model's confidence labelling and pre-registered transfer tests are designed to keep that interest from biasing the reported conclusions.

## Acknowledgements

This work builds on openly-shared datasets from the SAFE Project (Sabah, Borneo), the La Jarda network (Cádiz, Spain), the SoilTemp initiative, and FAO ECOCROP, whose authors and contributors are gratefully acknowledged.

---

## References

*Bibliographic details verified June 2026 (PubMed for ecology refs 1–6; publisher records for 7–9). Dataset entries (11–14) are cited by Zenodo DOI; refs 17–21 are real, located sources whose full author lists/DOIs should be finalised from the publisher record. Final formatting to the target journal's author–date style is a copy-edit step.*

1. De Frenne, P., Zellweger, F., Rodríguez-Sánchez, F., Scheffers, B. R., Hylander, K., Luoto, M., Vellend, M., Verheyen, K., & Lenoir, J. (2019). Global buffering of temperatures under forest canopies. *Nature Ecology & Evolution*, 3(5), 744–749. https://doi.org/10.1038/s41559-019-0842-1
2. De Frenne, P., Lenoir, J., Luoto, M., Scheffers, B. R., Zellweger, F., Aalto, J., … Hylander, K. (2021). Forest microclimates and climate change: Importance, drivers and future research agenda. *Global Change Biology*, 27(11), 2279–2297. https://doi.org/10.1111/gcb.15569
3. Haesen, S., Lembrechts, J. J., De Frenne, P., Lenoir, J., Aalto, J., Ashcroft, M. B., … Van Meerbeek, K. (2021). ForestTemp – Sub-canopy microclimate temperatures of European forests. *Global Change Biology*, 27(23), 6307–6319. https://doi.org/10.1111/gcb.15892
4. Lembrechts, J. J., Aalto, J., Ashcroft, M. B., De Frenne, P., Kopecký, M., Lenoir, J., … Nijs, I. (2020). SoilTemp: A global database of near-surface temperature. *Global Change Biology*, 26(11), 6616–6629. https://doi.org/10.1111/gcb.15123
5. Zellweger, F., De Frenne, P., Lenoir, J., Rocchini, D., & Coomes, D. (2019). Advances in microclimate ecology arising from remote sensing. *Trends in Ecology & Evolution*, 34(4), 327–341. https://doi.org/10.1016/j.tree.2018.12.012
6. Hardwick, S. R., Toumi, R., Pfeifer, M., Turner, E. C., Nilus, R., & Ewers, R. M. (2015). The relationship between leaf area index and microclimate in tropical forest and oil palm plantation. *Agricultural and Forest Meteorology*, 201, 187–195. https://doi.org/10.1016/j.agrformet.2014.11.010
7. Pylianidis, C., Osinga, S., & Athanasiadis, I. N. (2021). Introducing digital twins to agriculture. *Computers and Electronics in Agriculture*, 184, 105942. https://doi.org/10.1016/j.compag.2020.105942
8. Romano, Y., Patterson, E., & Candès, E. J. (2019). Conformalized quantile regression. *Advances in Neural Information Processing Systems (NeurIPS)*, 32, 3538–3548. https://doi.org/10.48550/arXiv.1905.03222
9. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16)*, 785–794. https://doi.org/10.1145/2939672.2939785
10. FAO. *ECOCROP — Crop environmental requirements database*. Food and Agriculture Organization of the United Nations, Rome. https://gaez.fao.org/pages/ecocrop *(online database; accessed 2026)*
11. [dataset] SAFE Project — Forest microclimate (1st-order sites), Sabah, Borneo. Zenodo. https://doi.org/10.5281/zenodo.1228188
12. [dataset] SAFE Project gazetteer of site locations. Zenodo. https://doi.org/10.5281/zenodo.3906082
13. [dataset] SAFE landscape sub-canopy microclimate rasters, Borneo. Zenodo. https://doi.org/10.5281/zenodo.7893600
14. [dataset] La Jarda microclimate time series, Cádiz, Spain. Zenodo. https://doi.org/10.5281/zenodo.18913503
15. Maclean, I. M. D., Mosedale, J. R., & Bennie, J. J. (2019). Microclima: An R package for modelling meso- and microclimate. *Methods in Ecology and Evolution*, 10(2), 280–290. https://doi.org/10.1111/2041-210X.13093
16. Kearney, M. R., & Porter, W. P. (2017). NicheMapR — an R package for biophysical modelling: the microclimate model. *Ecography*, 40(5), 664–674. https://doi.org/10.1111/ecog.02360
17. Blaser, W. J., Oppong, J., Yeboah, E., & Six, J. (2018). Shade trees and tree pruning alter throughfall and microclimate in cocoa production systems. *(DOI to confirm: 10.1007/s13595-018-0723-9)*
18. Coffee-agroforestry microclimate estimation from full-sun weather data and shade-tree characteristics. *European Journal of Agronomy* (2021). *(author list + DOI to confirm)*
19. GIS-based cropland suitability prediction using machine learning. *Agronomy*, 12(9), 2210 (2022). https://doi.org/10.3390/agronomy12092210 *(confirm authors)*
20. Conformal prediction for uncertainty quantification in crop-production decision support. *Computers and Electronics in Agriculture* (2025). *(author list + DOI to confirm)*
21. Global Random-Forest crop-suitability surfaces for 17 crops. *Scientific Data* (2024). *(author list + DOI to confirm)*

---

## Figure captions

- **Figure 1.** Study site and training regimes. The offset model is trained on tropical Borneo (forest and oil-palm) and Mediterranean Spain, then applied to the warm-night semi-arid Anaikadu site in Tamil Nadu; the thermal-regime bars show Anaikadu's warm-night gap. (`figures/fig_sitemap.png`)
- **Figure 2.** Six-layer methods schematic: controllable design → microclimate → disease → viability → economics → finance → Monte-Carlo profit, with per-layer confidence and the inverse-design loop. (`figures/fig0_pipeline.png`)
- **Figure 3.** Training feature-space coverage and target extrapolation. Anaikadu lies outside the observed macroclimate range (warm nights) and the coconut canopy outside the observed structure range, so the temperature/VPD offset is flagged out-of-distribution. (`figures/fig_featurespace.png`)
- **Figure 4.** Leave-one-site-out validation error for the temperature and VPD offsets (within-climate transfer). (`figures/fig1_transfer.png`)
- **Figure 5.** Leave-one-climate-out transfer: skill vs baseline (left) and interval coverage (right) by held-out regime and target. Transfer degrades and coverage collapses out-of-climate. (`figures/fig_loco.png`)
- **Figure 6.** Few-shot conformal recalibration: a small number of in-regime calibration points restores dT_mean interval coverage toward the 0.80 target after the leave-one-climate-out collapse. (`figures/fig_fewshot.png`)
- **Figure 7.** Predicted under-canopy microclimate by candidate overstorey at Anaikadu; shade/wind HIGH confidence, temperature/VPD offset flagged LOW (out-of-distribution). (`figures/fig2_microclimate.png`)
- **Figure 8.** Crop thermal envelopes against the predicted Anaikadu under-coconut temperature sweep. Black pepper's envelope overlaps the full plausible range more robustly than nutmeg's. (`figures/fig_envelope.png`)
- **Figure 9.** System economics: NPV/IRR by overstorey × intercrop combination. (`figures/fig4_economics.png`)
- **Figure 10.** Monte-Carlo 25-year NPV distributions and probability of loss per system. (`figures/fig5_montecarlo.png`)
- **Figure 11.** Cash-flow timing: steady annual spice income versus a single distant timber harvest. (`figures/fig6_cashflow.png`)

*Tables 1–7 appear inline in their respective sections.*
