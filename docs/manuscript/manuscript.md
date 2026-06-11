# From canopy design to crop profit under uncertainty: an honesty-first agroforestry microclimate model with explicit transfer limits, applied to a smallholder coconut farm in Tamil Nadu

**Leo Antony**
Independent research · Anaikadu (Pattukkottai), Thanjavur District, Tamil Nadu, India

*Manuscript draft — v0.2, June 2026. All numbers trace to the committed pipeline (`scripts/export_results.py` → `reports/results.json`; transfer metrics `reports/loso_full_metrics.json`, `reports/loco_metrics.json`, `reports/mondrian_metrics.json`). References verified (DOIs in §References). Pre-submission manual steps remaining: confirm Zenodo depositor names on each dataset "Cite as" line; export Figs 1–6 at journal DPI.*

---

## Highlights

- A six-layer model chains agroforestry **design → microclimate → disease → crop viability → profit** under propagated uncertainty.
- Canopy temperature/VPD offsets are learned (gradient-boosted, quantile) with conformal intervals and an out-of-distribution flag.
- Offsets transfer **within** climate (leave-one-site-out skill +49 %) but **fail across** macroclimates (leave-one-climate-out skill negative).
- ~5–25 local calibration points restore out-of-climate interval coverage from 0.08 to ~0.80 — quantifying the value of on-plot sensing.
- For a real Tamil Nadu farm, coconut + black pepper is the robust, profitable pick; the model flags rather than over-claims its extrapolations.

---

## Abstract

Conventional crop-recommendation tools use *regional* climate, yet an agroforestry system creates its **own** microclimate, and that microclimate — not the regional average — governs which crops are viable, what diseases take hold, and whether the planting pays. We present an end-to-end, **honesty-first** decision pipeline that chains six layers: (1) design → microclimate, combining mechanistic physics (Beer–Lambert light, shelterbelt wind) with machine-learned (gradient-boosted, quantile) temperature and vapour-pressure-deficit *offsets* carrying conformalised prediction intervals; (2) microclimate → disease risk via a two-axis mechanistic model (foliar air-microclimate and soil-water/waterlogging) scaled by variety susceptibility; (3) growth + disease → crop viability by fuzzy limiting-factor aggregation; (4) viability → economics (yield × suitability × (1−disease) × banded price − validated cost); (5) → 25-year discounted cash-flow (NPV/IRR/payback respecting gestation and harvest timing); and (6) → Monte-Carlo propagation to a profit distribution and probability of loss. An inverse-design optimiser searches the controllable design (overstorey, canopy density, windbreak, drainage) for the risk-aware profit optimum.

Trained on real sub-canopy loggers from tropical Borneo (SAFE) and Mediterranean Spain (La Jarda) plus Borneo oil-palm rasters (596 sites, 2,764 site-months), the learned offset is **genuinely skilful within climate** — full leave-one-site-out dT_mean MAE ≈ 0.41 °C, **+49 % skill** over a mean-offset baseline (dT_max +48 %, dVPD +56 %), with calibrated intervals (coverage 0.76–0.82). Critically, a stricter **leave-one-climate-out** test shows transfer **fails across macroclimates**: skill turns negative on a held-out Mediterranean climate and interval coverage collapses to ~0.1–0.5; a physics-prior + ML-residual hybrid was tested and did **not** rescue it. The model therefore **flags** the target application — semi-arid, warm-night Tamil Nadu under an open coconut canopy — as out-of-distribution rather than over-claiming. Applied to a real farm in Anaikadu, the physics-grounded shade/wind layer and a temperature-robust crop ranking identify a defensible plan: a coconut overstorey with a **black pepper** intercrop — whose lead is stable across the entire plausible temperature band — clears an 8 % real hurdle (NPV ≈ ₹565k/acre, IRR ≈ 33 %, payback 7 yr, P(loss) ≈ 12 %), whereas nutmeg, sitting at its thermal optimum's edge, is viable only if the cooler end of the uncertain offset holds — itself a decision-relevant finding. The central contribution is methodological: a transparent, uncertainty-propagating design→profit chain whose honest quantification of *where transfer breaks* is itself the result, and which converts a planting decision into a set of confidence-labelled, falsifiable predictions.

**Keywords:** agroforestry; microclimate; temperature offset; machine learning; transferability; conformal prediction; crop suitability; decision support; coconut; Tamil Nadu.

