# Placeholder output schemas

The manuscript intentionally keeps placeholder figures and tables. This file is the authoritative schema for generated outputs. Replace placeholders by generating the CSVs listed below, then exporting plots/tables from those CSVs. If a caption or placeholder comment differs from this file, update the caption/comment or this schema before generating results.

## Simulation figures

- `F1_tail_equivalence.csv`: `seed,spawned_seed,N,alpha,x,n,mu_hat,ci_low,ci_high,first_order,second_order,truth_method,runtime_seconds`
- `F2_max_vs_sum.csv`: `seed,spawned_seed,N,alpha,x,n,p_max,p_sum,ratio,ci_low,ci_high,truth_method`
- `F3_exp_eff_vs_x.csv`: `seed,spawned_seed,N,alpha,x,n,kappa,p_dev_cdmc,p_dev_crmc,lambda_n,rate_hat,R_x,rate_bound_finite,rate_bound_asymptotic,outer_rep`
- `F4_exp_eff_vs_alpha.csv`: `seed,spawned_seed,config,alpha_bar,alpha_min,alpha_vector,n,kappa,lambda_n,rate_hat,common_alpha_flag,theory_tag`
- `F5_exp_eff_vs_amin.csv`: `seed,spawned_seed,config,alpha_bar,alpha_min,alpha_vector,n,kappa,lambda_n,rate_hat,common_alpha_flag,theory_tag`
- `F6_relative_error.csv`: `seed,spawned_seed,N,alpha,x,n,estimator,mu_hat,variance,rel_sd,ci_low,ci_high,pilot_variance,runtime_seconds,centering_status`
- `F7_stratified.csv`: `seed,spawned_seed,N,alpha,x,n,estimator,runtime_seconds,variance,work_norm_variance,tail_evals_per_rep,weight_rule`
- `F8_second_order.csv`: `seed,spawned_seed,N,alpha,x,n,mu_hat,first_order,second_order,normalized_error,target_constant,n_equals_one_check`

## Fama-French application

- `T_tail_indices.csv`: `data_vintage,series,tail,estimator,threshold,k,alpha_hat,ci_low,ci_high,block_length,n_obs,window,common_index_group`
- `F9_var_path.csv`: `data_vintage,date,loss,var_99,es_99,var_995,es_995,estimator,window,crisis_flag,seed,config_hash`
- `T_var_es_comparison.csv`: `data_vintage,date,level,estimator,var,var_ci_low,var_ci_high,es,es_ci_low,es_ci_high,runtime_seconds,variance_ratio,pilot_variance,centering_status`
- `T_backtest.csv`: `data_vintage,model,level,significance_level,expected_hits,observed_hits,kupiec_stat,kupiec_p,christoffersen_stat,christoffersen_p,dq_stat,dq_p,es_stat,es_p,decision`
- `F10_backtest.csv`: `data_vintage,date,level,loss,var,hit,rolling_violation_rate,model,window`
- `T_compute_cost.csv`: `data_vintage,estimator,n,tail_evals_per_rep,hardware,threads,runtime_seconds,sample_variance,ci_half_width,work_norm_variance,centering_status`


## Added dependent-extension and real-data outputs

The edited manuscript adds the following planned outputs. Numeric entries should
remain `xx` in manuscript tables until the corresponding CSV has passed schema
validation.

### Simulation outputs

- `F11_common_shock_constant.csv`: `seed, spawned_seed, design, N, alpha, x, loading_id, empirical_tail, ci_low, ci_high, correct_latent_constant, misspecified_observed_constant, estimator`
- `T_common_shock_experiment.csv`: `design, N, alpha, shock_loading, correct_constant, misspecified_constant, rel_var, runtime, status`
- `F12_tail_dependence_heatmap.csv`: `seed, design, pair_i, pair_j, threshold_u, chi_hat, chibar_hat, eta_hat, active_pair`
- `T_copula_experiment.csv`: `copula, parameter, tail_class, threshold_u, chi_hat, eta_hat, estimator, rel_var, bias_diagnostic, status`
- `F13_spectral_measure.csv`: `seed, design, angle_bin, true_mass, estimated_mass, portfolio_weight_id, spectral_constant`
- `F14_hidden_rv.csv`: `seed, design, x, empirical_tail, axis_term, hidden_cone_term, marginal_second_order, remainder_estimate`
- `T_simulation_dashboard.csv`: `experiment, purpose, main_output, replications, config_hash, validation_flag, status`

