r"""Independent summed CdMC (§3).

The estimator is

.. math::

    Z^{\mathrm{ind}}(x) = \sum_{i=1}^N \overline F_i(T_i(x)),
    \quad T_i(x) = (x - S_{-i}) \vee M_{-i},

with deterministic envelope :math:`\sum_i \overline F_i(x/N)` and
asymptotic BRE constant :math:`N^\alpha - 1`. The implementation respects
the tie-breaking rule from ``ass:tie`` by drawing the selected-maximum
index :math:`R(X)` deterministically as the smallest argmax index.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from factortail.cdmc.base import CdMCResult, bernstein_ci
from factortail.utils.tails import TailDistribution
from factortail.utils.timing import runtime_seconds

__all__ = ["independent_cdmc", "envelope"]


def envelope(marginals: list[TailDistribution], x: float) -> float:
    r"""Deterministic envelope :math:`B(x) = \sum_i \overline F_i(x/N)`."""
    N = len(marginals)
    return float(sum(m.sf(x / N) for m in marginals))


def _T_values(
    X: NDArray[np.float64],
    x: float,
) -> NDArray[np.float64]:
    r"""Compute :math:`T_i(x) = (x - S_{-i}) \vee M_{-i}` for each replicate
    and coordinate.

    Inputs
    ------
    X : (n, N) array
    x : scalar threshold

    Returns
    -------
    T : (n, N) array
    """
    S = X.sum(axis=1, keepdims=True)
    S_minus = S - X
    # M_{-i} = max_{j != i} X_j ; computed via leave-one-out trick.
    # We sort each row once and read off the two largest values.
    n, N = X.shape
    if N == 1:
        return np.full((n, 1), x, dtype=float)
    sorted_X = np.sort(X, axis=1)
    largest = sorted_X[:, -1:]
    second = sorted_X[:, -2:-1]
    is_argmax = largest == X
    # For each row and column, M_{-i} = largest if X_i != largest, else second
    M_minus = np.where(is_argmax, second, largest)
    return np.maximum(x - S_minus, M_minus)


def independent_cdmc(
    marginals: list[TailDistribution],
    *,
    x: float,
    n: int,
    rng: np.random.Generator | None = None,
    seed: int | None = None,
    signs: NDArray[np.float64] | None = None,
) -> CdMCResult:
    r"""Run the independent summed CdMC of §3.

    Parameters
    ----------
    marginals:
        Independent margins :math:`F_i`.
    x:
        Threshold.
    n:
        Number of replicates.
    rng:
        Optional pre-seeded random generator. If ``None``, ``seed`` is used.
    seed:
        Seed for :func:`numpy.random.default_rng`.
    signs:
        Optional :math:`\pm 1` array applied per coordinate (the original
        manuscript treats both signed exposures and unsigned losses).
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    N = len(marginals)
    if signs is None:
        signs = np.ones(N)
    signs = np.asarray(signs, dtype=float)
    # Sample positive-signed coordinates only (negative-signed coordinates
    # contribute to the left tail; the right-tail probability uses the
    # absolute coordinate with reversed sign convention).
    X = np.column_stack([m.rvs(n, rng) for m in marginals]) * signs[None, :]
    with runtime_seconds() as elapsed:
        T = _T_values(X, x)
        kernel = np.column_stack([m.sf(T[:, i]) for i, m in enumerate(marginals)])
        # Only coordinates with positive sign contribute the right-tail kernel.
        kernel = kernel * (signs[None, :] > 0)
        Z = kernel.sum(axis=1)
        mu_hat = float(Z.mean())
        var = float(Z.var(ddof=1)) if n > 1 else float("nan")
    B = envelope(marginals, x)
    lo, hi = bernstein_ci(Z, envelope=B, alpha=0.05)
    return CdMCResult(
        mu_hat=mu_hat,
        variance=var,
        n=n,
        runtime_seconds=float(elapsed[0]),
        ci_low=lo,
        ci_high=hi,
        extra={
            "envelope": B,
            "rel_envelope": B / mu_hat if mu_hat > 0 else float("inf"),
            "estimator": "independent_cdmc",
        },
    )
