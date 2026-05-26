r"""F2 — P(M_N > x) / P(S_N > x) under independent regular variation.

Verifies the manuscript's `thm:catastrophe-exact` and `thm:sum-equivalence`:
both probabilities are asymptotically $\sim C \overline G(x)$, so the
ratio approaches 1 in the deep tail. At moderate thresholds the sum is
larger than the maximum (many medium configurations contribute).
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
from factortail.dgp import IndependentINID
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "F2_max_vs_sum"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 2))
    dgp = IndependentINID.from_specs(config["marginals"])
    x_grid = np.array(config["x_grid"], dtype=float)
    n = int(config.get("n", 200_000))

    rows = []
    p_max_list = []
    p_sum_list = []
    ratio_list = []
    for idx, xi in enumerate(x_grid):
        rng = spawner.rng(idx)
        X = dgp.sample(n, rng)
        M = X.max(axis=1)
        S = X.sum(axis=1)
        p_max = float((xi < M).mean())
        p_sum = float((xi < S).mean())
        se_max = float(np.sqrt(max(p_max * (1 - p_max), 1e-12) / n))
        se_sum = float(np.sqrt(max(p_sum * (1 - p_sum), 1e-12) / n))
        ratio = p_max / max(p_sum, 1e-300)
        # CI on the ratio via the delta method.
        if p_max > 0 and p_sum > 0:
            var_log = (se_max / p_max) ** 2 + (se_sum / p_sum) ** 2
            half = 1.96 * np.sqrt(var_log)
            ci_low = ratio * np.exp(-half)
            ci_high = ratio * np.exp(half)
        else:
            ci_low, ci_high = float("nan"), float("nan")
        rows.append(
            dict(
                seed=spawner.spawned_seed(idx),
                design=config.get("design", "default"),
                N=dgp.N,
                alpha=float(dgp.marginals[0].alpha),
                x=float(xi),
                n=n,
                p_max=p_max,
                p_sum=p_sum,
                ratio=ratio,
                ci_low=float(ci_low),
                ci_high=float(ci_high),
                truth_method="crude_mc",
            )
        )
        p_max_list.append(p_max)
        p_sum_list.append(p_sum)
        ratio_list.append(ratio)
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F2.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.0), constrained_layout=True)
    axes[0].loglog(x_grid, p_max_list, marker="o", label=r"$P(M_N > x)$")
    axes[0].loglog(x_grid, p_sum_list, marker="s", label=r"$P(S_N > x)$")
    axes[0].set_xlabel(r"$x$")
    axes[0].set_ylabel("probability")
    axes[0].set_title("Maximum vs sum")
    axes[0].legend()
    axes[1].semilogx(x_grid, ratio_list, marker="D", color="#188a4f")
    axes[1].axhline(1.0, color="black", linestyle="--", linewidth=0.8)
    axes[1].set_xlabel(r"$x$")
    axes[1].set_ylabel(r"$P(M_N > x)\,/\,P(S_N > x)$")
    axes[1].set_title("Catastrophe ratio")
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
    ctx = cli("configs/F2.yaml", description="Generate F2 max vs sum")
    run(config=ctx.config, results_dir=ctx.results_dir)
