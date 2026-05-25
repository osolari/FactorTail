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

__all__ = [
    "bootstrap_bands",
    "empirical_spectral_measure",
    "spectral_constant_estimate",
]


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


def bootstrap_bands(
    X: NDArray[np.float64],
    *,
    exposure: NDArray[np.float64],
    alpha: float,
    k_grid: list[int] | NDArray[np.int_],
    n_boot: int = 500,
    scheme: str = "iid",
    block_length: int = 20,
    confidence: float = 0.95,
    rng: np.random.Generator | None = None,
    seed: int | None = None,
) -> dict:
    r"""Threshold-stability bootstrap for the empirical spectral constant.

    For each ``k`` in ``k_grid``, draws ``n_boot`` bootstrap resamples of
    ``X`` and recomputes :math:`\widehat C_\ell(k)` on each resample. Returns
    point estimates, percentile bands, and bootstrap standard errors per
    ``k``.

    Parameters
    ----------
    scheme:
        - ``"iid"``: standard bootstrap (resample rows with replacement).
        - ``"block"``: non-overlapping block bootstrap with ``block_length``.
        - ``"stationary"``: Politis-Romano stationary bootstrap with
          geometric block lengths of mean ``block_length``.
    block_length:
        Block size for block/stationary bootstrap; ignored for iid.
    confidence:
        Two-sided confidence level for percentile bands.

    Returns
    -------
    dict with keys ``k``, ``estimate``, ``lo``, ``hi``, ``se``.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    X = np.asarray(X, dtype=float)
    n = X.shape[0]
    k_arr = np.asarray(k_grid, dtype=int)
    lo_pct = (1 - confidence) / 2 * 100
    hi_pct = 100 - lo_pct

    def resample_indices() -> NDArray[np.int_]:
        if scheme == "iid":
            return rng.integers(0, n, size=n)
        if scheme == "block":
            n_blocks = (n + block_length - 1) // block_length
            starts = rng.integers(0, n - block_length + 1, size=n_blocks)
            idx = np.concatenate([np.arange(s, s + block_length) for s in starts])[:n]
            return idx
        if scheme == "stationary":
            # Politis-Romano: each block has geometric length with mean L.
            idx = np.empty(n, dtype=int)
            i = 0
            p = 1.0 / block_length
            while i < n:
                start = int(rng.integers(0, n))
                length = int(rng.geometric(p))
                for j in range(length):
                    if i >= n:
                        break
                    idx[i] = (start + j) % n
                    i += 1
            return idx
        raise ValueError(f"Unknown bootstrap scheme: {scheme!r}")

    rows = []
    for k in k_arr:
        point = spectral_constant_estimate(X, exposure=exposure, alpha=alpha, k=int(k))
        boots = np.empty(n_boot)
        for b in range(n_boot):
            idx = resample_indices()
            boots[b] = spectral_constant_estimate(X[idx], exposure=exposure, alpha=alpha, k=int(k))
        rows.append(
            {
                "k": int(k),
                "estimate": point,
                "lo": float(np.percentile(boots, lo_pct)),
                "hi": float(np.percentile(boots, hi_pct)),
                "se": float(np.std(boots, ddof=1)),
            }
        )
    return {
        "k": [r["k"] for r in rows],
        "estimate": np.array([r["estimate"] for r in rows]),
        "lo": np.array([r["lo"] for r in rows]),
        "hi": np.array([r["hi"] for r in rows]),
        "se": np.array([r["se"] for r in rows]),
        "scheme": scheme,
        "confidence": confidence,
    }
