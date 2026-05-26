r"""F10 — single-portfolio backtest exception time series.

For each forecast date, records the realized loss, the rolling VaR
forecast, the exception indicator, and the rolling violation rate (the
fraction of exceptions in a trailing window). Companion to F16 with a
single-portfolio focus.
"""

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
from factortail.io.writers import write_csv
from factortail.plotting import ESTIMATOR_COLORS, save_figure, set_theme
from factortail.real_data import RollingVaRConfig, load_fama_french, run_rolling_var_es

SCHEMA_NAME = "F10_backtest"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    panel = load_fama_french(
        name=config.get("panel", "FF3_daily"),
        offline=config.get("offline", True),
        n_synthetic=int(config.get("n_synthetic", 1500)),
        rng_seed=int(config.get("seed", 10)),
    )
    portfolio = config.get("portfolio", "Mkt-RF")
    series = panel.data[portfolio]
    factors = panel.data.drop(columns=[portfolio, "RF"], errors="ignore")
    if factors.shape[1] == 0:
        factors = panel.data[[portfolio]].rename(columns={portfolio: "self_factor"})
    levels = tuple(config.get("levels", (0.99,)))
    rc = RollingVaRConfig(
        window=int(config.get("window", 400)),
        levels=levels,
        n_inner=int(config.get("n_inner", 3000)),
        seed=int(config.get("seed", 10)),
    )
    df = run_rolling_var_es(series, factors, portfolio=portfolio, config=rc)
    df = df.rename(columns={"hit": "hit"})  # already named hit
    rolling_window = int(config.get("rolling_window", 60))
    out_frames = []
    for level in levels:
        sub = df[df["level"] == level].copy().sort_values("date")
        sub["rolling_violation_rate"] = (
            sub["hit"].rolling(rolling_window, min_periods=1).mean().to_numpy()
        )
        sub["model"] = "FF"
        sub["window"] = rc.window
        sub = sub[
            [
                "date",
                "level",
                "loss",
                "var",
                "hit",
                "rolling_violation_rate",
                "model",
                "window",
            ]
        ]
        out_frames.append(sub)
    out = pd.concat(out_frames, ignore_index=True)
    out["data_vintage"] = panel.vintage
    out = stamp_provenance(out, ctx=_Ctx(Path("F10.yaml"), config, results_dir))
    csv_path = write_csv(
        out, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    fig, ax = plt.subplots(figsize=(10.0, 4.0), constrained_layout=True)
    for level in levels:
        sub = out[out["level"] == level]
        ax.plot(
            sub["date"],
            sub["rolling_violation_rate"],
            label=f"violation rate (level {level:.3f})",
        )
        target = 1.0 - level
        ax.axhline(
            target, color=ESTIMATOR_COLORS.get("reference", "#222"), linestyle=":", linewidth=0.8
        )
    ax.set_xlabel("date")
    ax.set_ylabel(f"rolling violation rate ({rolling_window}-day)")
    ax.set_title(f"Exception clustering — {portfolio}")
    ax.legend(loc="upper left")
    fig_paths = save_figure(fig, results_dir / SCHEMA_NAME)
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
    ctx = cli("configs/F10.yaml", description="Generate F10 backtest path")
    run(config=ctx.config, results_dir=ctx.results_dir)
