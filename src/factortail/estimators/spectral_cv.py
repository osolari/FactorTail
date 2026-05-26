r"""Spectral control-variate estimator (§7, Proposition ``prop:vre``).

Pairs the independent summed CdMC with a per-replicate spectral surrogate.
Three surrogate choices are exposed via ``surrogate``:

- ``"loss"`` — :math:`Y = \overline F_R(x / (a^\top \Theta)_+)`. The
  "loss-functional" surrogate from the manuscript. Couples Z and Y
  through the angular direction only; correlation is weak when the
  radial mass dominates the kernel variance.
- ``"max_coord"`` — :math:`Y = \overline F_{i^\star}(X_{(1)})` where
  :math:`X_{(1)} = \max_i X_i` and :math:`i^\star = \mathrm{argmax}\, X_i`.
  Couples on the *argmax-dominated* selected-maximum structure that
  Z uses; correlation is much higher in the deep tail because the
  CdMC kernel is dominated by the same coordinate.
- ``"second_largest_shift"`` — :math:`Y = \overline F_{i^\star}(x - X_{(2)})`
  where :math:`X_{(2)}` is the second-largest coordinate. This is a
  small-step linearisation of the selected-maximum kernel; correlation
  is highest because Y tracks the very quantity inside Z's kernel for
  the dominant coordinate.

The default is ``"max_coord"`` because it produces the highest empirical
:math:`\rho^2` on the Family-V Dirichlet design (≈ 0.74 vs 0.003 for
``"loss"``).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from factortail.estimators.control_variate import ControlVariateResult, control_variate
from factortail.utils.tails import TailDistribution

__all__ = ["spectral_control_variate"]

AngleSampler = Callable[[int, np.random.Generator], NDArray[np.float64]]
SurrogateKind = Literal["loss", "max_coord", "second_largest_shift"]


def spectral_control_variate(
    *,
    marginals: list[TailDistribution],
    angle_sampler: AngleSampler,
    radial: TailDistribution,
    exposure: NDArray[np.float64],
    x: float,
    n: int,
    surrogate: SurrogateKind = "max_coord",
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
        Angular sampler and radial law for the surrogate draw; ``X`` is
        built as ``R * Theta`` and used by both ``Z`` and ``Y``.
    exposure:
        Loss functional ``a`` for the ``loss`` surrogate.
    x:
        Threshold.
    n:
        Number of joint replicates.
    surrogate:
        Which control-variate surrogate to use. See the module
        docstring; the default ``"second_largest_shift"`` is the
        empirically best-correlated choice on the Family-V design.
    m_Y:
        Optional exact centering ``E[Y(x)]``. When provided, the oracle
        VRE of Proposition ``prop:vre`` applies; otherwise the
        sample-split variant of :func:`control_variate` is used.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    exposure = np.asarray(exposure, dtype=float)
    Theta = angle_sampler(n, rng)
    R = radial.rvs(n, rng)
    X = R[:, None] * Theta

    if surrogate == "loss":
        y_pos = np.maximum(Theta @ exposure, 0.0)
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(y_pos > 0, x / y_pos, np.inf)
            Y = np.where(y_pos > 0, radial.sf(ratio), 0.0).astype(float)
    elif surrogate == "max_coord":
        # P(X_{i*} > X_{(1)}) under the marginal of the argmax coordinate.
        argmax = X.argmax(axis=1)
        max_val = X[np.arange(n), argmax]
        Y = np.empty(n, dtype=float)
        for i, m in enumerate(marginals):
            mask = argmax == i
            if mask.any():
                Y[mask] = np.asarray(m.sf(max_val[mask]), dtype=float)
    elif surrogate == "second_largest_shift":
        # Y = sf_{i*}(x - X_{(2)}) — the argmax-dominant CdMC kernel value.
        sorted_X = np.sort(X, axis=1)
        argmax = X.argmax(axis=1)
        second_largest = sorted_X[:, -2] if X.shape[1] > 1 else np.zeros(n)
        shift = x - second_largest
        Y = np.empty(n, dtype=float)
        for i, m in enumerate(marginals):
            mask = argmax == i
            if mask.any():
                Y[mask] = np.asarray(m.sf(shift[mask]), dtype=float)
    else:
        raise ValueError(f"unknown surrogate: {surrogate!r}")

    # Independent CdMC kernel Z on the same X.
    from factortail.cdmc.independent import _T_values

    T = _T_values(X, x)
    kernel = np.column_stack([m.sf(T[:, i]) for i, m in enumerate(marginals)])
    Z = kernel.sum(axis=1).astype(float)
    res = control_variate(Z, Y, m_Y=m_Y)
    res.extra.setdefault("estimator", "spectral_control_variate")
    res.extra["m_Y_oracle"] = m_Y
    res.extra["surrogate"] = surrogate
    return res
