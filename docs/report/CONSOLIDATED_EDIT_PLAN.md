# Consolidated Edit Plan

Items in document order. Identifier format: `<section>-<category><index>`. Categories: A technical errors, B theoretical development/algorithmic formalization, C rigor & completeness, D clarity & organization, E planned/placeholder material, F new additions, G other substantive, H minor/LaTeX, Lit annotated literature review, Bib bibliography, Build build hygiene, Global cross-cutting.

Approval rules per the protocol:

- Items in category E (status-labeling) are **never defaultable**; each needs an explicit yes/no.
- Items in categories C, D, F, G, H, Lit, Bib, Build, Global may be **defaulted** if marked with a `[default: …]` tag; per-item override is fine.
- Items in category A and B are mandatory unless rejected.
- Items marked `[author decision]` are surfaced with up to three options and a recommendation.

Every E item that softens a prose claim to projection voice is keyed to the corrected manifest.

---

## Build hygiene (top priority — blocks clean compile)

**Build-Build1** — `main.tex:45–48`. The `\theHALG@line` patch references `\theHalgorithm`, which is never defined. Causes 32 undefined-control-sequence errors during compile. Action: replace the broken `\providecommand/\renewcommand` pair with the correct hyperref idiom `\providecommand*{\theHALG@line}{\thealgorithm.\arabic{ALG@line}}` and drop the renew. [default: apply]

**Build-Build2** — cleveref format for label type `assumption` not defined (5 warnings). Action: add `\crefname{assumption}{Assumption}{Assumptions}` and `\Crefname{assumption}{Assumption}{Assumptions}` to the preamble. [default: apply]

**Build-Build3** — 10 hyperref `Token not allowed in a PDF string` warnings from math/macros in section and subsection headings. Action: wrap each offending heading argument with `\texorpdfstring{<math>}{<plaintext>}`. Affects `sec:setup`, `sec:dependent-cdmcs` subheadings, `sec:mrv-spectral` subheadings, and any heading containing macros like `\Aset`, `\CdMC`, `\MRV`. [default: apply per offending heading; will list specifics in execution.]

**Build-Build4** — Overfull \\hbox (53) and underfull \\hbox (128) audit. Most overfull boxes are in tables and one-letter-too-wide URLs in the bibliography render. Action: pass `microtype` is already loaded; add `\sloppy` locally inside the literature tables that overrun, and break long URLs in `references.bib` with `\href`/`\url` line breaks. [default: apply selectively — only to the worst offenders (≥5pt overfull).]

---

## Global passes

**Global-Global1** — Verify and unify notation across all live files against a corrected `appendices/A_notation.tex`. Currently A_notation.tex is short and incomplete (it does not list, for instance, `\Aset`, `\CdMC`, `\CrMC`, `\HRV`, `\MRV`, `\BRE`, `\VRE`, `\indep`, or the signed-tail constants `c_i^+`, `c_i^-`, `p_i^+`, `p_i^-`). Action: expand A_notation.tex into a complete notation glossary partitioned by section. [default: apply]

**Global-Global2** — Theorem environments use `[section]` numbering and a single shared counter (theorem-numbered). This is fine. Verify no theorem/definition/assumption duplicates a label after Global-Global1. [default: apply as a sanity check.]

**Global-Global3** — Switch the manuscript date string from `Long-form development draft: \today` to `Manuscript draft: \today`, or remove it entirely. [author decision]
  - Option a: keep `Long-form development draft:` (current)
  - Option b: change to `Manuscript draft:`
  - Option c: drop the prefix and use only `\today`
  - Recommendation: **b**, to remove development-stage framing now that the manuscript is being prepared for journal submission.

---

## Section 00 — Abstract

**00-C1** — Verify all asset-backed claims in the abstract are projection-voice for planned assets. Inspection needed to find any indicative claims about simulation evidence or empirical findings. Action: identify and soften. [default: apply only after manifest-driven inspection.]

