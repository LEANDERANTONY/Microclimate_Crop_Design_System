# ADR-018 — Few-shot recalibration makes intervals honest by widening them; restating the plot-logger claim

- **Status:** Accepted
- **Date:** 2026-07-23
- **Clarifies (does not supersede):** [[ADR-014]] (few-shot / Mondrian conformal recalibration)
- **Follows:** [[ADR-012]] (transfer validation — "the fix is data, not a cleverer model"),
  [[ADR-016]] (external validation discipline)

## Context

ADR-014 adopted **few-shot conformal recalibration** as the out-of-climate uncertainty fix and
reported that "~5–25 in-regime calibration points restore dT_mean out-of-climate coverage from
~0.08 to ~0.80". That statement is correct as written and is **not** retracted here.

What has drifted is how the result is *used elsewhere*. `ROADMAP.md`, `AGENTS.md` and
`docs/PROJECT_CONTEXT.md` each state that the user's own plot logger (year 1) "would **collapse**
the offset uncertainty", and cite the ADR-014 few-shot result as the supporting evidence. That
conflates two different things:

1. **Interval honesty** — do the stated 80 % intervals actually contain 80 % of the truth?
2. **Interval width / decision-usefulness** — are those intervals narrow enough to separate one
   agroforestry design from another?

Few-shot recalibration addresses (1). It does not address (2), and in every regime we have
measured it makes (2) **worse**. "Collapse the uncertainty" claims (2) while citing evidence for
(1). This ADR records the corrected statement, the evidence for it, and the nuance that must
survive the correction — the plot logger is still the decisive investment, but by a different
route than the one currently written down.

This ADR **clarifies the interpretation of ADR-014**; ADR-014 is left unedited and its decisions
stand, exactly as ADR-017 scopes ADR-006 without retracting it.

## Findings (evidence)

**1. Recalibration buys coverage by paying width — in our own committed metrics.**
From `reports/mondrian_metrics.json` (the ADR-014 experiment, target `dT_max`, nominal
coverage 0.80), and from the first reproduction on real local data near the deployment site
(`reports/murugan_fewshot_metrics.json`, secondary daily analysis, target `dT_mean`):

| Held-out regime (target) | Cold (k=0) coverage @ width | Recalibrated coverage @ width | Width change |
|---|---|---|---|
| Mediterranean Spain (`dT_max`) | 0.409 @ **5.605 °C** | k=10 → 0.860 @ **10.931 °C** | **~2× wider** |
| Borneo oil-palm, open (`dT_max`) | 0.322 @ **3.626 °C** | k=5 → 0.943 @ **14.152 °C** | **~4× wider** |
| Borneo humid forest (`dT_max`) | 0.441 @ **2.947 °C** | k=5 → 0.846 @ **5.092 °C** | **~1.7× wider** |
| Tamil Nadu savanna, real local data (`dT_mean`) | 0.39 @ **2.58 °C** | k=5 → 0.81 @ **8.86 °C** | **~3.4× wider** |

The pattern is uniform across three held-out training regimes and one real external site: the
cold interval under-covers because it is **too narrow for an error the model is genuinely
making**; recalibration finds that out from the local points and inflates the width until the
stated coverage is true.

**2. The point prediction is untouched.** The few-shot step recalibrates the conformal width
**only** — no retraining, no change to the fitted quantile model (`scripts/mondrian_conformal.py`,
`scripts/run_murugan_fewshot.py`, both explicit on this). Mean absolute error, skill vs baseline
and bias are identical at every k. A biased prediction stays exactly as biased; only its stated
uncertainty becomes truthful.

**3. Honest width is not yet design-useful.** The Tamil Nadu k=5 result is an 8.86 °C interval on
`dT_mean`, i.e. **±~4.4 °C**. A truthful ±4.4 °C offset cannot discriminate between candidate
canopy designs whose predicted offsets differ by a fraction of a degree. Coverage restored is a
statement about honesty, not about resolution.

**4. Narrowing requires in-regime *training* data — a different use of the same logger.**
ADR-012's conclusion is unchanged and is the operative one here: cross-macroclimate transfer is a
**data-regime** limitation, not an estimator limitation, so "the fix is data, not a cleverer
model". Local points used as **calibration** data make the intervals honest (this ADR). The same
local points used as **training** data move the target from extrapolation toward interpolation,
which is the only mechanism in the system that can genuinely narrow the interval — and it needs
enough of them to retrain against, not 5–25.

