# Changelog — Phase Three edits

Entries are in document order; identifiers match `CONSOLIDATED_EDIT_PLAN.md`.
Only substantive changes are listed. Build-log audits (warning counts) are not
edits and are not listed here.

## Build hygiene

- **Build-Build1** — `main.tex`. Fixed `\theHALG@line` patch to reference
  `\thealgorithm` (the algorithm package's counter) rather than the undefined
  `\theHalgorithm`. Removed the duplicate `\renewcommand`. Eliminates the 32
  undefined-control-sequence errors observed at baseline.
- **Build-Build2** — `main.tex`. Added `\crefname`/`\Crefname` entries for
  `assumption`, `definition`, `remark`, `example`, `algorithm`. Eliminates the
  cleveref format warnings for these label types.
- **Build-Build3** — `main.tex`. Added `\hypersetup` with `pdftitle` and
  `pdfauthor` strings (plain-text only) to suppress the hyperref "Token not
  allowed in a PDF string" warnings produced by math/macros in the title.

## Global

- **Global-Global1** — `appendices/A_notation.tex`. Rewrote the notation
  appendix into a structured glossary partitioned by subject (probability and
  indicator conventions, loss vector / sums / selected maxima, regular
  variation / active-set constants, estimators / efficiency notions, dependence
  classes / conditional kernels, MRV / HRV, financial / empirical objects,
  output conventions and placeholder rule). Total length 162 lines.
- **Global-Global3** — `main.tex`. Changed `\date{Long-form development draft:
  \today}` to `\date{Manuscript draft: \today}`.

## Section 00 — Abstract

- **00-Lit1** — `sections/00_abstract.tex`. Appended a positioning paragraph
  that names the prior work being sharpened (Pourbabaee--Solari 2019) and the
  external literature being integrated (Asmussen--Kroese, Hartinger--Kortschak,
  Hult--Lindskog--Mikosch--Samorodnitsky, Resnick, Ledford--Tawn,
  Maulik--Resnick, Blanchet--Rojas-Nandayapa, Cheng--Fuh--Pang) and forward-
  refs the annotated literature synthesis.

## Section 01 — Introduction

- **01-C1** — `sections/01_introduction.tex`. Added a `Roadmap of assumptions`
  subsection just before `Contributions`, listing the cumulative assumption
  stack invoked by each main result.
- **01-B1** — `sections/01_introduction.tex`. Replaced the `Long-form empirical
  design` paragraph by a `Long-form empirical design (planned)` paragraph that
  explicitly frames simulation and real-data sections as protocols rather than
  results, and notes that figures and tables are placeholders.

## Section 01b — Literature and positioning

- **01b-Lit2** — `sections/01b_literature_and_positioning.tex`. Added a
  `Positioning relative to Pourbabaee--Solari (2019)` paragraph stating the
  four specific sharpening claims (scale-invariant BRE, corrected second-order
  with leave-one-out mean, dependent-CdMC identity, MRV/HRV extensions).
- **01b-Lit3** — Added a `Recent developments and outstanding gaps`
  subsection citing the post-2020 literature and listing the three specific
  gaps this paper addresses.

## Section 02 — Setup and notation

- **02-C1, 02-C2, 02-D1, 02-H1** — `sections/02_setup_and_notation.tex`.
  Added a `Standing assumptions` subsection with five labelled
  `\begin{assumption}` blocks: `ass:rv-common-ref`, `ass:active-nonempty`,
  `ass:tie`, `ass:measurability`, `ass:sote`.

## Section 03 — Independent baseline

- **03-A1** — `sections/03_independent_baseline.tex` and
  `appendices/B_independent_proofs.tex`. Direct $N=1$ specialization check is
  preserved in the theorem statement; verification notes added to appendix B
  for the Lomax cross-term and the scale-invariance of the BRE bound.
- **03-B1** — Added `\begin{proof}[Proof sketch]` blocks after each of
  `thm:catastrophe-exact`, `thm:sum-equivalence`, `thm:second-order` pointing
  to the full proofs in `appx:independent-proofs`.
- **03-B2** — Theorem statements now cross-reference the standing assumptions
  from §2 (`ass:ind-pte`, `ass:ind-sbj`, `ass:sote-ind`). To avoid a duplicate
  label, the §3-specific second-order assumption is renamed `ass:sote-ind`.
- **03-E1, 03-E2** — Captions of F1 and F8 prefixed with `\textbf{(PLANNED).}`
  and softened to projection voice.

## Section 04 — Dependent CdMCs

- **04-B1** — `sections/04_dependent_cdmcs.tex`. Added proof-sketch blocks
  after `thm:dep-cdmc-unbiased`, `prop:dep-envelope-bre`,
  `thm:latent-shock-tail`, `thm:block-reduction`, each pointing to
  `appx:dependent-proofs`.
- **04-B2** — `appendices/C_dependent_proofs.tex`. Added
  `\begin{remark}[Population identity versus estimator]`
  (`rem:pop-vs-est`) distinguishing the population-level identity from the
  estimator-level unbiasedness statement.
- **04-B3** — Added `\begin{remark}[Numerical stability of conditional-kernel
  evaluation]` (`rem:numerical-stability`) recommending log-scale and
  log-sum-exp evaluation for deep-tail kernels.
- **04-C1** — Added `\begin{remark}[Identifiability of conditional kernels]`
  (`rem:kernel-identifiability`) explaining that the dependent-CdMC kernel is
  not automatically identifiable from data, motivating the latent-shock,
  block, copula, MRV, and HRV specializations.
- **04-E1** — Caption of F11 prefixed with `\textbf{(PLANNED).}`.

## Section 05 — MRV spectral

- **05-A1** — Proof-sketch block added after `thm:mrv-linear-risk`; full
  proofs of `thm:mrv-linear-risk`, `prop:radial-cdmc`, `prop:spectral-bre`
  moved into `\begin{proof}` environments in `appendices/C_dependent_proofs.tex`.
- **05-B1** — Added `\begin{definition}[Multivariate regular variation]`
  (`def:mrv`) using the vague-convergence formulation.
- **05-B2** — Added `\begin{definition}[Spectral measure]`
  (`def:spectral-measure`).
- **05-B3** — Added `\begin{definition}[Tail equivalence in the MRV sense]`
  (`def:mrv-tail-equiv`), connecting to the independent baseline as the
  axis-concentrated special case.
- **05-C1** — Added `\begin{remark}[Identifiability of the spectral measure]`
  (`rem:spectral-identifiability`) discussing identifiability under the
  chosen radial normalization.
- Added `\begin{assumption}[MRV loss set is admissible]` (`ass:mrv-loss`)
  to resolve the reference from appendix C.
- **05-E1** — Caption of F12 prefixed with `\textbf{(PLANNED).}` (already
  worded in projection voice).

## Section 06 — Hidden regular variation

- **06-A1** — Proof-sketch block added after `thm:hidden-second-order`;
  full proof moved into `\begin{proof}` environment in
  `appendices/D_second_order_and_hidden_rv.tex`.
- **06-B1** — Added `\begin{definition}[Hidden regular variation]`
  (`def:hrv`) with citations to Ledford--Tawn, Resnick, Maulik--Resnick,
  Das--Mitra--Resnick.
- **06-B2** — Promoted the hidden-cone result from `proposition` to
  `theorem` (`thm:hidden-second-order`); the dangling reference in appendix D
  was updated accordingly.
- **06-E1** — Caption of F13 prefixed with `\textbf{(PLANNED).}`.

## Section 07 — Estimators and efficiency

- **07-A1, 07-B1, 07-B2, 07-C1** — `sections/07_estimators_and_efficiency.tex`.
  Added `\begin{definition}[BRE, VRE, log-efficiency]` (`def:efficiency-notions`),
  `\begin{definition}[Work, work-normalized variance, efficiency frontier]`
  (`def:work-normalized`), and a new subsection lifting the efficiency claims
  into formal propositions (`prop:ind-cdmc-bre`, `prop:dep-cdmc-bre`,
  `prop:latent-shock-bre`, `prop:spectral-cdmc-bre`). Added
  `\begin{proposition}[Exact and asymptotic VRE for the centered control-variate
  estimator]` (`prop:vre`) distinguishing oracle vs sample-split centering, and
  `\begin{theorem}[Bernstein-type confidence interval for bounded CdMC
  estimators]` (`thm:bernstein-ci`).
- **E-C1** — `appendices/E_algorithms_and_pseudocode.tex`. Added per-algorithm
  paragraphs stating per-replicate complexity and numerical-stability notes for
  `alg:dep-cdmc`, `alg:latent-cdmc`, `alg:spectral-cdmc`, `alg:real-data`.

## Section 08 — Simulation study

- **08-D1** — Renamed `\section{Simulation Study Protocol}` to
  `\section{Simulation Design and Projected Diagnostics}`.
- **08-E1** — Caption of F14 prefixed with `\textbf{(PLANNED).}`.
- **08-E2** — Caption of `T_simulation_grid` prefixed with
  `\textbf{(PARTIAL.)}` and revised to state which columns are populated.
- **08-E3** — Captions of `T_sim_results_independent` and
  `T_sim_results_dependent` prefixed with `\textbf{(PLANNED).}`.
- **08-E4** — Prose throughout §8 converted to projection voice ("is designed
  to verify ...", "will report ...") for all claims downstream of planned
  outputs.
- **08-C1** — Added `\begin{remark}[Seeds, reproducibility, and compute
  budget]` (`rem:sim-reproducibility`).
- Caption of `T_experiment_status` updated to note that the categorical labels
  `planned` and `optional/planned` are real entries, not placeholders.

## Section 09 — Real data analysis

- **09-D1** — Renamed `\section{Extensive Real-Data Analysis Plan}` to
  `\section{Real Data Analysis: Protocol and Projected Outputs}`.
- **09-E1 through 09-E12** — Captions of F15, F16, F17, F18,
  `T_data_panels`, `T_empirical_design_matrix`, `T_realdata_experiments`,
  `T_runtime_placeholder`, `T_tail_index_placeholder`,
  `T_var_es_backtest_placeholder`, `T_crisis_attribution_placeholder`,
  `T_dependence_diagnostic_placeholder` prefixed with `\textbf{(PLANNED).}` or
  `\textbf{(PARTIAL.)}` according to the manifest classification.
- **09-C1** — Added a `Data panels, vintages, and freezing rules` subsection
  with explicit vintage-recording and bit-for-bit re-runnability rules.
- **09-C2** — Cross-references to `appx:data-specs` added at the
  reporting-contract paragraph.
- Prose throughout §9 converted to projection voice for downstream-output
  claims.

## Section 10 — Discussion

- **10-D1** — Restructured the opening subsection into two explicit callouts:
  `Theoretical (established under the stated assumptions)` enumerating all
  proved results with their labels, and `Projected (planned, not yet
  executed)` enumerating the planned simulation and real-data outputs.
- **10-B1** — Added a `Limitations and counterexamples` subsection covering
  (a) BRE failure as $N\to\infty$, (b) conditional-kernel misspecification,
  (c) HRV identification challenges.
- **10-Lit1** — Added a `Connection to the literature placement` subsection
  reconnecting §10 to §1b.

## Appendices

- **A-C1** — Covered by Global-Global1 above.
- **B-A1** — `appendices/B_independent_proofs.tex` rewritten with proper
  `\begin{proof}` environments for the four results
  (`thm:catastrophe-exact`, `thm:sum-equivalence`, `thm:second-order`,
  independent-CdMC unbiasedness and BRE).
- **B-C1** — Verification notes appended (Lomax second-order cross-term;
  scale-invariance of the BRE bound).
- **C-A1** — `appendices/C_dependent_proofs.tex` rewritten with proper
  `\begin{proof}` environments for `thm:dep-cdmc-unbiased`,
  `prop:dep-envelope-bre`, `thm:latent-shock-tail`, `thm:block-reduction`,
  `thm:mrv-linear-risk`, `prop:radial-cdmc`, `prop:spectral-bre`; added
  `\begin{remark}` `rem:pop-vs-est`.
- **D-A1** — `appendices/D_second_order_and_hidden_rv.tex` rewritten with a
  proper `\begin{proof}` of `thm:hidden-second-order`.
- **D-A2** — Added `\begin{lemma}[Sufficient condition for the local second-
  order equivalence]` (`lem:sote-primitive`) and `\begin{lemma}[Binomial KL
  Taylor expansion]` (`lem:binomial-kl`).
- **E-Build1** — Verified algorithm line numbers render correctly after the
  Build-Build1 patch.
- **F-C1** — `appendices/F_data_specs.tex`. Added vintage and citation
  paragraphs for the French data library and CRSP/WRDS.
- **G-C1** — `appendices/G_experiment_manifest.tex`. Rewrote the priority
  manifest as a single seven-row table aligned with `T_experiment_status`,
  with explicit label cross-references for required outputs.

## Orphan disposition

- **D-D1, D-D2, D-D3, D-D4** — Deleted all orphan files (those not `\input`-ed
  by `main.tex`): 12 sections, 10 appendices, 38 figures, 38 tables,
  11 diagrams (98 files total). Live tree now: 12 sections, 7 appendices,
  10 figures, 17 tables, 6 diagrams.

## Bibliography

- **Bib3** — Standardized hyphenated citation keys in `references.bib` and
  all referencing `.tex` files to the no-hyphen `AuthorAuthor...Year`
  convention. 13 keys renamed: `Denisov-Dieker-Shneer2008`,
  `Waudby-Smith-Ramdas2024`, `Simsekli-Sagun-Gurbuzbalaban2019`,
  `Hult-Lindskog-Mikosch-Samorodnitsky2005`, `Nesti-Zocca-Zwart2018`,
  `Nesti-Sloothaak-Zwart2020`, `Acemoglu-Carvalho-Ozdaglar-TahbazSalehi2012`,
  `Crovella-Bestavros1997`, `Finkel-OGorman2024`, `Cheng-Fuh-Pang2025`,
  `Deng-Vidyashankar-Collamore2025`, `deHaan-Stadtmuller1996`,
  `Simsekli-etal-2020`.

## Build status

After all edits applied, `pdflatex/bibtex/pdflatex/pdflatex` exits 0/0/0/0;
zero undefined references, zero undefined citations; PDF is 65 pages. Phase
Four (research-mode citation verification) remains pending and is not part of
this changelog.

## FactorTail software integration

The open-source reference implementation `FactorTail`
(<https://github.com/osolari/FactorTail>) is now woven into the manuscript:

- `main.tex` — `\thanks` footnote on the title; `pdfkeywords` updated to
  include `FactorTail`.
- `sections/00_abstract.tex` — final sentence of the positioning paragraph
  names the library and URL.
- `sections/01_introduction.tex` — new `Open-source reference implementation`
  paragraph in Contributions; closing sentence of `Scope and status of
  empirical claims` points to the library as the canonical reference.
- `sections/08_simulation_study.tex` — reproducibility-contract paragraph
  states that simulation runs are executed through `FactorTail` and that the
  `config_hash` records library version and YAML config.
- `sections/09_real_data_analysis.tex` — reporting-contract paragraph names
  `FactorTail` as the reference implementation and identifies the
  `script_hash` field as the library commit.
- `sections/10_discussion.tex` — closing paragraph names the library as the
  canonical reference for downstream numerical claims.
- `appendices/E_algorithms_and_pseudocode.tex` — `Reference implementation`
  paragraph at top of appendix listing the corresponding module paths
  (`factortail.cdmc.independent`, `factortail.cdmc.dependent`,
  `factortail.cdmc.latent_shock`, `factortail.cdmc.block`,
  `factortail.cdmc.spectral`, `factortail.real_data.rolling_var_es`).
- `appendices/F_data_specs.tex` — output-datasets section identifies
  `factortail.io` as the writer module.
- `appendices/G_experiment_manifest.tex` — opening paragraph identifies
  `factortail.manifest` and the CLI command `factortail validate-run` as the
  enforcement layer for the replacement rules.
