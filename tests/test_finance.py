"""Tests for the financial model (NPV / IRR / payback)."""
import numpy as np
from agroforestry.finance import npv, irr, payback, system_finance, crop_cashflow


def test_npv_zero_rate_is_sum():
    cf = np.array([100.0, 100.0, 100.0])
    assert abs(npv(cf, 0.0) - 300.0) < 1e-6


def test_npv_discounts_future():
    cf = np.array([100.0])
    assert abs(npv(cf, 0.10) - 100.0 / 1.1) < 1e-6


def test_irr_root_is_consistent():
    cf = np.array([-100.0, 60.0, 60.0])   # outflow yr1, inflow yr2-3
    r = irr(cf)
    assert r is not None
    assert abs(npv(cf, r)) < 1.0           # NPV at IRR is ~0


def test_irr_none_when_never_profitable():
    assert irr(np.array([-100.0, -10.0, -10.0])) is None


def test_payback_year():
    assert payback(np.array([-100.0, 60.0, 60.0])) == 3   # cumulative >=0 at year 3
    assert payback(np.array([-100.0, -10.0])) is None


def test_gestation_delays_income():
    # nutmeg has a long gestation -> no revenue in early years (only costs -> negative cf)
    cf = crop_cashflow("Nutmeg", growth=80, disease=0)
    assert cf[0] < 0 and cf[1] < 0          # years 1-2: establishment/maintenance, no yield
    assert cf[20] > cf[1]                    # mature years are better than gestation years


def test_system_finance_keys():
    f = system_finance("coconut_wide", "Nutmeg", growth=50, disease=10)
    for k in ("npv", "irr", "payback_yr", "cashflow"):
        assert k in f
    assert len(f["cashflow"]) == f["horizon"]
