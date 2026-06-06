# Disease Layer — Literature-Sourced Parameters

**Purpose.** Replace the literature-*shaped* (eyeballed) values currently in
`config.py` (`DISEASES`, `VARIETY_SUSCEPTIBILITY`) with literature-*sourced*
values, each citation traceable. This is a sourcing pass only — **no code was
edited and nothing was pushed.** Apply (or not) deliberately, in a later commit
with an ADR.

**Confidence.** Per project discipline, the entire disease layer remains **LOW
confidence / not locally calibrated**. These citations tighten the priors and
make them defensible; they do not make absolute risk numbers trustworthy.
Comparisons (wet vs dry bahar, variety A vs B) stay more reliable than any single
probability. Several pathogens have *no published cardinal-temperature triplet*
or *no LWD threshold* — sources give favourable ranges, optima, or RH bands
instead. Where a parameter is inferred rather than directly measured it is marked
**[inferred]**.

Site reminder (Pattukkottai): infection-relevant temperature `T` in the model is
`t_mean` of the fruiting/infection window; the humid risk window is the NE
monsoon (Oct–Dec), summers are hot/dry.

---

## Table 1 — Infection-model parameters

Columns: pathogen; the literature finding; sourced values for the model fields;
the current `config.py` value; and a note. Temperatures °C. "Disp." = dispersal
(rain/splash vs airborne/humidity). Ref numbers map to the reference list below.

### Pomegranate

**Bacterial blight — *Xanthomonas axonopodis* pv. *punicae*** (type `wetness`, rain-driven)
- Literature: optimum growth **29 ± 3 °C / ~30 °C**; disease present across **9–43 °C**; symptoms appear 3–4 d after infection at 30 °C and 60–70% RH; **positively & significantly correlated with RH and rainfall**; rapid in rainy months; spread by **rain splash**, irrigation, tools, insects. [R1, R2, R3]
- Sourced: t_min ≈ **10** (effectively inactive <9), t_opt **30**, t_max ≈ **42** [inferred from the 9–43 °C activity envelope]; LWD lwd_min **4 h**, lwd_sat **12 h** [inferred — no published LWD curve for Xap; keep current as plausible]; rain_driven **True**. [R1, R2, R3]
- Current config: t_min 15, t_opt 29, t_max 34, lwd 4→12, rain_driven True.
- Note: **t_max 34 is too low** — the pathogen is active well into the low-40s; raising t_max to ~42 matters for Pattukkottai summers. t_opt fine. LWD values are unsourced placeholders (no LWD study exists for Xap) — flag.

