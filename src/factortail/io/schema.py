"""Authoritative output schema for every generated CSV.

Source of truth: ``results/SCHEMA.md``. The dictionary here mirrors that file
column-for-column and is enforced by :mod:`factortail.io.validators`. A
pre-commit hook (``scripts/_dev/check_schema_headers.py``) verifies the two
remain in sync.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

__all__ = ["RequiredColumns", "SCHEMA", "get_schema"]


@dataclass(frozen=True)
class RequiredColumns:
    name: str
    columns: tuple[str, ...]
    metadata_required: tuple[str, ...] = ()
    description: str = ""

    def all_columns(self) -> set[str]:
        return set(self.columns) | set(self.metadata_required)


_METADATA_DEFAULT: tuple[str, ...] = (
    "run_id",
    "config_hash",
    "git_hash",
    "code_version",
    "run_timestamp",
)


_SCHEMAS: list[RequiredColumns] = [
    # Simulation figures (Sec. 8)
    RequiredColumns(
        name="F1_tail_equivalence",
        columns=(
            "seed",
            "design",
            "x",
            "n",
            "mu_hat",
            "ci_low",
            "ci_high",
            "first_order",
            "second_order",
            "runtime_seconds",
        ),
        description="Independent tail-equivalence diagnostic (Family I).",
    ),
    RequiredColumns(
        name="F2_max_vs_sum",
        columns=(
            "seed",
            "design",
            "N",
            "alpha",
            "x",
            "n",
            "p_max",
            "p_sum",
            "ratio",
            "ci_low",
            "ci_high",
            "truth_method",
        ),
        description=(
            "P(M_N > x) / P(S_N > x) under independent regular variation; "
            "ratio -> 1 in deep tail (thm:catastrophe-exact)."
        ),
    ),
    RequiredColumns(
        name="F3_exp_eff_vs_x",
        columns=(
            "seed",
            "design",
            "N",
            "alpha",
            "x",
            "n",
            "kappa",
            "rel_variance",
            "lambda_n",
            "rate_hat",
            "rate_bound_finite",
            "rate_bound_asymptotic",
        ),
        description=(
            "Exponential efficiency rate of independent CdMC vs threshold x; "
            "rate_hat = -log(rel_variance) / kappa_x for the LDP scaling."
        ),
    ),
    RequiredColumns(
        name="F4_exp_eff_vs_alpha",
        columns=(
            "seed",
            "design",
            "alpha_bar",
            "alpha_min",
            "n",
            "kappa",
            "lambda_n",
            "rate_hat",
            "common_alpha_flag",
            "theory_tag",
        ),
        description=(
            "Efficiency rate vs average tail index alpha_bar; "
            "common_alpha_flag distinguishes equal-index from heterogeneous designs."
        ),
    ),
    RequiredColumns(
        name="F5_exp_eff_vs_amin",
        columns=(
            "seed",
            "design",
            "alpha_bar",
            "alpha_min",
            "n",
            "kappa",
            "lambda_n",
            "rate_hat",
            "common_alpha_flag",
            "theory_tag",
        ),
        description=(
            "Efficiency rate vs minimum tail index alpha_min in heterogeneous "
            "Pareto sums; tests the alpha_min-dominated LDP regime."
        ),
    ),
    RequiredColumns(
        name="F6_relative_error",
        columns=(
            "seed",
            "design",
            "N",
            "alpha",
            "x",
            "n",
            "estimator",
            "pilot_rule",
            "mu_hat",
            "variance",
            "rel_sd",
            "ci_low",
            "ci_high",
            "rho_squared",
            "runtime_seconds",
            "centering_status",
        ),
        description=(
            "Oracle vs sample-split VRE benchmark (Proposition prop:vre); "
            "compares pilot rules n0 in {sqrt(n), n/log(n), n^{2/3}} on Family I."
        ),
    ),
    RequiredColumns(
        name="F7_stratified",
        columns=(
            "seed",
            "design",
            "N",
            "alpha",
            "x",
            "n",
            "estimator",
            "mu_hat",
            "variance",
            "work_norm_variance",
            "tail_evals_per_rep",
            "runtime_seconds",
            "weight_rule",
        ),
        description=(
            "Stratified CdMC variance and work-normalized variance vs unstratified "
            "(Section 3 stratification)."
        ),
    ),
    RequiredColumns(
        name="F8_second_order",
        columns=(
            "seed",
            "design",
            "x",
            "first_order_error",
            "second_order_error",
            "leave_one_out_term",
            "remainder_estimate",
        ),
        description="Second-order independent expansion diagnostic.",
    ),
    RequiredColumns(
        name="F9_var_path",
        columns=(
            "date",
            "loss",
            "var_99",
            "es_99",
            "var_995",
            "es_995",
            "estimator",
            "window",
            "crisis_flag",
        ),
        metadata_required=("data_vintage",) + _METADATA_DEFAULT,
        description=(
            "Single-portfolio rolling VaR and ES path at 99% and 99.5%; "
            "complements F16 dashboard with a per-portfolio breakout."
        ),
    ),
    RequiredColumns(
        name="F10_backtest",
        columns=(
            "date",
            "level",
            "loss",
            "var",
            "hit",
            "rolling_violation_rate",
            "model",
            "window",
        ),
        metadata_required=("data_vintage",) + _METADATA_DEFAULT,
        description=(
            "Single-portfolio backtest exception time series with rolling " "violation rate."
        ),
    ),
    RequiredColumns(
        name="F11_common_shock_geometry",
        columns=(
            "seed",
            "design",
            "x",
            "observed_constant",
            "latent_constant",
            "empirical_tail",
            "ci_low",
            "ci_high",
            "attribution_class",
        ),
        description="Common-shock geometry (Family II).",
    ),
    RequiredColumns(
        name="F12_spectral_simplex",
        columns=(
            "seed",
            "design",
            "theta_1",
            "theta_2",
            "theta_3",
            "spectral_weight",
            "portfolio_loading",
            "contribution",
        ),
        description="Empirical spectral measure on simplex (Family V).",
    ),
    RequiredColumns(
        name="F13_hidden_cones",
        columns=(
            "seed",
            "design",
            "x",
            "axis_term",
            "hidden_pair_term",
            "marginal_second_order",
            "empirical_tail",
            "selected_scale",
        ),
        description="Hidden-cone diagnostic (Family VI).",
    ),
    RequiredColumns(
        name="F14_simulation_dashboard",
        columns=(
            "family",
            "estimator",
            "threshold",
            "rel_error",
            "wnre",
            "runtime",
            "bias",
            "coverage",
            "config_hash",
        ),
        description="Simulation dashboard.",
    ),
    # Real-data figures (Sec. 9)
    RequiredColumns(
        name="F15_tail_dependence_heatmap",
        columns=(
            "factor_i",
            "factor_j",
            "threshold_u",
            "chi_hat",
            "chibar_hat",
            "eta_hat",
            "cluster",
            "selected_block",
        ),
        metadata_required=("data_vintage",) + _METADATA_DEFAULT,
        description="Pairwise tail-dependence heatmap.",
    ),
    RequiredColumns(
        name="F16_var_es_dashboard",
        columns=(
            "date",
            "portfolio",
            "model",
            "level",
            "loss",
            "var",
            "es",
            "hit",
            "crisis_flag",
        ),
        metadata_required=("data_vintage", "config_hash"),
        description="Rolling VaR/ES dashboard.",
    ),
    RequiredColumns(
        name="F17_spectral_by_period",
        columns=(
            "period",
            "theta_1",
            "theta_2",
            "theta_3",
            "theta_4",
            "theta_5",
            "weight",
            "axis_flag",
            "block_flag",
            "stress_flag",
        ),
        metadata_required=("data_vintage",) + _METADATA_DEFAULT,
        description="Rolling empirical spectral measure.",
    ),
    RequiredColumns(
        name="F18_hill_plots",
        columns=(
            "date",
            "series",
            "side",
            "threshold_k",
            "estimator",
            "alpha_hat",
            "ci_low",
            "ci_high",
            "selected_threshold",
            "active_flag",
        ),
        metadata_required=("data_vintage",) + _METADATA_DEFAULT,
        description="Hill / POT stability plots.",
    ),
    # Tables (Sec. 8, 9)
    RequiredColumns(
        name="T_data_panels",
        columns=(
            "panel",
            "source",
            "frequency",
            "start_date",
            "end_date",
            "n_assets_or_portfolios",
            "n_obs",
            "missing_rate",
            "vintage",
            "checksum",
            "status",
        ),
        description="Real-data panel inventory.",
    ),
    RequiredColumns(
        name="T_empirical_design_matrix",
        columns=(
            "universe",
            "model",
            "tail_fit",
            "dependence_diagnostic",
            "estimator_candidates",
            "backtest_window",
            "status",
        ),
        description="Empirical design matrix.",
    ),
    RequiredColumns(
        name="T_tail_index_placeholder",
        columns=(
            "series",
            "side",
            "estimator",
            "threshold",
            "k",
            "alpha_hat",
            "ci_low",
            "ci_high",
            "active_flag",
            "common_index_group",
            "status",
        ),
        description="Real-data tail-index table.",
    ),
    RequiredColumns(
        name="T_dependence_diagnostic_placeholder",
        columns=(
            "pair",
            "diagnostic",
            "threshold_grid",
            "estimate",
            "interval_low",
            "interval_high",
            "decision",
            "selected_model_layer",
            "status",
        ),
        description="Dependence diagnostic table.",
    ),
    RequiredColumns(
        name="T_var_es_backtest_placeholder",
        columns=(
            "portfolio",
            "model",
            "level",
            "expected_hits",
            "observed_hits",
            "kupiec_p",
            "christoffersen_p",
            "dq_p",
            "es_score",
            "comparative_loss",
            "status",
        ),
        description="VaR/ES backtest table.",
    ),
    RequiredColumns(
        name="T_crisis_attribution_placeholder",
        columns=(
            "window",
            "axis_share",
            "latent_shock_share",
            "block_share",
            "spectral_sector_share",
            "hidden_cone_share",
            "dominant_driver",
            "status",
        ),
        description="Crisis-window attribution table.",
    ),
    RequiredColumns(
        name="T_realdata_experiments",
        columns=(
            "experiment",
            "target",
            "estimators",
            "forecast_levels",
            "output_files",
            "status",
        ),
        description="Real-data experiment registry.",
    ),
    RequiredColumns(
        name="T_runtime_placeholder",
        columns=(
            "model",
            "estimator",
            "phase",
            "n_replications",
            "tail_evaluations",
            "runtime_seconds",
            "variance",
            "work_normalized_variance",
            "status",
        ),
        description="Runtime / work-normalized variance table.",
    ),
    RequiredColumns(
        name="T_sim_results_independent",
        columns=(
            "design",
            "N",
            "alpha",
            "x",
            "n",
            "first_order",
            "second_order",
            "mu_hat",
            "rel_error",
            "wnre",
            "runtime_seconds",
            "status",
        ),
        description="Independent simulation results.",
    ),
    RequiredColumns(
        name="T_sim_results_dependent",
        columns=(
            "family",
            "design",
            "estimator",
            "x",
            "mu_hat",
            "ref_mu",
            "rel_error",
            "wnre",
            "runtime_seconds",
            "status",
        ),
        description="Dependent simulation results.",
    ),
]


SCHEMA: dict[str, RequiredColumns] = {s.name: s for s in _SCHEMAS}


def get_schema(name: str) -> RequiredColumns:
    """Return the schema entry for ``name`` (with or without ``.csv`` suffix)."""
    stem = name.removesuffix(".csv")
    if stem not in SCHEMA:
        raise KeyError(f"Unknown schema {stem!r}. Known: {sorted(SCHEMA)}")
    return SCHEMA[stem]


def all_schema_names() -> Sequence[str]:
    return tuple(SCHEMA)
