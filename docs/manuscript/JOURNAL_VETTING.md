# Journal vetting + honest readiness assessment

*June 2026. Purpose: decide where to submit, and judge — against the actual published
literature — whether the manuscript (`manuscript.md`) meets the bar or needs more first.
Impact factors are the 2024 JCR set released June 2025 (latest available).*

---

## TL;DR

- The **methods and scope are current and publishable** — venues in this space published,
  in 2024–2025, conformal-prediction-for-crop-decision-support (in *Computers and Electronics
  in Agriculture* itself), single-site agroforestry-ML suitability studies, and agroforestry
  decision-support systems. We are not proposing anything outside the field's accepted shape.
- The manuscript **structure already meets journal standards** (IMRaD + Highlights, methods by
  layer, skill-scored validation, limitations, data/code availability, verified DOIs).
- The **two things that cap our ceiling** are: (1) the headline application is **out-of-distribution
  and not locally validated** (we flag it honestly, but high-tier reviewers may still want a working,
  in-regime result), and (2) **single author, independent, no institutional affiliation, site = the
  author's prospective farm** — not disqualifying at sound-science venues, but a credibility signal
  some Q1 reviewers weigh.
- **Realistic landing zone: a solid Q1 mid-tier (IF ~5–7).** A top-tier shot (CEA 8.9 / AI-in-Ag 12.4)
  is possible but higher-risk without local data; a safe floor (Sci Reports / PLOS ONE / MDPI, IF ~2.6–3.9)
  is essentially assured if framed well. **Recommended: preprint now → submit to a ~5–7 IF Q1.**

---

## Candidate journals