---

## 1. Introduction

Smallholders and plantation planners deciding how to lay out an agroforestry system face a chain of coupled questions that existing tools answer only piecemeal: *if I plant this overstorey at this density, with this windbreak and this drainage, what microclimate will emerge under the canopy? which intercrops then become viable once disease pressure is accounted for? and will the result actually be profitable, with what risk?* Conventional crop-suitability and recommendation systems answer the first question with the **regional** climate — gridded temperature, rainfall and humidity — and stop there. But a managed canopy is a microclimate engine: it buffers temperature extremes, raises humidity, cuts wind, and reshapes leaf-wetness duration, and those shifts — not the regional average — decide both crop performance and disease establishment (De Frenne et al., 2019; De Frenne et al., 2021 **[verify]**). Two farms with identical regional climates can therefore support very different crops.

Three literatures bear on this problem but have not been joined. First, **forest microclimate ecology** has established that the *offset* between sub-canopy and free-air temperature is a learnable, mappable function of canopy structure, topography and macroclimate: De Frenne et al. (2019) showed canopies buffer extremes across 98 sites on five continents with leaf area index a primary control, and Haesen et al. (2021) operationalised this as **ForestTemp**, a machine-learning model predicting the monthly sub-canopy temperature offset across Europe from ~1,200 in-situ series. Second, **crop-suitability mapping** matches crops to climate envelopes (e.g. FAO ECOCROP **[verify]**) but at regional scale, ignoring within-farm canopy modification. Third, **agricultural digital twins** have been proposed as integrative decision tools, though reviews note most existing systems are monitoring/simulation platforms rather than mature, calibrated twins (Pylianidis et al., 2021 **[verify]**).

The offset-modelling paradigm from forest ecology is precisely the right tool for the agroforestry-design question — but it has been applied to *natural* forests, where canopy structure is observed, not to *managed* agroforestry, where spacing, species, pruning, windbreaks and drainage are **design variables a farmer controls**. Nor has it been chained downstream to disease, economics and a profit decision. This work makes that combination its contribution:

> **Macroclimate + controllable farm design → microclimate offset → disease risk → crop viability → economics → risk-adjusted profit**, end-to-end, with an explicit confidence level on every layer and uncertainty propagated to the final decision.

Our second, equally deliberate contribution is **methodological honesty about transfer.** Because the intended application — semi-arid, warm-night Tamil Nadu under an open coconut canopy — is a different macroclimate *and* canopy type from any available training data, we treat transferability not as an assumption but as a hypothesis to be tested and, where it fails, reported. We show that within-climate transfer is skilful but **cross-macroclimate transfer fails**, and we build the model to flag that extrapolation rather than silently produce a confident-looking number. We argue this is the responsible posture for decision-support tools built on borrowed data, and that the *negative* transfer result is a useful contribution in its own right.

## 2. Study site

The system is developed for and applied to a real farm at **Anaikadu (10.4019° N, 79.3545° E), Pattukkottai taluk, Thanjavur District, Tamil Nadu, India** — a hot semi-arid pocket of the Cauvery delta. ERA5 (2019) at the plot gives a mean air temperature of 29.3 °C, mean daily maximum 34.3 °C, and — importantly — a mean daily **minimum of 25.9 °C** (warm nights), relative humidity ≈ 71 %, and ≈ 926 mm annual rainfall concentrated in the October–December north-east monsoon. SoilGrids indicates heavy alluvial clay (≈ 355 g kg⁻¹). Two site features shape the modelling. First, the warm-night, semi-arid regime is unlike the humid, cool-night forest sites in the training data — a transfer gap quantified in §6. Second, the humidity/disease-risk window is the NE-monsoon quarter while summers are hot and dry, which makes **fruiting-time (bahar) selection** as powerful a controllable lever as canopy or windbreaks. A practical caveat throughout: a ~31 km ERA5 reanalysis pixel cannot resolve the village from the surrounding town, motivating on-plot sensing (§9).

## 3. Methods

The system is a chain of six layers (Fig. 0), each matched to the simplest method its physics and data support. Decomposition rather than one monolithic model is the central design decision: it lets mechanistic physics carry the variables it governs exactly, confines machine learning to the variables that genuinely need it, keeps every step interpretable to a farmer, and lets uncertainty be attached and propagated layer by layer.

