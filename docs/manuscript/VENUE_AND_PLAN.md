# Target venue + submission plan

## Recommendation (primary → backup), with reasoning

The honest shape of this paper — a **coupled, transparent design→microclimate→disease→profit decision framework** whose headline scientific result includes an *honest negative* (cross-macroclimate transfer fails) and which is **not yet locally validated** — should steer venue choice. Lead with the systems/decision-framework framing, not a "new ML method" framing, and don't oversell the prediction in the target regime.

| Rank | Venue | IF (2025) | Why it fits | Risk |
|---|---|---|---|---|
| **Preprint (do first)** | **EarthArXiv** (or arXiv cs.LG/eess) | — | Establishes priority + a citable DOI immediately; lets you circulate while a journal review runs. Zero downside. | none |
| **Primary** | **Agricultural Systems** (Elsevier) | ~6.1, Q1 | Scope is *interactions among components of agricultural systems* and integrative, multi-disciplinary decision modelling — an near-perfect match for a six-layer coupled chain with propagated uncertainty. Values systems thinking and honest limitation analysis over architectural novelty. | Expects rigour on assumptions + sensitivity; will want the cross-climate limitation framed as a result (which we do). |
| **Backup / first-paper-friendly** | **Agroforestry Systems** (Springer) | ~2.2, Q1-ish in domain | The natural disciplinary home; more forgiving of a single-site applied study and of the "method + honest limits" posture; good if Agricultural Systems wants more validation than we can supply pre-sensor. | Lower IF; less ML-method appetite. |
| **Stretch (later, after local data)** | **Computers and Electronics in Agriculture** (Elsevier) | ~8.9, Q1 | Explicitly covers computerised decision-support aids and simulation models. Highest visibility. | Highest bar; reviewers there will likely want the method to *demonstrably work in the target regime* — i.e. local sensor validation. Better as a v2 target once year-1 data lands. |

**Bottom line:** post an **EarthArXiv preprint now**, submit to **Agricultural Systems** as primary; if it's deemed too applied/under-validated, **Agroforestry Systems** is the safe home. Hold **Computers and Electronics in Agriculture** for a stronger v2 after on-plot data closes the transfer gap.

## What this draft still needs before submission

**Cheap / doable now (no new data):**
- [x] **Full 596-site LOSO done** → `reports/loso_full_metrics.json` (dT_mean +48.7% skill / MAE 0.41 °C; dT_max +48.1%; dVPD +55.8%; coverage 0.76–0.82). Inserted in §5 (Table 1). Note: per-site R² is numerically unstable (near-zero within-site variance) — report skill, not R², for LOSO.
- [ ] Verify every **[verify]** citation (DOIs, exact venue/year) — especially Lembrechts/SoilTemp, De Frenne 2021 review, Hardwick 2015, Pylianidis 2021, Romano 2019, dataset authorship for SAFE / La Jarda.
- [ ] Add a **methods figure** (the 6-layer schematic) and ensure Figs 1–6 are publication-resolution with captions.
- [ ] Add a short **related-work** paragraph contrasting explicitly with ForestTemp (we extend offset→agroforestry-design→downstream) and with crop-suitability/digital-twin tools (we add the microclimate + disease coupling).
- [ ] **Per-climate (Mondrian) conformal** experiment to show whether coverage can be restored out-of-climate — strengthens the uncertainty story and pre-empts a reviewer ask.
- [ ] Tighten one disease/variety table against ECOCROP/TNAU so at least the headline crops are well-sourced.

**Needs data (defer; frame as future work — already done in §9):**
- [ ] Any in-regime (warm-night / dry-zone tropical) training point, or on-plot loggers, for genuine local validation.
- [ ] Multi-year mandi price series + per-crop cost line items to lift economics to HIGH.

## Authorship / logistics
- Single author (Leo Antony, independent). Consider adding a domain co-author (agronomy/forestry) — helps with both the envelope tables and reviewer credibility.
- Data + code already openly structured (Zenodo sources, committed scripts, ADRs); add a "Code & data availability" statement pointing to the GitHub repo and a tagged release at submission.
- License is MIT; fine for code. Confirm dataset redistribution terms (we don't redistribute raw data — only build scripts — which is the safe posture).

## Suggested timeline
1. **This week:** finish full-LOSO insert + citation verification + methods figure → post EarthArXiv preprint.
2. **+2–3 weeks:** Mondrian-conformal experiment + envelope sourcing + polish → submit to Agricultural Systems.
3. **Year 1 (with sensors):** local validation → v2 targeting Computers and Electronics in Agriculture.
