"""Central configuration: features, targets, crop envelopes, canopy params.

Edit FEATURES / TARGETS here and the rest of the pipeline follows.
"""

# ---- Targets the XGBoost models learn (offsets = under-canopy minus ambient) ----
TARGETS = ["dT_max", "dT_mean", "dVPD"]   # add "dRH" etc. as labels become available

# ---- Raw input features (what a loader must provide) ----
MACRO_FEATURES = ["t_mean", "t_max", "t_min", "rh", "wind", "solar", "rainfall"]
CANOPY_FEATURES = ["lai", "canopy_height", "ndvi", "fapar"]
TERRAIN_FEATURES = ["elevation", "slope", "twi"]
SOIL_FEATURES = ["soc", "clay"]
RAW_FEATURES = MACRO_FEATURES + CANOPY_FEATURES + TERRAIN_FEATURES + SOIL_FEATURES

GROUP_COL = "site_id"   # used for leave-one-site-out CV

# ---- Quantiles for prediction intervals ----
QUANTILES = [0.1, 0.5, 0.9]   # lower / median / upper

# ---- Beer-Lambert extinction coefficients per overstorey (physics layer) ----
SPECIES = {
    "none":          {"lai": 0.0, "k": 0.00, "drag": 0.00, "label": "Open field"},
    "coconut_wide":  {"lai": 1.0, "k": 0.50, "drag": 0.10, "label": "Coconut wide"},
    "coconut_close": {"lai": 1.7, "k": 0.50, "drag": 0.15, "label": "Coconut close"},
    "silver_oak":    {"lai": 1.3, "k": 0.55, "drag": 0.20, "label": "Silver oak"},
    "mahogany":      {"lai": 2.6, "k": 0.60, "drag": 0.25, "label": "Mahogany"},
    "teak_leaf":     {"lai": 2.0, "k": 0.60, "drag": 0.22, "label": "Teak (in leaf)"},
    "teak_bare":     {"lai": 0.3, "k": 0.60, "drag": 0.08, "label": "Teak (leafless)"},
}

# ---- Crop envelopes: [ideal_lo, ideal_hi, tol_lo, tol_hi]; wind = [ideal_max, tol_max] ----
CROPS = {
    "Vanilla":      {"t": [20, 30, 15, 33], "shade": [50, 60, 35, 78], "rh": [70, 90, 55, 100], "wind": [1.5, 3.0]},
    "Cocoa":        {"t": [21, 32, 18, 35], "shade": [25, 50, 10, 65], "rh": [70, 90, 55, 100], "wind": [1.5, 3.0]},
    "Black pepper": {"t": [23, 32, 18, 35], "shade": [20, 50, 5, 70],  "rh": [70, 90, 55, 100], "wind": [2.5, 4.5]},
    "Nutmeg":       {"t": [25, 35, 20, 38], "shade": [40, 50, 20, 72], "rh": [70, 90, 55, 100], "wind": [1.5, 3.0]},
    "Ginger":       {"t": [20, 30, 16, 35], "shade": [25, 50, 0, 70],  "rh": [70, 90, 55, 100], "wind": [4.0, 6.5]},
    # ---- fruits (full-sun unless noted); shade low = wants sun ----
    "Pomegranate":  {"t": [25, 35, 18, 40], "shade": [0, 20, 0, 45],  "rh": [40, 85, 30, 95], "wind": [4.0, 7.0]},
    "Guava":        {"t": [23, 30, 15, 38], "shade": [0, 25, 0, 50],  "rh": [50, 85, 35, 95], "wind": [4.0, 7.0]},
    "Mango":        {"t": [24, 30, 18, 38], "shade": [0, 20, 0, 45],  "rh": [45, 80, 30, 92], "wind": [3.0, 6.0]},
    "Grapes":       {"t": [20, 32, 12, 38], "shade": [0, 15, 0, 40],  "rh": [40, 70, 25, 88], "wind": [3.0, 6.0]},
    "Banana":       {"t": [25, 35, 16, 40], "shade": [0, 30, 0, 55],  "rh": [60, 90, 45, 98], "wind": [2.0, 4.0]},
    "Dragon fruit": {"t": [20, 33, 10, 38], "shade": [10, 40, 0, 60], "rh": [50, 85, 35, 95], "wind": [3.0, 6.0]},
}