**00-E1** — If the abstract makes any claim that "our simulations show…" or "our empirical study finds…", these must be reframed as "the simulation plan / empirical protocol is designed to …" because every simulation table and every real-data figure is planned. **Per-item yes/no required.** [author decision per occurrence found in execution.]

**00-Lit1** — Abstract positioning statement should preview the new annotated-literature contribution. [default: light pass only]

---

## Section 01 — Introduction

**01-B1** — Contributions list. The introduction's bullet list of contributions enumerates results; cross-check each bullet against the manifest. Bullets that claim empirical or simulation evidence inherit planned status; bullets about theorems/proofs do not. Action: split contributions into "theoretical contributions" (indicative) and "planned experimental and empirical contributions" (projection). [default: apply]

**01-C1** — The introduction should preview the assumption stack used in the main theorems (regularly varying margins; common reference tail; tail equivalence; second-order regular variation; multivariate regular variation; hidden regular variation). Action: add a half-page "Roadmap of assumptions" paragraph just before the contributions list. [default: apply]

**01-E1** — Any claim in the introduction that cites figures/tables: classify against the manifest and soften where needed. **Per-item yes/no in execution.**

**01-H1** — Verify all `\cref{}` targets exist after Build-Build1 fix. [default: apply]

---

## Section 01b — Literature and positioning

**01b-Lit1** — The annotated literature review section currently consists of a short paragraph plus the `T_literature_map_dependent` table and the `T_extension_ranking` table. It needs to be a deep critical synthesis. Action (Phase 4 research-mode for verification, Phase 3 for skeleton): for each of the six literature buckets (regular variation foundations, heavy-tailed rare-event simulation, dependent heavy-tailed sums, multivariate extremes, hidden regular variation, financial tail-risk methods), write 2–4 paragraphs that state what each cited work does, how it relates to this manuscript, what its limitations are, and how the present work differs. [default: apply in Phase 3 as skeleton; Phase 4 verifies references.]

**01b-Lit2** — Position the manuscript explicitly against Pourbabaee–Solari (2019), which is the prior work this paper sharpens. State the precise sharpening claim (sharper constants, the corrected second-order Lomax expansion, the MRV/HRV extensions, the empirical protocol). [default: apply]

**01b-Lit3** — Add explicit comparison with Cheng–Fuh–Pang (2025) and any other recent (post-2020) developments in dependent heavy-tailed simulation. [default: apply; Phase 4 verifies citations.]

**01b-Bib1** — Verify bibliography entries `Cheng-Fuh-Pang2025`, `SamorodnitskySun2016`, `Kortschak2012`, `BasrakSegers2009`, `DasMitraResnick2013`, `MaulikResnick2004`, `MaulikResnick2005` for venue and year correctness. [Phase 4]

---

## Section 02 — Setup and Notation

**02-C1** — The Setup-and-Notation section names notation but does not formalize the model class. It introduces `X`, `S_N`, `M_N`, `\mu(x)`, the active set `\Aset`, the threshold `T_i(x)` and the conditioning rule, plus regular variation and signed-tail constants — but the **assumption stack** itself is split across §§3–6. Action: add a final subsection "Standing assumptions" that names and labels (`\begin{assumption}…\end{assumption}`) each of the assumptions that subsequent sections will invoke: (A1) tail equivalence with common reference, (A2) active set non-empty, (A3) tie-breaking rule, (A4) measurability and integrability. [default: apply]

**02-C2** — Add a notation table at the end of §2 mirroring A_notation. [default: apply if Global-Global1 is approved.]

**02-D1** — `\subsection{Basic objects}` and `\subsection{Regular variation and common reference tails}` are the only subsections. Add subsections for "Active sets and signed contributions", "Dependence classes preview" (a one-paragraph forward pointer to §§4–6), and "Standing assumptions" (per 02-C1). [default: apply]

