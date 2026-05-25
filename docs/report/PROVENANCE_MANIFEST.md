# Provenance Manifest

Built by mechanical inspection of the source tree. Status assignment follows the four-rule provenance protocol exactly. **Only assets reachable from the live `main.tex` input chain are listed.** Orphan figure/table/diagram files (those not `\input`-ed by any live file) are inventoried in the consolidated edit plan under D-D1 (orphan disposition); they are out of scope for status-labeling because they do not render in the PDF.

## Rule references
- **Real** — table cells contain only real numbers, strings, or categorical labels; figure file renders an actual diagram/chart.
- **Partially-real** — most rows real, isolated placeholder rows/cells (e.g. one row of a multi-row table).
- **Planned** — at least one cell contains literal `xx`, `TBD`, `TODO`, em-dash placeholder, or empty expected value; or figure file is a blank/placeholder/instruction sheet.
- **Theoretical** — derivation, taxonomy, method-comparison, or method-design table; no source CSV is contemplated.

---

## Figures (live tree only)

All ten figures `\input`-ed by live section/appendix files are short TikZ "instruction sheets" containing the literal phrase `Implementation placeholder` rendered on the page, plus a CSV filename and a "Replace this box after generating the plot" instruction. None contains an actual chart, pgfplots axis, or rendered diagram.

| Label | Status | Evidence (file path · token) | Notes |
|---|---|---|---|
| `figures/F1_tail_equivalence.tex` | **planned** | file contains literal `Implementation placeholder` (×2) and instruction text | Cited from `sections/03_independent_baseline.tex:68`. |
| `figures/F8_second_order.tex` | **planned** | file contains literal `Implementation placeholder` (×2) | Cited from `sections/03_independent_baseline.tex:109`. |
| `figures/F11_common_shock_geometry.tex` | **planned** | file contains literal `Implementation placeholder` (×2) | Cited from `sections/04_dependent_cdmcs.tex:145`. |
| `figures/F12_spectral_simplex_placeholder.tex` | **planned** | filename + `Implementation placeholder` text | Cited from `sections/05_mrv_spectral.tex:121`. |
| `figures/F13_hidden_cones_placeholder.tex` | **planned** | filename + `Implementation placeholder` text | Cited from `sections/06_hidden_regular_variation.tex:97`. |
| `figures/F14_simulation_design_placeholder.tex` | **planned** | filename + `Implementation placeholder` text | Cited from `sections/08_simulation_study.tex`. |
| `figures/F15_tail_dependence_heatmap_placeholder.tex` | **planned** | filename + `Implementation placeholder` text | Cited from `sections/09_real_data_analysis.tex`. |
| `figures/F16_var_es_dashboard_placeholder.tex` | **planned** | filename + `Implementation placeholder` text | Cited from `sections/09_real_data_analysis.tex`. |
| `figures/F17_spectral_by_period_placeholder.tex` | **planned** | filename + `Implementation placeholder` text | Cited from `sections/09_real_data_analysis.tex`. |
| `figures/F18_hill_plots_placeholder.tex` | **planned** | filename + `Implementation placeholder` text | Cited from `sections/09_real_data_analysis.tex`. |

**Conclusion: 10/10 live figures are planned.** All prose claims that cite these figures inherit planned status and require projection voice.

---

## Diagrams (live tree only)

All six diagrams `\input`-ed by live section files are real TikZ flowcharts/DAGs/plates that render structural information (proof dependencies, decision trees, model plates, estimator workflows). No placeholder text; no CSV-instruction header. Diagrams are structural illustrations and are **theoretical** under the rule.

| Label | Status | Evidence | Notes |
|---|---|---|---|
| `diagrams/D3_estimators_flow.tex` | **theoretical** | TikZ flowchart of estimator relationships | Real diagram, no source CSV. |
| `diagrams/D8_dependent_hierarchy.tex` | **theoretical** | TikZ hierarchy of dependence classes | Real diagram, no source CSV. |
| `diagrams/D9_estimator_decision_tree.tex` | **theoretical** | TikZ decision tree | Real diagram, no source CSV. |
| `diagrams/D10_mrv_radial_angular.tex` | **theoretical** | TikZ radial-angular decomposition diagram | Real diagram, no source CSV. |
| `diagrams/D11_estimator_workflow.tex` | **theoretical** | TikZ workflow boxes-and-arrows | Real diagram, no source CSV. |
| `diagrams/D12_real_data_workflow.tex` | **theoretical** | TikZ real-data workflow diagram | Real diagram, no source CSV. |

