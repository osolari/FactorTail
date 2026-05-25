"""Generate F18: Hill and POT stability plots across k for each factor."""

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
from factortail.diagnostics.tail_index import hill_estimator, pot_gpd_estimator
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.real_data import load_fama_french

SCHEMA_NAME = "F18_hill_plots"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    panel = load_fama_french(
        name=config.get("panel", "FF3_daily"),
        offline=config.get("offline", True),
        n_synthetic=int(config.get("n_synthetic", 5000)),
        rng_seed=int(config.get("seed", 18)),
    )
    df = panel.data.drop(columns=["RF"], errors="ignore")
    rows = []
    for col in df.columns:
        for side, x in (("right", df[col].to_numpy()), ("left", -df[col].to_numpy())):
            pos = x[x > 0]
            n_pos = pos.size
            if n_pos < 50:
                continue
            ks = np.unique(np.linspace(20, max(int(0.2 * n_pos), 30), 8).astype(int))
            best_k = int(np.median(ks))
            for k in ks:
                hill = hill_estimator(pos, k=int(k))
                rows.append(
                    dict(
                        date=str(df.index.max().date()),
                        series=col,
                        side=side,
                        threshold_k=int(k),
                        estimator="hill",
                        alpha_hat=hill["alpha_hat"],
                        ci_low=hill["alpha_hat"] - 1.96 * hill["se"] * hill["alpha_hat"] ** 2,
                        ci_high=hill["alpha_hat"] + 1.96 * hill["se"] * hill["alpha_hat"] ** 2,
                        selected_threshold=best_k,
                        active_flag=int(k == best_k),
                    )
                )
            pot = pot_gpd_estimator(pos, k=int(0.1 * n_pos))
            rows.append(
                dict(
                    date=str(df.index.max().date()),
                    series=col,
                    side=side,
                    threshold_k=int(0.1 * n_pos),
                    estimator="pot",
                    alpha_hat=pot.get("alpha_hat", float("nan")),
                    ci_low=float("nan"),
                    ci_high=float("nan"),
                    selected_threshold=int(0.1 * n_pos),
                    active_flag=1,
                )
            )
    out = pd.DataFrame(rows)
    out["data_vintage"] = panel.vintage
    out = stamp_provenance(out, ctx=_Ctx(Path("F18.yaml"), config, results_dir))
    csv_path = write_csv(
        out, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    for series in out["series"].unique():
        sub = out[
            (out["series"] == series) & (out["estimator"] == "hill") & (out["side"] == "right")
        ]
        ax.plot(sub["threshold_k"], sub["alpha_hat"], marker="o", label=f"{series} (right)")
    ax.set_xlabel("k")
    ax.set_ylabel(r"$\widehat\alpha$")
    ax.set_title("Hill stability plot")
    ax.legend()
    fig_paths = save_figure(fig, results_dir / "F18_hill_plots")
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
    ctx = cli("configs/F18.yaml", description="Generate F18 Hill plots")
    run(config=ctx.config, results_dir=ctx.results_dir)
