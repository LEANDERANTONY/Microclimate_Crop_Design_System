"""Physics layer: Beer-Lambert light and shelterbelt wind."""
from agroforestry.physics import light_fraction, shade_pct, windbreak_reduction


def test_light_decreases_with_lai():
    assert light_fraction(0.0, 0.5) == 1.0
    assert light_fraction(2.0, 0.5) < light_fraction(0.5, 0.5)


def test_shade_within_bounds():
    for lai in (0.0, 1.0, 3.0):
        s = shade_pct(lai, 0.5)
        assert 0.0 <= s <= 100.0


def test_windbreak_peaks_near_optimal_porosity():
    # ~0.45 porosity should shelter more than a dense wall or an open barrier
    best = windbreak_reduction(10, 0.45)
    assert best > windbreak_reduction(10, 0.20)
    assert best > windbreak_reduction(10, 0.70)
