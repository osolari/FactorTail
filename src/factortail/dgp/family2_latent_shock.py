"""Family II: common-shock and latent-shock factor models (§4, §8).

Implements two specializations of :math:`X = BZ + E`:

* :class:`CommonShockModel`: scalar shock ``Z_0`` with loadings ``b_i`` plus
  idiosyncratic noise (Example ``ex:common-shock``).
* :class:`LatentFactorModel`: general factor matrix ``B`` and independent
  shock vector ``Z`` (Theorem ``thm:latent-shock-tail``).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from factortail.utils.tails import TailDistribution, build_marginal

__all__ = ["CommonShockModel", "LatentFactorModel"]


@dataclass
class CommonShockModel:
    """Single common shock plus idiosyncratic heavy-tailed noise."""

    loadings: NDArray[np.float64]
    shock: TailDistribution
    idiosyncratic: list[TailDistribution]

    def __post_init__(self) -> None:
        self.loadings = np.asarray(self.loadings, dtype=float)
        if self.loadings.shape[0] != len(self.idiosyncratic):
            raise ValueError("loadings and idiosyncratic margins must agree in length")

    @classmethod
    def from_spec(cls, spec: dict) -> CommonShockModel:
        return cls(
            loadings=np.asarray(spec["loadings"], dtype=float),
            shock=build_marginal(spec["shock"]),
            idiosyncratic=[build_marginal(s) for s in spec["idiosyncratic"]],
        )

    @property
    def N(self) -> int:
        return int(self.loadings.shape[0])

    def sample(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        Z0 = self.shock.rvs(size, rng)
        E = np.column_stack([m.rvs(size, rng) for m in self.idiosyncratic])
        return self.loadings[None, :] * Z0[:, None] + E

    def latent_constants(self) -> dict[str, float]:
        r"""Return the latent-shock first-order constant of Theorem
        ``thm:latent-shock-tail`` for the sum functional ``a = 1``.

        Constants are returned for both the correct latent-shock attribution
        and the misspecified observed-coordinate attribution
        (Example ``ex:common-shock``).
        """
        alpha = self.shock.alpha
        # Correct: (sum_i b_i)_+^alpha * c_shock + sum_i c_i (idio)
        sum_b = float(self.loadings.sum())
        sum_b_pos = max(sum_b, 0.0) ** alpha * self.shock.c
        idio_total = float(sum(m.c for m in self.idiosyncratic))
        correct = sum_b_pos + idio_total
        # Misspecified observed-coordinate independence: sum_i (b_i)_+^alpha c_shock + idio
        misspec = (
            float(sum(max(b, 0.0) ** alpha for b in self.loadings) * self.shock.c) + idio_total
        )
        return {"correct_latent_constant": correct, "misspecified_observed_constant": misspec}


@dataclass
class LatentFactorModel:
    """General latent-shock factor model :math:`X = B Z + E`."""

    B: NDArray[np.float64]
    shocks: list[TailDistribution]
    idiosyncratic: list[TailDistribution]

    def __post_init__(self) -> None:
        self.B = np.asarray(self.B, dtype=float)
        if self.B.shape[1] != len(self.shocks):
            raise ValueError("B columns must match number of shocks")
        if self.B.shape[0] != len(self.idiosyncratic):
            raise ValueError("B rows must match idiosyncratic count")

    @classmethod
    def from_spec(cls, spec: dict) -> LatentFactorModel:
        return cls(
            B=np.asarray(spec["B"], dtype=float),
            shocks=[build_marginal(s) for s in spec["shocks"]],
            idiosyncratic=[build_marginal(s) for s in spec["idiosyncratic"]],
        )

    @property
    def N(self) -> int:
        return int(self.B.shape[0])

    @property
    def K(self) -> int:
        return int(self.B.shape[1])

    def sample(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        Z = np.column_stack([m.rvs(size, rng) for m in self.shocks])
        E = np.column_stack([m.rvs(size, rng) for m in self.idiosyncratic])
        return Z @ self.B.T + E

    def latent_tail_constant(self, exposure: NDArray[np.float64]) -> float:
        r"""Compute the latent-shock tail constant for loss ``L = a^T X``.

        Implements
        :math:`c_k(q_k) = |q_k|^\alpha [p_k^+ \mathbf 1\{q_k>0\} + p_k^-\mathbf 1\{q_k<0\}]`
        with :math:`p_k^- = 0` for one-sided heavy tails.
        """
        q = self.B.T @ np.asarray(exposure, dtype=float)
        constant = 0.0
        for k, sh in enumerate(self.shocks):
            constant += abs(q[k]) ** sh.alpha * sh.c * (q[k] > 0)
        # Idiosyncratic axis contributions.
        constant += float(sum(m.c * (exposure[i] > 0) for i, m in enumerate(self.idiosyncratic)))
        return constant
