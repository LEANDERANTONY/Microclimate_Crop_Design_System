# Preprint submission package

*Everything needed to post the manuscript as a citable preprint. Recommended platform:
**EarthArXiv** (free, no endorsement required, ideal for agriculture / environmental /
earth-and-ecology work). Alternative: **arXiv** (cs.LG or eess.SP) — needs endorsement for
a first-time author in those categories, so EarthArXiv is the path of least resistance.*

---

## 1. Recommended platform — EarthArXiv

- Free; moderated (not peer-reviewed); issues a permanent DOI; indexed by Google Scholar.
- Scope explicitly covers agriculture, environmental science, ecology, and applied earth-data methods.
- Allows later "published-in-journal" linking, so the preprint and the journal version stay connected.
- Submit at the EarthArXiv site (ESSOAr/California Digital Library platform); create an account, "Submit a preprint," upload the PDF, paste the metadata below.

## 2. Files to upload

1. **Manuscript PDF** — generated from `docs/manuscript/manuscript.md` (see §5 for how to produce it). One file, figures embedded or appended.
2. **Figures** — `figures/fig0_pipeline.png` … `fig6_cashflow.png` (embed in the PDF; EarthArXiv takes a single combined PDF).
3. *(optional)* link to the code/data repository in the metadata rather than uploading code.

## 3. Metadata sheet (copy-paste at submission)

- **Title:** From canopy design to crop profit under uncertainty: an honesty-first agroforestry microclimate model with explicit transfer limits, applied to a smallholder coconut farm in Tamil Nadu
- **Author:** Leo Antony (Independent Researcher, Anaikadu, Pattukkottai, Thanjavur District, Tamil Nadu, India). ORCID: *[add — register free at orcid.org; recommended before posting].*
- **Corresponding email:** antony.leander@gmail.com
- **Discipline / subject:** Agriculture; Environmental Sciences; Ecology; Applied Machine Learning (pick the closest EarthArXiv subject terms, e.g. "Agriculture", "Environmental Sciences", "Life Sciences").
- **Keywords:** agroforestry; microclimate; temperature offset; machine learning; transferability; conformal prediction; crop suitability; decision support; coconut; Tamil Nadu.
- **License:** **CC-BY 4.0** (recommended — maximises reuse and is accepted by all target journals' preprint policies).
- **Abstract:** paste the Abstract from `manuscript.md` (one paragraph).
- **Comments / notes field:** "Non-peer-reviewed preprint. Code, data-build scripts, and an interactive results report are openly available; see the manuscript's Data and Code Availability section."
- **Competing interests:** "The author declares no competing financial interest. The application site is the author's prospective farm; the model's confidence-labelling and pre-registered transfer tests mitigate this."
- **Funding:** None.

## 4. Front-matter disclaimer (add one line to the top of the manuscript before export)

> *This is a non-peer-reviewed preprint submitted to EarthArXiv. It has not yet undergone peer review. Subsequent peer-reviewed versions may differ. Corresponding author: Leo Antony (antony.leander@gmail.com).*

*(The manuscript already carries a v0.2 status line; replace it with the disclaimer above for the public preprint, keeping the pipeline-provenance note.)*

## 5. Producing the PDF (one remaining manual/packaging step)

The manuscript lives as Markdown (`manuscript.md`). To get a clean PDF:
- **Easiest:** open `manuscript.md` in any Markdown editor (Typora, VS Code + "Markdown PDF", or paste into Google Docs) and export to PDF; insert the seven figures at their captioned positions.
- **Reproducible (Pandtoc):** `pandoc manuscript.md -o preprint.pdf` with a LaTeX engine; add `--toc` and a reference style if desired. (Not run here — no LaTeX in this environment; do locally or I can generate a `.docx` next session with figures embedded, which you can "Save as PDF".)
- Ensure **Figs 1–6 are exported at journal DPI** (≥300 dpi) before embedding; `fig0_pipeline.png` is already 150 dpi and can be regenerated higher if needed via `scripts/make_pipeline_figure.py`.

## 6. Pre-post checklist

- [ ] Register an **ORCID** and add it to the metadata.
- [ ] Confirm the four **Zenodo dataset "Cite as" depositor names** (refs 11–14) and finalise those reference lines.
- [ ] Export Figs 1–6 at ≥300 dpi; embed all seven figures in the PDF.
- [ ] Swap the v0.2 status line for the preprint disclaimer (§4).
- [ ] Generate the manuscript PDF (§5).
- [ ] Post to EarthArXiv; record the returned **DOI** in the repo (and in the journal cover letter where it says "DOI to follow").
- [ ] *(then)* submit the journal version + `cover_letter.md` to the chosen primary venue.

## 7. Sequencing

Post the preprint **first** (establishes priority + gives a citable DOI), then submit to the journal. Most target venues (Ecological Informatics, Agricultural Systems, Smart Agricultural Technology, Scientific Reports, MDPI) explicitly permit prior preprinting on a non-commercial server like EarthArXiv — but the cover letter discloses it anyway (it does).
