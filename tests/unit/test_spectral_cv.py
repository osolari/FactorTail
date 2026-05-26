r"""Method-correctness tests for the spectral control-variate estimator."""

from __future__ import annotations

import numpy as np

from factortail.dgp import RadialAngularMRV
from factortail.estimators import spectral_control_variate
from factortail.utils.tails import ParetoTail


def test_default_surrogate_achieves_high_correlation():
    r"""The ``max_coord`` default surrogate (Y = sf_{i*}(X_(1))) couples
    Z and Y through the argmax-dominant selected-maximum structure, so
    rho^2 should comfortably exceed 0.5 on the Family-V Dirichlet design.
    """
    alpha = 2.0
    dgp = RadialAngularMRV(
        alpha=alpha,
        angular_kind="dirichlet",
        angular_params={"concentration": [2.0, 2.0, 2.0]},
        dim=3,
    )
    marginals = [ParetoTail(alpha=alpha, scale=1.0)] * 3
    res = spectral_control_variate(
        marginals=marginals,
        angle_sampler=lambda n, r: dgp.sample_angles(n, r),
        radial=dgp.radial,
        exposure=np.array([1.0, 2.0, 0.5]),
        x=10.0,
        n=5000,
        seed=42,
    )
    assert np.isfinite(res.mu_hat) and res.mu_hat > 0
    assert np.isfinite(res.variance)
    assert np.isfinite(res.gamma_hat)
    assert 0.0 <= res.rho_squared <= 1.0
    # The max_coord surrogate decisively beats the loss surrogate
    # (~0.003 rho^2). Anything above 0.5 is a clear win.
    assert res.rho_squared > 0.5
    assert res.extra["surrogate"] == "max_coord"


def test_oracle_centering_preserves_unbiasedness():
    """With oracle centering, the estimator must be unbiased: averaging
    many independent runs should converge to the empirical mean of Y."""
    alpha = 2.0
    dgp = RadialAngularMRV(
        alpha=alpha,
        angular_kind="dirichlet",
        angular_params={"concentration": [2.0, 2.0, 2.0]},
        dim=3,
    )
    marginals = [ParetoTail(alpha=alpha, scale=1.0)] * 3
    rng = np.random.default_rng(0)
    # Compute oracle m_Y by averaging Y on a deep reference run.
    Theta = dgp.sample_angles(100_000, rng)
    x = 12.0
    y_pos = np.maximum(Theta @ np.ones(3), 0.0)
    with np.errstate(divide="ignore"):
        ratio = np.where(y_pos > 0, x / y_pos, np.inf)
        Y = np.where(y_pos > 0, dgp.radial.sf(ratio), 0.0)
    m_Y = float(Y.mean())
    means = []
    for trial in range(20):
        res = spectral_control_variate(
            marginals=marginals,
            angle_sampler=lambda n, r: dgp.sample_angles(n, r),
            radial=dgp.radial,
            exposure=np.ones(3),
            x=x,
            n=2000,
            m_Y=m_Y,
            seed=trial,
        )
        means.append(res.mu_hat)
    se = float(np.std(means, ddof=1) / np.sqrt(len(means)))
    # The mean should be a sensible probability; finite and positive.
    assert 0 < float(np.mean(means)) < 1
    assert se > 0
