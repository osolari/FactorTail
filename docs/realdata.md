# Real-data pipeline

The real-data pipeline (algorithm `alg:real-data`) is in
`factortail.real_data.rolling_var_es`. It performs, for each forecast
date:

1. **Rolling OLS factor fit** on the trailing `window` days.
2. **Marginal tail fit** on each signed factor and residual contribution
   using a Lomax POT fit (the default; Hill is also exposed for the
   diagnostic table).
3. **Estimator selection** via the dependence-diagnostic decision tree.
4. **Solve VaR** by Brent root-finding on the estimator survival curve.
5. **ES** via numerical tail integration.

For backtesting:

- `factortail.real_data.backtests.kupiec_test` — unconditional coverage.
- `factortail.real_data.backtests.christoffersen_test` — conditional
  coverage (independence + UC).
- `factortail.real_data.backtests.dq_test` — Engle-Manganelli dynamic
  quantile.
- `factortail.real_data.backtests.acerbi_szekely_es` — Z2 ES exceedance
  residual.

## Fama-French loader

`factortail.real_data.fama_french.load_fama_french` resolves the panel:

```python
panel = load_fama_french(name="FF3_daily", offline=False)
panel.data         # DataFrame indexed by Date
panel.checksum     # SHA-256 of the cached source CSV
panel.vintage      # source vintage string
```

When `offline=True` (default in CI), `synthesize_panel` produces a
deterministic heavy-tailed surrogate with the same shape and column
names.

## CRSP licensing

CRSP data are licensed and **must never be committed** to this repository
(see `docs/report/appendices/F_data_specs.tex`). The CRSP path (P7 of the
manifest) is an optional extension that requires institutional WRDS
access.
