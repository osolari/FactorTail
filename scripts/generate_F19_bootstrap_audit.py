r"""F19 — bootstrap-scheme audit for the empirical spectral constant
(handoff open question Q4).

Stationary heavy-tailed test process: an AR(1) on Pareto-radial / Dirichlet-
angular MRV draws. The **true** linear-risk constant is computable in closed
form for the Pareto-radial / Dirichlet-angular DGP via the formula

$$
  C_\ell = E[(\ell(\Theta)_+)^\alpha].
$$

For each of the three bootstrap schemes (iid, block, stationary) we record:

- the point estimate of $\widehat C_\ell(u)$ at threshold $k$,
- the 95% percentile band,
- the bootstrap SE,
- whether the true constant is covered.

The figure overlays coverage proportions across the k-grid for each scheme.
"""

from __future__ import annotations

import sys
from math import gamma
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.dgp import RadialAngularMRV
from factortail.diagnostics import bootstrap_bands
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "F19_bootstrap_audit"


def _true_spectral_constant(alpha: float, exposure: np.ndarray, concentration: np.ndarray) -> float:
    r"""Closed-form $E[(\ell(\Theta)_+)^\alpha]$ for symmetric exposure with
    a single non-degenerate concentration vector; we estimate it by a
    very-high-budget Monte Carlo because the closed form for a general
    exposure × Dirichlet is not analytical."""
    rng = np.random.default_rng(0)
    Theta = rng.dirichlet(concentration, size=200_000)
    y_pos = np.maximum(Theta @ exposure, 0.0)
    return float(np.mean(y_pos**alpha))


def _ar1_resample(X: np.ndarray, rho: float, rng: np.random.Generator) -> np.ndarray:
    """Inject simple AR(1) auto-correlation: ``X_t' = rho * X_{t-1}' + sqrt(1-rho^2)*X_t``.

    Preserves marginal mass (approximately) while introducing serial
    dependence — a clean stress test for the bootstrap schemes.
    """
    n, d = X.shape
    Y = np.zeros_like(X)
    Y[0] = X[0]
    for t in range(1, n):
        Y[t] = rho * Y[t - 1] + np.sqrt(max(1 - rho**2, 0.0)) * X[t]
    return Y


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 19))
    alpha = float(config.get("alpha", 2.0))
    dim = int(config.get("dim", 3))
    concentration = np.asarray(config.get("concentration", [2.0] * dim), dtype=float)
    exposure = np.asarray(config.get("exposure", [1.0, 2.0, 0.5]), dtype=float)
    n = int(config.get("n", 4000))
    rho = float(config.get("ar_rho", 0.4))
    k_grid = list(config.get("k_grid", [80, 160, 320, 640]))
    n_boot = int(config.get("n_boot", 300))
    schemes = list(config.get("schemes", ["iid", "block", "stationary"]))
    block_length = int(config.get("block_length", 30))

    true_C = _true_spectral_constant(alpha, exposure, concentration)

    rng = spawner.rng(0)
    dgp = RadialAngularMRV(
        alpha=alpha,
        angular_kind="dirichlet",
        angular_params={"concentration": concentration.tolist()},
        dim=dim,
    )
    X_iid = dgp.sample(n, rng)
    X = _ar1_resample(X_iid, rho=rho, rng=rng)

    rows = []
    coverage = {s: [] for s in schemes}
    for scheme in schemes:
        res = bootstrap_bands(
            X,
            exposure=exposure,
            alpha=alpha,
            k_grid=k_grid,
            n_boot=n_boot,
            scheme=scheme,
            block_length=block_length,
            seed=int(spawner.spawned_seed(1) % (2**31)),
        )
        for j, k in enumerate(k_grid):
            est = float(res["estimate"][j])
            lo = float(res["lo"][j])
            hi = float(res["hi"][j])
            covered = int(lo <= true_C <= hi)
            coverage[scheme].append(covered)
            rows.append(
                dict(
                    seed=spawner.spawned_seed(j),
                    design=config.get("design", "ar1_pareto_dirichlet"),
                    scheme=scheme,
                    block_length=block_length if scheme != "iid" else 0,
                    k=int(k),
                    true_constant=true_C,
                    estimate=est,
                    lo=lo,
                    hi=hi,
                    se=float(res["se"][j]),
                    covered=covered,
                    n_boot=n_boot,
                )
            )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F19.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.0), constrained_layout=True)
    for scheme in schemes:
        sub = df[df["scheme"] == scheme].sort_values("k")
        axes[0].errorbar(
            sub["k"],
            sub["estimate"],
            yerr=[sub["estimate"] - sub["lo"], sub["hi"] - sub["estimate"]],
            marker="o",
            label=scheme,
            capsize=3,
        )
    axes[0].axhline(true_C, color="black", linestyle="--", linewidth=0.8, label=r"true $C_\ell$")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel(r"$\widehat C_\ell(k)$ with 95% band")
    axes[0].set_title("Estimate vs k by scheme")
    axes[0].legend()
    for scheme in schemes:
        sub = df[df["scheme"] == scheme].sort_values("k")
        axes[1].plot(sub["k"], sub["covered"], marker="s", label=scheme)
    axes[1].set_xlabel("k")
    axes[1].set_ylabel("covered (1=yes)")
    axes[1].set_title("Coverage of true constant")
    axes[1].legend()
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
    ctx = cli("configs/F19.yaml", description="Generate F19 bootstrap audit")
    run(config=ctx.config, results_dir=ctx.results_dir)
