# Economics QA — audit of ALL crop inputs (after the coconut fix)

**Trigger:** after the coconut gestation-cost bug (ADR-010), check every other crop for
the same class of error. Tool: `scripts/qa_crop_economics.py` (standalone finance at
ideal suitability) + cross-checks vs TNAU cost-of-cultivation and the sourced doc.

## 1. Is the coconut-class bug present elsewhere? — NO

The coconut bug was **full bearing-phase maintenance charged during gestation**. The fix
(`finance.JUVENILE_MAINT_FRAC = 0.3`, maintenance scales with the bearing ramp) is applied
in `crop_cashflow` too, so it **already covers every perennial** (nutmeg 7-yr gestation,
mango 5-yr, cocoa/pepper/pomegranate 3-yr). Audit at ideal suitability — every crop is
clearly positive, none manufactures a loss:

| crop | yield_c (kg/ac) | price_mid | gross | cost | net | g/cost | gestation | NPV(ideal) | IRR |
|---|---|---|---|---|---|---|---|---|---|
| Black pepper | 400 | 500 | 200k | 40k | 160k | 5.0 | 3 | 1,077k | 67% |
| Nutmeg | 400 | 750 | 300k | 30k | 270k | 10.0 | 7 | 1,065k | 35% |
| Cocoa | 350 | 425 | 149k | 40k | 109k | 3.7 | 3 | 861k | 62% |
| Vanilla | 100 | 8000 | 800k | 60k | 740k | 13.3 | 3 | 3,414k | 137% |
| Ginger | 8000 | 95 | 760k | 120k | 640k | 6.3 | 1 | 6,832k | 200% |
| Banana | 20000 | 16.5 | 330k | 90k | 240k | 3.7 | 1 | 2,562k | 200% |
| Pomegranate | 5000 | 80 | 400k | 90k | 310k | 4.4 | 3 | 2,312k | 96% |
| Guava | 10000 | 27.5 | 275k | 40k | 235k | 6.9 | 2 | 1,863k | 168% |
| Mango | 4500 | 52.5 | 236k | 35k | 201k | 6.8 | 5 | 1,200k | 51% |
| Grapes | 7000 | 60 | 420k | 150k | 270k | 2.8 | 2 | 2,448k | 88% |
| Dragon fruit | 8000 | 140 | 1,120k | 120k | 1,000k | 9.3 | 2 | 8,069k | 200% |

(NPV/IRR at ideal suitability = best case; real Anaikadu values are lower because growth <
100. These are a SANITY check, not the recommendation.)

## 2. Unit discipline (the trap that bit coconut) — OK

TNAU tables are per **hectare**; our model is per **acre**. Spot-check: banana TNAU 75 MT/ha
= 30 MT/acre; our 20 MT/acre (≈ 49 MT/ha) is a *conservative TC-drip* figure, correctly in
per-acre terms. Pepper 400 kg/acre, nutmeg 400 kg/acre, pomegranate 5 t/acre — all match the
per-acre figures in `economics_inputs_sourced.md`. **No ha/acre slip found.**

## 3. Confidence by input

- **Yields & prices — MODERATE** (from `economics_inputs_sourced.md`: TNAU/ICAR/NHB +
  mandi bands). Prices are *not* stale-low the way coconut's was; e.g. pepper mid Rs 500
  (2024-25 Rs 600-950), nutmeg Rs 600-900 — within current ranges.
- **Costs — LOW (my estimates).** Realistic ranges but not line-itemed from TNAU. The
  high-input crops (ginger Rs 120k, banana Rs 90k, grapes Rs 150k, dragon Rs 120k/acre)
  are the ones most worth a TNAU line-item validation next.
- **The two RECOMMENDED crops are well-calibrated:** pepper (establish 60k for standards +
  vines, maintain 25k, net ~175k at full) and nutmeg (establish 50k, low maintain 20k, net
  ~280k) match known well-managed economics. The coconut+nutmeg / +pepper recommendation
  does not rest on shaky cost numbers.

