r"""F4 — efficiency rate ($1/\widehat\nu$) of the independent CdMC vs the
average tail index $\bar\alpha$, contrasting common-alpha designs with
heterogeneous-alpha designs.

For common-alpha designs the asymptotic floor is $1/(N^\alpha - 1)$;
larger $\alpha$ → larger $N^\alpha - 1$ → smaller rate. For
heterogeneous designs the BRE bound is governed by $\alpha_{\min}$,
so the rate should sit **below** the common-alpha curve at the same
$\bar\alpha$.
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

SCHEMA_NAME = "F4_exp_eff_vs_alpha"


def _design_marginals(alphas, scale=1.0):
    return [ParetoTail(alpha=a, scale=scale) for a in alphas]


def _rate(res) -> float:
    rel_var = res.variance / max(res.mu_hat, 1e-300) ** 2
    return float(1.0 / max(rel_var, 1e-12))


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 4))
    x = float(config.get("threshold", 20.0))
    n = int(config.get("n", 20_000))
    common_alphas = list(config.get("common_alphas", [1.5, 2.0, 2.5, 3.0, 4.0]))
    hetero_designs = config.get(
        "hetero_designs",
        [
            {"alphas": [1.5, 2.5, 3.5], "tag": "spread1"},
            {"alphas": [1.2, 2.0, 3.0], "tag": "spread2"},
            {"alphas": [1.8, 2.5, 2.7], "tag": "spread3"},
        ],
    )

    rows = []
    common_rates = []
    common_bounds = []
    hetero_rates = []
    hetero_alpha_bars = []
    hetero_alpha_mins = []
    hetero_tags = []
    for idx, a in enumerate(common_alphas):
        margs = _design_marginals([a] * 3)
        res = independent_cdmc(margs, x=x, n=n, rng=spawner.rng(idx))
        rate = _rate(res)
        kappa = float(np.log(max(1.0 / max(res.mu_hat, 1e-300), 1.0 + 1e-9)))
        common_rates.append(rate)
        common_bounds.append(1.0 / max(3.0**a - 1.0, 1e-12))
        rows.append(
            dict(
                seed=spawner.spawned_seed(idx),
                design=f"common_alpha_{a:g}",
                alpha_bar=float(a),
                alpha_min=float(a),
                n=n,
                kappa=kappa,
                lambda_n=float(rate),
                rate_hat=float(rate),
                common_alpha_flag=1,
                theory_tag=f"N^{a:g} - 1",
            )
        )
    for j, design in enumerate(hetero_designs):
        alphas = np.asarray(design["alphas"], dtype=float)
        margs = _design_marginals(alphas.tolist())
        res = independent_cdmc(margs, x=x, n=n, rng=spawner.rng(len(common_alphas) + j))
        rate = _rate(res)
        kappa = float(np.log(max(1.0 / max(res.mu_hat, 1e-300), 1.0 + 1e-9)))
        hetero_rates.append(rate)
        hetero_alpha_bars.append(float(alphas.mean()))
        hetero_alpha_mins.append(float(alphas.min()))
        hetero_tags.append(str(design.get("tag", j)))
        rows.append(
            dict(
                seed=spawner.spawned_seed(len(common_alphas) + j),
                design=f"hetero_{design.get('tag', j)}",
                alpha_bar=float(alphas.mean()),
                alpha_min=float(alphas.min()),
                n=n,
                kappa=kappa,
                lambda_n=float(rate),
                rate_hat=float(rate),
                common_alpha_flag=0,
                theory_tag="alpha_min dominates",
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F4.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.semilogy(common_alphas, common_rates, marker="o", label=r"common-$\alpha$ (CdMC)")
    ax.semilogy(
        common_alphas,
        common_bounds,
        marker="",
        linestyle=":",
        color="black",
        label=r"asymptotic floor $1/(N^\alpha-1)$",
    )
    ax.scatter(
        hetero_alpha_bars,
        hetero_rates,
        marker="s",
        s=80,
        color="#9b1f5b",
        label=r"heterogeneous-$\alpha$",
        zorder=5,
    )
    for ab, rate, amin, _tag in zip(
        hetero_alpha_bars, hetero_rates, hetero_alpha_mins, hetero_tags, strict=True
    ):
        ax.annotate(
            rf"$\alpha_{{\min}}={amin:g}$",
            xy=(ab, rate),
            xytext=(6, -3),
            textcoords="offset points",
            fontsize=8,
            color="#5d1639",
        )
    ax.set_xlabel(r"$\bar\alpha$")
    ax.set_ylabel(r"efficiency rate $1/\widehat\nu$")
    ax.set_title(rf"Rate vs $\bar\alpha$ at $x={x:g}$")
    ax.legend(loc="upper right")
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
    ctx = cli("configs/F4.yaml", description="Generate F4 efficiency vs alpha")
    run(config=ctx.config, results_dir=ctx.results_dir)
