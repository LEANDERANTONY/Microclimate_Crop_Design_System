"""Disease layer: leaf wetness, infection pressure, variety susceptibility."""
from agroforestry.disease import estimate_lwd, crop_disease_risk


def test_leaf_wetness_increases_with_humidity_and_rain():
    assert estimate_lwd(58, 0) <= estimate_lwd(88, 0)
    assert estimate_lwd(88, 0) <= estimate_lwd(88, 10)


def test_wet_window_raises_blight_risk():
    micro_dry = {"t_mean": 30, "t_max": 37, "rh": 58}
    micro_wet = {"t_mean": 26, "t_max": 31, "rh": 88}
    dry = crop_disease_risk("Pomegranate", micro_dry, variety="Bhagwa", rain_mm_day=0)
    wet = crop_disease_risk("Pomegranate", micro_wet, variety="Bhagwa", rain_mm_day=8)
    assert wet["max"] > dry["max"]


def test_resistant_variety_has_lower_risk():
    micro_wet = {"t_mean": 26, "t_max": 31, "rh": 88}
    bhagwa = crop_disease_risk("Pomegranate", micro_wet, variety="Bhagwa", rain_mm_day=8)
    ganesh = crop_disease_risk("Pomegranate", micro_wet, variety="Ganesh", rain_mm_day=8)
    assert ganesh["max"] <= bhagwa["max"]
