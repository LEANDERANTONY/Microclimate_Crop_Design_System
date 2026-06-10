# ADR-010 — QA: coconut economics were mis-calibrated (gestation cost bug)

- **Status:** Accepted
- **Date:** 2026-06
- **Trigger:** user challenge — the model said coconut monoculture was a *guaranteed
  loss*, which contradicts the obvious reality that coconut is widely grown profitably
  across Tamil Nadu.

## What was wrong

The "100% loss" was a calibration/logic error, not a framework flaw. Three bugs, in
order of impact:

1. **Full bearing-phase maintenance charged during gestation (the big one).** The model
   applied ~Rs 38k/acre/yr maintenance from year 1. TNAU's cost-of-cultivation table
   shows juvenile-year upkeep is only **~Rs 7-8k/acre/yr** (fertiliser ramps from 1/10th
   to full; little harvest labour). Charging full maintenance across the 6-year gestation
   over-counted cost by ~5x and buried the NPV.
2. **Nuts/acre too low.** Used 5,000; validated figure is **6,500-7,000** (Salem study;
   TNAU 4,800 at low density). Central raised to 6,000.
3. **Nut price band too conservative/stale.** Used Rs 7-12. Salem 2023-24 implies ~Rs 8;
   **2024-25 spiked to Rs 15-18+** (copra Rs 140-153/kg). Band widened to Rs 8-18.

## Validation sources

- **TNAU Coconut Cost of Cultivation** (agritech.tnau.ac.in): 5-yr establishment ~Rs 39k
  excl. land (live fencing); fertiliser only Rs 7,280 over 5 yrs; establishment normally
  **self-financed by banana intercrop** (+Rs 1.14L over 3 yrs).
- **Salem District economic study 2023-24** (Asian J. Agric. Hort. Res.): gross
  Rs 54,711, **net Rs 15,486/acre/yr**, bearing maintenance Rs 39,225, 6,500-7,000
  nuts/acre, **BCR 1.39** (profitable).

## Fix

- `economics.OVERSTOREY_ECON["coconut"]`: nuts (4800, 6000, 7500); price (8, 18); cost 39000.
- `finance`: added `JUVENILE_MAINT_FRAC = 0.3` — maintenance now scales with the bearing
  ramp (juvenile years cost 30% of full), applied to BOTH crops and overstorey. Coconut
  establish set to Rs 40k (excl. owned land).

## Result (Anaikadu, 8% real, 25 yr) — now matches reality

| system | NPV | IRR | payback | MC P(loss) |
|---|---|---|---|---|
| Coconut only | +Rs 129k | 17% | 10 yr | 3% |
| Coconut + Nutmeg | +Rs 313k | 18% | 11 yr | 24% |
| Coconut + Pepper | +Rs 243k | 19% | 9 yr | 18% |

Coconut monoculture is **profitable with ~97% confidence** (was 100% loss) — consistent
with BCR 1.39. The intercrop still adds substantial value and upside.

## Lessons / discipline

- Perennials need **bearing-ramped maintenance**, never flat full-cost from year 1.
- Always sanity-check a model verdict against lived reality before trusting it; the user's
  "this can't be right" was the correct signal.
- Remaining LOW-confidence inputs (timber, per-crop costs) flagged for the same treatment;
  an Agmarknet 3-yr price pull + TNAU per-crop cost tables remain the next QA upgrade.
