"""Generate T_realdata_experiments registry."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.io.writers import write_csv
from factortail.manifest import load_manifest

SCHEMA_NAME = "T_realdata_experiments"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    rows = []
    for entry in load_manifest():
        if not entry.priority.startswith(("P6", "P7")):
            continue
        rows.append(
            dict(
                experiment=entry.experiment,
                target=", ".join(entry.placeholder_labels),
                estimators=config.get("estimators", "independent;latent_shock;spectral"),
                forecast_levels=", ".join(str(l) for l in config.get("levels", (0.99, 0.995))),
                output_files=", ".join(entry.required_csvs),
                status=entry.status,
            )
        )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("T_realdata.yaml"), config, results_dir))
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
    ctx = cli("configs/T_realdata_experiments.yaml", description="Real-data registry")
    run(config=ctx.config, results_dir=ctx.results_dir)
