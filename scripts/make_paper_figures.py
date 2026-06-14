"""Generate the new manuscript figures (journal DPI) that enrich the evidence chain:
  fig_sitemap      study site + training regimes (geographic + climate bars)
  fig_featurespace training feature-space coverage + Anaikadu OOD
  fig_loco         leave-one-climate-out skill & coverage heatmaps
  fig_fewshot      few-shot conformal coverage recovery vs k
  fig_envelope     crop temperature envelopes vs the Anaikadu under-coconut sweep
Reads committed data/metrics; writes figures/*.png at 300 dpi.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from agroforestry.validation import climate_zone
from agroforestry.config import CROPS, GROUP_COL, TARGETS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)
INK, ACC, G, A, RED, MUT, BLUE = "#23291f", "#4a6b3a", "#3f8f4f", "#b9852b", "#b3503f", "#6b7363", "#3a6b8f"
plt.rcParams.update({"font.size": 10, "figure.facecolor": "white", "axes.facecolor": "white",
                     "axes.edgecolor": "#cfccc0", "savefig.dpi": 300})

df = pd.read_parquet(os.path.join(ROOT, "data/processed/labelled_offsets.parquet"))
zones = climate_zone(df[GROUP_COL].astype(str).values)
df = df.assign(zone=zones)
R = json.load(open(os.path.join(ROOT, "reports/results.json"), encoding="utf-8"))
LOCO = json.load(open(os.path.join(ROOT, "reports/loco_metrics.json"), encoding="utf-8"))
MOND = json.load(open(os.path.join(ROOT, "reports/mondrian_metrics.json"), encoding="utf-8"))
macro = R["site"]["macro"]
ZLAB = {"borneo_forest": "Borneo forest", "med_spain": "Med. Spain", "oilpalm_open": "Borneo oil-palm"}
ZCOL = {"borneo_forest": G, "med_spain": BLUE, "oilpalm_open": A}


def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(FIG, name), bbox_inches="tight"); plt.close(fig)
    print("wrote figures/" + name)


# ---- Fig: study site + training regimes -----------------------------------
def fig_sitemap():
    pts = {"Borneo forest (SAFE)": (117.5, 4.7, G), "Borneo oil-palm (SAFE)": (117.6, 4.5, A),
           "Mediterranean Spain (La Jarda)": (-5.6, 36.5, BLUE), "Anaikadu, Tamil Nadu (target)": (79.35, 10.40, RED)}
    fig, (axm, axb) = plt.subplots(1, 2, figsize=(11, 4.0), gridspec_kw={"width_ratios": [1.7, 1]})
    # crude geographic scatter (equirectangular); honest schematic, no basemap dependency
    axm.set_xlim(-30, 140); axm.set_ylim(-15, 55)
    axm.axhline(0, color="#e3e0d6", lw=0.8); axm.set_xticks(range(-30, 141, 30)); axm.set_yticks(range(-15, 56, 15))
    axm.set_xlabel("longitude (°E)"); axm.set_ylabel("latitude (°N)"); axm.grid(alpha=0.25)
    for lab, (lon, lat, c) in pts.items():
        mk = "*" if "target" in lab else "o"
        axm.scatter([lon], [lat], s=190 if mk == "*" else 90, c=c, marker=mk, edgecolor="white", zorder=3)
        axm.annotate(lab, (lon, lat), textcoords="offset points", xytext=(8, 6), fontsize=8, color=INK)
    axm.set_title("Training regimes vs target site (schematic)", fontweight="bold", fontsize=10.5)
    # climate bars per regime + Anaikadu
    regs = ["borneo_forest", "med_spain", "oilpalm_open"]
    tmean = [df[df.zone == z]["t_mean"].mean() for z in regs] + [macro["t_mean"]]
    tmin = [df[df.zone == z]["t_min"].mean() for z in regs] + [macro["t_min"]]
    labs = [ZLAB[z] for z in regs] + ["Anaikadu"]
    x = np.arange(len(labs)); w = 0.38
    axb.bar(x - w/2, tmean, w, label="mean T", color=ACC)
    axb.bar(x + w/2, tmin, w, label="min T (nights)", color=A)
    axb.set_xticks(x); axb.set_xticklabels(labs, rotation=25, ha="right", fontsize=8)
    axb.set_ylabel("°C"); axb.legend(fontsize=8, frameon=False)
    axb.set_title("Thermal regime: warm-night gap", fontweight="bold", fontsize=10.5)
    axb.axhline(macro["t_min"], color=RED, ls="--", lw=0.9, alpha=0.7)
    save(fig, "fig_sitemap.png")


# ---- Fig: feature-space coverage + OOD ------------------------------------
def fig_featurespace():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.2))
    for z in ["borneo_forest", "med_spain", "oilpalm_open"]:
        s = df[df.zone == z]
        a1.scatter(s["t_mean"], s["t_min"], s=10, alpha=0.35, color=ZCOL[z], label=ZLAB[z], edgecolor="none")
        a2.scatter(s["lai"], s["canopy_height"], s=10, alpha=0.35, color=ZCOL[z], edgecolor="none")
    # Anaikadu macroclimate + coconut design
    a1.scatter([macro["t_mean"]], [macro["t_min"]], s=220, marker="*", c=RED, edgecolor="white",
               zorder=4, label="Anaikadu (target)")
    a1.set_xlabel("mean temperature (°C)"); a1.set_ylabel("min temperature (°C)")
    a1.set_title("Macroclimate space", fontweight="bold", fontsize=10.5); a1.legend(fontsize=7.5, frameon=False)
    a1.annotate("warm nights:\noutside training", (macro["t_mean"], macro["t_min"]),
                textcoords="offset points", xytext=(-4, -34), fontsize=8, color=RED, ha="center")
    # coconut design point (grounded features): LAI~0.8-1.0, height~7.6 (regional RS)
    cf = json.load(open(os.path.join(ROOT, "reports/canopy_features_tn.json"), encoding="utf-8"))
    a2.scatter([1.0], [cf["coconut"]["canopy_height"]], s=220, marker="*", c=RED, edgecolor="white",
               zorder=4, label="coconut (target)")
    a2.set_xlabel("leaf area index"); a2.set_ylabel("canopy height (m)")
    a2.set_title("Canopy-structure space", fontweight="bold", fontsize=10.5); a2.legend(fontsize=7.5, frameon=False)
    save(fig, "fig_featurespace.png")


# ---- Fig: LOCO heatmaps (skill, coverage) ---------------------------------
def fig_loco():
    targets = ["dT_max", "dT_mean", "dVPD"]; regs = ["borneo_forest", "med_spain", "oilpalm_open"]
    skill = np.array([[LOCO[t]["pure_xgb"]["per_zone"][z]["skill_vs_baseline"] for t in targets] for z in regs])
    cov = np.array([[LOCO[t]["pure_xgb"]["per_zone"][z]["interval_coverage"] for t in targets] for z in regs])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 3.8))
    rdg = LinearSegmentedColormap.from_list("rdg", [RED, "#f2efe6", G])
    for ax, M, title, vmin, vmax, cmap, fmt in [
        (a1, skill * 100, "Skill vs baseline (%)", -120, 60, rdg, "{:.0f}"),
        (a2, cov, "Interval coverage (target 0.80)", 0.0, 1.0, rdg, "{:.2f}")]:
        im = ax.imshow(M, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
        ax.set_xticks(range(len(targets))); ax.set_xticklabels(targets, fontsize=9)
        ax.set_yticks(range(len(regs))); ax.set_yticklabels([ZLAB[z] for z in regs], fontsize=9)
        ax.set_title(title, fontweight="bold", fontsize=10.5)
        for i in range(len(regs)):
            for j in range(len(targets)):
                ax.text(j, i, fmt.format(M[i, j]), ha="center", va="center", fontsize=9, color=INK)
        if title.startswith("Interval"):
            ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("Leave-one-climate-out: transfer degrades, coverage collapses out-of-climate",
                 fontsize=10.5, fontweight="bold", y=1.02)
    save(fig, "fig_loco.png")


# ---- Fig: few-shot conformal recovery -------------------------------------
def fig_fewshot():
    res = MOND["results"]["dT_mean"]; ks = MOND["ks"]; tgt = MOND["target_coverage"]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for z, c in ZCOL.items():
        if z in res:
            ys = [res[z]["by_k"][str(k)]["coverage"] for k in ks]
            ax.plot(ks, ys, "-o", color=c, label=ZLAB[z], lw=1.8, ms=5)
    ax.axhline(tgt, color=INK, ls="--", lw=1.0, label=f"target {tgt:.2f}")
    ax.set_xlabel("in-regime calibration points  k"); ax.set_ylabel("interval coverage (dT_mean)")
    ax.set_title("Few-shot conformal recalibration restores coverage", fontweight="bold", fontsize=10.5)
    ax.set_ylim(0, 1); ax.legend(fontsize=8.5, frameon=False); ax.grid(alpha=0.25)
    save(fig, "fig_fewshot.png")


# ---- Fig: crop temperature envelopes vs Anaikadu sweep --------------------
def fig_envelope():
    crops = ["Black pepper", "Nutmeg", "Banana", "Cocoa", "Vanilla"]
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    for i, cr in enumerate(crops):
        lo, hi, tlo, thi = CROPS[cr]["t"]
        ax.plot([tlo, thi], [i, i], color=MUT, lw=3, alpha=0.5, solid_capstyle="round")
        ax.plot([lo, hi], [i, i], color=ACC, lw=9, alpha=0.9, solid_capstyle="round")
    # Anaikadu under-coconut T_max sweep band (from results sensitivity)
    tmaxes = [s["t_max"] for s in R["sensitivity"]]
    lo_s, hi_s = min(tmaxes), max(tmaxes); central = [s for s in R["sensitivity"] if s["delta"] == 0][0]["t_max"]
    ax.axvspan(lo_s, hi_s, color=RED, alpha=0.12)
    ax.axvline(central, color=RED, ls="--", lw=1.3)
    ax.annotate("under-coconut T_max\nuncertainty sweep", (hi_s, len(crops) - 0.4),
                fontsize=8, color=RED, ha="right")
    ax.set_yticks(range(len(crops))); ax.set_yticklabels(crops)
    ax.set_xlabel("temperature (°C)"); ax.set_xlim(8, 44)
    ax.set_title("Crop thermal envelopes vs the predicted Anaikadu microclimate",
                 fontweight="bold", fontsize=10.5)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([0], [0], color=ACC, lw=9, label="optimal range"),
                       Line2D([0], [0], color=MUT, lw=3, label="tolerated range"),
                       Line2D([0], [0], color=RED, ls="--", label="central T_max")],
              fontsize=8, frameon=False, loc="lower right")
    save(fig, "fig_envelope.png")


# ---- Fig: model-family benchmark under climate shift ----------------------
def fig_benchmark():
    B = json.load(open(os.path.join(ROOT, "reports/benchmark_metrics.json"), encoding="utf-8"))
    models = ["ridge", "rf", "gp", "moe", "xgb", "hybrid"]
    lab = {"ridge": "Ridge", "rf": "Random\nforest", "gp": "Gaussian\nprocess",
           "moe": "Mixture-of-\nexperts", "xgb": "XGBoost\n(ours)", "hybrid": "Physics\nhybrid"}
    tg = TARGETS
    loco_skill = [np.mean([B["loco"][t][m]["skill"] for t in tg]) for m in models]
    indist_skill = [np.mean([B["in_distribution"][t][m]["skill"] for t in tg]) for m in models]
    loco_cov = [np.mean([B["loco"][t][m]["coverage"] for t in tg]) for m in models]
    x = np.arange(len(models))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
    w = 0.4
    a1.bar(x - w/2, indist_skill, w, label="in-distribution", color=G)
    a1.bar(x + w/2, loco_skill, w, label="cross-climate (LOCO)",
           color=[RED if v < 0 else ACC for v in loco_skill])
    a1.axhline(0, color=INK, lw=0.8); a1.set_ylim(-1.2, 0.8)
    a1.set_xticks(x); a1.set_xticklabels([lab[m] for m in models], fontsize=8)
    a1.set_ylabel("skill vs baseline"); a1.legend(fontsize=8, frameon=False)
    a1.set_title("All families learn in-distribution; only GP keeps\npositive skill across climates",
                 fontweight="bold", fontsize=10)
    a1.annotate("Ridge −3.2 (off-scale)", (0, -1.15), fontsize=7, color=RED, ha="center")
    a2.bar(x, loco_cov, color=[G if abs(v-0.8) < 0.18 else A for v in loco_cov])
    a2.axhline(0.8, color=INK, ls="--", lw=1.0, label="target 0.80")
    a2.set_xticks(x); a2.set_xticklabels([lab[m] for m in models], fontsize=8)
    a2.set_ylabel("out-of-climate interval coverage"); a2.set_ylim(0, 1)
    a2.legend(fontsize=8, frameon=False)
    a2.set_title("Distance-aware uncertainty (GP) stays\nbest-calibrated out-of-climate",
                 fontweight="bold", fontsize=10)
    save(fig, "fig_benchmark.png")


if __name__ == "__main__":
    fig_sitemap(); fig_featurespace(); fig_loco(); fig_fewshot(); fig_envelope(); fig_benchmark()
    print("done")
