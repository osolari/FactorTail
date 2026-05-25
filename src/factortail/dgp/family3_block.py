"""Family III: block-dependent factor models (§4, §8).

Coordinates are partitioned into blocks. Inside a block, dependence is
arbitrary (we instantiate a copula or common-shock model); across blocks,
the sums are independent so that
``thm:block-reduction`` applies.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from factortail.dgp.family2_latent_shock import CommonShockModel

__all__ = ["BlockModel"]


@dataclass
class BlockModel:
    """Block-dependent model: independent block sums with within-block dependence."""

    blocks: list[CommonShockModel] = field(default_factory=list)

    @classmethod
    def from_spec(cls, spec: dict) -> BlockModel:
        return cls(blocks=[CommonShockModel.from_spec(b) for b in spec["blocks"]])

    @property
    def K(self) -> int:
        return len(self.blocks)

    @property
    def N(self) -> int:
        return sum(b.N for b in self.blocks)

    def sample(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        cols = [b.sample(size, rng) for b in self.blocks]
        return np.concatenate(cols, axis=1)

    def block_sample(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        r"""Return block sums :math:`Y_k = \\sum_{i \\in B_k} X_i`."""
        cols = [b.sample(size, rng).sum(axis=1) for b in self.blocks]
        return np.column_stack(cols)
