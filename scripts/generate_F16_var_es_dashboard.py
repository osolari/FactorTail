"""Generate F16: VaR/ES forecast dashboard from rolling pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import matplotlib.pyplot as plt

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.plotting.panels import var_es_overlay
from factortail.real_data import RollingVaRConfig, load_fama_french, run_rolling_var_es

SCHEMA_NAME = "F16_var_es_dashboard"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    panel = load_fama_french(
        name=config.get("panel", "FF3_daily"),
        offline=config.get("offline", True),
        n_synthetic=int(config.get("n_synthetic", 2000)),
        rng_seed=int(config.get("seed", 16)),
    )
    portfolio = config.get("portfolio", "Mkt-RF")
    series = panel.data[portfolio]
    factors = panel.data.drop(columns=[portfolio, "RF"], errors="ignore")
    if factors.shape[1] == 0:
        factors = panel.data[[portfolio]].rename(columns={portfolio: "self_factor"})
    rc = RollingVaRConfig(
        window=int(config.get("window", 500)),
        levels=tuple(config.get("levels", (0.99, 0.995))),
        n_inner=int(config.get("n_inner", 5000)),
        seed=int(config.get("seed", 16)),
    )
    df = run_rolling_var_es(series, factors, portfolio=portfolio, config=rc)
    df["data_vintage"] = panel.vintage
    df = stamp_provenance(df, ctx=_Ctx(Path("F16.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    # Figure: one panel per level
    fig, axes = plt.subplots(len(rc.levels), 1, figsize=(7.5, 3.0 * len(rc.levels)), sharex=True)
    if len(rc.levels) == 1:
        axes = [axes]
    for ax, level in zip(axes, rc.levels, strict=True):
        sub = df[df["level"] == level]
        var_es_overlay(
            ax,
            sub["date"].to_numpy(),
            sub["loss"].to_numpy(),
            var=sub["var"].to_numpy(),
            es=sub["es"].to_numpy(),
            hits=sub["hit"].to_numpy(),
        )
        ax.set_title(f"VaR/ES at level {level}")
    fig_paths = save_figure(fig, results_dir / "F16_var_es_dashboard")
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
    ctx = cli("configs/F16.yaml", description="Generate F16 VaR/ES dashboard")
    run(config=ctx.config, results_dir=ctx.results_dir)
