"""Region reference: sample the SoilTemp global near-surface temperature maps
(Lembrechts et al. 2022, on GEE) at Anaikadu vs our two training regions, to
quantify how far the target site sits from the Borneo+Spain training climate.

SBIO is near-surface SOIL temperature (not canopy air), so it is used here as a
REGIONAL REFERENCE / cross-check -- not as air-offset training labels (ADR-009).
"""
import ee
ee.Initialize(project="microclimate-crop-design-sys")

SITES = {
    "Anaikadu (target, TN)":   [79.3545, 10.4019],
    "SAFE Borneo (train)":     [117.60, 4.75],
    "La Jarda Spain (train)":  [-5.58, 36.53],
}
sbio = ee.Image("projects/crowtherlab/soil_bioclim/SBIO_v2_0_5cm")
keep = {
    "SBIO1_Annual_Mean_Temperature": "annual_mean",
    "SBIO5_Max_Temperature_of_Warmest_Month": "warm_month_max",
    "SBIO6_Min_Temperature_of_Coldest_Month": "cold_month_min",
    "SBIO10_Mean_Temperature_of_Warmest_Quarter": "warm_qtr_mean",
    "SBIO11_Mean_Temperature_of_Coldest_Quarter": "cold_qtr_mean",
}
print("Near-surface (0-5 cm) soil temperature climatology, SoilTemp/SBIO (degC):\n")
hdr = f"{'site':24s}" + "".join(f"{v:>16s}" for v in keep.values())
print(hdr)
for name, lonlat in SITES.items():
    vals = sbio.reduceRegion(ee.Reducer.mean(), ee.Geometry.Point(lonlat), 1000).getInfo()
    row = f"{name:24s}" + "".join(f"{vals.get(k, float('nan')):16.1f}" for k in keep)
    print(row)
print("\nThe wider the gap vs the two training rows, the more the offset model is")
print("extrapolating for Anaikadu -- this is the regional-transfer gap ADR-008 found.")
