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
    r"""Clayton copula with parameter ``theta > 0`` in dimension ``d``.

    The Clayton CDF is
    :math:`C(u) = (\sum_i u_i^{-\theta} - (d-1))^{-1/\theta}`,
    and the conditional CDF of :math:`U_i` given the other coordinates is

    .. math::

       F_{i|-i}(t \mid u_{-i})
       = \left(\frac{s_{-i}}{s_{-i} + t^{-\theta} - 1}\right)^{1/\theta + (d-1)},

    where :math:`s_{-i} = \sum_{j\neq i} u_j^{-\theta} - (d-2)`.
    """

    theta: float
    d: int = 2

    def __post_init__(self) -> None:
        if self.theta <= 0:
            raise ValueError("Clayton theta must be positive")
        if self.d < 2:
            raise ValueError("Clayton dimension must be >= 2")

    def sample_uniform(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        # Marshall-Olkin: V ~ Gamma(1/theta, 1), then U_i = (1 - log(E_i)/V)^{-1/theta}
        V = rng.gamma(shape=1.0 / self.theta, scale=1.0, size=size)
        E = rng.exponential(size=(size, self.d))
        return (1.0 + E / V[:, None]) ** (-1.0 / self.theta)

    def conditional_survival(
        self,
        t: float,
        U_minus_i: NDArray[np.float64] | float,
        i: int = 0,
    ) -> float:
        r"""``P(U_i > t | U_{-i} = u_{-i})`` for the Clayton copula in any
        dimension ``d``.

        Accepts either a length-``(d-1)`` array ``U_minus_i`` for ``d \ge 2``
        or a single scalar (the bivariate case).
        """
        theta = self.theta
        if isinstance(U_minus_i, float | int):
            u = np.array([float(U_minus_i)])
        else:
            u = np.asarray(U_minus_i, dtype=float).ravel()
        if u.size != self.d - 1:
            raise ValueError(
                f"Clayton dim {self.d}: expected {self.d - 1} conditioning values, got {u.size}"
            )
        if t <= 0:
            return 1.0
        if t >= 1:
            return 0.0
        s = float(np.sum(u ** (-theta))) - (self.d - 2)
        denom = s + t ** (-theta) - 1.0
        if denom <= 0:
            return 1.0
        cdf = (s / denom) ** (1.0 / theta + (self.d - 1))
        return float(1.0 - cdf)


@dataclass
class GumbelCopula:
    r"""Gumbel copula with parameter ``theta >= 1`` in dimension ``d``.

    The conditional kernel ``P(U_2 > t | U_1 = u)`` is implemented in closed
    form only for ``d = 2``. Higher-dimensional Gumbel kernels would require
    vine-style decomposition and are not exposed here.
    """

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

    def conditional_survival(
        self,
        t: float,
        U_minus_i: NDArray[np.float64] | float,
        i: int = 0,
    ) -> float:
        r"""Bivariate Gumbel conditional survival
        :math:`P(U_2 > t \mid U_1 = u)`.

        Derived from :math:`C(u_1, u_2) = \exp\{-[(-\log u_1)^\theta + (-\log u_2)^\theta]^{1/\theta}\}`
        via :math:`F_{2|1}(t|u_1) = \partial C / \partial u_1`.
        """
        if self.d != 2:
            raise NotImplementedError("Gumbel conditional survival is implemented for d=2 only")
        if isinstance(U_minus_i, float | int):
            u = float(U_minus_i)
        else:
            arr = np.asarray(U_minus_i, dtype=float).ravel()
            if arr.size != 1:
                raise ValueError(f"d=2 Gumbel: expected 1 conditioning value, got {arr.size}")
            u = float(arr[0])
        if t <= 0:
            return 1.0
        if t >= 1 or u <= 0 or u >= 1:
            return 0.0 if t >= 1 else 1.0
        theta = self.theta
        a = (-np.log(u)) ** theta
        b = (-np.log(t)) ** theta
        s = a + b
        C = np.exp(-(s ** (1.0 / theta)))
        # ∂C/∂u_1 = C * s^{1/theta - 1} * (-log u_1)^{theta - 1} / u_1
        dC_du1 = C * s ** (1.0 / theta - 1.0) * (-np.log(u)) ** (theta - 1.0) / u
        return float(1.0 - dC_du1)


@dataclass
class FrankCopula:
    """Frank copula with parameter ``theta != 0``.

    Sampling and conditional survival are exposed only for ``d = 2``.
    """

    theta: float
    d: int = 2

    def __post_init__(self) -> None:
        if self.theta == 0:
            raise ValueError("Frank theta must be non-zero")

    def sample_uniform(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        r"""Conditional inverse sampler.

        Starting from :math:`V = C_{2|1}(U_2 \mid U_1)`,
        :math:`U_2 = -\tfrac1\theta\log\bigl(1 + V A / (e^{-\theta U_1} - V B)\bigr)`
        with :math:`A = e^{-\theta}-1`, :math:`B = e^{-\theta U_1}-1`.
        """
        if self.d != 2:
            raise NotImplementedError("Frank sampler implemented only for d=2 here")
        theta = self.theta
        u1 = rng.random(size=size)
        v = rng.random(size=size)
        A = np.expm1(-theta)
        B = np.expm1(-theta * u1)
        eu = np.exp(-theta * u1)
        denom = eu - v * B
        denom = np.where(np.abs(denom) < 1e-300, np.sign(denom) * 1e-300, denom)
        ratio = v * A / denom
        u2 = -np.log1p(ratio) / theta
        u2 = np.clip(u2, 1e-12, 1.0 - 1e-12)
        return np.column_stack([u1, u2])

    def conditional_survival(
        self,
        t: float,
        U_minus_i: NDArray[np.float64] | float,
        i: int = 0,
    ) -> float:
        r"""Bivariate Frank conditional survival via
        :math:`F_{2|1}(t|u) = \partial C/\partial u_1`."""
        if self.d != 2:
            raise NotImplementedError("Frank conditional survival is implemented for d=2 only")
        if isinstance(U_minus_i, float | int):
            u = float(U_minus_i)
        else:
            arr = np.asarray(U_minus_i, dtype=float).ravel()
            if arr.size != 1:
                raise ValueError(f"d=2 Frank: expected 1 conditioning value, got {arr.size}")
            u = float(arr[0])
        if t <= 0:
            return 1.0
        if t >= 1:
            return 0.0
        theta = self.theta
        em = np.expm1(-theta)
        num = np.expm1(-theta * u) * np.expm1(-theta * t)
        cdf = num / (em + np.expm1(-theta * u) * (np.exp(-theta * t) - 1.0) + 0.0)
        # Above is C(u, t) / u, the bivariate Frank conditional CDF.
        # The standard closed form: C_{2|1}(t|u) = exp(-theta*u) (e^{-theta*t}-1) / [(e^{-theta}-1) + (e^{-theta*u}-1)(e^{-theta*t}-1)]
        a_u = np.expm1(-theta * u)
        a_t = np.expm1(-theta * t)
        denom = em + a_u * a_t
        if abs(denom) < 1e-300:
            return 1.0
        cdf = np.exp(-theta * u) * a_t / denom
        return float(1.0 - cdf)
