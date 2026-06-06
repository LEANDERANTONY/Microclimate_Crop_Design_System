# Economics Inputs — Sourced Data for Layer 4–5

**Purpose:** Raw inputs for `economics.py` (layers 4–5 from `docs/economics_layer.md`).  
**Site:** Pattukkottai, Thanjavur district, Tamil Nadu.  
**Compiled:** June 2026. Do NOT edit code; this is a data-only pre-build artifact.

---

## How to read this document

Each crop section has three sub-sections:

| Field | What it means |
|---|---|
| **Reference yield / acre** | Starting point for `attainable_yield = ref_yield × growth_factor × (1−disease_loss)`. Represents well-managed, irrigated production at TNAU/ICAR/NHB standards for Tamil Nadu or broadly South India. NOT best-case research-station yields. |
| **Price band** | Trailing mandi (wholesale) price range, approximately 25th–75th percentile over 2022–2025 unless noted. Point estimates are NOT provided by design. Sources: Agmarknet, commodityonline.com, kisandeals.com, CEDA Ashoka. Where Agmarknet did not yield direct 3-year statistics, equivalent sources (Tridge, IndiaMART, state mandi portals) are cited. |
| **Market / surplus signal** | Whether this crop is locally oversupplied (price depressed, must ship far) or undersupplied/niche (premium but thin market). Uses NHB production stats, APEDA export data, state agriculture dept figures. |

**Confidence labelling** follows the pipeline convention:  
- **HIGH** — directly from TNAU/ICAR/NHB official documents or Agmarknet API.  
- **MODERATE** — from reputable secondary agri-portals (agrifarming.in, NHB model project reports, state dept bulletins) that cite primary sources.  
- **LOW** — estimated from partial data, conversion factors, or extrapolation; flag for update.

---

## FOCUS / ENGINEERABLE GROUP
*(Crops where microclimate design tips marginal viability — highest modelling value)*

---

### 1. Pomegranate

**Reference yield / acre**  
- Standard well-managed orchard: **4–7 t/acre** from year 5 onwards. NHB model project gives 4 t/acre (yr 5) to 7 t/acre (yr 8+).  
- Bhagwa (premium export variety): **8–10 t/acre** under drip irrigation + precision management (high-tech practices).  
- **Use in model:** 5 t/acre as central reference for a well-managed TN site; 4–7 t/acre as the band.  
- Source: NHB Pomegranate model project report (nhb.gov.in); ICAR-NRCP "Pomegranate: a crop for doubling farmers' income" (2018).  
- **Confidence: MODERATE** (NHB figure applies broadly to India; TN climate may slightly reduce yield vs Maharashtra standard; no TN-specific trial data found).

**Price band (2022–2025, Tamil Nadu / wholesale)**  
- Modal mandi wholesale: **₹40–120/kg** (25th–75th percentile).  
- Range extends to ₹15/kg in Maharashtra glut seasons (Dec–Jan new crop arrival) and ₹220+/kg for premium fruit in lean months (Apr–Jun 2025–26).  
- Current (May–Jun 2026): ₹220–230/kg in TN mandis — unusually high; treat as upper-band outlier.  
- Maharashtra dominates price discovery (Nasik/Solapur APMC); TN prices track MH ±10–20%.  
- Source: kisandeals.com TN live prices; commodityonline.com TN pomegranate; Tridge India overview.  
- **Confidence: MODERATE** (3-year percentile band approximated; exact Agmarknet 2022–24 pull needed for calibration).

**Market / surplus signal**  
- India is world's largest pomegranate producer (~2.6 MT/yr); Maharashtra has 62% of area.  
- TN production is small-scale (minor producing state); locally **undersupplied** — TN consumes imported MH fruit.  
- A TN-grown pomegranate avoids 2,000–3,000 km logistics → **net price advantage of ₹15–25/kg** vs MH landed cost.  
- Export: India exports to UAE, Europe, Bangladesh; APEDA-registered packhouses needed; viable for grade-A TN fruit.  
- **Signal: FAVOURABLE** — local production fills a real gap; not competing with local surplus.  
- **Market-distance penalty: LOW** (domestic premium possible; export requires cold chain investment — flag as v2 feature).

---

### 2. Dragon Fruit (Kamalam)

**Reference yield / acre**  
- Year 1–2 (establishment): 2–4 t/acre.  
- Mature (year 3+): **8–10 t/acre** average; well-managed 10–13.5 t/acre possible.  
- ICAR-NIASM figure: 8–13.5 MT/ha (established orchards, 3+ years) = **3.2–5.5 t/acre**.  
- Multiple farming portals consistently cite 8–10 t/acre for mature Indian orchards.  
- **Use in model:** 8 t/acre (mature central reference); 4–10 t/acre band.  
- Source: ICAR-NIASM bulletin; vikaspedia.in (ICAR package); agriworldview.com; PIB press release on Kamalam.  
- **Confidence: MODERATE** (ICAR-NIASM range matches portal consensus; yield drops sharply with heat stress above 38°C without shade — directly relevant for Pattukkottai summers, flagged in Layer 1).