---

## Tables (live tree only)

17 tables `\input`-ed by live section files. Each row is justified by direct inspection of the source file.

| Label | Status | Evidence | Notes |
|---|---|---|---|
| `tables/T_crisis_attribution_placeholder.tex` | **planned** | 30 `xx` tokens across cells; filename includes `_placeholder` | Pure planned data table. |
| `tables/T_data_panels.tex` | **planned** | 30 `xx` tokens in vintage/window/T/N cells | Empirical-design table awaiting frozen vintage. |
| `tables/T_dependence_diagnostic_placeholder.tex` | **planned** | 36 `xx` tokens; filename includes `_placeholder` | Pure planned diagnostics table. |
| `tables/T_dependent_estimator_summary.tex` | **theoretical** | 0 placeholder tokens; structural estimator taxonomy with closed-form properties | No source CSV contemplated. |
| `tables/T_empirical_design_matrix.tex` | **partially-real** | Real portfolio/method columns; final column `Window xx; status xx` in every row | 5 rows; last column placeholders, other cells real. |
| `tables/T_estimator_summary.tex` | **theoretical** | 0 placeholder tokens; estimator-by-property comparison with closed-form column "tail evals", "guarantee" | No source CSV contemplated. |
| `tables/T_experiment_status.tex` | **real** | 0 placeholder tokens; cells contain genuine categorical labels including the string `planned` as a category | The string "planned" is a real status label, not a placeholder. |
| `tables/T_extension_ranking.tex` | **theoretical** | 0 placeholder tokens; subjective rank/innovation/contribution/feasibility scoring | Author judgment table; no source CSV. |
| `tables/T_literature_map_dependent.tex` | **theoretical** | 0 placeholder tokens; literature taxonomy with citations and roles | No source CSV. |
| `tables/T_planned_real_data_figures.tex` | **theoretical** | 0 placeholder tokens; descriptive mapping of figure ID to diagnostic and replacement rule | Planning table; all cells real descriptive strings. |
| `tables/T_realdata_experiments.tex` | **partially-real** | Real E1–E10 experiment descriptions + 7 `xx` cells in the last "status/result" column | 10 rows; status column awaits run, descriptive columns are real. |
| `tables/T_runtime_placeholder.tex` | **planned** | 30 `xx` tokens; filename includes `_placeholder` | Pure planned runtime table. |
| `tables/T_sim_results_dependent.tex` | **planned** | 30 `xx` tokens | Simulation-results table awaiting run. |
| `tables/T_sim_results_independent.tex` | **planned** | 28 `xx` tokens | Simulation-results table awaiting run. |
| `tables/T_simulation_grid.tex` | **partially-real** | Real Sims-I–V descriptors; "Truth" and "Estimators-tested" columns contain `\xx` | 5 rows; design columns real, status/truth columns placeholder. |
| `tables/T_tail_index_placeholder.tex` | **planned** | 35 `xx` tokens; filename includes `_placeholder` | Pure planned diagnostic table. |
| `tables/T_var_es_backtest_placeholder.tex` | **planned** | 42 `xx` tokens; filename includes `_placeholder` | Pure planned backtest table. |

---

## Summary by status

| Status | Figures | Diagrams | Tables | Total |
|---|---|---|---|---|
| real | 0 | 0 | 1 | 1 |
| partially-real | 0 | 0 | 3 | 3 |
| planned | 10 | 0 | 10 | 20 |
| theoretical | 0 | 6 | 3 | 9 |

---

## Prose-claim inheritance

The four-rule manifest implies the following for prose:

- **Section 3 (independent baseline)** cites F1 and F8 — both planned. Any indicative-voice claims about simulation evidence in §3 must be softened to projection voice.
- **Section 4 (dependent CdMCs)** cites F11 — planned.
- **Section 5 (MRV spectral)** cites F12 — planned.
- **Section 6 (hidden RV)** cites F13 — planned.
- **Section 8 (simulation study)** cites F14 — planned, and the simulation result tables T_sim_results_* are planned.
- **Section 9 (real data analysis)** cites F15–F18 (all planned) plus the placeholder real-data tables.
- **Section 7 (estimators and efficiency)** cites only `T_estimator_summary` (theoretical) and a diagram. No status-labeling required for §7.
- **Section 10 (discussion)** cites no assets directly; discussion claims that reference earlier asset-backed claims inherit accordingly.

Status-labeling edits in the consolidated edit plan reference this manifest. Any change to a manifest entry below will be propagated through the plan.
