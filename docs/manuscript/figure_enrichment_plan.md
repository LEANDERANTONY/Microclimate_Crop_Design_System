# Figure enrichment plan for the manuscript

Purpose: suggest additional figures, graphs and visual panels that can make the agroforestry manuscript feel richer and more publication-ready, using the style logic of the earlier published solar-air-heater paper: visualise the system, validate the model, show parameter sweeps, and then show final performance. This is only a planning guide; the Word file is not changed.

## Current Visual Inventory

Current manuscript figures:

| Current figure | File | Role | Keep? | Notes |
|---|---|---|---|---|
| Fig. 0 | `figures/fig0_pipeline.png` | Six-layer methods schematic | Yes | Strong overview figure; should stay near Methods. |
| Fig. 1 | `figures/fig1_transfer.png` | Cross-climate / transfer performance | Yes, upgrade | Important but currently compact; should become a richer validation figure. |
| Fig. 2 | `figures/fig2_microclimate.png` | Predicted microclimate by overstorey at Anaikadu | Yes, upgrade | Good application figure; should show confidence/OOD more visually. |
| Fig. 3 | `figures/fig3_suitability.png` | Suitability and temperature sensitivity | Yes | Central farm decision figure. |
| Fig. 4 | `figures/fig4_economics.png` | NPV/IRR by system | Yes | Useful final decision graphic. |
| Fig. 5 | `figures/fig5_montecarlo.png` | NPV uncertainty distributions | Yes | Important because uncertainty is a headline contribution. |
| Fig. 6 | `figures/fig6_cashflow.png` | Cash-flow timing | Yes | Nice practical visual; keep. |

Current inline tables:

| Current table | Section | Role | Keep? | Notes |
|---|---|---|---|---|
| Table 1 | Section 5 | Full LOSO skill and coverage | Yes | Could be paired with a richer diagnostic figure. |
| Table 2 | Section 6.1 | Few-shot/Mondrian coverage recovery | Yes | Strong result; should probably become a figure too. |
| Table 3 | Section 7 | Temperature-offset sensitivity top crops | Yes | Could remain a table, or become a compact heatmap. |

Current figure-resolution note:

- `fig1_transfer.png`, `fig2_microclimate.png`, `fig4_economics.png`, `fig5_montecarlo.png`, and `fig6_cashflow.png` are currently modest-resolution PNGs. Before submission, regenerate them at journal DPI and preferably at larger canvas size.

## Main Recommendation

The paper already has the right figure categories, but it lacks the richer "evidence chain" that your published simulation paper had: geometry/context, validation, mechanism, parameter sweeps, and final performance. For this paper, the equivalent visual richness should come from:

1. A study-site and data-regime map.
2. A training-data feature-space / OOD plot.
3. A proper LOCO validation figure.
4. A few-shot conformal recovery figure.
5. A design-lever response surface.
6. A final decision matrix / risk-return plot.

These additions would make the paper look less like a dashboard export and more like a complete research article.

## Proposed New Figures

### New Fig. 1 - Study-site and training-data map

Suggested placement: end of `Section 2. Study site`, before Methods.

What it should show:

- Anaikadu / Pattukkottai application point.
- SAFE Borneo training region.
- La Jarda Spain training region.
- SAFE oil-palm/open-canopy raster region.
- Optional inset map of Tamil Nadu / Cauvery delta.

Why add it:

This gives readers immediate spatial intuition. It also visually supports the transfer argument: the target site is geographically and climatically distant from the training regimes.

Possible panels:

- Panel A: world map with Borneo, Spain, and South India.
- Panel B: Tamil Nadu inset with Anaikadu point.
- Panel C: small climate summary bars for each regime: `T_mean`, `T_min`, rainfall, RH.

Data source:

- Site coordinates already in manuscript and data scripts.
- Climate summaries from `reports/results.json`, `reports/loso_metrics.json`, `reports/loco_metrics.json`, and regional-reference outputs.

Caption idea:

`Study site and training regimes. The learned offset model is trained on tropical Borneo, Mediterranean Spain and an open-canopy Borneo oil-palm regime, then applied to the warm-night semi-arid Anaikadu site in Tamil Nadu.`

Priority: **Very high**.

### New Fig. 2 - Climate and canopy feature-space coverage

