r"""Method-correctness tests for copula samplers and conditional kernels.

* GaussianCopula: the conditional survival under independent margins
  (R = I) collapses to the marginal Gaussian survival.
* Comonotone Gaussian copula (R = 11^T) yields ``U_i = U_j``.
* Clayton with theta -> 0 approaches independence (sample correlation -> 0).
"""

from __future__ import annotations

import numpy as np
import pytest

from factortail.copula import ClaytonCopula, GaussianCopula, GumbelCopula


class TestGaussianCopula:
    def test_independent_correlation_is_zero(self):
        R = np.eye(3)
        cop = GaussianCopula(R=R)
        rng = np.random.default_rng(0)
        U = cop.sample_uniform(20_000, rng)
        # Spearman rank correlation between independent uniforms is close to 0.
        corr = np.corrcoef(U.T)
        off = corr[~np.eye(3, dtype=bool)]
        assert np.all(np.abs(off) < 0.05)

    def test_conditional_survival_independent_reduces_to_marginal(self):
        R = np.eye(3)
        cop = GaussianCopula(R=R)
        # Independent => P(U_i > t | U_-i) = P(U_i > t) = 1 - t.
        u_minus = np.array([0.3, 0.7])
        for t in (0.1, 0.5, 0.9):
            assert cop.conditional_survival(t, u_minus, i=0) == pytest.approx(1 - t, abs=1e-9)

    def test_strong_positive_correlation(self):
        R = np.array([[1.0, 0.9], [0.9, 1.0]])
        cop = GaussianCopula(R=R)
        rng = np.random.default_rng(1)
        U = cop.sample_uniform(20_000, rng)
        # Rank correlation should be high.
        from scipy.stats import spearmanr

        rho_s, _ = spearmanr(U[:, 0], U[:, 1])
        assert rho_s > 0.8


class TestClayton:
    def test_independence_limit_theta_small(self):
        cop = ClaytonCopula(theta=0.01, d=2)
        rng = np.random.default_rng(0)
        U = cop.sample_uniform(20_000, rng)
        from scipy.stats import spearmanr

        rho_s, _ = spearmanr(U[:, 0], U[:, 1])
        assert abs(rho_s) < 0.1

    def test_strong_positive_dependence(self):
        cop = ClaytonCopula(theta=4.0, d=2)
        rng = np.random.default_rng(0)
        U = cop.sample_uniform(20_000, rng)
        from scipy.stats import spearmanr

        rho_s, _ = spearmanr(U[:, 0], U[:, 1])
        assert rho_s > 0.5


class TestGumbel:
    def test_independence_when_theta_one(self):
        cop = GumbelCopula(theta=1.0, d=2)
        rng = np.random.default_rng(0)
        U = cop.sample_uniform(20_000, rng)
        from scipy.stats import spearmanr

        rho_s, _ = spearmanr(U[:, 0], U[:, 1])
        assert abs(rho_s) < 0.05

    def test_positive_dependence_for_theta_three(self):
        cop = GumbelCopula(theta=3.0, d=2)
        rng = np.random.default_rng(0)
        U = cop.sample_uniform(10_000, rng)
        from scipy.stats import spearmanr

        rho_s, _ = spearmanr(U[:, 0], U[:, 1])
        assert rho_s > 0.6
