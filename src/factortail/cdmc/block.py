r"""Block CdMC (§4, Theorem ``thm:block-reduction``).

Given a block partition with independent block sums :math:`Y_k`, run
independent summed CdMC on the block sums. We treat the block tail
:math:`P(Y_k > t)` either via a known closed-form (when each block is a
common-shock model) or via a nested-MC reference estimator.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from factortail.cdmc.base import CdMCResult, sample_ci
from factortail.cdmc.independent import _T_values
from factortail.utils.timing import runtime_seconds

__all__ = ["block_cdmc"]

BlockSampler = Callable[[int, np.random.Generator], NDArray[np.float64]]
BlockTail = Callable[[float, int], float]


def block_cdmc(
    *,
    block_sampler: BlockSampler,
    block_tail: BlockTail,
    K: int,
    x: float,
    n: int,
    rng: np.random.Generator | None = None,
    seed: int | None = None,
) -> CdMCResult:
    r"""Run block CdMC on independent block sums.

    Parameters
    ----------
    block_sampler:
        Function ``(n, rng) -> (n, K)`` returning a matrix of block sums.
    block_tail:
        Callable ``(t, k) -> P(Y_k > t)`` returning the tail of block ``k``
        at threshold ``t`` (this is the analog of :math:`\overline F_i` for
        the independent estimator).
    K:
        Number of blocks.
    x:
        Threshold.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    Y = block_sampler(n, rng)
    if Y.shape != (n, K):
        raise ValueError(f"block_sampler returned shape {Y.shape}; expected ({n},{K})")
    with runtime_seconds() as elapsed:
        T = _T_values(Y, x)
        kernel = np.zeros_like(Y)
        for k in range(K):
            for m in range(n):
                kernel[m, k] = block_tail(float(T[m, k]), k)
        Z = kernel.sum(axis=1)
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
        extra={"estimator": "block_cdmc", "n_blocks": K},
    )
