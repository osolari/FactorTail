# Diagnostics

Three layers of diagnostics under `factortail.diagnostics` plus
`factortail.hrv`.

## Marginal tail-index estimators

`factortail.diagnostics.tail_index`:

| Function | What it returns |
|---|---|
| `hill_estimator(x, k)` | $\widehat\alpha_H^{-1} = k^{-1}\sum_{i=1}^k \log X_{(n-i+1)} - \log X_{(n-k)}$ |
| `pickands_estimator(x, k)` | $(\log 2)^{-1}\log\bigl((X_{(n-k+1)} - X_{(n-2k+1)})/(X_{(n-2k+1)} - X_{(n-4k+1)})\bigr)$ |
| `pot_gpd_estimator(x, *, threshold or k)` | MLE of a generalized Pareto fit to excesses |

Each returns `alpha_hat`, `gamma_hat = 1/alpha_hat`, asymptotic SE,
threshold, and `k`. The Hill diagnostic is consistent on Pareto:
$\widehat\alpha_H \to \alpha$ as $k\to\infty$ with $k/n\to 0$.

## Pairwise extremal dependence

`factortail.hrv.ledford_tawn`:

- `chi_chibar(U, V, threshold_u)` returns the empirical
  $\chi(u) = P(U > u \mid V > u)$ and
  $\bar\chi(u) = 2\log P(V>u)/\log P(U>u, V>u) - 1$.
- `ledford_tawn_eta(U, V, k)` is the Hill-based residual
  tail-dependence estimator. For independent uniforms $\eta = 1/2$; for
  the comonotone copula $\eta = 1$.

`factortail.diagnostics.dependence`:

- `chi_diagnostic(X, threshold_u, eta_k)` returns the pairwise
  $(\chi, \bar\chi, \eta)$ matrices.
- `pairwise_dependence_table(X, ...)` produces the long-format
  DataFrame used by figure `F15_tail_dependence_heatmap`.

## Empirical spectral measure

`factortail.diagnostics.spectral`:

- `empirical_spectral_measure(X, k, norm)` returns top-$k$ angular
  exceedances $\widehat\Theta_t = X_t / \|X_t\|$.
- `spectral_constant_estimate(X, exposure, alpha, k)` computes
  $\widehat C_\ell(u) = k^{-1}\sum (\ell(\widehat\Theta_t)_+)^{\widehat\alpha}$.
- `bootstrap_bands(X, exposure, alpha, k_grid, n_boot, scheme)` returns
  percentile bands + SE per $k$ for IID, non-overlapping block, or
  Politis-Romano stationary bootstrap.

## VaR / ES backtests (§9)

`factortail.real_data.backtests`:

- `kupiec_test(hits, level)` — unconditional coverage LR test.
- `christoffersen_test(hits, level)` — conditional coverage (independence + UC).
- `dq_test(hits, level, lags)` — Engle-Manganelli dynamic-quantile test.
- `acerbi_szekely_es(losses, var, es, level)` — Z2 ES exceedance residual.

## Decision tree

The estimator-selection workflow follows the manuscript's
`fig:estimator-decision-tree`: start with marginal tails (Hill /
Pickands / POT), test extremal dependence ($\chi$ / $\bar\chi$ /
$\eta$), check spectral concentration on axes vs rays vs interior,
then route to independent / latent / block / spectral / hidden-cone
estimators accordingly.
