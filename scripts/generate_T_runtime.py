"""Generate T_runtime_placeholder: per-estimator runtime and WNRE."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import numpy as np
import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.cdmc import independent_cdmc, latent_shock_cdmc, spectral_cdmc
from factortail.dgp import IndependentINID, LatentFactorModel, RadialAngularMRV
from factortail.io.writers import write_csv
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "T_runtime_placeholder"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    spawner = SeedSpawner(master_seed=config.get("seed", 99))
    x = float(config.get("threshold", 10.0))
    n = int(config.get("n", 20_000))
    rows = []
    dgp1 = IndependentINID.from_specs(config["family1"]["marginals"])
    r1 = independent_cdmc(dgp1.marginals, x=x, n=n, rng=spawner.rng(0))
    rows.append(_row("independent", "FF", "production", n, dgp1.N * n, r1))
    dgp2 = LatentFactorModel.from_spec(config["family2"])
    r2 = latent_shock_cdmc(
        B=dgp2.B,
        exposure=np.asarray(config["family2"].get("exposure", np.ones(dgp2.N))),
        shocks=dgp2.shocks,
        idiosyncratic=dgp2.idiosyncratic,
        x=x,
        n=n,
        rng=spawner.rng(1),
    )
    rows.append(_row("latent_shock", "FF", "production", n, dgp2.K * n, r2))
    dgp5 = RadialAngularMRV.from_spec(config["family5"])
    r5 = spectral_cdmc(
        angle_sampler=lambda nn, rr: dgp5.sample_angles(nn, rr),
        radial=dgp5.radial,
        exposure=np.asarray(config["family5"].get("exposure", np.ones(dgp5.dim))),
        x=x,
        n=n,
        rng=spawner.rng(2),
    )
    rows.append(_row("spectral", "FF", "production", n, n, r5))
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("T_runtime.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    return [csv_path]


def _row(estimator: str, model: str, phase: str, n_rep: int, tail_evals: int, res) -> dict:
    return dict(
        model=model,
        estimator=estimator,
        phase=phase,
        n_replications=n_rep,
        tail_evaluations=tail_evals,
        runtime_seconds=res.runtime_seconds,
        variance=res.variance,
        work_normalized_variance=res.variance * res.runtime_seconds,
        status="complete",
    )


class _Ctx:
    def __init__(self, p, c, r):
        from factortail.utils.hashing import config_hash

        self.config_path = p
        self.config = c
        self.results_dir = r
        self.run_id = c.get("run_id", p.stem)
        self.config_hash = config_hash(c)


if __name__ == "__main__":
    ctx = cli("configs/T_runtime.yaml", description="Runtime table")
    run(config=ctx.config, results_dir=ctx.results_dir)
