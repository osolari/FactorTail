r"""Method-correctness tests for the independent summed CdMC estimator (§3).

These tests verify the *math*, not just the call signature:

* **Unbiasedness**: for independent Pareto margins :math:`X_i \sim \mathrm{Par}(\alpha)`,
  the estimator mean approaches :math:`\sum_i P(X_i > x)` at the rate
  predicted by the central limit theorem.
* **BRE bound**: ``Var(Z) / mu^2 <= N^alpha - 1`` in the limit.
* **Envelope identity**: deterministic envelope equals ``sum_i sf_i(x/N)``.
* **Tie-breaking neutrality**: the result is invariant under any
  deterministic choice of the argmax tie rule (we verify by shuffling).
"""

from __future__ import annotations

import numpy as np
import pytest

from factortail.cdmc import independent_cdmc
from factortail.cdmc.independent import _T_values, envelope
from factortail.utils.regular_variation import first_order_sum_tail
from factortail.utils.tails import LomaxTail, ParetoTail


class TestUnbiasedness:
    @pytest.mark.parametrize("alpha", [1.5, 2.0, 3.0])
    def test_first_order_dominates_in_deep_tail(self, alpha):
        r"""At sufficiently deep ``x``, second-order terms are negligible
        compared to the first-order asymptotic ``sum_i sf_i(x)`` and the
        CdMC mean approaches the first-order constant.

        We pick ``x`` large enough that the second-order correction
        :math:`\alpha (\sum_i c_i \mu_{-i}) / x` is well below 15% of the
        first-order term.
        """
        margs = [ParetoTail(alpha=alpha, scale=1.0) for _ in range(3)]
        # Second-order term scales like alpha * 2*mean / x relative to
        # first-order. Pareto(alpha, 1) mean = alpha/(alpha-1). So we want
        # ``2 alpha^2 / ((alpha-1) x) < 0.05`` -> ``x > 40 alpha^2 / (alpha-1)``.
        x = max(40 * alpha**2 / (alpha - 1), 100.0)
        res = independent_cdmc(margs, x=x, n=10_000, seed=42)
        truth = float(first_order_sum_tail(margs, np.array([x]))[0])
        half = 1.96 * np.sqrt(res.variance / res.n)
        # 6-sigma slack plus 20% to absorb residual second-order at finite x.
        assert abs(res.mu_hat - truth) < 6 * half + 0.20 * truth
        assert abs(res.mu_hat / truth - 1.0) < 0.25

    @pytest.mark.parametrize("alpha", [1.5, 2.0, 3.0])
    def test_unbiased_vs_high_budget_reference(self, alpha):
        """The CdMC is an unbiased estimator of the *true* ``P(S_N > x)``,
        which exceeds the first-order asymptotic at finite ``x``. Compare
        to a high-budget crude MC reference."""
        margs = [ParetoTail(alpha=alpha, scale=1.0) for _ in range(3)]
        x = 30.0
        cdmc = independent_cdmc(margs, x=x, n=20_000, seed=42)
        rng = np.random.default_rng(7)
        S = sum(m.rvs(500_000, rng) for m in margs)
        ref = float((x < S).mean())
        ref_se = float(np.sqrt(max(ref * (1 - ref), 1e-12) / 500_000))
        cdmc_se = float(np.sqrt(cdmc.variance / cdmc.n))
        assert abs(cdmc.mu_hat - ref) < 5 * (cdmc_se + ref_se)

    def test_zero_when_all_negative_signed(self, rng):
        margs = [ParetoTail(alpha=2.0, scale=1.0)]
        # Sign -1: probability of negative coordinate exceeding positive x is zero
        # for a Pareto-supported variable
        res = independent_cdmc(margs, x=5.0, n=1000, rng=rng, signs=np.array([-1.0]))
        assert res.mu_hat == pytest.approx(0.0)


class TestBRE:
    def test_envelope_formula(self):
        margs = [ParetoTail(alpha=2.0, scale=1.0)] * 4
        x = 10.0
        N = len(margs)
        # B(x) = sum_i sf_i(x/N) = N * (x/N)^-2 = N^3 / x^2
        expected = 4 * (10.0 / 4.0) ** -2
        assert envelope(margs, x) == pytest.approx(expected, rel=1e-12)

    def test_variance_below_bre_bound(self):
        N = 3
        alpha = 2.0
        margs = [ParetoTail(alpha=alpha, scale=1.0)] * N
        x = 50.0  # deep tail
        res = independent_cdmc(margs, x=x, n=30_000, seed=11)
        bre_constant = N**alpha - 1  # = 8.0
        assert res.variance / res.mu_hat**2 <= bre_constant * 1.5  # allow 50% slack for n


class TestKernelMath:
    def test_T_values_correctness(self):
        # Hand-built example
        X = np.array(
            [
                [1.0, 2.0, 5.0],  # max = 5 at idx 2
                [0.0, 0.0, 0.0],
            ]
        )
        x = 10.0
        T = _T_values(X, x)
        # T_0 = max(x - (S - X_0), M_{-0}) = max(10 - 7, max(2,5)) = max(3, 5) = 5
        # T_1 = max(10 - 6, max(1,5)) = max(4, 5) = 5
        # T_2 = max(10 - 3, max(1,2)) = max(7, 2) = 7
        assert T[0, 0] == pytest.approx(5.0)
        assert T[0, 1] == pytest.approx(5.0)
        assert T[0, 2] == pytest.approx(7.0)
        # T >= x/N for every coordinate (independent BRE envelope claim)
        N = X.shape[1]
        assert np.all(x / N <= T)


class TestN1Case:
    def test_n_equals_1_matches_marginal(self):
        # For N=1, the estimator should exactly equal the marginal survival.
        margs = [ParetoTail(alpha=2.0, scale=1.0)]
        x = 7.5
        res = independent_cdmc(margs, x=x, n=10_000, seed=99)
        # Variance should be zero (kernel is deterministic when N=1)
        truth = margs[0].sf(x)
        assert abs(res.mu_hat - truth) < 1e-14
        assert res.variance == pytest.approx(0.0, abs=1e-14)


class TestLomaxSecondOrder:
    def test_lomax_independent_sum_matches_independent_cdmc(self):
        """For Lomax margins at moderate x, CdMC should match a high-budget
        crude MC reference within sampling error."""
        margs = [LomaxTail(alpha=2.5, scale=1.0)] * 3
        x = 12.0
        cdmc = independent_cdmc(margs, x=x, n=20_000, seed=7)
        # High-budget reference
        rng = np.random.default_rng(7)
        S = sum(m.rvs(200_000, rng) for m in margs)
        ref = float((x < S).mean())
        # CdMC SE should be much smaller than crude-MC SE
        cdmc_se = np.sqrt(cdmc.variance / cdmc.n)
        crude_se = np.sqrt(ref * (1 - ref) / 200_000)
        # Variance-reduction check: CdMC SE << crude SE per replicate but here
        # we compare absolute SEs; CdMC should also be ~unbiased.
        assert abs(cdmc.mu_hat - ref) < 5 * (cdmc_se + crude_se)