### Real-data outputs

- `T_real_data_sources.csv`: `panel, source, frequency, start_date, end_date, observations, vintage, checksum, parser_version`
- `T_empirical_design_matrix.csv`: `universe, model, tail_fit, dependence_diagnostic, estimator_candidates, backtest_window, status`
- `F15_tail_stability_realdata.csv`: `data_vintage, portfolio, factor, side, threshold_k, estimator, alpha_hat, ci_low, ci_high, active_flag`
- `F16_tail_dependence_realdata.csv`: `data_vintage, portfolio, factor_i, factor_j, threshold_u, chi_hat, chibar_hat, eta_hat, active_pair`
- `F17_spectral_realdata.csv`: `data_vintage, portfolio, window_end, angle_bin, estimated_mass, axis_flag, block_flag, interior_flag`
- `T_dependence_diagnostics_plan.csv`: `diagnostic, statistic, threshold_grid, measured_value, decision_rule, selected_path, status`
- `T_estimator_grid_realdata.csv`: `data_vintage, portfolio, forecast_date, estimator, assumption, diagnostic_gate, tail_level, mu_hat, rel_var, runtime, status`
- `T_backtest_plan_extended.csv`: `data_vintage, portfolio, model, level, violations, kupiec_p, christoffersen_p, dq_p, es_score, status`
- `T_robustness_plan.csv`: `perturbation, expected_invariant, measured_value, failure_criterion, action, status`
- `F18_estimator_dashboard_realdata.csv`: `data_vintage, portfolio, estimator, level, rel_var, runtime, rel_half_width, selected_class, status`

## Added real-data and dependence-extension outputs

All added outputs must include metadata columns: `data_vintage`, `run_timestamp`,
`code_version`, `config_hash`, `seed`, `sample_start`, `sample_end`, and
`model_name` unless explicitly static.

### `F11_tail_stability.csv`
Columns: `data_vintage`, `series`, `side`, `threshold_k`, `threshold_u`,
`alpha_hat`, `alpha_lo`, `alpha_hi`, `estimator`, `window_start`, `window_end`,
`active_flag`, `common_index_flag`.

### `F12_tail_dependence_heatmap.csv`
Columns: `data_vintage`, `series_i`, `series_j`, `side_i`, `side_j`, `q`,
`chi_hat`, `chibar_hat`, `eta_hat`, `bootstrap_lo`, `bootstrap_hi`,
`model_implication`.

### `F13_empirical_spectral.csv`
Columns: `data_vintage`, `date`, `radius_threshold`, `theta_1`, `theta_2`,
`theta_3`, `theta_4`, `theta_5`, `loss_direction`, `cone_label`, `weight`.

### `F14_common_shock_loadings.csv`
Columns: `data_vintage`, `window_end`, `shock_id`, `factor`, `loading`,
`tail_index`, `active_flag`, `sign`, `method`, `variance_share`.

### `F15_efficiency_frontier.csv`
Columns: `data_vintage`, `model`, `estimator`, `level`, `runtime_sec`,
`variance`, `ci_half_width`, `work_variance`, `sample_size`, `tail_evals`,
`pilot_size`, `production_size`, `auxiliary_size`.

