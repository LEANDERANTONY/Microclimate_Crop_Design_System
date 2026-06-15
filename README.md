# Agroforestry Microclimate → Crop → Profit, under uncertainty

**From canopy design to crop profitability for a real smallholder farm — with calibrated, honest uncertainty at every step.**

![tests](https://img.shields.io/badge/tests-35%20passing-3f8f4f) ![python](https://img.shields.io/badge/python-3.11-4a6b3a) ![license](https://img.shields.io/badge/license-MIT-7a5a2e) ![status](https://img.shields.io/badge/pipeline-6%20layers%20built-2f3a28) ![manuscript](https://img.shields.io/badge/manuscript-draft%20v0.3-4a6b3a)

> **Manuscript:** a full draft (literature review, 22 numbered equations, 8 tables, 12 figures, declarations, verified references) is in [`docs/manuscript/manuscript.md`](docs/manuscript/manuscript.md); a Word build with figures embedded is in [`docs/manuscript/submission/manuscript.docx`](docs/manuscript/submission/manuscript.docx). Venue analysis, cover letter and preprint checklist are alongside it in [`docs/manuscript/`](docs/manuscript/).

This research codebase predicts the **microclimate a planned agroforestry design will create**, scores **crop suitability and disease risk** under that microclimate, runs the result through **economics and discounted cash-flow**, and **propagates uncertainty** to a profit distribution — then recommends a design. It is built for a real site, **Anaikadu (Pattukkottai), Thanjavur District, Tamil Nadu** (hot semi-arid Cauvery delta), but the method is general.

> **Headline result for Anaikadu:** coconut as the overstorey with a **black pepper** intercrop clears an 8% real hurdle — **NPV ≈ ₹565k/acre, IRR ≈ 33%, payback 7 yr, P(loss) ≈ 12%** — and pepper's lead is **robust across the whole plausible temperature band**. Nutmeg, by contrast, sits at its thermal-optimum edge here and is viable only if the cooler end of the uncertain offset holds (a decision-relevant finding, not a flaw). An interactive report is in [`reports/anaikadu_preprint.html`](reports/anaikadu_preprint.html). *(Headline-crop envelopes sourced from FAO ECOCROP / PROSEA — `reports/crop_envelopes_ecocrop.md`.)*

---

## Why this exists

Conventional crop recommendation uses *regional* climate. But an agroforestry system creates its **own** microclimate, and that microclimate — not the regional average — decides what grows and what **diseases** take hold. The causal chain that actually governs profitability is:

```
Macroclimate + Farm design → Microclimate → Disease → Crop viability → Economics → Profit (with risk)
                                  ↑                                                      ↓
                         (design is controllable)                       (inverse-design optimiser)
```

The distinguishing idea is **honesty-first modelling**: every layer carries an explicit confidence level, the learned parts are validated for transfer and flagged when extrapolating, and downstream economics *propagate* that uncertainty instead of hiding it behind point estimates.

---

## The six layers

| # | Layer | Method | Confidence |
|---|---|---|---|
| 1 | design → **microclimate** | Beer–Lambert light + shelterbelt wind (physics); XGBoost **quantile** offsets for temperature/VPD + conformal intervals; **OOD** flag; design→feature mapping grounded on real TN satellite values (ADR-013) | physics HIGH · offset MODERATE |
| 2 | → **disease risk** | two axes — air-microclimate (foliar) + soil-water/waterlogging (soil-borne); variety susceptibility; drainage as a design lever | MODERATE |
| 3 | growth + disease → **viability** | fuzzy trapezoidal membership, Liebig limiting factor | MODERATE |
| 4 | viability → **economics** | reference yield × growth × (1−disease), banded price − validated cost; coconut + timber overstorey | MODERATE |
| 5 | → **finance** | 25-yr cash-flow with gestation/bearing/harvest timing; NPV / IRR / payback | MODERATE |
| 6 | → **uncertainty** | Monte Carlo over offset + yield + price + timber bands → NPV distribution, P(loss) | propagated |

An **inverse-design optimiser** wraps the chain to search overstorey, canopy density, windbreak and drainage for the profit-maximising design.

---

## Key findings (all figures are real pipeline output)

### 1 · The canopy→microclimate offset transfers *within* climate — but not yet *across* macroclimates

Trained on tropical Borneo (SAFE) + Mediterranean Spain (La Jarda) forest plots and tested **leave-one-site-out** (an entire site held out per fold):

![cross-climate transfer](figures/fig1_transfer.png)

Within climate the model **genuinely learns**: dT_mean LOSO MAE **0.28–0.33 °C**, **+27 % skill** over a mean-offset baseline (dVPD +33 %, dT_max +19 %), intervals calibrated near the 0.8 target. The documented full two-climate LOSO is 0.28 °C (ADR-006).

But the stricter **leave-one-climate-out (LOCO)** test — holding out an entire macroclimate / canopy regime — is honest about the limit: transfer is strong for the held-out humid forest (+22 % skill), modest for the open oil-palm canopy, and **fails on the held-out Mediterranean climate** (negative skill), with interval coverage collapsing from ~0.8 to ~0.2–0.5 out-of-climate. The warm-night semi-arid Anaikadu target is a different regime again, so the under-coconut offset is **genuine extrapolation** (flagged LOW). A physics-prior + ML-residual **hybrid was built and tested**; it ties in-distribution but does **not** rescue cross-climate transfer (it overshoots into the held-out climate), so the pure quantile model stays default (ADR-012). The decisive fix is on-plot sensing. Metrics: [`reports/loso_metrics.json`](reports/loso_metrics.json), [`reports/loco_metrics.json`](reports/loco_metrics.json).

### 2 · Physics is trustworthy; the learned offset is flagged when extrapolating

Shade and wind come from mechanistic physics (HIGH confidence) for any candidate canopy:

![microclimate](figures/fig2_microclimate.png)

The temperature offset under **coconut** is flagged **LOW (out-of-distribution)** — an open palm canopy is unlike the closed-forest training data — rather than silently extrapolated.

### 3 · The intercrop shortlist is robust to that uncertainty

![suitability + sensitivity](figures/fig3_suitability.png)

Under coconut, **black pepper leads at every point** of the temperature sweep — its top rank is robust to the uncertain offset. Nutmeg leads only at the cool end and falls away as temperature rises (Anaikadu sits at the edge of its flowering optimum), so the model makes two different-confidence claims: pepper is the actionable pick now; nutmeg is conditional on the cooler microclimate, which on-plot sensing would confirm.

### 4 · Economics and finance, validated against reality

![economics](figures/fig4_economics.png)

Coconut + pepper clears the hurdle decisively (NPV ≈ ₹565k, IRR ≈ 33%); coconut + nutmeg is marginal (≈ ₹127k, IRR ≈ 13%) given the thermal-edge sensitivity above; banana under mature coconut is uneconomic; timber shows high *annualised* return but as a single far-off harvest (see cash-flow timing below). Costs are validated against NHB Detailed Project Reports + TNAU; prices anchored to live data.gov.in Agmarknet. *(A coconut "guaranteed loss" the model first produced was traced to a gestation-cost bug and fixed — documented in [ADR-010](docs/architectural_decision_records/ADR-010-coconut-economics-qa.md) as a validation-discipline example.)*

### 5 · Uncertainty made explicit

![monte carlo](figures/fig5_montecarlo.png)
![cash-flow timing](figures/fig6_cashflow.png)

Monte Carlo turns every point estimate into a distribution and a probability of loss. Coconut+pepper sits mostly positive (P(loss) ≈ 12%); coconut+nutmeg carries a much wider loss probability (≈ 41%) — hot draws fail the crop at its thermal edge, cool draws pay well. The cash-flow chart shows the real trade-off: steady annual spice income vs a single distant timber harvest.

### 6 · The transfer failure is a data-regime property, not an estimator flaw

A six-family benchmark (Ridge, Random Forest, Gaussian process, mixture-of-experts, the XGBoost-quantile model, and the physics hybrid) on the same offset task shows that **in-distribution every family is skilful**, but **under leave-one-climate-out they diverge sharply**: linear and mixture-of-experts models collapse, tree models are bounded but lose nearly all skill, and **only the distance-aware Gaussian process keeps non-negative cross-climate skill and the best out-of-climate interval coverage** (~0.62). No family transfers across the warm-night gap — confirming the limit is the data regime. Reproduce with `scripts/benchmark_models.py` (classes in `src/agroforestry/models_benchmark.py`) → [`reports/benchmark_metrics.json`](reports/benchmark_metrics.json).

---

## Install & run (uv)

```bash
uv sync                                        # env from uv.lock
uv run pytest                                  # 35 tests
uv run python scripts/run_validation.py        # -> LOSO + LOCO skill metrics
uv run python scripts/benchmark_models.py      # -> model-family benchmark (reports/benchmark_metrics.json)

uv run python scripts/run_site.py --lat 10.4019 --lon 79.3545 --label "Anaikadu"   # end-to-end at a real point
uv run python scripts/finance_anaikadu.py      # NPV / IRR / payback per system
uv run python scripts/monte_carlo_anaikadu.py  # uncertainty distributions

uv run python scripts/export_results.py        # -> reports/results.json
uv run python scripts/make_figures.py          # -> figures/*.png (results figures)
uv run python scripts/make_paper_figures.py    # -> figures/*.png (site map, OOD, LOCO, benchmark, …)
uv run python scripts/build_dashboard.py       # -> reports/anaikadu_preprint.html
uv run python scripts/build_docx.py            # -> docs/manuscript/submission/*.docx
```

Earth-Engine-backed scripts (`run_site.py`, the data builders) need an authenticated `earthengine-api` project; the offset/economics/finance/Monte-Carlo scripts run from the committed `data/processed/labelled_offsets.parquet` (gitignored) without network.

---

## Data

Real, openly-sourced; raw files are gitignored. Microclimate labels: **SAFE Project** Borneo (Zenodo 1228188) + gazetteer (3906082); **La Jarda**, Cádiz, Spain (Zenodo 18913503); **SAFE landscape** oil-palm rasters (Zenodo 7893600). Features via Google Earth Engine: ERA5 / ERA5-Land, SoilGrids, Copernicus DEM, MODIS LAI/NDVI, ETH canopy height, SoilTemp/SBIO. Economics: NHB DPRs, TNAU cost-of-cultivation, Salem District study, live data.gov.in Agmarknet. Provenance in [`reports/`](reports/) and the ADRs.

---

## Repo layout

```
src/agroforestry/   physics · models · models_benchmark · predict · suitability · disease · economics · finance · monte_carlo · optimize · validation
scripts/            data builders, run_site, finance/MC/sensitivity, run_validation, benchmark_models, export_results, make_figures, make_paper_figures, build_dashboard, build_docx
tests/              35 tests
docs/               architecture, modeling_blueprint, economics_layer, data_acquisition, ADRs 001–014, manuscript/ (paper + submission docx + venue/cover-letter/preprint guides)
reports/            results.json, loso/loco/benchmark/mondrian metrics, anaikadu_preprint.html, economics_qa, sourced inputs, catalogs
figures/            12 manuscript figures (regenerated by make_figures.py + make_paper_figures.py)
```

See [`folder_structure.txt`](folder_structure.txt); running log in [`DEVLOG.md`](DEVLOG.md); plans in [`ROADMAP.md`](ROADMAP.md).

---

## Honest limitations

- The under-coconut **temperature offset is extrapolation** (forest-trained, open palm canopy) — flagged LOW; physics (shade/wind) and the robust shortlist carry the decision. Grounding the design→feature mapping on real TN satellite values (ADR-013) confirmed the OOD is **genuine**, not a proxy artefact.
- A **macroclimate-transfer gap** remains, now **quantified by leave-one-climate-out**: warm-night semi-arid Tamil Nadu has no close analog in the humid-tropical + Mediterranean training set, transfer skill goes negative on a held-out climate, and intervals lose calibration out-of-climate (ADR-012). A physics-prior hybrid was tested and did not close it.
- Economics are **MODERATE** confidence (validated vs DPRs/TNAU + live mandi prices); a clean 3-yr CEDA price series is still pending; timber prices are LOW.
- Reanalysis can't resolve the village from the town (shared ~31 km ERA5 pixel) — an **on-plot logger (year 1)** is the definitive fix and would collapse the temperature uncertainty.

Treat **comparisons** (design A vs B, crop ranking, dry vs wet timing) as reliable and absolute numbers as indicative-with-stated-uncertainty. Every modelling decision is recorded in [`docs/architectural_decision_records/`](docs/architectural_decision_records/) (ADR-001–014).

---

## Status

All six layers built, validated, and runnable (35 tests). Real data integrated across two macroclimates + an open-canopy regime. Transfer validated with skill scores + leave-one-climate-out; a physics-prior hybrid tested (ADR-012); design→feature mapping grounded on real TN satellite values (ADR-013); a six-family model benchmark packaged and tested (`models_benchmark.py`). **Full manuscript drafted** (literature review, equations, 8 tables, 12 figures, declarations, verified references) with a submission Word build, venue analysis, cover letter and EarthArXiv checklist in `docs/manuscript/`. Outstanding (manual / data): post the preprint (ORCID + Zenodo "Cite as" names + Save-as-PDF), SoilTemp / tropical-understory data (to close the climate gap), CEDA 3-yr prices, and the user's own plot sensor. *Research preprint — model output with stated uncertainty, not guarantees.*
