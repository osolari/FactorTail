"""Generate F8: corrected second-order independent expansion diagnostic.

Compares first-order error and corrected second-order error against a
high-precision reference. The reference uses crude MC at a very large
budget for the modest threshold range chosen in the config.
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
from factortail.dgp import IndependentINID
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.utils.regular_variation import (
    first_order_sum_tail,
    second_order_sum_tail,
)
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "F8_second_order"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 8))
    dgp = IndependentINID.from_specs(config["marginals"])
    x_grid = np.array(config["x_grid"], dtype=float)
    n_ref = int(config.get("n_reference", 200_000))
    fo = first_order_sum_tail(dgp.marginals, x_grid)
    so = second_order_sum_tail(dgp.marginals, x_grid)
    rows = []
    for i, xi in enumerate(x_grid):
        res = independent_cdmc(dgp.marginals, x=float(xi), n=n_ref, rng=spawner.rng(i))
        mu = res.mu_hat
        rows.append(
            dict(
                seed=spawner.spawned_seed(i),
                design=config.get("design", "default"),
                x=float(xi),
                first_order_error=float((fo[i] - mu) / mu) if mu > 0 else float("nan"),
                second_order_error=float((so[i] - mu) / mu) if mu > 0 else float("nan"),
                leave_one_out_term=float(so[i] - fo[i]),
                remainder_estimate=float(mu - so[i]),
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F8.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    ax.semilogy(
        x_grid, np.abs(df["first_order_error"]), marker="o", label="first-order |rel error|"
    )
    ax.semilogy(
        x_grid, np.abs(df["second_order_error"]), marker="s", label="second-order |rel error|"
    )
    ax.set_xlabel(r"threshold $x$")
    ax.set_ylabel(r"|relative error|")
    ax.set_title("Second-order independent expansion")
    ax.legend()
    fig_paths = save_figure(fig, results_dir / "F8_second_order")
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
    ctx = cli("configs/F8.yaml", description="Generate F8 second-order diagnostic")
    run(config=ctx.config, results_dir=ctx.results_dir)
