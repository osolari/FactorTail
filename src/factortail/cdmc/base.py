"""Shared result type and confidence-interval helpers for CdMC estimators."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

__all__ = ["CdMCResult", "bernstein_ci", "sample_ci"]


@dataclass
class CdMCResult:
    r"""Result of a CdMC run.

    Attributes
    ----------
    mu_hat:
        Sample mean of the estimator outputs :math:`\widehat\mu = n^{-1}\sum_m Z_m`.
    variance:
        Sample variance :math:`s^2 = (n-1)^{-1}\sum_m (Z_m - \widehat\mu)^2`.
    n:
        Number of replicates.
    runtime_seconds:
        Wall-clock runtime of the production sample.
    ci_low, ci_high:
        Half-width 95% confidence-interval endpoints (Bernstein when an
        envelope is supplied; sample t-CI otherwise).
    extra:
        Estimator-specific diagnostics (BRE diagnostic, envelope, etc.).
    """

    mu_hat: float
    variance: float
    n: int
    runtime_seconds: float
    ci_low: float
    ci_high: float
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def rel_sd(self) -> float:
        if self.mu_hat <= 0:
            return float("inf")
        return float(np.sqrt(self.variance / max(self.n, 1)) / self.mu_hat)

    @property
    def standard_error(self) -> float:
        return float(np.sqrt(self.variance / max(self.n, 1)))

    def to_dict(self) -> dict[str, Any]:
        d = {
            "mu_hat": self.mu_hat,
            "variance": self.variance,
            "n": self.n,
            "runtime_seconds": self.runtime_seconds,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "standard_error": self.standard_error,
            "rel_sd": self.rel_sd,
        }
        d.update(self.extra)
        return d


def sample_ci(
    samples: NDArray[np.float64],
    *,
    alpha: float = 0.05,
) -> tuple[float, float]:
    r"""Symmetric Gaussian CI of level :math:`1-\alpha` (t-distribution would
    differ negligibly for our replicate counts).
    """
    from scipy import stats

    n = len(samples)
    if n < 2:
        return float("nan"), float("nan")
    mean = float(samples.mean())
    se = float(samples.std(ddof=1) / np.sqrt(n))
    half = float(stats.norm.isf(alpha / 2.0) * se)
    return mean - half, mean + half


def bernstein_ci(
    samples: NDArray[np.float64],
    *,
    envelope: float,
    alpha: float = 0.05,
) -> tuple[float, float]:
    r"""Empirical Bernstein CI for bounded :math:`Z \in [0, B]`.

    Maurer-Pontil (2009) empirical Bernstein bound.
    """
    samples = np.asarray(samples, dtype=float)
    n = len(samples)
    if n < 2:
        return float("nan"), float("nan")
    mean = float(samples.mean())
    var = float(samples.var(ddof=1))
    log_term = np.log(2.0 / alpha)
    half = float(np.sqrt(2.0 * var * log_term / n) + (7.0 / 3.0) * envelope * log_term / (n - 1))
    return mean - half, mean + half
