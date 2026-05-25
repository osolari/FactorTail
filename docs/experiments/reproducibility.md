# Reproducibility contract

Every output CSV is stamped with:

- `run_id` — a free-text identifier (defaults to the YAML stem).
- `config_hash` — SHA-256 of the YAML config, with sorted keys and stable
  separators (`factortail.utils.hashing.config_hash`).
- `git_hash` — short `git rev-parse --short HEAD`, or `"unknown"` if not
  in a git checkout.
- `code_version` — `factortail.__version__`.
- `run_timestamp` — ISO-8601 UTC, second resolution.

Real-data outputs also carry `data_vintage` (the source download
timestamp) and the source-file SHA-256 (`T_data_panels.checksum`).

## Seeds

`factortail.utils.seeds.SeedSpawner` wraps `numpy.random.SeedSequence`:
given a master seed it spawns a deterministic, independent per-replicate
seed. Any single replicate can be re-executed in isolation, which is the
hard requirement of remark `rem:sim-reproducibility` in the manuscript.

```python
from factortail.utils.seeds import SeedSpawner

sp = SeedSpawner(master_seed=20260524)
rng = sp.rng(replicate=7)
spawned_seed_for_replicate_7 = sp.spawned_seed(7)  # 32-bit int for CSV column
```

## Validating a run

After producing the CSVs, record the run and then validate:

```python
from factortail.manifest import record_run, validate_run

record_run(
    run_id="r-2026-05-24",
    priority="P1",
    config_hash="...",
    git_hash="...",
    seed=20260524,
    csvs=["F1_tail_equivalence.csv", "F8_second_order.csv"],
)
validate_run("r-2026-05-24")
```

`validate_run` raises `ReplacementError` if any required field is missing
or any CSV fails schema validation. The CLI form is

```bash
factortail validate-run r-2026-05-24
```
