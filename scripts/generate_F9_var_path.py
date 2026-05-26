r"""F9 — single-portfolio VaR/ES path at 99% and 99.5%.

Per-portfolio breakout of the F16 dashboard. Same rolling pipeline
(`alg:real-data`) but only one portfolio per CSV.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import matplotlib.pyplot as plt
import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.plotting.panels import var_es_overlay
from factortail.real_data import RollingVaRConfig, load_fama_french, run_rolling_var_es

SCHEMA_NAME = "F9_var_path"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    panel = load_fama_french(
        name=config.get("panel", "FF3_daily"),
        offline=config.get("offline", True),
        n_synthetic=int(config.get("n_synthetic", 1500)),
        rng_seed=int(config.get("seed", 9)),
    )
    portfolio = config.get("portfolio", "Mkt-RF")
    series = panel.data[portfolio]
    factors = panel.data.drop(columns=[portfolio, "RF"], errors="ignore")
    if factors.shape[1] == 0:
        factors = panel.data[[portfolio]].rename(columns={portfolio: "self_factor"})
    rc = RollingVaRConfig(
        window=int(config.get("window", 400)),
        levels=(0.99, 0.995),
        n_inner=int(config.get("n_inner", 3000)),
        seed=int(config.get("seed", 9)),
    )
    df_full = run_rolling_var_es(series, factors, portfolio=portfolio, config=rc)

    # Pivot to one row per date with both 99 and 99.5 levels alongside.
    p99 = df_full[df_full["level"] == 0.99].set_index("date")
    p995 = df_full[df_full["level"] == 0.995].set_index("date")
    merged = pd.DataFrame(
        {
            "date": p99.index,
            "loss": p99["loss"].to_numpy(),
            "var_99": p99["var"].to_numpy(),
            "es_99": p99["es"].to_numpy(),
            "var_995": p995["var"].reindex(p99.index).to_numpy(),
            "es_995": p995["es"].reindex(p99.index).to_numpy(),
            "estimator": "independent",
            "window": rc.window,
            "crisis_flag": 0,
        }
    )
    merged["data_vintage"] = panel.vintage
    merged = stamp_provenance(merged, ctx=_Ctx(Path("F9.yaml"), config, results_dir))
    csv_path = write_csv(
        merged, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    fig, ax = plt.subplots(figsize=(10.0, 4.0), constrained_layout=True)
    var_es_overlay(
        ax,
        merged["date"].to_numpy(),
        merged["loss"].to_numpy(),
        var=merged["var_99"].to_numpy(),
        es=merged["es_99"].to_numpy(),
    )
    ax.plot(
        merged["date"],
        merged["var_995"],
        color="#9b1f5b",
        linestyle="--",
        linewidth=1.0,
        label="VaR 99.5%",
    )
    ax.legend(loc="upper left")
    ax.set_title(f"VaR / ES path — {portfolio}")
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
    ctx = cli("configs/F9.yaml", description="Generate F9 single-portfolio VaR/ES path")
    run(config=ctx.config, results_dir=ctx.results_dir)
