r"""Family I: independent i.n.i.d. tails (§8).

Generates :math:`X_1,\dots,X_N` with mutually independent heavy-tailed
margins of possibly unequal tail indices, scales, signed exposures, and
inactive components. Targets the verification of the maximum constant
``thm:catastrophe-exact``, the sum constant ``thm:sum-equivalence``, the
BRE bound ``N^alpha - 1`` from §3, and the second-order expansion
``thm:second-order``.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from factortail.utils.tails import TailDistribution, build_marginal

__all__ = ["IndependentINID"]


@dataclass
class IndependentINID:
    """Independent inid family with signed exposures."""

    marginals: list[TailDistribution]
    signs: NDArray[np.float64]

    @classmethod
    def from_specs(cls, specs: Iterable[dict]) -> IndependentINID:
        ms: list[TailDistribution] = []
        signs: list[float] = []
        for sp in specs:
            sp = dict(sp)
            sign = float(sp.pop("sign", 1.0))
            ms.append(build_marginal(sp))
            signs.append(sign)
        return cls(marginals=ms, signs=np.asarray(signs, dtype=float))

    @property
    def N(self) -> int:
        return len(self.marginals)

    def sample(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        X = np.column_stack([m.rvs(size, rng) for m in self.marginals])
        return X * self.signs[None, :]

    def sum_sample(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        return self.sample(size, rng).sum(axis=1)

    def tail_constants(self) -> NDArray[np.float64]:
        return np.array(
            [m.c if s > 0 else 0.0 for m, s in zip(self.marginals, self.signs, strict=True)]
        )
