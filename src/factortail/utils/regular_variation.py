"""Regular variation tools: closed-form sum tails for benchmark distributions.

The simulation study (Section 8) needs a high-precision reference
``P(S_N > x)`` against which Monte Carlo estimators are compared. For the
Pareto and Lomax families, exact or near-exact tail probabilities are
available via convolution arguments and numerical integration.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from factortail.utils.tails import TailDistribution

__all__ = [
    "first_order_sum_tail",
    "second_order_sum_tail",
    "reference_sum_tail",
]


def first_order_sum_tail(
    marginals: list[TailDistribution],
    x: ArrayLike,
) -> NDArray[np.float64]:
    r"""First-order independent sum-tail approximation: ``sum_i P(X_i > x)``.

    Implements :math:`P(S_N > x) \sim \sum_i \overline F_i(x)` from
    :math:`\textrm{Theorem }` ``thm:sum-equivalence``.
    """
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x, dtype=float)
    for m in marginals:
        out = out + m.sf(x)
    return out


def second_order_sum_tail(
    marginals: list[TailDistribution],
    x: ArrayLike,
    *,
    means: list[float] | None = None,
) -> NDArray[np.float64]:
    r"""Corrected second-order independent expansion.

    Implements :math:`\textrm{Theorem }` ``thm:second-order``: adds the
    mean-shift correction :math:`\alpha \overline G(x)/x \sum_i c_i \mu_{-i}`
    to the first-order term, using equal-index Pareto reference
    :math:`\overline G(x)=x^{-\alpha}`.
    """
    x = np.asarray(x, dtype=float)
    if not marginals:
        return np.zeros_like(x)
    alpha = marginals[0].alpha
    if not all(np.isclose(m.alpha, alpha) for m in marginals):
        # Heterogeneous tail indices: fall back to first order (no closed-form
        # second-order in this paper for unequal alphas).
        return first_order_sum_tail(marginals, x)
    if means is None:
        means = [getattr(m, "mean", lambda: 0.0)() for m in marginals]
    means_arr = np.array([m if np.isfinite(m) else 0.0 for m in means], dtype=float)
    c = np.array([m.c for m in marginals], dtype=float)
    first = first_order_sum_tail(marginals, x)
    # \sum_i c_i \mu_{-i} = (\sum_i c_i)(\sum_j mu_j) - \sum_i c_i mu_i
    total_c = c.sum()
    total_mu = means_arr.sum()
    cross = total_c * total_mu - float(np.dot(c, means_arr))
    # Reference scale ``\overline G(x) = x^{-alpha}``.
    g = np.where(x > 0, x ** (-alpha), 1.0)
    correction = alpha * g / np.where(x > 0, x, 1.0) * cross
    return first + correction


def reference_sum_tail(
    marginals: list[TailDistribution],
    x: ArrayLike,
    *,
    n_samples: int = 1_000_000,
    seed: int = 0,
) -> NDArray[np.float64]:
    """Monte Carlo reference for ``P(S_N > x)``.

    This is a deliberately *crude* importance-free estimator used only for
    cross-checking the closed-form approximations at moderate ``x``. For deep
    tails the CdMC estimators in :mod:`factortail.cdmc` are far more accurate.
    """
    rng = np.random.default_rng(seed)
    x = np.atleast_1d(np.asarray(x, dtype=float))
    samples = np.zeros(n_samples, dtype=float)
    for m in marginals:
        samples += m.rvs(n_samples, rng)
    return np.array([(samples > xi).mean() for xi in x])
