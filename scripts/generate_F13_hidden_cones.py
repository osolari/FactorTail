"""Generate F13: hidden-cone diagnostic (P5).

Compares axis term, hidden pair-cone term, and marginal second-order term
across thresholds for a Family VI mixture.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.dgp import HiddenConeMixture
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "F13_hidden_cones"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 13))
    dgp = HiddenConeMixture.from_spec(config["hidden"])
    n = int(config.get("n", 200_000))
    x_grid = np.array(config["x_grid"], dtype=float)
    rng = spawner.rng(0)
    X = dgp.sample(n, rng)
    S = X.sum(axis=1)
    rows = []
    axis_terms = []
    hidden_terms = []
    second_orders = []
    empirical = []
    for i, xi in enumerate(x_grid):
        emp = float((xi < S).mean())
        axis_term = float((X.max(axis=1) > xi).mean())  # at least one axis exceedance
        # Hidden pair-cone term: replicate has at least two large coordinates relative to threshold.
        pair_exc = (0.5 * xi <= X).sum(axis=1) >= 2
        hidden_term = float(pair_exc.mean())
        second_order = abs(axis_term - emp)
        rows.append(
            dict(
                seed=spawner.spawned_seed(i),
                design=config.get("design", "hidden_default"),
                x=float(xi),
                axis_term=axis_term,
                hidden_pair_term=hidden_term,
                marginal_second_order=second_order,
                empirical_tail=emp,
                selected_scale=float(xi) ** (-dgp.alpha_hidden),
            )
        )
        axis_terms.append(axis_term)
        hidden_terms.append(hidden_term)
        empirical.append(emp)
        second_orders.append(second_order)
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F13.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    ax.loglog(x_grid, axis_terms, marker="o", label="axis term")
    ax.loglog(x_grid, hidden_terms, marker="s", label="hidden pair-cone term")
    ax.loglog(x_grid, empirical, marker="x", label="empirical tail")
    ax.set_xlabel(r"threshold $x$")
    ax.set_ylabel("probability")
    ax.set_title("Hidden-cone diagnostic")
    ax.legend()
    fig_paths = save_figure(fig, results_dir / "F13_hidden_cones")
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
    ctx = cli("configs/F13.yaml", description="Generate F13 hidden-cones diagnostic")
    run(config=ctx.config, results_dir=ctx.results_dir)
