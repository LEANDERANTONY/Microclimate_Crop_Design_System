"""Generate README figures from reports/results.json -> figures/*.png."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = json.load(open("reports/results.json", encoding="utf-8"))
os.makedirs("figures", exist_ok=True)
INK, ACC, G, A, RED, MUT = "#23291f", "#4a6b3a", "#3f8f4f", "#b9852b", "#b3503f", "#6b7363"
plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#cfccc0", "axes.titlesize": 12,
                     "axes.titleweight": "bold", "figure.facecolor": "white", "axes.facecolor": "white"})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(f"figures/{name}", dpi=120, bbox_inches="tight")
    plt.close(fig)
    print("wrote figures/" + name)


# 1. cross-climate transfer (LOSO MAE)
lo = R["loso"]
fig, ax = plt.subplots(figsize=(5.2, 3.2))
ks = ["dT_max", "dT_mean", "dVPD"]
vals = [lo[k]["MAE"] for k in ks]
bars = ax.bar(ks, vals, color=[A, G, ACC])
for b, v, k in zip(bars, vals, ks):
    u = "kPa" if k == "dVPD" else "°C"
    ax.text(b.get_x() + b.get_width() / 2, v, f" {v} {u}", ha="center", va="bottom", fontsize=10)
ax.set_ylabel("LOSO MAE"); ax.set_title("Cross-macroclimate transfer (leave-one-site-out)")
ax.set_ylim(0, max(vals) * 1.3)
fig.text(0.5, -0.02, "Trained on Borneo + Mediterranean Spain forest plots; held-out site error.",
         ha="center", fontsize=8.5, color=MUT)
save(fig, "fig1_transfer.png")

# 2. shade by overstorey (physics)
mi = R["microclimate"]
fig, ax = plt.subplots(figsize=(6, 3.2))
labs = [m["label"] for m in mi]; sh = [m["shade"] for m in mi]
ax.barh(labs, sh, color=ACC); ax.invert_yaxis()
for i, v in enumerate(sh):
    ax.text(v + 1, i, f"{v}%", va="center", fontsize=9.5)
ax.set_xlabel("light reduction / shade (%)"); ax.set_xlim(0, 100)
ax.set_title("Under-canopy shade by overstorey (physics, HIGH confidence)")
save(fig, "fig2_microclimate.png")

# 3. intercrop viability + temperature sensitivity
ic = R["intercrops"]; sens = R["sensitivity"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 3.4))
crops = [c["crop"] for c in ic][::-1]; v = [c["viability"] for c in ic][::-1]
cols = [G if x >= 40 else A if x >= 15 else RED for x in v]
a1.barh(crops, v, color=cols)
for i, x in enumerate(v):
    a1.text(x + 1, i, str(x), va="center", fontsize=9)
a1.set_xlabel("viability (0-100)"); a1.set_xlim(0, 105)
a1.set_title("Intercrop viability under coconut")
top3 = ["Nutmeg", "Black pepper", "Banana"]
for crop in top3:
    ys = []
    for s in sens:
        d = dict(s["top"])
        ys.append(d.get(crop, 0))
    a2.plot([s["t_max"] for s in sens], ys, marker="o", label=crop)
a2.set_xlabel("under-canopy t_max (°C)"); a2.set_ylabel("viability")
a2.set_title("Sensitivity to temperature offset"); a2.legend(fontsize=8.5, frameon=False)
fig.text(0.5, -0.03, "Shortlist (nutmeg/pepper/banana) is robust; only the level moves with the uncertain offset.",
         ha="center", fontsize=8.5, color=MUT)
save(fig, "fig3_suitability.png")

# 4. NPV by system
fin = R["finance"]
fig, ax = plt.subplots(figsize=(7.5, 3.4))
sys = [f["system"] for f in fin]; npv = [f["npv"] / 1000 for f in fin]
cols = [G if x > 0 else RED for x in npv]
bars = ax.bar(range(len(sys)), npv, color=cols)
ax.set_xticks(range(len(sys))); ax.set_xticklabels(sys, rotation=20, ha="right", fontsize=9)
ax.axhline(0, color="#888", lw=.8); ax.set_ylabel("NPV (₹ 000 / acre, 25 yr @ 8%)")
ax.set_title("System economics (NPV); IRR labelled")
for i, f in enumerate(fin):
    irr = f"{f['irr']*100:.0f}%" if f["irr"] is not None else "n/a"
    ax.text(i, npv[i] + (30 if npv[i] >= 0 else -60), irr, ha="center", fontsize=8.5, color=INK)
save(fig, "fig4_economics.png")

# 5. Monte Carlo distributions (3 key systems)
mc = {m["system"]: m for m in R["montecarlo"]}
fig, ax = plt.subplots(figsize=(7.5, 3.6))
for name, col in [("Coconut + Pepper", G), ("Coconut + Nutmeg", ACC), ("Coconut only", A)]:
    h = mc[name]["hist"]; e = np.array(h["edges"]); ctr = e[:-1] + (e[1] - e[0]) / 2
    ax.bar(ctr, h["counts"], width=(e[1] - e[0]) * 0.95, alpha=0.55, color=col,
           label=f"{name} (P(loss) {round(mc[name]['prob_loss']*100)}%)")
ax.axvline(0, color="k", lw=1, ls="--")
ax.set_xlabel("NPV (₹ 000 / acre)"); ax.set_ylabel("draws"); ax.set_xlim(-500, 1500)
ax.set_title("Monte Carlo NPV distributions (n=2000)"); ax.legend(fontsize=8.5, frameon=False)
save(fig, "fig5_montecarlo.png")

# 6. cashflow timeline contrast
fig, ax = plt.subplots(figsize=(7.5, 3.2))
for name, col in [("Coconut + Pepper", G), ("Teak block", A)]:
    cf = [f for f in fin if f["system"] == name][0]["cashflow"]
    ax.plot(range(1, len(cf) + 1), np.array(cf) / 1000, marker=".", color=col, label=name)
ax.axhline(0, color="#888", lw=.8); ax.set_xlabel("year"); ax.set_ylabel("net cash (₹ 000/acre)")
ax.set_title("Cash-flow timing: steady spice income vs one timber harvest")
ax.legend(fontsize=9, frameon=False)
save(fig, "fig6_cashflow.png")
print("done")
