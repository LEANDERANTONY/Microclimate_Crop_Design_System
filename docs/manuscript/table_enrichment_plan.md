# Table enrichment plan for the manuscript

Purpose: assess whether the manuscript has enough tables and suggest additional tables that would strengthen the paper without making it feel cluttered. This is only a planning guide; the Word manuscript is not changed.

## Current Table Inventory

The manuscript currently has three inline tables:

| Current table | Section | What it shows | Verdict |
|---|---|---|---|
| Table 1 | Section 5 | Full LOSO validation: MAE, baseline MAE, skill and coverage for `dT_max`, `dT_mean`, `dVPD` | Keep. This is essential. |
| Table 2 | Section 6.1 | Few-shot/Mondrian coverage recovery for `dT_mean` across held-out climates | Keep, but also convert to a figure if possible. |
| Table 3 | Section 7 | Top-3 intercrops under temperature-offset sensitivity sweep | Keep, or convert to a crop-sensitivity heatmap. |

Short answer: **three tables are not quite enough** for a methods-heavy paper like this. The existing tables show results, but the paper also needs tables that make the data, assumptions, and confidence levels auditable.

## Recommended Main-Paper Tables

### Table 1 - Data sources and label construction

Suggested placement: `Section 4. Data`

Why add it:

The data section currently compresses a lot into prose: SAFE loggers, La Jarda, SAFE oil-palm rasters, Earth Engine features, economics sources. A reviewer will want to see exactly what is measured, what is modelled, and what is only a reference layer.

Suggested columns:

| Column | Description |
|---|---|
| Source | SAFE first-order loggers, La Jarda, SAFE oil-palm rasters, Earth Engine, economics sources |
| Region / regime | Borneo humid forest, Mediterranean Spain, Borneo open oil-palm, Tamil Nadu application |
| Role in pipeline | Target labels, remote-sensing features, regional reference, economics input |
| Observations / sites | Rows and site count where applicable |
| Variables used | Temperature, RH/VPD, LAI, NDVI, FAPAR, canopy height, etc. |
| Label type | Raw logger, modelled raster, remote-sensing feature, economic source |
| Confidence | High / moderate / low |

Recommended status: **Add to main paper**.

### Table 2 - Layer methods and confidence labels

Suggested placement: `Section 3. Methods`, after the pipeline figure.

Why add it:

The paper’s whole philosophy is confidence-labelled modelling. Right now that philosophy is described well, but a table would make it sharper and easier to review.

Suggested columns:

| Column | Description |
|---|---|
| Layer | Microclimate, disease, viability, economics, finance, uncertainty |
| Input | What enters the layer |
| Method | Physics, XGBoost quantile, fuzzy membership, cash-flow, Monte Carlo |
| Output | What the layer returns |
| Validation / source | LOSO, LOCO, literature, DPR/TNAU, propagated uncertainty |
| Confidence | High / moderate / low / propagated |

Recommended status: **Add to main paper**.

### Table 3 - Existing LOSO validation table

Suggested placement: `Section 5`

What to change:

- Keep the current table.
- Once equations are added, replace the caption formula with "Skill is defined in Eq. (16)."
- Consider adding an extra column for `target coverage = 0.80` or `coverage gap`.

Recommended status: **Keep in main paper**.

### Table 4 - LOCO transfer by held-out regime

Suggested placement: `Section 6`

Why add it:

Right now the LOCO result is mostly prose. This is arguably the most important scientific result in the paper, so it should have either a table or a heatmap figure. Ideally both: a compact table in the paper and a richer figure.

Suggested columns:

| Column | Description |
|---|---|
| Held-out regime | Borneo forest, Mediterranean Spain, Borneo oil-palm open |
| Target | `dT_max`, `dT_mean`, `dVPD` |
| MAE | Model error |
| Baseline MAE | Naive baseline |
| Skill | Improvement over baseline |
| Coverage | Interval coverage |
| Interpretation | Transfers / weak / fails |

Recommended status: **Add to main paper or convert into a LOCO heatmap figure**.

### Table 5 - Existing few-shot coverage table

Suggested placement: `Section 6.1`

What to change:

- Keep current Table 2 if there is room.
- But the better main-paper presentation is a recovery curve figure, with the table moved to supplement.

Recommended status: **Keep if the journal allows enough tables; otherwise move to supplement after making a figure**.

### Table 6 - Crop envelope and source confidence

Suggested placement: `Section 7` or supplement.

Why add it:

The crop recommendation depends on envelope assumptions. The manuscript says pepper and nutmeg are sourced from ECOCROP/PROSEA, but readers may want to see the actual values behind the ranking.

Suggested columns:

| Column | Description |
|---|---|
| Crop | Black pepper, nutmeg, banana, cocoa, vanilla, ginger, pomegranate |
| Temperature optimum | Ideal range |
| Temperature tolerance | Absolute range |
| Shade range | Ideal or tolerated shade |
| RH/VPD preference | Where available |
| Main risk | Foot rot, thermal edge, shade, disease, market |
| Source | ECOCROP, PROSEA, extension/literature |
| Confidence | High / moderate / screening |

