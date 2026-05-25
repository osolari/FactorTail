r"""Method-correctness tests for ``fit_block_tail`` and the block CdMC."""

from __future__ import annotations

import numpy as np

from factortail.cdmc import block_cdmc, fit_block_tail
from factortail.dgp import BlockModel, CommonShockModel
from factortail.utils.tails import LomaxTail, ParetoTail


def _build_two_block_model():
    return BlockModel(
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


class TestFitBlockTail:
    def test_closed_form_matches_simulation_in_deep_tail(self):
        bm = _build_two_block_model()
        tail = fit_block_tail(bm, method="closed_form")
        # At a very deep threshold, P(Y_k > x) ~ c_k * x^-alpha; the closed
        # form must agree with a high-budget crude MC reference.
        rng = np.random.default_rng(0)
        for k in range(bm.K):
            n_ref = 200_000
            Y_ref = bm.blocks[k].sample(n_ref, rng).sum(axis=1)
            x = 50.0  # deep tail
            emp = float((Y_ref > x).mean())
            se = float(np.sqrt(emp * (1 - emp) / n_ref))
            theo = tail(x, k)
            assert abs(theo - emp) < 5 * se + 0.1 * emp

    def test_nested_mc_decreases_in_t(self):
        bm = _build_two_block_model()
        tail = fit_block_tail(bm, method="nested_mc", n_ref=20_000, seed=1)
        ts = [1.0, 3.0, 10.0, 30.0]
        for k in range(bm.K):
            vals = [tail(t, k) for t in ts]
            assert all(vals[i] >= vals[i + 1] for i in range(len(vals) - 1))


class TestBlockCdMC:
    def test_block_cdmc_unbiased_with_closed_form_tail(self):
        bm = _build_two_block_model()
        tail = fit_block_tail(bm, method="closed_form")
        res = block_cdmc(
            block_sampler=lambda n, r: bm.block_sample(n, r),
            block_tail=tail,
            K=bm.K,
            x=20.0,
            n=5000,
            seed=0,
        )
        rng = np.random.default_rng(0)
        Y = bm.block_sample(80_000, rng)
        emp = float((Y.sum(axis=1) > 20.0).mean())
        se = float(np.sqrt(emp * (1 - emp) / 80_000))
        cdmc_se = float(np.sqrt(res.variance / res.n))
        assert abs(res.mu_hat - emp) < 6 * (cdmc_se + se)