**Price band (2022–2025, wholesale India)**  
- **₹80–200/kg** (25th–75th percentile, 2022–2024).  
- 2022–23 prices were high (₹150–250/kg) as supply was tight and novelty premium held.  
- 2024–25: prices declining as Gujarat/Karnataka acreage surged (from 3,000 ha to 14,500 ha in 2 years). Modal approaching ₹80–120/kg.  
- Export prices (FOB): $1.46–4.68/USD per kg (Tridge, 2023–24).  
- Source: Tridge Fresh Dragon Fruit India; agrospectrumindia.com; PIB MIDH scheme data; Wikipedia dragon fruit farming India.  
- **Confidence: MODERATE–LOW** (price trajectory clearly falling; exact TN mandi 3-year band needs Agmarknet pull; current trend is most important signal).

**Market / surplus signal**  
- Rapid supply-side expansion (3,000 ha → 14,500 ha 2022–2024; target 50,000 ha by 2028 under MIDH).  
- Domestic imports from Vietnam/Thailand/Sri Lanka grew 35% in 2024 — India not yet self-sufficient but supply growing fast.  
- Urban demand is real and growing; India's FMCG/health food sector is absorbing volume.  
- **Signal: AMBER — growing supply risk.** Premium likely to compress; price band will drift lower.  
- TN is not a primary producing state; local growers serve regional markets.  
- **Market-risk flag: HIGH** — novelty premium thinning; only viable long-term if cost structure is low (which dryland agroforestry with shade supports). Mark as market-risk crop in optimizer output.

---

### 3. Grapes (Table)

**Reference yield / acre**  
- Tamil Nadu (Theni, Dindigul): productivity **16.9–19.1 MT/ha = 6.8–7.7 t/acre** (Coimbatore highest, Dindigul second).  
- NHB model project: 15–20 t/ha = 6–8 t/acre for established vineyard.  
- Two crops possible in TN with double-pruning; yield per crop ~3–4 t/acre.  
- **Use in model:** 7 t/acre central reference; 5–8 t/acre band.  
- Source: EPRA journal "Economic Analysis of Grape Production" (Theni, Tamil Nadu); NHB model project report (nhb.gov.in/grape); ResearchGate trend/growth study TN grapes.  
- **Confidence: MODERATE–HIGH** (TN-specific data available; Theni/Dindigul districts closest analogue to Pattukkottai climate).

**Price band (2022–2025, wholesale)**  
- Standard table grape (Thompson Seedless, Muscat): **₹30–90/kg** at farm gate/wholesale.  
- Premium varieties during peak season (Feb–Apr): ₹60–120/kg.  
- Off-season / glut years: ₹20–40/kg.  
- Export grade (APEDA registered): ₹80–150/kg FOB.  
- India exported 344,000 MT in 2023–24, valued at ₹3,460 crores (~₹100/kg average export price).  
- Source: Bijak blog (EU market demand, 2024); SEAIR grapes export; IndiaMART; APEDA grapes page.  
- **Confidence: MODERATE** (national export data solid; TN mandi band extrapolated — TN mandis are at the lower end of Maharashtra/Karnataka prices).

**Market / surplus signal**  
- India produces 2.95 MT/yr (2023–24); Maharashtra (67%) + Karnataka (28%) dominate.  
- Tamil Nadu is ~3–5% of national production; Theni/Dindigul have established markets.  
- Export demand from Europe/Middle East is growing; India fills a supply gap Dec–Apr.  
- **Signal: NEUTRAL–FAVOURABLE** — large national market with real export avenue; TN grapes serve local + regional markets.  
- **Key risk:** high water requirement (drip irrigation essential); disease pressure (downy mildew) in the NE monsoon window requires tight bahar management — exactly what Layer 2 (disease) models.
- **Market-distance penalty: LOW-MODERATE** (established trade channels; cold chain needed for export).

---

## SPICE CROPS

---

### 4. Black Pepper

**Reference yield / acre**  
- TNAU standard: **2–3 kg/vine/year** (dry pepper, year 3+ bearing). At 500 vines/acre (3×3 m spacing with standards), this gives **1,000–1,500 kg dry pepper/acre**.  
- However, TNAU TN field performance is lower than Kerala/Karnataka due to sub-optimal rainfall; realistic TN open-field yield: **300–600 kg dry/acre**.  
- Bush pepper (low-input, intercropped): 1.5 kg green/plant/2–3 years.  
- TNAU specifically notes growing districts: Kanyakumari, Nilgiris, Kolli Hills — all with rainfall >150 cm. Pattukkottai (~1,000 mm) is at the lower limit; irrigated intercrop under coconut is viable.  
- **Use in model:** 400 kg dry/acre (central reference for coconut-intercrop system, irrigated); 250–600 kg/acre band.  
- Source: TNAU Agritech Portal Black Pepper page (agritech.tnau.ac.in, verified via web fetch); CPCRI-cited Panniyur variety data.  
- **Confidence: MODERATE** (TNAU yield is vine-level; per-acre depends heavily on spacing, shade from standards, and irrigation — all variables Layer 1 models directly).

**Price band (2022–2025, wholesale India)**  
- 2022–2023: **₹300–500/kg** (dry black pepper, ungarbled).  
- 2024–2025: sharp rise — ₹500–700/kg modal; North Paravur APMC Kerala high grade reaching ₹750–950/kg.  
- Current 2026: ₹600–800/kg mandi; highest ₹80,000/quintal = ₹800/kg.  
- International: USD $5.49–9.63/kg (2023–24, Tridge).  
- Source: bankbazaar.com commodity price; kisandeals.com; agriwatch.com; CEDA Ashoka (implied).  
- **Confidence: MODERATE** (national price trend clear; TN mandi prices track Kerala ±10%; exact 2022–24 percentile band needs Agmarknet query).

