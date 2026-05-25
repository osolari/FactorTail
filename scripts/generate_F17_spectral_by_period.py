"""Generate F17: rolling empirical spectral measure across crisis windows."""

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
from factortail.diagnostics.spectral import empirical_spectral_measure
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.real_data import load_fama_french

SCHEMA_NAME = "F17_spectral_by_period"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    panel = load_fama_french(
        name=config.get("panel", "FF3_daily"),
        offline=config.get("offline", True),
        n_synthetic=int(config.get("n_synthetic", 5000)),
        rng_seed=int(config.get("seed", 17)),
    )
    df = panel.data.drop(columns=["RF"], errors="ignore")
    # Real factor names (used in the plot). Pad to 5 columns afterwards just
    # to satisfy the schema's fixed five-theta layout.
    real_names = list(df.columns)
    while df.shape[1] < 5:
        df[f"_pad_{df.shape[1]}"] = 0.0
    df = df.iloc[:, :5]
    column_names = list(df.columns)
    n_real = len(real_names)
    periods = config.get(
        "periods",
        [
            {"name": "early", "start": str(df.index.min()), "end": str(df.index[len(df) // 3])},
            {
                "name": "middle",
                "start": str(df.index[len(df) // 3]),
                "end": str(df.index[2 * len(df) // 3]),
            },
            {"name": "late", "start": str(df.index[2 * len(df) // 3]), "end": str(df.index.max())},
        ],
    )
    rows = []
    for period in periods:
        sub = df.loc[period["start"] : period["end"]].to_numpy()
        # Loss-direction angles: use absolute values so the spectral mass
        # lives on the positive orthant of the unit simplex.
        spec = empirical_spectral_measure(np.abs(sub), k=max(int(0.05 * len(sub)), 10), norm="l1")
        angles = spec["angles"]
        avg = angles.mean(axis=0)
        rows.append(
            dict(
                period=period["name"],
                theta_1=float(avg[0]),
                theta_2=float(avg[1]),
                theta_3=float(avg[2]),
                theta_4=float(avg[3]),
                theta_5=float(avg[4]),
                weight=1.0,
                axis_flag=int(float(avg.max()) > 0.7),
                block_flag=int(float(avg.max()) <= 0.7 and float(np.sort(avg)[-2]) > 0.3),
                stress_flag=int(period["name"].lower() in {"gfc", "covid", "stress"}),
            )
        )
    out = pd.DataFrame(rows)
    out["data_vintage"] = panel.vintage
    out = stamp_provenance(out, ctx=_Ctx(Path("F17.yaml"), config, results_dir))
    csv_path = write_csv(
        out, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    # Plot only the real factor columns (drop padding placeholders).
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    width = 0.8 / max(len(out), 1)
    x = np.arange(n_real)
    for i, row in out.iterrows():
        ax.bar(
            x + (i - (len(out) - 1) / 2) * width,
            [row[f"theta_{k+1}"] for k in range(n_real)],
            width=width,
            label=row["period"],
        )
    ax.set_xticks(x)
    ax.set_xticklabels(real_names)
    ax.set_ylabel("angular mass")
    ax.set_title("Rolling empirical spectral measure")
    ax.legend()
    fig_paths = save_figure(fig, results_dir / "F17_spectral_by_period")
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
    ctx = cli("configs/F17.yaml", description="Generate F17 rolling spectral")
    run(config=ctx.config, results_dir=ctx.results_dir)
