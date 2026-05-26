r"""Method-correctness: batched kernels must produce the same numerical
output as the scalar kernel they accelerate."""

from __future__ import annotations

import numpy as np
import pytest

from factortail.cdmc import (
    block_cdmc,
    build_copula_kernel,
    build_copula_kernel_batched,
    build_copula_sampler,
    dependent_cdmc,
    fit_block_tail,
)
from factortail.copula import ClaytonCopula
from factortail.dgp import BlockModel, CommonShockModel
from factortail.utils.tails import LomaxTail, ParetoTail


class TestDependentCdMCBatch:
    def test_clayton_batched_matches_scalar(self):
        marginals = [ParetoTail(alpha=2.0, scale=1.0)] * 3
        cop = ClaytonCopula(theta=2.0, d=3)
        sampler = build_copula_sampler(cop, marginals)
        scalar_kernel = build_copula_kernel(cop, marginals)
        batch_kernel = build_copula_kernel_batched(cop, marginals)

        res_scalar = dependent_cdmc(sampler=sampler, kernel=scalar_kernel, x=10.0, n=500, seed=42)
        res_batch = dependent_cdmc(
            sampler=sampler, kernel_batch=batch_kernel, x=10.0, n=500, seed=42
        )
        # The two paths consume the same RNG sequence (sampler is deterministic
        # given seed), so mu_hat / variance must agree up to floating noise.
        assert res_scalar.mu_hat == pytest.approx(res_batch.mu_hat, rel=1e-10)
        assert res_scalar.variance == pytest.approx(res_batch.variance, rel=1e-10)
        assert res_batch.extra["kernel_kind"] == "batched"
        assert res_scalar.extra["kernel_kind"] == "scalar"

    def test_either_kernel_required(self):
        with pytest.raises(ValueError):
            dependent_cdmc(
                sampler=lambda n, r: np.zeros((n, 2)),
                x=1.0,
                n=10,
                seed=0,
            )


class TestBlockCdMCBatch:
    def test_batched_matches_scalar(self):
        bm = BlockModel(
            blocks=[
                CommonShockModel(
                    loadings=np.array([1.0, 1.0]),
                    shock=ParetoTail(alpha=2.0, scale=1.0),
                    idiosyncratic=[LomaxTail(alpha=2.0, scale=0.1)] * 2,
                ),
                CommonShockModel(
                    loadings=np.array([0.8, 0.6]),
                    shock=ParetoTail(alpha=2.0, scale=1.0),
                    idiosyncratic=[LomaxTail(alpha=2.0, scale=0.1)] * 2,
                ),
            ]
        )
        scalar_tail = fit_block_tail(bm, method="closed_form")

        def batch_tail(t_arr: np.ndarray, k: int) -> np.ndarray:
            return np.array([scalar_tail(float(t), k) for t in t_arr], dtype=float)

        res_scalar = block_cdmc(
            block_sampler=lambda n, r: bm.block_sample(n, r),
            block_tail=scalar_tail,
            K=bm.K,
            x=15.0,
            n=2000,
            seed=0,
        )
        res_batch = block_cdmc(
            block_sampler=lambda n, r: bm.block_sample(n, r),
            block_tail_batch=batch_tail,
            K=bm.K,
            x=15.0,
            n=2000,
            seed=0,
        )
        assert res_scalar.mu_hat == pytest.approx(res_batch.mu_hat, rel=1e-12)
        assert res_scalar.variance == pytest.approx(res_batch.variance, rel=1e-12)

    def test_either_tail_required(self):
        with pytest.raises(ValueError):
            block_cdmc(
                block_sampler=lambda n, r: np.zeros((n, 2)),
                K=2,
                x=1.0,
                n=10,
                seed=0,
            )
