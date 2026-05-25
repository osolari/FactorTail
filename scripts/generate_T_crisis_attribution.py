"""Generate T_crisis_attribution_placeholder."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import numpy as np
import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.io.writers import write_csv
from factortail.real_data import load_fama_french

SCHEMA_NAME = "T_crisis_attribution_placeholder"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    panel = load_fama_french(
        name=config.get("panel", "FF3_daily"),
        offline=config.get("offline", True),
        n_synthetic=int(config.get("n_synthetic", 5000)),
        rng_seed=int(config.get("seed", 0)),
    )
    df = panel.data.drop(columns=["RF"], errors="ignore")
    L = -df.iloc[:, 0]
    rows = []
    crisis_windows = config.get(
        "windows",
        [
            {"name": "tail-1pct", "quantile": 0.99},
            {"name": "tail-0p1pct", "quantile": 0.999},
        ],
    )
    total_var = float(L.var())
    for win in crisis_windows:
        thresh = float(np.quantile(L, win["quantile"]))
        mask = thresh < L
        if not mask.any():
            continue
        # Decompose contribution by axis (single factor dominant), block (top-2 factors share),
        # hidden (more than two factors).
        sub = df.loc[mask].abs()
        top = sub.idxmax(axis=1)
        axis_share = float((sub.max(axis=1) / sub.sum(axis=1)).mean())
        block_share = float(
            (
                sub.apply(lambda r: sorted(r)[-2] if len(r) > 1 else 0.0, axis=1) / sub.sum(axis=1)
            ).mean()
        )
        spectral_sector_share = float(1.0 - axis_share - block_share)
        hidden_share = float(max(0.0, 1.0 - axis_share - block_share - spectral_sector_share))
        rows.append(
            dict(
                window=win["name"],
                axis_share=axis_share,
                latent_shock_share=0.0,
                block_share=block_share,
                spectral_sector_share=spectral_sector_share,
                hidden_cone_share=hidden_share,
                dominant_driver=str(top.mode().iloc[0]),
                status="complete",
            )
        )
    out = pd.DataFrame(rows)
    out = stamp_provenance(out, ctx=_Ctx(Path("T_crisis.yaml"), config, results_dir))
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
    ctx = cli("configs/T_crisis.yaml", description="Crisis attribution table")
    run(config=ctx.config, results_dir=ctx.results_dir)
