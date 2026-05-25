"""Tests for the unified plotting theme."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from factortail.plotting import (
    ESTIMATOR_COLORS,
    FACTORTAIL_PALETTE,
    save_figure,
    set_theme,
)


def test_set_theme_applies_palette():
    set_theme()
    cycler = plt.rcParams["axes.prop_cycle"]
    colors = [d["color"] for d in cycler]
    assert colors[:3] == list(FACTORTAIL_PALETTE[:3])


def test_estimator_colors_distinct():
    estimators = list(ESTIMATOR_COLORS.values())
    assert len(set(estimators)) == len(estimators)


def test_save_figure_writes_pdf_and_png(tmp_path):
    set_theme()
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = save_figure(fig, tmp_path / "x", formats=("pdf", "png"))
    assert all(p.exists() and p.stat().st_size > 0 for p in paths)
    plt.close(fig)
