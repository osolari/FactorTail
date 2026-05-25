# Experiment manifest (App. G)

The seven-row priority manifest of appendix G is encoded as
`factortail.manifest._DEFAULT_MANIFEST` and printed by

```bash
factortail list-experiments
```

| Priority | Experiment                  | Generated outputs (CSV + figure / table) |
|----------|-----------------------------|------------------------------------------|
| P1       | Independent replication     | F1, F8, T_sim_results_independent        |
| P2       | Common-shock simulation     | F11, T_sim_results_dependent rows (II)   |
| P3       | Copula-kernel test          | T_sim_results_dependent rows (IV)        |
| P4       | MRV spectral test           | F12, T_sim_results_dependent rows (V)    |
| P5       | Hidden-cone test            | F13, T_sim_results_dependent rows (VI)   |
| P6       | Public Fama-French data     | F15, F16, F17, F18, T_data_panels, T_tail_index, T_dependence, T_var_es_backtest, T_crisis_attribution |
| P7       | CRSP licensed extension     | F15, F16 with CRSP universe (optional)   |

Each row maps to one master YAML config in `configs/` (`P1` <-> `F1.yaml`,
`F8.yaml`, `T_sim_results_independent.yaml`; etc.) and the
`scripts/generate_*.py` driver invoked through the YAML's `script:` field.

See also:

- [Reproducibility contract](reproducibility.md)
- [Replacement rules](replacement.md)