**02-H1** — Section heading `Setup, Notation, and Dependence Classes` contains "Dependence Classes" but no subsection covers them. Either add a forward-pointer subsection or shorten the title to `Setup and Notation`. Recommendation: add a one-paragraph forward-pointer subsection. [default: apply]

---

## Section 03 — Independent baseline

**03-A1** — Verify the corrected Lomax second-order constant is the one cited in body (memory of prior pass mentions this was a corrected constant). Action: re-verify the cross-term in the Lomax second-order expansion using a direct N=1 substitution check; document the check in a comment. [default: apply — verification-only, no value change.]

**03-B1** — Section currently has 3 theorems and 3 assumptions but **no proofs are stated in-section, and the proofs in `appendices/B_independent_proofs.tex` are written as plain prose without `\begin{proof}…\end{proof}` environments**. Action: wrap each appendix-B proof in a proof environment with a label, and add `\begin{proof}[Proof of Theorem~X]\hfill\\See \cref{appx:indep-proofs}.\end{proof}` (or similar) at the theorem statement in §3. [default: apply]

**03-B2** — Each of the three theorems should have its hypotheses fully stated using the standing assumptions from 02-C1. Currently hypotheses are inline in the theorem statements but sometimes invoke conditions named only in surrounding prose. Action: convert all hypothesis references to `\cref{ass:…}`. [default: apply]

**03-C1** — Add a `\begin{proof}` for any inline sketch that exists, label it as `Proof sketch`, and direct the full proof to the appendix. [default: apply]

**03-E1** — F1_tail_equivalence is planned. The prose at `sections/03_independent_baseline.tex:68` cites it. **Per-item yes/no:** add `(PLANNED)` prefix to caption and convert the surrounding prose claim to projection voice ("the simulation is designed to verify…").

**03-E2** — F8_second_order is planned. Same treatment as 03-E1 at `sections/03_independent_baseline.tex:109`. **Per-item yes/no.**

---

## Section 04 — Dependent CdMCs

**04-A1** — The section states 3 theorems, 1 proposition, 1 assumption. Cross-check theorem hypotheses against the assumption. [default: apply]

**04-B1** — Add `\begin{proof}` environments in `appendices/C_dependent_proofs.tex` matching every body theorem/proposition. Same issue as 03-B1. [default: apply]

**04-B2** — The dependent CdMC identity (Theorem 4.1 in current draft) should be stated as both a population-level identity and as the basis for the algorithm. Action: factor the identity into a Lemma (population) + Proposition (estimator). [default: apply]

**04-B3** — Algorithm `alg:dep-cdmc` (in appendix E) requires inputs to be measurable and the conditional kernels to be specified. Add a numerical-stability remark (when `\(p_i(t)\)` is computed under-flow-prone closed forms, use log-scale). [default: apply]

**04-C1** — Identifiability of the conditional kernel decomposition is not discussed. Add a Remark stating when the conditional kernel CdMC is identifiable from observed data. [default: apply]

**04-E1** — F11_common_shock_geometry is planned. Add `(PLANNED)` prefix and projection-voice softening to caption at `sections/04_dependent_cdmcs.tex:145`. **Per-item yes/no.**

---

## Section 05 — MRV spectral

**05-A1** — Section has 1 theorem and 2 propositions but no proofs. Add proof environments in `appendices/D_second_order_and_hidden_rv.tex` (or split into a new appendix). [default: apply]

**05-B1** — Define MRV formally (vague-tail measure, regularly varying with limit measure on `\mathbb{E}_0`) before stating the spectral CdMC theorem. Currently the MRV definition is invoked but not formally stated. Action: add `\begin{definition}` for MRV. [default: apply]

**05-B2** — State the spectral measure `\(S\)` formally and connect to the limit measure `\(\nu\)`. [default: apply]

**05-B3** — Add a `\begin{definition}` for "tail equivalence in MRV sense" and connect to the independent baseline tail equivalence in §3. [default: apply]

**05-C1** — Discuss the radial-angular decomposition's identifiability and the conditions under which the empirical spectral measure converges. [default: apply]

