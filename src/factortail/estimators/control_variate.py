r"""Control-variate estimator (§7, Proposition ``prop:vre``).

Two variants:

1. **Oracle centering.** ``m_Y(x)`` is known exactly and the coefficient
   :math:`\gamma^*(x) = \mathrm{Cov}(Z, Y) / \mathrm{Var}(Y)` is estimated
   on the production sample.
2. **Sample-split centering.** ``m_Y(x)`` and :math:`\gamma` are estimated
   on an independent pilot of size ``n_0`` (default :math:`\sqrt n`).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from factortail.cdmc.base import sample_ci

__all__ = ["ControlVariateResult", "control_variate"]


@dataclass
class ControlVariateResult:
    mu_hat: float
    variance: float
    n: int
    n_pilot: int
    gamma_hat: float
    rho_squared: float
    runtime_seconds: float
    ci_low: float
    ci_high: float
    centering_status: str  # "oracle" or "sample_split"
    extra: dict


def control_variate(
    Z_samples: NDArray[np.float64],
    Y_samples: NDArray[np.float64],
    *,
    m_Y: float | None = None,
    pilot_split: int | None = None,
) -> ControlVariateResult:
    r"""Compute the centered control-variate estimator.

    Parameters
    ----------
    Z_samples, Y_samples:
        Equal-length sample sequences from joint replicates.
    m_Y:
        If provided, use exact (oracle) centering. Otherwise sample-split.
    pilot_split:
        Size of pilot split; defaults to :math:`\lfloor \sqrt n \rfloor` for
        sample-split centering.
    """
    Z = np.asarray(Z_samples, dtype=float)
    Y = np.asarray(Y_samples, dtype=float)
    if Z.shape != Y.shape:
        raise ValueError("Z_samples and Y_samples must have the same shape")
    n = len(Z)
    if m_Y is not None:
        # Oracle variant
        cov_zy = float(np.cov(Z, Y, ddof=1)[0, 1])
        var_y = float(Y.var(ddof=1))
        gamma = cov_zy / max(var_y, 1e-300)
        adjusted = Z - gamma * (Y - m_Y)
        mu_hat = float(adjusted.mean())
        var = float(adjusted.var(ddof=1))
        rho_sq = float((cov_zy**2) / max(Z.var(ddof=1) * var_y, 1e-300))
        lo, hi = sample_ci(adjusted)
        return ControlVariateResult(
            mu_hat=mu_hat,
            variance=var,
            n=n,
            n_pilot=0,
            gamma_hat=gamma,
            rho_squared=rho_sq,
            runtime_seconds=0.0,
            ci_low=lo,
            ci_high=hi,
            centering_status="oracle",
            extra={"m_Y": m_Y},
        )
    # Sample-split variant.
    n0 = pilot_split if pilot_split is not None else max(int(np.sqrt(n)), 5)
    if not (0 < n0 < n):
        raise ValueError(f"pilot_split must satisfy 0 < n0 < {n}")
    Z_pilot, Z_prod = Z[:n0], Z[n0:]
    Y_pilot, Y_prod = Y[:n0], Y[n0:]
    m_Y_hat = float(Y_pilot.mean())
    cov_zy = float(np.cov(Z_pilot, Y_pilot, ddof=1)[0, 1])
    var_y = float(Y_pilot.var(ddof=1))
    gamma = cov_zy / max(var_y, 1e-300)
    adjusted = Z_prod - gamma * (Y_prod - m_Y_hat)
    mu_hat = float(adjusted.mean())
    var = float(adjusted.var(ddof=1))
    rho_sq = float((cov_zy**2) / max(Z_pilot.var(ddof=1) * var_y, 1e-300))
    lo, hi = sample_ci(adjusted)
    return ControlVariateResult(
        mu_hat=mu_hat,
        variance=var,
        n=n - n0,
        n_pilot=n0,
        gamma_hat=gamma,
        rho_squared=rho_sq,
        runtime_seconds=0.0,
        ci_low=lo,
        ci_high=hi,
        centering_status="sample_split",
        extra={"m_Y_hat": m_Y_hat},
    )
