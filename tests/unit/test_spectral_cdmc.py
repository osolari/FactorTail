r"""Method-correctness tests for spectral CdMC (``alg:spectral-cdmc``).

When the radial component is exact Pareto :math:`R\sim\mathrm{Par}(\alpha)`,

.. math::
    Z^{\mathrm{spec}}(x) = x^{-\alpha} (\ell(\Theta)_+)^\alpha,

and

.. math::
    E[Z^{\mathrm{spec}}(x)] = x^{-\alpha} \int (\ell(\theta)_+)^\alpha S(d\theta).

For axis-concentrated :math:`S` with equal masses on each :math:`e_i`,
:math:`E[Z^{\mathrm{spec}}(x)] = (1/d) \sum_i a_i^\alpha x^{-\alpha}`.
"""

from __future__ import annotations

import numpy as np

from factortail.cdmc import spectral_cdmc
from factortail.dgp.family5_mrv import RadialAngularMRV


def test_axis_angles_recover_independent_constant():
    alpha = 2.0
    d = 3
    dgp = RadialAngularMRV(
        alpha=alpha,
        angular_kind="axis",
        angular_params={"weights": [1.0, 1.0, 1.0]},
        radial_scale=1.0,
        dim=d,
    )
    exposure = np.array([1.0, 2.0, 0.5])
    x = 10.0
    res = spectral_cdmc(
        angle_sampler=lambda nn, rr: dgp.sample_angles(nn, rr),
        radial=dgp.radial,
        exposure=exposure,
        x=x,
        n=20_000,
        seed=42,
    )
    # P(R > x/(e_i^T a)) under uniform mass on axes:
    # mu(x) = (1/d) * sum_i (a_i_+)^alpha * x^-alpha
    expected = (1 / d) * float(((np.maximum(exposure, 0.0)) ** alpha).sum()) * x ** (-alpha)
    half = 1.96 * np.sqrt(res.variance / res.n)
    assert abs(res.mu_hat - expected) < 5 * half


def test_pareto_radial_yields_x_minus_alpha_scaling():
    alpha = 1.5
    dgp = RadialAngularMRV(
        alpha=alpha,
        angular_kind="dirichlet",
        angular_params={"concentration": [1.0, 1.0, 1.0]},
        radial_scale=1.0,
        dim=3,
    )
    exposure = np.ones(3)
    # mu(x) / mu(2x) = 2^alpha (since the estimator is exact x^-alpha scaled).
    res1 = spectral_cdmc(
        angle_sampler=lambda nn, rr: dgp.sample_angles(nn, rr),
        radial=dgp.radial,
        exposure=exposure,
        x=10.0,
        n=20_000,
        seed=1,
    )
    res2 = spectral_cdmc(
        angle_sampler=lambda nn, rr: dgp.sample_angles(nn, rr),
        radial=dgp.radial,
        exposure=exposure,
        x=20.0,
        n=20_000,
        seed=1,
    )
    ratio = res1.mu_hat / res2.mu_hat
    assert abs(ratio - 2.0**alpha) / (2.0**alpha) < 0.05


def test_spectral_zero_when_exposure_negative():
    # If the exposure is everywhere negative on the angular support, then
    # ell(theta) <= 0 and the estimator must be exactly zero.
    dgp = RadialAngularMRV(
        alpha=2.0,
        angular_kind="dirichlet",
        angular_params={"concentration": [1.0, 1.0]},
        dim=2,
    )
    res = spectral_cdmc(
        angle_sampler=lambda nn, rr: dgp.sample_angles(nn, rr),
        radial=dgp.radial,
        exposure=np.array([-1.0, -1.0]),
        x=5.0,
        n=5000,
        seed=0,
    )
    assert res.mu_hat == 0.0
    assert res.variance == 0.0 or np.isnan(res.variance)
