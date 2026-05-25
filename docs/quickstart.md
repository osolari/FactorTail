# Quickstart

## 1. Run a single experiment

```bash
factortail run --config configs/F1.yaml --results-dir results/
```

This:

1. Loads `configs/F1.yaml`.
2. Dispatches to `scripts/generate_F1_tail_equivalence.py`.
3. Writes `results/F1_tail_equivalence.csv` (schema-validated).
4. Writes `results/F1_tail_equivalence.pdf` and `.png` using the unified
   [plotting theme](plotting.md).

The CSV carries the appendix-F provenance metadata (`run_id`,
`config_hash`, `git_hash`, `code_version`, `run_timestamp`).

## 2. Run everything

```bash
make run-all          # factortail run-all --config configs/all.yaml
```

## 3. Drive an estimator from Python

```python
import numpy as np
from factortail.cdmc import independent_cdmc, latent_shock_cdmc, spectral_cdmc
from factortail.dgp import RadialAngularMRV
from factortail.utils.tails import ParetoTail

# Independent baseline (Section 3)
margs = [ParetoTail(alpha=2.0, scale=1.0) for _ in range(3)]
res = independent_cdmc(margs, x=20.0, n=20_000, seed=42)
print(res.to_dict())

# Latent-shock CdMC (alg:latent-cdmc)
B = np.array([[1.0, 0.0], [0.5, 0.5]])
shocks = [ParetoTail(alpha=2.0, scale=1.0)] * 2
lat = latent_shock_cdmc(B=B, exposure=np.ones(2), shocks=shocks,
                       x=15.0, n=5000, seed=0)

# Spectral CdMC (alg:spectral-cdmc)
dgp = RadialAngularMRV(alpha=2.0, angular_kind="dirichlet",
                       angular_params={"concentration": [1.5, 1.5, 1.5]},
                       dim=3)
spec = spectral_cdmc(
    angle_sampler=lambda n, r: dgp.sample_angles(n, r),
    radial=dgp.radial,
    exposure=np.ones(3),
    x=15.0,
    n=5000,
    seed=1,
)
```

## 4. Verify against the schema

```bash
factortail validate-schema results/SCHEMA.md
factortail validate-schema results/
```

## 5. Record a reproducible run

```python
from factortail.manifest import record_run, validate_run

record_run(
    run_id="r-2026-05-24",
    priority="P1",
    config_hash="...",
    git_hash="abcd123",
    seed=20260524,
    csvs=["F1_tail_equivalence.csv", "F8_second_order.csv"],
    results_dir="results/",
)
validate_run("r-2026-05-24", results_dir="results/")
```
