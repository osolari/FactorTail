"""Family IV: copula-dependence factor models (§4 copula CdMC, §8).

Margins are heavy-tailed (Pareto/Lomax) and joint dependence is induced by
a copula. The DGP returns :math:`X_i = F_i^{-1}(U_i)` for a copula sample
``U``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from factortail.copula import (
    ClaytonCopula,
    FrankCopula,
    GaussianCopula,
    GumbelCopula,
    StudentTCopula,
)
from factortail.utils.tails import TailDistribution, build_marginal

__all__ = ["CopulaModel"]


_COPULAS = {
    "gaussian": GaussianCopula,
    "student_t": StudentTCopula,
    "clayton": ClaytonCopula,
    "gumbel": GumbelCopula,
    "frank": FrankCopula,
}


@dataclass
class CopulaModel:
    """Copula + heavy-tailed margins."""

    copula: object
    marginals: list[TailDistribution]

    @classmethod
    def from_spec(cls, spec: dict) -> CopulaModel:
        copula_spec = dict(spec["copula"])
        kind = copula_spec.pop("type").lower()
        if kind not in _COPULAS:
            raise ValueError(f"Unknown copula type: {kind!r}")
        copula = _COPULAS[kind](**copula_spec)
        marginals = [build_marginal(s) for s in spec["marginals"]]
        return cls(copula=copula, marginals=marginals)

    @property
    def N(self) -> int:
        return len(self.marginals)

    def sample(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        U = self.copula.sample_uniform(size, rng)
        if U.shape[1] != self.N:
            raise ValueError(f"Copula dimension {U.shape[1]} != number of marginals {self.N}")
        cols = [m.ppf(U[:, i]) for i, m in enumerate(self.marginals)]
        return np.column_stack(cols)
