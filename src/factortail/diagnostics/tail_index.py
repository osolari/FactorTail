r"""Hill, Pickands, and POT/GPD tail-index estimators.

* Hill: :math:`\widehat\alpha_H^{-1} = k^{-1} \sum_{i=1}^k \log X_{(n-i+1)} - \log X_{(n-k)}`.
* Pickands: :math:`\widehat\gamma_P = (\log 2)^{-1}
  \log\bigl((X_{(n-k+1)} - X_{(n-2k+1)})/(X_{(n-2k+1)} - X_{(n-4k+1)})\bigr)`.
* POT/GPD: maximum-likelihood fit of a generalized Pareto distribution to
  excesses above a high threshold.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike
from scipy import stats

__all__ = ["hill_estimator", "pickands_estimator", "pot_gpd_estimator"]


def hill_estimator(x: ArrayLike, *, k: int) -> dict[str, float]:
    r"""Hill estimator with the top ``k`` order statistics.

    Returns
    -------
    dict with keys ``alpha_hat``, ``gamma_hat = 1/alpha_hat``, ``se``,
    ``threshold``, ``k``.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    if n < 3:
        raise ValueError("Need at least 3 observations")
    if not (0 < k < n):
        raise ValueError(f"k must satisfy 0 < k < {n}")
    pos = x[x > 0]
    if pos.size < k:
        raise ValueError(f"Not enough positive observations ({pos.size}) for k={k}")
    sorted_pos = np.sort(pos)
    upper = sorted_pos[-k:]
    threshold = sorted_pos[-k - 1] if pos.size > k else sorted_pos[-k]
    log_excesses = np.log(upper) - np.log(threshold)
    gamma = float(log_excesses.mean())
    alpha = 1.0 / gamma if gamma > 0 else float("inf")
    se = float(gamma / np.sqrt(k))
    return {
        "alpha_hat": alpha,
        "gamma_hat": gamma,
        "se": se,
        "threshold": float(threshold),
        "k": int(k),
        "n": int(n),
    }


def pickands_estimator(x: ArrayLike, *, k: int) -> dict[str, float]:
    """Pickands estimator (requires ``n >= 4k``)."""
    x = np.asarray(x, dtype=float)
    n = x.size
    if n < 4 * k:
        raise ValueError(f"n={n} must be at least 4*k={4*k}")
    sorted_x = np.sort(x)
    xk = sorted_x[n - k]
    x2k = sorted_x[n - 2 * k]
    x4k = sorted_x[n - 4 * k]
    num = xk - x2k
    den = x2k - x4k
    if num <= 0 or den <= 0:
        return {"alpha_hat": float("nan"), "gamma_hat": float("nan"), "k": int(k)}
    gamma = float(np.log(num / den) / np.log(2.0))
    alpha = 1.0 / gamma if gamma > 0 else float("inf")
    return {"alpha_hat": alpha, "gamma_hat": gamma, "k": int(k), "n": int(n)}


def pot_gpd_estimator(
    x: ArrayLike, *, threshold: float | None = None, k: int | None = None
) -> dict[str, float]:
    """Generalized-Pareto POT estimator.

    Either ``threshold`` or ``k`` (top-k order statistics) must be supplied.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    if threshold is None:
        if k is None:
            raise ValueError("Provide threshold or k")
        sorted_x = np.sort(x)
        threshold = float(sorted_x[n - k])
    excesses = x[x > threshold] - threshold
    if excesses.size < 5:
        return {
            "alpha_hat": float("nan"),
            "gamma_hat": float("nan"),
            "scale_hat": float("nan"),
            "threshold": threshold,
            "k": int(excesses.size),
        }
    # scipy.stats.genpareto: f(x; c) = (1 + c*x)^(-1-1/c), shape c = gamma
    c, _, scale = stats.genpareto.fit(excesses, floc=0)
    gamma = float(c)
    alpha = 1.0 / gamma if gamma > 0 else float("inf")
    return {
        "alpha_hat": alpha,
        "gamma_hat": gamma,
        "scale_hat": float(scale),
        "threshold": threshold,
        "k": int(excesses.size),
        "n": int(n),
    }
