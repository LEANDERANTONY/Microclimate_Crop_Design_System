"""Methods schematic (Fig. 0): the six-layer design->profit pipeline with confidence
labels and the inverse-design loop. -> figures/fig0_pipeline.png

Matches the README/figure palette. Pure matplotlib (no external deps)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

os.makedirs("figures", exist_ok=True)
INK, ACC, G, A, RED, MUT, LINE = "#23291f", "#4a6b3a", "#3f8f4f", "#b9852b", "#b3503f", "#6b7363", "#cfccc0"
GBG, ABG, RBG = "#e6f1e6", "#fbf1dc", "#f7e2dd"
plt.rcParams.update({"font.size": 10, "figure.facecolor": "white"})

# layer: (title, subtitle, method, confidence-color, confidence-label)
layers = [
    ("Farm design", "overstorey · spacing/LAI\nwindbreak · drainage · variety · timing", "controllable inputs", "#eceae0", "DESIGN"),
    ("1 · Microclimate", "shade, wind, under-canopy\nT, VPD, leaf-wetness", "Beer–Lambert + shelterbelt (physics);\nXGBoost quantile offsets + conformal; OOD flag", GBG, "physics HIGH · offset MOD"),
    ("2 · Disease risk", "foliar (air) + soil-water\ntwo axes", "mechanistic infection ×\nvariety susceptibility", ABG, "MODERATE"),
    ("3 · Viability", "growth × (1 − disease)", "fuzzy limiting-factor\n(Liebig minimum)", ABG, "MODERATE"),
    ("4 · Economics", "yield × suitability ×\n(1−disease) × price − cost", "banded, validated\n(NHB/TNAU/Agmarknet)", ABG, "MODERATE"),
    ("5 · Finance", "25-yr cash-flow\nNPV / IRR / payback", "gestation + harvest timing", ABG, "MODERATE"),
    ("6 · Uncertainty", "NPV distribution\nP(loss)", "Monte Carlo over\noffset+yield+price bands", GBG, "propagated"),
]

fig, ax = plt.subplots(figsize=(12.5, 4.6))
ax.set_xlim(0, len(layers) * 3.0); ax.set_ylim(0, 6); ax.axis("off")

box_w, box_h, y0 = 2.5, 2.6, 2.2
centers = []
for i, (title, sub, meth, col, conf) in enumerate(layers):
    x = i * 3.0 + 0.15
    cx = x + box_w / 2
    centers.append(cx)
    ax.add_patch(FancyBboxPatch((x, y0), box_w, box_h, boxstyle="round,pad=0.05,rounding_size=0.12",
                                fc=col, ec=LINE, lw=1.2))
    ax.text(cx, y0 + box_h - 0.32, title, ha="center", va="top", fontsize=10.5, fontweight="bold", color=INK)
    ax.text(cx, y0 + box_h - 0.95, sub, ha="center", va="top", fontsize=8.2, color=INK)
    ax.text(cx, y0 + 0.62, meth, ha="center", va="center", fontsize=7.4, color=MUT, style="italic")
    # confidence chip
    chipcol = G if ("HIGH" in conf or "propagated" in conf) else (A if "MOD" in conf else MUT)
    ax.text(cx, y0 - 0.28, conf, ha="center", va="center", fontsize=7.6, fontweight="bold", color=chipcol)
    # forward arrow
    if i < len(layers) - 1:
        ax.add_patch(FancyArrowPatch((x + box_w, y0 + box_h / 2), (x + box_w + 0.5, y0 + box_h / 2),
                                     arrowstyle="-|>", mutation_scale=14, color=INK, lw=1.6))

# inverse-design loop arrow (from layer 6 back to design), drawn beneath
x_start = centers[-1]; x_end = centers[0]
ax.add_patch(FancyArrowPatch((x_start, y0 - 0.55), (x_end, y0 - 0.55),
                             connectionstyle="arc3,rad=0.18", arrowstyle="-|>",
                             mutation_scale=16, color=ACC, lw=1.8, linestyle=(0, (5, 2))))
ax.text((x_start + x_end) / 2, y0 - 1.7, "Inverse design — search design to maximise risk-aware profit",
        ha="center", va="center", fontsize=9, color=ACC, fontweight="bold")

ax.text(centers[0], y0 + box_h + 0.55, "Macroclimate (ERA5) + controllable farm design",
        ha="left", va="bottom", fontsize=9, color=MUT)
ax.set_title("Six-layer agroforestry design → microclimate → disease → profit pipeline (confidence-labelled, uncertainty-propagated)",
             fontsize=11.5, fontweight="bold", color=INK, pad=12)

fig.savefig("figures/fig0_pipeline.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("wrote figures/fig0_pipeline.png")
