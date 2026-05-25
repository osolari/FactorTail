"""Generate T_data_panels: real-data panel inventory."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.io.writers import write_csv
from factortail.real_data import load_fama_french

SCHEMA_NAME = "T_data_panels"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    rows = []
    for panel_cfg in config["panels"]:
        panel = load_fama_french(
            name=panel_cfg["name"],
            offline=panel_cfg.get("offline", True),
            n_synthetic=int(panel_cfg.get("n_synthetic", 5000)),
            rng_seed=int(panel_cfg.get("seed", 0)),
        )
        rows.append(
            dict(
                panel=panel.name,
                source=panel.source,
                frequency="daily",
                start_date=str(panel.start_date.date()),
                end_date=str(panel.end_date.date()),
                n_assets_or_portfolios=panel.data.shape[1],
                n_obs=panel.n_obs,
                missing_rate=panel.missing_rate,
                vintage=panel.vintage,
                checksum=panel.checksum,
                status="loaded",
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("T_data_panels.yaml"), config, results_dir))
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
    ctx = cli("configs/T_data_panels.yaml", description="Data panel inventory")
    run(config=ctx.config, results_dir=ctx.results_dir)
