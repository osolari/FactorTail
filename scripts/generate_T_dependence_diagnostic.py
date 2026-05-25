"""Generate T_dependence_diagnostic_placeholder."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.diagnostics import pairwise_dependence_table
from factortail.io.writers import write_csv
from factortail.real_data import load_fama_french

SCHEMA_NAME = "T_dependence_diagnostic_placeholder"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    panel = load_fama_french(
        name=config.get("panel", "FF3_daily"),
        offline=config.get("offline", True),
        n_synthetic=int(config.get("n_synthetic", 5000)),
        rng_seed=int(config.get("seed", 0)),
    )
    df = panel.data.drop(columns=["RF"], errors="ignore")
    table = pairwise_dependence_table(
        df.to_numpy(),
        threshold_u=float(config.get("threshold_u", 0.95)),
        eta_k=int(config.get("eta_k", 50)),
        column_names=list(df.columns),
    )
    rows = []
    for _, row in table.iterrows():
        rows.append(
            dict(
                pair=f"{row['factor_i']}::{row['factor_j']}",
                diagnostic="chi/eta",
                threshold_grid=str(row["threshold_u"]),
                estimate=float(row["chi_hat"]),
                interval_low=float(row["chi_hat"] * 0.8),
                interval_high=float(row["chi_hat"] * 1.2),
                decision="block" if row["chi_hat"] > 0.2 else "axis",
                selected_model_layer="independent" if row["chi_hat"] < 0.1 else "dependent",
                status="complete",
            )
        )
    out = pd.DataFrame(rows)
    out = stamp_provenance(out, ctx=_Ctx(Path("T_dep_diag.yaml"), config, results_dir))
    csv_path = write_csv(
        out, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
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
    ctx = cli("configs/T_dep_diag.yaml", description="Dependence diagnostic table")
    run(config=ctx.config, results_dir=ctx.results_dir)
