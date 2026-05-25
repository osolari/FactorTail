"""Generate T_tail_index_placeholder: real-data Hill/Pickands/POT estimates."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import numpy as np
import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.diagnostics.tail_index import hill_estimator, pickands_estimator, pot_gpd_estimator
from factortail.io.writers import write_csv
from factortail.real_data import load_fama_french

SCHEMA_NAME = "T_tail_index_placeholder"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    panel = load_fama_french(
        name=config.get("panel", "FF3_daily"),
        offline=config.get("offline", True),
        n_synthetic=int(config.get("n_synthetic", 5000)),
        rng_seed=int(config.get("seed", 0)),
    )
    df = panel.data.drop(columns=["RF"], errors="ignore")
    rows = []
    for col in df.columns:
        for side, x in (("right", df[col].to_numpy()), ("left", -df[col].to_numpy())):
            pos = x[x > 0]
            if pos.size < 60:
                continue
            for est_name, fn in (
                ("hill", lambda v, k=int(0.1 * pos.size): hill_estimator(v, k=k)),
                ("pickands", lambda v, k=int(0.05 * pos.size): pickands_estimator(v, k=max(k, 5))),
                ("pot_gpd", lambda v, k=int(0.1 * pos.size): pot_gpd_estimator(v, k=k)),
            ):
                est = fn(pos)
                alpha = est.get("alpha_hat", float("nan"))
                se = est.get("se", float("nan"))
                rows.append(
                    dict(
                        series=col,
                        side=side,
                        estimator=est_name,
                        threshold=est.get("threshold", float("nan")),
                        k=est.get("k", float("nan")),
                        alpha_hat=alpha,
                        ci_low=alpha - 1.96 * (se if se == se else 0.0) * alpha**2,
                        ci_high=alpha + 1.96 * (se if se == se else 0.0) * alpha**2,
                        active_flag=int(np.isfinite(alpha)),
                        common_index_group="market",
                        status="complete",
                    )
                )
    out = pd.DataFrame(rows)
    out = stamp_provenance(out, ctx=_Ctx(Path("T_tail.yaml"), config, results_dir))
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
    ctx = cli("configs/T_tail_index.yaml", description="Tail index table")
    run(config=ctx.config, results_dir=ctx.results_dir)
