"""Generate T_sim_results_independent: independent simulation results table."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import numpy as np
import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.cdmc import independent_cdmc
from factortail.dgp import IndependentINID
from factortail.io.writers import write_csv
from factortail.utils.regular_variation import first_order_sum_tail, second_order_sum_tail
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "T_sim_results_independent"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    spawner = SeedSpawner(master_seed=config.get("seed", 1))
    rows = []
    for i, design in enumerate(config["designs"]):
        dgp = IndependentINID.from_specs(design["marginals"])
        x_grid = np.array(design["x_grid"], dtype=float)
        n = int(design.get("n", 10_000))
        fo = first_order_sum_tail(dgp.marginals, x_grid)
        so = second_order_sum_tail(dgp.marginals, x_grid)
        for j, xi in enumerate(x_grid):
            res = independent_cdmc(dgp.marginals, x=float(xi), n=n, rng=spawner.rng(i * 100 + j))
            rel_err = float(abs(res.mu_hat - so[j]) / max(so[j], 1e-300))
            wnre = float(np.sqrt(res.variance * res.runtime_seconds) / max(res.mu_hat, 1e-300))
            rows.append(
                dict(
                    design=design.get("name", f"design_{i}"),
                    N=dgp.N,
                    alpha=float(dgp.marginals[0].alpha),
                    x=float(xi),
                    n=n,
                    first_order=float(fo[j]),
                    second_order=float(so[j]),
                    mu_hat=res.mu_hat,
                    rel_error=rel_err,
                    wnre=wnre,
                    runtime_seconds=res.runtime_seconds,
                    status="complete",
                )
            )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("T_indep.yaml"), config, results_dir))
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
    ctx = cli("configs/T_sim_results_independent.yaml", description="Independent sim results")
    run(config=ctx.config, results_dir=ctx.results_dir)
