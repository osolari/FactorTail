r"""Method-correctness tests for tail/dependence diagnostics.

* Hill on Pareto(alpha): :math:`\widehat\alpha \to \alpha` as ``k`` grows
  (Mason 1982).
* Pickands on Pareto: same consistency.
* :math:`\eta` for independent uniforms is :math:`1/2`.
* :math:`\chi(u)` for the comonotone copula is :math:`1`.
"""

from __future__ import annotations

import numpy as np
import pytest

from factortail.diagnostics import hill_estimator, pickands_estimator, pot_gpd_estimator
from factortail.hrv.ledford_tawn import chi_chibar, ledford_tawn_eta
from factortail.utils.tails import ParetoTail


class TestHill:
    @pytest.mark.parametrize("alpha", [1.5, 2.0, 3.0])
    def test_consistency_on_pareto(self, alpha):
        d = ParetoTail(alpha=alpha, scale=1.0)
        rng = np.random.default_rng(0)
        x = d.rvs(20_000, rng)
        hill = hill_estimator(x, k=500)
        assert abs(hill["alpha_hat"] - alpha) / alpha < 0.10

    def test_rejects_invalid_k(self):
        x = np.array([1.0, 2.0, 3.0])
        with pytest.raises(ValueError):
            hill_estimator(x, k=10)


class TestPickands:
    def test_pareto_consistency(self):
        d = ParetoTail(alpha=2.0, scale=1.0)
        rng = np.random.default_rng(1)
        x = d.rvs(50_000, rng)
        # Pickands is high-variance; use larger k.
        pick = pickands_estimator(x, k=1000)
        assert abs(pick["alpha_hat"] - 2.0) / 2.0 < 0.25


class TestPotGpd:
    def test_pareto_alpha_recovered(self):
        d = ParetoTail(alpha=2.5, scale=1.0)
        rng = np.random.default_rng(2)
        x = d.rvs(30_000, rng)
        pot = pot_gpd_estimator(x, k=2000)
        # MLE consistency
        assert abs(pot["alpha_hat"] - 2.5) / 2.5 < 0.15


class TestLedfordTawn:
    def test_independent_uniforms_have_eta_half(self):
        rng = np.random.default_rng(0)
        n = 20_000
        U = rng.random(n)
        V = rng.random(n)
        res = ledford_tawn_eta(U, V, k=500)
        # eta should be approximately 1/2 for independent uniforms.
        assert abs(res["eta_hat"] - 0.5) < 0.1

    def test_comonotone_has_eta_one(self):
        rng = np.random.default_rng(0)
        U = rng.random(20_000)
        V = U.copy()
        res = ledford_tawn_eta(U, V, k=500)
        # eta -> 1 for perfectly dependent uniforms.
        assert res["eta_hat"] > 0.8


class TestChiChibar:
    def test_independent_chi_zero(self):
        rng = np.random.default_rng(0)
        U = rng.random(10_000)
        V = rng.random(10_000)
        res = chi_chibar(U, V, threshold_u=0.95)
        # P(U>0.95, V>0.95) / P(V>0.95) = P(U>0.95) = 0.05 in the limit;
        # for independent, chi = 0.05 conditional rate, not 0.
        assert abs(res["chi_hat"] - 0.05) < 0.04

    def test_comonotone_chi_one(self):
        rng = np.random.default_rng(0)
        U = rng.random(10_000)
        V = U.copy()
        res = chi_chibar(U, V, threshold_u=0.95)
        assert res["chi_hat"] == pytest.approx(1.0, abs=0.05)
