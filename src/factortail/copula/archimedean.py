"""Archimedean copulas: Clayton, Gumbel, Frank.

We provide sampling via the Marshall-Olkin representation when available and
expose the bivariate conditional survival ``P(U_i > t | U_j = u)``. For
``d > 2`` we expose pairwise conditional kernels via the vine-style
truncation used in the simulation harness.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

__all__ = ["ClaytonCopula", "FrankCopula", "GumbelCopula"]


@dataclass
class ClaytonCopula:
    """Clayton copula with parameter ``theta > 0``."""

    theta: float
    d: int = 2

    def __post_init__(self) -> None:
        if self.theta <= 0:
            raise ValueError("Clayton theta must be positive")

    def sample_uniform(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        # Marshall-Olkin: V ~ Gamma(1/theta, 1), then U_i = (1 - log(E_i)/V)^{-1/theta}
        V = rng.gamma(shape=1.0 / self.theta, scale=1.0, size=size)
        E = rng.exponential(size=(size, self.d))
        return (1.0 + E / V[:, None]) ** (-1.0 / self.theta)

    def conditional_survival(self, t: float, u: float) -> float:
        r"""Bivariate :math:`P(U_2 > t | U_1 = u)` for the Clayton copula."""
        theta = self.theta
        if u <= 0 or t <= 0:
            return 1.0
        ratio = u ** (-theta) - 1.0 + t ** (-theta)
        return float(1.0 - u ** (-theta - 1) * ratio ** (-(1.0 + theta) / theta))


@dataclass
class GumbelCopula:
    """Gumbel copula with parameter ``theta >= 1``."""

    theta: float
    d: int = 2

    def __post_init__(self) -> None:
        if self.theta < 1.0:
            raise ValueError("Gumbel theta must be >= 1")

    def sample_uniform(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        # Marshall-Olkin via a positive stable mixing variable.
        theta = self.theta
        if theta == 1.0:
            return rng.random(size=(size, self.d))
        # Stable(1/theta) sampler (Chambers-Mallows-Stuck).
        U = rng.random(size=size) * np.pi
        W = rng.exponential(size=size)
        alpha = 1.0 / theta
        V = (np.sin(alpha * U) / np.sin(U) ** (1.0 / alpha)) * (np.sin((1 - alpha) * U) / W) ** (
            (1 - alpha) / alpha
        )
        E = rng.exponential(size=(size, self.d))
        return np.exp(-((E / V[:, None]) ** alpha))


@dataclass
class FrankCopula:
    """Frank copula with parameter ``theta != 0``."""

    theta: float
    d: int = 2

    def __post_init__(self) -> None:
        if self.theta == 0:
            raise ValueError("Frank theta must be non-zero")

    def sample_uniform(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        if self.d != 2:
            raise NotImplementedError("Frank sampler implemented only for d=2 here")
        u1 = rng.random(size=size)
        v = rng.random(size=size)
        a = -np.expm1(-self.theta) * v / (1.0 - v * (1.0 - np.exp(-self.theta * u1)))
        u2 = -np.log1p(a * np.expm1(-self.theta * u1) / np.expm1(-self.theta)) / self.theta
        # numerical guard
        u2 = np.clip(u2, 1e-12, 1.0 - 1e-12)
        return np.column_stack([u1, u2])
