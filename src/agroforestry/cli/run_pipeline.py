"""End-to-end runner: train -> validate (LOSO) -> predict -> score -> optimise.

Runs out-of-the-box on synthetic 'borrowed-label' data so you can see the whole
pipeline work today. Switch DATA_SOURCE to 'real' once data_load.py is wired to
SoilTemp / ForestTemp / GEE exports.
"""
import os, json
import numpy as np

from agroforestry.config import (TARGETS, GROUP_COL, ARTIFACT_DIR, CROPS,
                                 WATERLOGGING_WET, WATERLOGGING_DRY)
from agroforestry.features import engineer
from agroforestry.models import QuantileModel
from agroforestry.validation import loso
from agroforestry.predict import Predictor
from agroforestry.suitability import score_all, viability
from agroforestry.optimize import optimise

DATA_SOURCE = os.environ.get("DATA_SOURCE", "synthetic")   # "synthetic" | "real"
MAX_FOLDS = 25                # cap LOSO folds for speed; set None for all


def load_data():
    if DATA_SOURCE == "real":
        from agroforestry.data.load import load_real
        return load_real()
    from agroforestry.data.synth import make_dataset
    return make_dataset()


def main():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    print(f"\n=== Loading data ({DATA_SOURCE}) ===")
    df = load_data()
    print(f"{len(df)} rows across {df[GROUP_COL].nunique()} sites")

    X, feats = engineer(df)
    Xv = X[feats].values
    groups = df[GROUP_COL].values

    metrics = {}
    models = {}
    print("\n=== Leave-one-site-out validation (transferability test) ===")
    for tgt in TARGETS:
        y = df[tgt].values
        m = loso(Xv, y, groups, feats, max_folds=MAX_FOLDS)
        metrics[tgt] = m
        print(f"  {tgt:8s}  MAE {m['MAE']:.3f} (±{m['MAE_std']:.3f})  "
              f"RMSE {m['RMSE']:.3f}  interval cov {m['interval_coverage']:.2f} "
              f"(target {0.9-0.1:.2f})  width {m['interval_width']:.2f}")
        # fit final model on all data for downstream prediction (group-aware conformal)
        models[tgt] = QuantileModel().fit(Xv, y, feature_names=feats, groups=groups)

    # feature importance snapshot (median model of dT_max)
    print("\n=== Top features for dT_max ===")
    for name, imp in models["dT_max"].importances()[:8]:
        print(f"  {name:16s} {imp:.3f}")

    predictor = Predictor(models, feats)

    # ---- demo macro + site context (pull from ERA5/NASA POWER for real site) ----
    macro = dict(t_mean=28, t_max=34, t_min=22, rh=75, wind=3.0, solar=22, rainfall=2500)
    context = dict(elevation=50, slope=3, twi=7, soc=20, clay=35)

    print("\n=== Predict + score a sample design (coconut wide, LAI 1.4) ===")
    design = {"species": "coconut_wide", "lai": 1.4, "wb_height": 10, "wb_porosity": 0.45}
    micro = predictor.predict_micro(design, macro, context)
    print(f"  under-canopy: shade {micro['shade']:.0f}%  t_max {micro['t_max']:.1f}C  "
          f"rh {micro['rh']:.0f}%  wind {micro['wind']:.1f} m/s")
    print(f"  dT_max 80% interval: {micro['intervals']['dT_max'][0]:.2f} .. "
          f"{micro['intervals']['dT_max'][1]:.2f} C")
    for crop, s in score_all(micro).items():
        print(f"    {crop:13s} {s['score']:3d}/100  (limiting: {s['limiting']}, conf {s['confidence']})")

    print("\n=== Inverse design: best layout for each crop ===")
    opt_results = {}
    for crop in CROPS:
        best = optimise(predictor, crop, macro, context)
        d = best["design"]
        opt_results[crop] = best
        print(f"  {crop:13s} -> {best['score']:3d}/100 | "
              f"{d['species']}, LAI {d['lai']:.2f} ({best['micro']['shade']:.0f}% shade), "
              f"windbreak {d['wb_height']}m@{d['wb_porosity']} | "
              f"limiting {best['limiting']}")

    # ---- Disease layer demo: pomegranate two axes (air-timing x soil-drainage) ----
    print("\n=== Disease layer: pomegranate -- air-timing (bahar) x soil-drainage ===")
    sun_design = {"species": "none", "lai": 0.0, "wb_height": 0, "wb_porosity": 0.45}
    windows = {
        "Dry bahar (summer)":     dict(t_mean=30, t_max=37, t_min=23, rh=58, wind=3, solar=26, rainfall=2500),
        "Wet bahar (NE-monsoon)": dict(t_mean=26, t_max=31, t_min=22, rh=88, wind=2, solar=18, rainfall=2500),
    }
    rain_for = {"Dry bahar (summer)": 0.0, "Wet bahar (NE-monsoon)": 8.0}
    for wname, wmacro in windows.items():
        micro = predictor.predict_micro(sun_design, wmacro, context)
        wl = WATERLOGGING_DRY if "Dry" in wname else WATERLOGGING_WET   # seasonal soil baseline (ADR-005)
        for drn in ["none", "raised_beds+drains"]:
            v = viability("Pomegranate", micro, variety="Bhagwa",
                          rain_mm_day=rain_for[wname], waterlogging=wl, drainage=drn)
            print(f"  {wname:22s} drainage={drn:18s} -> growth {v['growth']:3d}  "
                  f"disease {v['disease_risk']:3d} ({v['worst_disease']}, wl_eff {v['waterlogging_eff']})"
                  f"  => VIABILITY {v['viability']:3d}/100")
    print("  (two axes, two levers: dry-season TIMING cuts foliar blight, but soil WILT persists on")
    print("   the delta's waterlogging-prone clay until DRAINAGE is added -- different diseases need")
    print("   different fixes. waterlogging default = delta clay (ADR-004); calibrate w/ CGWB+SoilGrids)")

    # persist metrics
    with open(os.path.join(ARTIFACT_DIR, "loso_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nMetrics written to {ARTIFACT_DIR}/loso_metrics.json")
    print("Done.")


if __name__ == "__main__":
    main()
