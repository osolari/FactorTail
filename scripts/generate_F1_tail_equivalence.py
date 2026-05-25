"""Generate F1: independent tail-equivalence diagnostic (P1).

Plots :math:`P(S_N > x)`, the first-order sum :math:`\\sum_i P(X_i > x)`,
the corrected second-order expansion (Theorem ``thm:second-order``), and
the independent CdMC estimate with Bernstein CIs on a log-log axis.

Run:
    python scripts/generate_F1_tail_equivalence.py --config configs/F1.yaml
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
from factortail.plotting.panels import tail_loglog
from factortail.utils.regular_variation import (
    first_order_sum_tail,
    second_order_sum_tail,
)
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "F1_tail_equivalence"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    rng_spawner = SeedSpawner(master_seed=config.get("seed", 20260524))
    dgp = IndependentINID.from_specs(config["marginals"])
    x_grid = np.array(config["x_grid"], dtype=float)
    n = int(config["n"])
    rows: list[dict] = []
    cdmc_mu = []
    cdmc_lo = []
    cdmc_hi = []
    fo = first_order_sum_tail(dgp.marginals, x_grid)
    so = second_order_sum_tail(dgp.marginals, x_grid)
    for idx, xi in enumerate(x_grid):
        res = independent_cdmc(dgp.marginals, x=float(xi), n=n, rng=rng_spawner.rng(idx))
        cdmc_mu.append(res.mu_hat)
        cdmc_lo.append(res.ci_low)
        cdmc_hi.append(res.ci_high)
        rows.append(
            dict(
                seed=rng_spawner.spawned_seed(idx),
                design=config.get("design", "default"),
                x=float(xi),
                n=n,
                mu_hat=res.mu_hat,
                ci_low=res.ci_low,
                ci_high=res.ci_high,
                first_order=float(fo[idx]),
                second_order=float(so[idx]),
                runtime_seconds=res.runtime_seconds,
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(
        df,
        ctx=_Ctx(
            config_path=Path(config.get("_path", "F1.yaml")), config=config, results_dir=results_dir
        ),
    )
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    # Figure
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    tail_loglog(
        ax,
        x_grid,
        curves={
            "first_order": fo,
            "second_order": so,
            "independent_cdmc": np.asarray(cdmc_mu),
        },
        title=f"Independent tail equivalence (N={dgp.N})",
    )
    ax.fill_between(x_grid, cdmc_lo, cdmc_hi, alpha=0.2, color="#1f3a93", label="95% CI")
    ax.legend()
    fig_paths = save_figure(fig, results_dir / "F1_tail_equivalence")
    plt.close(fig)
    return [csv_path, *fig_paths]


# Lightweight RunContext shim so the script can be invoked both via the CLI
# wrapper and via the dispatcher.
class _Ctx:
    def __init__(self, *, config_path: Path, config: dict, results_dir: Path):
        from factortail.utils.hashing import config_hash

        self.config_path = config_path
        self.config = config
        self.results_dir = results_dir
        self.run_id = config.get("run_id", config_path.stem)
        self.config_hash = config_hash(config)


if __name__ == "__main__":
    ctx = cli("configs/F1.yaml", description="Generate F1 tail-equivalence diagnostic")
    run(config=ctx.config, results_dir=ctx.results_dir)