### 3.1 Layer 1 — design → microclimate

We predict the **offset** from ambient macroclimate, not the raw under-canopy value, because the offset is the quantity that transfers across climates (De Frenne et al., 2019; Haesen et al., 2021).

*Light and wind (mechanistic, HIGH confidence).* Under-canopy light is the Beer–Lambert fraction `I/I₀ = exp(−k·LAI)`, with an extinction coefficient `k` per overstorey. In-field wind reduction combines canopy drag with a perimeter-windbreak term that peaks at ~45 % porosity (a Gaussian in porosity, so a solid wall cannot "win") and saturates with barrier height — standard shelterbelt aerodynamics. These need no training data and are HIGH confidence.

*Temperature and VPD offsets (learned, MODERATE; OOD-flagged).* The maximum- and mean-temperature offsets (dT_max, dT_mean) and the VPD offset (dVPD) are learned with **XGBoost quantile regressors** (`reg:quantileerror`, lower/median/upper quantiles) on physically-motivated features: canopy cover and structure (LAI, height, NDVI, FAPAR, and their interactions), radiation load, ambient VPD, diurnal range, terrain (elevation, slope, topographic wetness) and soil (clay, organic carbon). Prediction intervals are calibrated by **conformalised quantile regression** (Romano et al., 2019 **[verify]**) with a **group-aware** calibration split (whole sites held out for calibration) so coverage reflects site-transfer error. The model stores its training feature ranges and exposes an **out-of-distribution (OOD) score** — the fraction of a query design's features outside the training range — and returns an `extrapolating` flag and an `offset_confidence` label, so a design unlike the training cloud (e.g. an open coconut canopy versus closed forest) is flagged LOW rather than silently extrapolated.

*Grounded design→feature mapping.* For a hypothetical design, NDVI/FAPAR/canopy-height are not fabricated from LAI but set to **real regional satellite values** per canopy type (MODIS LAI/FPAR/NDVI + ETH canopy height, 2020, sampled over Tamil Nadu coconut-belt and timber sites), so the learned model is fed realistic inputs.

*A tested hybrid.* Because tree models cannot extrapolate beyond their training range (they predict the boundary, flat), we also implemented a **physics-guided hybrid**: an extrapolating linear (Ridge) backbone on the canopy-cover buffering term, clipped to the observed offset range, plus XGBoost on the residual. We evaluate it against the pure model in §6.

### 3.2 Layer 2 — microclimate → disease risk

Disease risk follows the disease triangle, decomposed as `realized_risk = environmental_pressure(microclimate) × variety_susceptibility`. Environmental pressure is computed by mechanistic infection models — **no incidence data required** — along **two independent axes**: a *foliar / air-microclimate* axis (a temperature beta-response × leaf-wetness-duration or relative-humidity term, with a rain-splash modifier) and a *soil-water* axis for soil-borne pathogens (wilt, foot rot), driven by effective **waterlogging** = site waterlogging × a drainage-mitigation multiplier (a design lever) — explicitly *not* air humidity. Leaf-wetness duration is estimated from daily RH and rainfall (a deliberately crude, LOW-confidence first approximation). Variety susceptibility enters as an ordinal multiplier (R/MR/MS/S → 0.2/0.5/0.8/1.0) from published cultivar screening, with a conservative default where unscreened. This makes the two controllable levers explicit: fruiting-time (bahar) suppresses the foliar axis by avoiding the wet window; drainage suppresses the soil axis.

### 3.3 Layer 3 — viability

Growth fit is a fuzzy trapezoidal membership of each predicted microclimate variable against the crop's envelope, aggregated by the **limiting factor** (Liebig's law of the minimum — the worst-matched variable sinks the crop, never a compensating average). Viability = growth × (1 − disease risk), so a crop with ideal growth conditions but high disease pressure correctly collapses. Envelopes for the two headline intercrops (black pepper, nutmeg) are sourced from FAO ECOCROP and PROSEA (`reports/crop_envelopes_ecocrop.md`); the remaining crops use screening-grade extension values, flagged for later tightening.

### 3.4 Layers 4–5 — economics and finance

