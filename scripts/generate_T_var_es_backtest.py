"""Generate T_var_es_backtest_placeholder."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.io.writers import write_csv
from factortail.real_data import RollingVaRConfig, load_fama_french, run_rolling_var_es
from factortail.real_data.backtests import (
    acerbi_szekely_es,
    christoffersen_test,
    dq_test,
    kupiec_test,
)

SCHEMA_NAME = "T_var_es_backtest_placeholder"


def run(*, config: dict, results_dir: Path) -> list[Path]:
    panel = load_fama_french(
        name=config.get("panel", "FF3_daily"),
        offline=config.get("offline", True),
        n_synthetic=int(config.get("n_synthetic", 2000)),
        rng_seed=int(config.get("seed", 0)),
    )
    portfolio = config.get("portfolio", "Mkt-RF")
    series = panel.data[portfolio]
    factors = panel.data.drop(columns=[portfolio, "RF"], errors="ignore")
    if factors.shape[1] == 0:
        factors = panel.data[[portfolio]].rename(columns={portfolio: "self_factor"})
    rc = RollingVaRConfig(
        window=int(config.get("window", 500)),
        levels=tuple(config.get("levels", (0.99, 0.995))),
        n_inner=int(config.get("n_inner", 3000)),
        seed=int(config.get("seed", 0)),
    )
    df = run_rolling_var_es(series, factors, portfolio=portfolio, config=rc)
    rows = []
    for level in rc.levels:
        sub = df[df["level"] == level].dropna()
        kup = kupiec_test(sub["hit"].to_numpy(), level=level)
        chris = christoffersen_test(sub["hit"].to_numpy(), level=level)
        dq = dq_test(sub["hit"].to_numpy(), level=level)
        es = acerbi_szekely_es(
            sub["loss"].to_numpy(),
            sub["var"].to_numpy(),
            sub["es"].to_numpy(),
            level=level,
        )
        rows.append(
            dict(
                portfolio=portfolio,
                model="FF",
                level=level,
                expected_hits=kup["expected_hits"],
                observed_hits=kup["observed_hits"],
                kupiec_p=kup["p_value"],
                christoffersen_p=chris["p_value"],
                dq_p=dq["p_value"],
                es_score=es["statistic"],
                comparative_loss=float(sub["loss"].mean()),
                status="complete",
            )
        )
    out = pd.DataFrame(rows)
    out = stamp_provenance(out, ctx=_Ctx(Path("T_back.yaml"), config, results_dir))
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
    ctx = cli("configs/T_var_es_backtest.yaml", description="VaR/ES backtest")
    run(config=ctx.config, results_dir=ctx.results_dir)
