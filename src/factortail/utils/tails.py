"""Marginal heavy-tailed distributions used across the simulation families.

Each distribution exposes the survival function, the log-survival function,
the quantile, and a sampler. We work in log-scale where deep-tail
underflow would otherwise corrupt the conditional kernels (see
``rem:numerical-stability`` in the manuscript).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import stats

__all__ = [
    "TailDistribution",
    "ParetoTail",
    "LomaxTail",
    "BurrTail",
    "StudentTTail",
    "build_marginal",
]


@runtime_checkable
class TailDistribution(Protocol):
    r"""A right-tailed distribution suitable for rare-event simulation.

    Implementations must satisfy

    * ``alpha`` is the tail index ``alpha > 0``;
    * ``c`` is the tail constant relative to the common reference
      ``\overline G(x) = x^{-alpha}`` (so ``P(X > x) ~ c x^{-alpha}``);
    * ``sf(x) = P(X > x)`` and ``logsf(x) = log P(X > x)`` are exact when
      possible.
    """

    alpha: float
    c: float

    def sf(self, x: ArrayLike) -> NDArray[np.float64]: ...
    def logsf(self, x: ArrayLike) -> NDArray[np.float64]: ...
    def ppf(self, q: ArrayLike) -> NDArray[np.float64]: ...
    def rvs(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]: ...


class _Tail:
    """Common base providing default ``logsf`` and array coercion."""

    alpha: float
    c: float

    def sf(self, x: ArrayLike) -> NDArray[np.float64]:  # pragma: no cover - abstract
        raise NotImplementedError

    def logsf(self, x: ArrayLike) -> NDArray[np.float64]:
        x = np.asarray(x, dtype=float)
        with np.errstate(divide="ignore"):
            return np.log(np.clip(self.sf(x), a_min=np.finfo(float).tiny, a_max=None))


class ParetoTail(_Tail):
    """Exact Pareto right tail: ``P(X > x) = (x/scale)^{-alpha}`` for ``x >= scale``.

    Tail constant relative to ``x^{-alpha}`` is ``c = scale^{alpha}``.
    """

    def __init__(self, alpha: float, scale: float = 1.0) -> None:
        if alpha <= 0:
            raise ValueError("Pareto alpha must be positive")
        if scale <= 0:
            raise ValueError("Pareto scale must be positive")
        self.alpha = float(alpha)
        self.scale = float(scale)
        self.c = float(scale**alpha)

    def sf(self, x: ArrayLike) -> NDArray[np.float64]:
        x = np.asarray(x, dtype=float)
        out = np.where(x < self.scale, 1.0, (x / self.scale) ** (-self.alpha))
        return out

    def logsf(self, x: ArrayLike) -> NDArray[np.float64]:
        x = np.asarray(x, dtype=float)
        return np.where(
            x < self.scale,
            0.0,
            -self.alpha * (np.log(np.maximum(x, self.scale)) - np.log(self.scale)),
        )

    def ppf(self, q: ArrayLike) -> NDArray[np.float64]:
        q = np.asarray(q, dtype=float)
        return self.scale * (1.0 - q) ** (-1.0 / self.alpha)

    def rvs(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        u = rng.random(size=size)
        return self.scale * u ** (-1.0 / self.alpha)

    def mean(self) -> float:
        if self.alpha <= 1.0:
            return float("inf")
        return self.scale * self.alpha / (self.alpha - 1.0)


class LomaxTail(_Tail):
    """Lomax (shifted Pareto): ``P(X > x) = (1 + x/scale)^{-alpha}`` for ``x >= 0``.

    Tail constant relative to ``x^{-alpha}`` is ``c = scale^{alpha}``.
    """

    def __init__(self, alpha: float, scale: float = 1.0) -> None:
        if alpha <= 0:
            raise ValueError("Lomax alpha must be positive")
        if scale <= 0:
            raise ValueError("Lomax scale must be positive")
        self.alpha = float(alpha)
        self.scale = float(scale)
        self.c = float(scale**alpha)

    def sf(self, x: ArrayLike) -> NDArray[np.float64]:
        x = np.asarray(x, dtype=float)
        return np.where(x <= 0, 1.0, (1.0 + x / self.scale) ** (-self.alpha))

    def logsf(self, x: ArrayLike) -> NDArray[np.float64]:
        x = np.asarray(x, dtype=float)
        return np.where(x <= 0, 0.0, -self.alpha * np.log1p(np.maximum(x, 0.0) / self.scale))

    def ppf(self, q: ArrayLike) -> NDArray[np.float64]:
        q = np.asarray(q, dtype=float)
        return self.scale * ((1.0 - q) ** (-1.0 / self.alpha) - 1.0)

    def rvs(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        u = rng.random(size=size)
        return self.scale * (u ** (-1.0 / self.alpha) - 1.0)

    def mean(self) -> float:
        if self.alpha <= 1.0:
            return float("inf")
        return self.scale / (self.alpha - 1.0)


class BurrTail(_Tail):
    """Burr Type XII: ``P(X > x) = (1 + (x/scale)^k)^{-d}`` for ``x >= 0``.

    Tail index is ``alpha = k * d`` and ``c = scale^{alpha}``.
    """

    def __init__(self, k: float, d: float, scale: float = 1.0) -> None:
        if k <= 0 or d <= 0 or scale <= 0:
            raise ValueError("Burr parameters must be positive")
        self.k = float(k)
        self.d = float(d)
        self.scale = float(scale)
        self.alpha = float(k * d)
        self.c = float(scale**self.alpha)

    def sf(self, x: ArrayLike) -> NDArray[np.float64]:
        x = np.asarray(x, dtype=float)
        return np.where(x <= 0, 1.0, (1.0 + (x / self.scale) ** self.k) ** (-self.d))

    def logsf(self, x: ArrayLike) -> NDArray[np.float64]:
        x = np.asarray(x, dtype=float)
        return np.where(
            x <= 0,
            0.0,
            -self.d * np.log1p((np.maximum(x, 0.0) / self.scale) ** self.k),
        )

    def ppf(self, q: ArrayLike) -> NDArray[np.float64]:
        q = np.asarray(q, dtype=float)
        inv = (1.0 - q) ** (-1.0 / self.d) - 1.0
        return self.scale * inv ** (1.0 / self.k)

    def rvs(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        u = rng.random(size=size)
        inv = u ** (-1.0 / self.d) - 1.0
        return self.scale * inv ** (1.0 / self.k)

    def mean(self) -> float:
        from math import gamma

        if self.alpha <= 1.0:
            return float("inf")
        # Burr XII closed-form mean: scale * Gamma(1 + 1/k) * Gamma(d - 1/k) / Gamma(d)
        return self.scale * gamma(1 + 1 / self.k) * gamma(self.d - 1 / self.k) / gamma(self.d)


class StudentTTail(_Tail):
    """Student-t right tail with degrees of freedom ``alpha`` (so tail index = nu).

    For Student-t with df=nu, ``P(|T| > x) ~ K_nu x^{-nu}`` as x -> infty, with
    a known constant depending on nu. We expose the right tail
    ``P(T > x) ~ (K_nu / 2) x^{-nu}``.
    """

    def __init__(self, alpha: float, scale: float = 1.0) -> None:
        if alpha <= 0:
            raise ValueError("Student alpha must be positive")
        if scale <= 0:
            raise ValueError("Student scale must be positive")
        self.alpha = float(alpha)
        self.scale = float(scale)
        nu = self.alpha
        from math import gamma, pi, sqrt

        k_nu = gamma((nu + 1) / 2.0) / (gamma(nu / 2.0) * sqrt(nu * pi)) * nu ** (nu / 2.0)
        self.c = float(0.5 * k_nu * (1.0 / scale) ** (-nu) if False else 0.5 * k_nu * scale**nu)

    def sf(self, x: ArrayLike) -> NDArray[np.float64]:
        x = np.asarray(x, dtype=float)
        return np.asarray(stats.t.sf(x / self.scale, df=self.alpha), dtype=float)

    def logsf(self, x: ArrayLike) -> NDArray[np.float64]:
        x = np.asarray(x, dtype=float)
        return np.asarray(stats.t.logsf(x / self.scale, df=self.alpha), dtype=float)

    def ppf(self, q: ArrayLike) -> NDArray[np.float64]:
        q = np.asarray(q, dtype=float)
        return self.scale * np.asarray(stats.t.isf(1.0 - q, df=self.alpha), dtype=float)

    def rvs(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        return self.scale * rng.standard_t(df=self.alpha, size=size)

    def mean(self) -> float:
        # Student-t with alpha=nu has zero mean when nu > 1; undefined for
        # nu <= 1.
        if self.alpha <= 1.0:
            return float("inf")
        return 0.0


_FACTORY = {
    "pareto": ParetoTail,
    "lomax": LomaxTail,
    "burr": BurrTail,
    "student_t": StudentTTail,
    "student": StudentTTail,
    "t": StudentTTail,
}


def build_marginal(spec: dict) -> TailDistribution:
    """Instantiate a tail distribution from a YAML-friendly dict spec.

    Examples
    --------
    >>> d = build_marginal({"type": "pareto", "alpha": 1.5, "scale": 1.0})
    >>> abs(d.sf(2.0) - 2.0 ** -1.5) < 1e-12
    True
    """
    spec = dict(spec)
    kind = spec.pop("type").lower()
    if kind not in _FACTORY:
        raise ValueError(f"Unknown distribution type: {kind!r}")
    return _FACTORY[kind](**spec)
