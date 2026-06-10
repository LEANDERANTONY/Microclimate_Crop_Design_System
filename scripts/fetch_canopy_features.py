"""Ground the design->feature mapping with REAL satellite features over Tamil Nadu
coconut and timber canopies.

Problem (ADR-007): predict.build_feature_row fabricates a design's NDVI / FAPAR /
canopy_height from LAI with crude proxies, while the offset models were trained on
*real* satellite features. So a coconut design is scored on made-up features and the
OOD flag fires partly on that artefact, not just genuine novelty.

Fix: sample real MODIS LAI/FPAR/NDVI + ETH canopy height over actual TN coconut-belt
and timber locations, take the regional median per canopy type, and write them to
reports/canopy_features_tn.json so build_feature_row can emit realistic per-species
values. MODERATE confidence (regional remote sensing, not the user's own plot).
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import ee

ee.Initialize(project="microclimate-crop-design-sys")

# Real Tamil Nadu locations (lon, lat). Coconut belt: Pollachi/Coimbatore + Cauvery
# delta (incl. the Anaikadu/Pattukkottai vicinity). Timber: TN tree-plantation /
# wooded sites in the Western Ghats foothills (teak/silver-oak range).
SITES = {
    "coconut": [
        (77.01, 10.66), (77.10, 10.60), (76.97, 10.70),   # Pollachi/Aliyar belt
        (77.56, 11.00),                                    # Kangeyam/Tiruppur
        (79.13, 10.78), (79.32, 10.42), (79.45, 10.86),    # Cauvery delta incl. Pattukkottai
    ],
    "timber": [
        (76.94, 10.46), (76.86, 10.40),                    # Anamalai foothills (tree plantation/forest)
        (77.25, 11.30), (78.20, 11.70),                    # Sathyamangalam / Kalrayan foothills
    ],
}

YEAR = "2020"
lai = ee.ImageCollection("MODIS/061/MCD15A3H").filterDate(f"{YEAR}-01-01", f"{YEAR}-12-31")
lai_img = lai.select("Lai").median().multiply(0.1)        # scale 0.1
fpar_img = lai.select("Fpar").median().multiply(0.01)     # scale 0.01
ndvi_img = (ee.ImageCollection("MODIS/061/MOD13Q1")
            .filterDate(f"{YEAR}-01-01", f"{YEAR}-12-31").select("NDVI").median().multiply(0.0001))
try:
    height_img = ee.Image("users/nlang/ETH_GlobalCanopyHeight_2020_10m_v1").rename("h")
    _ = height_img.bandNames().getInfo()
except Exception:
    height_img = None

stack = lai_img.rename("lai").addBands(fpar_img.rename("fapar")).addBands(ndvi_img.rename("ndvi"))
if height_img is not None:
    stack = stack.addBands(height_img.rename("canopy_height"))


def sample(points):
    fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point(p).buffer(150)) for p in points])
    vals = stack.reduceRegions(collection=fc, reducer=ee.Reducer.mean(), scale=250).getInfo()
    out = {}
    for k in ["lai", "fapar", "ndvi", "canopy_height"]:
        xs = [f["properties"].get(k) for f in vals["features"] if f["properties"].get(k) is not None]
        out[k] = round(sum(xs) / len(xs), 3) if xs else None
    out["n_points"] = len(points)
    return out


result = {ctype: sample(pts) for ctype, pts in SITES.items()}
result["_meta"] = {"year": YEAR, "lai_src": "MODIS MCD15A3H", "ndvi_src": "MODIS MOD13Q1",
                   "height_src": "ETH GlobalCanopyHeight 2020 10m" if height_img else "unavailable",
                   "confidence": "MODERATE (regional RS, not on-plot)"}
os.makedirs("reports", exist_ok=True)
with open("reports/canopy_features_tn.json", "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
print("-> reports/canopy_features_tn.json")
