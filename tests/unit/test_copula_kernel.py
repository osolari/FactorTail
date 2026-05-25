r"""Method-correctness tests for the copula-kernel wrappers and the d-dim
Archimedean conditional formulas.
"""

from __future__ import annotations

import numpy as np
import pytest

from factortail.cdmc import dependent_cdmc
from factortail.cdmc.copula_kernel import build_copula_kernel, build_copula_sampler
from factortail.copula import (
    ClaytonCopula,
    FrankCopula,
    GaussianCopula,
    GumbelCopula,
)
from factortail.utils.tails import ParetoTail


class TestClaytonConditional:
    def test_bivariate_matches_old_formula(self):
        """The new d-dim formula must reduce to the old bivariate Clayton
        conditional survival at d=2."""
        cop = ClaytonCopula(theta=2.0, d=2)
        u, t = 0.7, 0.4
        new = cop.conditional_survival(t, np.array([u]))
        # Old bivariate closed form: 1 - u^{-theta-1} * (u^{-theta} + t^{-theta} - 1)^{-(1+theta)/theta}
        theta = 2.0
        old = 1.0 - u ** (-theta - 1) * (u ** (-theta) + t ** (-theta) - 1.0) ** (
            -(1.0 + theta) / theta
        )
        assert abs(new - old) < 1e-12

    def test_d3_endpoint_at_t_one_is_zero(self):
        cop = ClaytonCopula(theta=2.0, d=3)
        u = np.array([0.5, 0.6])
        assert cop.conditional_survival(1.0 - 1e-15, u) <= 1e-9

    def test_d3_endpoint_at_t_zero_is_one(self):
        cop = ClaytonCopula(theta=2.0, d=3)
        u = np.array([0.5, 0.6])
        assert cop.conditional_survival(1e-15, u) == pytest.approx(1.0, abs=1e-9)

    def test_d3_consistency_with_simulation(self):
        """Monte Carlo check: the conditional survival should match the
        empirical conditional tail in a high-budget simulation."""
        cop = ClaytonCopula(theta=2.0, d=3)
        rng = np.random.default_rng(0)
        n = 100_000
        U = cop.sample_uniform(n, rng)
        # Condition: U_0 in [u0 ± eps], U_1 in [u1 ± eps].
        u0, u1 = 0.6, 0.7
        eps = 0.05
        mask = (np.abs(U[:, 0] - u0) < eps) & (np.abs(U[:, 1] - u1) < eps)
        sub = U[mask, 2]
        emp = float((sub > 0.5).mean())
        predicted = cop.conditional_survival(0.5, np.array([u0, u1]))
        assert abs(emp - predicted) < 0.05  # tight CI given ~few thousand subsamples


class TestGumbelConditional:
    def test_endpoint_t_zero_is_one(self):
        cop = GumbelCopula(theta=2.5, d=2)
        assert cop.conditional_survival(1e-15, np.array([0.5])) == pytest.approx(1.0, abs=1e-9)

    def test_bivariate_consistency_with_simulation(self):
        cop = GumbelCopula(theta=2.5, d=2)
        rng = np.random.default_rng(0)
        U = cop.sample_uniform(100_000, rng)
        u0 = 0.7
        eps = 0.03
        mask = np.abs(U[:, 0] - u0) < eps
        emp = float((U[mask, 1] > 0.5).mean())
        predicted = cop.conditional_survival(0.5, np.array([u0]))
        assert abs(emp - predicted) < 0.05

    def test_d_greater_than_2_rejected(self):
        cop = GumbelCopula(theta=2.0, d=3)
        with pytest.raises(NotImplementedError):
            cop.conditional_survival(0.5, np.array([0.4, 0.6]))


class TestFrankConditional:
    def test_endpoint_consistency(self):
        cop = FrankCopula(theta=3.0, d=2)
        assert cop.conditional_survival(1e-15, 0.5) == pytest.approx(1.0, abs=1e-9)
        # As t -> 1 the conditional CDF -> 1 so survival -> 0.
        assert cop.conditional_survival(1.0 - 1e-9, 0.5) < 1e-6

    def test_consistency_with_simulation(self):
        cop = FrankCopula(theta=3.0, d=2)
        rng = np.random.default_rng(0)
        n = 400_000
        U = cop.sample_uniform(n, rng)
        u0 = 0.6
        eps = 0.03
        mask = np.abs(U[:, 0] - u0) < eps
        emp = float((U[mask, 1] > 0.4).mean())
        predicted = cop.conditional_survival(0.4, 0.6)
        n_slice = int(mask.sum())
        se = float(np.sqrt(max(emp * (1 - emp), 1e-6) / max(n_slice, 1)))
        assert abs(emp - predicted) < 4 * se + 0.03


class TestCopulaKernelWrapper:
    def test_reduces_to_marginal_for_independent_copula(self):
        """Gaussian copula with identity correlation -> independent copula;
        the kernel must equal the marginal survival."""
        marginals = [ParetoTail(alpha=2.0, scale=1.0)] * 3
        copula = GaussianCopula(R=np.eye(3))
        kernel = build_copula_kernel(copula, marginals)
        X_minus_i = np.array([2.0, 3.0])
        t = 5.0
        # Under independence: P(X_0 > 5 | X_1, X_2) = P(X_0 > 5) = sf(5).
        expected = float(marginals[0].sf(t))
        got = kernel(t, X_minus_i, i=0)
        assert abs(got - expected) < 1e-4

    def test_dependent_cdmc_with_clayton_returns_finite_estimate(self):
        marginals = [ParetoTail(alpha=2.0, scale=1.0)] * 3
        cop = ClaytonCopula(theta=2.0, d=3)
        sampler = build_copula_sampler(cop, marginals)
        kernel = build_copula_kernel(cop, marginals)
        res = dependent_cdmc(sampler=sampler, kernel=kernel, x=10.0, n=1000, seed=42)
        assert np.isfinite(res.mu_hat) and res.mu_hat > 0
        # Crude reference (low budget; just check order of magnitude).
        rng = np.random.default_rng(42)
        X = sampler(20_000, rng)
        emp = float((X.sum(axis=1) > 10.0).mean())
        # Should agree to within 50%.
        assert 0.5 * emp < res.mu_hat < 1.5 * emp + 1e-3
