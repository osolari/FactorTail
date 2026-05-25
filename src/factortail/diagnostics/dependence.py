r"""Dependence diagnostics: empirical :math:`\chi`, :math:`\bar\chi`,
:math:`\eta`, and the pairwise summary table used in §9.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from factortail.hrv.ledford_tawn import chi_chibar, ledford_tawn_eta

__all__ = ["chi_diagnostic", "pairwise_dependence_table", "empirical_ranks"]


def empirical_ranks(x: NDArray[np.float64]) -> NDArray[np.float64]:
    """Empirical-CDF transform per column: ``U_i = rank(X_i) / (n+1)``."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    n = x.shape[0]
    ranks = np.empty_like(x)
    for j in range(x.shape[1]):
        ranks[:, j] = pd.Series(x[:, j]).rank(method="average").to_numpy() / (n + 1)
    return ranks


def chi_diagnostic(
    X: NDArray[np.float64],
    *,
    threshold_u: float = 0.95,
    eta_k: int | None = None,
) -> dict[str, NDArray[np.float64]]:
    r"""Pairwise :math:`\\chi`, :math:`\\bar\\chi`, and :math:`\\eta` matrices."""
    X = np.asarray(X, dtype=float)
    n, d = X.shape
    U = empirical_ranks(X)
    chi = np.zeros((d, d))
    chibar = np.zeros((d, d))
    eta = np.zeros((d, d))
    for i in range(d):
        for j in range(d):
            if i == j:
                chi[i, j] = 1.0
                chibar[i, j] = 1.0
                eta[i, j] = 1.0
            else:
                cc = chi_chibar(U[:, i], U[:, j], threshold_u=threshold_u)
                chi[i, j] = cc["chi_hat"]
                chibar[i, j] = cc["chibar_hat"]
                lt = ledford_tawn_eta(U[:, i], U[:, j], k=eta_k)
                eta[i, j] = lt["eta_hat"]
    return {"chi": chi, "chibar": chibar, "eta": eta}


def pairwise_dependence_table(
    X: NDArray[np.float64],
    *,
    threshold_u: float = 0.95,
    eta_k: int | None = None,
    column_names: list[str] | None = None,
) -> pd.DataFrame:
    diag = chi_diagnostic(X, threshold_u=threshold_u, eta_k=eta_k)
    d = X.shape[1]
    names = column_names if column_names is not None else [f"X{i}" for i in range(d)]
    rows = []
    for i in range(d):
        for j in range(i + 1, d):
            rows.append(
                {
                    "factor_i": names[i],
                    "factor_j": names[j],
                    "threshold_u": threshold_u,
                    "chi_hat": diag["chi"][i, j],
                    "chibar_hat": diag["chibar"][i, j],
                    "eta_hat": diag["eta"][i, j],
                }
            )
    return pd.DataFrame(rows)