**Wilt — *Ceratocystis fimbriata*** (type `soil`, rain_driven False)
- Literature: **max soil colonisation at 25 °C** (89.7%), sharply lower at 15 °C (6.3%) and 35 °C (7.0%), **no growth at 10 °C or >40 °C**; favoured **18–30 °C + frequent rains**; **100% incidence at 50–70% soil moisture**. [R4]
- Sourced: t_min **15** (≈ no growth ≤10, weak at 15), t_opt **25**, t_max **38** [inferred — 0 above 40]; soil-moisture proxy via rh_min **75**, rh_sat **95** [inferred — model has no soil-moisture input; RH is a weak stand-in, see caveat]; rain_driven **arguably True** (frequent rains favour it). [R4]
- Current config: t_min 18, t_opt 28, t_max 38, rh_min 75, rh_sat 95, rain_driven False.
- Note: **t_opt should drop 28→25** (clear literature peak). Consider rain_driven True. The RH proxy is the weakest assumption in the whole table — wilt is driven by *soil* moisture (regulated by the user's bores), not air RH; this disease may not belong on the air-microclimate axis at all. Flag for design review.

### Grapes

**Downy mildew — *Plasmopara viticola*** (type `wetness`, rain-driven)
- Literature: primary infection needs **≥ ~8–12 h leaf wetness at 10–15 °C**; infection occurs over a wide range, **optimum ~19–24 °C** (zoospore release peaks 15–20 °C); classic "10-10-24" rule (≥10 °C, ≥10 mm rain, shoots ≥10 cm); free water **required**. [R5, R6]
- Sourced: t_min **10**, t_opt **22**, t_max **30** [inferred upper bound]; lwd_min **6** (shorter at warm temps, longer at cool), lwd_sat **10–12**; rain_driven **True**. [R5, R6]
- Current config: t_min 10, t_opt 23, t_max 30, lwd 4→10, rain_driven True.
- Note: Good match. Optionally raise lwd_min 4→6 (primary infection rarely below ~6 h). t_opt 22–23 both defensible.

**Powdery mildew — *Erysiphe necator*** (type `humidity`, rain_driven False)
- Literature: optimum **20–28 °C** (rapid growth 23–30 °C); range **~6–35 °C**, **inhibited >35 °C**; favoured by **high RH (~85% optimum)** and shade/poor aeration; **free water NOT required** (humidity sufficient); sporulation down to 40% RH. [R7, R8]
- Sourced: t_min **6**, t_opt **25**, t_max **35**; rh_min **40** (sporulation floor) or 60 (for meaningful infection), rh_sat **85**; rain_driven **False**. [R7, R8]
- Current config: t_min 15, t_opt 25, t_max 33, rh_min 60, rh_sat 85, rain_driven False.
- Note: **t_min 15 is too high** — E. necator is active from ~6 °C; lower it. t_max 33→35. The "shade/poor aeration raises RH → more PM" link is exactly the airflow-vs-disease trade-off the project is built around — worth surfacing.

### Mango

**Anthracnose — *Colletotrichum gloeosporioides*** (type `wetness`, rain-driven)
- Literature: optimum **25–30 °C** with free moisture; conidia germinate/form appressoria at **95–100% RH** (free water at 100%); **prolonged >90% RH + frequent rain**, especially at flowering/fruit-set; infection severity rises with **wet-period duration**. [R9, R10, R11]
- Sourced: t_min **15**, t_opt **27** (penetration peg max at 25, melanisation max at 30), t_max **35** [inferred]; lwd_min **6**, lwd_sat **14**; rain_driven **True**. [R9, R10, R11]
- Current config: t_min 15, t_opt 27, t_max 32, lwd 6→14, rain_driven True.
- Note: Good. Optionally raise t_max 32→35.

**Powdery mildew — *Oidium mangiferae*** (type `humidity`, rain_driven False)
- Literature: active **10–31 °C, RH 60–90%**; optimum infection **~23 °C + high RH then an abrupt RH drop**; most congenial 17–31 °C max with **moderate RH 64–72%**; free water not needed; **panicle/full-bloom stage most susceptible**. [R12, R13]
- Sourced: t_min **10**, t_opt **23**, t_max **31**; rh_min **60**, rh_sat **80**; rain_driven **False**. [R12, R13]
- Current config: t_min 10, t_opt 22, t_max 30, rh_min 60, rh_sat 80, rain_driven False.
- Note: Excellent match; no change needed (t_opt 22→23, t_max 30→31 are cosmetic).

### Guava

**Anthracnose — *Colletotrichum gloeosporioides*** (type `wetness`, rain-driven)
- Literature: favoured by **RH >90% and 22–32 °C**; **optimum for severe infection 30 °C** (less at 20 and 35 °C); penetration-peg formation max at 25 °C; conidia germinate from ~95% RH up. [R14, R15]
- Sourced: t_min **15**, t_opt **30** (severe-infection optimum), t_max **35** [inferred]; lwd_min **6**, lwd_sat **14**; rain_driven **True**. [R14, R15]
- Current config: t_min 15, t_opt 27, t_max 33, lwd 6→14, rain_driven True.
- Note: Consider raising **t_opt 27→30** (the severe-infection peak) and t_max 33→35.

### Banana

**Sigatoka** (config calls it generically "Sigatoka"; cite **black Sigatoka — *Mycosphaerella fijiensis***, the more aggressive of the pair) (type `wetness`, rain-driven)
- Literature: conidial germination optimum **27 °C**; thrives **25–28 °C**; **RH >80%** + leaf wetness from rain/overhead irrigation; LWD and temperature jointly govern development (APS 1992). [R16, R17]
- Sourced: t_min **16**, t_opt **27**, t_max **35** [inferred]; lwd_min **8**, lwd_sat **16**; rain_driven **True**. [R16, R17]
- Current config: t_min 16, t_opt 27, t_max 35, lwd 8→16, rain_driven True.
- Note: Good match. **Decide which Sigatoka you mean** — at Pattukkottai the prevalent one is historically yellow Sigatoka (*M. musicola*); black Sigatoka is more temperature/humidity-demanding and faster. Parameters above are for black Sigatoka. Record the choice in an ADR.

### Black pepper

**Foot rot — *Phytophthora capsici*** (type `wetness`, rain-driven; partly soil)
- Literature: optimum **soil temp 22–28 °C + ~40% soil water**; broader favourable **24–33 °C**; outbreak with **rain 15.8–23 mm/day, 22.7–29.6 °C, RH 81–90%**; grows best ~27 °C; root infection while soil moist and **T < 30 °C**; SW-monsoon (Jun–Sep) disease. [R18, R19]
- Sourced: t_min **18**, t_opt **26**, t_max **32** [inferred; activity falls off >30–33]; lwd_min **8**, lwd_sat **16**; rain_driven **True**. [R18, R19]
- Current config: t_min 18, t_opt 26, t_max 32, lwd 8→16, rain_driven True.
- Note: Good match. It is dual soil+aerial; current `wetness` type is acceptable but the **soil-moisture driver is user-controlled (bores)** — same caveat as pomegranate wilt.

### Dragon fruit

**Sunburn / heat stress** (type `heat`, abiotic)
- Literature: tolerable **up to ~38 °C (100 °F)**; sunburn injury when summer temps **exceed ~35 °C**; CAM physiology closes stomata by day → poor evaporative cooling → high heat susceptibility; **30–35% shade** recommended; worse in low-humidity/high-radiation sites. [R20, R21]
- Sourced: t_threshold **38** (onset of damage ~35, severe ≥38). [R20, R21]
- Current config: t_threshold 38.
- Note: Defensible. Could model onset at 35 with severe at 38 if a graded response is wanted. This is the cleanest mechanistic justification for a shade lever in the whole crop set.

**Stem rot / canker** (type `wetness`, rain-driven)
- Literature: in India the dominant agent is ***Neoscytalidium dimidiatum*** (stem canker); also *Bipolaris cactivora*, *Fusarium* spp., *Colletotrichum*; disease develops at **25–28 °C, ~80–97% RH / moist box**; favoured by **overhead irrigation & high humidity** (avoid wetting). [R22, R23]
- Sourced: t_min **20**, t_opt **28**, t_max **36** [inferred]; lwd_min **10**, lwd_sat **18**; rain_driven **True**. [R22, R23]
- Current config: t_min 20, t_opt 28, t_max 36, lwd 10→18, rain_driven True.
- Note: Reasonable. Name the target pathogen (*N. dimidiatum* for an Indian site) in an ADR; cardinal temps are inferred from pathogenicity-assay conditions, not a dose-response study — genuinely LOW confidence.

**Summary of suggested edits (do NOT apply yet):** Pomegranate blight t_max 34→~42; pomegranate wilt t_opt 28→25 (and reconsider as soil-moisture, not RH); grape PM t_min 15→~6, t_max 33→35; guava anthracnose t_opt 27→30; minor t_max bumps for mango/guava anthracnose. Mango PM, banana Sigatoka, pepper foot rot, dragon-fruit entries already match literature well.

---

## Table 2 — Variety × disease susceptibility (R / MR / MS / S)

Scale: R (resistant) 0.2 · MR 0.5 · MS 0.8 · S 1.0 (the existing `RESISTANCE_SCALE`).
**Overarching caveat:** published ratings are largely **ordinal and qualitative**,
trial- and region-specific, and frequently disagree. For several pairs **no
screening exists** — those are marked *(no data)* and should fall back to the
`DEFAULT_SUSCEPTIBILITY` with a LOW-confidence flag, not a guessed letter.

| Crop | Variety | Disease | Sourced rating | Current config | Note / source |
|---|---|---|---|---|---|
| Pomegranate | Bhagwa | Bacterial blight | **MS–S** (one study: MS; another: "highly susceptible") | S | Conflicting; none resistant. [R24, R25] |
| Pomegranate | Ganesh | Bacterial blight | **S** (categorised susceptible) | MS | **Config likely backwards** — Ganesh rated *more* susceptible than Bhagwa in [R24]. [R24] |
| Pomegranate | Arakta | Bacterial blight | **S** [inferred — none of the four commercial cvs are resistant] | S | No cultivar-specific rating found; "none resistant/tolerant." [R25] |
| Pomegranate | Mridula | Bacterial blight | **MS** | S | Grouped with Bhagwa as moderately susceptible in [R24]. [R24] |
| Pomegranate | Bhagwa | Wilt (*Ceratocystis*) | **S** | MS | Monocropping of "susceptible variety Bhagwa" aggravated wilt. [R26] |
| Pomegranate | Ganesh | Wilt | **S** | MS | First cv reported wilt-infected (1988). [R26] |
| Pomegranate | Arakta | Wilt | *(no data)* → default | S | No wilt screening found; none reported tolerant. [R26] |
| Pomegranate | Mridula | Wilt | *(no data)* → default | MS | No wilt screening found. — |
| Grapes | Thompson Seedless | Downy mildew | **MS** | S | "Moderately susceptible to downy mildew." [R27] |
| Grapes | Thompson Seedless | Powdery mildew | **MS** (can be seriously affected) | S | "Moderately susceptible"; genomically NLR-poor → fungal-sensitive. [R27, R28] |
| Mango | Alphonso | Anthracnose | **MS** (delayed onset, then moderate) | S | "Moderately susceptible." [R29] |
| Mango | Banganapalli | Anthracnose | **MS–S** (moderate-high in humid conditions) | MS | Not especially resistant. [R29] |
| Mango | Alphonso | Powdery mildew | **MS** (moderately tolerant) | MS | Match. No mango cv is truly resistant. [R30] |
| Mango | Banganapalli | Powdery mildew | *(no data)* → default | MS | No cv-specific PM rating found. [R30] |
| Guava | Allahabad Safeda | Anthracnose | **S** (rated *highly* susceptible) | MS | **Config too lenient** — raise to S. [R31] |
| Guava | Lalit | Anthracnose | *(no data)* → default | MR | **Config "MR" unsupported** — no screening of Lalit vs anthracnose found; do not claim resistance. (L-49/"Lucknow-49" — a *different* cv — is highly susceptible.) [R31] |

**Net for the matrix:** the strongest correction is **pomegranate blight Ganesh
vs Bhagwa appears inverted** relative to [R24] — important because the pipeline's
headline demo uses exactly that comparison ("Ganesh beats Bhagwa in the wet
window"). At minimum, downgrade confidence on that claim; ideally re-rate from
[R24]. Also raise Allahabad Safeda anthracnose MS→S and drop the unsupported
Lalit "MR". Treat all *(no data)* cells as default + LOW flag rather than letters.

---

## References

R1. Present status of pomegranate bacterial blight (*X. axonopodis* pv. *punicae*) and its management — ISHS / Acta Hort. 890_72. https://ishs.org/ishs-article/890_72/
R2. Recent Developments in Bacterial Blight of Pomegranate and Its Management — Springer. https://link.springer.com/chapter/10.1007/978-81-322-2571-3_11
R3. Epidemiology and management of bacterial blight of pomegranate — Acta Hort. 818_43. https://www.actahort.org/books/818/818_43.htm
R4. Role of abiotic factors on the epidemiology of wilt of pomegranate caused by *Ceratocystis fimbriata*. https://www.longdom.org/proceedings/role-of-abiotic-factors-on-the-epidemiology-of-wilt-of-pomegranate-caused-by-ceratocystis-fimbriata-44846.html
R5. Effect of temperature and wetness duration on infection by *Plasmopara viticola* — Eur. J. Plant Pathol. https://link.springer.com/article/10.1007/s10658-015-0802-9
R6. Grapevine disease models (downy mildew, primary infection rules) — METOS/Pessl. https://metos.global/en/disease-models-grapevine/
R7. Diseases of the Grapevine: Powdery Mildew — Texas A&M Aggie Horticulture. https://aggie-horticulture.tamu.edu/vitwine/viticulture/viticulture-resources/diseases-of-the-grapevine-powdery-mildew/
R8. Effects of Humidity on the Development of Grapevine Powdery Mildew — *Phytopathology* 93(9):1137. https://apsjournals.apsnet.org/doi/abs/10.1094/PHYTO.2003.93.9.1137
R9. Effect of humidity and temperature on conidial germination and appressorium development of *C. gloeosporioides* (mango), Estrada et al. 2000 — *Plant Pathology*. https://bsppjournals.onlinelibrary.wiley.com/doi/full/10.1046/j.1365-3059.2000.00492.x
R10. A model for estimating infection levels of anthracnose of mango, Fitzell 1984 — *Ann. Appl. Biol.* https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1744-7348.1984.tb03027.x
R11. *Colletotrichum gloeosporioides*: Pathogen of Anthracnose in Mango — Springer. https://link.springer.com/chapter/10.1007/978-3-319-27312-9_9
R12. Powdery mildew of mango: ecology, biology, epidemiology and management (review). https://www.academia.edu/29950313/Powdery_mildew_of_mango_A_review_of_ecology_biology_epidemiology_and_management
R13. Mango powdery mildew (*Oidium mangiferae*) — NHB factsheet. https://nhb.gov.in/pdf/fruits/mango/man002.pdf
R14. Effect of environmental conditions and inoculum density on infection of guava fruits by *C. gloeosporioides* — *Mycopathologia*. https://link.springer.com/article/10.1023/A:1006842801828
R15. Infection of guava by *C. gloeosporioides* and *C. acutatum* under different temperatures and wetting periods. https://www.researchgate.net/publication/262593779
R16. Black Sigatoka (*Mycosphaerella fijiensis*) — Wikipedia (summary of cardinal conditions, with primary refs). https://en.wikipedia.org/wiki/Black_sigatoka
R17. Effects of Leaf Wetness Duration and Temperature on Development of Black Sigatoka — *Phytopathology* 82:515 (1992). https://www.apsnet.org/publications/phytopathology/backissues/Documents/1992Abstracts/Phyto82_515.htm
R18. Infection of *Phytophthora capsici* on pepper — models and affecting factors — *Front. Agric. China*. https://link.springer.com/article/10.1007/s11703-008-0010-x
R19. Spread of *Phytophthora capsici* in black pepper — SciRP. https://www.scirp.org/html/4-8102441_59136.htm
R20. Mitigating heat stress in dragon fruit in semi-arid climates: role of shade nets — *Environ. Dev. Sustain.* https://link.springer.com/article/10.1007/s10668-024-05619-w
R21. Pitaya (Dragonfruit) Growing in the Florida Home Landscape — UF/IFAS HS303 (temp tolerance, ~30% shade). https://ask.ifas.ufl.edu/publication/HS303
R22. First Report of *Neoscytalidium dimidiatum* Causing Dragon Fruit Stem Canker in India — *Plant Disease*. https://apsjournals.apsnet.org/doi/10.1094/PDIS-04-22-0909-PDN
R23. Stem and Fruit Canker of Dragon Fruit in South Florida — UF/IFAS PP355. https://ask.ifas.ufl.edu/publication/PP355
R24. Differential gene responses in different varieties of pomegranate during pathogenesis of *X. axonopodis* pv. *punicae* (categorises Mridula/Bhagwa as moderately susceptible, Ganesh as susceptible) — PMC7981347. https://pmc.ncbi.nlm.nih.gov/articles/PMC7981347/
R25. Biocontrol of bacterial blight in pomegranate (notes Bhagwa highly susceptible; none of the commercial cvs resistant/tolerant) — *Front. Microbiol.* https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2024.1491124/full
R26. Incidence of Pomegranate Wilt in Southern Karnataka (Bhagwa susceptible; Ganesh first reported infected) — ResearchGate 368574453. https://www.researchgate.net/publication/368574453
R27. Thompson Seedless — disease susceptibility profile (moderately susceptible to downy & powdery mildew). https://grapevarieties.info/grape-variety/thompson-seedless/
R28. Telomere-to-telomere gap-free genome of a susceptible grapevine (Thompson Seedless); reduced NLR repertoire → fungal sensitivity — PMC10822838. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10822838/
R29. Resistance to anthracnose in commercial cultivars and advanced hybrids of mango (Alphonso moderately susceptible) — *Plant Pathol. J.* https://scialert.net/fulltext/?doi=ppj.2015.255.258
R30. Evaluation of mango varieties against powdery mildew (*Oidium mangiferae*); no resistant cv; Alphonso moderately tolerant — SciRP. https://www.scirp.org/journal/paperinformation?paperid=47701
R31. Screening of commercial guava varieties against anthracnose (Allahabad Safeda & L-49 highly susceptible) — *Indian Phytopathology*. https://link.springer.com/article/10.1007/s42360-025-00821-w

---

*Sourcing pass completed 2026-06-06. No code edited, nothing pushed. Next:
decide which edits to accept, then apply to `config.py` in a dedicated commit
with an ADR recording the chosen pathogen identities (Sigatoka species, dragon-
fruit stem-rot agent) and the soil-moisture-vs-RH treatment of wilt/foot-rot.*
