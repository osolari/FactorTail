"""Gaussian and Student-t copulas with closed-form conditional survival."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy import stats

__all__ = ["GaussianCopula", "StudentTCopula"]


def _check_corr(R: NDArray[np.float64]) -> None:
    R = np.asarray(R, dtype=float)
    if R.ndim != 2 or R.shape[0] != R.shape[1]:
        raise ValueError("Correlation matrix must be square")
    if not np.allclose(R, R.T):
        raise ValueError("Correlation matrix must be symmetric")
    eig = np.linalg.eigvalsh(R)
    if eig.min() <= -1e-10:
        raise ValueError("Correlation matrix must be positive semi-definite")


@dataclass
class GaussianCopula:
    """Multivariate Gaussian copula with correlation matrix ``R``."""

    R: NDArray[np.float64]

    def __post_init__(self) -> None:
        self.R = np.asarray(self.R, dtype=float)
        _check_corr(self.R)
        self._L = np.linalg.cholesky(self.R + 1e-12 * np.eye(self.R.shape[0]))

    @property
    def d(self) -> int:
        return int(self.R.shape[0])

    def sample_uniform(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        Z = rng.standard_normal((size, self.d)) @ self._L.T
        return stats.norm.cdf(Z)

    def conditional_survival(
        self,
        t: float,
        U_minus_i: NDArray[np.float64],
        i: int,
    ) -> float:
        r"""``P(U_i > t | U_{-i})`` under the Gaussian copula."""
        U_minus_i = np.asarray(U_minus_i, dtype=float)
        z_minus = stats.norm.ppf(U_minus_i)
        idx = [j for j in range(self.d) if j != i]
        R = self.R
        sigma_ii = R[i, i]
        sigma_iJ = R[i, idx]
        sigma_JJ = R[np.ix_(idx, idx)]
        sigma_JJ_inv = np.linalg.inv(sigma_JJ)
        cond_mean = sigma_iJ @ sigma_JJ_inv @ z_minus
        cond_var = max(sigma_ii - sigma_iJ @ sigma_JJ_inv @ sigma_iJ, 1e-12)
        z_t = stats.norm.ppf(t)
        return float(stats.norm.sf((z_t - cond_mean) / np.sqrt(cond_var)))


@dataclass
class StudentTCopula:
    """Multivariate Student-t copula with df ``nu`` and dispersion ``R``."""

    R: NDArray[np.float64]
    nu: float

    def __post_init__(self) -> None:
        self.R = np.asarray(self.R, dtype=float)
        _check_corr(self.R)
        if self.nu <= 0:
            raise ValueError("Degrees of freedom must be positive")
        self._L = np.linalg.cholesky(self.R + 1e-12 * np.eye(self.R.shape[0]))

    @property
    def d(self) -> int:
        return int(self.R.shape[0])

    def sample_uniform(self, size: int, rng: np.random.Generator) -> NDArray[np.float64]:
        Z = rng.standard_normal((size, self.d)) @ self._L.T
        chi2 = rng.chisquare(df=self.nu, size=size)
        T = Z / np.sqrt(chi2 / self.nu)[:, None]
        return stats.t.cdf(T, df=self.nu)

    def conditional_survival(
        self,
        t: float,
        U_minus_i: NDArray[np.float64],
        i: int,
    ) -> float:
        t_minus = stats.t.ppf(U_minus_i, df=self.nu)
        idx = [j for j in range(self.d) if j != i]
        R = self.R
        sigma_iJ = R[i, idx]
        sigma_JJ = R[np.ix_(idx, idx)]
        sigma_JJ_inv = np.linalg.inv(sigma_JJ)
        cond_mean = sigma_iJ @ sigma_JJ_inv @ t_minus
        cond_var = max(R[i, i] - sigma_iJ @ sigma_JJ_inv @ sigma_iJ, 1e-12)
        # Conditional Student-t with updated df
        nu_cond = self.nu + len(idx)
        quad = float(t_minus @ sigma_JJ_inv @ t_minus)
        scale = np.sqrt(cond_var * (self.nu + quad) / nu_cond)
        t_t = stats.t.ppf(t, df=self.nu)
        return float(stats.t.sf((t_t - cond_mean) / scale, df=nu_cond))
