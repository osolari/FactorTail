"""Reusable panel helpers shared by every ``scripts/generate_*.py``."""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np

from factortail.plotting.theme import (
    ESTIMATOR_COLORS,
    FACTORTAIL_CMAP,
    LINESTYLES,
    MARKERS,
)

__all__ = [
    "tail_loglog",
    "rel_error_panel",
    "heatmap_panel",
    "simplex_scatter",
    "var_es_overlay",
]


def tail_loglog(
    ax: plt.Axes,
    x: np.ndarray,
    curves: dict[str, np.ndarray],
    *,
    title: str = "",
    ylabel: str = r"$P(L > x)$",
    xlabel: str = r"$x$",
) -> None:
    """Plot multiple tail-probability curves on a log-log scale."""
    for name, y in curves.items():
        color = ESTIMATOR_COLORS.get(name, None)
        ls = LINESTYLES.get(name, "-")
        marker = MARKERS.get(name, "")
        ax.loglog(x, y, color=color, linestyle=ls, marker=marker, label=name)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()


def rel_error_panel(
    ax: plt.Axes,
    x: np.ndarray,
    estimators: dict[str, np.ndarray],
    *,
    title: str = "Relative error vs threshold",
) -> None:
    for name, y in estimators.items():
        ax.semilogy(
            x,
            np.abs(y),
            color=ESTIMATOR_COLORS.get(name, None),
            marker=MARKERS.get(name, "o"),
            label=name,
        )
    ax.set_title(title)
    ax.set_xlabel("threshold $x$")
    ax.set_ylabel("|relative error|")
    ax.legend()


def heatmap_panel(
    ax: plt.Axes,
    matrix: np.ndarray,
    *,
    labels: Sequence[str],
    title: str = "",
    vmin: float = -1.0,
    vmax: float = 1.0,
) -> None:
    img = ax.imshow(matrix, cmap=FACTORTAIL_CMAP, vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    ax.set_title(title)
    ax.figure.colorbar(img, ax=ax, shrink=0.8)


def simplex_scatter(
    ax: plt.Axes,
    theta: np.ndarray,
    *,
    weights: np.ndarray | None = None,
    title: str = "Empirical spectral measure on simplex",
) -> None:
    """Project a 3D simplex onto 2D barycentric coordinates and scatter."""
    if theta.shape[1] != 3:
        raise ValueError("simplex_scatter expects (n, 3) angles on the 2-simplex")
    # Barycentric to Cartesian
    e1 = np.array([0.0, 0.0])
    e2 = np.array([1.0, 0.0])
    e3 = np.array([0.5, np.sqrt(3.0) / 2.0])
    pts = theta @ np.vstack([e1, e2, e3])
    sizes = 8 + 80 * (weights / weights.max() if weights is not None else np.ones(len(theta)))
    ax.scatter(pts[:, 0], pts[:, 1], s=sizes, c=ESTIMATOR_COLORS["spectral_cdmc"], alpha=0.7)
    # Simplex outline
    outline = np.vstack([e1, e2, e3, e1])
    ax.plot(outline[:, 0], outline[:, 1], color="black", linewidth=0.8)
    ax.set_axis_off()
    ax.set_title(title)
    ax.set_aspect("equal")


def var_es_overlay(
    ax: plt.Axes,
    dates: np.ndarray,
    loss: np.ndarray,
    *,
    var: np.ndarray,
    es: np.ndarray,
    hits: np.ndarray | None = None,
) -> None:
    ax.plot(dates, loss, color="#444444", linewidth=0.8, label="realized loss")
    ax.plot(dates, var, color=ESTIMATOR_COLORS["independent_cdmc"], label="VaR")
    ax.plot(dates, es, color=ESTIMATOR_COLORS["spectral_cdmc"], label="ES")
    if hits is not None and hits.any():
        ax.scatter(
            dates[hits.astype(bool)],
            loss[hits.astype(bool)],
            color=ESTIMATOR_COLORS["hrv_mixture"],
            marker="x",
            s=24,
            label="exception",
        )
    ax.set_xlabel("date")
    ax.set_ylabel("loss")
    ax.legend(loc="upper left")
