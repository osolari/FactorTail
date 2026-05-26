# FactorTail output schema

This file is the authoritative schema for every generated CSV under
`results/`. It mirrors the Python registry in `factortail.io.schema` and is
checked by a pre-commit hook
(`scripts/_dev/check_schema_headers.py`). Each entry below is referenced by
name (without `.csv` suffix); the same name appears in the figure/table
generation scripts under `scripts/generate_*.py`.

All entries additionally carry the provenance metadata columns enforced by
`factortail.io.writers.write_csv`:

- `run_id` (string)
- `config_hash` (SHA-256 of the YAML config)
- `git_hash` (output of `git rev-parse --short HEAD`)
- `code_version` (`factortail.__version__`)
- `run_timestamp` (ISO-8601 UTC, second resolution)

Real-data outputs additionally carry `data_vintage`. Real-data backtests
also carry `model_name`, `sample_start`, `sample_end` when applicable.

## Simulation figures

- `F1_tail_equivalence`: `seed, design, x, n, mu_hat, ci_low, ci_high, first_order, second_order, runtime_seconds`
- `F2_max_vs_sum`: `seed, design, N, alpha, x, n, p_max, p_sum, ratio, ci_low, ci_high, truth_method`
- `F3_exp_eff_vs_x`: `seed, design, N, alpha, x, n, kappa, rel_variance, lambda_n, rate_hat, rate_bound_finite, rate_bound_asymptotic`
- `F4_exp_eff_vs_alpha`: `seed, design, alpha_bar, alpha_min, n, kappa, lambda_n, rate_hat, common_alpha_flag, theory_tag`
- `F5_exp_eff_vs_amin`: `seed, design, alpha_bar, alpha_min, n, kappa, lambda_n, rate_hat, common_alpha_flag, theory_tag`
- `F6_relative_error`: `seed, design, N, alpha, x, n, estimator, pilot_rule, mu_hat, variance, rel_sd, ci_low, ci_high, rho_squared, runtime_seconds, centering_status`
- `F7_stratified`: `seed, design, N, alpha, x, n, estimator, mu_hat, variance, work_norm_variance, tail_evals_per_rep, runtime_seconds, weight_rule`
- `F8_second_order`: `seed, design, x, first_order_error, second_order_error, leave_one_out_term, remainder_estimate`
- `F9_var_path`: `date, loss, var_99, es_99, var_995, es_995, estimator, window, crisis_flag` (+ `data_vintage`)
- `F10_backtest`: `date, level, loss, var, hit, rolling_violation_rate, model, window` (+ `data_vintage`)
- `F11_common_shock_geometry`: `seed, design, x, observed_constant, latent_constant, empirical_tail, ci_low, ci_high, attribution_class`
- `F12_spectral_simplex`: `seed, design, theta_1, theta_2, theta_3, spectral_weight, portfolio_loading, contribution`
- `F13_hidden_cones`: `seed, design, x, axis_term, hidden_pair_term, marginal_second_order, empirical_tail, selected_scale`
- `F14_simulation_dashboard`: `family, estimator, threshold, rel_error, wnre, runtime, bias, coverage, config_hash`

## Real-data figures

- `F15_tail_dependence_heatmap`: `factor_i, factor_j, threshold_u, chi_hat, chibar_hat, eta_hat, cluster, selected_block` (+ `data_vintage`)
- `F16_var_es_dashboard`: `date, portfolio, model, level, loss, var, es, hit, crisis_flag` (+ `data_vintage`, `config_hash`)
- `F17_spectral_by_period`: `period, theta_1, theta_2, theta_3, theta_4, theta_5, weight, axis_flag, block_flag, stress_flag` (+ `data_vintage`)
- `F18_hill_plots`: `date, series, side, threshold_k, estimator, alpha_hat, ci_low, ci_high, selected_threshold, active_flag` (+ `data_vintage`)

## Tables

- `T_data_panels`: `panel, source, frequency, start_date, end_date, n_assets_or_portfolios, n_obs, missing_rate, vintage, checksum, status`
- `T_empirical_design_matrix`: `universe, model, tail_fit, dependence_diagnostic, estimator_candidates, backtest_window, status`
- `T_tail_index_placeholder`: `series, side, estimator, threshold, k, alpha_hat, ci_low, ci_high, active_flag, common_index_group, status`
- `T_dependence_diagnostic_placeholder`: `pair, diagnostic, threshold_grid, estimate, interval_low, interval_high, decision, selected_model_layer, status`
- `T_var_es_backtest_placeholder`: `portfolio, model, level, expected_hits, observed_hits, kupiec_p, christoffersen_p, dq_p, es_score, comparative_loss, status`
- `T_crisis_attribution_placeholder`: `window, axis_share, latent_shock_share, block_share, spectral_sector_share, hidden_cone_share, dominant_driver, status`
- `T_realdata_experiments`: `experiment, target, estimators, forecast_levels, output_files, status`
- `T_runtime_placeholder`: `model, estimator, phase, n_replications, tail_evaluations, runtime_seconds, variance, work_normalized_variance, status`
- `T_sim_results_independent`: `design, N, alpha, x, n, first_order, second_order, mu_hat, rel_error, wnre, runtime_seconds, status`
- `T_sim_results_dependent`: `family, design, estimator, x, mu_hat, ref_mu, rel_error, wnre, runtime_seconds, status`

## Replacement rule

Per appendix G of the manuscript, a placeholder figure/table in the LaTeX
source may be replaced by a generated file with the same basename only
after:

1. The CSV exists and passes schema validation (`factortail validate-run
   <run_id>`).
2. A run record JSON exists in `results/_run_<run_id>.json` containing
   `run_id`, `config_hash`, `git_hash`, `seed`, and the list of CSVs.
3. The generated PDF/TeX has the same basename as the placeholder.
4. The manuscript caption and label remain unchanged unless the underlying
   diagnostic changes.
