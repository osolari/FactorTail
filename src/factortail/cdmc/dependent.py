r"""Dependent selected-maximum CdMC (``alg:dep-cdmc``).

The estimator is

.. math::

    Z^{\mathrm{dep}}(x) = \sum_{i=1}^N p_i(T_i(x); X_{-i}),
    \qquad p_i(t; X_{-i}) = P(X_i > t \mid X_{-i}).

It is unbiased under arbitrary dependence whenever the conditional kernels
``p_i`` are evaluated exactly (Theorem ``thm:dep-cdmc-unbiased``).

Two kernel paths are supported:

- **Scalar kernel** (default): ``kernel(t: float, X_minus_i: ndarray, i: int) -> float``
  is called once per (replicate, coordinate) pair. Slow but trivial to write.
- **Batched kernel**: ``kernel_batch(t: ndarray[n], X_minus_i: ndarray[n, N-1], i: int) -> ndarray[n]``
  is called once per coordinate ``i`` and evaluates the kernel on all
  replicates at once. ≥ 10× faster for non-trivial kernels (Gaussian /
  Student-t / Clayton).
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
BatchKernelFn = Callable[
    [NDArray[np.float64], NDArray[np.float64], int],
    NDArray[np.float64],
]


def _drop_column(X: NDArray[np.float64], i: int) -> NDArray[np.float64]:
    """Return ``X`` with column ``i`` removed (single allocation)."""
    cols = list(range(X.shape[1]))
    cols.pop(i)
    return X[:, cols]


def dependent_cdmc(
    *,
    sampler: Callable[[int, np.random.Generator], NDArray[np.float64]],
    kernel: KernelFn | None = None,
    kernel_batch: BatchKernelFn | None = None,
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
        Scalar callable ``(t, X_minus_i, i) -> float``. Called once per
        (replicate, coordinate). Use for prototyping or when batching is
        not available.
    kernel_batch:
        Batched callable ``(t_array, X_minus_i_array, i) -> array``. Called
        once per coordinate; receives every replicate's value at once. When
        supplied, this is used in preference to ``kernel``.
    x:
        Threshold.
    n:
        Number of outer replicates.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    if kernel is None and kernel_batch is None:
        raise ValueError("Provide either `kernel` or `kernel_batch`")
    X = sampler(n, rng)
    if X.ndim != 2:
        raise ValueError(f"sampler must return a 2D array, got shape {X.shape}")
    n, N = X.shape
    with runtime_seconds() as elapsed:
        T = _T_values(X, x)
        Z = np.zeros(n, dtype=float)
        if kernel_batch is not None:
            for i in range(N):
                X_minus = _drop_column(X, i)
                Z += np.asarray(
                    kernel_batch(T[:, i].astype(float), X_minus, i),
                    dtype=float,
                )
        else:
            assert kernel is not None  # for mypy; the entry-point guard ensures this
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
        extra={
            "estimator": "dependent_cdmc",
            "kernel_kind": "batched" if kernel_batch is not None else "scalar",
        },
    )
