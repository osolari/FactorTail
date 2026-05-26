r"""F19 — bootstrap-scheme audit for the empirical spectral constant
(handoff open question Q4).

Compares iid / non-overlapping-block / Politis-Romano stationary
bootstrap on a stationary heavy-tailed series.

**Design.** AR(1)-injected Pareto-radial / Dirichlet-angular MRV; the
true linear-risk constant is computed by a 200k-MC closed-form
reference (the constant is :math:`E[(\ell(\Theta)_+)^\alpha]`).

**Why a sweep.** Single-seed coverage is binary (the band either covers
the truth or it doesn't). We sweep:

1. ``rho`` (AR(1) auto-correlation) in
   :math:`\{0.0, 0.4, 0.7, 0.9\}` so the panel can show how the
   schemes break under stronger serial dependence,
2. ``replicate`` index in :math:`\{0, \dots, R-1\}` so coverage
   *proportion* (not 0/1) is the y-axis.

The headline expected result: under :math:`\rho = 0` (iid), all three
schemes hit ~95% coverage. Under :math:`\rho \ge 0.7`, the iid
bootstrap under-covers (over-confident bands ignore serial dep) while
block and stationary stay near nominal.
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
from factortail.dgp import RadialAngularMRV
from factortail.diagnostics import bootstrap_bands
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "F19_bootstrap_audit"


def _true_spectral_constant(alpha: float, exposure: np.ndarray, concentration: np.ndarray) -> float:
    rng = np.random.default_rng(0)
    Theta = rng.dirichlet(concentration, size=200_000)
    y_pos = np.maximum(Theta @ exposure, 0.0)
    return float(np.mean(y_pos**alpha))


def _ar1_resample(X: np.ndarray, rho: float) -> np.ndarray:
    if rho == 0.0:
        return X
    Y = np.zeros_like(X)
    Y[0] = X[0]
    sigma = np.sqrt(max(1.0 - rho**2, 0.0))
    for t in range(1, X.shape[0]):
        Y[t] = rho * Y[t - 1] + sigma * X[t]
    return Y


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 19))
    alpha = float(config.get("alpha", 2.0))
    dim = int(config.get("dim", 3))
    concentration = np.asarray(config.get("concentration", [2.0] * dim), dtype=float)
    exposure = np.asarray(config.get("exposure", [1.0, 2.0, 0.5]), dtype=float)
    n = int(config.get("n", 4000))
    rho_grid = list(config.get("rho_grid", [0.0, 0.4, 0.7, 0.9]))
    R = int(config.get("replications", 40))
    k = int(config.get("k", 200))
    n_boot = int(config.get("n_boot", 200))
    schemes = list(config.get("schemes", ["iid", "block", "stationary"]))
    block_length = int(config.get("block_length", 30))

    true_C = _true_spectral_constant(alpha, exposure, concentration)
    dgp = RadialAngularMRV(
        alpha=alpha,
        angular_kind="dirichlet",
        angular_params={"concentration": concentration.tolist()},
        dim=dim,
    )

    rows: list[dict] = []
    coverage_map: dict[tuple[float, str], list[int]] = {
        (r, s): [] for r in rho_grid for s in schemes
    }
    for r_idx, rho_val in enumerate(rho_grid):
        for rep in range(R):
            base_rng = spawner.rng(r_idx * 1000 + rep)
            X_iid = dgp.sample(n, base_rng)
            X = _ar1_resample(X_iid, rho=rho_val)
            for scheme in schemes:
                res = bootstrap_bands(
                    X,
                    exposure=exposure,
                    alpha=alpha,
                    k_grid=[k],
                    n_boot=n_boot,
                    scheme=scheme,
                    block_length=block_length,
                    seed=int(spawner.spawned_seed(r_idx * 10_000 + rep) % (2**31)),
                )
                est = float(res["estimate"][0])
                lo = float(res["lo"][0])
                hi = float(res["hi"][0])
                covered = int(lo <= true_C <= hi)
                coverage_map[(rho_val, scheme)].append(covered)
                rows.append(
                    dict(
                        seed=spawner.spawned_seed(r_idx * 10_000 + rep),
                        design=f"ar1_rho_{rho_val:g}_rep_{rep}",
                        scheme=scheme,
                        block_length=block_length if scheme != "iid" else 0,
                        k=k,
                        true_constant=true_C,
                        estimate=est,
                        lo=lo,
                        hi=hi,
                        se=float(res["se"][0]),
                        covered=covered,
                        n_boot=n_boot,
                    )
                )

    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F19.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    # Plot: coverage proportion vs rho, one curve per scheme + Wilson CI.
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    from math import sqrt

    scheme_colors = {"iid": "#7f8c8d", "block": "#1f3a93", "stationary": "#188a4f"}
    for scheme in schemes:
        props = []
        cis_lo = []
        cis_hi = []
        for rho_val in rho_grid:
            covers = np.asarray(coverage_map[(rho_val, scheme)], dtype=float)
            p_hat = float(covers.mean()) if covers.size else float("nan")
            # Wilson CI half-width at 95%.
            z = 1.96
            half = z * sqrt(max(p_hat * (1 - p_hat), 1e-12) / max(R, 1))
            props.append(p_hat)
            cis_lo.append(max(0.0, p_hat - half))
            cis_hi.append(min(1.0, p_hat + half))
        props = np.asarray(props)
        cis_lo = np.asarray(cis_lo)
        cis_hi = np.asarray(cis_hi)
        ax.errorbar(
            rho_grid,
            props,
            yerr=[props - cis_lo, cis_hi - props],
            marker="o",
            capsize=4,
            label=scheme,
            color=scheme_colors[scheme],
        )
    ax.axhline(0.95, color="black", linestyle=":", linewidth=0.8, label="nominal 0.95")
    ax.set_xlabel(r"AR(1) coefficient $\rho$")
    ax.set_ylabel(r"empirical coverage of true $C_\ell$  (R=" + str(R) + ")")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("Bootstrap coverage vs serial dependence")
    ax.legend(loc="lower left")

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
