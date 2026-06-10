"""Profit-based inverse design at Anaikadu: for each robust intercrop, find the
system design (overstorey, canopy density, windbreak, drainage) that maximises
risk-aware annualised margin -- once over the FULL space (timber allowed) and once
constrained to a coconut overstorey (annual cash income)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pandas as pd
from agroforestry.features import engineer
from agroforestry.models import QuantileModel
from agroforestry.predict import Predictor
from agroforestry.optimize import optimise
from agroforestry.config import TARGETS, WATERLOGGING_WET, SPECIES

df = pd.read_parquet("data/processed/labelled_offsets.parquet")
X, feats = engineer(df)
models = {t: QuantileModel().fit(X[feats].values, df[t].values, feature_names=feats) for t in TARGETS}
predictor = Predictor(models, feats)

macro = dict(t_mean=29.3, t_max=34.3, t_min=25.9, rh=71, wind=0.4, solar=21.0, rainfall=926)
context = dict(elevation=23, slope=1.0, twi=4.0, soc=328, clay=355)


def money(x):
    return f"Rs {x/1000:,.0f}k"


def show(tag, b):
    d = b["design"]
    print(f"  [{tag}] {SPECIES[d['species']]['label']:14s} lai {d['lai']:.2f}  "
          f"windbreak h{d['wb_height']} por{d['wb_porosity']}  drainage {d.get('drainage')}")
    print(f"        growth {b['growth']}  disease {b['disease_risk']}  | overstorey {money(b['overstorey_income'])}"
          f" + intercrop {money(b['intercrop_margin'])} = SYSTEM exp {money(b['system_expected'])}"
          f"  (downside {money(b['system_downside'])})")


coconut_only = ["coconut_wide", "coconut_close"]
for crop in ["Nutmeg", "Black pepper", "Banana"]:
    print(f"\n=== Best system for intercrop: {crop} (Anaikadu) ===")
    full = optimise(predictor, crop, macro, context, objective="profit",
                    rain_mm_day=0.0, waterlogging=WATERLOGGING_WET)
    coco = optimise(predictor, crop, macro, context, objective="profit",
                    rain_mm_day=0.0, waterlogging=WATERLOGGING_WET, species_list=coconut_only)
    show("FULL space", full)
    show("coconut overstorey", coco)
print("\nNOTE: the FULL-space optimum often picks TIMBER overstorey -- its annualised value")
print("dominates on Rs, but it is LOW confidence and a 15-18 yr cash lock-up (no annual income).")
print("The coconut-overstorey row is the trustworthy ANNUAL-CASH design. Read them together:")
print("coconut+spice for yearly income, a timber block/boundary for long-horizon capital.")
