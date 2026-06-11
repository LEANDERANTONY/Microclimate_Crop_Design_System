# Formula inventory for Word editing

Purpose: identify the formulas currently embedded in the agroforestry manuscript and list them in the order they should appear as separated display equations in Word. This file is only an editing guide; the Word document is not changed.

Reference style from the published solar-air-heater paper: equations are separated from prose as displayed formulas and numbered sequentially, with the surrounding paragraph explaining the variables.

## Recommended Equation Order

### Eq. (1) - Conceptual modelling chain

Section: `1.5 Research gap and objectives`

Current prose location: the manuscript currently gives the whole framework as an inline/block chain after "The integrating contribution is summarised as:"

Display equation:

```text
Macroclimate + controllable farm design
    -> microclimate offset
    -> disease risk
    -> crop viability
    -> economics
    -> risk-adjusted profit
```

Word note: This is more of a conceptual framework than a mathematical equation. It can be kept as an unnumbered displayed model chain, or labelled as Eq. (1) if the journal allows conceptual equations.

### Eq. (2) - Microclimate offset definition

Section: `3.1 Layer 1 - design -> microclimate`

Current prose location: after "We predict the offset from ambient macroclimate, not the raw under-canopy value..."

Display equation:

```text
Delta X = X_sub-canopy - X_ambient
```

Variable note:

`X` represents each target microclimate variable: `T_max`, `T_mean`, or `VPD`.

Optional expanded form:

```text
dT_max  = T_sub,max  - T_ambient,max
dT_mean = T_sub,mean - T_ambient,mean
dVPD    = VPD_sub    - VPD_ambient
```

### Eq. (3) - Beer-Lambert light transmission

Section: `3.1 Layer 1 - design -> microclimate`

Current prose location: in the paragraph beginning "Light and wind (mechanistic, HIGH confidence)."

Display equation:

```text
I / I0 = exp(-k x LAI)
```

Variable note:

`I` is under-canopy light, `I0` is open-field/top-of-canopy light, `k` is the extinction coefficient, and `LAI` is leaf area index.

### Eq. (4) - Out-of-distribution score

Section: `3.1 Layer 1 - design -> microclimate`

Current prose location: in the paragraph explaining that the model stores training feature ranges and exposes an OOD score.

Display equation:

```text
OOD score = (number of query features outside the training range) / (total number of features)
```

More compact mathematical form:

```text
OOD(x) = (1 / p) sum_{j=1}^{p} 1[x_j < min_train,j or x_j > max_train,j]
```

Variable note:

`p` is the number of model features and `1[...]` is an indicator function.

### Eq. (5) - Disease risk decomposition

Section: `3.2 Layer 2 - microclimate -> disease risk`

Current prose location: the paragraph begins "Disease risk follows the disease triangle..."

Display equation:

```text
realized_risk = environmental_pressure x variety_susceptibility
```

Variable note:

`environmental_pressure` is computed from microclimate conditions; `variety_susceptibility` is the crop-variety disease rating converted to a numeric multiplier.

### Eq. (6) - Effective waterlogging

Section: `3.2 Layer 2 - microclimate -> disease risk`

Current prose location: same paragraph, where soil-borne pathogens are described as driven by effective waterlogging.

Display equation:

```text
effective_waterlogging = site_waterlogging x drainage_mitigation
```

Variable note:

This belongs to the soil-water disease axis and should be clearly separated from air relative humidity.

### Eq. (7) - Crop viability

Section: `3.3 Layer 3 - viability`

Current prose location: the sentence "Viability = growth x (1 - disease risk)..."

Display equation:

```text
viability = growth_fit x (1 - disease_risk)
```

Variable note:

`growth_fit` is the fuzzy limiting-factor score against the crop envelope.

### Eq. (8) - Attainable yield

Section: `3.4 Layers 4-5 - economics and finance`

Current prose location: the sentence beginning "Attainable yield = reference yield..."

Display equation:

```text
attainable_yield = reference_yield x growth_fit x (1 - disease_risk)
```

Variable note:

This converts environmental fit and disease penalty into a yield multiplier.

### Eq. (9) - Gross margin / crop margin

Section: `3.4 Layers 4-5 - economics and finance`

Current prose location: this is implied by the abstract phrase "yield x suitability x (1-disease) x banded price - validated cost" and by the economics paragraph.

Display equation:

```text
crop_margin = attainable_yield x price - cost
```

Optional expanded form:

```text
crop_margin = reference_yield x growth_fit x (1 - disease_risk) x price - cost
```

Variable note:

Use `price` as a banded value, not a single fixed price, if explaining uncertainty.

### Eq. (10) - Discounted net present value

Section: `3.4 Layers 4-5 - economics and finance`

Current prose location: after "A 25-year discounted cash-flow..."

Display equation:

```text
NPV = sum_{t=0}^{T} C_t / (1 + r)^t
```

Variable note:

`C_t` is cash flow in year `t`, `r` is the real discount rate, and `T = 25` years in the Anaikadu analysis.

### Eq. (11) - Internal rate of return

Section: `3.4 Layers 4-5 - economics and finance`

Current prose location: same paragraph as NPV, where IRR is mentioned.

Display equation:

```text
0 = sum_{t=0}^{T} C_t / (1 + IRR)^t
```

Variable note:

This defines IRR as the discount rate that makes the NPV equal to zero.

### Eq. (12) - Monte Carlo sampling output

