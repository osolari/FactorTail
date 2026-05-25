r"""Spectral control-variate estimator (§7, Proposition ``prop:vre``).

Pairs the independent summed CdMC with a spectral surrogate as a control
variate. The two estimators are coupled at the sample level: each
replicate samples a *single* radial-angular draw ``(R, Theta)``, builds
``X = R * Theta``, and evaluates both the independent CdMC kernel
``Z = sum_i sf_i(T_i(X))`` and the spectral surrogate
``Y = sf_R(x / (a^T Theta)_+)`` on that single draw. With Pareto-radial /
axis-angular alignment, ``corr(Z, Y) -> 1`` and the control-variate
identity drives variance to zero (Proposition ``prop:vre`` part 1).
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from factortail.estimators.control_variate import ControlVariateResult, control_variate
from factortail.utils.tails import TailDistribution

__all__ = ["spectral_control_variate"]

AngleSampler = Callable[[int, np.random.Generator], NDArray[np.float64]]


def spectral_control_variate(
    *,
    marginals: list[TailDistribution],
    angle_sampler: AngleSampler,
    radial: TailDistribution,
    exposure: NDArray[np.float64],
    x: float,
    n: int,
    m_Y: float | None = None,
    rng: np.random.Generator | None = None,
    seed: int | None = None,
) -> ControlVariateResult:
    r"""Coupled spectral CV pairing.

    Parameters
    ----------
    marginals:
        Independent margins for the ``Z`` kernel ``sum_i sf_i(T_i(X))``.
    angle_sampler, radial:
        Angular sampler and radial law for the ``Y`` surrogate; ``X`` is
        built as ``R * Theta`` and used by both ``Z`` and ``Y``.
    exposure:
        Loss functional ``a`` for the spectral surrogate.
    x:
        Threshold.
    n:
        Number of joint replicates.
    m_Y:
        Optional exact centering ``E[Y(x)]``. When provided, the oracle VRE
        of Proposition ``prop:vre`` applies; otherwise the sample-split
        variant of :func:`control_variate` is used.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    exposure = np.asarray(exposure, dtype=float)
    Theta = angle_sampler(n, rng)
    R = radial.rvs(n, rng)
    X = R[:, None] * Theta
    # Spectral surrogate Y on the coupled draw.
    y_pos = np.maximum(Theta @ exposure, 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(y_pos > 0, x / y_pos, np.inf)
        Y = np.where(y_pos > 0, radial.sf(ratio), 0.0).astype(float)
    # Independent CdMC kernel Z on the same X.
    from factortail.cdmc.independent import _T_values

    T = _T_values(X, x)
    kernel = np.column_stack([m.sf(T[:, i]) for i, m in enumerate(marginals)])
    Z = kernel.sum(axis=1).astype(float)
    res = control_variate(Z, Y, m_Y=m_Y)
    res.extra.setdefault("estimator", "spectral_control_variate")
    res.extra["m_Y_oracle"] = m_Y
    return res
