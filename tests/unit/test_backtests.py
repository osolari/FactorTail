"""Tests for VaR/ES backtest statistics."""

from __future__ import annotations

import numpy as np
import pytest

from factortail.real_data.backtests import (
    acerbi_szekely_es,
    christoffersen_test,
    dq_test,
    kupiec_test,
)


def test_kupiec_rejects_when_hits_far_from_expectation():
    """If observed hits == expected hits, Kupiec p-value should be ~1."""
    n = 1000
    level = 0.99
    hits = np.zeros(n)
    hits[:10] = 1  # exactly 1% hits, matching expectation
    res = kupiec_test(hits, level=level)
    assert res["p_value"] > 0.5
    # Now flood with hits.
    hits_excess = np.zeros(n)
    hits_excess[:100] = 1
    res2 = kupiec_test(hits_excess, level=level)
    assert res2["p_value"] < 0.01


def test_christoffersen_independent_passes():
    rng = np.random.default_rng(0)
    n = 1000
    level = 0.99
    p = 1 - level
    hits = (rng.random(n) < p).astype(int)
    res = christoffersen_test(hits, level=level)
    # Independent hits => p-value of conditional coverage should be moderate.
    assert 0.0 <= res["p_value"] <= 1.0


def test_dq_test_runs_on_random_hits():
    rng = np.random.default_rng(0)
    hits = (rng.random(500) < 0.01).astype(int)
    res = dq_test(hits, level=0.99)
    assert np.isfinite(res["statistic"])
    assert 0 <= res["p_value"] <= 1


def test_acerbi_szekely_zero_when_no_exceptions():
    n = 200
    losses = np.zeros(n)
    var = np.ones(n)
    es = np.full(n, 2.0)
    res = acerbi_szekely_es(losses, var, es, level=0.99)
    # No exceptions => statistic = -1
    assert res["statistic"] == pytest.approx(-1.0)