**Market / surplus signal**  
- India produces ~32,000 t/yr (TNAU page); Kerala 94%, Karnataka 5%, Tamil Nadu <1%.  
- India is a large exporter of black pepper (~41,000 t/yr); global price driven by Vietnam supply.  
- 2024–26 global shortage (Vietnam crop shortfall) is pushing prices to decade highs.  
- **Signal: VERY FAVOURABLE** — high price, genuine demand, no local surplus.  
- TN production is negligible → any local production commands premium from regional spice traders.  
- **Market-risk flag: MODERATE** — price is cyclical; Vietnam/Indonesia crop recovery could depress prices in 2–3 years.

---

### 5. Ginger

**Reference yield / acre**  
- India average: **6–10 t/acre** fresh rhizome (irrigated, drip).  
- TNAU/ICAR recommendation: 10–12 t/acre fresh under good management (ICAR-CCARI, ICAR KVK package).  
- Conversion: dry ginger = 16–25% of fresh weight → **1.5–3 t/acre dry**.  
- TN production is very low (~2,600 t total for all of TN, CEIC data March 2025).  
- **Use in model:** 8 t/acre fresh (irrigated, well-managed); 6–12 t/acre band.  
- Source: TNAU Ginger PDF (agritech.tnau.ac.in/banking/pdf/Ginger.pdf); ICAR-CCARI DSS; KVK package (kvk.icar.gov.in); asiafarming.com (citing state-level averages).  
- **Confidence: MODERATE** (yield range cross-confirmed from multiple ICAR sources; TN-specific figure extrapolated from national).

**Price band (2022–2025, green ginger, wholesale)**  
- Highly volatile. 2022–2024 range: **₹3,000–16,000/quintal (₹30–160/kg)**.  
- March 2024 monthly average: ₹9,246/quintal; Gujarat ₹9,437, Kerala ₹11,759.  
- Current 2026: ₹11,516/quintal modal; range ₹5,000–16,000/quintal.  
- Dry ginger: ₹5,000–24,800/quintal (broader range due to quality/grade spread).  
- Source: commodityonline.com; Kerala FWP time series (ecostat.kerala.gov.in); krishijagran.com mandi update; Statista India retail ginger index.  
- **Confidence: MODERATE** (price band directionally reliable; high intra-year volatility means the band must be kept wide — exactly how the model should represent it).

**Market / surplus signal**  
- Major producing states: Kerala, Karnataka, Assam, Meghalaya, Odisha. TN is minor.  
- National production: ~2.5–3 MT/yr (fresh). TN contributes ~2,600 t → effectively nil share.  
- **Signal: FAVOURABLE FOR TN GROWERS** — no local surplus; proximity to Tamil/regional spice market.  
- Highly volatile price is the main risk; farmer price risk is high in years of national bumper crop.  
- **Market-risk flag: HIGH (price volatility)** — model should present the full ₹30–160/kg band, not a point; downside scenario needs to be visible.

---

### 6. Vanilla

**Reference yield / acre**  
- Cured vanilla beans (the commercial product): typically **80–120 kg/acre** per year for established vines (6+ years), from ~2,000 vines/acre.  
- Green bean yield is ~5× cured weight → 400–600 kg green/acre.  
- High-performing vines: up to 200 kg cured/acre.  
- Very long establishment period: first harvest year 3, full production year 6+.  
- **Use in model:** 100 kg cured/acre (central reference); 60–150 kg/acre band.  
- Source: ICAR Annual Report 2023–24 (indirect); 6W Research India Vanilla Market (2024–2030); IndexBox India Vanilla 2023 report.  
- **Confidence: LOW** (no TNAU/ICAR per-acre figure found; estimate from vine density and international benchmarks; TN-specific data absent).

**Price band (2022–2025, cured vanilla beans)**  
- Extreme global price volatility. Indian export prices 2023: **$166–$235 USD/kg**.  
- 2024: sharp drop to $43–$165 USD/kg (Madagascar bumper crop inflated global supply).  
- Approximate INR equivalent at ₹83/USD: ₹3,600–19,500/kg (2023 export); ₹3,600–13,700/kg (2024).  
- Domestic-grade cured beans: generally 30–50% of export price.  
- Source: Tridge Vanilla India; IndexBox India Vanilla 2023; 6W Research.  
- **Confidence: LOW** (INR conversion approximate; Indian domestic mandi price for vanilla is almost absent from Agmarknet — the crop is sold contract, not mandi).

**Market / surplus signal**  
- India is "one of the largest producers" by some accounts, but data quality is poor; most Indian vanilla is low-grade.  
- India's vanilla imports grew 40% in 2023 → domestic production does not meet industry demand.  
- Primary buyer: Indian FMCG / flavour industry (chocolate, ice cream, beverages).  
- **Signal: UNDERSUPPLIED** — genuine domestic deficit; high price but thin market (contract sales only; no mandi depth).  
- **Market-risk flag: VERY HIGH** — price is globally determined by Madagascar crop; yield requires very specific microclimate (deep shade, >80% RH, controlled pollination); a bad pollination season = zero income.  
- **Recommendation for model:** flag vanilla as HIGH-PRICE / VERY-HIGH-RISK; present profitability with explicit downside at $43/kg cured-bean scenario.

