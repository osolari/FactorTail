r"""Method-correctness tests for latent-shock CdMC
(Theorem ``thm:latent-shock-tail``).

For a single-shock model :math:`X_i = b_i Z_0`, the latent-shock CdMC must
recover the constant :math:`(\sum_i b_i)_+^\alpha c_{Z_0}`, distinct from the
misspecified observed-axes constant :math:`\sum_i b_i^\alpha c_{Z_0}`.
"""

from __future__ import annotations

import numpy as np
import pytest

from factortail.cdmc import latent_shock_cdmc
from factortail.dgp.family2_latent_shock import CommonShockModel
from factortail.utils.tails import LomaxTail, ParetoTail


def test_common_shock_constant_matches_theory():
    b = np.array([1.0, 0.8, 0.6, 0.4])
    Z = ParetoTail(alpha=2.0, scale=1.0)
    E = [LomaxTail(alpha=2.0, scale=0.1) for _ in range(4)]
    dgp = CommonShockModel(loadings=b, shock=Z, idiosyncratic=E)
    constants = dgp.latent_constants()
    # Theory: correct = (sum b)_+^alpha * c_Z + sum c_i ; misspec = sum b_i^alpha c_Z + sum c_i
    correct_expected = b.sum() ** 2.0 * Z.c + sum(e.c for e in E)
    misspec_expected = float((b**2.0).sum()) * Z.c + sum(e.c for e in E)
    assert constants["correct_latent_constant"] == pytest.approx(correct_expected, rel=1e-12)
    assert constants["misspecified_observed_constant"] == pytest.approx(misspec_expected, rel=1e-12)
    # Sanity: same-sign loadings make the latent constant dominate.
    assert correct_expected > misspec_expected


def test_latent_shock_cdmc_unbiased_for_two_factor_pareto():
    r"""Two-factor model :math:`X = B Z` with independent Pareto shocks; the
    sum loss has known first-order constant
    :math:`(\sum_i q_i)_+^\alpha + \dots`. We compare the CdMC mean to the
    empirical tail of a high-budget crude MC."""
    B = np.array([[1.0, 0.0], [0.5, 0.5]])
    shocks = [ParetoTail(alpha=2.0, scale=1.0), ParetoTail(alpha=2.0, scale=1.0)]
    a = np.array([1.0, 1.0])
    # Crude reference
    n_ref = 100_000
    x = 15.0
    rng = np.random.default_rng(0)
    Z = np.column_stack([s.rvs(n_ref, rng) for s in shocks])
    L = Z @ B.T @ a
    emp = float((x < L).mean())
    se = np.sqrt(emp * (1 - emp) / n_ref)
    # CdMC
    res = latent_shock_cdmc(
        B=B,
        exposure=a,
        shocks=shocks,
        idiosyncratic=None,
        x=x,
        n=5000,
        seed=42,
    )
    cdmc_se = np.sqrt(res.variance / res.n)
    # CdMC must agree with crude MC reference within combined uncertainty.
    assert abs(res.mu_hat - emp) < 6 * (cdmc_se + se)


def test_latent_shock_handles_zero_exposure():
    B = np.eye(2)
    shocks = [ParetoTail(alpha=2.0, scale=1.0)] * 2
    res = latent_shock_cdmc(
        B=B,
        exposure=np.array([1.0, 0.0]),
        shocks=shocks,
        x=5.0,
        n=1000,
        seed=1,
    )
    # Only first shock is active.
    assert res.extra["active_shocks"] == 1
