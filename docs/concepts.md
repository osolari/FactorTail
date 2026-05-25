# Concepts

FactorTail mirrors the manuscript module-for-module. The table below
maps each section, theorem, or algorithm to its implementation.

| Manuscript | Module / function |
|---|---|
| §3 Independent baseline | [`factortail.cdmc.independent`](api.md#3-5-conditional-monte-carlo-factortailcdmc) |
| `thm:catastrophe-exact` | `independent_cdmc(...).mu_hat` ≈ `sum_i sf_i(x)` in the deep tail |
| `thm:sum-equivalence` | `factortail.utils.regular_variation.first_order_sum_tail` |
| `thm:second-order` | `factortail.utils.regular_variation.second_order_sum_tail` |
| `prop:ind-cdmc-bre` | Envelope diagnostic returned in `CdMCResult.extra["envelope"]` |
| §4 Dependent CdMC identity | [`factortail.cdmc.dependent`](api.md#3-5-conditional-monte-carlo-factortailcdmc) |
| `alg:dep-cdmc` | `factortail.cdmc.dependent.dependent_cdmc` |
| `thm:latent-shock-tail` | `factortail.cdmc.latent_shock.latent_shock_cdmc` |
| `alg:latent-cdmc` | `factortail.cdmc.latent_shock.latent_shock_cdmc` |
| `thm:block-reduction` | `factortail.cdmc.block.block_cdmc` (+ `fit_block_tail`) |
| §5 MRV + spectral CdMC | [`factortail.cdmc.spectral`](api.md#3-5-conditional-monte-carlo-factortailcdmc) |
| `alg:spectral-cdmc` | `factortail.cdmc.spectral.spectral_cdmc` |
| `thm:mrv-linear-risk` | `factortail.diagnostics.spectral.spectral_constant_estimate` |
| `prop:radial-cdmc`, `prop:spectral-bre` | Same; radial survival is the `radial` argument |
| §6 Hidden RV | [`factortail.hrv`](api.md#6-hidden-regular-variation-factortailhrv) |
| `def:hrv` | `factortail.hrv.ledford_tawn.ledford_tawn_eta` |
| `thm:hidden-second-order` | `factortail.hrv.mixture_estimator.hrv_mixture_estimator` |
| §7 Estimator families / efficiency | [`factortail.estimators`](api.md#7-estimator-families-factortailestimators) |
| `prop:vre` | `factortail.estimators.control_variate` (oracle + sample-split) + `spectral_control_variate` |
| `thm:bernstein-ci` | `factortail.cdmc.base.bernstein_ci` |
| §8 Simulation families I-VI | [`factortail.dgp`](api.md#data-generating-processes-factortaildgp) |
| §9 Real-data protocol | [`factortail.real_data`](api.md#real-data-pipeline-factortailreal_data) |
| `alg:real-data` | `factortail.real_data.rolling_var_es.run_rolling_var_es` |
| Appendix E pseudo-code | Every algorithm has a one-to-one Python entry point. |
| Appendix F data specs / IO | [`factortail.io`](api.md#io-contracts-factortailio), `results/SCHEMA.md` |
| Appendix G manifest | [`factortail.manifest`](api.md#replacement-manifest-factortailmanifest) |

## Architecture in one diagram

```
┌──────────────────────────────────────────────────────────────┐
│  scripts/generate_F*.py / generate_T*.py  (one per artifact) │
├──────────────────────────────────────────────────────────────┤
│  factortail.cli  +  factortail.experiments.dispatch          │
├───────────────┬────────────────┬─────────────────────────────┤
│ factortail.   │ factortail.    │ factortail.                 │
│  cdmc.*       │  hrv.*         │  diagnostics.*              │
│  (§3-5)       │  (§6)          │  (§3 / §6 / §9)              │
├───────────────┼────────────────┼─────────────────────────────┤
│ factortail.   │ factortail.    │ factortail.                 │
│  dgp.*        │  copula.*      │  estimators.*               │
├──────────────────────────────────────────────────────────────┤
│ factortail.real_data.* (Fama-French loader, rolling VaR/ES)  │
├──────────────────────────────────────────────────────────────┤
│ factortail.io.* (schema, writers, validators)                │
│ factortail.manifest.* (replacement contract)                 │
│ factortail.plotting.* (unified theme + panel helpers)        │
│ factortail.utils.* (tails, regular variation, seeds, …)      │
└──────────────────────────────────────────────────────────────┘
```

Each layer depends only on the layers below it. The `scripts/` layer
owns CLI plumbing, YAML loading, and the provenance stamp, then delegates
to the library.

## Why a `src/` layout

The `src/` layout prevents the local checkout from shadowing the
installed package on `PYTHONPATH`. The CI matrix would otherwise pass
`tests/` against the checkout but ship a broken wheel.

## Why separate `scripts/` from the library

The library is a stable API; the scripts are the experiment plan. A
manuscript revision should touch `scripts/` and a YAML, never the
library, in the common case. The manifest in
`factortail.manifest.replacement` ties the two together.

## Replacement contract in one paragraph

A placeholder figure or table in the LaTeX source may be replaced by a
generated artifact only when (1) the source CSV exists and passes schema
validation, (2) the generation run records `run_id`, `config_hash`,
`git_hash`, and `seed` in `results/_run_<id>.json`, (3) the generated PDF
has the same basename as the placeholder, and (4) the caption and label
remain unchanged unless the underlying diagnostic changes. The CLI command
`factortail validate-run <id>` enforces all four conditions.