**05-E1** — F12_spectral_simplex_placeholder is planned. Add `(PLANNED)` prefix and projection-voice softening at `sections/05_mrv_spectral.tex:121`. **Per-item yes/no.**

---

## Section 06 — Hidden regular variation

**06-A1** — Section has 1 proposition and 1 assumption, no theorem, no proofs. Add proof environment for the proposition. [default: apply]

**06-B1** — Define hidden regular variation formally (second-order tail measure on the hidden cone), citing Ledford–Tawn, Resnick. Currently HRV is invoked operationally without a definition. Action: add `\begin{definition}` for HRV. [default: apply]

**06-B2** — State the hidden-cone second-order expansion as a theorem (currently stated as a proposition). Justification: it is a load-bearing result. [author decision]
  - Option a: promote proposition to theorem
  - Option b: keep as proposition
  - Recommendation: **a**, to match its load-bearing role.

**06-C1** — Add an explicit threshold-ordering remark stating when the hidden-cone term is empirically significant (already present in `appendices/D_second_order_and_hidden_rv.tex` but should be cross-referenced from §6). [default: apply]

**06-E1** — F13_hidden_cones_placeholder is planned. Add `(PLANNED)` prefix at `sections/06_hidden_regular_variation.tex:97`. **Per-item yes/no.**

**06-E2** — `\cref{tab:tail-dep-placeholder}` and `\cref{fig:tail-dep-heatmap-placeholder}` at line 117–118. The cited assets are planned. Confirm both labels resolve correctly and prose is projection-voice. **Per-item yes/no.**

---

## Section 07 — Estimators and efficiency

**07-A1** — Section currently has 0 theorems, 0 propositions, 0 lemmas, 0 proofs. It is descriptive prose plus the `T_estimator_summary` table. For a journal submission, this section should state estimator-efficiency results formally. Action: lift the efficiency claims (BRE for CdMC, stratified BRE, control-variate VRE) into formal Propositions with proofs cross-referenced to appendix B. [default: apply]

**07-B1** — Define the work-normalized variance and the work-normalized relative error precisely. Currently the section invokes both but does not state the definitions. Action: add `\begin{definition}` for work, work-normalized variance, work-normalized RMSE, and efficiency frontier. [default: apply]

**07-B2** — State the Bernstein-style finite-sample concentration inequality used to motivate confidence intervals (`thm:bernstein-ci` per `diagrams/D7_proof_dag.tex`). [default: apply]

**07-C1** — Discuss the conditions under which the control-variate VRE estimator is exact vs. asymptotically VRE. The diagram `D7_proof_dag` references `thm:vre`; verify this exists in the live tree or add it. [default: apply]

---

## Section 08 — Simulation study

**08-D1** — Section title is "Simulation study" but the content is a plan, not executed results. Action: rename to "Simulation study: design and projected diagnostics" or "Simulation design" to make scope explicit. [author decision]
  - Option a: rename to "Simulation study: design"
  - Option b: rename to "Simulation design and projected diagnostics"
  - Option c: keep "Simulation study" and rely on per-figure planned labels
  - Recommendation: **b**, most informative.

**08-E1** — F14_simulation_design_placeholder is planned. Add `(PLANNED)` prefix. **Per-item yes/no.**

**08-E2** — T_simulation_grid is partially-real (design columns real, truth/estimators columns `xx`). Caption should say "Simulation grid (design columns populated; estimator outputs to be generated)." **Per-item yes/no.**

**08-E3** — T_sim_results_independent and T_sim_results_dependent are planned. Add `(PLANNED)` prefix to captions. **Per-item yes/no.**

**08-E4** — All prose claims in §8 about what the simulations "show" or "demonstrate" must be projection voice. **Per-item yes/no in execution.**

**08-C1** — Add a Remark listing the seeds, reproducibility, and computational-resource expectations. [default: apply]

---

## Section 09 — Real data analysis

