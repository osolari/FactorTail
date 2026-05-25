r"""Hidden-cone axis/pair mixture CdMC estimator.

Splits the rare event into an axis component and a hidden-cone component
and runs a stratified estimator with mixture probability :math:`\pi_x`.

.. math::

    Z^{\mathrm{mix}}(x)
    = \frac{\mathbf 1\{I=0\}}{\pi_x} Z_{\mathrm{axis}}(x)
    + \frac{\mathbf 1\{I=1\}}{1-\pi_x} Z_{\mathrm{hid}}(x).
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from factortail.cdmc.base import CdMCResult, sample_ci
from factortail.utils.timing import runtime_seconds

__all__ = ["hrv_mixture_estimator"]


def hrv_mixture_estimator(
    *,
    axis_estimator: Callable[[int, np.random.Generator], NDArray[np.float64]],
    hidden_estimator: Callable[[int, np.random.Generator], NDArray[np.float64]],
    pi_x: float,
    n: int,
    rng: np.random.Generator | None = None,
    seed: int | None = None,
) -> CdMCResult:
    r"""Stratified axis+hidden mixture estimator.

    Each ``estimator`` callable returns per-replicate kernel evaluations
    (length ``n``) for its component. The mixture estimator inverts the
    stratification weights, so its expectation equals the sum of component
    means.
    """
    if not (0.0 < pi_x < 1.0):
        raise ValueError("pi_x must be in (0, 1)")
    if rng is None:
        rng = np.random.default_rng(seed)
    with runtime_seconds() as elapsed:
        indicator = rng.random(n) < pi_x  # True = axis stratum
        n_axis = int(indicator.sum())
        n_hidden = n - n_axis
        Z_axis = axis_estimator(n_axis, rng) if n_axis > 0 else np.zeros(0)
        Z_hid = hidden_estimator(n_hidden, rng) if n_hidden > 0 else np.zeros(0)
        Z = np.zeros(n)
        if n_axis > 0:
            Z[indicator] = Z_axis / pi_x
        if n_hidden > 0:
            Z[~indicator] = Z_hid / (1.0 - pi_x)
        mu_hat = float(Z.mean())
        var = float(Z.var(ddof=1)) if n > 1 else float("nan")
    lo, hi = sample_ci(Z)
    return CdMCResult(
        mu_hat=mu_hat,
        variance=var,
        n=n,
        runtime_seconds=float(elapsed[0]),
        ci_low=lo,
        ci_high=hi,
        extra={
            "estimator": "hrv_mixture",
            "pi_x": pi_x,
            "axis_mean": float(Z_axis.mean()) if n_axis else 0.0,
            "hidden_mean": float(Z_hid.mean()) if n_hidden else 0.0,
        },
    )
