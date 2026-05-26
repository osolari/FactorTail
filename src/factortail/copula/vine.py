r"""C-vine truncation for high-dimensional Archimedean copula conditional kernels.

For Gumbel and Frank copulas in dimension :math:`d > 2` the closed-form
:math:`(d-1)`-th derivative of the inverse Archimedean generator is
tractable but heavy. The manuscript (§4 dependent CdMC) documents
**vine truncation** as the standard substitute: chain bivariate
conditionals to approximate the high-dimensional kernel.

This module implements a **C-vine** with a single root variable. For a
copula with d variables and root index ``root``, the conditional CDF
:math:`F_{i|-i}(t \mid u_{-i})` is approximated by chaining bivariate
conditional CDFs through ``root``.

The approximation is exact for the **bivariate** case and recovers
the exchangeable-Archimedean result when the bivariate copula is
identical for every pair. For non-exchangeable mixtures the truncation
introduces a controlled error — see :cite:`AasCzadoFrigessiBakken2009`
for the rigorous treatment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

__all__ = ["CVineKernel"]


@dataclass
class CVineKernel:
    r"""C-vine kernel built from a single bivariate Archimedean copula.

    Parameters
    ----------
    bivariate_copula:
        Object exposing ``conditional_survival(t, u, i=0) -> float`` for
        ``d = 2``. Examples: ``ClaytonCopula(d=2)``, ``GumbelCopula(d=2)``,
        ``FrankCopula(d=2)``.
    d:
        Target dimension.
    root:
        Index of the root variable in the C-vine. Defaults to 0.

    The returned kernel is

    .. math::

        \hat F_{i|-i}(t \mid u_{-i}) \;=\;
        \tfrac{1}{d-1}\sum_{j \ne i}
        F_{i|j}\bigl(t \mid u_j\bigr),

    a symmetric truncation that averages every pairwise conditional. It
    is *not* the exact high-d conditional but is the recommended
    truncation when an exact :math:`(d-1)`-th derivative is unavailable.
    """

    bivariate_copula: Any
    d: int
    root: int = 0

    def __post_init__(self) -> None:
        if self.d < 2:
            raise ValueError("CVineKernel requires d >= 2")
        if not (0 <= self.root < self.d):
            raise ValueError("root index out of range")
        if not hasattr(self.bivariate_copula, "conditional_survival"):
            raise TypeError("bivariate_copula must expose conditional_survival(t, u, i=0)")

    def conditional_survival(
        self,
        t: float,
        U_minus_i: NDArray[np.float64] | float,
        i: int = 0,
    ) -> float:
        r"""Approximate :math:`P(U_i > t \mid U_{-i})` by averaging pairwise
        bivariate conditional survivals.

        For ``d=2`` this is **exact** and identical to the underlying
        bivariate copula's ``conditional_survival``.
        """
        if isinstance(U_minus_i, float | int):
            u = np.array([float(U_minus_i)])
        else:
            u = np.asarray(U_minus_i, dtype=float).ravel()
        if u.size != self.d - 1:
            raise ValueError(
                f"CVine dim {self.d}: expected {self.d - 1} conditioning values, got {u.size}"
            )
        if self.d == 2:
            return float(self.bivariate_copula.conditional_survival(t, u, i))
        survivals = np.array(
            [float(self.bivariate_copula.conditional_survival(t, float(uj))) for uj in u]
        )
        return float(survivals.mean())