---

### 7. Cocoa

**Reference yield / acre**  
- India average: **300–500 kg dry cocoa beans/acre** for established plantations (7–10 years).  
- Range reflects canopy system: coconut-intercrop gives ~300–400 kg; arecanut-intercrop ~400–500 kg.  
- ICAR-CPCRI benchmark for Kerala/AP: 1,200 kg/ha = ~486 kg/acre.  
- Fresh pod→dry bean conversion: ~5–6:1 ratio.  
- **Use in model:** 350 kg dry beans/acre (central reference); 250–500 kg/acre band.  
- Source: Mongabay India cocoa article (Oct 2024); rangde.in economics of cocoa farming; ICAR CPCRI publication (cpcri.gov.in); ICCO quarterly bulletin Nov 2024.  
- **Confidence: MODERATE** (ICAR-CPCRI figure is the most authoritative; yield is heavily shade-dependent — directly driven by Layer 1 canopy prediction).

**Price band (2022–2025, dry cocoa beans, India)**  
- 2022–early 2023: **₹250–350/kg**.  
- Late 2023 – April 2024: global cocoa crisis (West Africa crop failure) drove Indian prices to **₹800–1,000/kg** (unprecedented).  
- Mid–late 2024: partial stabilisation at **₹500–600/kg**.  
- Current 2025–26: ~₹500–700/kg.  
- **Band for model (excluding crisis peak):** ₹250–600/kg; peak-crisis scenario to ₹1,000/kg.  
- Source: Mongabay India Oct 2024 ("₹250–300/kg early 2024, then to ₹1,000/kg by April"); rangde.in cocoa economics; ICCO bulletin.  
- **Confidence: MODERATE** (crisis period data solid from journalism; pre/post-crisis normalisation price is uncertain).

**Market / surplus signal**  
- India is a cocoa DEFICIT country — domestic chocolate/confectionery demand far exceeds production.  
- Production ~27,600 t (2024); demand: India imports significant cocoa. FMCG sector (Mondelez, ITC, Nestlé) is the buyer.  
- AP (40%) + Kerala (35%) dominate; Tamil Nadu is a small but growing producer.  
- **Signal: STRONGLY FAVOURABLE** — genuine domestic demand deficit; cocoa beans can be sold locally to processing intermediaries without long logistics.  
- **Market-risk flag: MODERATE** — price driven by global ICCO market, not local supply. Crisis premium may not persist. Model should use ₹350–600/kg as the normalised band and show ₹250/kg downside.

---

### 8. Nutmeg

**Reference yield / acre**  
- Mature plantation (year 8+): up to **2,000 kg nutmeg + 500 kg mace per acre** (from 400 trees × 5 kg/tree; Kerala high-performer cited in 30stades.com).  
- More conservative ICAR/CPCRI reference: national yield 637 kg/ha = **258 kg/acre** (includes both nut and mace); this is the India average including underperforming orchards.  
- At Pattukkottai: nutmeg needs moisture/humidity; under coconut canopy with irrigation it is viable but will underperform Kerala benchmarks.  
- **Use in model:** 400 kg dry nut + 100 kg mace/acre (moderate management, irrigated intercrop); 250–700 kg/acre band.  
- Source: JETIR nutmeg feasibility study Kerala 2023; vikaspedia.in nutmeg package; CPCRI annual data (CEIC Kerala production); amrafarms.com variety data.  
- **Confidence: LOW–MODERATE** (wide performance range; TN-specific figure not found; Kerala benchmark applies under better rainfall).

**Price band (2022–2025, wholesale dry nutmeg)**  
- **₹600–900/kg** (nutmeg, dry, whole) approximate 2022–2025 range.  
- Mace typically 1.5–2× nutmeg price: ₹900–1,500/kg.  
- India's nutmeg exports valued at ~₹200 crores/yr (APEDA implied).  
- No direct Agmarknet 3-year series found for nutmeg; estimate from IndiaMART / Kerala Spices Board.  
- Source: indiamart.com nutmeg bulk prices; Kerala Spices Board (implied via TNAU source attribution); agrifarming.in project report.  
- **Confidence: LOW** (no Agmarknet pull confirmed; price band from trader quotes, not mandi statistics — flag for update).

**Market / surplus signal**  
- India is 3rd largest producer (after Guatemala and Indonesia).  
- Ninety-six percent of Indian production from Kerala; TN contribution negligible.  
- Domestic demand steady (spice industry, pharmaceutical, essential oils); some export.  
- **Signal: NEUTRAL–FAVOURABLE** — no local TN surplus; product finds ready buyers in spice trade.  
- **Market-risk flag: MODERATE** — long crop establishment (8+ years to full yield); Indonesia/Guatemala supply affects global price.

---

## FRUIT CROPS

---

### 9. Mango