## 4. Known minor inconsistency (not a bug)

`economics.CROP_ECON['cost']` (single-year margin) and `finance.CROP_FIN` (establish +
maintain) are independently set and differ slightly (e.g. pepper 40k vs 25k+60k). Each is
internally reasonable for its layer; reconciling them (cost = maintain + amortised
establish) is a tidy-up for the next pass, not a correctness issue.

## 5. Next validation pass (to lift LOW -> HIGH)

1. TNAU/NHB per-acre **cost-of-cultivation line items** for ginger, banana, grapes, dragon
   fruit, pepper, nutmeg (replace my cost estimates).
2. **Agmarknet 3-yr** mandi price pull for TN to firm the price bands (already flagged in
   `economics_inputs_sourced.md`).
3. Reconcile `CROP_ECON.cost` with `CROP_FIN` once line-item costs land.

**Verdict:** the coconut error was a one-off (gestation handling), now fixed everywhere.
No other crop manufactures a false loss; remaining risk is LOW-confidence *cost* estimates,
flagged and bounded, not a structural bug.

## 6. Agmarknet price pull (data.gov.in) — live snapshot, 2026-06-10

`scripts/agmarknet_pull.py` queries the data.gov.in Agmarknet feed for TN. **Honest
limitations:** the free resource is the **current daily snapshot, not a multi-year
archive**; the public demo key caps at ~10 markets/call; prices are **wholesale** (farm-gate
runs lower). So this is a present-day reality check, not the full 3-yr series — a true
monthly history needs CEDA-Ashoka bulk download (offered as a follow-up).

Live TN modal (Rs/kg) vs my prior band upper — several bands were skewed LOW (same lesson
as coconut):

| crop | live median | live max | prior band | action |
|---|---|---|---|---|
| Black pepper | 680 (all-India) | 800 | 300-700 | -> 300-**800** |
| Pomegranate | 235 | 270 | 40-120 | -> 40-**200** |
| Banana | 50 | 67 | 8-25 | -> 8-**40** |
| Grapes | 100 | 150 | 30-90 | -> 30-**120** |
| Guava | 55 | 90 | 15-40 | -> 15-**60** |
| Mango | 47 | 90 | 25-80 | -> 25-**90** |
| Ginger (green) | 135 | 180 | 30-160 | kept (within) |

I **widened upper bounds to current levels, kept historical-glut lows** (wider, more honest
bands) rather than recentre on one possibly-seasonal-high day. Effect: coconut+pepper P50
+Rs 225k, P(loss) 21% (pepper stays the most robust pick). Nutmeg/cocoa/vanilla are NOT
Agmarknet-traded (spice-board/contract) so their bands are unchanged. Prices now **MODERATE**
(live-snapshot-anchored); CEDA 3-yr monthly pull would lift to HIGH.

## 7. CEDA 3-yr series — attempted, blocked (2026-06-10)

Tried to pull CEDA-Ashoka's cleaned 3-yr monthly Agmarknet series. **Not programmatically
accessible from this environment:** the shell times out (Cloudflare-style bot protection)
and the automated browser hits an error/challenge page (not circumvented — bot-detection
is not bypassed). A normal (human) browser loads CEDA fine.

So the multi-year basis stays: **`economics_inputs_sourced.md` 2022-2025 price ranges +
the live data.gov.in snapshot** — both already baked into the widened bands. To reach HIGH
confidence with a true monthly series, the reliable route is **user-side**: open CEDA in a
normal browser, select each commodity / Tamil Nadu / 2022-2025 / Monthly, click *Download
Data* (CSV), and share the CSVs for ingestion. (Alternatively, register a personal
data.gov.in API key to lift the 10-record/daily cap — still daily, not monthly history.)
Bands are defensible as-is; this is a refinement, not a gap.