## Decision

**Adopt the following as the project's canonical statement of what few-shot recalibration and the
plot logger deliver. Any doc, snapshot or manuscript sentence that says otherwise is corrected to
this.**

1. **Few-shot / Mondrian conformal recalibration restores *honest interval coverage* out of
   climate.** It does so by **widening** intervals until they tell the truth about an error the
   model is still making. It **does not** improve the point prediction and **does not** narrow
   uncertainty. (ADR-014's adoption of the method is unaffected — this is what the method is for.)
2. **The plot logger remains the decisive remedy**, and remains the right investment. Its value
   comes by **two distinct routes**, which must not be merged:
   - *as calibration data* (few-shot, ~5–25 points) → **honest intervals, immediately, but wider**;
   - *as in-regime training data* (a local source folded into the training set, then retrain) →
     **narrower intervals** — the ADR-012 remedy.
3. **"Collapse the offset uncertainty" is retired as a description of the few-shot mechanism.**
   Where the logger's value is asserted, say which route is meant. Narrowing is claimed **only**
   for the in-regime-training route, and there it is a well-grounded expectation
   (ADR-008/009/012/014), not a measured result.
4. **Decision-usefulness follows narrowing, not recalibration.** Reporting restored coverage
   without reporting the width that bought it is misleading in the flattering direction and is not
   permitted in project docs or the manuscript.

**Options considered**

- **(a) Leave the wording as-is** — rejected; it overstates a mechanism we have measured, in the
  one direction (optimism about the deployment site) the project's honesty-first posture exists to
  prevent.
- **(b) Retract or amend ADR-014** — rejected. ADRs are append-only, and ADR-014's finding is
  correct; the defect is downstream interpretation. This ADR is the correction vehicle.
- **(c) Downgrade the plot logger to a nice-to-have** — rejected as an over-correction. The logger
  is still the gating item; only the account of *what it buys and how* changes.
- **(d) Restate the claim, split it by route, and record the width evidence** — **adopted**.

## Consequences

- **ADR-014 stands unedited.** Its benchmark, its adoption of few-shot recalibration, and its
  reported coverage restoration are all unchanged. Read ADR-014 together with this ADR.
- **Docs restated:** `ROADMAP.md`, `AGENTS.md` (local-only), `docs/PROJECT_CONTEXT.md`
  (local-only) and the deployment-gap row of `docs/external_validation_datasets.md` no longer say
  the logger "collapses" the offset uncertainty; they state the calibration-vs-training split
  above. `README.md` carries the same wording in its limitations list and is flagged for the same
  restatement.
- **Manuscript constraint:** Paper 1 must **not** describe few-shot recalibration as collapsing,
  shrinking or reducing uncertainty. The correct framing is *restored coverage at increased
  width*, with the width reported alongside the coverage in every table and figure where the
  few-shot curve appears. The deployment-gap discussion should present the logger under both
  routes.
- **Confidence labelling unchanged in kind, sharper in statement:** the learned offset stays
  **MODERATE within-climate / LOW (OOD-flagged) at the deployment site**. Recalibration does not
  raise that label — an honest wide interval is still a wide interval.
- **Reporting rule:** wherever a coverage number from `mondrian_metrics.json` or
  `murugan_fewshot_metrics.json` is quoted, the corresponding interval width is quoted with it.
- **No code or metric changes.** Nothing in `src/`, `scripts/` or `reports/` is affected; the
  evidence for this ADR is the metrics already committed there.

## Next

- Re-read the few-shot passages of Paper 1 against decision 4 before submission.
- The narrowing route is untested: no in-regime training source exists yet. When one arrives (a
  warm-night / dry-zone source, or a season of the user's own plot data), re-run LOCO and the
  few-shot sweep and report the width change — that is the experiment that would let a narrowing
  claim be made from evidence rather than expectation.
- Keep the two routes separate in any future logger-specification work: calibration needs a few
  well-placed points; training needs a season of them across the design contrasts of interest.
