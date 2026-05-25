"""Unified plotting theme and figure helpers.

* :func:`set_theme` configures matplotlib rcParams for a consistent
  publication-quality look (Helvetica-like sans, soft grids, log-friendly
  ticks).
* :data:`FACTORTAIL_PALETTE` is a 7-tone categorical palette used to color
  estimators consistently across every figure.
* :data:`FACTORTAIL_CMAP` is the diverging colormap used for tail-dependence
  heatmaps.
* :data:`ESTIMATOR_COLORS` and :data:`FAMILY_COLORS` are stable
  semantic-color dictionaries used by all ``scripts/generate_*.py`` files.
"""

from factortail.plotting.theme import (
    ESTIMATOR_COLORS,
    FACTORTAIL_CMAP,
    FACTORTAIL_PALETTE,
    FAMILY_COLORS,
    LINESTYLES,
    MARKERS,
    save_figure,
    set_theme,
)

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
