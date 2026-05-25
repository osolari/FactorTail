# Coding Agent Handoff — FactorTail

## 1. Project overview

This repository contains the LaTeX source for "Sharp Tail Asymptotics and
Efficient Rare-Event Simulation for Independent and Dependent Regularly-Varying
Factor Models" by O. Shams Solari and F. Pourbabaee. The paper sharpens the
independent finite-$N$ regularly-varying factor result of
\citet{PourbabaeeSolari2019} and extends it to dependent models via dependent
conditional Monte Carlo (CdMC) identities, multivariate regular variation
(MRV), and hidden regular variation (HRV). The theoretical content is complete
and proved; the simulation and real-data sections are written as protocols
with placeholder figures and tables that this handoff will turn into executed
outputs.

The reference implementation is the open-source **FactorTail** library at
<https://github.com/osolari/FactorTail>. The library's module structure
mirrors the manuscript section-by-section, and every algorithm in
`appendices/E_algorithms_and_pseudocode.tex` has a one-to-one Python entry
point. All commits described below are commits to that repository.

The manuscript currently compiles to a 65-page PDF with 0 undefined references
and 0 undefined citations.

## 2. Build instructions

```
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Required LaTeX packages: standard TeX Live distribution plus
`texlive-fonts-extra` (provides `dsfont.sty`). The `algorithm`, `algorithmicx`,
`booktabs`, `longtable`, `tabularx`, `hyperref`, `cleveref`, `microtype`,
`enumitem`, and `xcolor` packages are required. No external graphics other
than the placeholder TikZ files are needed for compilation.

## 3. Implementation tasks (in priority order)

Each task corresponds to one row of `T_experiment_status` and to one row of
the seven-row priority manifest in `appendices/G_experiment_manifest.tex`.

- **P1 — Independent replication.** Implement the data-generating processes
  of Family I in §8, run summed CdMC and stratified CdMC, and generate
  `results/F1_tail_equivalence.csv`, `results/F8_second_order.csv`, and the
  rows of `T_sim_results_independent` corresponding to the design grid.
- **P2 — Common-shock simulation.** Implement the latent-shock model
  $X=BZ+E$ of Family II; generate `results/F11_common_shock_geometry.csv` and
  the Family II rows of `T_sim_results_dependent`.
- **P3 — Copula-kernel test.** Implement the Family IV copulas (Gaussian,
  Student $t$, Clayton, Gumbel, Frank, vine); generate the Family IV rows of
  `T_sim_results_dependent`.
- **P4 — MRV spectral test.** Implement the Family V radial-angular DGPs;
  generate `results/F12_spectral_simplex.csv` and the Family V rows of
  `T_sim_results_dependent`.
- **P5 — Hidden-cone test.** Implement Family VI hidden-cone mixtures;
  generate `results/F13_hidden_cones.csv` and the Family VI rows of
  `T_sim_results_dependent`.
- **P6 — Public Fama--French data.** Download the Kenneth French Data
  Library panels listed in `appendices/F_data_specs.tex`; execute
  `alg:real-data` on each panel; generate F15--F18 CSVs and the planned
  tables (`T_data_panels`, `T_tail_index_placeholder`,
  `T_tail_dep_placeholder`, `T_var_es_backtest_placeholder`,
  `T_crisis_attribution_placeholder`, `T_runtime_placeholder`,
  `T_empirical_design_matrix` final column, `T_realdata_experiments` status
  column).
- **P7 — CRSP licensed extension.** Optional. Mirror P6 using CRSP security
  data through WRDS, subject to license terms.

## 4. Experiment plan

Each simulation family in §8 specifies a data-generating process,
estimators to be tested, threshold range, and primary diagnostics. The
authoritative version of each plan is the section text plus
`T_simulation_grid`. The reproducibility contract in §8 specifies the
required metadata: generator name and version, master seed, PCG-style spawned
seed per replicate, threshold, number of outer/inner samples, CPU time, peak
memory, git hash, config hash, software versions.

For real-data work, the protocol in §9 specifies the data vintages,
freezing rule, rolling-window length grid, factor models (FF3, FF5,
FF5+momentum), tail-fit methods (Hill, Pickands, POT/GPD), dependence
diagnostics ($\chi$, $\bar\chi$, $\eta$, spectral mass), estimators
(independent, copula-kernel, latent-shock, block, spectral, filtered
historical simulation), confidence levels (99\%, 99.5\%, 99.9\%), backtests
(unconditional coverage, conditional coverage, dynamic quantile, exception
clustering, traffic-light; Acerbi--Szekely ES), and crisis-window definitions.

## 5. Figures and tables to generate

The seven-row priority manifest in `appendices/G_experiment_manifest.tex`
maps each experiment to its required CSV files, figure labels, and table
labels. The replacement contract is: when a CSV passes schema validation
against `results/SCHEMA.md`, the corresponding placeholder figure or table
file may be replaced by a generated file with the same basename. Captions
and labels in the manuscript remain unchanged unless the underlying
diagnostic changes.

Live placeholders to be replaced:

- Figures: F1, F8, F11, F12, F13, F14, F15, F16, F17, F18 (10 files).
- Tables: T_crisis_attribution_placeholder, T_data_panels,
  T_dependence_diagnostic_placeholder, T_empirical_design_matrix (window/status
  cells only), T_realdata_experiments (status cells only), T_runtime_placeholder,
  T_sim_results_dependent, T_sim_results_independent, T_simulation_grid
  (truth/estimators cells only), T_tail_index_placeholder,
  T_var_es_backtest_placeholder (11 files / 4 partially-real).

## 6. Projected (expected) results

These projections are not claimed in the manuscript and are not committed to.
They are guidance for the implementation:

- The independent BRE bound $N^\alpha-1$ should be approached but not
  exceeded in Family I across replicate budgets.
- The corrected second-order expansion should reduce relative error against
  a high-precision reference, especially at moderate thresholds.
- Latent-shock CdMC should outperform observed-coordinate CdMC under
  common-shock designs (Family II) with positive same-sign exposures.
- Block CdMC should outperform observed-coordinate CdMC under Family III
  with strong within-block tail dependence.
- Spectral CdMC should outperform under Family V when non-axis spectral mass
  is large.
- The hidden-cone term should be detectable only when its scale exceeds the
  marginal second-order and mean-shift scales.

## 7. Theory-to-code connections

The estimator definitions and identities in §§3--7 map directly to
implementation:

- `thm:catastrophe-exact`, `thm:sum-equivalence`, `thm:second-order` define
  the first- and second-order targets for Family I diagnostics.
- `thm:dep-cdmc-unbiased` defines the kernel quantity to be evaluated per
  replicate; see `alg:dep-cdmc`.
- `thm:latent-shock-tail`, `prop:latent-shock-bre` define the
  latent-shock estimator; see `alg:latent-cdmc`.
- `thm:block-reduction` defines the block estimator; the block partition is
  selected by dependence diagnostics in §9.
- `thm:mrv-linear-risk`, `prop:radial-cdmc`, `prop:spectral-bre`,
  `prop:spectral-cdmc-bre` define the spectral estimator; see
  `alg:spectral-cdmc`.
- `thm:hidden-second-order`, `lem:sote-primitive`, `lem:binomial-kl` underpin
  the hidden-cone diagnostic.
- `prop:vre` defines the two control-variate variants (oracle and
  sample-split).
- `thm:bernstein-ci` defines the confidence-interval construction used in the
  reproducibility output.

## 8. Open technical questions

- The exact-VRE vs asymptotic-VRE distinction for the control-variate
  estimator (`prop:vre`, part 2) requires a pilot-split size choice; the
  recommended choice (e.g., $n_0=\sqrt{n}$) should be validated in Family I.
- The hidden-tail scale $\Hb_2$ in Family VI requires a model selection
  between Ledford--Tawn $\eta$ estimators and direct cone-mass estimators;
  this should be benchmarked.
- For Family IV (vine copulas), the conditional-kernel evaluation may require
  numerical integration; convergence tolerances should be tighter than the
  Monte Carlo half-width.
- Threshold-stability bands for the empirical spectral measure require a
  bootstrap; block-bootstrap vs stationary-bootstrap choice should be
  documented.

## 9. Files changed/added

Phase Three rewrote or substantively modified the following files:

- `main.tex` (build patches, date string, hyperref setup, cleveref names).
- All twelve live `sections/*.tex` files.
- All seven live `appendices/*.tex` files.
- `references.bib` (key normalization).

98 orphan files (12 sections, 10 appendices, 38 figures, 38 tables,
11 diagrams) were deleted. Live tree counts: 12 sections, 7 appendices,
10 figures, 17 tables, 6 diagrams.

## 10. Do-not-change constraints

- Theorem statements, definitions, and assumption labels are part of the
  manuscript's cross-reference graph. Renaming any of them requires updating
  all references; the current set is consistent.
- The placeholder rule is enforced: any cell containing `\xx{}` must remain
  unfilled until a validated CSV is generated. Filling a placeholder without
  a recorded vintage, config hash, and run id is a protocol violation.
- Captions of placeholder figures and partial-real tables carry an explicit
  `\textbf{(PLANNED).}` or `\textbf{(PARTIAL.)}` prefix. Removing the prefix
  is allowed only when the corresponding output replaces all placeholder
  content in that figure/table.
- The `(PARTIAL.)` prefix indicates that some columns or cells are real and
  some are placeholder. When all placeholder cells in such a table are
  replaced, the prefix is dropped; the prefix never becomes `(PLANNED.)`.
- The CRSP data are licensed; raw CRSP data files must never be committed
  to this repository.
- The bibliography keys are now in `AuthorAuthor...Year` form. New entries
  must follow the same convention.

## 11. FactorTail repository layout

The reference implementation at <https://github.com/osolari/FactorTail> should
mirror the manuscript module-for-module:

```
FactorTail/
├── factortail/
│   ├── __init__.py
│   ├── cdmc/
│   │   ├── independent.py      # §3, alg implicit in proofs
│   │   ├── dependent.py        # §4, alg:dep-cdmc
│   │   ├── latent_shock.py     # §4 (latent), alg:latent-cdmc
│   │   ├── block.py            # §4 (block)
│   │   └── spectral.py         # §5, alg:spectral-cdmc
│   ├── hrv/                    # §6, hidden-cone diagnostics
│   ├── estimators/             # §7: control variates, Bernstein CI
│   ├── diagnostics/            # tail-index, dep, spectral, hidden-cone
│   ├── real_data/
│   │   └── rolling_var_es.py   # alg:real-data
│   ├── io/                     # appx F: schema, writers, validators
│   ├── manifest/               # appx G: replacement-rule enforcement
│   └── cli.py                  # `factortail validate-run`, `factortail run`
├── configs/                    # YAML configs hashed into config_hash
├── results/                    # SCHEMA.md and generated CSV/PDF outputs
├── tests/
├── pyproject.toml
└── README.md
```

CLI entry points:
- `factortail run --config <path>`: executes one experiment row, writes CSV.
- `factortail validate-run <run_id>`: enforces the replacement rules of
  `appendices/G_experiment_manifest.tex`.
- `factortail replace-figure <label>`: swaps a placeholder TikZ file for the
  generated PDF/TeX with the same basename.

Citation: please cite the manuscript and the library together; see the
`CITATION.cff` file in the repository for the canonical citation block.
