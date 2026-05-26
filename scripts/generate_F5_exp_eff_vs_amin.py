r"""F5 — efficiency rate vs the minimum tail index $\alpha_{\min}$ in
heterogeneous Pareto sums.

Sweeps $\alpha_{\min}$ on a grid while holding $\bar\alpha$ approximately
fixed; the BRE bound is governed by $\alpha_{\min}$ rather than the
average. The figure is the companion of F4.
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
from factortail.cdmc import independent_cdmc
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.utils.seeds import SeedSpawner
from factortail.utils.tails import ParetoTail

SCHEMA_NAME = "F5_exp_eff_vs_amin"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 5))
    x = float(config.get("threshold", 20.0))
    n = int(config.get("n", 20_000))
    a_max = float(config.get("alpha_max", 5.0))
    amin_grid = list(config.get("alpha_min_grid", [1.2, 1.5, 1.8, 2.2, 2.6, 3.0]))

    rows = []
    rates = []
    for idx, amin in enumerate(amin_grid):
        # Build a 3-component design with one alpha_min and two alpha_max.
        alphas = [amin, a_max, a_max]
        margs = [ParetoTail(alpha=a, scale=1.0) for a in alphas]
        res = independent_cdmc(margs, x=x, n=n, rng=spawner.rng(idx))
        rel_var = res.variance / max(res.mu_hat, 1e-300) ** 2
        kappa = max(np.log(max(1.0 / res.mu_hat, 1.0 + 1e-9)), 1e-6)
        rate = 1.0 / (rel_var * kappa**2) if rel_var > 0 else float("inf")
        rates.append(rate)
        rows.append(
            dict(
                seed=spawner.spawned_seed(idx),
                design=f"amin_{amin:g}",
                alpha_bar=float(np.mean(alphas)),
                alpha_min=float(amin),
                n=n,
                kappa=float(kappa),
                lambda_n=float(rate * kappa**2),
                rate_hat=float(rate),
                common_alpha_flag=0,
                theory_tag="alpha_min dominates",
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F5.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.semilogy(amin_grid, rates, marker="o")
    ax.set_xlabel(r"$\alpha_{\min}$")
    ax.set_ylabel("efficiency rate")
    ax.set_title(rf"Rate vs $\alpha_{{\min}}$ at $x={x:g}$ ($\alpha_{{\max}}={a_max:g}$)")
    fig_paths = save_figure(fig, results_dir / SCHEMA_NAME)
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
    ctx = cli("configs/F5.yaml", description="Generate F5 efficiency vs alpha_min")
    run(config=ctx.config, results_dir=ctx.results_dir)
