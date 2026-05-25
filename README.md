# FactorTail

[![CI](https://github.com/osolari/FactorTail/actions/workflows/ci.yml/badge.svg)](https://github.com/osolari/FactorTail/actions/workflows/ci.yml)
[![Docs](https://github.com/osolari/FactorTail/actions/workflows/docs.yml/badge.svg)](https://osolari.github.io/FactorTail/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

Sharp tail asymptotics and efficient rare-event simulation for
**independent and dependent regularly-varying factor models** — the
reference implementation of the manuscript by O. Shams Solari and
F. Pourbabaee.

`FactorTail` mirrors the manuscript section-by-section: every theorem in
§§3–7 has an algorithmic counterpart in `factortail.cdmc.*`, every data
family in §8 has a generator in `factortail.dgp.*`, and every figure or
table in the paper has a one-script entry point under `scripts/`.

---

## Highlights

- **Six estimator families** (independent / dependent kernel / latent-shock
  / block / spectral / hidden-cone mixture) with formal BRE diagnostics and
  Bernstein CIs.
- **Six DGP families** (independent inid, common-shock, block,
  copula, MRV, hidden RV) with closed-form first-order constants and
  signed-exposure support.
- **One script per figure / table** under `scripts/generate_*.py`, each
  producing a schema-validated CSV plus a PDF/PNG rendered with the
  unified plotting theme.
- **Reproducibility contract**: PCG-style replicate seeds, config-hash
  provenance, git-hash stamping, validated CSV schema mirrored in
  `results/SCHEMA.md` and `factortail.io.schema`.
- **Replacement rules**: `factortail validate-run <id>` enforces the
  appendix-G contract before a generated artifact may replace a placeholder
  in the manuscript build.
- **Rolling VaR/ES backtests**: Kupiec, Christoffersen, dynamic quantile
  (Engle-Manganelli), Acerbi-Szekely Z2.
- **Modern tooling**: `src/` layout, PEP 621 `pyproject.toml`, ruff + black
  + mypy + pre-commit, pytest with parametrized math-correctness tests,
  GitHub Actions CI matrix (Python 3.10–3.12 × Linux/macOS), MkDocs site
  deployed to `gh-pages`.

## Install

```bash
# editable install with dev extras
pip install -e ".[dev,plot]"
# or with the full set
pip install -e ".[dev,plot,docs,realdata]"
```

System requirements: Python 3.10 or newer; numpy, scipy, pandas,
matplotlib, click, rich, pyyaml are pulled in automatically.

## Quickstart

```python
import numpy as np
from factortail.cdmc import independent_cdmc
from factortail.utils.tails import ParetoTail

margs = [ParetoTail(alpha=2.0, scale=1.0) for _ in range(3)]
res = independent_cdmc(margs, x=20.0, n=20_000, seed=42)
print(res.mu_hat, res.ci_low, res.ci_high)
```

For a full reproducible run of one experiment:

```bash
factortail run --config configs/F1.yaml --results-dir results/
```

For every figure/table in one go:

```bash
make run-all          # equivalent to factortail run-all --config configs/all.yaml
```

To validate a finished run against the appendix-G replacement contract:

```bash
factortail validate-run <run_id> --results-dir results/
```

## Repository layout

```
FactorTail/
├── src/factortail/                # the importable library (src/ layout)
│   ├── cdmc/                       # §3-§5 estimators
│   │   ├── independent.py          # §3 independent summed CdMC
│   │   ├── dependent.py            # alg:dep-cdmc
│   │   ├── latent_shock.py         # alg:latent-cdmc
│   │   ├── block.py                # block CdMC (thm:block-reduction)
│   │   └── spectral.py             # alg:spectral-cdmc
│   ├── hrv/                        # §6 hidden RV
│   ├── estimators/                 # §7 control variates, Bernstein CI
│   ├── diagnostics/                # tail, dependence, spectral diagnostics
│   ├── dgp/                        # Families I-VI data generators
│   ├── copula/                     # Gaussian / Student / Clayton / Gumbel / Frank
│   ├── real_data/                  # Fama-French loader, rolling VaR/ES, backtests
│   ├── io/                         # schema, writers, validators (appx F)
│   ├── manifest/                   # replacement-rule enforcement (appx G)
│   ├── plotting/                   # unified theme + panel helpers
│   ├── experiments/                # YAML dispatch
│   └── cli.py
├── scripts/                        # one entry point per figure/table
│   ├── generate_F1_tail_equivalence.py    # P1
│   ├── generate_F8_second_order.py        # P1
│   ├── generate_F11_common_shock_geometry.py  # P2
│   ├── generate_F12_spectral_simplex.py   # P4
│   ├── generate_F13_hidden_cones.py       # P5
│   ├── generate_F14_simulation_dashboard.py
│   ├── generate_F15_tail_dependence_heatmap.py   # P6
│   ├── generate_F16_var_es_dashboard.py          # P6
│   ├── generate_F17_spectral_by_period.py        # P6
│   ├── generate_F18_hill_plots.py                # P6
│   └── generate_T_*.py                            # every table
├── configs/                        # one YAML per script + master `all.yaml`
├── results/                        # generated CSVs / PDFs + SCHEMA.md
├── tests/                          # 92+ tests of *math*, not just shapes
│   ├── unit/
│   └── integration/
├── docs/                           # MkDocs site (+ docs/report/ for paper)
├── .github/workflows/              # CI matrix and gh-pages deploy
├── pyproject.toml                  # PEP 621 packaging
├── Makefile                        # `make dev`, `make test`, `make docs`, ...
├── tox.ini
├── mkdocs.yml
├── .pre-commit-config.yaml
└── CITATION.cff
```

## Manuscript ↔ code map

| Section / theorem            | Module                                            |
|------------------------------|---------------------------------------------------|
| §3 independent baseline      | `factortail.cdmc.independent`                     |
| §4 dependent CdMC identity   | `factortail.cdmc.dependent`                       |
| §4 latent-shock              | `factortail.cdmc.latent_shock`                    |
| §4 block reduction           | `factortail.cdmc.block`                           |
| §5 MRV + spectral CdMC       | `factortail.cdmc.spectral` + `diagnostics.spectral` |
| §6 hidden RV                 | `factortail.hrv.mixture_estimator` + `ledford_tawn` |
| §7 control variates + CI     | `factortail.estimators.control_variate` + `cdmc.base.bernstein_ci` |
| §8 simulation study (I-VI)   | `factortail.dgp` + `scripts/generate_F*.py`       |
| §9 real-data protocol        | `factortail.real_data.rolling_var_es`             |
| Appendix E pseudo-code       | `factortail.cdmc.*`                               |
| Appendix F data specs / IO   | `factortail.io.schema` (+ `results/SCHEMA.md`)    |
| Appendix G manifest          | `factortail.manifest.replacement`                 |

## CLI reference

```text
factortail list-experiments        # print App. G manifest
factortail run --config <path>     # execute one experiment YAML
factortail run-all --config all.yaml
factortail validate-schema <path>  # validate CSV(s) or SCHEMA.md
factortail validate-run <run_id>   # enforce App. G replacement rules
factortail replace-figure <label>  # swap placeholder for generated PDF
```

## Reproducibility

Every output CSV is stamped with `run_id`, `config_hash` (SHA-256 of the
YAML), `git_hash`, `code_version`, and `run_timestamp`. Seeds are spawned
with `numpy.random.SeedSequence` so every replicate can be re-executed in
isolation. The replacement contract in appendix G is implemented in
`factortail.manifest` and enforced by the CLI.

CRSP data must never be committed to this repository (see
[`docs/report/appendices/F_data_specs.tex`](docs/report/appendices/F_data_specs.tex)).

## Development

```bash
make dev          # install with all extras and install pre-commit hooks
make lint         # ruff + black --check
make test         # full pytest suite
make cov          # tests with coverage
make docs-serve   # local MkDocs server on :8000
make docs-deploy  # publishes to gh-pages branch
```

## Citing

Please cite both the library and the manuscript; see
[`CITATION.cff`](CITATION.cff).

## License

MIT (see [`LICENSE`](LICENSE)).
