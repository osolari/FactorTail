r"""F7 — stratified CdMC vs unstratified.

The independent CdMC kernel is a sum over coordinates
$Z = \sum_i \overline F_i(T_i)$. Stratification by the empirical
argmax index $i^\star = \arg\max_i X_i$ replaces the joint sample mean
by a weighted average

$$
  \widehat\mu_{\text{strat}} = \sum_i w_i \, \mathbb E[Z \mid R = i],
$$

with $w_i$ either the true partition mass (proportional sampling) or
the Neyman-optimal weights $w_i \propto \sqrt{\mathrm{Var}(Z \mid R=i)}$.
Work-normalized variance is reported alongside raw variance.
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
from factortail.cdmc.independent import _T_values
from factortail.dgp import IndependentINID
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.utils.seeds import SeedSpawner
from factortail.utils.timing import runtime_seconds

SCHEMA_NAME = "F7_stratified"


def _kernel_per_replicate(dgp: IndependentINID, x: float, n: int, rng):
    X = np.column_stack([m.rvs(n, rng) for m in dgp.marginals])
    T = _T_values(X, x)
    kernel = np.column_stack([m.sf(T[:, i]) for i, m in enumerate(dgp.marginals)])
    return X, kernel


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 7))
    dgp = IndependentINID.from_specs(config["marginals"])
    x = float(config["x"])
    N = dgp.N
    alpha = float(dgp.marginals[0].alpha)
    n = int(config.get("n", 30_000))

    rng = spawner.rng(0)
    with runtime_seconds() as elapsed_unstrat:
        X, kernel = _kernel_per_replicate(dgp, x, n, rng)
        Z_un = kernel.sum(axis=1)
        mu_un = float(Z_un.mean())
        var_un = float(Z_un.var(ddof=1))

    # Stratification by empirical argmax.
    R = X.argmax(axis=1)
    rows = []
    rows.append(
        dict(
            seed=spawner.spawned_seed(0),
            design=config.get("design", "default"),
            N=N,
            alpha=alpha,
            x=x,
            n=n,
            estimator="unstratified_cdmc",
            mu_hat=mu_un,
            variance=var_un,
            work_norm_variance=float(var_un * elapsed_unstrat[0]),
            tail_evals_per_rep=N,
            runtime_seconds=float(elapsed_unstrat[0]),
            weight_rule="none",
        )
    )

    # Proportional stratification.
    with runtime_seconds() as elapsed_prop:
        means = np.zeros(N)
        variances = np.zeros(N)
        weights_prop = np.zeros(N)
        for i in range(N):
            mask = i == R
            count = int(mask.sum())
            if count > 1:
                Z_i = Z_un[mask]
                means[i] = float(Z_i.mean())
                variances[i] = float(Z_i.var(ddof=1))
                weights_prop[i] = count / n
        mu_prop = float(np.sum(weights_prop * means))
        var_prop = float(np.sum(weights_prop**2 * variances / np.maximum(weights_prop * n, 1)))
    rows.append(
        dict(
            seed=spawner.spawned_seed(0),
            design=config.get("design", "default"),
            N=N,
            alpha=alpha,
            x=x,
            n=n,
            estimator="proportional_stratified",
            mu_hat=mu_prop,
            variance=float(var_prop * n),  # back to per-replicate scale
            work_norm_variance=float(var_prop * n * elapsed_prop[0]),
            tail_evals_per_rep=N,
            runtime_seconds=float(elapsed_prop[0]),
            weight_rule="proportional",
        )
    )

    # Neyman-optimal weights (using the same single-pass estimates).
    with runtime_seconds() as elapsed_neyman:
        sd = np.sqrt(np.maximum(variances, 0.0))
        if sd.sum() > 0:
            weights_neyman = sd / sd.sum()
        else:
            weights_neyman = np.ones(N) / N
        mu_neyman = float(np.sum(weights_neyman * means))
        var_neyman = float(np.sum(weights_neyman**2 * variances / np.maximum(weights_prop * n, 1)))
    rows.append(
        dict(
            seed=spawner.spawned_seed(0),
            design=config.get("design", "default"),
            N=N,
            alpha=alpha,
            x=x,
            n=n,
            estimator="neyman_stratified",
            mu_hat=mu_neyman,
            variance=float(var_neyman * n),
            work_norm_variance=float(var_neyman * n * elapsed_neyman[0]),
            tail_evals_per_rep=N,
            runtime_seconds=float(elapsed_neyman[0]),
            weight_rule="neyman",
        )
    )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F7.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.bar(df["estimator"], df["work_norm_variance"], color=["#7f8c8d", "#188a4f", "#1f3a93"])
    ax.set_ylabel("work-normalized variance")
    ax.set_title("Stratified CdMC efficiency")
    ax.tick_params(axis="x", rotation=15)
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
    ctx = cli("configs/F7.yaml", description="Generate F7 stratified diagnostic")
    run(config=ctx.config, results_dir=ctx.results_dir)
