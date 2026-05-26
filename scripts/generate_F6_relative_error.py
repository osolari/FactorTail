r"""F6 — surrogate-choice benchmark for the spectral control variate
(Proposition ``prop:vre``).

Three surrogates are compared on a Family-V MRV design:

- ``loss``: classical loss-functional surrogate
  :math:`Y = \overline F_R(x/(a^\top\Theta)_+)`.
- ``second_largest_shift``: :math:`Y = \overline F_{i^\star}(x - X_{(2)})`.
- ``max_coord``: :math:`Y = \overline F_{i^\star}(X_{(1)})`.

For each surrogate, we run ``trials`` replicate fits and record
:math:`\widehat\rho^2`, the post-CV variance, and the pre-CV variance
of :math:`Z` alone. The headline result is that **surrogate choice
dominates pilot-rule choice** by orders of magnitude: ``loss`` gives
:math:`\rho^2 \approx 0.01`; ``max_coord`` and ``second_largest_shift``
give :math:`\rho^2 \ge 0.6` and reduce variance by ~3-4×.

Earlier versions of this figure tried to compare pilot rules
:math:`n_0 \in \{\sqrt n, n/\log n, n^{2/3}\}` under an iid-Pareto
design, but the marginal surrogate had :math:`\rho \approx 0` there,
so every rule tied. The pilot rule only matters once the surrogate
is informative — closes handoff Q1.
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
from factortail.dgp import RadialAngularMRV
from factortail.estimators import spectral_control_variate
from factortail.io.writers import write_csv
from factortail.plotting import save_figure, set_theme
from factortail.utils.seeds import SeedSpawner
from factortail.utils.tails import ParetoTail

SCHEMA_NAME = "F6_relative_error"

SURROGATES = ("loss", "second_largest_shift", "max_coord")


def run(*, config: dict, results_dir: Path) -> list[Path]:
    set_theme()
    spawner = SeedSpawner(master_seed=config.get("seed", 6))
    alpha = float(config.get("alpha", 2.0))
    dim = int(config.get("dim", 3))
    exposure = np.asarray(config.get("exposure", [1.0, 2.0, 0.5]), dtype=float)
    x = float(config.get("x", 10.0))
    n = int(config.get("n", 5000))
    trials = int(config.get("trials", 30))

    dgp = RadialAngularMRV(
        alpha=alpha,
        angular_kind="dirichlet",
        angular_params={"concentration": [2.0] * dim},
        dim=dim,
    )
    marginals = [ParetoTail(alpha=alpha, scale=1.0) for _ in range(dim)]

    rows = []
    by_surrogate: dict[str, dict] = {s: {"rho2": [], "var": []} for s in SURROGATES}
    for trial in range(trials):
        for kind in SURROGATES:
            res = spectral_control_variate(
                marginals=marginals,
                angle_sampler=lambda nn, rr: dgp.sample_angles(nn, rr),
                radial=dgp.radial,
                exposure=exposure,
                x=x,
                n=n,
                surrogate=kind,
                rng=spawner.rng(trial),
            )
            by_surrogate[kind]["rho2"].append(res.rho_squared)
            by_surrogate[kind]["var"].append(res.variance)
            rows.append(
                dict(
                    seed=spawner.spawned_seed(trial),
                    design=f"surrogate_{kind}",
                    N=dim,
                    alpha=alpha,
                    x=x,
                    n=n,
                    estimator=f"cv_{kind}",
                    pilot_rule="sample_split_sqrt",
                    mu_hat=res.mu_hat,
                    variance=res.variance,
                    rel_sd=float(
                        np.sqrt(max(res.variance, 0.0) / max(res.n, 1))
                        / max(abs(res.mu_hat), 1e-300)
                    ),
                    ci_low=res.ci_low,
                    ci_high=res.ci_high,
                    rho_squared=res.rho_squared,
                    runtime_seconds=0.0,
                    centering_status=res.centering_status,
                )
            )

    df = pd.DataFrame(rows)
    df = stamp_provenance(df, ctx=_Ctx(Path("F6.yaml"), config, results_dir))
    csv_path = write_csv(
        df, results_dir / f"{SCHEMA_NAME}.csv", schema_name=SCHEMA_NAME, config=config
    )

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5), constrained_layout=True)
    labels = [r"loss", r"$X_{(2)}$-shift", r"max coord"]
    colors = ["#7f8c8d", "#1f3a93", "#188a4f"]

    # Left: rho^2 by surrogate.
    bp1 = axes[0].boxplot(
        [by_surrogate[s]["rho2"] for s in SURROGATES],
        tick_labels=labels,
        patch_artist=True,
        widths=0.55,
    )
    for patch, c in zip(bp1["boxes"], colors, strict=True):
        patch.set_facecolor(c)
        patch.set_alpha(0.6)
    axes[0].axhline(0.5, color="black", linestyle=":", linewidth=0.8)
    axes[0].set_ylabel(r"$\widehat\rho^2$  (CV variance-reduction factor $= 1 - \rho^2$)")
    axes[0].set_title("Surrogate kind drives correlation")
    axes[0].set_ylim(-0.05, 1.05)

    # Right: median variance by surrogate, log-y.
    medians = [float(np.median(by_surrogate[s]["var"])) for s in SURROGATES]
    bars = axes[1].bar(labels, medians, color=colors, alpha=0.6)
    for bar, val in zip(bars, medians, strict=True):
        axes[1].annotate(
            f"{val:.2e}",
            xy=(bar.get_x() + bar.get_width() / 2, val),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            fontsize=8,
        )
    axes[1].set_yscale("log")
    axes[1].set_ylabel("post-CV variance (log scale)")
    axes[1].set_title("Post-CV variance: lower is better")

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
    ctx = cli("configs/F6.yaml", description="Generate F6 spectral CV surrogate benchmark")
    run(config=ctx.config, results_dir=ctx.results_dir)
