# Manuscript ↔ code map

`FactorTail` mirrors the manuscript module-for-module. The table below
maps each section, theorem, or algorithm to its implementation.

| Manuscript                            | Module / function                                                            |
|---------------------------------------|------------------------------------------------------------------------------|
| §3 Independent baseline               | [`factortail.cdmc.independent`](../api/cdmc.md)                              |
| `thm:catastrophe-exact`               | `independent_cdmc(...).mu_hat` ≈ `sum_i sf_i(x)` in the deep tail            |
| `thm:sum-equivalence`                 | `factortail.utils.regular_variation.first_order_sum_tail`                    |
| `thm:second-order`                    | `factortail.utils.regular_variation.second_order_sum_tail`                   |
| `prop:ind-cdmc-bre`                   | Envelope diagnostic returned in `CdMCResult.extra["envelope"]`               |
| §4 Dependent CdMC identity            | [`factortail.cdmc.dependent`](../api/cdmc.md)                                |
| `alg:dep-cdmc`                        | `factortail.cdmc.dependent.dependent_cdmc`                                   |
| `ass:conditional-envelope`            | Callers pass the kernel; the BRE bound applies whenever the envelope holds. |
| `thm:latent-shock-tail`               | `factortail.cdmc.latent_shock.latent_shock_cdmc`                             |
| `alg:latent-cdmc`                     | `factortail.cdmc.latent_shock.latent_shock_cdmc`                             |
| `thm:block-reduction`                 | `factortail.cdmc.block.block_cdmc`                                           |
| §5 MRV + spectral CdMC                | [`factortail.cdmc.spectral`](../api/cdmc.md)                                 |
| `alg:spectral-cdmc`                   | `factortail.cdmc.spectral.spectral_cdmc`                                     |
| `thm:mrv-linear-risk`                 | `factortail.diagnostics.spectral.spectral_constant_estimate`                 |
| `prop:radial-cdmc`, `prop:spectral-bre`| Same; the radial survival is the `radial` argument.                          |
| §6 Hidden RV                          | [`factortail.hrv`](../api/hrv.md)                                            |
| `def:hrv`                             | `factortail.hrv.ledford_tawn.ledford_tawn_eta`                               |
| `thm:hidden-second-order`             | `factortail.hrv.mixture_estimator.hrv_mixture_estimator` mixture form        |
| §7 Estimator families / efficiency    | [`factortail.estimators`](../api/estimators.md)                              |
| `prop:vre`                            | `factortail.estimators.control_variate` (oracle + sample-split variants)     |
| `thm:bernstein-ci`                    | `factortail.cdmc.base.bernstein_ci`                                          |
| §8 Simulation families I-VI           | [`factortail.dgp`](../api/dgp.md)                                            |
| §9 Real-data protocol                 | [`factortail.real_data`](../api/real_data.md) + `scripts/generate_F1{5..8}*` |
| `alg:real-data`                       | `factortail.real_data.rolling_var_es.run_rolling_var_es`                     |
| Appendix E pseudo-code                | Every algorithm has a one-to-one Python entry point.                         |
| Appendix F data specs / IO            | [`factortail.io`](../api/io.md), `results/SCHEMA.md`                         |
| Appendix G manifest                   | [`factortail.manifest`](../api/manifest.md)                                  |

## Replacement contract in one paragraph

A placeholder figure or table in the LaTeX source may be replaced by a
generated artifact only when (1) the source CSV exists and passes schema
validation, (2) the generation run records `run_id`, `config_hash`,
`git_hash`, and `seed` in `results/_run_<id>.json`, (3) the generated PDF
has the same basename as the placeholder, and (4) the caption and label
remain unchanged unless the underlying diagnostic changes. The CLI command
`factortail validate-run <id>` enforces all four conditions.
