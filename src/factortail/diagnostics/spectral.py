r"""Empirical spectral-measure estimator (§5).

For data :math:`X_1,\dots,X_n` and radial norm :math:`\|\cdot\|`, the
empirical spectral measure is the empirical distribution of
:math:`\widehat\Theta_t = X_t / \|X_t\|` over indices ``t`` with
:math:`\|X_t\| > u`. The first-order linear-risk constant estimator is

.. math::

    \widehat C_\ell(u)
    = \frac{1}{k}\sum_{t:\|X_t\|>u} (\ell(\widehat\Theta_t)_+)^{\widehat\alpha}.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

__all__ = ["empirical_spectral_measure", "spectral_constant_estimate"]


def empirical_spectral_measure(
    X: NDArray[np.float64],
    *,
    k: int | None = None,
    norm: str = "l1",
) -> dict:
    r"""Estimate the empirical spectral measure from top-k exceedances.

    Parameters
    ----------
    X : (n, d) array
    k : number of exceedances; defaults to ``int(sqrt(n))``.
    norm : "l1" or "l2".
    """
    X = np.asarray(X, dtype=float)
    n = X.shape[0]
    if k is None:
        k = max(int(np.sqrt(n)), 5)
    if not (0 < k < n):
        raise ValueError(f"k must satisfy 0 < k < {n}")
    if norm == "l1":
        radii = np.abs(X).sum(axis=1)
    elif norm == "l2":
        radii = np.linalg.norm(X, axis=1)
    else:
        raise ValueError(f"Unknown norm: {norm!r}")
    threshold = np.sort(radii)[-k]
    mask = radii >= threshold
    selected = X[mask]
    selected_radii = radii[mask]
    angles = selected / selected_radii[:, None]
    return {
        "angles": angles,
        "threshold": float(threshold),
        "k_effective": int(mask.sum()),
        "norm": norm,
    }


def spectral_constant_estimate(
    X: NDArray[np.float64],
    *,
    exposure: NDArray[np.float64],
    alpha: float,
    k: int | None = None,
    norm: str = "l1",
) -> float:
    """Estimate :math:`\\widehat C_\\ell(u) = k^{-1}\\sum (\\ell(\\Theta)_+)^\\alpha`."""
    res = empirical_spectral_measure(X, k=k, norm=norm)
    angles = res["angles"]
    exposure = np.asarray(exposure, dtype=float)
    y = angles @ exposure
    y_pos = np.maximum(y, 0.0)
    return float(np.mean(y_pos**alpha))
