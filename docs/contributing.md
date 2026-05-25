# Contributing

Contributions are welcome. The development workflow is:

```bash
make dev          # installs all extras and pre-commit hooks
make fmt          # auto-format with ruff and black
make lint         # ruff + black --check
make test         # pytest suite (92+ tests of math correctness)
make cov          # pytest with coverage
```

## Tests

Tests must verify **mathematical correctness**, not just data shapes.
Examples of acceptable assertions:

- CdMC estimator mean within 5 standard errors of a closed-form / high-budget
  reference probability.
- Hill estimator within 10 % of the true Pareto alpha at `k = sqrt(n)`.
- :math:`\eta = 1/2` for independent uniforms (Ledford-Tawn limit).
- BRE bound :math:`\mathrm{Var}(Z)/\mu^2 \le N^\alpha - 1` (modulo finite-n
  slack).

A test that only checks `len(df) > 0` or `'mu_hat' in df.columns` is not
sufficient.

## Adding a new figure / table

1. Add a row to `factortail.io.schema._SCHEMAS` with the CSV columns.
2. Add the schema name to `results/SCHEMA.md` (the pre-commit hook
   verifies the two stay in sync).
3. Add `scripts/generate_<basename>.py` that exposes
   ``run(*, config: dict, results_dir: Path) -> list[Path]`` and writes a
   validated CSV plus PDF using `factortail.plotting.save_figure`.
4. Add `configs/<basename>.yaml` referencing the script.
5. Append the YAML to `configs/all.yaml`.
6. If the artifact replaces a manuscript placeholder, append it to the
   appropriate row in `factortail.manifest.replacement._DEFAULT_MANIFEST`.
7. Add a test under `tests/integration/test_run_scripts.py` that asserts
   a *math* property of the produced CSV.

## Pull requests

- PRs should keep the CI green (lint + tests).
- Reference the manuscript label being implemented or extended.
- Update the documentation when changing user-visible behaviour.
