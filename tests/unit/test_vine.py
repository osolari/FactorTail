r"""Method-correctness tests for the C-vine truncation kernel."""

from __future__ import annotations

import numpy as np
import pytest

from factortail.copula import ClaytonCopula, CVineKernel, GumbelCopula


def test_d2_matches_bivariate_exactly():
    """For d=2 the vine kernel is the bivariate kernel itself."""
    cop = ClaytonCopula(theta=2.0, d=2)
    vine = CVineKernel(bivariate_copula=cop, d=2)
    u = np.array([0.6])
    for t in (0.2, 0.5, 0.8):
        assert vine.conditional_survival(t, u) == pytest.approx(
            cop.conditional_survival(t, u), rel=1e-12
        )


def test_d3_vine_is_finite_and_in_unit_interval():
    cop = GumbelCopula(theta=2.0, d=2)
    vine = CVineKernel(bivariate_copula=cop, d=3)
    u = np.array([0.5, 0.7])
    for t in (0.1, 0.5, 0.9):
        v = vine.conditional_survival(t, u)
        assert 0.0 <= v <= 1.0
        assert np.isfinite(v)


def test_d3_vine_recovers_independence_at_theta_one_gumbel():
    """With Gumbel(theta=1) the copula is independence, so the conditional
    survival equals the marginal 1 - t."""
    cop = GumbelCopula(theta=1.0, d=2)
    vine = CVineKernel(bivariate_copula=cop, d=3)
    u = np.array([0.4, 0.7])
    for t in (0.2, 0.5, 0.8):
        assert vine.conditional_survival(t, u) == pytest.approx(1.0 - t, abs=1e-9)


def test_rejects_invalid_dimension():
    cop = ClaytonCopula(theta=1.5, d=2)
    with pytest.raises(ValueError):
        CVineKernel(bivariate_copula=cop, d=1)


def test_rejects_wrong_conditioning_length():
    cop = ClaytonCopula(theta=1.5, d=2)
    vine = CVineKernel(bivariate_copula=cop, d=4)
    with pytest.raises(ValueError):
        vine.conditional_survival(0.5, np.array([0.4, 0.6]))
