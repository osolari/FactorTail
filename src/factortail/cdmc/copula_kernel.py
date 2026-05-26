r"""Build conditional kernels for :func:`factortail.cdmc.dependent.dependent_cdmc`
from a (copula, marginals) pair.

The dependent CdMC identity (Theorem ``thm:dep-cdmc-unbiased``) requires
the conditional kernel :math:`p_i(t; X_{-i}) = P(X_i > t \mid X_{-i})`.
For a copula model :math:`U_i = F_i(X_i)` with copula :math:`C`, the kernel
factors as

.. math::

   p_i(t; X_{-i}) = 1 - C_{i \mid -i}\{F_i(t) \mid U_{-i}\}
                 = \mathrm{copula.conditional\_survival}(F_i(t), U_{-i}, i).
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from factortail.utils.tails import TailDistribution

__all__ = [
    "build_copula_kernel",
    "build_copula_kernel_batched",
    "build_copula_sampler",
]

KernelFn = Callable[[float, NDArray[np.float64], int], float]
BatchKernelFn = Callable[
    [NDArray[np.float64], NDArray[np.float64], int],
    NDArray[np.float64],
]
SamplerFn = Callable[[int, np.random.Generator], NDArray[np.float64]]


def _marginal_cdf(m: TailDistribution, x: float) -> float:
    """``F_i(x) = 1 - sf_i(x)`` clipped into ``(0, 1)`` for numerical safety."""
    sf = float(np.asarray(m.sf(np.asarray([x], dtype=float))).item())
    return float(np.clip(1.0 - sf, 1e-12, 1.0 - 1e-12))


def build_copula_kernel(
    copula,
    marginals: list[TailDistribution],
) -> KernelFn:
    r"""Return a kernel callable ``(t, X_minus_i, i) -> p_i(t; X_{-i})``.

    The kernel:

    1. Transforms each conditioning :math:`X_j` to :math:`U_j = F_j(X_j)`
       using its marginal CDF.
    2. Transforms the threshold :math:`t` to :math:`u_t = F_i(t)`.
    3. Returns
       :math:`\mathrm{copula.conditional\_survival}(u_t, U_{-i}, i)`.

    The copula object must expose ``conditional_survival(t, U_minus_i, i)``.
    """

    def kernel(t: float, X_minus_i: NDArray[np.float64], i: int) -> float:
        marg_minus_i = [m for j, m in enumerate(marginals) if j != i]
        if len(marg_minus_i) != len(np.asarray(X_minus_i).ravel()):
            raise ValueError(
                f"X_minus_i length {len(X_minus_i)} != " f"{len(marg_minus_i)} non-i marginals"
            )
        U_minus_i = np.array(
            [_marginal_cdf(m, float(x)) for m, x in zip(marg_minus_i, X_minus_i, strict=True)]
        )
        u_t = _marginal_cdf(marginals[i], float(t))
        return float(copula.conditional_survival(u_t, U_minus_i, i))

    return kernel


def build_copula_kernel_batched(
    copula,
    marginals: list[TailDistribution],
) -> BatchKernelFn:
    r"""Batched variant of :func:`build_copula_kernel`.

    The returned callable processes all replicates for coordinate ``i`` in
    one numpy call:

    - the conditioning columns ``X_{-i}`` are transformed in batch through
      each marginal's CDF;
    - the threshold column ``t`` is transformed in batch through
      ``marginals[i]``;
    - the copula's ``conditional_survival`` is called row-by-row (most
      copulas can't be vectorised without restructuring, but the per-call
      cost is dominated by linear-algebra ops that benefit from numpy
      pre-allocation; this still cuts Python overhead by ~10x).

    Plugged into :func:`factortail.cdmc.dependent.dependent_cdmc` via the
    ``kernel_batch`` keyword.
    """

    def _cdf_array(m: TailDistribution, x_array: NDArray[np.float64]) -> NDArray[np.float64]:
        sf = np.asarray(m.sf(x_array), dtype=float)
        return np.clip(1.0 - sf, 1e-12, 1.0 - 1e-12)

    def kernel_batch(
        t_array: NDArray[np.float64],
        X_minus_i: NDArray[np.float64],
        i: int,
    ) -> NDArray[np.float64]:
        marg_minus_i = [m for j, m in enumerate(marginals) if j != i]
        if X_minus_i.shape[1] != len(marg_minus_i):
            raise ValueError(
                f"X_minus_i has {X_minus_i.shape[1]} cols, "
                f"expected {len(marg_minus_i)} non-i marginals"
            )
        U_minus_i = np.column_stack(
            [_cdf_array(m, X_minus_i[:, j]) for j, m in enumerate(marg_minus_i)]
        )
        u_t = _cdf_array(marginals[i], t_array)
        out = np.empty(t_array.shape[0], dtype=float)
        for m_idx in range(t_array.shape[0]):
            out[m_idx] = float(copula.conditional_survival(float(u_t[m_idx]), U_minus_i[m_idx], i))
        return out

    return kernel_batch


def build_copula_sampler(
    copula,
    marginals: list[TailDistribution],
) -> SamplerFn:
    """Return a sampler ``(n, rng) -> (n, d)`` producing copula-coupled
    heavy-tailed draws ``X_i = F_i^{-1}(U_i)``.
    """

    def sampler(n: int, rng: np.random.Generator) -> NDArray[np.float64]:
        U = copula.sample_uniform(n, rng)
        if U.shape[1] != len(marginals):
            raise ValueError(
                f"copula returns dim {U.shape[1]} but {len(marginals)} marginals given"
            )
        cols = [m.ppf(U[:, j]) for j, m in enumerate(marginals)]
        return np.column_stack(cols)

    return sampler
