"""Generate F12: empirical spectral simplex (P4)."""

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
from factortail.diagnostics.spectral import empirical_spectral_measure
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.plotting.panels import simplex_scatter
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "F12_spectral_simplex"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 12))
    rng = spawner.rng(0)
    dgp = RadialAngularMRV.from_spec(config["mrv"])
    n = int(config.get("n", 50_000))
    X = dgp.sample(n, rng)
    spec = empirical_spectral_measure(X, k=int(config.get("k", 500)), norm="l1")
    angles = spec["angles"]
    exposure = np.asarray(config.get("exposure", np.ones(angles.shape[1])), dtype=float)
    if exposure.shape[0] != angles.shape[1]:
        raise ValueError("Exposure length must match dim")
    loading = angles @ exposure
    contribution = np.maximum(loading, 0.0) ** dgp.alpha
    weight = np.ones(angles.shape[0]) / angles.shape[0]
    # F12 CSV
    rows = []
    for i, theta in enumerate(angles):
        rows.append(
            dict(
                seed=spawner.spawned_seed(i),
                design=config.get("design", "mrv_default"),
                theta_1=float(theta[0]) if theta.size > 0 else 0.0,
                theta_2=float(theta[1]) if theta.size > 1 else 0.0,
                theta_3=float(theta[2]) if theta.size > 2 else 0.0,
                spectral_weight=float(weight[i]),
                portfolio_loading=float(loading[i]),
                contribution=float(contribution[i]),
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F12.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    fig, ax = plt.subplots(figsize=(5.0, 4.5))
    simplex_scatter(ax, angles[:, :3], weights=contribution)
    fig_paths = save_figure(fig, results_dir / "F12_spectral_simplex")
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
    ctx = cli("configs/F12.yaml", description="Generate F12 spectral simplex")
    run(config=ctx.config, results_dir=ctx.results_dir)
