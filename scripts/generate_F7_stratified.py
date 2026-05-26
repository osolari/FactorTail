r"""F7 — stratified CdMC vs unstratified.

The independent CdMC kernel is a sum over coordinates
$Z = \sum_i \overline F_i(T_i)$. Post-stratification by the empirical
argmax index $i^\star = \arg\max_i X_i$ writes

$$
  \widehat\mu = \sum_i \pi_i \,\bar Z_i,
$$

with $\pi_i = n_i/n$ the **stratum probability** estimated on the
sample and $\bar Z_i$ the within-stratum sample mean. This is the
*unbiased* estimator for any sampling allocation $(n_1, \dots, n_K)$.

The **Neyman allocation** is the variance-minimising choice
$n_i \propto \sqrt{\mathrm{Var}(Z \mid R = i)}$, but it controls
*allocation*, not the estimator's averaging weights. We compare:

- **Unstratified**: $\bar Z = n^{-1}\sum_m Z_m$.
- **Post-stratified (proportional)**: same draw, partition by
  $i^\star$, average within strata using $\pi_i = n_i/n$. The
  estimator is identical to unstratified in expectation; the
  *variance* can differ because the within-stratum variances are
  pooled.
- **Neyman-allocated**: a pilot estimates $\sigma_i$; we then draw a
  fresh second pass with $n_i^{\mathrm{Neyman}} \propto \sigma_i$
  samples per stratum (rejection-sampled from the joint), and
  average with $\pi_i^{\mathrm{Neyman}} = n_i^{\mathrm{Neyman}}/n$
  evaluated under the *pilot's* $\pi_i$ for unbiasedness.

Runtime is measured for the *full pipeline* (sampler + kernel +
aggregation).
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


def _kernel(dgp: IndependentINID, x: float, n: int, rng):
    X = np.column_stack([m.rvs(n, rng) for m in dgp.marginals])
    T = _T_values(X, x)
    kernel = np.column_stack([m.sf(T[:, i]) for i, m in enumerate(dgp.marginals)])
    return X, kernel.sum(axis=1)


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 7))
    dgp = IndependentINID.from_specs(config["marginals"])
    x = float(config["x"])
    N = dgp.N
    alpha = float(dgp.marginals[0].alpha)
    n = int(config.get("n", 30_000))

    # 1. Unstratified — full pipeline timed.
    with runtime_seconds() as t_un:
        rng_un = spawner.rng(0)
        X_un, Z_un = _kernel(dgp, x, n, rng_un)
        mu_un = float(Z_un.mean())
        var_un_per_rep = float(Z_un.var(ddof=1))
    runtime_un = float(t_un[0])
    se_un = float(np.sqrt(var_un_per_rep / n))

    # 2. Post-stratification on the same draw — almost-zero added cost.
    with runtime_seconds() as t_post:
        rng_post = spawner.rng(0)  # same seed for fair compare
        X_post, Z_post = _kernel(dgp, x, n, rng_post)
        R_post = X_post.argmax(axis=1)
        # Stratum means + within-stratum variances + stratum probabilities.
        means = np.zeros(N)
        within_var = np.zeros(N)
        pi = np.zeros(N)
        for i in range(N):
            mask = R_post == i
            count = int(mask.sum())
            pi[i] = count / n
            if count > 1:
                means[i] = float(Z_post[mask].mean())
                within_var[i] = float(Z_post[mask].var(ddof=1))
        mu_post = float(np.sum(pi * means))
        # Variance of the post-stratified mean: sum(pi^2 * within_var / n_i).
        with np.errstate(divide="ignore", invalid="ignore"):
            var_post = float(
                np.sum(np.where(pi * n >= 2, pi**2 * within_var / np.maximum(pi * n, 1), 0.0))
            )
    runtime_post = float(t_post[0])
    se_post = float(np.sqrt(var_post))

    # 3. Neyman-allocated second-pass. Estimate sigma_i on the pilot,
    # allocate fresh draws proportional to sigma_i, then average using
    # the pilot's pi for unbiasedness.
    with runtime_seconds() as t_ney:
        sigma_hat = np.sqrt(np.maximum(within_var, 0.0))
        if sigma_hat.sum() > 0:
            alloc = sigma_hat / sigma_hat.sum()
        else:
            alloc = np.ones(N) / N
        n_alloc = np.round(alloc * n).astype(int)
        n_alloc = np.maximum(n_alloc, 1)
        rng_ney = spawner.rng(1)
        means_ney = np.zeros(N)
        var_ney = np.zeros(N)
        # Rejection sample: draw from joint, keep replicates with argmax == i,
        # until we have n_alloc[i] for each i.
        oversample = 5
        for i in range(N):
            buf = []
            while sum(len(b) for b in buf) < n_alloc[i]:
                Xb, Zb = _kernel(dgp, x, n_alloc[i] * oversample, rng_ney)
                mask_i = Xb.argmax(axis=1) == i
                buf.append(Zb[mask_i])
                oversample = min(oversample * 2, 256)
            Z_i = np.concatenate(buf)[: n_alloc[i]]
            means_ney[i] = float(Z_i.mean())
            var_ney[i] = float(Z_i.var(ddof=1)) if len(Z_i) > 1 else 0.0
        # Estimator: weight by *pilot* pi (unbiased under the joint).
        mu_ney = float(np.sum(pi * means_ney))
        var_ney_total = float(
            np.sum(np.where(n_alloc >= 2, pi**2 * var_ney / np.maximum(n_alloc, 1), 0.0))
        )
    runtime_ney = float(t_ney[0])
    se_ney = float(np.sqrt(var_ney_total))

    seed_val = spawner.spawned_seed(0)
    design = config.get("design", "default")
    rows = [
        dict(
            seed=seed_val,
            design=design,
            N=N,
            alpha=alpha,
            x=x,
            n=n,
            estimator="unstratified_cdmc",
            mu_hat=mu_un,
            variance=var_un_per_rep,
            work_norm_variance=float((var_un_per_rep / n) * runtime_un),
            tail_evals_per_rep=N,
            runtime_seconds=runtime_un,
            weight_rule="none",
        ),
        dict(
            seed=seed_val,
            design=design,
            N=N,
            alpha=alpha,
            x=x,
            n=n,
            estimator="post_stratified",
            mu_hat=mu_post,
            variance=var_post * n,  # back to per-replicate scale
            work_norm_variance=float(var_post * runtime_post),
            tail_evals_per_rep=N,
            runtime_seconds=runtime_post,
            weight_rule="proportional",
        ),
        dict(
            seed=seed_val,
            design=design,
            N=N,
            alpha=alpha,
            x=x,
            n=int(n_alloc.sum()),
            estimator="neyman_allocated",
            mu_hat=mu_ney,
            variance=var_ney_total * n_alloc.sum(),
            work_norm_variance=float(var_ney_total * runtime_ney),
            tail_evals_per_rep=N,
            runtime_seconds=runtime_ney,
            weight_rule="neyman",
        ),
    ]
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F7.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.0), constrained_layout=True)
    colors = ["#7f8c8d", "#188a4f", "#1f3a93"]
    se = np.array([se_un, se_post, se_ney])
    mu = np.array([mu_un, mu_post, mu_ney])
    labels = ["unstratified", "post-stratified", "Neyman-allocated"]
    axes[0].errorbar(labels, mu, yerr=2 * se, fmt="o", capsize=4, color="#1f3a93")
    axes[0].set_ylabel(r"$\widehat\mu \pm 2\,\mathrm{SE}$")
    axes[0].set_title("Estimator means (must agree)")
    axes[0].tick_params(axis="x", rotation=15)
    axes[1].bar(labels, [r["work_norm_variance"] for r in rows], color=colors)
    axes[1].set_ylabel("work-normalised variance (s)")
    axes[1].set_title("Efficiency: lower is better")
    axes[1].tick_params(axis="x", rotation=15)
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
