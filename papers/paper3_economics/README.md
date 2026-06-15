# Paper 3 — Risk-aware agroforestry farm economics

**Central claim.** Validated environmental suitability (Papers 1–2) can be
integrated with transparent, uncertainty-aware economics to support risk-adjusted
farm-design decisions — reported as distributions and P(loss), never as a single
confident profit figure.

Last in the program. Depends on Papers 1–2. Deliberately **not** a trained
yield/price model.

## Scope

- Yield: `attainable = reference × growth_factor × (1 − disease_loss)` — reuses
  upstream outputs, no training.
- Economics: banded price (trailing-average + trend + market-distance penalty) −
  validated costs; coconut + timber overstorey.
- Finance: 25-yr cash flow with gestation/bearing/harvest timing → NPV/IRR/payback.
- Uncertainty: Monte Carlo → NPV distribution + P(loss).

## Maps to core

- Modules: + `economics.py`, `finance.py`, `monte_carlo.py`.
- Scripts: `econ_run.py`, `finance_anaikadu.py`, `monte_carlo_anaikadu.py`,
  `qa_crop_economics.py`, `agmarknet_pull.py`.
- Reports: `economics_qa.md`, `economics_inputs_sourced.md`, `monte_carlo_npv.png`,
  `sensitivity_coconut.md`.
- Decisions: ADR-010, 011.

## Validation targets

Government cost-of-cultivation reports (NHB DPRs, TNAU), multi-year Agmarknet
price series, historical yield records. Keep every assumption user-editable.

## Target venues

Agricultural Systems / Smart Agricultural Technology.

## Open items

- [ ] Prices to HIGH confidence (multi-year Agmarknet series, TNAU cost lines).
- [ ] Keep economics framed as transparent calculator, not prediction.
