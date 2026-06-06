"""Disease layer: leaf wetness, infection pressure, variety susceptibility."""
from agroforestry.disease import estimate_lwd, crop_disease_risk


def test_leaf_wetness_increases_with_humidity_and_rain():
    assert estimate_lwd(58, 0) <= estimate_lwd(88, 0)
    assert estimate_lwd(88, 0) <= estimate_lwd(88, 10)


def test_wet_window_raises_foliar_blight_risk():
    # Foliar (air-axis) blight rises in the humid window. Checked per-disease so the
    # soil-axis wilt (which does not depend on air timing) does not mask it.
    micro_dry = {"t_mean": 30, "t_max": 37, "rh": 58}
    micro_wet = {"t_mean": 26, "t_max": 31, "rh": 88}
    dry = crop_disease_risk("Pomegranate", micro_dry, variety="Bhagwa", rain_mm_day=0)
    wet = crop_disease_risk("Pomegranate", micro_wet, variety="Bhagwa", rain_mm_day=8)
    assert wet["per_disease"]["Bacterial blight"] > dry["per_disease"]["Bacterial blight"]


def test_drainage_mitigation_lowers_soil_disease():
    # Soil-axis: improving drainage lowers effective waterlogging -> lower wilt risk,
    # independent of the air microclimate.
    micro = {"t_mean": 26, "t_max": 31, "rh": 80}
    undrained = crop_disease_risk("Pomegranate", micro, variety="Bhagwa", waterlogging=0.8, drainage="none")
    drained = crop_disease_risk("Pomegranate", micro, variety="Bhagwa", waterlogging=0.8, drainage="raised_beds+drains")
    assert drained["per_disease"]["Wilt"] < undrained["per_disease"]["Wilt"]


def test_waterlogging_index_formula():
    from agroforestry.config import waterlogging_index
    # shallower water table and higher clay -> higher index; output bounded 0..1
    assert waterlogging_index(36, 1.0) > waterlogging_index(36, 5.0)
    assert waterlogging_index(50, 0.0) >= waterlogging_index(10, 5.0)
    assert 0.0 <= waterlogging_index(36, 1.0) <= 1.0


def test_less_susceptible_variety_has_lower_risk():
    # Per sourced ratings (ADR-003): Bhagwa is MS to blight, Ganesh is S, so
    # Bhagwa carries the lower realized risk in the wet window.
    micro_wet = {"t_mean": 26, "t_max": 31, "rh": 88}
    bhagwa = crop_disease_risk("Pomegranate", micro_wet, variety="Bhagwa", rain_mm_day=8)
    ganesh = crop_disease_risk("Pomegranate", micro_wet, variety="Ganesh", rain_mm_day=8)
    assert bhagwa["max"] <= ganesh["max"]
