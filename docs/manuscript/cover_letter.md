# Cover letter

*Primary target: **Ecological Informatics** (Elsevier). Retargeting notes for Agricultural
Systems / Smart Agricultural Technology are at the foot of this letter.*

---

Leo Antony
Independent Researcher
Anaikadu (Pattukkottai), Thanjavur District, Tamil Nadu, India
antony.leander@gmail.com

[Date]

To the Editors,
*Ecological Informatics*

**Re: Submission of an original research article — "From canopy design to crop profit under uncertainty: an honesty-first agroforestry microclimate model with explicit transfer limits, applied to a smallholder coconut farm in Tamil Nadu."**

Dear Editors,

Please consider the enclosed manuscript for publication in *Ecological Informatics*. The work sits squarely within the journal's scope of computational ecology and the application of machine learning to environmental data: it builds a transferable, uncertainty-quantified model of the **sub-canopy microclimate offset** — the difference between under-canopy and free-air conditions — and chains it to downstream ecological and agronomic consequences for a real land-use decision.

**What the paper does.** We assemble an end-to-end, confidence-labelled pipeline that maps a *controllable* agroforestry design (overstorey species, canopy density, windbreak, drainage, variety, fruiting time) to the microclimate it creates, then to disease risk, crop viability, and risk-adjusted profit. Mechanistic physics carries the variables it governs exactly (Beer–Lambert light, shelterbelt wind); machine learning is confined to the temperature and vapour-pressure-deficit offsets, where we use gradient-boosted quantile regression with conformalised prediction intervals and an explicit out-of-distribution flag. Uncertainty is propagated end-to-end to a profit distribution, and an inverse-design step searches the controllable design for the risk-aware optimum.

**Why we think it is a good fit and a genuine contribution.** Three threads — forest-microclimate offset modelling (e.g. De Frenne et al. 2019; Haesen et al. 2021), crop-suitability mapping, and agricultural digital twins — have not previously been joined, and never with the design levers a farmer actually controls or with disease coupled to the engineered microclimate. Beyond the integration, our central methodological contribution is **honesty about transfer**. Trained on real sub-canopy loggers across two macroclimates plus an open-canopy regime (596 sites), the learned offset is skilful within climate (leave-one-site-out skill +49% over a mean-offset baseline, calibrated intervals) but we show, via a stricter **leave-one-climate-out** test, that it **fails across macroclimates** (negative skill on a held-out climate; interval coverage collapsing from ~0.8 to ~0.1–0.5). A physics-prior hybrid we implemented does not rescue this. Rather than hide this, the model flags its own extrapolation, and we further show (a few-shot recalibration experiment) that **~5–25 in-regime observations restore calibrated intervals** — turning the limitation into a quantitative, actionable specification for field sensing. We believe this kind of pre-registered, reported negative-transfer result is exactly the discipline ecological ML needs as it moves from mapping to decision support, and that it is a useful contribution in its own right.

**Statements.** This manuscript is original, has not been published previously, and is not under consideration elsewhere. It is single-authored. All data are openly sourced (Zenodo microclimate datasets; Google Earth Engine remote sensing; public Indian agricultural cost/price sources) and the full analysis pipeline, tests, and decision records are openly available; a tagged code release will accompany any revision. A preprint has been deposited on EarthArXiv (DOI to follow). The author declares no competing financial interest; we note transparently that the application site is the author's prospective farm, and the manuscript's confidence-labelling and pre-registered transfer tests are designed precisely to keep that interest from biasing the reported conclusions.

**Suggested reviewers** (experts in microclimate offset modelling and ecological ML; please exclude any with a conflict): researchers in the De Frenne / Lembrechts / Haesen forest-microclimate group (Ghent University; University of Antwerp; KU Leuven), F. Zellweger (WSL, Switzerland), and authors working on conformal prediction for agricultural decision support. We are happy to provide specific names and contacts on request.

We hope you find the work of interest and look forward to the reviewers' feedback.

Sincerely,
Leo Antony

---

## Retargeting notes (swap before sending)

**If submitting to *Agricultural Systems* instead:** change the scope sentence to emphasise the **coupled-systems** framing — "interactions among components of agricultural systems" — and that the paper integrates biophysical microclimate, disease, and farm economics into one decision model with propagated uncertainty. Drop the "computational ecology" phrasing; keep the honest-transfer and inverse-design points.

**If submitting to *Smart Agricultural Technology* instead:** lead with the **applied decision-support tool** angle (a farmer-facing design→profit optimiser with honest uncertainty and an interactive report), note it is a companion-scope fit to *Computers and Electronics in Agriculture*, and that the system is reproducible and deployable. Keep the transfer-limits result as the scientific backbone.

**For all three:** keep the originality/competing-interest/data-availability statements verbatim; update the addressee and the one scope paragraph only.

**Do NOT send to top-tier (CEA 8.9 / AI-in-Agriculture 12.4) yet** — per `JOURNAL_VETTING.md`, hold those until in-regime (on-plot) validation data exists; the cover letter for those should foreground a *validated* result, which we will not have until year-1 sensors.
