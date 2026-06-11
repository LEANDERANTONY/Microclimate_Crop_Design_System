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
- [x] **Citations verified** (June 2026, PubMed + publisher records): De Frenne 2019 (10.1038/s41559-019-0842-1), De Frenne 2021 review (10.1111/gcb.15569), Haesen/ForestTemp (10.1111/gcb.15892), Lembrechts/SoilTemp (10.1111/gcb.15123), Zellweger (10.1016/j.tree.2018.12.012), Hardwick 2015 (10.1016/j.agrformet.2014.11.010), Pylianidis 2021 (10.1016/j.compag.2020.105942), Romano CQR (arXiv:1905.03222), Chen&Guestrin XGBoost (10.1145/2939672.2939785). Datasets cited by Zenodo DOI — still confirm exact depositor names against each record's "Cite as" before submission.
- [x] **Methods figure done** — `figures/fig0_pipeline.png` (6-layer schematic with confidence chips + inverse-design loop), referenced in §3. *(Still: bump Figs 1–6 to publication DPI + finalise captions.)*
- [x] **Related-work** positioning written into §1 (contrasts ForestTemp/offset ecology, crop-suitability mapping, agricultural digital twins; our extension = managed-design control + disease coupling + downstream profit + honest transfer limits).
- [x] **Mondrian / few-shot conformal experiment done** → `reports/mondrian_metrics.json`, §6.1 + Table 2: ~5–25 held-out-climate calibration points restore coverage from 0.08 to ~0.80. Quantifies the value of on-plot sensing.
- [x] **Headline-crop envelopes sourced** to FAO ECOCROP (pepper, id 1714) + PROSEA (nutmeg) → `reports/crop_envelopes_ecocrop.md`. Material effect: pepper now the robust clear pick (NPV ₹565k, top across the full temp sweep); nutmeg downgraded to conditional (thermal-edge). Manuscript §3.3/§7 + Table 3 updated.

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