**09-D1** — Section is structured as an empirical protocol with planned outputs, not as a results section. Rename to "Real data analysis: protocol and expected outputs". [author decision]
  - Option a: rename to "Real data analysis: protocol and projected outputs"
  - Option b: keep title and use per-asset planned labels
  - Recommendation: **a**.

**09-E1** — F15_tail_dependence_heatmap_placeholder is planned. **Per-item yes/no.**
**09-E2** — F16_var_es_dashboard_placeholder is planned. **Per-item yes/no.**
**09-E3** — F17_spectral_by_period_placeholder is planned. **Per-item yes/no.**
**09-E4** — F18_hill_plots_placeholder is planned. **Per-item yes/no.**
**09-E5** — T_data_panels is planned. **Per-item yes/no.**
**09-E6** — T_empirical_design_matrix is partially-real. Mark the "Window/status" column placeholder; keep other columns indicative. **Per-item yes/no.**
**09-E7** — T_realdata_experiments is partially-real. Mark the status column placeholder. **Per-item yes/no.**
**09-E8** — T_runtime_placeholder is planned. **Per-item yes/no.**
**09-E9** — T_tail_index_placeholder is planned. **Per-item yes/no.**
**09-E10** — T_var_es_backtest_placeholder is planned. **Per-item yes/no.**
**09-E11** — T_crisis_attribution_placeholder is planned. **Per-item yes/no.**
**09-E12** — T_dependence_diagnostic_placeholder is planned. **Per-item yes/no.**

**09-C1** — Add a subsection on data vintages, freezing rules, and reproducibility. [default: apply]

**09-C2** — Cross-reference `appendices/F_data_specs.tex` from every empirical protocol step. [default: apply]

---

## Section 10 — Discussion

**10-D1** — Discussion should explicitly call out what is theoretical vs. what is projected. [default: apply]

**10-B1** — Add a "Limitations and counterexamples" subsection. Should name (a) the failure of the independent BRE bound when N→∞, (b) failure modes for the conditional kernel CdMC when the kernel is misspecified, (c) HRV identification challenges with limited extreme observations. [default: apply]

**10-Lit1** — Discussion should connect back to the literature placement from §01b. [default: apply]

---

## Appendices

**A-C1** — Expand `appendices/A_notation.tex` to a complete glossary (covered by Global-Global1). [default: apply]

**B-A1** — `appendices/B_independent_proofs.tex` has 0 `\begin{proof}` environments. Wrap every proof in a proper environment with a label that identifies which theorem it proves. [default: apply]

**B-C1** — Verify the BRE rescale-invariance argument is complete (memory of prior pass mentions this was a corrected proof). Action: re-verify by direct symbolic substitution; document the check. [default: apply — verification only.]

**C-A1** — Same as B-A1 for `appendices/C_dependent_proofs.tex`. [default: apply]

**D-A1** — Same as B-A1 for `appendices/D_second_order_and_hidden_rv.tex`; this file has the proposition proofs but as plain prose. [default: apply]

**D-A2** — The KL divergence Taylor expansion is mentioned in `diagrams/D7_proof_dag.tex` (lem:binomial-kl) but the lemma is not stated in any live appendix. Add the lemma and its proof. [default: apply]

**E-Build1** — `appendices/E_algorithms_and_pseudocode.tex` is the file primarily affected by Build-Build1. Verify line numbers render correctly after the patch fix. [default: apply]

**E-C1** — Each of the 4 algorithms in appendix E should specify complexity (per-replicate cost in tail-survival evaluations) and a numerical-stability note. [default: apply]

**F-C1** — `appendices/F_data_specs.tex` should specify vintage, data-license, and citation requirements for CRSP and Fama–French. [default: apply]

**G-C1** — `appendices/G_experiment_manifest.tex` should be a single manifest table of every experiment, its planned figures/tables, and its replacement contract. Cross-check against `tables/T_experiment_status.tex`. [default: apply]

---

