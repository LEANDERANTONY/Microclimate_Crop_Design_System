# Publication program (modular)

This project is published as **three focused papers** that share one tested core
package (`src/agroforestry/`). Each paper has one defensible empirical claim and
its own validation protocol, so reviewers evaluate one contribution at a time
instead of six interlinked ones.

> **Non-destructive layout.** We do **not** fork or move the core code per paper.
> The shared package stays single-sourced and tested; each `paperN_*/` folder
> holds only that paper's experiment configs, frozen result snapshots, figures,
> and a manuscript pointer. The mapping from paper → core modules → scripts →
> reports is documented in each paper's `README.md`.

| Paper | Title (working) | Core modules used | Status |
|---|---|---|---|
| 1 | Uncertainty-aware agroforestry microclimate prediction | `physics`, `features`, `models`, `models_benchmark`, `validation`, `predict`, `data`, `config` | Drafted (all-in-one); to **carve out** + add warm-tropical training source + frozen external test |
| 2 | Microclimate-aware crop suitability & inverse design | + `suitability`, `disease`, `optimize` | Built; needs suitability/disease validation |
| 3 | Risk-aware agroforestry farm economics | + `economics`, `finance`, `monte_carlo` | Built; kept transparent/uncalibrated until farm records exist |

## Build order (each leans on the previous)

1. **Paper 1** is the foundation: design + macroclimate → under-canopy
   microclimate, with honest transfer characterization. Everything downstream
   inherits its predictions and its uncertainty.
2. **Paper 2** consumes Paper 1's microclimate to rank crops and run inverse
   design ("what design achieves conditions suitable for crop X?"). Disease is
   **one modifier** of suitability, not the headline.
3. **Paper 3** adds economics on top of validated suitability — transparent,
   user-editable estimates with bands, never a trained yield/price model.

## Shared discipline (all papers)

- Confidence labels everywhere (physics = HIGH; temp offset = MODERATE; humidity/
  VPD + disease params = LOW / literature-shaped).
- Validation is leave-one-site-out and **leave-one-climate-out**, never random
  split. Conformal calibration is group-aware; few-shot Mondrian recalibration
  documented.
- External validation datasets are **pre-registered and frozen before looking at
  results** — see `docs/external_validation_datasets.md`.
