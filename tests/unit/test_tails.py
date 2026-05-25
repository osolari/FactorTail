"""Method-correctness tests for tail distributions.

Each test checks an exact closed-form identity:

* :class:`ParetoTail` ``sf(x) = (x/scale)^{-alpha}`` and ``ppf`` is its inverse.
* :class:`LomaxTail` ``sf(x) = (1 + x/scale)^{-alpha}``; quantile inverts;
  ``E[X] = scale/(alpha-1)`` for ``alpha > 1`` is matched empirically.
* :class:`BurrTail` parameters satisfy ``alpha = k * d`` and ``c = scale^alpha``.
* :class:`StudentTTail` ``sf`` matches ``scipy.stats.t.sf``.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy import stats

from factortail.utils.tails import (
    BurrTail,
    LomaxTail,
    ParetoTail,
    StudentTTail,
    build_marginal,
)


class TestParetoTail:
    def test_sf_closed_form(self):
        d = ParetoTail(alpha=2.3, scale=1.4)
        x = np.array([1.5, 2.0, 3.0, 10.0])
        expected = (x / 1.4) ** (-2.3)
        assert np.allclose(d.sf(x), expected, rtol=1e-12)

    def test_sf_below_scale_is_one(self):
        d = ParetoTail(alpha=2.0, scale=2.0)
        assert d.sf(1.0) == pytest.approx(1.0)

    def test_ppf_inverts_sf(self):
        d = ParetoTail(alpha=1.7, scale=1.0)
        q = np.array([0.1, 0.5, 0.9, 0.99])
        x = d.ppf(q)
        assert np.allclose(d.sf(x), 1 - q, rtol=1e-10)

    def test_rvs_empirical_tail(self, rng):
        d = ParetoTail(alpha=2.0, scale=1.0)
        x = d.rvs(200_000, rng)
        emp = (x > 10.0).mean()
        # P(X > 10) = 10^-2 = 0.01
        assert abs(emp - 0.01) < 0.002

    def test_logsf_consistency(self):
        d = ParetoTail(alpha=2.5, scale=1.0)
        x = np.array([2.0, 5.0, 100.0, 10_000.0])
        # At very large x, sf underflows; logsf must remain finite and correct.
        log_sf = d.logsf(x)
        assert np.allclose(log_sf, -2.5 * np.log(x), rtol=1e-12)
        assert np.all(np.isfinite(log_sf))


class TestLomaxTail:
    def test_sf_closed_form(self):
        d = LomaxTail(alpha=3.0, scale=2.0)
        x = np.array([1.0, 5.0, 50.0])
        expected = (1 + x / 2.0) ** (-3.0)
        assert np.allclose(d.sf(x), expected, rtol=1e-12)

    def test_ppf_inverts_sf(self):
        d = LomaxTail(alpha=2.5, scale=1.0)
        q = np.linspace(0.01, 0.99, 50)
        x = d.ppf(q)
        assert np.allclose(d.sf(x), 1 - q, rtol=1e-9)

    def test_finite_mean_matches_theory(self, rng):
        d = LomaxTail(alpha=3.0, scale=2.0)
        x = d.rvs(500_000, rng)
        theoretical = 2.0 / (3.0 - 1.0)  # = 1.0
        assert abs(x.mean() - theoretical) < 0.05
        # Direct check
        assert d.mean() == pytest.approx(theoretical)

    def test_infinite_mean_returns_inf(self):
        d = LomaxTail(alpha=0.8, scale=1.0)
        assert np.isinf(d.mean())


class TestBurrTail:
    def test_alpha_equals_k_times_d(self):
        d = BurrTail(k=2.0, d=1.5, scale=1.0)
        assert d.alpha == pytest.approx(3.0)

    def test_sf_closed_form(self):
        d = BurrTail(k=2.0, d=1.5, scale=1.0)
        x = np.array([1.0, 3.0, 7.0])
        expected = (1 + x**2.0) ** (-1.5)
        assert np.allclose(d.sf(x), expected, rtol=1e-12)


class TestStudentTTail:
    def test_sf_matches_scipy(self):
        d = StudentTTail(alpha=4.0, scale=1.5)
        x = np.array([1.0, 2.5, 5.0])
        assert np.allclose(d.sf(x), stats.t.sf(x / 1.5, df=4.0), rtol=1e-12)


def test_build_marginal_dispatch():
    d = build_marginal({"type": "pareto", "alpha": 2.0, "scale": 1.0})
    assert isinstance(d, ParetoTail)
    d = build_marginal({"type": "lomax", "alpha": 3.0, "scale": 1.0})
    assert isinstance(d, LomaxTail)
    with pytest.raises(ValueError):
        build_marginal({"type": "unknown"})
