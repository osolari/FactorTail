r"""Dependent selected-maximum CdMC (``alg:dep-cdmc``).

The estimator is

.. math::

    Z^{\mathrm{dep}}(x) = \sum_{i=1}^N p_i(T_i(x); X_{-i}),
    \qquad p_i(t; X_{-i}) = P(X_i > t \mid X_{-i}).

It is unbiased under arbitrary dependence whenever the conditional kernels
``p_i`` are evaluated exactly (Theorem ``thm:dep-cdmc-unbiased``).
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from factortail.cdmc.base import CdMCResult, sample_ci
from factortail.cdmc.independent import _T_values
from factortail.utils.timing import runtime_seconds

__all__ = ["dependent_cdmc"]

KernelFn = Callable[[float, NDArray[np.float64], int], float]


def dependent_cdmc(
    *,
    sampler: Callable[[int, np.random.Generator], NDArray[np.float64]],
    kernel: KernelFn,
    x: float,
    n: int,
    rng: np.random.Generator | None = None,
    seed: int | None = None,
) -> CdMCResult:
    r"""Algorithm ``alg:dep-cdmc``.

    Parameters
    ----------
    sampler:
        Function ``(n, rng) -> X`` returning an :math:`n \times N` matrix of
        joint draws from the fitted model.
    kernel:
        Callable computing :math:`p_i(t; X_{-i})` for replicate-specific
        :math:`X_{-i}`. Signature ``(t, X_minus_i, i) -> float``.
    x:
        Threshold.
    n:
        Number of outer replicates.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    X = sampler(n, rng)
    if X.ndim != 2:
        raise ValueError(f"sampler must return a 2D array, got shape {X.shape}")
    n, N = X.shape
    with runtime_seconds() as elapsed:
        T = _T_values(X, x)
        Z = np.zeros(n)
        for m in range(n):
            row = X[m]
            t_row = T[m]
            total = 0.0
            for i in range(N):
                X_minus = np.delete(row, i)
                total += kernel(t_row[i], X_minus, i)
            Z[m] = total
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
        extra={"estimator": "dependent_cdmc"},
    )