# Per-variable confidence (mirrors the methodology: physics = high, borrowed ML = moderate/low)
CONFIDENCE = {"t": "MODERATE", "shade": "HIGH", "rh": "LOW", "wind": "HIGH"}

ARTIFACT_DIR = "reports"   # where models / plots / metrics are written

# ---------------------------------------------------------------------------
# Disease layer
# ---------------------------------------------------------------------------
# Each disease is a mechanistic infection model (no incidence data needed yet):
#   type "wetness"  -> driven by leaf wetness duration (LWD) + temperature
#   type "humidity" -> driven by RH + temperature (e.g. powdery mildew)
#   type "soil"     -> driven by waterlogging proxy (high RH/rain) + temperature
#   type "heat"     -> abiotic stress above a threshold (e.g. dragon-fruit sunburn)
# rain_driven: splash-dispersed pathogens need rain to spread (risk cut if dry).
DISEASES = {
    "Pomegranate": [
        {"name": "Bacterial blight", "type": "wetness", "t_min": 15, "t_opt": 29, "t_max": 34, "lwd_min": 4, "lwd_sat": 12, "rain_driven": True},
        {"name": "Wilt",             "type": "soil",    "t_min": 18, "t_opt": 28, "t_max": 38, "rh_min": 75, "rh_sat": 95, "rain_driven": False},
    ],
    "Grapes": [
        {"name": "Downy mildew",   "type": "wetness",  "t_min": 10, "t_opt": 23, "t_max": 30, "lwd_min": 4, "lwd_sat": 10, "rain_driven": True},
        {"name": "Powdery mildew", "type": "humidity", "t_min": 15, "t_opt": 25, "t_max": 33, "rh_min": 60, "rh_sat": 85, "rain_driven": False},
    ],
    "Mango": [
        {"name": "Anthracnose",    "type": "wetness",  "t_min": 15, "t_opt": 27, "t_max": 32, "lwd_min": 6, "lwd_sat": 14, "rain_driven": True},
        {"name": "Powdery mildew", "type": "humidity", "t_min": 10, "t_opt": 22, "t_max": 30, "rh_min": 60, "rh_sat": 80, "rain_driven": False},
    ],
    "Guava": [
        {"name": "Anthracnose", "type": "wetness", "t_min": 15, "t_opt": 27, "t_max": 33, "lwd_min": 6, "lwd_sat": 14, "rain_driven": True},
    ],
    "Banana": [
        {"name": "Sigatoka", "type": "wetness", "t_min": 16, "t_opt": 27, "t_max": 35, "lwd_min": 8, "lwd_sat": 16, "rain_driven": True},
    ],
    "Black pepper": [
        {"name": "Foot rot", "type": "wetness", "t_min": 18, "t_opt": 26, "t_max": 32, "lwd_min": 8, "lwd_sat": 16, "rain_driven": True},
    ],
    "Dragon fruit": [
        {"name": "Sunburn", "type": "heat", "t_threshold": 38},
        {"name": "Stem rot", "type": "wetness", "t_min": 20, "t_opt": 28, "t_max": 36, "lwd_min": 10, "lwd_sat": 18, "rain_driven": True},
    ],
}

# Ordinal resistance -> susceptibility multiplier (Resistant..Susceptible)
RESISTANCE_SCALE = {"R": 0.2, "MR": 0.5, "MS": 0.8, "S": 1.0}
DEFAULT_SUSCEPTIBILITY = 0.8   # used when a variety/disease pair is not catalogued

# variety -> {disease: ordinal rating}. Sparse on purpose; flag low confidence.
VARIETY_SUSCEPTIBILITY = {
    "Pomegranate": {
        "Bhagwa":  {"Bacterial blight": "S",  "Wilt": "MS"},
        "Ganesh":  {"Bacterial blight": "MS", "Wilt": "MS"},   # more wet-tolerant
        "Arakta":  {"Bacterial blight": "S",  "Wilt": "S"},
        "Mridula": {"Bacterial blight": "S",  "Wilt": "MS"},
    },
    "Grapes": {
        "Thompson Seedless": {"Downy mildew": "S", "Powdery mildew": "S"},
    },
    "Mango": {
        "Alphonso": {"Anthracnose": "S",  "Powdery mildew": "MS"},
        "Banganapalli": {"Anthracnose": "MS", "Powdery mildew": "MS"},
    },
    "Guava": {
        "Allahabad Safeda": {"Anthracnose": "MS"},
        "Lalit": {"Anthracnose": "MR"},
    },
}
