# ADR-003 — Apply literature-sourced envelopes and disease parameters

- **Status:** Accepted
- **Date:** 2026-06

## Context

The crop growth envelopes (`CROPS`), disease infection parameters (`DISEASES`),
and variety susceptibility ratings (`VARIETY_SUSCEPTIBILITY`) in `config.py` were
initially literature-*shaped* (eyeballed). Three parallel sourcing passes
produced traceable, cited values:

- `reports/crop_envelopes_sourced.csv` (envelopes, worker A)
- `reports/disease_params_sourced.md` (infection params + variety ratings, worker B)
- `reports/economics_inputs_sourced.md` (yield/price inputs, worker C — for the
  staged layers 4–5, not applied to code here)

## Decision

Apply worker A's envelopes and worker B's disease/variety values to `config.py`.
Most-impactful changes:

- **Pomegranate RH ideal-high 85→65%** — the key fix. Couples the growth envelope
  to disease reality: high NE-monsoon humidity is no longer scored "ideal" when
  it is exactly the blight/fruit-cracking window.
- **Cocoa upper-ideal temp 32→28**, **Banana RH-low 60→75**, **Vanilla shade
  50–60→30–50**, **Black pepper tolerance 10–40 °C**, **Grapes RH tightened to
  stay consistent with the disease threshold**, **Mango/Guava ideal temps lowered**.
- **Pomegranate blight t_max 34→42** (pathogen active into the low-40s — matters
  for Pattukkottai summers); **wilt t_opt 28→25**; grape powdery-mildew t_min
  15→6; guava anthracnose t_opt 27→30.
- **Variety ratings corrected**, notably **pomegranate Ganesh/Bhagwa blight was
  inverted** — [R24] rates Ganesh *more* susceptible than Bhagwa. Fixed (Bhagwa
  MS, Ganesh S). The pipeline demo and `test_disease.py` were updated to match.
  Unsupported ratings (Guava "Lalit MR", wilt for Arakta/Mridula, Banganapalli
  powdery) dropped to `DEFAULT_SUSCEPTIBILITY`.

## Open decisions recorded (not yet resolved)

1. **Soil-moisture vs air-RH for pomegranate wilt and pepper foot rot.** Both are
   driven by *soil* moisture — which the user regulates via bores — not air RH.
   They currently sit on the air-microclimate axis with RH as a weak proxy. Flagged
   for design review; may be moved off the air axis or gated by an irrigation input.
2. **Sigatoka species** for banana: parameters are for *black* Sigatoka
   (*M. fijiensis*); historically *yellow* Sigatoka (*M. musicola*) is more common
   at the site. Recorded as black; revisit with local scouting.
3. **Dragon-fruit stem-rot agent** taken as *Neoscytalidium dimidiatum* (the Indian
   stem-canker pathogen); cardinal temps inferred from pathogenicity assays.
4. **Blight LWD thresholds** (4 h / 12 h) remain unsourced placeholders — no LWD
   dose-response study exists for *Xanthomonas axonopodis* pv. *punicae*.

## Consequences

- Envelopes and disease priors are now defensible and citation-traced.
- The disease layer remains **LOW confidence** overall (per the project discipline)
  — sourcing tightens the priors; it does not make absolute risk numbers
  trustworthy. Comparisons (timing, variety, design) stay the reliable outputs.
- Sourced values live in `reports/`; this ADR is the record of what was applied.