### Added tables
- `T_data_inventory.csv`: data source, frequency, start/end dates, fields, filters, status.
- `T_portfolio_universe.csv`: portfolio construction, rebalance rule, universe, purpose, status.
- `T_dependence_diagnostics.csv`: diagnostic, object, thresholds, estimates, intervals, decisions.
- `T_model_gate.csv`: pre-specified gates, pass conditions, fallback models, observed status.
- `T_realdata_experiments.csv`: experiment target, estimators, levels, output files, status.
- `T_crisis_windows.csv`: window label, dates, realized max loss, VaR breaches, dominant mechanism.

## Exact placeholder CSVs used by `main.tex`

The compiled long-form draft currently references these figure-source CSVs in
captions. These names take precedence over earlier exploratory names if there is
any conflict.

- `F1_tail_equivalence.csv`: `seed, design, x, n, mu_hat, ci_low, ci_high, first_order, second_order, runtime_seconds`
- `F8_second_order.csv`: `seed, design, x, first_order_error, second_order_error, leave_one_out_term, remainder_estimate`
- `F11_common_shock_geometry.csv`: `seed, design, x, observed_constant, latent_constant, empirical_tail, ci_low, ci_high, attribution_class`
- `F12_spectral_simplex.csv`: `seed, design, theta_1, theta_2, theta_3, spectral_weight, portfolio_loading, contribution`
- `F13_hidden_cones.csv`: `seed, design, x, axis_term, hidden_pair_term, marginal_second_order, empirical_tail, selected_scale`
- `F14_simulation_dashboard.csv`: `family, estimator, threshold, rel_error, wnre, runtime, bias, coverage, config_hash`
- `F15_tail_dependence_heatmap.csv`: `factor_i, factor_j, chi, chibar, eta, cluster, threshold_u, data_vintage`
- `F16_var_es_dashboard.csv`: `date, portfolio, estimator, loss, var, es, exception, level, data_vintage`
- `F17_spectral_by_period.csv`: `period, theta_1, theta_2, theta_3, weight, stress_flag, data_vintage`
- `F18_hill_plots.csv`: `factor, sign, k, hill_alpha, pot_alpha, ci_low, ci_high, data_vintage`

## Current long-form real-data placeholders in `main.tex`

- `T_data_panels.csv`: `panel, source, frequency, start_date, end_date, n_assets_or_portfolios, n_obs, missing_rate, vintage, checksum, status`
- `T_empirical_design_matrix.csv`: `universe, model, tail_fit, dependence_diagnostic, estimator_candidates, backtest_window, status`
- `T_tail_index_placeholder.csv`: `series, side, estimator, threshold, k, alpha_hat, ci_low, ci_high, active_flag, common_index_group, status`
- `F18_hill_plots.csv`: `date, series, side, threshold_k, estimator, alpha_hat, ci_low, ci_high, selected_threshold, active_flag`
- `T_dependence_diagnostic_placeholder.csv`: `pair, diagnostic, threshold_grid, estimate, interval_low, interval_high, decision, selected_model_layer, status`
- `F15_tail_dependence_heatmap.csv`: `factor_i, factor_j, threshold_u, chi_hat, chibar_hat, eta_hat, cluster, selected_block`
- `F17_spectral_by_period.csv`: `period, theta_1, theta_2, theta_3, theta_4, theta_5, weight, axis_flag, block_flag, stress_flag`
- `F16_var_es_dashboard.csv`: `date, portfolio, model, level, loss, var, es, hit, crisis_flag, config_hash`
- `T_var_es_backtest_placeholder.csv`: `portfolio, model, level, expected_hits, observed_hits, kupiec_p, christoffersen_p, dq_p, es_score, comparative_loss, status`
- `T_crisis_attribution_placeholder.csv`: `window, axis_share, latent_shock_share, block_share, spectral_sector_share, hidden_cone_share, dominant_driver, status`
- `T_realdata_experiments.csv`: `experiment, target, estimators, forecast_levels, output_files, status`
- `T_runtime_placeholder.csv`: `model, estimator, phase, n_replications, tail_evaluations, runtime_seconds, variance, work_normalized_variance, status`
