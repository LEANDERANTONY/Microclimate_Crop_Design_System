# Section order and heading review

Purpose: assess whether the current manuscript has the usual sections expected in a journal paper, whether the heading order is coherent, and what to adjust before editing the Word submission. This file is only a review guide; the Word manuscript is not changed.

## Current Section Order

Current manuscript structure:

1. Title
2. Author / affiliation
3. Manuscript draft note
4. Highlights
5. Abstract
6. Keywords
7. Introduction
   - 1.1 Forest and agroforestry microclimate: the offset paradigm
   - 1.2 Crop suitability modelling
   - 1.3 Disease as a microclimate-driven layer
   - 1.4 Uncertainty, transfer, and agricultural digital twins
   - 1.5 Research gap and objectives
8. Study site
9. Methods
   - 3.1 Layer 1 - design -> microclimate
   - 3.2 Layer 2 - microclimate -> disease risk
   - 3.3 Layer 3 - viability
   - 3.4 Layers 4-5 - economics and finance
   - 3.5 Layer 6 - uncertainty, and inverse design
   - 3.6 Validation protocol
10. Data
11. Result - within-climate transfer is skilful
12. Result - cross-macroclimate transfer fails, and the model says so
   - 6.1 A handful of local observations restores calibrated intervals
13. Result - application to Anaikadu
14. Discussion
15. Limitations and future work
16. Reproducibility
17. References
18. Data and code availability
19. Author contributions
20. Funding
21. Conflicts of interest
22. Acknowledgements
23. Figure captions

## Overall Verdict

The manuscript is coherent and readable, but the order is not yet ideal for a polished journal submission.

Main issue:

- `Data` appears after `Methods`, even though validation methods and model definitions depend heavily on the datasets. For most journals, this is acceptable but slightly awkward. It would read cleaner as `Materials and Methods`, with `Study site` and `Data sources` before the model description.

Second issue:

- The Results headings are strong but slightly argumentative: "cross-macroclimate transfer fails, and the model says so" is memorable, but some journals prefer neutral heading language. The same idea can be kept with a more formal title.

Third issue:

- `Reproducibility`, `Data and code availability`, and `Figure captions` are currently mixed into the back matter. This is fine for a preprint, but for journal submission they should be arranged according to the target journal's required format.

## Usual Paper Sections: Present Or Missing?

| Usual section | Present? | Current location | Comment |
|---|---|---|---|
| Title | Yes | Top | Strong but long; acceptable for preprint, may be shortened for journal. |
| Author affiliation | Yes | Top | Needs final institutional wording if any. |
| Highlights | Yes | Before Abstract | Good for Elsevier-style journals. |
| Abstract | Yes | Before Introduction | Strong and complete. |
| Keywords | Yes | After Abstract | Good. |
| Nomenclature | Not yet in Word | Planned separately | Add if we separate equations and use many symbols. |
| Introduction | Yes | Section 1 | Well structured. |
| Literature review / related work | Yes | Section 1 subsections | Integrated into Introduction; no separate section needed. |
| Research gap / objectives | Yes | Section 1.5 | Good and necessary. |
| Study site | Yes | Section 2 | Good. Could become part of Materials and Methods. |
| Materials / Data | Yes | Section 4 | Should probably move before model methods or become Section 3. |
| Methods | Yes | Section 3 | Strong. Could be renamed `Materials and Methods`. |
| Validation protocol | Yes | Section 3.6 | Good. Could be moved after Data so folds/regimes are clearer. |
| Results | Yes | Sections 5-7 | Strong, but headings can be made more formal. |
| Discussion | Yes | Section 8 | Good. |
| Limitations / future work | Yes | Section 9 | Good and honest; could be a subsection inside Discussion if journal prefers. |
| Conclusion | No | Missing | Recommended. The paper currently ends with limitations/reproducibility, but a concise conclusion would help. |
| Reproducibility | Yes | Section 10 | Good for computational paper; may merge with Data/code availability. |
| Data/code availability | Yes | Back matter | Required; keep. |
| Author contributions | Yes | Back matter | Required by many journals. |
| Funding | Yes | Back matter | Required. |
| Conflicts of interest | Yes | Back matter | Required. |
| Acknowledgements | Yes | Back matter | Good. |
| References | Yes | Before back matter | Should usually come after declarations depending on journal. |
| Figure captions | Yes | End | Fine for submission package; in final Word figures may be embedded. |

## Main Missing Section

### Add a short Conclusion

Current issue:

The manuscript has a good Discussion and Limitations section, but it lacks a crisp final conclusion. Many journals expect one, and readers benefit from a final paragraph that states what was proven, what was not proven, and what the next data step is.

Suggested placement:

- After `9. Limitations and future work`
- Before `10. Reproducibility`

Suggested title:

`10. Conclusion`

Then renumber Reproducibility to `11`.

Suggested content:

```text
This work presents a confidence-labelled agroforestry design-to-profit framework that links controllable canopy and management decisions to microclimate offsets, disease risk, crop viability and risk-adjusted finance. Across 596 borrowed-label sites, the learned offset model is skilful within observed regimes, but strict leave-one-climate-out validation shows that cross-macroclimate transfer remains unresolved and that intervals lose calibration out of regime. Rather than treating this as a hidden weakness, the framework exposes it through OOD flags and uncertainty propagation, while few-shot conformal recalibration quantifies how a small number of local observations can restore interval honesty. Applied to Anaikadu, the physics-supported and sensitivity-robust result favours coconut with black pepper as the current actionable system, while nutmeg remains conditional on local sensing confirming a cooler under-canopy microclimate. The next decisive step is in-regime field data, which would turn the current honest decision framework into a locally calibrated digital twin.
```

## Recommended Journal-Style Section Order