Suggested placement: `Section 4. Data` or early `Section 6`.

What it should show:

- Scatter/embedding of training rows and Anaikadu design points.
- Axes can be simple and interpretable:
  - `t_mean` vs `t_min`
  - `LAI` vs canopy height
  - `NDVI` vs `t_mean`
- Anaikadu/coconut points highlighted in a different marker.

Why add it:

This is probably the most scientifically important missing visual. The manuscript says Anaikadu is OOD; this figure would let the reader see it.

Possible panels:

- Panel A: macroclimate space: `t_mean` vs `t_min`.
- Panel B: canopy structure space: `LAI` vs canopy height.
- Panel C: OOD score bars for candidate overstoreys.

Data source:

- `data/processed/labelled_offsets.parquet` for training rows.
- `reports/results.json` for Anaikadu candidate designs.
- `reports/canopy_features_tn.json` for grounded canopy features.

Caption idea:

`Training feature-space coverage and target extrapolation. Anaikadu lies outside the observed macroclimate range of the borrowed-label data, while coconut also occupies a sparse open-canopy feature regime; the model therefore flags the temperature/VPD offset as low-confidence.`

Priority: **Very high**.

### New Fig. 3 - Full validation diagnostic figure

Suggested placement: `Section 5. Result - within-climate transfer is skilful`.

What it should show:

- Observed vs predicted offsets for `dT_max`, `dT_mean`, `dVPD`.
- Error distribution by target.
- Skill vs baseline by target.
- Coverage vs target coverage line.

Why add it:

Table 1 is good, but a validation paper needs visual evidence. Your earlier simulation paper had grid independence, model selection and validation figures; this is our equivalent.

Possible panels:

- Panel A: predicted vs observed `dT_mean`.
- Panel B: predicted vs observed `dT_max`.
- Panel C: predicted vs observed `dVPD`.
- Panel D: bar chart of skill and coverage.

Data source:

- Output can be generated from `scripts/run_validation.py`, or by extending it to save fold predictions.
- If fold predictions are not currently saved, add a small script to produce them.

Caption idea:

`Leave-one-site-out validation. The offset model improves over a mean-offset baseline across all three targets and maintains near-target conformal coverage, showing that it learns canopy- and context-linked offset structure within observed regimes.`

Priority: **High**.

### New Fig. 4 - Leave-one-climate-out failure figure

Suggested placement: `Section 6. Result - cross-macroclimate transfer fails`.

What it should show:

- LOCO skill by held-out regime and target.
- Interval coverage by held-out regime and target.
- Optional comparison of pure XGBoost vs physics-prior hybrid.

Why add it:

This is the paper's most important scientific result. Right now it is described in prose. It deserves its own strong figure.

Possible panels:

- Panel A: heatmap of skill, rows = held-out regime, columns = targets.
- Panel B: heatmap of interval coverage.
- Panel C: grouped bars comparing pure model vs hybrid.

Data source:

- `reports/loco_metrics.json`.

Caption idea:

`Leave-one-climate-out transfer. Performance degrades when an entire macroclimate/canopy regime is held out; interval coverage collapses out-of-climate, and the physics-prior hybrid does not remove the macroclimate-transfer failure.`

Priority: **Very high**.

### New Fig. 5 - Few-shot/Mondrian conformal recovery curve

Suggested placement: `Section 6.1 A handful of local observations restores calibrated intervals`.

What it should show:

- Coverage vs number of calibration points `k`.
- Separate lines for held-out regimes.
- Horizontal line at target coverage `0.80`.
- Possibly include interval width in a second panel.

Why add it:

Table 2 is powerful, but the recovery curve will be more intuitive and persuasive. This is one of the cleanest "new science" figures in the paper.

Possible panels:

- Panel A: `dT_mean` coverage vs `k`.
- Panel B: all targets or average coverage vs `k`.
- Panel C: average interval width vs `k`.

Data source:

- `reports/mondrian_metrics.json`.

Caption idea:

`Few-shot conformal recalibration. A small number of in-regime calibration points restores interval coverage close to the 0.80 target after leave-one-climate-out coverage collapse, quantifying the value of local sensing.`

Priority: **Very high**.

### New Fig. 6 - Mechanistic design levers: shade and wind

