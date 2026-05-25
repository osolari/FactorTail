"""Generate T_sim_results_dependent: dependent simulation results table."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import numpy as np
import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.cdmc import latent_shock_cdmc, spectral_cdmc
from factortail.dgp import (
    HiddenConeMixture,
    LatentFactorModel,
    RadialAngularMRV,
)
from factortail.io.writers import write_csv
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "T_sim_results_dependent"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    spawner = SeedSpawner(master_seed=config.get("seed", 2))
    rows: list[dict] = []
    for i, design in enumerate(config["designs"]):
        family = design["family"]
        x = float(design["x"])
        n = int(design.get("n", 10_000))
        if family == "Family II":
            dgp = LatentFactorModel.from_spec(design)
            exposure = np.asarray(design.get("exposure", np.ones(dgp.N)))
            res = latent_shock_cdmc(
                B=dgp.B,
                exposure=exposure,
                shocks=dgp.shocks,
                idiosyncratic=dgp.idiosyncratic,
                x=x,
                n=n,
                rng=spawner.rng(i),
            )
            est_name = "latent_shock_cdmc"
            ref = float("nan")
        elif family == "Family V":
            dgp5 = RadialAngularMRV.from_spec(design)
            exposure5 = np.asarray(design.get("exposure", np.ones(dgp5.dim)))
            res = spectral_cdmc(
                angle_sampler=lambda nn, rr, _dgp5=dgp5: _dgp5.sample_angles(nn, rr),
                radial=dgp5.radial,
                exposure=exposure5,
                x=x,
                n=n,
                rng=spawner.rng(i),
            )
            est_name = "spectral_cdmc"
            ref = float("nan")
        elif family == "Family VI":
            dgp6 = HiddenConeMixture.from_spec(design)
            rng = spawner.rng(i)
            X = dgp6.sample(n, rng)
            emp = float((X.sum(axis=1) > x).mean())
            rows.append(
                dict(
                    family=family,
                    design=design.get("name", f"design_{i}"),
                    estimator="empirical",
                    x=x,
                    mu_hat=emp,
                    ref_mu=emp,
                    rel_error=0.0,
                    wnre=0.0,
                    runtime_seconds=0.0,
                    status="complete",
                )
            )
            continue
        else:
            raise ValueError(f"Unknown family: {family}")
        rel_err = (
            float(abs(res.mu_hat - ref) / max(abs(ref), 1e-300))
            if np.isfinite(ref)
            else float("nan")
        )
        wnre = float(np.sqrt(res.variance * res.runtime_seconds) / max(res.mu_hat, 1e-300))
        rows.append(
            dict(
                family=family,
                design=design.get("name", f"design_{i}"),
                estimator=est_name,
                x=x,
                mu_hat=res.mu_hat,
                ref_mu=ref,
                rel_error=rel_err,
                wnre=wnre,
                runtime_seconds=res.runtime_seconds,
                status="complete",
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("T_dep.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    return [csv_path]


class _Ctx:
    def __init__(self, p, c, r):
        from factortail.utils.hashing import config_hash

        self.config_path = p
        self.config = c
        self.results_dir = r
        self.run_id = c.get("run_id", p.stem)
        self.config_hash = config_hash(c)


if __name__ == "__main__":
    ctx = cli("configs/T_sim_results_dependent.yaml", description="Dependent sim results")
    run(config=ctx.config, results_dir=ctx.results_dir)
