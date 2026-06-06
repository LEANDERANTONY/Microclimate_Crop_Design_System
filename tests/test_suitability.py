"""Suitability layer: limiting-factor growth score and two-axis viability."""
from agroforestry.suitability import score_crop, viability


def _micro(t_max=32, t_mean=27, shade=10, rh=60, wind=2.0):
    return {"t_max": t_max, "t_mean": t_mean, "shade": shade, "rh": rh, "wind": wind}


def test_score_in_range_and_names_limiting_factor():
    s = score_crop("Pomegranate", _micro())
    assert 0 <= s["score"] <= 100
    assert s["limiting"] in {"temperature", "shade/light", "humidity", "wind"}


def test_viability_never_exceeds_growth():
    v = viability("Pomegranate", _micro(rh=88, t_mean=26), variety="Bhagwa", rain_mm_day=8)
    assert v["viability"] <= v["growth"]


def test_dry_timing_beats_wet_timing_for_pomegranate():
    dry = viability("Pomegranate", _micro(rh=58, t_mean=30), variety="Bhagwa", rain_mm_day=0)
    wet = viability("Pomegranate", _micro(rh=88, t_mean=26), variety="Bhagwa", rain_mm_day=8)
    assert dry["viability"] > wet["viability"]