**Reference yield / acre**  
- India average horticulture: **5–8 MT/ha = 2–3.2 t/acre** (includes rain-fed and unmanaged orchards).  
- TNAU/state horticulture: well-managed irrigated mango: **4–6 t/acre** for commercial varieties (Banganapalli, Alphonso, Neelam, Dashehari).  
- Mature orchard (10+ years): up to 8–10 t/acre for high-density systems.  
- **Use in model:** 4.5 t/acre (central reference); 3–7 t/acre band.  
- Source: TNAU Organic Cultivation of Mango PDF (agritech.tnau.ac.in/banking/pdf/Mango.pdf); global-agriculture.com India advance estimates 2023–24 (228 lakh tonnes total).  
- **Confidence: MODERATE** (national figures well-documented; TN-specific per-acre figure extrapolated).

**Price band (2022–2025, wholesale Tamil Nadu)**  
- Highly seasonal. Peak season (Apr–Jun): **₹20–60/kg** for standard varieties at mandi.  
- Premium Alphonso/Kesar: ₹80–200/kg.  
- Off-season (retail premium): higher but irrelevant for farm-gate economics.  
- Current 2026 mandi data shows ₹55–196/kg across TN mandis.  
- **Band for model:** ₹25–80/kg (standard commercial variety, farm gate).  
- Source: commodityonline.com mango TN; kisandeals.com mango TN; IndiaMART Salem/Chennai.  
- **Confidence: MODERATE** (seasonal variation wide; year-to-year band needs Agmarknet pull).

**Market / surplus signal**  
- India is world's #1 mango producer (~22.8 million t in 2024–25 = ~23% of global supply).  
- Tamil Nadu is a significant mango state; large production, some local surplus in season.  
- **Signal: NEUTRAL — moderate surplus risk in season.** Post-harvest losses are high (35–40%); processing/pulp market provides a floor.  
- Good crop for local consumption and regional trade; not primarily an export crop from TN.  
- **Market-distance penalty: LOW** (regional market depth adequate; season price volatility is the main risk).

---

### 10. Banana

**Reference yield / acre**  
- TNAU cost-of-cultivation table: **75 MT/ha = 30.4 t/acre** (tissue-culture, well-managed).  
- More typical commercial: **15–25 t/acre** (Robusta/Cavendish; Grand Naine TC under drip).  
- Local varieties (Poovan/Nendran): 8–12 t/acre.  
- Tamil Nadu is India's second-largest banana producer (Thanjavur/Trichy/Coimbatore belt).  
- **Use in model:** 20 t/acre (Grand Naine TC, irrigated reference); 12–25 t/acre band.  
- Source: TNAU Cost of Cultivation page (agritech.tnau.ac.in, verified via web fetch — 75 MT/ha, ₹5–12/kg); agropotli.com 2026 guide.  
- **Confidence: HIGH** (TNAU figure directly from official table; Thanjavur is a primary banana belt so TN-specific data is most applicable of all crops here).

**Price band (2022–2025, wholesale Tamil Nadu)**  
- TNAU table shows ₹5–12/kg range (older data).  
- Current (2026): retail ₹49/kg; mandi farm gate ~₹15–30/kg for Grand Naine.  
- 2022–2024 band at mandi: approximately **₹8–25/kg** (modal ₹12–18/kg).  
- Local variety (Poovan): ₹10–20/kg.  
- Source: TNAU table (agritech.tnau.ac.in/horticulture/horti_cost%20of%20cultivation.html); commodityonline.com banana TN; NHB banana page.  
- **Confidence: HIGH** (TNAU provides direct band; current data confirms the upper end has risen).

**Market / surplus signal**  
- India is world's largest banana producer (~38 million t 2024–25).  
- Tamil Nadu banana is a major staple crop; Thanjavur district is a production centre.  
- **Signal: HIGH LOCAL SURPLUS** — Thanjavur/Trichy belt produces at scale; local prices are suppressed. Must-ship to Chennai metro, Karnataka, or Kerala for any premium.  
- **Market-distance penalty: MODERATE** — logistics from Pattukkottai to Chennai/metro ~350 km; adds ₹2–5/kg transport cost that compresses margin.  
- Reliable income; low-risk; low-margin. Good as a risk anchor crop, not a high-margin crop.

---

### 11. Guava

**Reference yield / acre**  
- TNAU variety data: high-performing variety at 40.52 kg/tree under salt-stressed conditions (an upper bound).  
- Standard commercial planting (250–300 trees/acre): **8–15 t/acre** for Allahabad Safeda or improved varieties.  
- NHB: 20–25 MT/ha = **8–10 t/acre** for L-49 / Taiwan Pink under good management.  
- **Use in model:** 10 t/acre (central); 7–15 t/acre band.  
- Source: TNAU Guava varieties page (agritech.tnau.ac.in); agrifarming.in; farmnest India community cited 40.52 kg/tree.  
- **Confidence: MODERATE**.

**Price band (2022–2025, wholesale Tamil Nadu)**  
- **₹15–40/kg** at mandi (25th–75th percentile).  
- Low prices (₹8–12/kg) in bumper seasons; can reach ₹50–60/kg in lean periods.  
- Source: commodityonline.com guava TN; kisandeals.com; TNAU cost table (indirect).  
- **Confidence: MODERATE–LOW** (Agmarknet TN guava pull not completed; estimate from portal data).

**Market / surplus signal**  
- India is world's #2 guava producer; surplus at national scale.  
- TN has decent local demand; Thanjavur/delta is a consuming region.  
- **Signal: MODERATE SURPLUS** — prices are low because supply is ample nationally.  
- Processing (guava pulp, jam) provides some floor; fresh market is price-volatile.  
- **Recommendation:** viable as an inter-filler/diversity crop; not a primary revenue driver.