These are **staged, transparent, and not trained**. Attainable yield = reference yield (TNAU/ICAR/NHB) × growth × (1 − disease). Margins use banded mandi prices (live data.gov.in Agmarknet) minus costs validated against NHB Detailed Project Reports and Tamil Nadu district studies. Overstorey income is modelled for coconut (annual nut income) and timber (teak/mahogany/silver-oak, annualised over rotation). A 25-year discounted cash-flow (8 % real default) respects timing — gestation, bearing ramp, coconut annual income, timber single-harvest lump — yielding NPV, IRR (bisection) and payback. Maintenance scales with the bearing ramp (juvenile years cost a fraction of full upkeep); charging full maintenance during gestation was a bug we caught by reality-checking against measured coconut economics and report as a validation-discipline illustration (§7).

### 3.5 Layer 6 — uncertainty, and inverse design

Monte-Carlo (n = 2,000–3,000) samples the genuinely uncertain inputs — the temperature-offset band, attainable yield, crop price, and overstorey (nut price; timber volume/price) bands — and pushes each draw through the same chain to an NPV **distribution** with P10/P50/P90, mean and probability of loss. The inverse-design optimiser searches overstorey, canopy density (LAI), windbreak height/porosity and drainage to maximise a risk-aware objective (0.7 × expected + 0.3 × downside), reusing layers 1–5.

### 3.6 Validation protocol

Because the central claim is transferability, we validate with two holdouts and report skill against a naive baseline (predict the training-mean offset; skill = 1 − MAE/MAE_baseline), the metric that distinguishes a learned signal from a near-constant offset: (a) **leave-one-site-out (LOSO)** — an entire site held out per fold (within-climate transfer); (b) **leave-one-climate-out (LOCO)** — an entire macroclimate / canopy regime held out (Borneo humid forest / Mediterranean Spain / Borneo oil-palm open canopy) — the honest test of cross-macroclimate transfer and of the leap to Tamil Nadu. We report out-of-sample R² only where the holdout makes it numerically stable (it is unreliable under single-site holdout, where within-site offset variance is near-zero; §5).

## 4. Data

*Microclimate labels (offsets).* SAFE Project sub-canopy loggers, Sabah, Borneo (Zenodo 1228188) with plot coordinates from the SAFE Gazetteer (Zenodo 3906082); La Jarda, Cádiz, Spain, a Mediterranean forest network (Zenodo 18913503); and SAFE landscape microclimate rasters spanning forest → logged → oil-palm → cleared (Zenodo 7893600), which contribute the open-canopy regime (offsets up to +6.6 °C, matching Hardwick et al., 2015 **[verify]**). The assembled dataset is **2,764 site-months over 596 sites** across two macroclimates plus the open-canopy regime. Offsets are sub-canopy minus ambient, with ambient taken as ERA5 **atmospheric** (free-air) rather than ERA5-Land, which over dense canopy is canopy-coupled and ~2–3 °C too cool.

*Features (Google Earth Engine).* ERA5/ERA5-Land macroclimate; MODIS LAI/FPAR/NDVI; ETH 10 m canopy height; Copernicus DEM (elevation, slope, derived topographic wetness); SoilGrids (clay, organic carbon).

*Economics.* NHB Detailed Project Reports, TNAU cost-of-cultivation, a Salem-District coconut study (2023–24), and live data.gov.in Agmarknet mandi prices.

*Crop envelopes, diseases, varieties.* Horticultural/extension references and cultivar-screening literature; flagged for tightening against FAO ECOCROP and local trial data.

## 5. Result — within-climate transfer is skilful

Under full leave-one-site-out across all 596 sites (every site held out once), the learned offset is genuinely skilful, not a recovered constant (Table 1). Skill over the mean-offset baseline is **+48.7 % for dT_mean** (MAE 0.41 °C), **+48.1 % for dT_max** (MAE 1.10 °C) and **+55.8 % for dVPD** (MAE 0.15 kPa); conformal interval coverage is calibrated near the 0.8 target (0.76–0.82). Absolute MAE is somewhat higher than a forest-only subset (e.g. a documented two-climate forest LOSO gives dT_mean 0.28 °C) precisely because the full test set includes the harder open oil-palm sites — yet the model's *skill* over baseline rises, the more honest indicator of learned value. We report skill rather than out-of-sample R²: under single-site holdout the within-site offset variance is near-zero for some sites, making per-fold R² numerically unstable (a known artefact), whereas MAE-based skill is robust. Canopy-structure interactions (cover × radiation, LAI × height, NDVI) dominate feature importance, recovering the physical expectation that canopy buffering is structure-driven.

