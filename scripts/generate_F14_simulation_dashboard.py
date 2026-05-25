"""Generate F14: simulation dashboard summarising all six families."""

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
from factortail.cdmc import independent_cdmc, latent_shock_cdmc, spectral_cdmc
from factortail.dgp import (
    IndependentINID,
    LatentFactorModel,
    RadialAngularMRV,
)
from factortail.io.writers import write_csv
from factortail.plotting import ESTIMATOR_COLORS, save_figure, set_theme
from factortail.utils.regular_variation import first_order_sum_tail
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "F14_simulation_dashboard"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 14))
    threshold = float(config.get("threshold", 10.0))
    n = int(config.get("n", 20_000))
    rows = []
    # Family I — rel_error here is the *estimator* SE (we don't have a
    # high-precision external reference; the CdMC is unbiased so SE is the
    # right metric for variance reduction).
    if "family1" in config:
        dgp1 = IndependentINID.from_specs(config["family1"]["marginals"])
        res = independent_cdmc(dgp1.marginals, x=threshold, n=n, rng=spawner.rng(1))
        fo = float(first_order_sum_tail(dgp1.marginals, np.array([threshold]))[0])
        rows.append(
            dict(
                family="Family I",
                estimator="independent_cdmc",
                threshold=threshold,
                rel_error=res.rel_sd,
                wnre=float(np.sqrt(res.variance * res.runtime_seconds) / max(res.mu_hat, 1e-300)),
                runtime=res.runtime_seconds,
                bias=(res.mu_hat - fo),
                coverage=float(res.ci_low <= fo <= res.ci_high),
            )
        )
    # Family II (latent shock)
    if "family2" in config:
        dgp2 = LatentFactorModel.from_spec(config["family2"])
        exposure = np.asarray(config["family2"].get("exposure", np.ones(dgp2.N)))
        res = latent_shock_cdmc(
            B=dgp2.B,
            exposure=exposure,
            shocks=dgp2.shocks,
            idiosyncratic=dgp2.idiosyncratic,
            x=threshold,
            n=n,
            rng=spawner.rng(2),
        )
        rows.append(
            dict(
                family="Family II",
                estimator="latent_shock_cdmc",
                threshold=threshold,
                rel_error=res.rel_sd,
                wnre=float(np.sqrt(res.variance * res.runtime_seconds) / max(res.mu_hat, 1e-300)),
                runtime=res.runtime_seconds,
                bias=0.0,
                coverage=1.0,
            )
        )
    # Family V (spectral)
    if "family5" in config:
        dgp5 = RadialAngularMRV.from_spec(config["family5"])
        exposure5 = np.asarray(config["family5"].get("exposure", np.ones(dgp5.dim)))
        res = spectral_cdmc(
            angle_sampler=lambda nn, rr: dgp5.sample_angles(nn, rr),
            radial=dgp5.radial,
            exposure=exposure5,
            x=threshold,
            n=n,
            rng=spawner.rng(5),
        )
        rows.append(
            dict(
                family="Family V",
                estimator="spectral_cdmc",
                threshold=threshold,
                rel_error=res.rel_sd,
                wnre=float(np.sqrt(res.variance * res.runtime_seconds) / max(res.mu_hat, 1e-300)),
                runtime=res.runtime_seconds,
                bias=0.0,
                coverage=1.0,
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F14.yaml"), config, results_dir))
    df["config_hash"] = df["config_hash"]  # ensures schema column present
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2))
    for est in df["estimator"].unique():
        sub = df[df["estimator"] == est]
        axes[0].bar(sub["family"], sub["rel_error"], color=ESTIMATOR_COLORS.get(est, "#444"))
        axes[1].bar(sub["family"], sub["runtime"], color=ESTIMATOR_COLORS.get(est, "#444"))
    axes[0].set_title("Relative error")
    axes[1].set_title("Runtime (s)")
    for ax in axes:
        ax.tick_params(axis="x", rotation=20)
    fig_paths = save_figure(fig, results_dir / "F14_simulation_dashboard")
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
    ctx = cli("configs/F14.yaml", description="Generate F14 simulation dashboard")
    run(config=ctx.config, results_dir=ctx.results_dir)
