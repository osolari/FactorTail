"""Generate T_empirical_design_matrix."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.io.writers import write_csv

SCHEMA_NAME = "T_empirical_design_matrix"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    rows = config.get(
        "rows",
        [
            dict(
                universe="FF3 daily",
                model="FF3",
                tail_fit="hill+pot",
                dependence_diagnostic="chi/eta",
                estimator_candidates="independent;latent_shock;spectral",
                backtest_window="rolling 500",
                status="ready",
            ),
            dict(
                universe="FF5 daily",
                model="FF5",
                tail_fit="hill+pot",
                dependence_diagnostic="chi/eta",
                estimator_candidates="independent;latent_shock;spectral;block",
                backtest_window="rolling 500",
                status="ready",
            ),
            dict(
                universe="FF5+mom daily",
                model="FF5+mom",
                tail_fit="hill+pot+pickands",
                dependence_diagnostic="chi/eta/spectral",
                estimator_candidates="all",
                backtest_window="rolling 1000",
                status="planned",
            ),
        ],
    )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("T_design.yaml"), config, results_dir))
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
    ctx = cli("configs/T_empirical_design_matrix.yaml", description="Empirical design matrix")
    run(config=ctx.config, results_dir=ctx.results_dir)
