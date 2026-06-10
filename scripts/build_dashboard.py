"""Build the self-contained preprint dashboard from reports/results.json.
Inlines the data so the HTML opens locally with no server. Reproducible:
  uv run python scripts/export_results.py && uv run python scripts/build_dashboard.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
data = json.load(open(os.path.join(ROOT, "reports", "results.json"), encoding="utf-8"))

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agroforestry microclimate-to-profit model — Anaikadu, Tamil Nadu</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--bg:#faf8f4;--ink:#23291f;--muted:#6b7363;--line:#e3e0d6;--card:#fff;--head:#2f3a28;
--accent:#4a6b3a;--accent2:#7a5a2e;--g:#3f8f4f;--gbg:#e6f1e6;--a:#b9852b;--abg:#fbf1dc;--r:#b3503f;--rbg:#f7e2dd;--blue:#3a6b8f;}
*{box-sizing:border-box}
body{font-family:-apple-system,Segoe UI,Roboto,Georgia,serif;background:var(--bg);color:var(--ink);margin:0;line-height:1.55;font-size:15px}
.wrap{max-width:920px;margin:0 auto;padding:0 22px 80px}
header.top{border-bottom:2px solid var(--head);padding:34px 0 18px;margin-bottom:8px}
h1{font-size:27px;line-height:1.25;margin:0 0 8px;color:var(--head);font-family:Georgia,serif}
.authors{font-size:14.5px;color:var(--ink);margin:6px 0 2px}
.affil{font-size:13px;color:var(--muted);margin:0 0 10px}
.tag{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.03em;background:var(--abg);color:var(--a);padding:2px 9px;border-radius:11px;margin-right:6px}
nav{position:sticky;top:0;background:rgba(250,248,244,.96);backdrop-filter:blur(4px);border-bottom:1px solid var(--line);padding:9px 0;margin-bottom:22px;z-index:20;font-size:12.5px}
nav a{color:var(--accent);text-decoration:none;margin-right:14px;white-space:nowrap}
nav a:hover{text-decoration:underline}
section{margin:30px 0;scroll-margin-top:52px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--accent);border-bottom:1px solid var(--line);padding-bottom:6px;margin:0 0 14px}
h3{font-size:15px;color:var(--head);margin:18px 0 6px}
p{margin:0 0 12px}
.abstract{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:8px;padding:16px 18px;font-size:14.5px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:12px 0}
.mc{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:11px 12px}
.mc .lab{font-size:10.5px;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.03em}
.mc .num{font-size:22px;font-weight:700;margin-top:3px;color:var(--head)}
.mc .unit{font-size:12px;color:var(--muted);font-weight:500}
.badge{display:inline-block;font-size:9.5px;font-weight:800;padding:2px 7px;border-radius:10px;letter-spacing:.03em}
.b-hi{background:var(--gbg);color:var(--g)}.b-mod{background:var(--abg);color:var(--a)}.b-lo{background:var(--rbg);color:var(--r)}
table{border-collapse:collapse;width:100%;font-size:13px;margin:10px 0}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:right}
th:first-child,td:first-child{text-align:left}
th{background:var(--head);color:#fff;font-weight:600}
tr:nth-child(even) td{background:#fbfaf6}
.panel{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:12px 0}
select{padding:6px 10px;border:1px solid var(--line);border-radius:6px;font-size:13.5px;background:#fff;font-weight:600;color:var(--head)}
.bar{height:15px;background:#ececec;border-radius:8px;overflow:hidden;margin-top:2px}
.bar span{display:block;height:100%;border-radius:8px}
.crop{margin:8px 0}.crop .top{display:flex;justify-content:space-between;font-size:13px;font-weight:600}
.lim{font-size:11px;color:var(--muted)}
.note{font-size:12.5px;color:var(--muted);font-style:italic;margin-top:8px}
.layer{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin:10px 0}
.lbox{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:12.5px;font-weight:600;text-align:center;min-width:96px}
.lbox small{display:block;font-weight:500;color:var(--muted);font-size:10px;margin-top:2px}
.arrow{color:var(--muted);font-size:16px}
.chartbox{position:relative;height:300px;margin-top:10px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:760px){.two{grid-template-columns:1fr}nav{overflow-x:auto;white-space:nowrap}}
.rec{background:var(--gbg);border:1px solid var(--g);border-radius:10px;padding:16px 18px}
.foot{font-size:12px;color:var(--muted);border-top:1px solid var(--line);margin-top:30px;padding-top:14px}
code{background:#f0efe7;padding:1px 5px;border-radius:4px;font-size:12.5px}
ul{margin:6px 0 12px;padding-left:20px}li{margin:4px 0}
</style></head>
<body><div class="wrap">

<header class="top">
<div><span class="tag">PREPRINT</span><span class="tag" style="background:var(--gbg);color:var(--g)">REPRODUCIBLE</span></div>
<h1>From canopy design to crop profit under uncertainty: an honesty-first agroforestry microclimate model applied to a smallholder coconut farm in Tamil Nadu</h1>
<div class="authors">Leo Antony</div>
<div class="affil">Independent research · Anaikadu (Pattukkottai), Thanjavur District, Tamil Nadu, India · <span id="gen"></span></div>
<div class="abstract" id="abstract"></div>
</header>

<nav>
<a href="#pipeline">Pipeline</a><a href="#site">Site</a><a href="#methods">Methods</a>
<a href="#transfer">Transfer</a><a href="#micro">Microclimate</a><a href="#crops">Crops</a>
<a href="#econ">Economics</a><a href="#uncertainty">Uncertainty</a><a href="#limits">Limitations</a>
<a href="#rec">Recommendation</a><a href="#repro">Reproducibility</a>
</nav>

<section id="pipeline"><h2>1 · The six-layer pipeline</h2>
<p>Each layer carries an explicit confidence level. Mechanistic physics is HIGH; learned offsets are MODERATE and flagged LOW where a design lies outside the training distribution; downstream economics inherit and propagate that uncertainty rather than hiding it.</p>
<div class="layer" id="layerflow"></div>
<p class="note">Design &rarr; microclimate is part physics (light, wind) and part machine-learned offset (temperature, vapour-pressure deficit); the learned part is validated for transfer across macroclimates and flagged when extrapolating.</p>
</section>

<section id="site"><h2>2 · Study site (real inputs)</h2>
<p id="sitep"></p><div class="cards" id="sitecards"></div>
<p class="note">Macroclimate from ERA5 (2019), soil from SoilGrids, terrain from Copernicus DEM — sampled at the exact plot. Note: a ~31 km reanalysis pixel cannot resolve the village from the town, motivating on-plot sensing (see Limitations).</p>
</section>

<section id="methods"><h2>3 · Methods (condensed)</h2>
<table><thead><tr><th>Layer</th><th>Approach</th><th>Confidence</th></tr></thead><tbody id="methodtbl"></tbody></table>
</section>

<section id="transfer"><h2>4 · Result — cross-macroclimate transfer</h2>
<p>The core scientific claim is that the canopy&rarr;microclimate <em>offset</em> learned in one climate transfers to another. Leave-one-site-out (LOSO) cross-validation holds out an entire site per fold — the honest test of transfer. Models trained on tropical Borneo (SAFE) + Mediterranean Spain (La Jarda) forest plots predict an unseen site's offset to:</p>
<div class="cards" id="losocards"></div>
<p class="note" id="losonote"></p>
</section>

<section id="micro"><h2>5 · Result — under-canopy microclimate at Anaikadu</h2>
<p>Predicted microclimate beneath candidate overstoreys. Shade and wind are physics (HIGH); the temperature/VPD offset is the learned part and is flagged LOW here because coconut is an open palm canopy unlike the closed-forest training data (out-of-distribution).</p>
<p><label>Overstorey: </label><select id="oversel"></select></p>
<div class="cards" id="micards"></div>
<div class="panel"><h3 style="margin-top:0">Light reduction (shade %) by overstorey — physics, HIGH confidence</h3><div class="chartbox"><canvas id="shadeChart"></canvas></div></div>
</section>

<section id="crops"><h2>6 · Result — intercrop suitability &amp; its robustness</h2>
<div class="two"><div>
<h3>Viability under coconut (median prediction)</h3><div id="cropbars"></div>
<p class="note">Viability = growth fit &times; (1 &minus; disease risk). All candidates are temperature-limited at this hot site.</p>
</div><div>
<h3>Sensitivity: does the uncertain temperature offset change the shortlist?</h3>
<table><thead><tr><th>scenario</th><th>t_max</th><th>top 3 (viability)</th></tr></thead><tbody id="senstbl"></tbody></table>
<p class="note">The <b>shortlist (nutmeg, pepper, banana) is robust</b> across the whole plausible temperature band; only the absolute level moves. So the pending data changes <em>how well</em>, not <em>which</em> crops — the decision is actionable now.</p>
</div></div></section>

<section id="econ"><h2>7 · Result — economics &amp; finance</h2>
<p>Staged, transparent (not trained): reference yield &times; suitability &times; (1&minus;disease), priced against validated mandi bands, minus validated costs, over a 25-year horizon at 8% real discount. NPV / IRR / payback respect timing (gestation, bearing ramp, timber harvested once).</p>
<table><thead><tr><th>System</th><th>NPV (&#8377;/ac)</th><th>IRR</th><th>Payback</th></tr></thead><tbody id="fintbl"></tbody></table>
<div class="panel"><h3 style="margin-top:0">Cash-flow timeline <select id="cfsel"></select></h3><div class="chartbox"><canvas id="cfChart"></canvas></div>
<p class="note">Coconut+spice gives steady annual cash; timber is a single far-off harvest spike — a different financial animal (high return, late payback, risk concentrated at harvest; timber inputs are LOW confidence).</p></div>
</section>

<section id="uncertainty"><h2>8 · Result — uncertainty (Monte Carlo)</h2>
<p>Every point estimate (temperature offset, yield, price, timber value) is sampled across its band and pushed through the same chain (n=2000) to a distribution of 25-year NPV and a probability of loss.</p>
<table><thead><tr><th>System</th><th>P10</th><th>P50</th><th>P90</th><th>P(loss)</th></tr></thead><tbody id="mctbl"></tbody></table>
<div class="panel"><h3 style="margin-top:0">NPV distribution <select id="mcsel"></select></h3><div class="chartbox"><canvas id="mcChart"></canvas></div>
<p class="note" id="mcnote"></p></div>
</section>

<section id="limits"><h2>9 · Limitations (stated, not hidden)</h2><ul id="limul"></ul></section>

<section id="rec"><h2>10 · Recommendation</h2><div class="rec" id="recbox"></div></section>

<section id="repro"><h2>11 · Reproducibility &amp; data</h2>
<p>Every figure traces to a committed script. Pipeline: <code>src/agroforestry/</code> (physics, models, suitability, disease, economics, finance, monte_carlo); numbers here exported by <code>scripts/export_results.py</code> &rarr; <code>reports/results.json</code>. Design decisions logged as ADRs (<code>docs/architectural_decision_records/</code>).</p>
<p><b>Data:</b> SAFE Project Borneo microclimate (Zenodo 1228188) + gazetteer (3906082); La Jarda, C&aacute;diz (Zenodo 18913503); SAFE landscape microclimate rasters (Zenodo 7893600); ERA5 / ERA5-Land; SoilGrids; Copernicus DEM; MODIS LAI/NDVI; ETH canopy height; SoilTemp/SBIO (GEE). Economics: NHB DPRs, TNAU cost-of-cultivation, Salem District study, live data.gov.in Agmarknet.</p>
<div class="foot">Generated <span id="gen2"></span> from real pipeline output. Confidence labels: <span class="badge b-hi">HIGH</span> mechanistic · <span class="badge b-mod">MODERATE</span> learned/validated · <span class="badge b-lo">LOW</span> extrapolation. This is a research preprint; figures are model output with stated uncertainty, not guarantees.</div>
</section>

</div>
<script>const DATA = __DATA__;</script>
<script>
const $=s=>document.querySelector(s), el=(t,c,h)=>{const e=document.createElement(t);if(c)e.className=c;if(h!=null)e.innerHTML=h;return e};
const inr=v=>(v>=0?'₹':'-₹')+Math.abs(Math.round(v/1000)).toLocaleString()+'k';
const badge=c=>c&&c.indexOf('LOW')>=0?'b-lo':c==='HIGH'?'b-hi':'b-mod';
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();

$('#gen').textContent='generated '+DATA.generated; $('#gen2').textContent=DATA.generated;
$('#abstract').innerHTML="<b>Abstract.</b> Smallholders deciding how to design an agroforestry plot face a chain of coupled questions — how a chosen canopy reshapes the local microclimate, which crops then become viable once disease is accounted for, and whether the result actually pays. We build a six-layer model that answers this end-to-end: mechanistic physics for light and wind, machine-learned (gradient-boosted, quantile) offsets for temperature and vapour-pressure deficit, a two-axis disease model, fuzzy limiting-factor suitability, and a staged economics + discounted-cash-flow layer, with uncertainty propagated by Monte Carlo. The learned offset transfers across macroclimates (leave-one-site-out dT_mean MAE "+DATA.loso.dT_mean.MAE+"°C, trained on Borneo + Mediterranean Spain), and the model flags when a design (here, open coconut canopy) lies outside its training distribution rather than over-claiming. Applied to a real farm in Anaikadu, Tamil Nadu, the system identifies a robust intercrop shortlist (nutmeg, black pepper) whose ranking is insensitive to the uncertain temperature offset, and shows coconut+pepper clearing an 8% hurdle (NPV ≈ ₹230k/acre, IRR ≈ 20%, payback 9 yr) while quantifying its probability of loss. A reality-check that initially mislabelled coconut as loss-making — traced to a gestation-cost bug — is reported as a methodological illustration of validation discipline.";

// pipeline flow
const layers=[['Design','canopy, windbreak'],['Microclimate','physics + ML offset'],['Disease','two-axis'],['Suitability','fuzzy / limiting'],['Economics','yield×price−cost'],['Finance + risk','NPV/IRR, Monte Carlo']];
const lf=$('#layerflow');layers.forEach((L,i)=>{lf.appendChild(el('div','lbox',L[0]+'<small>'+L[1]+'</small>'));if(i<layers.length-1)lf.appendChild(el('span','arrow','→'))});

// site
const s=DATA.site, m=s.macro, c=s.context;
$('#sitep').innerHTML='<b>'+s.name+'</b> ('+s.lat+'°N, '+s.lon+'°E). Real macroclimate and soil at the plot:';
const sc=[['Mean temp',m.t_mean,'°C'],['Max temp',m.t_max,'°C'],['Min temp',m.t_min,'°C'],['Humidity',m.rh,'%'],['Rainfall',m.rainfall,'mm/yr'],['Wind',m.wind,'m/s'],['Clay',c.clay,'g/kg'],['Soil C',c.soc,'g/kg'],['Elevation',c.elevation,'m']];
sc.forEach(r=>$('#sitecards').appendChild(el('div','mc','<div class="lab">'+r[0]+'</div><div class="num">'+r[1]+'<span class="unit"> '+r[2]+'</span></div>')));

// methods
const meth=[['Light / shade','Beer–Lambert extinction through canopy (LAI, k)','HIGH'],
['Wind','Shelterbelt porosity / drag reduction','HIGH'],
['Temp & VPD offset','XGBoost quantile regression + conformalised intervals; LOSO transfer; OOD flag','MODERATE'],
['Disease','Two axes: air microclimate (foliar) + soil-water/waterlogging (soil-borne)','MODERATE'],
['Suitability','Fuzzy trapezoidal membership; Liebig limiting factor','MODERATE'],
['Economics','Reference yield × growth × (1−disease); banded price−cost','MODERATE'],
['Finance','25-yr cash-flow w/ gestation+harvest timing; NPV/IRR/payback','MODERATE'],
['Uncertainty','Monte Carlo over offset+yield+price+timber bands','MODERATE']];
meth.forEach(r=>{const tr=el('tr');tr.innerHTML='<td>'+r[0]+'</td><td>'+r[1]+'</td><td style="text-align:center"><span class="badge '+badge(r[2])+'">'+r[2]+'</span></td>';$('#methodtbl').appendChild(tr)});

// LOSO
const lo=DATA.loso;
[['dT_max','°C'],['dT_mean','°C'],['dVPD','kPa']].forEach(([k,u])=>{
$('#losocards').appendChild(el('div','mc','<div class="lab">'+k+' MAE</div><div class="num">'+lo[k].MAE+'<span class="unit"> '+u+'</span></div><div class="lim">coverage '+lo[k].interval_coverage+'</div>'))});
$('#losonote').textContent='Folds: '+lo.dT_mean.folds+' forest plots, two macroclimates ('+lo.dT_mean.scope+'). Prediction-interval coverage near the 0.8 target indicates calibrated, not over-confident, uncertainty. Full LOSO recorded in ADR-006.';

// microclimate selector
const ovsel=$('#oversel');DATA.microclimate.forEach((o,i)=>ovsel.appendChild(new Option(o.label,i)));
function drawMicro(){const o=DATA.microclimate[ovsel.value];
const cards=[['Shade',o.shade,'%','HIGH'],['Max temp',o.t_max,'°C',o.confidence],['Humidity',o.rh,'%',o.confidence],['Wind',o.wind,'m/s','HIGH']];
$('#micards').innerHTML='';cards.forEach(r=>$('#micards').appendChild(el('div','mc','<div class="lab">'+r[0]+'</div><div class="num">'+r[1]+'<span class="unit"> '+r[2]+'</span></div><div style="margin-top:4px"><span class="badge '+badge(r[3])+'">'+(r[3]==='HIGH'?'HIGH':'offset '+r[3])+'</span></div>')));
$('#micards').appendChild(el('div','mc','<div class="lab">OOD score</div><div class="num">'+o.ood+'</div><div class="lim">dT_max band '+o.dT_max_lo+'..'+o.dT_max_hi+'°C</div>'));}
ovsel.value=1;ovsel.onchange=drawMicro;drawMicro();
new Chart($('#shadeChart'),{type:'bar',data:{labels:DATA.microclimate.map(o=>o.label),datasets:[{label:'Shade %',data:DATA.microclimate.map(o=>o.shade),backgroundColor:css('--accent')}]},options:{plugins:{legend:{display:false}},scales:{y:{title:{display:true,text:'shade %'},max:100}}}});

// crops
const maxv=100;DATA.intercrops.forEach(r=>{const col=r.viability>=40?css('--g'):r.viability>=15?css('--a'):css('--r');
const d=el('div','crop','<div class="top"><span>'+r.crop+(r.worst?' <span class="lim">('+r.worst+')</span>':'')+'</span><span>'+r.viability+'</span></div><div class="bar"><span style="width:'+(r.viability/maxv*100)+'%;background:'+col+'"></span></div><div class="lim">growth '+r.growth+' · disease '+r.disease+' · limiting: '+r.limiting+'</div>');$('#cropbars').appendChild(d)});
DATA.sensitivity.forEach(s=>{const tr=el('tr');tr.innerHTML='<td>'+(s.delta>0?'+':'')+s.delta+'°C</td><td>'+s.t_max+'</td><td style="text-align:left">'+s.top.map(t=>t[0]+'('+t[1]+')').join(', ')+'</td>';$('#senstbl').appendChild(tr)});

// finance
DATA.finance.forEach(f=>{const tr=el('tr');const irr=f.irr!=null?(f.irr*100).toFixed(0)+'%':'—';const pb=f.payback?f.payback+' yr':'never';
tr.innerHTML='<td>'+f.system+'</td><td>'+inr(f.npv)+'</td><td>'+irr+'</td><td>'+pb+'</td>';
if(f.system.indexOf('Pepper')>=0)tr.style.fontWeight='700';$('#fintbl').appendChild(tr)});
const cfsel=$('#cfsel');DATA.finance.forEach((f,i)=>cfsel.appendChild(new Option(f.system,i)));
let cfChart;function drawCF(){const f=DATA.finance[cfsel.value];const yrs=f.cashflow.map((_,i)=>i+1);
if(cfChart)cfChart.destroy();cfChart=new Chart($('#cfChart'),{type:'bar',data:{labels:yrs,datasets:[{label:'net cash ₹/acre',data:f.cashflow,backgroundColor:f.cashflow.map(v=>v>=0?css('--g'):css('--r'))}]},options:{plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:'year'}},y:{title:{display:true,text:'₹/acre'}}}}});}
cfsel.value=2;cfsel.onchange=drawCF;drawCF();

// monte carlo
DATA.montecarlo.forEach(r=>{const tr=el('tr');const pl=Math.round(r.prob_loss*100);
const plcol=pl<=10?css('--g'):pl<=40?css('--a'):css('--r');
tr.innerHTML='<td>'+r.system+'</td><td>'+inr(r.p10)+'</td><td>'+inr(r.p50)+'</td><td>'+inr(r.p90)+'</td><td style="color:'+plcol+';font-weight:700">'+pl+'%</td>';
if(r.system.indexOf('Pepper')>=0)tr.style.fontWeight='700';$('#mctbl').appendChild(tr)});
const mcsel=$('#mcsel');DATA.montecarlo.forEach((r,i)=>mcsel.appendChild(new Option(r.system,i)));
let mcChart;function drawMC(){const r=DATA.montecarlo[mcsel.value];const e=r.hist.edges;
const labels=r.hist.counts.map((_,i)=>e[i]);const cols=r.hist.counts.map((_,i)=>e[i]<0?css('--r'):css('--g'));
if(mcChart)mcChart.destroy();mcChart=new Chart($('#mcChart'),{type:'bar',data:{labels:labels,datasets:[{data:r.hist.counts,backgroundColor:cols}]},options:{plugins:{legend:{display:false},tooltip:{callbacks:{title:i=>'NPV ≈ ₹'+labels[i[0].dataIndex]+'k'}}},scales:{x:{title:{display:true,text:'NPV (₹ 000/acre)'},ticks:{maxTicksLimit:12}},y:{title:{display:true,text:'draws'}}}}});
$('#mcnote').innerHTML='P(loss) = '+Math.round(r.prob_loss*100)+'%  ·  P(NPV>₹250k) = '+Math.round(r.prob_strong*100)+'%. '+(r.system.indexOf('Nutmeg')>=0&&r.system.indexOf('Coconut')>=0?'The bimodal shape is the temperature uncertainty made visible: hot draws fail the crop (left), cool draws pay well (right).':r.system.indexOf('Teak')>=0||r.system.indexOf('Mahogany')>=0?'Timber’s near-zero P(loss) is optimistic — the bands omit market/mortality/harvest-timing risk (LOW confidence).':'');}
mcsel.value=2;mcsel.onchange=drawMC;drawMC();

// limitations
['The under-coconut <b>temperature offset is extrapolation</b> (forest-trained, open palm canopy): flagged LOW, OOD≈0.5. Physics (shade, wind) stays reliable; the shortlist is robust to it (sensitivity).',
'A <b>macroclimate-transfer gap</b> remains: warm-night semi-arid Tamil Nadu has no close analog in the humid-tropical + Mediterranean training set (quantified vs SBIO).',
'Economics are <b>MODERATE confidence</b>: yields/prices from TNAU/ICAR/NHB + live Agmarknet; costs validated vs NHB DPRs; a clean 3-yr CEDA price series is still pending (site bot-blocked).',
'Reanalysis cannot resolve the village from the town (shared ~31 km ERA5 pixel) — an on-plot logger (year 1) is the definitive fix and would collapse the temperature uncertainty.',
'Timber returns rest on LOW-confidence farm-gate prices and a single distant harvest; treat as capital-appreciation, not income.'
].forEach(t=>$('#limul').appendChild(el('li',null,t)));

// recommendation
$('#recbox').innerHTML="<b>For Anaikadu:</b> plant <b>coconut as the overstorey with black pepper (and nutmeg) as the intercrop</b> for resilient annual cash — pepper clears the 8% hurdle (NPV ≈ "+inr(DATA.finance.find(f=>f.system.indexOf('Pepper')>=0).npv)+"/acre, IRR ≈ "+(DATA.finance.find(f=>f.system.indexOf('Pepper')>=0).irr*100).toFixed(0)+"%, payback 9 yr) with the lowest probability of loss of the intercrops. Add a <b>teak or mahogany block / boundary</b> as long-horizon capital and windbreak (high modelled return but a 15–18 yr lock-up, LOW-confidence prices). Avoid banana under mature coconut (heat- and shade-limited here). The choice of <em>which</em> crop is robust to the model’s remaining temperature uncertainty; one season of on-plot sensing would sharpen <em>how well</em> it performs.";
</script>
</body></html>"""

html = TEMPLATE.replace("__DATA__", json.dumps(data))
out = os.path.join(ROOT, "reports", "anaikadu_preprint.html")
open(out, "w", encoding="utf-8").write(html)
print("wrote", out, f"({len(html)//1024} KB)")
