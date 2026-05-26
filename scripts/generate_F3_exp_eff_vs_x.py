r"""F3 — efficiency rate of the independent CdMC vs threshold $x$.

The exponential efficiency rate is the inverse of the relative variance,

.. math::
    \widehat{\mathrm{rate}}(x) \;=\; 1 / \widehat\nu(x), \qquad
    \widehat\nu(x) = \widehat{\mathrm{Var}} Z(x) / \widehat\mu(x)^2.

Under BRE, $\widehat\nu \to V^* < \infty$ so the rate is bounded
*below* by $1/V^*$. For independent CdMC the BRE bound is
$V^* = N^\alpha - 1$ (Proposition `prop:ind-cdmc-bre`), so the
asymptotic rate floor is $1/(N^\alpha - 1)$.

For comparison we also plot $1/\nu_{\mathrm{crude}}(x) = \mu(x)/(1-\mu(x))$,
the relative-variance reciprocal of *crude* Monte Carlo, which decays
to 0 as $x\to\infty$. The CdMC's bounded floor sitting above the crude
curve is the headline efficiency claim.
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
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "F3_exp_eff_vs_x"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 3))
    dgp = IndependentINID.from_specs(config["marginals"])
    x_grid = np.array(config["x_grid"], dtype=float)
    n = int(config.get("n", 20_000))
    N = dgp.N
    alpha = float(dgp.marginals[0].alpha)
    # Asymptotic BRE rate floor for independent CdMC.
    rate_asym = 1.0 / max(N**alpha - 1.0, 1e-12)

    rows = []
    rates = []
    rates_crude = []
    bounds_finite = []
    for idx, xi in enumerate(x_grid):
        res = independent_cdmc(dgp.marginals, x=float(xi), n=n, rng=spawner.rng(idx))
        rel_var = res.variance / max(res.mu_hat, 1e-300) ** 2
        rate_hat = 1.0 / max(rel_var, 1e-12)
        # Crude MC rate: 1 / [Var(Bernoulli)/μ^2] = μ / (1 - μ).
        rate_crude = res.mu_hat / max(1.0 - res.mu_hat, 1e-12)
        # Finite-N envelope: B(x)/μ̂ bounds the relative envelope ratio.
        env = res.extra.get("envelope", float("inf"))
        rel_env = env / max(res.mu_hat, 1e-300)
        bound_finite = 1.0 / max(rel_env**2, 1e-12)
        # Kappa retained for schema back-compat.
        kappa = float(np.log(max(1.0 / max(res.mu_hat, 1e-300), 1.0 + 1e-9)))
        rates.append(rate_hat)
        rates_crude.append(rate_crude)
        bounds_finite.append(bound_finite)
        rows.append(
            dict(
                seed=spawner.spawned_seed(idx),
                design=config.get("design", "default"),
                N=N,
                alpha=alpha,
                x=float(xi),
                n=n,
                kappa=kappa,
                rel_variance=float(rel_var),
                lambda_n=float(rate_hat),
                rate_hat=float(rate_hat),
                rate_bound_finite=float(bound_finite),
                rate_bound_asymptotic=float(rate_asym),
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F3.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.loglog(x_grid, rates, marker="o", label=r"$1/\widehat\nu(x)$  (independent CdMC)")
    ax.loglog(
        x_grid,
        rates_crude,
        marker="x",
        linestyle="--",
        color="#7f8c8d",
        label=r"$\mu/(1-\mu)$  (crude MC)",
    )
    ax.axhline(
        rate_asym,
        color="black",
        linestyle=":",
        linewidth=1.0,
        label=rf"asymptotic floor $1/(N^\alpha-1)={rate_asym:.3g}$",
    )
    ax.set_xlabel(r"threshold $x$")
    ax.set_ylabel(r"efficiency rate $1/\nu$")
    ax.set_title(rf"Efficiency rate of independent CdMC (N={N}, $\alpha$={alpha:g})")
    ax.legend(loc="lower right")
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
    ctx = cli("configs/F3.yaml", description="Generate F3 efficiency rate vs x")
    run(config=ctx.config, results_dir=ctx.results_dir)
