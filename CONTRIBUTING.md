# Contributing to FactorTail

See [docs/contributing.md](docs/contributing.md) for the full guide.

## Quick start for contributors

```bash
make dev          # install with all extras + install pre-commit hooks
make fmt          # auto-format
make lint         # ruff + black --check
make test         # 92+ tests of mathematical correctness
make cov          # tests with coverage
make docs-serve   # local mkdocs server on :8000
```

## Test policy

Tests must verify mathematical correctness — for example: estimator
unbiasedness against closed-form or high-budget references, Hill
consistency, BRE bounds, Ledford-Tawn :math:`\eta = 1/2` for independent
uniforms. A test that only checks shape, dtype, or column names is not
sufficient.
