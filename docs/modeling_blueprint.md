# Modeling Blueprint — Agroforestry Microclimate → Crop Suitability

*Companion to the crop × canopy reachability matrix. v1 · June 2026*

---

## The one principle that decides everything

**This is not one model. It is a pipeline of three layers, and each layer has a different best-suited model class.** The most common mistake in projects like this is to reach for a single big neural network that maps "design → suitability" end to end. Don't. You have little data, several distinct physical processes, and a need to *explain* recommendations to a farmer. That calls for decomposition: model each sub-process with the simplest tool its physics allows, then chain them.

The chain:

```
DESIGN (controllable)            FORWARD MODEL              SUITABILITY            INVERSE DESIGN
main tree, spacing, LAI,   →   microclimate offset    →   distance to crop   →   "best design for
windbreak H & porosity         (light, wind, temp, VPD)    envelope (score)        crop X" (optimizer)
```

Match the model to the sub-problem. The sections below do exactly that.

---

## Layer 1 — Forward microclimate model (structure → microclimate)

Model **each microclimate variable separately**, because they are governed by different physics and have very different data hunger. Predict the **offset** (difference from the open-field macroclimate), not the raw value — offsets are what transfer across climates.

| Variable | Governing process | **Start with** | Graduate to | Why this choice | Data need |
|---|---|---|---|---|---|
| **Light / PAR** | Beer–Lambert extinction through canopy | **Mechanistic equation** `I = I₀·e^(−k·LAI)`, fit extinction coefficient *k* per overstorey species | Hybrid: let *k* be an ML function of crown structure | Near-pure physics; 1–2 fitted parameters; transfers almost perfectly | Very low |
| **Wind** | Shelterbelt aerodynamics (height, porosity) | **Empirical curve**: Δwind vs downwind distance (x/H) and porosity | Regression / CFD-informed surrogate | Classic, well-quantified shelterbelt science; rule-based | Low |
| **Temperature offset** | Canopy energy balance / radiation buffering | **Gradient boosting** (LightGBM / XGBoost) or Random Forest | Physics-guided hybrid (energy-balance prior + ML residual) | The ForestTemp/SoilTemp precedent used exactly this; best tabular performer on modest data | Moderate |
| **Humidity / VPD** | Transpiration + radiation + mixing | **Gradient boosting with quantile loss**, or Gaussian Process | PINN with energy/water-balance constraints | Noisiest, most local variable — the one that needs uncertainty bands and, eventually, physics constraints | Moderate–high |
| ~~Soil moisture~~ | — | **Excluded** — regulated by bores; treated as a controlled input, not a predicted output | — | Your decision; collapses the hardest-to-transfer variable | n/a |

**Key idea — residual / physics-guided ML.** Where physics gives a backbone (light, wind, even temperature via energy balance), use it as the base prediction and train the ML model only on the *residual* (what physics misses). The literature is consistent that these hybrids beat pure ML and, crucially, **resist data scarcity** — which is your binding constraint.

---

## Layer 2 — Suitability scoring (microclimate → crop fit)

