# Nomenclature guide for Word editing

Purpose: provide a separate `Nomenclature` section for the agroforestry manuscript, following the style of the published solar-air-heater paper where symbols and abbreviated terms are listed near the beginning of the paper. This file is only an editing guide; the Word manuscript is not changed.

Recommended placement in Word: after `Keywords` and before `1. Introduction`, or after the Introduction if the target journal prefers nomenclature after the first section.

## Mathematical Symbols

| Symbol | Meaning | Unit / notes |
|---|---|---|
| `X` | Generic microclimate variable | Used for `T_max`, `T_mean`, or `VPD` |
| `Delta X` | Microclimate offset from ambient | `X_sub-canopy - X_ambient` |
| `T` | Air temperature | `deg C` |
| `T_max` | Mean daily maximum air temperature | `deg C` |
| `T_mean` | Mean daily air temperature | `deg C` |
| `T_min` | Mean daily minimum air temperature | `deg C` |
| `T_sub,max` | Under-canopy maximum air temperature | `deg C` |
| `T_ambient,max` | Ambient/free-air maximum temperature | `deg C` |
| `dT_max` | Maximum-temperature offset | `T_sub,max - T_ambient,max`, `deg C` |
| `dT_mean` | Mean-temperature offset | `T_sub,mean - T_ambient,mean`, `deg C` |
| `VPD` | Vapour-pressure deficit | `kPa` |
| `dVPD` | Vapour-pressure-deficit offset | `VPD_sub-canopy - VPD_ambient`, `kPa` |
| `RH` | Relative humidity | `%` |
| `I` | Under-canopy light / radiation reaching the crop layer | Usually expressed as a fraction of `I0` |
| `I0` | Open-field or top-of-canopy light | Same unit as `I` |
| `k` | Beer-Lambert extinction coefficient | Dimensionless |
| `LAI` | Leaf area index | `m2 leaf area / m2 ground area`, dimensionless |
| `p` | Number of model features | Used in the OOD-score definition |
| `x` | Feature vector for a site or design | Model input |
| `x_j` | Feature `j` in the input vector | Model input component |
| `y_i` | Observed target value for sample `i` | Offset target |
| `yhat_i` | Predicted target value for sample `i` | Offset prediction |
| `q_lo(x)` | Lower quantile prediction at feature vector `x` | Used for conformal interval |
| `q_hi(x)` | Upper quantile prediction at feature vector `x` | Used for conformal interval |
| `s_i` | Conformal nonconformity score | `max(q_lo(x_i) - y_i, y_i - q_hi(x_i))` |
| `qhat_alpha` | Conformal calibration offset | Quantile of calibration scores |
| `PI(x)` | Prediction interval at feature vector `x` | `[q_lo(x)-qhat_alpha, q_hi(x)+qhat_alpha]` |
| `n` | Number of observations in a validation set | Used in `MAE` |
| `k` | Number of local/few-shot calibration points | Context-dependent; distinct from Beer-Lambert `k` |
| `M` | Number of Monte Carlo draws | Used in uncertainty propagation |
| `m` | Monte Carlo draw index | `m = 1, ..., M` |
| `C_t` | Cash flow in year `t` | `Rs acre^-1 yr^-1` |
| `t` | Year index in discounted cash flow | `t = 0, ..., T` |
| `T` | Analysis horizon in finance equations | `T = 25 yr`; avoid confusing with temperature `T` in prose |
| `r` | Real discount rate | Fraction per year; `0.08` in the Anaikadu analysis |
| `IRR` | Internal rate of return | Fraction or `%` |
| `NPV` | Net present value | `Rs acre^-1` |
| `P(loss)` | Probability of financial loss | `P(NPV < 0)` |
| `P10(NPV)` | 10th percentile of NPV | Downside-risk metric |
| `E[NPV]` | Expected net present value | Mean of Monte Carlo NPV distribution |

## Model Terms And Metrics

| Term | Meaning | Notes |
|---|---|---|
| `offset` | Difference between sub-canopy and ambient/free-air microclimate | Core supervised-learning target |
| `sub-canopy` | Crop-layer or understorey measurement under canopy | Opposed to ambient/free-air |
| `ambient` | Free-air macroclimate reference | ERA5 atmospheric reference in the pipeline |
| `growth_fit` | Fuzzy suitability score against crop envelope | `0-1` or scaled to `0-100` depending on context |
| `disease_risk` | Realized disease pressure after variety susceptibility | `0-1` |
| `environmental_pressure` | Disease pressure from microclimate and soil-water conditions | Before variety susceptibility |
| `variety_susceptibility` | Variety-level disease susceptibility multiplier | From R/MR/MS/S ordinal ratings |
| `effective_waterlogging` | Soil-water stress used for soil-borne disease axis | `site_waterlogging x drainage_mitigation` |
| `attainable_yield` | Reference yield adjusted by growth and disease | Crop-specific |
| `crop_margin` | Crop income minus cost | Before full discounted cash-flow treatment |
| `MAE` | Mean absolute error | Main offset validation error |
| `baseline_MAE` | MAE from training-mean offset baseline | Used to compute skill |
| `skill` | Improvement over baseline | `1 - MAE_model / MAE_baseline` |
| `coverage` | Fraction of observations inside prediction interval | Target near `0.80` in manuscript |
| `OOD score` | Fraction of query features outside training range | Higher score means stronger extrapolation |
| `few-shot calibration` | Recalibration with a small number of target-regime observations | Used in Section 6.1 |
| `Mondrian conformal` | Group-conditional conformal calibration | In this paper, climate/regime is the group |
| `Monte Carlo` | Repeated sampling of uncertain inputs through the full pipeline | Produces NPV distribution and `P(loss)` |

