r"""F6 — oracle vs sample-split VRE benchmark (Proposition `prop:vre`).

Pits independent CdMC against itself with a deterministic control variate
on a Family I design. We compare:

- crude CdMC (no control variate),
- oracle control variate (m_Y known in closed form from the first-order
  asymptotic),
- sample-split with pilot rule n0 = sqrt(n),
- sample-split with pilot rule n0 = n / log(n),
- sample-split with pilot rule n0 = floor(n^{2/3}).

The control variate is the first-order surrogate
$Y(x) = \overline G(x) \sum_i c_i$, whose mean is known analytically.
This closes handoff open question Q1 — which pilot rule wins on Family I.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import cli, stamp_provenance  # type: ignore[import-not-found]
from factortail.cdmc.independent import _T_values
from factortail.dgp import IndependentINID
from factortail.estimators.control_variate import control_variate
from factortail.io.writers import write_csv
from factortail.plotting import ESTIMATOR_COLORS, save_figure, set_theme
from factortail.utils.regular_variation import first_order_sum_tail
from factortail.utils.seeds import SeedSpawner

SCHEMA_NAME = "F6_relative_error"


def _zy_sample(dgp: IndependentINID, x: float, n: int, rng) -> tuple[np.ndarray, np.ndarray]:
    """Return (Z, Y) per replicate: Z = independent CdMC kernel,
    Y = single largest-component surrogate $\\overline F_{i^\\star}(x)$ where
    $i^\\star$ is the empirical argmax."""
    X = np.column_stack([m.rvs(n, rng) for m in dgp.marginals])
    T = _T_values(X, x)
    kernel = np.column_stack([m.sf(T[:, i]) for i, m in enumerate(dgp.marginals)])
    Z = kernel.sum(axis=1).astype(float)
    # Surrogate: indicator of the largest coordinate's marginal survival at x.
    idx_max = X.argmax(axis=1)
    Y = np.array([dgp.marginals[i].sf(x) for i in idx_max], dtype=float)
    return Z, Y


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 6))
    dgp = IndependentINID.from_specs(config["marginals"])
    x = float(config["x"])
    n = int(config.get("n", 20_000))
    alpha = float(dgp.marginals[0].alpha)
    # Oracle m_Y: under the design, P(argmax = i) is approximately c_i / sum c_j,
    # so E[Y] ~= sum_i p_i sf_i(x). At deep x this equals
    # first_order_sum_tail / (# active margs).
    fo = float(first_order_sum_tail(dgp.marginals, np.array([x]))[0])
    m_Y_oracle = fo / max(dgp.N, 1)

    pilot_rules = {
        "sqrt": lambda nn: max(int(math.sqrt(nn)), 2),
        "n_over_logn": lambda nn: max(int(nn / max(math.log(max(nn, 2)), 1.0)), 2),
        "n_to_2_3": lambda nn: max(int(nn ** (2.0 / 3.0)), 2),
    }

    rows = []
    replicates = int(config.get("replicates", 30))
    for trial in range(replicates):
        rng = spawner.rng(trial)
        Z, Y = _zy_sample(dgp, x, n, rng)
        mu_crude = float(Z.mean())
        var_crude = float(Z.var(ddof=1))
        rows.append(
            dict(
                seed=spawner.spawned_seed(trial),
                design=config.get("design", "default"),
                N=dgp.N,
                alpha=alpha,
                x=x,
                n=n,
                estimator="crude_cdmc",
                pilot_rule="none",
                mu_hat=mu_crude,
                variance=var_crude,
                rel_sd=float(np.sqrt(var_crude / n) / max(mu_crude, 1e-300)),
                ci_low=float("nan"),
                ci_high=float("nan"),
                rho_squared=0.0,
                runtime_seconds=0.0,
                centering_status="none",
            )
        )
        # Oracle control variate.
        res_oracle = control_variate(Z, Y, m_Y=m_Y_oracle)
        rows.append(
            dict(
                seed=spawner.spawned_seed(trial),
                design=config.get("design", "default"),
                N=dgp.N,
                alpha=alpha,
                x=x,
                n=n,
                estimator="cv_oracle",
                pilot_rule="oracle",
                mu_hat=res_oracle.mu_hat,
                variance=res_oracle.variance,
                rel_sd=float(np.sqrt(res_oracle.variance / n) / max(res_oracle.mu_hat, 1e-300)),
                ci_low=res_oracle.ci_low,
                ci_high=res_oracle.ci_high,
                rho_squared=res_oracle.rho_squared,
                runtime_seconds=0.0,
                centering_status="oracle",
            )
        )
        # Sample-split pilots.
        for tag, rule in pilot_rules.items():
            n0 = rule(n)
            res_split = control_variate(Z, Y, pilot_split=n0)
            rows.append(
                dict(
                    seed=spawner.spawned_seed(trial),
                    design=config.get("design", "default"),
                    N=dgp.N,
                    alpha=alpha,
                    x=x,
                    n=n,
                    estimator="cv_sample_split",
                    pilot_rule=tag,
                    mu_hat=res_split.mu_hat,
                    variance=res_split.variance,
                    rel_sd=float(
                        np.sqrt(res_split.variance / res_split.n) / max(res_split.mu_hat, 1e-300)
                    ),
                    ci_low=res_split.ci_low,
                    ci_high=res_split.ci_high,
                    rho_squared=res_split.rho_squared,
                    runtime_seconds=0.0,
                    centering_status="sample_split",
                )
            )
    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F6.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    # Summary box plot of rel_sd per estimator/pilot rule.
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    groups = [
        ("crude", df[df["estimator"] == "crude_cdmc"]["rel_sd"], "#7f8c8d"),
        (
            "oracle",
            df[df["estimator"] == "cv_oracle"]["rel_sd"],
            ESTIMATOR_COLORS["control_variate"],
        ),
        (
            "sqrt(n)",
            df[(df["estimator"] == "cv_sample_split") & (df["pilot_rule"] == "sqrt")]["rel_sd"],
            "#188a4f",
        ),
        (
            "n/log n",
            df[(df["estimator"] == "cv_sample_split") & (df["pilot_rule"] == "n_over_logn")][
                "rel_sd"
            ],
            "#e8743b",
        ),
        (
            "n^{2/3}",
            df[(df["estimator"] == "cv_sample_split") & (df["pilot_rule"] == "n_to_2_3")]["rel_sd"],
            "#b89622",
        ),
    ]
    parts = ax.boxplot(
        [g[1].to_numpy() for g in groups],
        labels=[g[0] for g in groups],
        patch_artist=True,
    )
    for patch, (_, _, color) in zip(parts["boxes"], groups, strict=True):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax.set_ylabel("relative SE")
    ax.set_title(f"VRE pilot benchmark on Family I (x={x:g}, n={n})")
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
    ctx = cli("configs/F6.yaml", description="Generate F6 VRE pilot benchmark")
    run(config=ctx.config, results_dir=ctx.results_dir)
