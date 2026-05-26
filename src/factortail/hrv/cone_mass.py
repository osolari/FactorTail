r"""Direct cone-mass estimator for the hidden tail scale.

For a Family-VI mixture with axis-supported first-order $\nu_1$ and a
hidden cone $\mathbb E_2$ at slower scale $\overline H_2 \in \mathrm{RV}_{-\alpha_2}$,
the cone-mass estimator at radial threshold $u$ is

$$
  \widehat{\overline H}_2(u)
  \;=\; \frac{1}{n} \sum_{t=1}^n
        \mathbf 1\{\|X_t\| > u,\ \widehat\Theta_t \in \mathbb E_2\}.
$$

Fitting :math:`\overline H_2(u) \propto u^{-\alpha_2}` on a log-spaced
grid of thresholds recovers an estimator
:math:`\widehat\alpha_2^{\text{cone}}` competitive with the Ledford–Tawn
:math:`\widehat\eta` (Theorem `def:hrv`).

Returned as a small helper consumed by ``T_sim_results_dependent``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

__all__ = ["cone_mass_alpha", "is_interior"]


def is_interior(
    angles: NDArray[np.float64],
    *,
    min_coord: float = 0.05,
    min_active: int = 2,
) -> NDArray[np.bool_]:
    r"""Mask for angles that lie in a hidden cone — i.e. at least
    ``min_active`` coordinates exceed ``min_coord``.

    The pair-cone is ``min_active=2``; full-interior is
    ``min_active=d`` (the default for ``min_active`` is 2 so that
    pair-cone designs are recognised). Coordinate axes (only one
    coordinate active) are *excluded*."""
    angles = np.asarray(angles, dtype=float)
    return (angles >= min_coord).sum(axis=1) >= min_active


def cone_mass_alpha(
    X: NDArray[np.float64],
    *,
    u_grid: NDArray[np.float64] | None = None,
    min_coord: float = 0.05,
    norm: str = "l1",
) -> dict:
    r"""Estimate $\alpha_2$ by linear regression of
    :math:`\log \widehat{\overline H}_2(u)` on :math:`\log u`.

    Returns ``dict(alpha_hat, slope, intercept, n_active, u_grid, mass)``.
    """
    X = np.asarray(X, dtype=float)
    n = X.shape[0]
    if norm == "l1":
        radii = np.abs(X).sum(axis=1)
    elif norm == "l2":
        radii = np.linalg.norm(X, axis=1)
    else:
        raise ValueError(f"unknown norm {norm!r}")
    angles = X / np.where(radii[:, None] > 0, radii[:, None], 1.0)
    interior = is_interior(angles, min_coord=min_coord)
    if u_grid is None:
        u_grid = np.geomspace(np.quantile(radii, 0.80), np.quantile(radii, 0.995), 12)
    mass = np.array([float(((radii > u) & interior).mean()) for u in u_grid])
    log_u = np.log(u_grid)
    log_mass = np.log(np.where(mass > 0, mass, 1.0 / n))
    keep = mass > 0
    if keep.sum() < 3:
        return {
            "alpha_hat": float("nan"),
            "slope": float("nan"),
            "intercept": float("nan"),
            "n_active": int(keep.sum()),
            "u_grid": u_grid,
            "mass": mass,
        }
    slope, intercept = np.polyfit(log_u[keep], log_mass[keep], deg=1)
    return {
        "alpha_hat": float(-slope),
        "slope": float(slope),
        "intercept": float(intercept),
        "n_active": int(keep.sum()),
        "u_grid": u_grid,
        "mass": mass,
    }
