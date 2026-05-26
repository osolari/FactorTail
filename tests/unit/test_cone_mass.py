r"""Method-correctness tests for the direct cone-mass alpha_2 estimator."""

from __future__ import annotations

import numpy as np

from factortail.dgp import HiddenConeMixture
from factortail.hrv import cone_mass_alpha, is_interior


def test_pair_cone_mask_excludes_pure_axis():
    """is_interior should treat (1, 0, 0) as not-interior but (.5, .5, 0)
    as interior at min_active=2."""
    angles = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.5, 0.5, 0.0],
            [0.4, 0.3, 0.3],
        ]
    )
    mask = is_interior(angles, min_coord=0.05, min_active=2)
    assert mask.tolist() == [False, False, True, True]


def test_cone_mass_recovers_pareto_alpha_on_synthetic_pair():
    """On a clean pair-cone Pareto design, the cone-mass slope must recover
    the true alpha_2 within ~20%."""
    rng = np.random.default_rng(0)
    true_alpha_2 = 2.5
    dim = 3
    n = 80_000
    # Build a manual pair-cone DGP: with prob p, sample R~Pareto(alpha_2)
    # and place equal mass on coordinates (0, 1); otherwise place mass on
    # a coordinate axis.
    p_hidden = 0.5
    R_hidden = rng.pareto(true_alpha_2, size=n) + 1.0
    R_axis = rng.pareto(1.5, size=n) + 1.0
    is_hidden = rng.random(n) < p_hidden
    X = np.zeros((n, dim))
    rows_hidden = np.where(is_hidden)[0]
    X[rows_hidden, 0] = R_hidden[rows_hidden] * 0.55
    X[rows_hidden, 1] = R_hidden[rows_hidden] * 0.45
    rows_axis = np.where(~is_hidden)[0]
    idx_axis = rng.integers(0, dim, size=len(rows_axis))
    X[rows_axis, idx_axis] = R_axis[rows_axis]

    res = cone_mass_alpha(X, min_coord=0.05)
    assert np.isfinite(res["alpha_hat"])
    # 20% slack accommodates the regression fit + finite sample.
    assert abs(res["alpha_hat"] - true_alpha_2) / true_alpha_2 < 0.20


def test_cone_mass_outperforms_eta_on_factory_family_vi():
    """End-to-end: the FactorTail Family-VI mixture's true alpha_2 is
    recovered better by cone_mass than by Ledford-Tawn eta = 1/alpha_2."""
    from factortail.diagnostics.dependence import empirical_ranks
    from factortail.hrv import ledford_tawn_eta

    dgp = HiddenConeMixture(
        alpha=2.0,
        alpha_hidden=3.0,
        hidden_prob=0.4,
        dim=4,
        pair_indices=[(0, 1), (2, 3)],
        pair_weights=np.array([0.6, 0.4]),
    )
    rng = np.random.default_rng(1)
    X = dgp.sample(80_000, rng)
    true_alpha2 = 3.0

    U = empirical_ranks(X[:, :2])
    eta = ledford_tawn_eta(U[:, 0], U[:, 1], k=400)
    eta_alpha2 = 1.0 / max(eta["eta_hat"], 1e-9)
    cone = cone_mass_alpha(X, min_coord=0.05)
    cone_alpha2 = float(cone["alpha_hat"])

    err_eta = abs(eta_alpha2 - true_alpha2) / true_alpha2
    err_cone = abs(cone_alpha2 - true_alpha2) / true_alpha2
    # Cone-mass should be at least as accurate as eta on this design.
    assert err_cone <= err_eta + 0.05
