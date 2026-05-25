"""Family V: multivariate-regular-variation models (§5, §8).

The radial component is exact Pareto and the angular component is supplied
as either an analytic distribution on the simplex (logistic / max-stable),
an axis-concentrated mixture, or empirical resampling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from factortail.utils.tails import ParetoTail

__all__ = ["RadialAngularMRV"]

AngularKind = Literal["axis", "ray_mixture", "dirichlet", "empirical"]


@dataclass
class RadialAngularMRV:
    r"""Radial-angular MRV model :math:`X = R \\Theta`."""

    alpha: float
    angular_kind: AngularKind = "dirichlet"
    angular_params: dict | None = None
    radial_scale: float = 1.0
    dim: int = 3

    def __post_init__(self) -> None:
        if self.alpha <= 0:
            raise ValueError("alpha must be positive")
        if self.angular_kind not in ("axis", "ray_mixture", "dirichlet", "empirical"):
            raise ValueError(f"Unknown angular kind: {self.angular_kind!r}")
        if self.angular_params is None:
            self.angular_params = {}
        self._radial = ParetoTail(alpha=self.alpha, scale=self.radial_scale)

    @classmethod
    def from_spec(cls, spec: dict) -> RadialAngularMRV:
        return cls(**spec)

    def sample_angles(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        if self.angular_kind == "axis":
            weights = np.asarray(self.angular_params.get("weights", np.ones(self.dim)))
            weights = weights / weights.sum()
            idx = rng.choice(self.dim, size=size, p=weights)
            Theta = np.zeros((size, self.dim))
            Theta[np.arange(size), idx] = 1.0
            return Theta
        if self.angular_kind == "ray_mixture":
            rays = np.asarray(self.angular_params.get("rays"), dtype=float)
            if rays is None or rays.ndim != 2:
                raise ValueError("ray_mixture requires 'rays' as 2D array")
            weights = np.asarray(self.angular_params.get("weights", np.ones(rays.shape[0])))
            weights = weights / weights.sum()
            idx = rng.choice(rays.shape[0], size=size, p=weights)
            T = rays[idx]
            norm = np.linalg.norm(T, axis=1, keepdims=True)
            return T / np.where(norm > 0, norm, 1.0)
        if self.angular_kind == "dirichlet":
            concentration = np.asarray(
                self.angular_params.get("concentration", np.ones(self.dim)), dtype=float
            )
            return rng.dirichlet(concentration, size=size)
        if self.angular_kind == "empirical":
            pool = np.asarray(self.angular_params.get("angles"), dtype=float)
            idx = rng.integers(0, pool.shape[0], size=size)
            return pool[idx]
        raise AssertionError("unreachable")

    def sample(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        R = self._radial.rvs(size, rng)
        Theta = self.sample_angles(size, rng)
        return R[:, None] * Theta

    @property
    def radial(self) -> ParetoTail:
        return self._radial
