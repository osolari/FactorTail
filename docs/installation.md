# Installation

`FactorTail` is a pure-Python package targeting Python 3.10+. Install in
editable mode for the development workflow:

```bash
pip install -e ".[dev,plot]"
```

For the full set of extras (including docs and the real-data downloader):

```bash
pip install -e ".[dev,plot,docs,realdata]"
```

Then install the pre-commit hooks:

```bash
pre-commit install
```

## Extras

| Extra      | What it pulls in                                     |
|------------|------------------------------------------------------|
| `plot`     | `matplotlib`, `seaborn`                              |
| `dev`      | `pytest`, `pytest-cov`, `pytest-xdist`, `hypothesis`, `ruff`, `black`, `mypy`, `pre-commit` |
| `docs`     | `mkdocs`, `mkdocs-material`, `mkdocstrings[python]`  |
| `realdata` | `pandas-datareader`, `requests` (for live Fama-French pulls) |

## Offline / CI mode

Every script that touches Fama-French data accepts `offline: true` in its
YAML config, in which case `factortail.real_data.fama_french.synthesize_panel`
produces a deterministic heavy-tailed surrogate panel suitable for the test
suite and for CI runs without network access.
