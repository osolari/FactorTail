"""Family VI: hidden-regular-variation models (§6, §8).

We construct mixtures that are asymptotically independent at first order
(spectral mass on coordinate axes) but possess hidden mass on pair cones at
a slower scale ``H_2(x) ~ x^{-alpha_2}`` with ``alpha_2 >= alpha``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from factortail.utils.tails import ParetoTail

__all__ = ["HiddenConeMixture"]


@dataclass
class HiddenConeMixture:
    r"""Axis + hidden-pair mixture.

    With probability ``1 - p`` we draw an axis-supported vector :math:`R e_i`
    with :math:`R \\sim \\mathrm{Pareto}(\\alpha)`; with probability ``p`` we
    draw a pair-supported vector with both coordinates extreme but with
    radial index :math:`\\alpha_2 \\ge \\alpha` so the joint tail mass lives at
    a slower scale than the axis tail.
    """

    alpha: float
    alpha_hidden: float
    hidden_prob: float
    dim: int
    pair_indices: list[tuple[int, int]]
    pair_weights: NDArray[np.float64] | None = None

    def __post_init__(self) -> None:
        if not (0.0 <= self.hidden_prob < 1.0):
            raise ValueError("hidden_prob must lie in [0, 1)")
        if self.alpha_hidden < self.alpha:
            raise ValueError("alpha_hidden must be >= alpha")
        if not self.pair_indices:
            raise ValueError("pair_indices required")
        for i, j in self.pair_indices:
            if i == j or i < 0 or j < 0 or i >= self.dim or j >= self.dim:
                raise ValueError(f"invalid pair ({i},{j})")
        if self.pair_weights is None:
            self.pair_weights = np.ones(len(self.pair_indices)) / len(self.pair_indices)
        else:
            self.pair_weights = np.asarray(self.pair_weights, dtype=float)
            self.pair_weights = self.pair_weights / self.pair_weights.sum()
        self._axis_radial = ParetoTail(alpha=self.alpha)
        self._hidden_radial = ParetoTail(alpha=self.alpha_hidden)

    @classmethod
    def from_spec(cls, spec: dict) -> HiddenConeMixture:
        return cls(**spec)

    def sample(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        X = np.zeros((size, self.dim))
        is_hidden = rng.random(size) < self.hidden_prob
        n_hidden = int(is_hidden.sum())
        n_axis = size - n_hidden
        # Axis component
        if n_axis:
            r_axis = self._axis_radial.rvs(n_axis, rng)
            idx = rng.integers(0, self.dim, size=n_axis)
            rows = np.where(~is_hidden)[0]
            X[rows, idx] = r_axis
        # Hidden-pair component
        if n_hidden:
            r_hidden = self._hidden_radial.rvs(n_hidden, rng)
            pair_idx = rng.choice(len(self.pair_indices), size=n_hidden, p=self.pair_weights)
            # Equal split across pair coordinates with Dirichlet jitter to spread mass
            jitter = rng.dirichlet(np.array([2.0, 2.0]), size=n_hidden)
            rows = np.where(is_hidden)[0]
            for k, (row, pidx) in enumerate(zip(rows, pair_idx, strict=True)):
                i, j = self.pair_indices[pidx]
                X[row, i] = r_hidden[k] * jitter[k, 0]
                X[row, j] = r_hidden[k] * jitter[k, 1]
        return X
