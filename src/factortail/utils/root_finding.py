r"""Root finding for VaR/quantile inversion of estimator-based survival curves.

Given an unbiased Monte Carlo estimator :math:`\hat\mu(x;\theta)` of
:math:`P(L > x)`, the VaR forecast at level :math:`\tau` is the root of
:math:`\hat\mu(x;\theta) = 1 - \tau`. We use Brent's method with logarithmic
bracketing because survival curves change by orders of magnitude across the
relevant range of ``x``.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from scipy.optimize import brentq

__all__ = ["invert_survival", "expected_shortfall_from_tail"]


def invert_survival(
    survival: Callable[[float], float],
    *,
    target: float,
    lower: float,
    upper: float,
    rtol: float = 1e-6,
    max_iter: int = 200,
) -> float:
    """Solve ``survival(x) = target`` for ``x`` on the interval ``(lower, upper)``.

    Parameters
    ----------
    survival:
        Strictly monotone non-increasing in ``x``. Must accept a scalar.
    target:
        Target survival value, ``0 < target < 1``.
    lower, upper:
        Bracketing values. The function ensures
        ``survival(lower) > target > survival(upper)``; if not, the bracket is
        doubled outward up to ``max_iter`` times.
    rtol:
        Relative tolerance for the root.
    """
    if not (0.0 < target < 1.0):
        raise ValueError("target must be in (0, 1)")
    s_lo = survival(lower)
    s_hi = survival(upper)
    expansion = 0
    while s_lo <= target and expansion < max_iter:
        lower /= 2.0
        s_lo = survival(lower)
        expansion += 1
    expansion = 0
    while s_hi >= target and expansion < max_iter:
        upper *= 2.0
        s_hi = survival(upper)
        expansion += 1
    if s_lo <= target or s_hi >= target:
        raise RuntimeError(f"Could not bracket survival = {target}: lo={s_lo}, hi={s_hi}")
    return float(brentq(lambda x: survival(x) - target, lower, upper, rtol=rtol))


def expected_shortfall_from_tail(
    survival: Callable[[float], float],
    *,
    var_level: float,
    var: float | None = None,
    lower: float = 1e-6,
    upper: float | None = None,
    n_grid: int = 64,
) -> float:
    r"""Compute :math:`\mathrm{ES}_\tau = \frac{1}{1-\tau}\int_\tau^1 \mathrm{VaR}_u\,du`
    by integrating the tail survival from the VaR level outward.

    Uses the identity
    :math:`\mathrm{ES}_\tau = \mathrm{VaR}_\tau + \frac{1}{1-\tau}\int_{\mathrm{VaR}_\tau}^\infty \overline F(x)\,dx`.

    Parameters
    ----------
    survival:
        Strictly monotone non-increasing survival function.
    var_level:
        Confidence level :math:`\tau \in (0, 1)`.
    var:
        Optional pre-computed VaR; saves a redundant root-find when the
        caller already inverted the survival curve.
    lower, upper:
        Bracketing range for the internal root-find when ``var`` is not
        supplied. ``lower`` should be small relative to the loss scale.
    """
    if var is None:
        upper_root = upper if upper is not None else max(lower * 1e6, 1e6)
        var = invert_survival(survival, target=1.0 - var_level, lower=lower, upper=upper_root)
    if upper is None:
        upper = max(var * 1000.0, var + 1.0)
    xs = np.geomspace(var, upper, n_grid)
    sf = np.array([survival(x) for x in xs])
    tail_integral = float(np.trapezoid(sf, xs))
    return float(var) + tail_integral / (1.0 - var_level)