Recommended status: **Add to main paper if crop recommendation is central; otherwise supplement**.

### Table 7 - Existing temperature sensitivity top-crop table

Suggested placement: `Section 7`

What to change:

- Current Table 3 is good because it directly supports the pepper-vs-nutmeg claim.
- If a crop envelope/sensitivity heatmap is added, this table can stay as a compact numerical companion.

Recommended status: **Keep in main paper**.

### Table 8 - Finance summary by system

Suggested placement: `Section 7`, after economics paragraph.

Why add it:

The paper reports NPV, IRR, payback, and P(loss) in prose. A table would make the farm decision easier to audit.

Suggested columns:

| Column | Description |
|---|---|
| System | Coconut only, coconut + pepper, coconut + nutmeg, coconut + banana, timber options |
| NPV | 25-year NPV |
| IRR | Internal rate of return |
| Payback | Years |
| P(loss) | Monte Carlo loss probability |
| Main limitation | Thermal edge, price risk, long harvest lock-up, etc. |
| Confidence | Moderate / low |

Recommended status: **Add to main paper or supplement depending on figure count**.

## Recommended Supplementary Tables

### Supplementary Table S1 - Full feature list

Placement: Supplement.

Suggested columns:

- Feature name
- Source
- Unit
- Used in model?
- Description
- Notes on scaling

Why:

Useful for reproducibility, but too detailed for the main paper.

### Supplementary Table S2 - Disease parameter table

Placement: Supplement.

Suggested columns:

- Crop
- Disease
- Disease axis
- Temperature range / optimum
- Wetness or RH threshold
- Rain-driven?
- Variety susceptibility source
- Confidence

Why:

The disease layer is important but literature-shaped. A supplementary table prevents overloading the main text while keeping it transparent.

### Supplementary Table S3 - Economics input table

Placement: Supplement.

Suggested columns:

- Crop/system
- Reference yield
- Price band
- Establishment cost
- Maintenance cost
- Gestation
- Source
- Confidence

Why:

Reviewers may ask where the economics numbers came from. This table answers that without crowding the main paper.

### Supplementary Table S4 - Full LOCO and hybrid comparison

Placement: Supplement, unless the LOCO figure is not added.

Suggested columns:

- Model
- Held-out regime
- Target
- MAE
- Baseline MAE
- Skill
- R2 if stable
- Coverage
- Interval width

Why:

Important for the method claim, but too large for the main paper if fully expanded.

### Supplementary Table S5 - Monte Carlo input distributions

Placement: Supplement.

Suggested columns:

- Variable
- Distribution / sampling rule
- Low
- Central
- High
- Source
- Confidence

Why:

This makes uncertainty propagation auditable.

## Suggested Final Main-Paper Table Set

If the journal allows around 5-6 tables, use this:

| Proposed table | Title | Section |
|---|---|---|
| Table 1 | Data sources, regimes and roles in the pipeline | Section 4 |
| Table 2 | Model layers, methods and confidence labels | Section 3 |
| Table 3 | Leave-one-site-out validation performance | Section 5 |
| Table 4 | Leave-one-climate-out transfer performance | Section 6 |
| Table 5 | Few-shot conformal recalibration coverage | Section 6.1 |
| Table 6 | Anaikadu system finance and risk summary | Section 7 |

Then move crop envelopes, disease parameters, full economics inputs, feature list and full hybrid ablation to supplement.

## Lean Main-Paper Version

If the journal prefers fewer tables, use only four:

| Proposed table | Title | Section |
|---|---|---|
| Table 1 | Data sources and regimes | Section 4 |
| Table 2 | Layer methods and confidence | Section 3 |
| Table 3 | Validation summary: LOSO and LOCO | Sections 5-6 |
| Table 4 | Anaikadu crop/system decision summary | Section 7 |

In this version:

- Existing few-shot Table 2 becomes a figure.
- Existing temperature-sweep Table 3 becomes either a heatmap figure or part of the decision summary table.
- Full details move to supplement.

## My Recommendation

The current three tables are **not enough** for the story we are telling. They show results, but they do not sufficiently expose the machinery and assumptions. I would add at least:

1. Data sources/regimes table.
2. Layer methods/confidence table.
3. LOCO transfer table or heatmap.
4. Finance/risk summary table.

That would give the manuscript a more mature research-paper feel and make the claims easier to audit.

## Avoid These Tables

- Do not add a huge crop catalogue table to the main manuscript; keep it supplemental.
- Do not add a raw feature-correlation table unless a reviewer asks.
- Do not duplicate a figure and a table if they say exactly the same thing; use the table for precise numbers and the figure for the pattern.
- Do not include too many finance tables in the main paper, because the core contribution is still microclimate transfer and uncertainty.
