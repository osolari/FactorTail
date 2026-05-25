# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-05-24

### Added

- Initial public release covering manuscript sections 3–9 and appendices E–G.
- `factortail.cdmc` package with five estimator entry points:
  `independent_cdmc`, `dependent_cdmc`, `latent_shock_cdmc`,
  `block_cdmc`, `spectral_cdmc`.
- `factortail.dgp` package with six DGP families (independent inid,
  common-shock, block, copula, MRV, hidden RV).
- `factortail.copula` with Gaussian, Student-t, Clayton, Gumbel, Frank.
- `factortail.hrv` with Ledford-Tawn :math:`\eta` and the axis/hidden
  mixture estimator.
- `factortail.diagnostics` with Hill / Pickands / POT-GPD and pairwise
  :math:`\chi` / :math:`\bar\chi` / :math:`\eta`.
- `factortail.estimators.control_variate` (oracle + sample-split VRE).
- `factortail.real_data` rolling VaR/ES pipeline and four standard
  backtests (Kupiec, Christoffersen, dynamic quantile,
  Acerbi-Szekely Z2).
- `factortail.io` schema + writers + validators.
- `factortail.manifest` replacement-contract enforcer.
- Unified `factortail.plotting` theme and panel helpers.
- 20 scripts under `scripts/generate_*.py`, one per manuscript figure
  or table.
- 92+ tests of mathematical correctness across `tests/unit` and
  `tests/integration`.
- GitHub Actions CI (lint, type, test matrix over Python 3.10–3.12 ×
  Linux/macOS) and MkDocs gh-pages deploy workflow.