| Journal | Publisher | IF (2024) | Quartile | OA / APC | Fit to our paper | Risk for us |
|---|---|---|---|---|---|---|
| **Artificial Intelligence in Agriculture** | KeAi (OA) | **12.4** | Q1 (#1 Ag-Multidisc.) | OA, low/sponsored APC | AI methods in agriculture — squarely on-scope; likes applied + methodological | **High bar**: new high-IF darling, competitive; honest-negative + single-site a hard sell as a *headline*; reframe as a method with a strong result |
| **Computers & Electronics in Agriculture** | Elsevier | **8.9** | Q1 | hybrid (OA optional) | Decision-support aids + simulation models = exact scope; **published conformal-DSS in 2025** | Stretch; reviewers may want in-regime validation / a working system, not a flagged extrapolation |
| **Ecological Informatics** | Elsevier | **7.3** | Q1 | hybrid | Offset ML + transfer + conformal + OOD is textbook ecoinformatics; our microclimate-modelling core fits best here | Economics/farm-decision half is slightly off their centre — lead with the ecoinformatics framing |
| **Agricultural Systems** | Elsevier | **6.1** | Q1 | hybrid | "Interactions among components of agricultural systems" — the six-layer coupled chain + honest systems analysis fit very well | Wants rigour on assumptions + sensitivity (we have it); fine on single-site if framed as a systems method |
| **Smart Agricultural Technology** | Elsevier (OA) | **5.7** | Q1 | OA, ~$1,800 | Companion to CEA for *applied* smart/decision tools; explicitly welcomes decision support; faster, more applied bar | Lowest-friction Q1 fit; APC is the main cost |
| **Agricultural & Forest Meteorology** | Elsevier | **5.7** | Q1 | hybrid | Canopy micrometeorology (radiation transfer, the offset) is *literally* their core | Would want more micrometeorological depth (energy balance) and less economics; partial fit |
| **Scientific Reports** | Nature (OA) | **3.9** | Q1 | OA, ~$2,690 | Sound-science, multidisciplinary; single-site + honest-negative explicitly acceptable | Lower prestige-per-IF; APC high |
| **Agronomy / Agriculture** | MDPI (OA) | **3.4 / 3.6** | Q1 | OA, ~$2,600 | Fast, broad; applied agronomy + modelling welcome | Perceived prestige varies; fast turnaround is a plus |
| **Agroforestry Systems** | Springer | **2.2** | Q1-ish (domain) | hybrid | Disciplinary home; forgiving of single-site applied work | Low IF; least "AI/methods" appetite |
| **PLOS ONE** | PLOS (OA) | **2.6** | Q2 | OA, ~$1,930 | Sound-science floor; single-site fine | Lowest IF of the shortlist; safe fallback |

*(APC figures are approximate list prices; waivers/discounts often available, especially for independent authors — worth asking.)*

---

## What the comparable literature actually looks like (the bar)

- **Conformal prediction for crop decision support** was published in *Computers and Electronics in
  Agriculture* (2025) — so our uncertainty machinery is not just acceptable but *current* at the
  flagship venue. Group-conditional (Mondrian) conformal for crop/weed tasks exists too (our §6.1 is
  in good company).
- **Single-site agroforestry-ML suitability** studies are published (e.g. an olive–maize agroforestry
  land-suitability ML study, 2024; agroforestry suitability for site-specific interventions, MDPI). So
  a single focal site is **not** disqualifying — the field accepts it, especially with a clear method.
- **Agroforestry decision-support systems** are an active, publishable topic (a 2025 DSS paper in an IOP
  environmental journal). Our end-to-end chain is differentiated by the disease coupling, the inverse
  design, and the honesty-first transfer analysis.
- **What the strongest papers have that we partly lack:** multi-site or in-regime validation, and a
  *working* (not flagged-as-extrapolating) headline result. That is exactly our gap — and exactly what
  one season of on-plot data fixes.

**Verdict on standards:** our paper *meets* the structural and methodological standards of Q1 venues in
this space. Its ceiling is set by validation scope, not by method or writing quality.

---

## Honest gap analysis — does our paper meet the bar?

**Meets the bar (strengths reviewers will credit):**
- Clear novelty: the *coupled* design→microclimate→disease→viability→profit chain with disease coupled
  to the engineered microclimate, plus inverse design — not previously assembled end-to-end.
- Methodologically current: gradient-boosted quantile offsets + **conformal intervals** + **OOD flag**;
  leave-one-**site** and leave-one-**climate** out; skill-vs-baseline reporting; a tested-and-rejected
  hybrid (a genuine ablation).
- A quantified, decision-relevant uncertainty result (§6.1: ~5–25 local points restore coverage).
- Real, openly-sourced data across two macroclimates + an open-canopy regime (596 sites); reproducible
  pipeline; verified DOIs; honest limitations.

**Caps the ceiling (what high-tier reviewers will push on):**
1. **No in-regime / local validation.** The headline farm application is OOD; we flag it, but a CEA/AI-in-Ag
   reviewer may say "validate where you apply it." → *Mitigation:* lead with the **method + the honest
   transfer finding** as the contribution (not the Anaikadu numbers); or hold top-tier until year-1 sensors.
2. **Single author, independent, no affiliation; site = author's farm.** → *Mitigation:* the conflict-of-interest
   statement + pre-registered transfer tests already address bias; **a domain co-author** (agronomy/forestry)
   would materially raise credibility and help the envelope tables.
3. **Soft lower layers.** Disease/economics are mechanistic/banded, not incidence- or trial-calibrated. → Already
   confidence-flagged; fine if reviewers accept the "comparisons reliable, absolutes indicative" framing.
4. **Breadth vs depth.** Six layers in one paper is ambitious; a micrometeorology-focused venue (AFM) may want
   more depth on the offset physics. → Choose venue to match (systems/AI venues reward the breadth; AFM doesn't).

**Net:** the paper is **submission-ready for a Q1 mid-tier (IF ~5–7)** as-is. For a top-tier (8.9–12.4) it is
*plausible but risky* without either (a) reframing hard as a methods/negative-result contribution, or (b) adding
in-regime data. It comfortably *exceeds* the bar for the safe floor (Sci Reports / MDPI / PLOS ONE).

---

## Recommendation

1. **Post a preprint now** (EarthArXiv or arXiv cs.LG/eess) — priority + citable DOI, zero downside.
2. **Primary submission — pick one of two strategies:**
   - *Ambitious:* **Ecological Informatics (7.3)** or **Agricultural Systems (6.1)** — both Q1, both a strong
     scope match, both realistic for a well-argued methods+systems paper with an honest transfer result.
     Ecological Informatics is the best intellectual fit for the offset/transfer/conformal core; Agricultural
     Systems for the coupled-systems + decision framing.
   - *Faster / lower-friction:* **Smart Agricultural Technology (5.7, OA)** — applied decision-support scope,
     quicker, companion to CEA.
3. **Backup:** **Scientific Reports (3.9)** or **Agronomy (3.4)** — sound-science, single-site-friendly, fast.
4. **Hold for v2 (after on-plot sensors):** **Computers and Electronics in Agriculture (8.9)** or
   **Artificial Intelligence in Agriculture (12.4)** — target these once the model is validated in-regime;
   that single addition moves them from "risky" to "competitive."
5. **Two cheap credibility multipliers, in priority order:** (a) recruit a **domain co-author**; (b) bump figures
   to journal DPI and write a tight cover letter that **frames the negative transfer result as the contribution**,
   pre-empting the "validate where you apply it" critique.

**One-line answer to "does ours meet the standard?"** — Yes for a respectable Q1 (IF ~5–7); the writing and
methods are there. The only thing standing between us and the very top tier is in-regime validation data, which
is the same thing that de-risks the farm decision — so it is worth waiting for if maximum impact factor is the goal,
and not worth waiting for if getting a solid Q1 paper out now is the goal.

---

### Sources (journal metrics, June 2025 JCR set; comparable literature)
- Artificial Intelligence in Agriculture IF 12.4 — KeAi; Computers & Electronics in Agriculture IF 8.9 — journalmetrics.org
- Ecological Informatics IF 7.3; Agricultural Systems IF 6.1; Smart Agricultural Technology IF 5.7; Agric. & Forest Meteorology IF 5.7 — journalmetrics.org / Elsevier
- Scientific Reports IF 3.9; PLOS ONE IF 2.6; Agronomy IF 3.4; Agriculture IF 3.6 — Nature / PLOS / MDPI announcements
- Comparable work: conformal prediction for crop production decision support (Computers and Electronics in Agriculture, 2025); olive–maize agroforestry suitability via ML (MDPI, 2024); agroforestry decision-support system (IOP, 2025); group-conditional conformal for crop/weed (2023).
