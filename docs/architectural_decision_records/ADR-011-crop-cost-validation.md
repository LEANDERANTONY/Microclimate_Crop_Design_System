# ADR-011 — Crop cost validation + intercrop-vs-standalone distinction

- **Status:** Accepted
- **Date:** 2026-06
- **Follows:** ADR-010 (coconut QA). Closes the "costs were my estimates" gap from
  `reports/economics_qa.md`.

## Context

After the coconut fix, the remaining LOW-confidence inputs were the per-crop **costs**
(my estimates). Validated them against NHB Detailed Project Reports, TN district economic
studies, and project-report aggregators (agrifarming / croplibrary / finline), June 2026.

## Key finding — cost depends on the production SYSTEM

The biggest correction is conceptual, not just numeric: a crop's establishment cost
differs greatly between **standalone** and **coconut intercrop**:

- **Pepper:** standalone ~Rs 1-1.5 L/acre (own standards + drip); as a coconut intercrop
  it climbs the palms and shares irrigation -> establishment ~Rs 30k.
- **Nutmeg, cocoa:** same logic — intercrop establishment well below standalone.
- **Full-sun crops (pomegranate, grapes, dragon fruit)** carry their own
  drip/trellis/fencing/borewell, so their costs are genuinely high.

Our model scores pepper/nutmeg/cocoa as coconut intercrops, so intercrop costs are the
correct ones to use.

## Changes (validated, Rs/acre)

| crop | establish | maintain | note | source |
|---|---|---|---|---|
| Black pepper | 30k | 35k | intercrop (palms as standards) | NHB DPR, croplibrary |
| Nutmeg | 50k | 40k | intercrop; maintain raised from 20k | agrifarming, croplibrary |
| Cocoa | 35k | 30k | intercrop, ~200 trees/ac | rangde, Mongabay |
| Vanilla | 80k | 60k | labour-intensive (hand pollination) | (LOW) |
| Pomegranate | 180k | 90k | drip+fence+borewell | NHB DPR |
| Ginger (annual) | — | 150k | seed-rhizome heavy | TNAU, asiafarming |
| Banana (annual) | — | 130k | TC+drip; NHB/TN ~Rs 1.25-1.34 L | NHB, TN study |
| Dragon fruit | 300k | 50k | concrete poles | project reports |
| Grapes | 200k | 90k | trellis+drip (unchanged) | NHB |
| Mango / Guava | 40k/50k | 20k/25k | low-input orchard (unchanged) | — |

`economics.CROP_ECON['cost']` reconciled to `maintain + establish/life` so the single-year
margin and the multi-year finance agree.

## Result (Anaikadu, 8% real, 25 yr)

| system | NPV | IRR | payback | MC P(loss) |
|---|---|---|---|---|
| Coconut only | +129k | 17% | 10 yr | 3% |
| Coconut + Nutmeg | +200k | 14% | 12 yr | 40% |
| Coconut + Pepper | +199k | 18% | 9 yr | 23% |
| Coconut + Banana | -766k | n/a | never | 77% |

Recommendation holds and **sharpens**: nutmeg and pepper are both solidly positive
(~Rs 200k NPV); **pepper now looks marginally more robust** (bears at year 3 vs nutmeg's
7, lower establishment -> earlier payback 9 yr and lower P(loss) 23% vs 40%). Banana under
coconut is firmly uneconomic (cost up to Rs 130k confirms it). 22 tests pass.

## Confidence now

Costs MODERATE (validated vs DPRs/studies; still not farmer-level line items). Prices
MODERATE (current, not stale). Remaining LOW: vanilla (thin/contract market). Next: a
true Agmarknet 3-yr price pull would lift prices to HIGH.