**Table 1.** Full leave-one-site-out (596 sites). Skill = 1 − MAE/MAE_baseline (baseline = predict the training-mean offset).

| Target | MAE | Baseline MAE | Skill | Interval coverage |
|---|---|---|---|---|
| dT_max  | 1.10 °C | 2.11 °C | **+48.1 %** | 0.82 |
| dT_mean | 0.41 °C | 0.80 °C | **+48.7 %** | 0.76 |
| dVPD    | 0.15 kPa | 0.33 kPa | **+55.8 %** | 0.77 |

## 6. Result — cross-macroclimate transfer fails, and the model says so

The stricter leave-one-climate-out test is the paper's pivotal result. Holding out an entire regime, transfer is **strong for the held-out humid forest** (dT_mean skill ≈ +22 %), **modest for the open oil-palm canopy**, and **fails for the held-out Mediterranean climate** (skill turns **negative**, ≈ −16 %), with prediction-interval coverage collapsing from ~0.8 (LOSO) to ~0.1–0.5 (LOCO). The offset's *magnitude* is regime-dependent: a model trained in one thermal regime mis-scales the buffering in a sufficiently different one.

The physics-guided hybrid does **not** rescue this. It ties the pure tree in-distribution (and marginally improves dT_mean on the held-out forest) but is **worse** on the held-out cool climate, because its linear backbone, trained tropical, overshoots when extrapolated there — even clipped to the observed offset range. The lesson is consequential for practice: the limitation is **data, not model** — the value of a physics-prior hybrid is unlocked only by training data *in the target regime* (so the backbone interpolates), not by architecture alone.

Applied to Anaikadu, these results are not hidden but operationalised. The coconut design is flagged **OOD (score ≈ 0.58, offset confidence LOW)**; grounding the design features on real Tamil-Nadu satellite values left the flag essentially unchanged, confirming the extrapolation is **genuine** (a real canopy-and-climate novelty) rather than an artefact of fabricated inputs. The learned temperature offset under coconut is therefore reported as LOW-confidence; the decision leans on the HIGH-confidence physics (shade, wind) and on a ranking shown to be robust to the temperature uncertainty (§7).

### 6.1 A handful of local observations restores calibrated intervals

The out-of-climate coverage collapse is recoverable — and cheaply. We recalibrate the conformal interval width on *k* points drawn from the held-out climate (a proxy for *k* on-plot sensor readings) and measure coverage on the remainder, averaged over five seeds (Table 2). At *k* = 0 (the LOCO collapse) dT_mean coverage on the held-out Mediterranean climate is 0.08; with just **5–10 local points it returns to ~0.85–0.89 and stabilises near the 0.80 target by k ≈ 25**, and the same pattern holds across all three targets and all held-out climates. This is the quantitative case for the on-plot logger: the learned *point* prediction needs a full local season to retrain, but its *uncertainty* — the quantity that makes the tool honest — is restored by on the order of ten local measurements. It also shows the failure in §6 is one of calibration transfer, not a broken model.

**Table 2.** dT_mean interval coverage (target 0.80) under leave-one-climate-out, recalibrated on *k* points from the held-out climate.

| Held-out climate | k=0 | k=5 | k=10 | k=25 | k=50 |
|---|---|---|---|---|---|
| Borneo humid forest | 0.48 | 0.84 | 0.85 | 0.84 | 0.81 |
| Mediterranean Spain | 0.08 | 0.87 | 0.89 | 0.77 | 0.75 |
| Borneo oil-palm (open) | 0.17 | 0.84 | 0.89 | 0.83 | 0.78 |

## 7. Result — application to Anaikadu (physics + robust ranking carry the decision)

*Microclimate.* Under a wide-spaced coconut overstorey the physics layer predicts ≈ 39 % shade and a modest in-field wind reduction (HIGH confidence); the temperature/VPD offset is reported with its LOW-confidence flag.

*Suitability and its robustness.* Scoring candidate intercrops under coconut against the ECOCROP/PROSEA-sourced envelopes (§3.3, headline-crop sourcing in `reports/crop_envelopes_ecocrop.md`), all candidates are temperature-limited at this hot site. Sweeping the *uncertain* temperature offset across its full plausible band (Table 3) is revealing: **black pepper is the top intercrop at every point in the sweep** — its lead is robust to the temperature uncertainty — whereas **nutmeg leads only at the cool end** (offset −3 °C) and collapses at the central and warm estimates, because Anaikadu sits at the upper edge of nutmeg's flowering optimum (~32 °C). So the model makes two distinct claims with different confidence: *pepper is the actionable pick now*; *nutmeg is conditionally viable, contingent on the cooler microclimate actually materialising* — precisely the question on-plot sensing would resolve.