If preparing a polished journal version, use this order:

1. Title
2. Author and affiliation
3. Highlights
4. Abstract
5. Keywords
6. Nomenclature
7. Introduction
   - Background: microclimate offsets
   - Crop suitability and disease
   - Uncertainty, transfer and digital twins
   - Research gap and objectives
8. Materials and Methods
   - Study site
   - Data sources and feature construction
   - Layer 1: microclimate model
   - Layer 2: disease model
   - Layer 3: viability
   - Layers 4-5: economics and finance
   - Layer 6: uncertainty and inverse design
   - Validation protocol
9. Results
   - Within-regime transfer
   - Cross-regime transfer and OOD behaviour
   - Few-shot recalibration
   - Anaikadu application
   - Economics, finance and risk
10. Discussion
11. Limitations and future work
12. Conclusion
13. Data and code availability
14. Author contributions
15. Funding
16. Conflicts of interest
17. Acknowledgements
18. References
19. Figure captions / supplementary material

Why this is better:

- It puts data before model details.
- It reduces section-number jumps between Methods and Data.
- It groups all Results under one umbrella.
- It adds the missing Conclusion.
- It makes back matter look more like a journal paper.

## Suggested Heading Edits

Current heading:

`5. Result - within-climate transfer is skilful`

Suggested:

`5.1 Within-regime transfer performance`

Why:

More formal and fits under a single `5. Results` heading.

Current heading:

`6. Result - cross-macroclimate transfer fails, and the model says so`

Suggested:

`5.2 Cross-regime transfer and out-of-distribution behaviour`

Why:

Keeps the honest negative result but sounds less editorial.

Current heading:

`6.1 A handful of local observations restores calibrated intervals`

Suggested:

`5.3 Few-shot conformal recalibration`

Why:

Shorter, cleaner, and matches the method name.

Current heading:

`7. Result - application to Anaikadu (physics + robust ranking carry the decision)`

Suggested:

`5.4 Anaikadu case study: crop and system ranking under uncertainty`

Why:

More journal-like and still clear.

Add a dedicated economics result subsection:

Suggested heading:

`5.5 Economics, finance and risk`

Why:

The title promises crop profit under uncertainty, and the pipeline includes layers 4-6. The economics should therefore read as a result in its own right, not just as a compressed paragraph at the end of the Anaikadu case study.

What this subsection should cover:

- Yield basis: explain that `attainable_yield = reference_yield x growth_fit x (1 - disease_risk)`, so yield is derived from agronomic reference values and modelled suitability/disease penalties.
- Price and cost basis: explain that prices are banded, not single-point forecasts, and costs are validated against NHB/TNAU and related sources where possible.
- Finance outputs: report NPV, IRR and payback for coconut only, coconut + pepper, coconut + nutmeg, coconut + banana, and timber options if retained.
- Risk outputs: report Monte Carlo `P(loss)` and downside behaviour, not only expected NPV.
- Decision interpretation: make clear that the finance layer turns "can the crop grow?" into "is the system worth planting under uncertainty?"

Suggested table companion:

`System | Yield basis | NPV | IRR | Payback | P(loss) | Main risk | Confidence`

Suggested short result claim:

`Coconut + black pepper is not only the most robust agronomic ranking under the temperature sweep; it is also the strongest financial system among the annual-cash options, because it bears earlier, remains viable across the temperature band, and has lower loss probability than nutmeg.`

Current heading:

`10. Reproducibility`

Suggested:

`11. Reproducibility and code availability`

Why:

If a separate Data/code availability declaration remains in the back matter, keep this section focused on computational reproducibility in the main text.

## Preprint vs Journal Version

For EarthArXiv preprint:

- Current order is acceptable.
- Add `Nomenclature` and `Conclusion`.
- Replace the draft note with the preprint disclaimer.
- Keep figure captions at the end or embed figures inline.

For journal submission:

- Use the recommended journal-style order.
- Convert `Result - ...` sections into subsections under one `Results` heading.
- Follow the journal's required declaration order.
- Move long planning/provenance notes out of the manuscript body.

## Title Review

Current title:

`From canopy design to crop profit under uncertainty: an honesty-first agroforestry microclimate model with explicit transfer limits, applied to a smallholder coconut farm in Tamil Nadu`

Verdict:

Strong but long. It is excellent for a preprint because it tells the full story, but it may be too long for a journal.

Possible shorter journal title:

`From canopy design to crop profit: an uncertainty-aware agroforestry microclimate model with explicit transfer limits`

Alternative with site:

`An uncertainty-aware agroforestry microclimate model with explicit transfer limits: application to a coconut farm in Tamil Nadu`

Recommendation:

- Keep current title for preprint.
- Use a shorter title for journal submission.

## Abstract Review

Verdict:

Strong and complete, but long. It includes methods, data, validation, negative transfer result, Anaikadu result and contribution. That is good for a preprint, but journals with strict abstract word limits may require compression.

Suggested compression target:

- 250-300 words for most journals.
- Keep the core sequence: problem -> method -> validation -> transfer failure -> Anaikadu application -> contribution.

## Final Recommendation

The manuscript has almost all standard paper sections. The two structural improvements I would make before polishing the Word version are:

1. Add a `Nomenclature` section after Keywords.
2. Add a short `Conclusion` before Reproducibility / declarations.

For a journal submission, I would also reorganize the middle into:

```text
2. Materials and Methods
   2.1 Study site
   2.2 Data sources
   2.3 Model layers
   2.4 Validation

3. Results
   3.1 Within-regime transfer
   3.2 Cross-regime transfer
   3.3 Few-shot recalibration
   3.4 Anaikadu case study
   3.5 Economics, finance and risk
```

That structure would read more like a mature journal article while preserving the current scientific story.
