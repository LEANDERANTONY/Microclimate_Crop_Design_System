# Economics layer — design notes (staged, build later)

Captures the yield / price / market thinking. These are **layers 4–5**: kept
deliberately separate and **uncalibrated** until data exists. The discipline
(from the blueprint): don't train models you can't validate — derive what you
can from the pipeline you already have, and leave the rest as transparent,
user-editable estimates.

## Why separate, and why later
Yield and price are noisy, multifactorial, and partly outside the farm's
control. Forcing them into a trained model now would produce confident-looking
numbers with no support. Instead: reuse the growth + disease outputs as
*multipliers* on reference data, and represent everything as a **range**, not a
point.

## Layer 4 — Yield (hard; derive, don't train)
Don't train a yield model yet. Start from reference yield and bend it with the
pipeline you already have:

```
attainable_yield = reference_yield(crop, region)        # TNAU / ICAR / FAO averages
                 × growth_factor                        # from suitability score (0..1)
                 × (1 − expected_disease_loss)          # from disease layer (0..1)
```

This is elegant: the suitability score and disease risk you already compute
*become* the yield modifiers. No new model, and it's interpretable ("yield is
down because blight risk is 0.6, not because of climate"). Output a **band**
(use the prediction intervals), not a single figure.
Later (v2): once you have farm records, learn a correction term on top.

## Layer 5 — Price & market (don't predict daily price)
Model **marketability**, not tomorrow's mandi price. Four components, each cheap:

1. **Price level** — trailing average of the last few years' mandi prices
   (Agmarknet) → expected ₹/kg as a band (e.g. 25th–75th percentile), not a point.
2. **Price trend** — simple slope over recent years (appreciating / flat /
   declining). Dragon fruit and avocado trend up; staples are flat.
3. **Saleability / ease of selling** — the surplus angle you raised:
   `surplus_index = regional_production − local_absorption`. High surplus → local
   price depressed *and* you must ship far (add a **market-distance / logistics
   penalty**). Niche/undersupplied → premium *but* thin market (add a
   **market-risk** flag). This is where "novelty crop with low local demand →
   must send to north India / export" gets modelled explicitly.
4. **Market depth / perishability** — shelf life and bulk-buyer availability.
   Perishable + shallow market = sale pressure = effective price discount.

Data sources: **Agmarknet** (daily/weekly mandi prices, free), **APEDA** (export
demand), state horticulture **production statistics** (for surplus), FAO.

## Putting it together — risk-adjusted profit
```
profit = attainable_yield × expected_price − costs
costs  = establishment + irrigation + labour + disease-management + logistics
```
Because yield and price are **bands**, propagate them: report an *expected*
profit **and** a downside (e.g. 10th-percentile), consistent with the
uncertainty discipline used everywhere else. A crop with high mean profit but a
brutal downside (thin market, disease-prone) should not outrank a steadier one.

## The trade-off this surfaces (the valuable part)
- **Staple, easy to sell, low margin** (banana, guava) vs
- **Novelty, high price, thin/distant market, higher risk** (dragon fruit, exotic).
The system shouldn't just pick the highest price — it should show the
margin-vs-market-risk trade-off, the same way the agronomy side shows the
growth-vs-disease trade-off.

## Staging
- **v1** (no farm data): reference-yield × suitability × (1−disease loss);
  price = trailing-average band; saleability = surplus index + distance penalty.
  All transparent, user-editable.
- **v2** (with records): learn a yield correction; optional price time-series
  model (trend + seasonality) if worth it.

## Hook into the codebase (later)
Add `economics.py`: `yield_band(crop, growth, disease)`,
`price_band(crop, region)`, `profit(crop, design, …)`. It consumes the existing
`viability()` output, so it slots on top of the current pipeline without
touching layers 1–3.
