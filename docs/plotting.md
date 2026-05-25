# Plotting theme

The package ships a unified matplotlib theme used by every figure script.
The theme is opinionated and publication-ready.

## Applying the theme

```python
from factortail.plotting import set_theme
set_theme(mode="paper")   # or "slides", "notebook"
```

`set_theme` configures `matplotlib.rcParams`:

- Helvetica-like sans-serif typography with STIX math.
- Soft grids (alpha 0.25, dashed) and clean spines (no top/right).
- Tight log-friendly tick marks and small markers.
- A 7-tone perceptually-uniform categorical palette
  (`FACTORTAIL_PALETTE`).

## Colors that mean things

`ESTIMATOR_COLORS` assigns a stable color to each estimator across every
figure: independent CdMC is always indigo, latent-shock always forest,
spectral always gold, hidden-cone mixture always plum. The full mapping
is in `factortail.plotting.theme.ESTIMATOR_COLORS`.

`FAMILY_COLORS` does the same for the six simulation families.

## Colormaps

`FACTORTAIL_CMAP` is a diverging blue/white/crimson colormap used for the
tail-dependence heatmaps in `F15`. The base values (indigo at 0, crimson
at 1) match `ESTIMATOR_COLORS["independent_cdmc"]` and
`ESTIMATOR_COLORS["block_cdmc"]`.

## Panel helpers

`factortail.plotting.panels` exposes a handful of reusable panel
constructors:

- `tail_loglog(ax, x, curves=..., title=...)` for log-log overlays.
- `rel_error_panel(ax, x, estimators=...)` for variance-reduction
  comparisons.
- `heatmap_panel(ax, matrix, labels=..., vmin=, vmax=)` for the
  tail-dependence and chi/eta heatmaps.
- `simplex_scatter(ax, theta, weights=...)` for the spectral simplex.
- `var_es_overlay(ax, dates, loss, var=, es=, hits=)` for the rolling
  VaR/ES dashboard.

## Saving figures

```python
from factortail.plotting import save_figure
save_figure(fig, "results/F1_tail_equivalence", formats=("pdf", "png"))
```

`save_figure` writes one file per format with consistent DPI and the
`bbox=tight` setting.