**Table 3.** Top-3 intercrop by viability as the (LOW-confidence) temperature offset is swept; under-canopy T_max in parentheses.

| Offset | T_max | Top 3 (viability) |
|---|---|---|
| −3 °C | 33.7 | Nutmeg 72 · Pepper 66 · Banana 63 |
| −1.5 °C | 35.2 | **Pepper 66** · Nutmeg 47 · Banana 47 |
| 0 (central) | 36.7 | **Pepper 50** · Nutmeg 22 · Banana 22 |
| +1.5 °C | 38.2 | **Pepper 31** · Nutmeg 0 · Banana 0 |
| +3 °C | 39.7 | **Pepper 7** · Nutmeg 0 · Banana 0 |

*Economics, finance, risk.* Over 25 years at an 8 % real hurdle: coconut + **black pepper** clears it decisively with **NPV ≈ ₹565k/acre, IRR ≈ 33 %, payback 7 yr** and the lowest probability of loss among the intercrops (**P(loss) ≈ 12 %**); coconut + nutmeg is marginal at the central estimate (NPV ≈ ₹127k, IRR ≈ 13 %, P(loss) ≈ 41 %) — its wide loss probability reflecting exactly the thermal-edge sensitivity above; coconut alone is positive but modest (≈ ₹129k, P(loss) ≈ 3 %); banana under mature coconut is uneconomic (heat- and shade-limited). Timber overstoreys (mahogany, teak) show high *annualised* return but concentrate all risk in a single distant harvest at 15–18 yr and rest on LOW-confidence farm-gate prices.

*A validation-discipline note.* An early model run mislabelled coconut monoculture as a guaranteed loss, contradicting reality. The cause was full bearing-phase maintenance charged during the multi-year gestation (plus a stale nut-price band); fixing maintenance to ramp with bearing, and validating nut yields/prices against TNAU and the Salem study, corrected it. We report this as an illustration that reality-checking model verdicts is part of the method.

## 8. Discussion

The contribution is a **transparent, uncertainty-propagating chain from controllable farm design to risk-adjusted profit**, with two features we believe are under-served in agricultural decision tools. First, **disease is coupled to the engineered microclimate**, surfacing a genuine two-sided trade-off — the humidity, shade and shelter that favour shade-loving intercrops also favour foliar pathogens — that a one-axis suitability score misses, and that turns canopy/windbreak/bahar choices into a balance rather than a maximisation. Second, **uncertainty is first-class**: every layer is confidence-labelled, the learned layer is validated for transfer *and flagged when extrapolating*, and downstream economics propagate that uncertainty to a probability of loss instead of a single deceptive figure.

The negative transfer result deserves emphasis rather than burial. The forest-ecology offset paradigm transfers well *within* a climatic regime, consistent with ForestTemp's European success, but our leave-one-climate-out test shows it does not transfer to a sufficiently different macroclimate — and that a popular "add a physics prior" fix does not help when the prior itself is fit out-of-regime. For a decision tool this is the difference between honesty and harm: a system that confidently extrapolated the learned offset into warm-night Tamil Nadu would mislead exactly the user it is meant to serve. Building the OOD flag and reporting the coverage collapse converts an unfalsifiable claim into a falsifiable, improvable one.

The practical upshot for the farm is also clear. Where the science is mechanistic and regime-independent (light via Beer–Lambert, wind via shelterbelt theory), the predictions are trustworthy and decide the big structural choices; where it is learned and out-of-regime (the temperature/VPD offset), it is flagged and the decision is deliberately routed through a ranking shown to be robust to that uncertainty. The result is a recommendation a planner can act on now (coconut + **black pepper**, with windbreak and dry-season bahar — adding nutmeg only if the cooler end of the microclimate is confirmed) while knowing precisely which number a season of local data would sharpen.

## 9. Limitations and future work

