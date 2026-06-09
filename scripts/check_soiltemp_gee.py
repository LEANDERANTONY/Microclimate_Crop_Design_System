"""Check whether the SoilTemp global near-surface/soil-temperature maps (Lembrechts
et al. 2022, 'Global maps of soil temperature') are accessible on Earth Engine and
return real values at Anaikadu -- i.e. usable as region-representative labels."""
import ee
ee.Initialize(project="microclimate-crop-design-sys")
PT = ee.Geometry.Point([79.3545, 10.4019])  # Anaikadu (GD Home Stay)

for asset in ["projects/crowtherlab/soil_bioclim/SBIO_v2_0_5cm",
              "projects/crowtherlab/soil_bioclim/SBIO_v2_5_15cm"]:
    try:
        img = ee.Image(asset)
        bands = img.bandNames().getInfo()
        print(f"\nOK  {asset}")
        print("   bands:", bands)
        vals = img.reduceRegion(ee.Reducer.mean(), PT, 1000).getInfo()
        print("   @Anaikadu:", {k: (round(v, 2) if isinstance(v, (int, float)) else v)
                                 for k, v in vals.items()})
    except Exception as e:
        print(f"\nFAIL {asset}: {repr(e)[:200]}")
