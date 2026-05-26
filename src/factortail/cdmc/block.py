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

__all__ = ["block_cdmc", "fit_block_tail"]

BlockSampler = Callable[[int, np.random.Generator], NDArray[np.float64]]
BlockTail = Callable[[float, int], float]
BlockTailBatch = Callable[[NDArray[np.float64], int], NDArray[np.float64]]


def block_cdmc(
    *,
    block_sampler: BlockSampler,
    block_tail: BlockTail | None = None,
    block_tail_batch: BlockTailBatch | None = None,
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
        Scalar callable ``(t, k) -> P(Y_k > t)``. Used when
        ``block_tail_batch`` is ``None``.
    block_tail_batch:
        Batched callable ``(t_array, k) -> P(Y_k > t_array)``. Preferred when
        the block tail can be evaluated vectorised.
    K:
        Number of blocks.
    x:
        Threshold.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    if block_tail is None and block_tail_batch is None:
        raise ValueError("Provide either `block_tail` or `block_tail_batch`")
    Y = block_sampler(n, rng)
    if Y.shape != (n, K):
        raise ValueError(f"block_sampler returned shape {Y.shape}; expected ({n},{K})")
    with runtime_seconds() as elapsed:
        T = _T_values(Y, x)
        kernel = np.zeros_like(Y, dtype=float)
        if block_tail_batch is not None:
            for k in range(K):
                kernel[:, k] = np.asarray(block_tail_batch(T[:, k].astype(float), k), dtype=float)
        else:
            assert block_tail is not None  # for mypy; entry-point guard ensures this
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
        extra={
            "estimator": "block_cdmc",
            "n_blocks": K,
            "kernel_kind": "batched" if block_tail_batch is not None else "scalar",
        },
    )


def fit_block_tail(
    block_model,
    *,
    method: str = "auto",
    n_ref: int = 200_000,
    rng: np.random.Generator | None = None,
    seed: int | None = None,
) -> BlockTail:
    r"""Construct a ``block_tail(t, k)`` callable for ``block_cdmc``.

    Parameters
    ----------
    block_model:
        Must expose ``.blocks: list``. Each block ``b`` may either
        (i) expose ``latent_constants()`` (a common-shock block) and a tail
        index ``b.shock.alpha`` for a closed-form Pareto tail, or
        (ii) be sampled via ``b.sample(size, rng).sum(axis=1)`` for a
        high-budget nested-MC reference.
    method:
        ``"auto"`` (default) picks closed-form when available else nested MC;
        ``"closed_form"`` requires every block to expose
        ``latent_constants()``;
        ``"nested_mc"`` always uses nested MC.
    n_ref:
        Sample size for the nested-MC reference per block.
    """
    if not hasattr(block_model, "blocks"):
        raise TypeError("block_model must expose a `.blocks` attribute")
    blocks = block_model.blocks
    if rng is None:
        rng = np.random.default_rng(seed)

    closed: list[tuple[float, float] | None] = []
    for b in blocks:
        if method in ("closed_form", "auto") and hasattr(b, "latent_constants"):
            const = b.latent_constants()["correct_latent_constant"]
            alpha = float(b.shock.alpha)
            closed.append((alpha, float(const)))
        else:
            closed.append(None)
    if method == "closed_form" and any(c is None for c in closed):
        raise ValueError("`closed_form` requested but not every block exposes latent_constants()")

    # For blocks without closed form, precompute a high-budget empirical
    # survival on a log-spaced grid for fast interpolation.
    empirical: list[tuple[NDArray[np.float64], NDArray[np.float64]] | None] = []
    for k, b in enumerate(blocks):
        if closed[k] is not None and method != "nested_mc":
            empirical.append(None)
            continue
        Y_ref = b.sample(n_ref, rng).sum(axis=1)
        sorted_Y = np.sort(Y_ref)
        # Survival function values at sorted points
        ranks = np.arange(n_ref, 0, -1) / n_ref
        empirical.append((sorted_Y, ranks))

    def block_tail(t: float, k: int) -> float:
        closed_k = closed[k]
        if closed_k is not None and method != "nested_mc":
            alpha, c = closed_k
            return float(c * max(t, 1e-300) ** (-alpha))
        emp_k = empirical[k]
        assert emp_k is not None  # mypy: method != "nested_mc" path ruled out above
        sorted_Y, ranks = emp_k
        # Linearly interpolate the empirical survival.
        idx = int(np.searchsorted(sorted_Y, t, side="left"))
        if idx >= len(sorted_Y):
            return 1.0 / n_ref  # below floor
        return float(ranks[idx])

    return block_tail
