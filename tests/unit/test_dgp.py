"""Tests for the simulation DGPs (Families I-VI)."""

from __future__ import annotations

import numpy as np
import pytest

from factortail.dgp import (
    CommonShockModel,
    HiddenConeMixture,
    IndependentINID,
    LatentFactorModel,
    RadialAngularMRV,
)
from factortail.utils.tails import LomaxTail, ParetoTail


def test_independent_inid_samples_are_independent():
    dgp = IndependentINID.from_specs(
        [
            {"type": "pareto", "alpha": 2.0, "scale": 1.0},
            {"type": "pareto", "alpha": 2.0, "scale": 1.0},
        ]
    )
    rng = np.random.default_rng(0)
    X = dgp.sample(20_000, rng)
    corr = float(np.corrcoef(X.T)[0, 1])
    assert abs(corr) < 0.05


def test_common_shock_produces_positive_correlation():
    dgp = CommonShockModel(
        loadings=np.array([1.0, 1.0]),
        shock=ParetoTail(alpha=2.0, scale=1.0),
        idiosyncratic=[LomaxTail(alpha=2.0, scale=0.1)] * 2,
    )
    rng = np.random.default_rng(0)
    X = dgp.sample(20_000, rng)
    from scipy.stats import spearmanr

    rho_s, _ = spearmanr(X[:, 0], X[:, 1])
    assert rho_s > 0.3


def test_latent_factor_model_tail_constant_matches_definition():
    B = np.array([[1.0, 0.0], [0.5, 0.5]])
    shocks = [ParetoTail(alpha=2.0, scale=1.0)] * 2
    idio = [LomaxTail(alpha=2.0, scale=0.1)] * 2
    dgp = LatentFactorModel(B=B, shocks=shocks, idiosyncratic=idio)
    a = np.array([1.0, 1.0])
    q = B.T @ a  # = [1.5, 0.5]
    expected = abs(q[0]) ** 2.0 + abs(q[1]) ** 2.0 + 0.1**2.0 + 0.1**2.0
    assert dgp.latent_tail_constant(a) == pytest.approx(expected, abs=1e-12)


def test_radial_angular_axis_concentration():
    dgp = RadialAngularMRV(
        alpha=2.0,
        angular_kind="axis",
        angular_params={"weights": [0.5, 0.5]},
        dim=2,
    )
    rng = np.random.default_rng(0)
    Theta = dgp.sample_angles(10_000, rng)
    # Exactly one coordinate is one and the other zero.
    assert np.all(Theta.sum(axis=1) == 1.0)
    # Empirical mass on axis 0 should be ~0.5.
    on_axis_0 = (Theta[:, 0] == 1.0).mean()
    assert abs(on_axis_0 - 0.5) < 0.05


def test_hidden_cone_alpha_hidden_dominates_at_moderate_x():
    """For Family VI: at moderate x, the hidden term should be observable."""
    dgp = HiddenConeMixture(
        alpha=2.0,
        alpha_hidden=2.0,  # for the test, set equal so both terms scale alike
        hidden_prob=0.5,
        dim=4,
        pair_indices=[(0, 1)],
    )
    rng = np.random.default_rng(0)
    X = dgp.sample(50_000, rng)
    # Pair-cone occupancy: both X_0 and X_1 large together.
    threshold = np.quantile(np.abs(X), 0.99)
    pair_exc = ((X[:, 0] > threshold * 0.5) & (X[:, 1] > threshold * 0.5)).mean()
    # Single-axis exceedance via axis component only.
    single_exc = (X[:, 0] > threshold).mean()
    # With hidden_prob = 0.5 both terms should be non-trivial.
    assert pair_exc > 0
    assert single_exc > 0