1. **Cross-macroclimate extrapolation.** The headline application is out-of-distribution on both macroclimate (warm-night semi-arid) and canopy type (open palm); the learned offset there is LOW-confidence by construction. The decisive remedy is **in-regime data**: a warm-night/dry-zone tropical training source (SoilTemp raw loggers; pan-tropical understory maps) and, definitively, **on-plot loggers** for one season spanning the hot months and the NE monsoon — which would both collapse the offset uncertainty and let the hybrid's backbone interpolate rather than extrapolate.
2. **Interval calibration out-of-climate.** Conformal coverage holds within climate but collapses across climates (§6). We show (§6.1) this is recoverable with ~5–25 calibration points from the target regime; full *point*-prediction accuracy in a new macroclimate still requires in-regime training data, not just calibration points.
3. **Disease and suitability are mechanistic, not yet incidence-calibrated.** Leaf-wetness is a daily approximation; envelopes and variety ratings are screening-grade. Comparisons (wet vs dry timing, variety A vs B, design A vs B) are more reliable than absolute probabilities.
4. **Economics are MODERATE confidence**; timber prices LOW. A clean multi-year mandi price series and per-crop cost line items would firm them.
5. **"Suitable" ≠ "profitable and reliable."** The model predicts environmental viability; pests, pollination, labour and market depth enter only partially (via disease and banded marketability) and warrant dedicated treatment.

## 10. Reproducibility

The pipeline is an installable package (`src/agroforestry/`: physics, models, predict, suitability, disease, economics, finance, monte_carlo, optimize, validation), environment-pinned with `uv`. Every reported figure traces to a committed script (`scripts/export_results.py` → `reports/results.json`; `scripts/run_validation.py` → `reports/loso_metrics.json`, `reports/loco_metrics.json`; `scripts/mondrian_conformal.py` → `reports/mondrian_metrics.json`; `scripts/make_figures.py` and `scripts/make_pipeline_figure.py`; `scripts/build_dashboard.py` → an interactive report). Design decisions are logged as architectural decision records (ADR-001–013). Data are openly sourced (Zenodo, Google Earth Engine, NHB/TNAU/Agmarknet); raw files are git-ignored with build scripts committed. Tests: 26 passing.

## References

*Bibliographic details verified June 2026 (PubMed for the ecology references 1–6; publisher records for 7–9). Dataset entries are cited by Zenodo DOI; confirm exact depositor names against each record's "Cite as" field before submission.*

1. De Frenne, P., Zellweger, F., Rodríguez-Sánchez, F., Scheffers, B. R., Hylander, K., Luoto, M., Vellend, M., Verheyen, K., & Lenoir, J. (2019). Global buffering of temperatures under forest canopies. *Nature Ecology & Evolution*, 3(5), 744–749. https://doi.org/10.1038/s41559-019-0842-1
2. De Frenne, P., Lenoir, J., Luoto, M., Scheffers, B. R., Zellweger, F., Aalto, J., … Hylander, K. (2021). Forest microclimates and climate change: Importance, drivers and future research agenda. *Global Change Biology*, 27(11), 2279–2297. https://doi.org/10.1111/gcb.15569
3. Haesen, S., Lembrechts, J. J., De Frenne, P., Lenoir, J., Aalto, J., Ashcroft, M. B., … Van Meerbeek, K. (2021). ForestTemp – Sub-canopy microclimate temperatures of European forests. *Global Change Biology*, 27(23), 6307–6319. https://doi.org/10.1111/gcb.15892
4. Lembrechts, J. J., Aalto, J., Ashcroft, M. B., De Frenne, P., Kopecký, M., Lenoir, J., … Nijs, I. (2020). SoilTemp: A global database of near-surface temperature. *Global Change Biology*, 26(11), 6616–6629. https://doi.org/10.1111/gcb.15123
5. Zellweger, F., De Frenne, P., Lenoir, J., Rocchini, D., & Coomes, D. (2019). Advances in microclimate ecology arising from remote sensing. *Trends in Ecology & Evolution*, 34(4), 327–341. https://doi.org/10.1016/j.tree.2018.12.012
6. Hardwick, S. R., Toumi, R., Pfeifer, M., Turner, E. C., Nilus, R., & Ewers, R. M. (2015). The relationship between leaf area index and microclimate in tropical forest and oil palm plantation: Forest disturbance drives changes in microclimate. *Agricultural and Forest Meteorology*, 201, 187–195. https://doi.org/10.1016/j.agrformet.2014.11.010
7. Pylianidis, C., Osinga, S., & Athanasiadis, I. N. (2021). Introducing digital twins to agriculture. *Computers and Electronics in Agriculture*, 184, 105942. https://doi.org/10.1016/j.compag.2020.105942
8. Romano, Y., Patterson, E., & Candès, E. J. (2019). Conformalized quantile regression. *Advances in Neural Information Processing Systems (NeurIPS)*, 32, 3538–3548. arXiv:1905.03222. https://doi.org/10.48550/arXiv.1905.03222
9. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16)*, 785–794. https://doi.org/10.1145/2939672.2939785
10. FAO. *ECOCROP — Crop environmental requirements database*. Food and Agriculture Organization of the United Nations, Rome. https://gaez.fao.org/pages/ecocrop *(online database; accessed 2026)*
11. [dataset] SAFE Project — Forest microclimate (1st-order sites), Sabah, Borneo. Zenodo. https://doi.org/10.5281/zenodo.1228188
12. [dataset] SAFE Project gazetteer of site locations. Zenodo. https://doi.org/10.5281/zenodo.3906082
13. [dataset] SAFE landscape sub-canopy microclimate rasters (forest → logged → oil palm → cleared), Borneo. Zenodo. https://doi.org/10.5281/zenodo.7893600
14. [dataset] La Jarda microclimate time series, Cádiz, Spain (Mediterranean). Zenodo. https://doi.org/10.5281/zenodo.18913503

