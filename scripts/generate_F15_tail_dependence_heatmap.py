"""Generate F15: tail-dependence heatmap from real (or synthetic) FF data."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import matplotlib.pyplot as plt
import numpy as np

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.diagnostics import pairwise_dependence_table
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.plotting.panels import heatmap_panel
from factortail.real_data import load_fama_french

SCHEMA_NAME = "F15_tail_dependence_heatmap"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    panel = load_fama_french(
        name=config.get("panel", "FF3_daily"),
        offline=config.get("offline", True),
        n_synthetic=int(config.get("n_synthetic", 5000)),
        rng_seed=int(config.get("seed", 15)),
    )
    factors = panel.data.drop(columns=["RF"], errors="ignore").to_numpy()
    column_names = [c for c in panel.data.columns if c != "RF"]
    table = pairwise_dependence_table(
        factors,
        threshold_u=float(config.get("threshold_u", 0.95)),
        eta_k=int(config.get("eta_k", 50)),
        column_names=column_names,
    )
    # Clustering: simple chi-based cut at the median.
    chi_median = float(table["chi_hat"].median())
    table["cluster"] = (table["chi_hat"] > chi_median).astype(int).astype(str)
    table["selected_block"] = table["cluster"]
    table["data_vintage"] = panel.vintage
    table = stamp_provenance(table, ctx=_Ctx(Path("F15.yaml"), config, results_dir))
    csv_path = write_csv(
        table, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    # Heatmap
    d = len(column_names)
    chi_mat = np.eye(d)
    eta_mat = np.eye(d)
    for _, row in table.iterrows():
        i = column_names.index(row["factor_i"])
        j = column_names.index(row["factor_j"])
        chi_mat[i, j] = chi_mat[j, i] = row["chi_hat"]
        eta_mat[i, j] = eta_mat[j, i] = row["eta_hat"]
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.5))
    heatmap_panel(axes[0], chi_mat, labels=column_names, title=r"$\chi$ matrix", vmin=0.0, vmax=1.0)
    heatmap_panel(axes[1], eta_mat, labels=column_names, title=r"$\eta$ matrix", vmin=0.5, vmax=1.0)
    fig_paths = save_figure(fig, results_dir / "F15_tail_dependence_heatmap")
    plt.close(fig)
    return [csv_path, *fig_paths]


class _Ctx:
    def __init__(self, p, c, r):
        from factortail.utils.hashing import config_hash

        self.config_path = p
        self.config = c
        self.results_dir = r
        self.run_id = c.get("run_id", p.stem)
        self.config_hash = config_hash(c)


if __name__ == "__main__":
    ctx = cli("configs/F15.yaml", description="Generate F15 tail-dependence heatmap")
    run(config=ctx.config, results_dir=ctx.results_dir)
