"""Copula samplers and conditional kernels (§4 vine/copula CdMC).

Each copula exposes a ``sample(size, rng) -> uniform marginals`` and a
``conditional_survival(t, U_minus_i, i) -> P(U_i > t | U_{-i})`` routine.
"""

from factortail.copula.archimedean import ClaytonCopula, FrankCopula, GumbelCopula
from factortail.copula.elliptical import GaussianCopula, StudentTCopula
from factortail.copula.vine import CVineKernel

__all__ = [
    "CVineKernel",
    "ClaytonCopula",
    "FrankCopula",
    "GaussianCopula",
    "GumbelCopula",
    "StudentTCopula",
]