## Orphan file disposition

**D-D1** — 12 orphan section files exist in `sections/` and 10 orphan appendix files in `appendices/`. These are prior-pass artifacts not `\input`-ed by `main.tex` and not contributing to the build. Action: delete them. [author decision]
  - Option a: delete (recommended for clean Overleaf submission)
  - Option b: move to a `sections/_archive/` directory (preserves history)
  - Option c: keep in place
  - Recommendation: **a**, to deliver a clean source ZIP.

Orphan section files: `01b_literature_review`, `02_literature_review`, `03_sharpened_asymptotics`, `04_estimators`, `05_efficiency_and_concentration`, `06_dependent_extensions`, `06_simulation_study`, `07_fama_french_application`, `08_dependent_extensions`, `08_dependent_factor_extensions`, `09_discussion`, `10_real_data_analysis_plan`.

Orphan appendix files: `B_proofs`, `C_second_order_RV`, `D_pseudo_code`, `E_reproducibility`, `G_roadmap_details`, `H_dependent_proofs`, `I_empirical_protocol`, `I_empirical_protocols`, `I_real_data_protocol`, `J_planned_experiments`.

**D-D2** — 11 orphan figure files exist (those not `\input`-ed by any live section). Action: same options as D-D1. Recommendation: delete. [author decision]

**D-D3** — 38 orphan table files exist. Action: same options as D-D1. Recommendation: delete. [author decision]

**D-D4** — 11 orphan diagram files exist. Action: same options as D-D1. Recommendation: delete. [author decision]

---

## Bibliography

**Bib1** — `references.bib` is large (28 KB). Phase 4 will verify entries that are cited by the live tree only. Action in Phase 3: prune `references.bib` to only entries actually `\cite`-d in the live tree. [default: apply if approved.]

**Bib2** — Verify all citation keys in `T_literature_map`, `T_literature_map_dependent`, `T_related_work`, and in-section `\citet/\citep` calls resolve. The baseline build reports 0 undefined citations, so this is a sanity check only. [Phase 4]

**Bib3** — Several citation keys use a hyphen-and-year convention (e.g., `Hult-Lindskog-Mikosch-Samorodnitsky2005`, `Cheng-Fuh-Pang2025`); others use the conventional `AuthorYear` (e.g., `AsmussenKroese2006`). [author decision]
  - Option a: keep mixed convention
  - Option b: standardize to `AuthorAuthor…Year` (no hyphens)
  - Option c: standardize to abbreviated `HLMSn2005`/`CFP2025`
  - Recommendation: **b**, conventional and unambiguous; affects ~6 keys.

---

## Phase Four research-mode items (surfaced now, executed later)

**Phase4-Lit1** — Verify venue, year, and DOI for all entries in `references.bib` that are post-2015. Confirm `Cheng-Fuh-Pang2025` exists in the published record (year and venue).

**Phase4-Lit2** — Add the annotated literature review prose drafted in §01b skeleton in Phase 3.

**Phase4-Lit3** — Cross-check Pourbabaee–Solari (2019) arXiv version vs. any published version.

**Phase4-Lit4** — Add 2024–2026 developments in dependent heavy-tailed rare-event simulation and MRV that may not yet be cited.

These do not gate Phase Three.

---

## Summary

| Category | Item count |
|---|---|
| A (technical errors) | 5 |
| B (theoretical development & algorithmic formalization) | 11 |
| C (rigor & completeness) | 14 |
| D (clarity & organization) | 6 |
| E (planned/placeholder — status labeling) | **24** (each yes/no) |
| Lit (annotated literature) | 4 |
| Bib (bibliography) | 3 |
| Build (build hygiene) | 4 |
| Global (cross-cutting) | 3 |
| Phase4 | 4 |
| **Total** | **78** |

All 24 E items require explicit yes/no. All A and B items are mandatory unless rejected. C, D, F, G, H, Lit, Bib, Build, Global items default to "apply" unless overridden.