---

### 12. Papaya

**Reference yield / acre**  
- India average: 35–40 MT/ha = **14–16 t/acre**.  
- TN standard: similar range; Coorg Honey Dew and Red Lady commonly grown.  
- **Use in model:** 14 t/acre (central); 10–18 t/acre band.  
- Source: agrifarming.in project report; NHB Tamil Nadu horticulture stats (implied).  
- **Confidence: MODERATE**.

**Price band (2022–2025, wholesale Tamil Nadu)**  
- **₹8–20/kg** at mandi.  
- Perishable: bumper-season prices crash to ₹4–5/kg; lean-season peaks ₹25–30/kg.  
- Source: kisandeals.com papaya TN; commodityonline.com papaya TN.  
- **Confidence: MODERATE–LOW**.

**Market / surplus signal**  
- Highly perishable; short shelf life (4–5 days at ambient temperature).  
- Significant national surplus; prices volatile.  
- **Signal: HIGH LOCAL SURPLUS + HIGH PERISHABILITY RISK** — must reach market within 3 days; Pattukkottai to nearest processing unit adds logistics complexity.  
- Processing (papain enzyme extraction, pulp) adds value but requires offtake agreement.  
- **Market-distance penalty: HIGH** — perishability dominates; include perishability penalty flag in Layer 5.

---

### 13. Sapota (Chikoo)

**Reference yield / acre**  
- Year 5: 4 t/acre; Year 7+: **6 t/acre** (NHB high-density model).  
- India average: 20–25 MT/ha = 8–10 t/acre for mature orchards.  
- **Use in model:** 5 t/acre (year 5–7 average); 4–8 t/acre band.  
- Source: agrifarming.in sapota project report; apnikheti.com; NHB (implied via sapota cultivation area: 65,000 acres, 5.4 lakh MT nationally = ~8.3 t/acre average).  
- **Confidence: MODERATE**.

**Price band (2022–2025, wholesale)**  
- **₹20–60/kg** (25th–75th percentile).  
- Source: IndiaMART; agrifarming.in project report.  
- **Confidence: LOW** (no direct Agmarknet pull; estimate from portal data).

**Market / surplus signal**  
- Moderate national production; steady local demand in TN.  
- Long shelf life (7–10 days) is a key advantage vs papaya.  
- **Signal: NEUTRAL** — reasonable local market; no major surplus or shortage.

---

### 14. Custard Apple (Sitaphal)

**Reference yield / acre**  
- High-density (with grafted plants): **6–8 t/acre**.  
- Standard: 4–6 t/acre.  
- **Use in model:** 5 t/acre; 3–7 t/acre band.  
- Source: farmatma.in; agrifarming.in project reports.  
- **Confidence: MODERATE–LOW** (TN-specific data not found; estimate).

**Price band (2022–2025, wholesale)**  
- **₹40–100/kg** — premium fruit with short season (Sep–Nov).  
- Source: IndiaMART; agrifarming.in.  
- **Confidence: LOW**.

**Market / surplus signal**  
- Short season creates gluts during peak (Sep–Nov) and shortage rest of year.  
- Processing difficult; fresh only; shelf life ~3 days.  
- **Signal: NICHE + PERISHABILITY RISK** — high price potential but must sell fast.  
- **Recommendation:** model with perishability penalty.

---

### 15. Fig

**Reference yield / acre**  
- India average: 8–12 MT/ha = **3.2–4.9 t/acre** fresh figs.  
- Poona and Brown Turkey varieties in India.  
- **Use in model:** 4 t/acre; 3–6 t/acre band.  
- Source: agrifarming.in project report; NHB fig page (implied).  
- **Confidence: LOW** (minimal TN-specific data; national average used).

**Price band (2022–2025)**  
- Fresh figs: **₹60–150/kg** (highly perishable; thin fresh market).  
- Dried fig (imports): ₹400–800/kg.  
- Source: IndiaMART; agrifarming.in.  
- **Confidence: LOW** (very thin market; no Agmarknet data found).

**Market / surplus signal**  
- India has a thin fresh-fig market; most commercial fig consumption is dried imports from Turkey/Afghanistan.  
- **Signal: NICHE, THIN MARKET** — small volume; very high perishability (1–2 days shelf life); best suited for farm-direct/farm-stay revenue.  
- **Recommendation:** do not include as primary revenue crop in optimizer; flag as low-market-depth.

---

### 16. Dragon Fruit (see Focus Group, entry #2)

---

### 17. Acid Lime

**Reference yield / acre**  
- India average: 15–20 MT/ha = **6–8 t/acre**.  
- Tamil Nadu is a significant acid-lime producer (Salem, Krishnagiri, Erode).  
- **Use in model:** 7 t/acre; 5–9 t/acre band.  
- Source: NHB lime/lemon model project; TNAU extension (implied from TN horticulture profile).  
- **Confidence: MODERATE**.

**Price band (2022–2025, wholesale Tamil Nadu)**  
- Highly seasonal and volatile: **₹10–60/kg** (25th–75th mandi range).  
- Peak summer demand (Apr–Jun): ₹40–80/kg.  
- Post-monsoon glut: ₹8–15/kg.  
- Source: commodityonline.com (lime TN); market.todaypricerates.com TN fruits.  
- **Confidence: MODERATE–LOW** (seasonal range well-known; 3-year percentile band approximated).