## Data and code availability

All code, build scripts and the architectural decision records are openly available in the project repository (a tagged release will accompany submission). The pipeline reproduces every figure and table from openly-sourced inputs: microclimate labels from Zenodo (refs 11–14); remote-sensing features via Google Earth Engine (ERA5, MODIS, ETH canopy height, Copernicus DEM, SoilGrids); economics from NHB Detailed Project Reports, TNAU cost-of-cultivation, a Salem-District study, and data.gov.in Agmarknet. Raw third-party data are not redistributed; the build scripts that fetch and assemble them are committed. An interactive version of all results is provided as a self-contained HTML report (`reports/anaikadu_preprint.html`).

## Author contributions

L.A. conceived the study, developed the model and software, performed the analysis, and wrote the manuscript.

## Funding

This research received no external funding.

## Conflicts of interest

The author declares no conflict of interest. The study site is the author's prospective farm; the model's confidence labelling and pre-registered transfer tests are designed precisely to keep that interest from biasing the reported conclusions.

## Acknowledgements

This work builds on openly-shared datasets from the SAFE Project (Sabah, Borneo), the La Jarda network (Cádiz, Spain), the SoilTemp initiative, and FAO ECOCROP, whose authors and contributors are gratefully acknowledged.

---

## Figure captions

- **Figure 0.** Methods schematic: the six-layer pipeline from controllable farm design (overstorey, spacing/LAI, windbreak, drainage, variety, timing) through microclimate, disease, viability, economics and finance to a Monte-Carlo profit distribution, with each layer's confidence level (HIGH physics / MODERATE learned / propagated) and the inverse-design loop. (`figures/fig0_pipeline.png`)
- **Figure 1.** Cross-climate transfer: leave-one-site-out error for the temperature and VPD offsets, trained on Borneo (SAFE) + Mediterranean Spain (La Jarda). (`figures/fig1_transfer.png`)
- **Figure 2.** Predicted under-canopy microclimate (shade, temperature, humidity, wind) for candidate overstoreys at Anaikadu; shade/wind HIGH confidence, temperature/VPD offset flagged LOW (out-of-distribution). (`figures/fig2_microclimate.png`)
- **Figure 3.** Intercrop viability under coconut and its sensitivity to the uncertain temperature offset (black pepper leads across the whole band; nutmeg only at the cool end). (`figures/fig3_suitability.png`)
- **Figure 4.** System economics: NPV/IRR by overstorey × intercrop combination. (`figures/fig4_economics.png`)
- **Figure 5.** Monte-Carlo 25-year NPV distributions and probability of loss per system. (`figures/fig5_montecarlo.png`)
- **Figure 6.** Cash-flow timing: steady annual spice income versus a single distant timber harvest. (`figures/fig6_cashflow.png`)

*Tables 1–3 appear inline in §5, §6.1 and §7 respectively.*
