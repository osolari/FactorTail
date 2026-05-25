"""Matplotlib theme: typography, color palette, colormaps, save helper."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

__all__ = [
    "ESTIMATOR_COLORS",
    "FACTORTAIL_CMAP",
    "FACTORTAIL_PALETTE",
    "FAMILY_COLORS",
    "LINESTYLES",
    "MARKERS",
    "save_figure",
    "set_theme",
]


# A perceptually-uniform categorical palette. Tested for color-vision-deficient
# observers using simulated deuteranopia at 25%.
FACTORTAIL_PALETTE: tuple[str, ...] = (
    "#1f3a93",  # indigo
    "#e8743b",  # ember
    "#188a4f",  # forest
    "#9b1f5b",  # crimson
    "#b89622",  # gold
    "#5d3b88",  # plum
    "#2e8b8b",  # teal
)


# Stable estimator <-> color mapping, used by every dashboard / overlay.
ESTIMATOR_COLORS: dict[str, str] = {
    "crude_mc": "#7f8c8d",
    "independent_cdmc": FACTORTAIL_PALETTE[0],
    "dependent_cdmc": FACTORTAIL_PALETTE[1],
    "latent_shock_cdmc": FACTORTAIL_PALETTE[2],
    "block_cdmc": FACTORTAIL_PALETTE[3],
    "spectral_cdmc": FACTORTAIL_PALETTE[4],
    "hrv_mixture": FACTORTAIL_PALETTE[5],
    "control_variate": FACTORTAIL_PALETTE[6],
    "reference": "#222222",
}


FAMILY_COLORS: dict[str, str] = {
    "Family I": FACTORTAIL_PALETTE[0],
    "Family II": FACTORTAIL_PALETTE[1],
    "Family III": FACTORTAIL_PALETTE[2],
    "Family IV": FACTORTAIL_PALETTE[3],
    "Family V": FACTORTAIL_PALETTE[4],
    "Family VI": FACTORTAIL_PALETTE[5],
}


LINESTYLES: dict[str, str] = {
    "truth": "-",
    "first_order": "--",
    "second_order": "-.",
    "empirical": ":",
    "ci": "-",
}


MARKERS: dict[str, str] = {
    "independent_cdmc": "o",
    "dependent_cdmc": "s",
    "latent_shock_cdmc": "D",
    "block_cdmc": "^",
    "spectral_cdmc": "P",
    "hrv_mixture": "X",
    "control_variate": "v",
    "crude_mc": ".",
}


# Diverging colormap centered at 0 for tail-dependence heatmaps.
FACTORTAIL_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "factortail_div",
    [
        (0.00, "#1f3a93"),
        (0.50, "#f5f5f5"),
        (1.00, "#9b1f5b"),
    ],
    N=256,
)


def set_theme(*, mode: str = "paper", grid: bool = True) -> None:
    """Apply the FactorTail matplotlib theme globally.

    Parameters
    ----------
    mode:
        ``"paper"`` (default), ``"slides"``, or ``"notebook"``.
    grid:
        If True, light dashed grid lines are enabled.
    """
    base = {
        "font.family": "sans-serif",
        "font.sans-serif": [
            "Helvetica Neue",
            "Helvetica",
            "Arial",
            "DejaVu Sans",
            "Bitstream Vera Sans",
            "sans-serif",
        ],
        "mathtext.fontset": "stix",
        "axes.titlesize": 11,
        "axes.titleweight": "semibold",
        "axes.labelsize": 10,
        "axes.linewidth": 0.9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": grid,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
        "grid.linewidth": 0.5,
        "legend.fontsize": 9,
        "legend.frameon": False,
        "legend.borderaxespad": 0.6,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3.5,
        "ytick.major.size": 3.5,
        "xtick.minor.size": 2.0,
        "ytick.minor.size": 2.0,
        "lines.linewidth": 1.6,
        "lines.markersize": 4.5,
        "savefig.bbox": "tight",
        "savefig.dpi": 200,
        "figure.dpi": 110,
        "axes.prop_cycle": plt.cycler(color=FACTORTAIL_PALETTE),
    }
    if mode == "slides":
        base.update(
            {
                "axes.titlesize": 14,
                "axes.labelsize": 13,
                "legend.fontsize": 12,
                "xtick.labelsize": 12,
                "ytick.labelsize": 12,
                "lines.linewidth": 2.0,
                "figure.dpi": 130,
            }
        )
    elif mode == "notebook":
        base.update(
            {
                "figure.dpi": 100,
                "savefig.dpi": 150,
            }
        )
    elif mode == "paper":
        pass
    else:
        raise ValueError(f"Unknown theme mode: {mode!r}")
    mpl.rcParams.update(base)


def save_figure(
    fig: plt.Figure, path: str | Path, *, formats: tuple[str, ...] = ("pdf", "png")
) -> list[Path]:
    """Save ``fig`` to one or more formats with consistent settings."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    out: list[Path] = []
    for fmt in formats:
        target = p.with_suffix(f".{fmt}")
        fig.savefig(target, format=fmt)
        out.append(target)
    return out