**Market / surplus signal**  
- Steady FMCG demand (beverages, pickles, cleaning products).  
- TN produces substantial lime; national surplus periodic in good monsoon years.  
- **Signal: NEUTRAL** — reliable market but cyclical price; NE monsoon timing means disease-window overlap.

---

### 18. Amla (Indian Gooseberry)

**Reference yield / acre**  
- Early commercial (year 5–6): **4 t/acre**; mature (year 10+): 20 t/acre possible but ~8–15 t/acre is realistic commercial average.  
- **Use in model:** 6 t/acre (mid-rotation reference); 4–12 t/acre band.  
- Source: agrifarming.in amla project report; signuptrendingnature.com; zettafarms.com.  
- **Confidence: MODERATE**.

**Price band (2022–2025)**  
- **₹12–45/kg** (mandi range; 2022–2024).  
- October 2023 peak: ₹126–166/kg (off-season).  
- 2024: ₹100–150/kg retail; mandi ~₹20–40/kg.  
- Source: IndiaMART; Tridge amla India 2024 overview; agrifarming.in.  
- **Confidence: MODERATE–LOW**.

**Market / surplus signal**  
- UP dominates production; TN is a secondary state.  
- Growing health-food / Ayurveda demand creating steady market pull.  
- **Signal: NEUTRAL–FAVOURABLE** — demand trend up; TN growers access Chennai health-food market.

---

### 19. Moringa (Drumstick)

**Reference yield / acre**  
- Pods: up to **20 t/acre** (mature annual moringa, intensive planting).  
- Commercial average: 12–15 t/acre pods.  
- Leaves: 12–20 t/acre.  
- TNAU annual moringa: yield in pods under Tamil Nadu conditions well-documented (TNAU veggie page).  
- **Use in model:** 12 t/acre pods (central); 8–18 t/acre band.  
- Source: TNAU Annual Moringa page (agritech.tnau.ac.in/horticulture/horti_vegetables_annualmoringa.html); agrifarming.in drumstick project; signuptrendingnature.com.  
- **Confidence: HIGH** (TNAU directly covers moringa for TN; Thanjavur delta is a primary moringa belt — directly applicable).

**Price band (2022–2025, wholesale Tamil Nadu pods)**  
- **₹15–40/kg** at mandi (25th–75th percentile).  
- Season (Feb–May) peak: ₹30–50/kg. Monsoon season dip: ₹10–15/kg.  
- Tamil Nadu is a net exporter of drumstick to other Indian states and to Middle East/EU (dried leaves and pods).  
- Source: market.todaypricerates.com TN fruits; IndiaMART moringa.  
- **Confidence: MODERATE**.

**Market / surplus signal**  
- Thanjavur / Pudukkottai region is a major moringa belt; TN accounts for ~60% of India's drumstick production.  
- Domestic demand (daily cooking vegetable) is steady and deep.  
- **Signal: MODERATE LOCAL SURPLUS** — large local production; prices low locally. Export market (leaves powder, pods) provides premium.  
- **Recommendation:** viable as a low-risk, lower-margin inter-crop; combine with export-processing angle for better returns.

---

## NEGATIVE/UNSUITABLE EXAMPLE (kept for model calibration)

---

### 20. Avocado

**Reference yield / acre** — not applicable for Pattukkottai.  
**Price band** — ₹200–500/kg in Indian retail; high demand.  
**Market signal** — India imports ~95% of its avocado; premium domestic demand real.  
**Why excluded:** requires cool hill climate (Nilgiris, Kodaikanal; elevation >1,000 m). Pattukkottai plains (~5 m asl, 40°C peak summer) are fundamentally unsuitable — no microclimate engineering compensates for heat accumulation at this latitude. Layer 3 viability score should output ≈ 0 even with maximum shade/cooling in the optimizer.  
**Confidence: HIGH** that it is unsuitable.

---

## Summary Table (Layer 5 model inputs)

| Crop | Ref yield/acre (central) | Price band (₹/kg) | Market signal | Yield conf | Price conf |
|---|---|---|---|---|---|
| Pomegranate | 5 t | 40–120 | Favourable (TN deficit) | MODERATE | MODERATE |
| Dragon fruit | 8 t (mature) | 80–200 (falling) | AMBER (rapid supply growth) | MODERATE | MOD–LOW |
| Grapes | 7 t | 30–90 | Neutral–favourable | MOD–HIGH | MODERATE |
| Black pepper | 400 kg dry | 300–700 | Very favourable | MODERATE | MODERATE |
| Ginger | 8 t fresh | 30–160 (₹/kg) | Favourable (volatile) | MODERATE | MODERATE |
| Vanilla | 100 kg cured | ₹3,600–13,700 | Undersupplied; HIGH risk | LOW | LOW |
| Cocoa | 350 kg dry beans | 250–600 | Strongly favourable | MODERATE | MODERATE |
| Nutmeg | 400 kg nut | 600–900 | Neutral–favourable | LOW–MOD | LOW |
| Mango | 4.5 t | 25–80 | Neutral (seasonal surplus) | MODERATE | MODERATE |
| Banana | 20 t | 8–25 | HIGH local surplus | HIGH | HIGH |
| Guava | 10 t | 15–40 | Moderate surplus | MODERATE | MOD–LOW |
| Papaya | 14 t | 8–20 | HIGH surplus + perishable | MODERATE | MOD–LOW |
| Sapota | 5 t | 20–60 | Neutral | MODERATE | LOW |
| Custard apple | 5 t | 40–100 | Niche + perishable | MOD–LOW | LOW |
| Fig | 4 t | 60–150 | Thin market | LOW | LOW |
| Acid lime | 7 t | 10–60 | Neutral | MODERATE | MOD–LOW |
| Amla | 6 t | 12–45 | Neutral–favourable | MODERATE | MOD–LOW |
| Moringa | 12 t pods | 15–40 | Moderate local surplus | HIGH | MODERATE |
| **Avocado** | **N/A** | **200–500** | **UNSUITABLE (altitude)** | **HIGH** | **–** |

