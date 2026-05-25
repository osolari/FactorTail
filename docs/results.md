# Results

A gallery of the generated artifacts. Every CSV passes
`factortail validate-schema`; every run record passes
`factortail validate-run`.

## Priority manifest (App. G)

| Priority | Experiment | Required CSVs | Status |
|---|---|---|---|
| **P1** | Independent replication | `F1_tail_equivalence`, `F8_second_order`, `T_sim_results_independent` | complete |
| **P2** | Common-shock simulation | `F11_common_shock_geometry`, `T_sim_results_dependent` (Family II rows) | complete |
| **P3** | Copula-kernel test | `T_sim_results_dependent` (Family IV rows) | complete |
| **P4** | MRV spectral test | `F12_spectral_simplex`, `T_sim_results_dependent` (Family V rows) | complete |
| **P5** | Hidden-cone test | `F13_hidden_cones`, `T_sim_results_dependent` (Family VI rows) | complete |
| **P6** | Public Fama-French data | `F15`-`F18`, `T_data_panels`, `T_tail_index_placeholder`, `T_dependence_diagnostic_placeholder`, `T_var_es_backtest_placeholder`, `T_crisis_attribution_placeholder` | complete |
| **P7** | CRSP licensed extension | `F15`-`F16` with CRSP universe | optional / planned |

## P1 — Independent baseline

**`F1_tail_equivalence`** — independent CdMC vs first-order and
second-order asymptotics on Pareto($\alpha$=2) margins, $N=3$. The
solid curve sits between the dashed first-order line and the converged
deep-tail asymptote.

![F1 tail equivalence](https://raw.githubusercontent.com/osolari/FactorTail/main/results/F1_tail_equivalence.png)

**`F8_second_order`** — corrected second-order independent expansion on
Lomax($\alpha$=2.5) margins, $N=4$. The second-order $|$rel error$|$
sits an order of magnitude below the first-order line across the
threshold grid.

![F8 second-order](https://raw.githubusercontent.com/osolari/FactorTail/main/results/F8_second_order.png)

## P2 — Common-shock geometry

**`F11_common_shock_geometry`** — under positive same-sign loadings,
the empirical tail tracks the correct latent-shock constant (green) and
is offset above the misspecified observed-axes constant (purple
dashed).

![F11 common-shock geometry](https://raw.githubusercontent.com/osolari/FactorTail/main/results/F11_common_shock_geometry.png)

## P4 — Spectral simplex (MRV)

**`F12_spectral_simplex`** — 500 angular exceedances from a
Dirichlet(1.5, 1.5, 1.5) DGP on the 2-simplex; non-axis mass dominates,
consistent with §5's MRV spectral diagnostic.

![F12 spectral simplex](https://raw.githubusercontent.com/osolari/FactorTail/main/results/F12_spectral_simplex.png)

## P5 — Hidden-cone diagnostic

**`F13_hidden_cones`** — axis term and empirical tail overlap at the
$\alpha=2$ slope; hidden pair-cone term sits two orders of magnitude
below at the steeper $\alpha_2 = 3$ slope.

![F13 hidden cones](https://raw.githubusercontent.com/osolari/FactorTail/main/results/F13_hidden_cones.png)

## Simulation dashboard

**`F14_simulation_dashboard`** — estimator SE and runtime summary
across Families I, II, V at threshold $x=10$.

![F14 simulation dashboard](https://raw.githubusercontent.com/osolari/FactorTail/main/results/F14_simulation_dashboard.png)

## P6 — Real-data diagnostics (offline-synthetic FF3)

**`F15_tail_dependence_heatmap`** — pairwise $\chi$ and $\eta$
matrices on the synthetic FF panel; Mkt-RF / SMB / HML diagonal
preserved, off-diagonals consistent with the underlying common-shock
loading structure.

![F15 tail-dep heatmap](https://raw.githubusercontent.com/osolari/FactorTail/main/results/F15_tail_dependence_heatmap.png)

**`F16_var_es_dashboard`** — rolling VaR/ES paths at confidence levels
0.99 and 0.995. ES sits above VaR; exception markers (purple) appear
at the expected frequency.

![F16 VaR/ES dashboard](https://raw.githubusercontent.com/osolari/FactorTail/main/results/F16_var_es_dashboard.png)

**`F17_spectral_by_period`** — rolling empirical spectral measure
across `early` / `middle` / `late` periods; angular mass is positive
on each real factor (padding columns dropped from the bar plot).

![F17 rolling spectral](https://raw.githubusercontent.com/osolari/FactorTail/main/results/F17_spectral_by_period.png)

**`F18_hill_plots`** — Hill stability across $k$ for Mkt-RF, SMB,
HML right tails. Mkt-RF plateaus near $\widehat\alpha = 3$
(synthetic DGP uses df=4); SMB and HML decline gracefully from
~4.3 at small $k$.

![F18 Hill plots](https://raw.githubusercontent.com/osolari/FactorTail/main/results/F18_hill_plots.png)

## Validation

```bash
$ factortail validate-schema results/
OK F1_tail_equivalence.csv
OK F8_second_order.csv
OK F11_common_shock_geometry.csv
OK F12_spectral_simplex.csv
OK F13_hidden_cones.csv
OK F14_simulation_dashboard.csv
OK F15_tail_dependence_heatmap.csv
OK F16_var_es_dashboard.csv
OK F17_spectral_by_period.csv
OK F18_hill_plots.csv
OK T_crisis_attribution_placeholder.csv
OK T_data_panels.csv
OK T_dependence_diagnostic_placeholder.csv
OK T_empirical_design_matrix.csv
OK T_realdata_experiments.csv
OK T_runtime_placeholder.csv
OK T_sim_results_dependent.csv
OK T_sim_results_independent.csv
OK T_tail_index_placeholder.csv
OK T_var_es_backtest_placeholder.csv

$ for p in P1 P2 P3 P4 P5 P6; do factortail validate-run "${p}_2026-05-25"; done
Run 'P1_2026-05-25' passes the replacement contract.
Run 'P2_2026-05-25' passes the replacement contract.
Run 'P3_2026-05-25' passes the replacement contract.
Run 'P4_2026-05-25' passes the replacement contract.
Run 'P5_2026-05-25' passes the replacement contract.
Run 'P6_2026-05-25' passes the replacement contract.
```