## Abbreviations

| Abbreviation | Expansion | Notes |
|---|---|---|
| `ADR` | Architectural Decision Record | Project decision log |
| `CQR` | Conformalized Quantile Regression | Used for calibrated prediction intervals |
| `DEM` | Digital Elevation Model | Copernicus DEM in the pipeline |
| `DSS` | Decision Support System | General literature term |
| `ECOCROP` | FAO crop environmental requirements database | Crop envelope source |
| `ERA5` | ECMWF Reanalysis v5 | Ambient climate source |
| `FAO` | Food and Agriculture Organization of the United Nations | ECOCROP source |
| `FAPAR` | Fraction of Absorbed Photosynthetically Active Radiation | MODIS canopy/radiation feature |
| `GIS` | Geographic Information System | Used in related-work context |
| `GIS-MCDA` | GIS-based Multi-Criteria Decision Analysis | Crop suitability literature |
| `IRR` | Internal Rate of Return | Finance metric |
| `LAI` | Leaf Area Index | Canopy structure feature |
| `LOCO` | Leave-One-Climate-Out | Cross-regime validation protocol |
| `LOSO` | Leave-One-Site-Out | Site-transfer validation protocol |
| `LWD` | Leaf-Wetness Duration | Disease-risk driver |
| `MAE` | Mean Absolute Error | Validation metric |
| `ML` | Machine Learning | General modelling term |
| `MODIS` | Moderate Resolution Imaging Spectroradiometer | LAI/FAPAR/NDVI source |
| `NDVI` | Normalized Difference Vegetation Index | Canopy greenness feature |
| `NHB` | National Horticulture Board | Economics/cost source |
| `NPV` | Net Present Value | Finance metric |
| `OOD` | Out-of-Distribution | Extrapolation flag |
| `PAR` | Photosynthetically Active Radiation | Related to crop-layer light |
| `PI` | Prediction Interval | Conformal interval |
| `PROSEA` | Plant Resources of South-East Asia | Nutmeg envelope source |
| `RH` | Relative Humidity | Microclimate variable |
| `SAFE` | Stability of Altered Forest Ecosystems Project | Borneo data source |
| `SBIO` | Soil bioclimatic variables | SoilTemp-derived Earth Engine reference |
| `SoilGrids` | ISRIC global gridded soil database | Clay and organic-carbon source |
| `TNAU` | Tamil Nadu Agricultural University | Agronomic/economic source |
| `VPD` | Vapour-Pressure Deficit | Microclimate stress variable |
| `XGBoost` | Extreme Gradient Boosting | Quantile offset model |

## Crop And Site Terms

| Term | Meaning | Notes |
|---|---|---|
| `Anaikadu` | Application site near Pattukkottai, Thanjavur, Tamil Nadu | Real farm site used in the case study |
| `Bahar` | Fruiting-season management window | Important for disease timing |
| `Coconut wide` | Wide-spaced coconut overstorey design | Main practical system in the case study |
| `Coconut close` | Denser coconut overstorey design | Alternative design scenario |
| `Overstorey` | Main tree canopy layer | Coconut, timber, etc. |
| `Intercrop` | Crop grown under or between overstorey trees | Pepper, nutmeg, banana, etc. |
| `Windbreak` | Perimeter or boundary planting used to reduce wind | Design lever |
| `Drainage mitigation` | Management reducing soil-water disease pressure | Ridges, raised beds, drains, etc. |

## Suggested Nomenclature Section Text

Use this as the starting point in Word:

```text
Nomenclature

Symbols
Delta X      microclimate offset, X_sub-canopy - X_ambient
T_max        mean daily maximum air temperature (deg C)
T_mean       mean daily air temperature (deg C)
VPD          vapour-pressure deficit (kPa)
I, I0        under-canopy and open-field light
k            Beer-Lambert extinction coefficient
LAI          leaf area index
NPV          net present value (Rs acre^-1)
C_t          cash flow in year t
r            real discount rate
P(loss)      probability that NPV is less than zero

Abbreviations
CQR          conformalized quantile regression
ERA5         ECMWF Reanalysis v5
FAPAR        fraction of absorbed photosynthetically active radiation
IRR          internal rate of return
LOCO         leave-one-climate-out
LOSO         leave-one-site-out
LWD          leaf-wetness duration
MAE          mean absolute error
NDVI         normalized difference vegetation index
OOD          out-of-distribution
RH           relative humidity
VPD          vapour-pressure deficit
```

## Notes Before Adding To Word

- The symbol `k` is used both for Beer-Lambert extinction and for number of few-shot calibration points. In the manuscript body, use `k_ext` or describe the few-shot count as `n_cal` if you want to avoid ambiguity.
- The symbol `T` is used for both temperature and the finance time horizon in standard notation. In prose, define the finance horizon as `H = 25 yr` if you want to keep `T` exclusively for temperature.
- If the journal has a strict nomenclature format, keep only the `Symbols` and `Abbreviations` tables and move crop/site terms to a glossary or delete them.
