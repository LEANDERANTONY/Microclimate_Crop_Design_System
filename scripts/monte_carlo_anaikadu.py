"""Monte Carlo NPV distributions for candidate systems at Anaikadu.
Propagates temperature-offset + yield + price + timber uncertainty -> P(loss), P10/50/90."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np, pandas as pd
from agroforestry.features import engineer
from agroforestry.models import QuantileModel
from agroforestry.predict import Predictor
from agroforestry.monte_carlo import simulate
from agroforestry.config import TARGETS, WATERLOGGING_WET

df = pd.read_parquet("data/processed/labelled_offsets.parquet")
X, feats = engineer(df)
models = {t: QuantileModel().fit(X[feats].values, df[t].values, feature_names=feats) for t in TARGETS}
predictor = Predictor(models, feats)
macro = dict(t_mean=29.3, t_max=34.3, t_min=25.9, rh=71, wind=0.4, solar=21.0, rainfall=926)
context = dict(elevation=23, slope=1.0, twi=4.0, soc=328, clay=355)

systems = [
    ("Coconut only",        "coconut_wide", 1.0, None),
    ("Coconut + Nutmeg",    "coconut_wide", 1.0, "Nutmeg"),
    ("Coconut + Pepper",    "coconut_wide", 1.0, "Black pepper"),
    ("Coconut + Banana",    "coconut_wide", 1.0, "Banana"),
    ("Mahogany + Nutmeg",   "mahogany",     0.5, "Nutmeg"),
    ("Teak block (timber)", "teak_leaf",    2.0, None),
]

print(f"Monte Carlo (n=3000) | Anaikadu | 8% real | 25 yr | NPV Rs/acre (k=thousand)\n")
print(f"{'system':22s} {'P10':>9s} {'P50':>9s} {'P90':>9s} {'mean':>9s}  {'P(loss)':>8s} {'P(>250k)':>9s}")
res = {}
for label, sp, lai, ic in systems:
    r = simulate(predictor, macro, context, sp, lai, ic, n=3000, seed=1, waterlogging=WATERLOGGING_WET)
    res[label] = r
    print(f"{label:22s} {r['p10']/1000:8,.0f}k {r['p50']/1000:8,.0f}k {r['p90']/1000:8,.0f}k "
          f"{r['mean']/1000:8,.0f}k  {r['prob_loss']*100:7.0f}% {r['prob_strong']*100:8.0f}%")

# optional histogram
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(9, 5))
    for label in ["Coconut + Nutmeg", "Coconut + Pepper", "Mahogany + Nutmeg"]:
        plt.hist(res[label]["npvs"] / 1000, bins=60, alpha=0.5, label=label)
    plt.axvline(0, color="k", lw=1, ls="--")
    plt.xlabel("NPV (Rs '000 / acre, 25 yr @ 8%)"); plt.ylabel("draws")
    plt.title("Anaikadu agroforestry — NPV distributions (Monte Carlo)")
    plt.legend()
    os.makedirs("reports", exist_ok=True)
    plt.savefig("reports/monte_carlo_npv.png", dpi=110, bbox_inches="tight")
    print("\nsaved reports/monte_carlo_npv.png")
except Exception as e:
    print("\n(plot skipped:", type(e).__name__, str(e)[:60], ")")

print("\nRead: P(loss) = chance NPV<0 over 25 yr; P(>250k) = chance of a clearly good outcome.")
print("A high mean with high P(loss) is a gamble; a steadier positive P50 with low P(loss) is")
print("the resilient choice. Timber shows P(loss) 0% ONLY because its bands omit market/")
print("mortality/harvest-timing risk (LOW confidence) -- treat that 0% as optimistic.")
