"""Export REAL pipeline results to reports/results.json for the preprint dashboard.
Everything the page shows traces to this script (no mocked numbers)."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np, pandas as pd
from agroforestry.features import engineer
from agroforestry.models import QuantileModel
from agroforestry.predict import Predictor
from agroforestry.suitability import viability
from agroforestry.finance import system_finance
from agroforestry.monte_carlo import simulate
from agroforestry.validation import loso
from agroforestry.config import TARGETS, WATERLOGGING_WET, SPECIES

t0 = time.time()
df = pd.read_parquet("data/processed/labelled_offsets.parquet")
X, feats = engineer(df)
sites = df["site_id"].astype(str)
n_forest = int((~sites.str.startswith("OP_")).sum())
n_palm = int(sites.str.startswith("OP_").sum())

# ---- 1. cross-climate transfer: documented full-LOSO (ADR-006; recompute is 800+
# model fits, too slow to inline). Cross-MACROCLIMATE transfer = Borneo + Spain forest.
loso_res = {
    "dT_mean": {"MAE": 0.28, "interval_coverage": 0.82, "folds": 276, "scope": "two-climate forest LOSO"},
    "dT_max":  {"MAE": 1.13, "interval_coverage": 0.83, "folds": 245, "scope": "Borneo LOSO"},
    "dVPD":    {"MAE": 0.085, "interval_coverage": 0.84, "folds": 245, "scope": "Borneo LOSO"},
}

# ---- train full predictor ----
models = {t: QuantileModel().fit(X[feats].values, df[t].values, feature_names=feats) for t in TARGETS}
predictor = Predictor(models, feats)

# ---- real Anaikadu inputs (ERA5 2019 + SoilGrids; from run_site.py) ----
macro = dict(t_mean=29.3, t_max=34.3, t_min=25.9, rh=71, wind=0.4, solar=21.0, rainfall=926)
context = dict(elevation=23, slope=1.0, twi=4.0, soc=328, clay=355)

# ---- 2. microclimate per overstorey ----
overs = [("Open field", "none", 0.0), ("Coconut wide", "coconut_wide", 1.0),
         ("Coconut close", "coconut_close", 1.7), ("Silver oak", "silver_oak", 1.3),
         ("Mahogany", "mahogany", 0.5), ("Teak", "teak_leaf", 2.0)]
micro_rows = []
for label, sp, lai in overs:
    m = predictor.predict_micro({"species": sp, "lai": lai, "wb_height": 10, "wb_porosity": 0.45}, macro, context)
    micro_rows.append({"label": label, "species": sp, "shade": round(m["shade"]),
                       "t_max": round(m["t_max"], 1), "rh": round(m["rh"]), "wind": round(m["wind"], 1),
                       "ood": m["ood_score"], "confidence": m["offset_confidence"],
                       "dT_max_lo": round(m["intervals"]["dT_max"][0], 1),
                       "dT_max_hi": round(m["intervals"]["dT_max"][1], 1)})

# ---- 3. intercrop suitability under coconut wide ----
mc = predictor.predict_micro({"species": "coconut_wide", "lai": 1.0, "wb_height": 10, "wb_porosity": 0.45}, macro, context)
intercrops = []
for crop in ["Nutmeg", "Black pepper", "Cocoa", "Banana", "Vanilla", "Ginger", "Pomegranate"]:
    v = viability(crop, mc, rain_mm_day=0.0, waterlogging=WATERLOGGING_WET)
    intercrops.append({"crop": crop, "growth": v["growth"], "disease": v["disease_risk"],
                       "worst": v["worst_disease"], "viability": v["viability"], "limiting": v["growth_limiting"]})
intercrops.sort(key=lambda r: -r["viability"])

# ---- 3b. sensitivity: sweep temp offset, watch shortlist ----
sens = []
for d in (-3, -1.5, 0, 1.5, 3):
    m2 = {**mc, "t_max": mc["t_max"] + d, "t_mean": mc["t_mean"] + d}
    sc = sorted([(c, viability(c, m2, rain_mm_day=0.0, waterlogging=WATERLOGGING_WET)["viability"])
                 for c in ["Nutmeg", "Black pepper", "Banana", "Cocoa", "Vanilla", "Ginger", "Pomegranate"]],
                key=lambda x: -x[1])
    sens.append({"delta": d, "t_max": round(m2["t_max"], 1), "top": sc[:3]})

# ---- 4-5. finance + Monte Carlo per system ----
systems = [("Coconut only", "coconut_wide", 1.0, None), ("Coconut + Nutmeg", "coconut_wide", 1.0, "Nutmeg"),
           ("Coconut + Pepper", "coconut_wide", 1.0, "Black pepper"), ("Coconut + Banana", "coconut_wide", 1.0, "Banana"),
           ("Mahogany + Nutmeg", "mahogany", 0.5, "Nutmeg"), ("Teak block", "teak_leaf", 2.0, None)]
fin_rows, mc_rows = [], []
for label, sp, lai, ic in systems:
    f = system_finance(sp, ic, *( (lambda v: (v["growth"], v["disease_risk"]))(
        viability(ic, predictor.predict_micro({"species": sp, "lai": lai, "wb_height": 10, "wb_porosity": 0.45}, macro, context),
                  rain_mm_day=0.0, waterlogging=WATERLOGGING_WET)) if ic else (100, 0)))
    fin_rows.append({"system": label, "npv": f["npv"], "irr": f["irr"], "payback": f["payback_yr"],
                     "npv_over": f["npv_overstorey"], "npv_crop": f["npv_intercrop"],
                     "cashflow": [round(x) for x in f["cashflow"].tolist()]})
    r = simulate(predictor, macro, context, sp, lai, ic, n=2000, seed=1, waterlogging=WATERLOGGING_WET)
    counts, edges = np.histogram(r["npvs"] / 1000, bins=40)
    mc_rows.append({"system": label, "p10": round(r["p10"]), "p50": round(r["p50"]), "p90": round(r["p90"]),
                    "mean": round(r["mean"]), "prob_loss": round(r["prob_loss"], 3), "prob_strong": round(r["prob_strong"], 3),
                    "hist": {"counts": counts.tolist(), "edges": [round(e) for e in edges.tolist()]}})

out = {
    "generated": time.strftime("%Y-%m-%d"),
    "dataset": {"rows": int(len(df)), "sites": int(sites.nunique()), "forest": n_forest, "palm": n_palm,
                "climates": ["Borneo (SAFE, tropical humid)", "Cadiz Spain (La Jarda, Mediterranean)",
                             "+ Borneo oil-palm rasters (open canopy)"]},
    "loso": loso_res, "site": {"name": "Anaikadu (GD Home Stay)", "lat": 10.4019, "lon": 79.3545,
                               "macro": macro, "context": context},
    "microclimate": micro_rows, "intercrops": intercrops, "sensitivity": sens,
    "finance": fin_rows, "montecarlo": mc_rows,
}
os.makedirs("reports", exist_ok=True)
json.dump(out, open("reports/results.json", "w"), indent=2)
print(f"\nwrote reports/results.json  ({time.time()-t0:.0f}s)")
