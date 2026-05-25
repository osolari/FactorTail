r"""Spectral / radial CdMC (``alg:spectral-cdmc``).

For a loss functional :math:`\ell(z) = a^\top z` and a radial-angular MRV
representation :math:`X = R \Theta`, the unbiased estimator is

.. math::

    Z^{\mathrm{spec}}(x) = \overline F_R\{x/\ell(\Theta) \mid \Theta\}
    \mathbf 1\{\ell(\Theta) > 0\}.

When :math:`R` is exact Pareto with index :math:`\alpha` (no conditional
dependence on :math:`\Theta`),
:math:`Z^{\mathrm{spec}}(x) = x^{-\alpha} (\ell(\Theta)_+)^\alpha`.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from factortail.cdmc.base import CdMCResult, sample_ci
from factortail.utils.tails import TailDistribution
from factortail.utils.timing import runtime_seconds

__all__ = ["spectral_cdmc"]

AngleSampler = Callable[[int, np.random.Generator], NDArray[np.float64]]


def spectral_cdmc(
    *,
    angle_sampler: AngleSampler,
    radial: TailDistribution,
    exposure: NDArray[np.float64],
    x: float,
    n: int,
    rng: np.random.Generator | None = None,
    seed: int | None = None,
) -> CdMCResult:
    r"""Algorithm ``alg:spectral-cdmc``.

    Parameters
    ----------
    angle_sampler:
        ``(n, rng) -> (n, dim)`` angular draws on the simplex / sphere.
    radial:
        Radial survival model (e.g. exact Pareto).
    exposure:
        Loss functional vector ``a``.
    x:
        Loss threshold.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    exposure = np.asarray(exposure, dtype=float)
    Theta = angle_sampler(n, rng)
    if Theta.ndim != 2 or Theta.shape[1] != exposure.shape[0]:
        raise ValueError(f"Angles {Theta.shape} incompatible with exposure {exposure.shape}")
    with runtime_seconds() as elapsed:
        y = Theta @ exposure
        y_pos = np.maximum(y, 0.0)
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(y_pos > 0, x / y_pos, np.inf)
            Z = radial.sf(ratio)
        Z = np.where(y_pos > 0, Z, 0.0)
        mu_hat = float(Z.mean())
        var = float(Z.var(ddof=1)) if n > 1 else float("nan")
    lo, hi = sample_ci(Z)
    spectral_constant = float(np.mean(y_pos**radial.alpha))
    return CdMCResult(
        mu_hat=mu_hat,
        variance=var,
        n=n,
        runtime_seconds=float(elapsed[0]),
        ci_low=lo,
        ci_high=hi,
        extra={
            "estimator": "spectral_cdmc",
            "spectral_constant": spectral_constant,
            "alpha": radial.alpha,
        },
    )