Section: `3.5 Layer 6 - uncertainty, and inverse design`

Current prose location: the paragraph beginning "Monte-Carlo (n = 2,000-3,000) samples..."

Display equation:

```text
NPV^{(m)} = f(offset^{(m)}, yield^{(m)}, price^{(m)}, overstorey^{(m)})
```

Variable note:

`m` is a Monte Carlo draw and `f(...)` represents the full pipeline from microclimate through finance.

### Eq. (13) - Probability of loss

Section: `3.5 Layer 6 - uncertainty, and inverse design`

Current prose location: same Monte Carlo paragraph, where probability of loss is discussed.

Display equation:

```text
P(loss) = P(NPV < 0)
```

Monte Carlo estimator:

```text
P(loss) = (1 / M) sum_{m=1}^{M} 1[NPV^{(m)} < 0]
```

Variable note:

`M` is the number of Monte Carlo draws.

### Eq. (14) - Risk-aware inverse-design objective

Section: `3.5 Layer 6 - uncertainty, and inverse design`

Current prose location: the sentence ending "maximise a risk-aware objective (0.7 x expected + 0.3 x downside)..."

Display equation:

```text
objective = 0.7 x E[NPV] + 0.3 x NPV_downside
```

Possible more precise form:

```text
objective = 0.7 x E[NPV] + 0.3 x P10(NPV)
```

Variable note:

Use `P10(NPV)` if the implementation defines downside as the 10th-percentile NPV.

### Eq. (15) - Mean absolute error

Section: `3.6 Validation protocol`

Current prose location: before or near the sentence defining skill against a naive baseline.

Display equation:

```text
MAE = (1 / n) sum_{i=1}^{n} |y_i - yhat_i|
```

Variable note:

This makes the validation metric explicit before defining skill.

### Eq. (16) - Skill over baseline

Section: `3.6 Validation protocol`

Current prose location: currently inline as `skill = 1 - MAE/MAE_baseline`.

Display equation:

```text
skill = 1 - MAE_model / MAE_baseline
```

Variable note:

Positive skill means the model improves on the training-mean offset baseline.

### Eq. (17) - Conformal calibration score

Section: `6.1 A handful of local observations restores calibrated intervals`

Current prose location: the section describes recalibrating interval width on `k` points, but the score is not written explicitly.

Display equation:

```text
s_i = max(q_lo(x_i) - y_i, y_i - q_hi(x_i))
```

Variable note:

`q_lo` and `q_hi` are the lower and upper quantile-model predictions. `s_i` is the nonconformity score for calibration point `i`.

### Eq. (18) - Few-shot conformal offset

Section: `6.1 A handful of local observations restores calibrated intervals`

Current prose location: immediately after the conformal score equation.

Display equation:

```text
qhat_alpha = Quantile_{target coverage}({s_i}_{i=1}^{k})
```

More explicit for the manuscript's 0.80 coverage:

```text
qhat_0.80 = Quantile_0.80({s_i}_{i=1}^{k})
```

Variable note:

This is the few-shot/Mondrian recalibration offset estimated from `k` in-regime points.

### Eq. (19) - Recalibrated prediction interval

Section: `6.1 A handful of local observations restores calibrated intervals`

Current prose location: after explaining that coverage is measured on the remaining held-out points.

Display equation:

```text
PI(x) = [q_lo(x) - qhat_alpha, q_hi(x) + qhat_alpha]
```

Variable note:

This is useful because it clarifies that the few-shot step widens or narrows intervals; it does not retrain the point predictor.

### Eq. (20) - Under-canopy temperature from offset

Section: `7. Result - application to Anaikadu`

Current prose location: the sensitivity paragraph describes sweeping the uncertain temperature offset and reporting under-canopy `T_max`.

Display equation:

```text
T_sub,max = T_ambient,max + dT_max
```

Variable note:

This links the temperature sweep in Table 3 to the offset model.

## Equations To Avoid Duplicating

- The conceptual chain appears in the abstract and Section 1.5. If numbered, number it only once in Section 1.5.
- `skill = 1 - MAE/MAE_baseline` appears again in the caption to Table 1. Once Eq. (16) exists, the table caption can say "Skill is defined in Eq. (16)."
- The crop-margin expression appears in the abstract and Methods. Display it in Methods only.
- NPV, IRR, and `P(loss)` are mentioned in the Abstract and Results. Display their formulas in Methods only, then use the symbols freely in Results.

## Optional Equations For A More Technical Version

These are not necessary for the current preprint, but could be added if reviewers ask for more detail:

1. Temperature-response beta function used inside disease risk.
2. Leaf-wetness-duration proxy from relative humidity and rainfall.
3. Gaussian windbreak porosity penalty centered near 0.45 porosity.
4. Bearing-ramp maintenance formula used in the finance model.
5. Waterlogging index formula from ADR-005, if soil-water calibration becomes a larger part of the manuscript.

## Practical Word Notes

- Insert the equations as separate display equations using Word's equation editor.
- Keep numbering sequential: `(1)`, `(2)`, etc., aligned right if possible.
- Define variables immediately below or in the paragraph before each equation.
- For simple equations, Word linear input works well; examples:
  - `I/I_0 = exp(-k LAI)`
  - `NPV = \\sum_(t=0)^T C_t/(1+r)^t`
  - `P(loss) = P(NPV < 0)`
- Do not add every formula to the Abstract. Abstract formulas make the paper feel heavy; the Methods section is the right place.