---

## Data gaps — priority list for next update

1. **Agmarknet 3-year pull** — run a programmatic query against Agmarknet for TN-specific mandi modal prices for: pomegranate, dragon fruit, grapes, ginger, pepper, banana, papaya, guava, mango (2022–2025). This upgrades MODERATE→HIGH confidence on all price bands.
2. **TNAU package-of-practices 2020 PDF** (agritech.tnau.ac.in/pdf/HORTICULTURE.pdf) — fetch and extract TN-specific yield per acre for all fruit crops. This should replace the national-level extrapolations in this document.
3. **Nutmeg + vanilla domestic mandi price** — these crops are not traded on standard Agmarknet mandis; seek Kerala Spices Board price data and APEDA export records for vanilla.
4. **Dragon fruit price trend 2025–26** — update quarterly as supply expansion is rapid and the price trajectory will alter the optimizer's recommendation.
5. **Local TN production-surplus cross-check** — obtain Tamil Nadu Horticulture Department annual report (tamilnadu.gov.in horticulture dept) for district-level production statistics.

---

## Sources cited

- TNAU Agritech Portal, Black Pepper: https://agritech.tnau.ac.in/horticulture/horti_spice%20crops_pepper.html
- TNAU Horticulture Cost of Cultivation: https://agritech.tnau.ac.in/horticulture/horti_cost%20of%20cultivation.html
- NHB Pomegranate Model Project: https://www.nhb.gov.in/report_files/pomegranate/POMEGRANATE.htm
- ICAR-NRCP Pomegranate Bulletin 2018: https://nrcpomegranate.in/wp-content/uploads/2025/09/8-1.pdf
- PIB / MIDH Dragon Fruit (Kamalam): https://www.pib.gov.in/PressReleasePage.aspx?PRID=1906572
- Vikaspedia Dragon Fruit (ICAR package): https://agriculture.vikaspedia.in/viewcontent/agriculture/crop-production/package-of-practices/fruits-1/dragon-fruit
- NIAM Dragon Fruit Cultivation Bulletin: https://niam.res.in/sites/default/files/pdfs/DragonFruitBulletin-27.pdf
- APEDA Grapes: https://apeda.gov.in/Grapes
- ICAR-CCARI Ginger DSS: https://ccari.icar.gov.in/dss/ginger.html
- TNAU Ginger PDF: https://agritech.tnau.ac.in/banking/pdf/Ginger.pdf
- Mongabay India Cocoa (Oct 2024): https://india.mongabay.com/2024/10/indian-farmers-choose-cocoa-amid-global-shortage/
- ICAR Annual Report 2023–24: https://icar.org.in/sites/default/files/2025-04/ICAR%20Annual%20Report%202023-24-english.pdf
- 6W Research India Vanilla Market 2024–2030: https://www.6wresearch.com/industry-report/india-vanilla-market
- Tridge Fresh Dragon Fruit India: https://dir.tridge.com/prices/fresh-dragon-fruit/IN
- Tridge Vanilla India: https://www.tridge.com/intelligences/vanilla/IN
- kisandeals.com Pomegranate TN: https://www.kisandeals.com/mandiprices/POMEGRANATE/TAMIL-NADU/ALL
- commodityonline.com Black Pepper: https://www.commodityonline.com/mandiprices/black-pepper
- CEIC Ginger TN production: https://www.ceicdata.com/en/india/production-of-horticulture-crops-in-major-states-spices-ginger/production-horticulture-crops-spices-ginger-tamil-nadu
- Kerala FWP Ginger time series: https://www.ecostat.kerala.gov.in/data-subset/450
- IndiaMART (pomegranate, grapes, fig, sapota, custard apple, nutmeg — bulk price quotes): https://dir.indiamart.com
- Global-agriculture.com India horticulture advance estimates 2023–24: https://www.global-agriculture.com/india-region/second-advance-estimates-of-2023-24-of-area-and-production-of-horticultural-crops/
- NHB Banana: https://www.nhb.gov.in/report_files/banana/BANANA.htm
- agrifarming.in (multiple crop project reports — secondary source citing NHB/ICAR)
- signuptrendingnature.com Drumstick / Moringa
- TNAU Annual Moringa: https://agritech.tnau.ac.in/horticulture/horti_vegetables_annualmoringa.html
- Agmarknet 2.0 (not directly queried in this pass; flagged as priority data gap): https://agmarknet.gov.in
- CEDA Agri Market Data (Ashoka): https://agmarknet.ceda.ashoka.edu.in/
