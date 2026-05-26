r"""F3 — exponential efficiency rate of the independent CdMC vs threshold x.

For an unbiased estimator with relative variance $\nu(x) = \mathrm{Var}Z(x)/\mu(x)^2$,
Markov's / Bernstein-style inequalities give a per-replicate large-deviation
rate $\lambda_n(x) \approx 1/\nu(x)$. Bounded relative error (BRE) is
equivalent to $\inf_x \lambda_n(x) > 0$. The empirical
$\widehat{\mathrm{rate}}(x) = 1/\widehat\nu(x)$ tracks the LDP rate up to
the standard CLT-to-LDP correction $\kappa = \log(1/\widehat{\mu})$ that
appears in the rate normalisation:

$$
  \widehat{\mathrm{rate}}(x) = \frac{1}{\widehat\nu(x)\,\kappa(x)^2}.
$$

The figure plots $\widehat{\mathrm{rate}}(x)$ across thresholds and
overlays the finite-$N$ envelope bound $1/(N^\alpha - 1)$ (from
Proposition `prop:ind-cdmc-bre`) and its asymptotic value.
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
    # Asymptotic BRE bound.
    bound_asym = 1.0 / max(N**alpha - 1.0, 1e-12)

    rows = []
    rates = []
    bounds_finite = []
    for idx, xi in enumerate(x_grid):
        res = independent_cdmc(dgp.marginals, x=float(xi), n=n, rng=spawner.rng(idx))
        rel_var = res.variance / max(res.mu_hat, 1e-300) ** 2
        kappa = max(np.log(max(1.0 / res.mu_hat, 1.0 + 1e-9)), 1e-6)
        rate_hat = 1.0 / (rel_var * kappa**2) if rel_var > 0 else float("inf")
        # Finite-N envelope: rel_var_bound = (B(x)/mu_hat)^2 / n_eff ... use envelope.
        env = res.extra.get("envelope", float("inf"))
        rel_env = env / max(res.mu_hat, 1e-300)
        bound_finite = 1.0 / max(rel_env**2, 1e-12)
        rates.append(rate_hat)
        bounds_finite.append(bound_finite)
        rows.append(
            dict(
                seed=spawner.spawned_seed(idx),
                design=config.get("design", "default"),
                N=N,
                alpha=alpha,
                x=float(xi),
                n=n,
                kappa=float(kappa),
                rel_variance=float(rel_var),
                lambda_n=float(rate_hat * kappa**2),
                rate_hat=float(rate_hat),
                rate_bound_finite=float(bound_finite),
                rate_bound_asymptotic=float(bound_asym),
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F3.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.semilogx(x_grid, rates, marker="o", label=r"$\widehat{\mathrm{rate}}(x)$")
    ax.semilogx(x_grid, bounds_finite, marker="s", linestyle="--", label="finite-N envelope")
    ax.axhline(bound_asym, color="black", linestyle=":", label=r"asymptotic $1/(N^\alpha - 1)$")
    ax.set_xlabel(r"threshold $x$")
    ax.set_ylabel("efficiency rate")
    ax.set_title(f"Efficiency rate of independent CdMC (N={N}, $\\alpha$={alpha:g})")
    ax.legend()
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