Suggested placement: `Section 3.1` after Beer-Lambert and shelterbelt descriptions, or `Section 7` before the Anaikadu crop ranking.

What it should show:

- Beer-Lambert light transmission vs LAI for coconut/timber overstoreys.
- Wind reduction vs windbreak porosity, showing optimum near 0.45.
- Optional wind reduction vs windbreak height.

Why add it:

This visually separates the high-confidence physics from the low-confidence learned offset. It also makes the design levers feel concrete.

Possible panels:

- Panel A: light transmitted vs LAI.
- Panel B: windbreak effect vs porosity.
- Panel C: candidate overstorey shade ranges.

Data source:

- `src/agroforestry/physics.py`.
- `src/agroforestry/config.py` species/canopy values.

Caption idea:

`Mechanistic design levers. Light and wind are computed from physics rather than learned from borrowed labels, making them the highest-confidence components of the design model.`

Priority: **High**.

### New Fig. 7 - Crop envelope overlay against predicted microclimate

Suggested placement: `Section 7`, before or alongside existing Fig. 3.

What it should show:

- Crop ideal/tolerable temperature bands for pepper, nutmeg, banana, cocoa, vanilla.
- Anaikadu under-coconut temperature uncertainty band overlaid.
- Optional shade bands and predicted shade.

Why add it:

This figure would make the pepper-vs-nutmeg story obvious at a glance. Readers can see why pepper remains viable over more of the hot band, while nutmeg is thermal-edge conditional.

Possible panels:

- Panel A: temperature envelope bars with predicted `T_max` sweep.
- Panel B: shade envelope bars with coconut shade.
- Panel C: wind tolerance vs predicted wind after windbreak.

Data source:

- `src/agroforestry/config.py`.
- `reports/crop_envelopes_ecocrop.md`.
- `reports/results.json`.

Caption idea:

`Crop envelopes against the predicted Anaikadu microclimate. Black pepper's thermal envelope overlaps the full plausible under-coconut temperature range more robustly than nutmeg's, explaining the temperature-sweep ranking.`

Priority: **High**.

### New Fig. 8 - Design-lever response surface / sensitivity heatmap

Suggested placement: `Section 7`, after crop envelope overlay or before economics.

What it should show:

- Viability or risk-aware NPV as a function of two controllable variables:
  - coconut LAI/canopy density vs windbreak porosity
  - canopy density vs temperature offset
  - drainage level vs fruiting season for disease-prone crops

Why add it:

Your published paper uses many parameter sweeps. This is our equivalent: show how changing the design changes the outcome.

Best candidate:

- Pepper viability or NPV heatmap across `canopy density` and `temperature offset`.
- Nutmeg viability heatmap across the same axes as a contrast.

Data source:

- Existing suitability/finance functions.
- Could be generated by extending `scripts/sensitivity_coconut.py`.

Caption idea:

`Design sensitivity under coconut. Black pepper remains the leading intercrop across a broad canopy-temperature range, whereas nutmeg depends strongly on the cooler end of the under-canopy temperature offset.`

Priority: **Medium-high**.

### New Fig. 9 - Risk-return decision plot

Suggested placement: `Section 7`, after economics and Monte Carlo figures.

What it should show:

- X-axis: expected NPV or median NPV.
- Y-axis: probability of loss.
- Point size: payback period or capital lock-up.
- Color: overstorey type.

Why add it:

This turns finance into a decision figure. It is more compact than reading NPV, IRR, P(loss), and payback across prose.

Data source:

- `reports/results.json`.

Caption idea:

`Risk-return comparison of candidate systems. Coconut + pepper occupies the desirable quadrant of high NPV and moderate-to-low loss probability, while nutmeg carries higher downside risk and timber concentrates return in a distant harvest.`

Priority: **Medium-high**.

### New Fig. 10 - Data and reproducibility workflow

Suggested placement: `Section 10. Reproducibility`, optional.

What it should show:

- Raw data sources -> build scripts -> processed dataset -> model -> reports/figures.
- Could be a compact flowchart distinct from Fig. 0.

Why add it:

If this is submitted to a computational journal, reproducibility matters. This figure makes the pipeline trustworthy.

Data source:

- Repo structure and scripts.

Caption idea:

`Reproducible analysis workflow. Raw third-party datasets are not redistributed; build scripts recreate the processed labels, validation metrics, figures and interactive report.`