| Stage | Method | Why |
|---|---|---|
| **Start** | **Fuzzy membership + limiting-factor (Liebig's "law of the minimum")** — each predicted variable gets a 0–1 membership against the crop's envelope; the crop score is driven by the *worst-matched* factor, not the average | Zero training data needed; fully interpretable; matches agronomy (one limiting factor sinks the crop); directly reuses your envelope table |
| **Graduate** | **Learned suitability** — regress actual observed crop performance/yield on predicted microclimate once you have outcomes | Replaces "can grow" with "grows well here," the claim that actually matters |

Use the *minimum* across factors, not a weighted sum — a perfect temperature can't compensate for fatal wind exposure. This is the agronomically honest aggregation and it's a defensible methodological choice in a paper.

---

## Layer 3 — Inverse design / optimisation (target crop → best design)

This layer **is the product**. Forward prediction is the means; the deliverable is "for vanilla, use coconut at this spacing + this windbreak."

| Situation | Method | Why |
|---|---|---|
| Single crop, smooth design space | **Bayesian optimisation** (GP surrogate, e.g. BoTorch / scikit-optimize) over the forward model | Sample-efficient search; native uncertainty; designed for "expensive" evaluations |
| Several variables / several intercrops at once | **Multi-objective genetic algorithm (NSGA-II)** | Returns a *Pareto front* of designs trading off competing crop needs — e.g. a layout good for both pepper and nutmeg |
| Differentiable forward model | Gradient-based constrained optimisation | Fastest if the whole chain is differentiable |

Constraints encode reality: spacing bounds, a single main-tree choice, windbreak height limits, budget. The optimiser searches **only the variables you control**.

---

## Cross-cutting — uncertainty is non-negotiable

With a small, partly-borrowed dataset, a bare point score is misleading. A planting decision needs *"suitable, 80% confidence,"* not *"score 72."*

- **Conformal prediction** — wraps *any* model (RF, boosting, GP) to give statistically calibrated intervals. Cheapest path to honest uncertainty; add it from day one.
- **Quantile regression / NGBoost / Gaussian Process** — give native predictive intervals; GP is especially strong in the small-data regime and doubles as the Bayesian-optimisation surrogate.

---

## The honest model-selection ladder (gated by data, not ambition)

**Phase A — borrowed + public data, few local points.**
Mechanistic light + wind · LightGBM (quantile) for temp/VPD offset · fuzzy/limiting-factor suitability · Bayesian-optimisation inverse design · conformal intervals. *This alone is a publishable, farm-useful system.*

**Phase B — your sensors added (one season).**
Switch the temp/VPD models to physics-guided hybrids; Gaussian Process for VPD; calibrate locally; keep conformal bands. Re-fit extinction *k* for your actual coconut/timber.

> **Tested early (ADR-012):** the physics-prior (extrapolating linear backbone) + XGBoost-residual hybrid is already implemented (`HybridQuantileModel`) and benchmarked with leave-one-climate-out. Finding: it ties the pure tree *in-distribution* but does **not** improve — and can worsen — cross-*macroclimate* transfer, because the offset magnitude is regime-dependent and a tropical-trained backbone overshoots into a held-out cool climate. Lesson: the hybrid's value is unlocked by *data in the target regime* (so its backbone interpolates), not by architecture alone. Kept as the Phase-B model, off by default until warm-climate data lands.

**Phase C — multi-season, rich data.**
PINN for the coupled energy/water balance (the "publishable physics + ML" version); GNN **only** if you move to predicting within-field *spatial* gradients across many sensor nodes.

---

## What NOT to start with — and why

- **PINNs** — powerful and paper-friendly, but data-hungry and finicky to train. They earn their place in Phase C with energy-balance-grade data, not before.
- **Graph Neural Networks** — justified only if you predict spatial fields over many in-field nodes. For plot-level averages they are pure overhead.
- **Deep MLPs / generic deep nets** — tree-based models beat them on tabular small data almost every time. Skip until data is abundant.

The novelty of this project lives in the **question, the dataset, and the inverse-design framing** — *not* in exotic architecture. A clean hybrid-physics + boosting + Bayesian-optimisation stack, well validated, is a stronger paper than a flashy GNN on thin data.

---

## Validation — test the thing the project actually claims

The central claim is **transferability across macroclimates**. So validate with **leave-one-site-out** (and ideally **leave-one-climate-zone-out**) cross-validation, *not* random splits. Random splits let the model memorise a site and flatter the metrics; leave-site-out directly measures "does the offset learned here transfer there." Report intervals, not just point error. This validation design is itself a credibility differentiator at review.

> **Done (ADR-012).** Both protocols are implemented in `validation.py` and report **skill vs a mean-offset baseline** + out-of-sample R². Result: within-climate LOSO is skilful (dT_mean +27%, dVPD +33%, dT_max +19%; intervals ~0.8), but **leave-one-climate-out** is the honest limit — skill goes **negative** on a held-out Mediterranean climate and interval coverage collapses to ~0.2–0.5. The negative result *is* a finding: it proves transfer is data-limited, not model-limited, and motivates a target-regime training source + per-climate (Mondrian) conformal calibration.

---

## Recommended concrete starting stack

| Component | Pick |
|---|---|
| Light/PAR | Beer–Lambert, *k* fitted per overstorey species |
| Wind | Empirical shelterbelt curve (Δwind vs x/H, porosity 40–60%) |
| Temp & VPD offset | LightGBM with quantile loss (gives intervals out of the box) |
| Suitability | Fuzzy membership + limiting-factor (min across variables) |
| Inverse design | Bayesian optimisation (BoTorch / scikit-optimize) |
| Uncertainty | Conformal prediction wrapper on every learned model |
| Validation | Leave-one-site-out / leave-one-climate-out CV |

---

### Sources
- Microclimate ML + hybrid physical heat-balance: [From Big Data to Small Scales (bioRxiv, 2025)](https://www.biorxiv.org/content/10.64898/2025.12.01.691551v1.full)
- Small-data function approximation (GP & RF): [Improving Random Forests by Smoothing (arXiv)](https://arxiv.org/pdf/2505.06852)
- Physics-constrained GP for data efficiency: [Hybrid data-driven/physics-constrained GP (arXiv)](https://arxiv.org/pdf/2205.06494)
- Hybrids resist data scarcity: [Integrating Scientific Knowledge with ML (ACM Computing Surveys)](https://dl.acm.org/doi/10.1145/3514228)
- Beer–Lambert extinction & LAI: [Extinction coefficient in the Beer–Lambert law (J. Forest Science)](https://www.tandfonline.com/doi/full/10.1080/21580103.2012.673744)
- ForestTemp sub-canopy ML offset model: [ForestTemp (Global Change Biology)](https://onlinelibrary.wiley.com/doi/abs/10.1111/gcb.15892)
