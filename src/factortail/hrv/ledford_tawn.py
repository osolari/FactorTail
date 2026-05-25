r"""Ledford-Tawn :math:`\eta` estimator (§6 hidden-cone diagnostic).

From two empirical rank series :math:`U_i, U_j`, fit the bivariate tail
exceedance probability

.. math::

    P(U_i > 1 - s, U_j > 1 - s) \approx L(s) s^{1/\eta_{ij}}

via the Hill estimator applied to the structure variable
:math:`T = -\log[\max\{1-U_i, 1-U_j\}]`. The estimator follows
:cite:`LedfordTawn1996,DraismaDeHaanFerreiraEtAl2004`.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

__all__ = ["ledford_tawn_eta", "chi_chibar"]


def ledford_tawn_eta(
    U: NDArray[np.float64],
    V: NDArray[np.float64],
    *,
    k: int | None = None,
) -> dict[str, float]:
    r"""Hill-based :math:`\eta` estimator.

    Parameters
    ----------
    U, V : (n,) arrays in (0, 1)
        Empirical ranks (e.g. ECDF transforms) of the two series.
    k : int, optional
        Number of upper order statistics. Defaults to ``int(sqrt(n))``.
    """
    U = np.asarray(U, dtype=float)
    V = np.asarray(V, dtype=float)
    if U.shape != V.shape:
        raise ValueError("U and V must have the same shape")
    n = len(U)
    if k is None:
        k = max(int(np.sqrt(n)), 5)
    if not (0 < k < n):
        raise ValueError(f"k must satisfy 0 < k < {n}")
    # Structure variable: T = min(1/(1-U), 1/(1-V)) -> the larger, the more
    # tail mass on the joint cone.
    eps = 1e-12
    T = np.minimum(1.0 / np.maximum(1.0 - U, eps), 1.0 / np.maximum(1.0 - V, eps))
    sorted_T = np.sort(T)
    threshold = sorted_T[n - k]
    excesses = np.log(sorted_T[n - k :]) - np.log(threshold)
    eta_hat = float(excesses.mean())
    se = float(eta_hat / np.sqrt(k))
    return {"eta_hat": eta_hat, "k": k, "threshold": float(threshold), "se": se}


def chi_chibar(
    U: NDArray[np.float64],
    V: NDArray[np.float64],
    *,
    threshold_u: float = 0.95,
) -> dict[str, float]:
    r"""Empirical :math:`\chi(u) = P(U > u | V > u)` and
    :math:`\bar\chi(u) = 2\log P(V > u)/\log P(U > u, V > u) - 1`.
    """
    U = np.asarray(U, dtype=float)
    V = np.asarray(V, dtype=float)
    n = len(U)
    excU = threshold_u < U
    excV = threshold_u < V
    p_joint = float((excU & excV).mean())
    p_U = float(excU.mean())
    p_V = float(excV.mean())
    chi = p_joint / max(p_V, 1e-12)
    chibar = (2.0 * np.log(max(1.0 - threshold_u, 1e-12)) / np.log(max(p_joint, 1e-12))) - 1.0
    return {
        "chi_hat": float(chi),
        "chibar_hat": float(chibar),
        "p_joint": p_joint,
        "p_U": p_U,
        "p_V": p_V,
        "threshold_u": threshold_u,
        "n": n,
    }