Priority: **Medium**.

## Suggested Final Figure Order

This order avoids repetition and gives the paper a more polished research flow:

| Proposed number | Figure | Section |
|---|---|---|
| Fig. 1 | Study-site and training-data map | Section 2 |
| Fig. 2 | Six-layer model schematic | Section 3 |
| Fig. 3 | Mechanistic design levers: shade and wind | Section 3.1 |
| Fig. 4 | Training feature-space / OOD coverage | Section 4 or 6 |
| Fig. 5 | LOSO validation diagnostics | Section 5 |
| Fig. 6 | LOCO transfer failure | Section 6 |
| Fig. 7 | Few-shot conformal recovery | Section 6.1 |
| Fig. 8 | Anaikadu microclimate by overstorey | Section 7 |
| Fig. 9 | Crop envelope overlay and sensitivity | Section 7 |
| Fig. 10 | Economics / risk-return plot | Section 7 |
| Fig. 11 | Monte Carlo NPV distributions | Section 7 |
| Fig. 12 | Cash-flow timing | Section 7 |

This is a lot, so for a journal with strict figure limits, combine panels:

- Combine `LOSO validation`, `LOCO transfer`, and `few-shot recovery` into one multi-panel validation figure.
- Combine `crop envelope overlay`, `sensitivity heatmap`, and `risk-return` into one multi-panel decision figure.

## Existing Figures To Upgrade Rather Than Replace

### Upgrade current Fig. 1

Current role: cross-climate transfer.

Recommended upgrade:

- Make it a multi-panel figure:
  - LOSO skill/coverage.
  - LOCO skill/coverage heatmap.
  - Hybrid vs pure model comparison.

Reason:

The transfer result is the paper's main scientific contribution, so it should not feel visually small.

### Upgrade current Fig. 2

Current role: predicted microclimate by overstorey.

Recommended upgrade:

- Add OOD score as color or warning marker.
- Add confidence labels directly.
- Include uncertainty bars for `dT_max`.

Reason:

This prevents readers from mistaking the Anaikadu under-coconut temperature estimate as fully validated.

### Upgrade current Fig. 3

Current role: suitability + sensitivity.

Recommended upgrade:

- Add crop envelope bars or separate panel.
- Make the temperature sweep visually central.

Reason:

Pepper's robust lead is one of the most actionable results.

### Upgrade current Fig. 4

Current role: economics.

Recommended upgrade:

- Add `P(loss)` or payback labels.
- Or pair it with the new risk-return plot.

Reason:

NPV alone can hide downside risk and timing.

## Tables To Add Or Convert

### New Table A - Dataset summary

Placement: `Section 4. Data`.

Columns:

- Source
- Climate/regime
- Rows/site-months
- Sites
- Variables
- Label type
- Confidence

Why:

The manuscript currently describes the data in prose. A table will make it cleaner and more reviewer-friendly.

### New Table B - Confidence by layer

Placement: `Section 3 Methods` or after Fig. 0.

Columns:

- Layer
- Method
- Training data needed?
- Validation status
- Confidence

Why:

The paper's philosophy is confidence-labelled modelling. This table makes that explicit.

### New Table C - Candidate crop envelope summary

Placement: `Section 7` or supplement.

Columns:

- Crop
- Temperature optimum
- Shade range
- RH/VPD preference
- Main disease/risk
- Source confidence

Why:

This supports the crop ranking and reduces reviewer suspicion that the crop envelopes were hand-waved.

## What Not To Add

- Do not add decorative farm photos unless they directly support the study site or design scenario.
- Do not add generic AI architecture diagrams beyond the existing pipeline; the paper is stronger when it looks like a scientific workflow, not a neural-network sales pitch.
- Do not add too many economics-only charts; the scientific contribution is the microclimate transfer and uncertainty discipline.
- Do not add a GNN/PINN architecture figure unless those models are actually implemented and evaluated.

## Highest-Value Figure Build Order

1. `Study-site and training-data map`.
2. `Feature-space / OOD coverage plot`.
3. `LOCO transfer failure heatmap`.
4. `Few-shot conformal recovery curve`.
5. `Crop envelope overlay`.
6. `Risk-return decision plot`.

These six additions would make the manuscript visually much richer while directly reinforcing the scientific claims.
