"""Generate F11: common-shock geometry (P2).

For a common-shock DGP :math:`X_i = b_i Z_0 + E_i`, compare:

* the misspecified observed-coordinate independence constant
  :math:`\\sum_i b_i^\\alpha c_{Z_0}`,
* the correct latent-shock constant :math:`(\\sum_i b_i)_+^\\alpha c_{Z_0}`,
* an empirical reference from a long crude-MC simulation.
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
from factortail.dgp.family2_latent_shock import CommonShockModel
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "F11_common_shock_geometry"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 11))
    dgp = CommonShockModel.from_spec(config["common_shock"])
    constants = dgp.latent_constants()
    x_grid = np.array(config["x_grid"], dtype=float)
    n = int(config.get("n", 50_000))
    alpha = dgp.shock.alpha
    rows = []
    correct_curve = []
    misspec_curve = []
    emp_curve = []
    for i, xi in enumerate(x_grid):
        # Crude reference: simulate the sum loss directly.
        rng = spawner.rng(i)
        X = dgp.sample(n, rng)
        L = X.sum(axis=1)
        emp = float((xi < L).mean())
        # Closed-form first-order constants applied at scale ``Gbar(x) = x^-alpha``.
        gbar = xi ** (-alpha)
        correct = constants["correct_latent_constant"] * gbar
        misspec = constants["misspecified_observed_constant"] * gbar
        # CI on empirical tail (normal approximation).
        se = np.sqrt(emp * (1 - emp) / max(n, 1))
        ci_low = max(emp - 1.96 * se, 0.0)
        ci_high = emp + 1.96 * se
        attribution = "latent" if correct < misspec else "axis"
        correct_curve.append(correct)
        misspec_curve.append(misspec)
        emp_curve.append(emp)
        rows.append(
            dict(
                seed=spawner.spawned_seed(i),
                design=config.get("design", "common_shock_default"),
                x=float(xi),
                observed_constant=float(misspec),
                latent_constant=float(correct),
                empirical_tail=emp,
                ci_low=ci_low,
                ci_high=ci_high,
                attribution_class=attribution,
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F11.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    # Figure: log-log of three curves.
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    ax.loglog(x_grid, correct_curve, label="latent-shock constant", color="#188a4f")
    ax.loglog(
        x_grid, misspec_curve, label="observed-axes (misspecified)", color="#9b1f5b", linestyle="--"
    )
    ax.loglog(x_grid, emp_curve, marker="o", label="empirical", color="#1f3a93")
    ax.set_xlabel(r"threshold $x$")
    ax.set_ylabel(r"$P(L > x)$")
    ax.set_title("Common-shock geometry")
    ax.legend()
    fig_paths = save_figure(fig, results_dir / "F11_common_shock_geometry")
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
    ctx = cli("configs/F11.yaml", description="Generate F11 common-shock geometry")
    run(config=ctx.config, results_dir=ctx.results_dir)
