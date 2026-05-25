# Reproducibility

Every generated artifact carries enough metadata to be re-executed in
isolation. The contract is enforced by
`factortail.io.writers.write_csv`,
`factortail.manifest.record_run`, and `factortail validate-run`.

## Provenance metadata stamped on every CSV

| Column | Source | Why |
|---|---|---|
| `run_id` | free-text identifier (defaults to YAML stem) | links the row to a run record |
| `config_hash` | SHA-256 of the YAML config (`factortail.utils.hashing.config_hash`) | identifies the exact parameters |
| `git_hash` | `git rev-parse --short HEAD` | identifies the code version |
| `code_version` | `factortail.__version__` | redundant with `git_hash` but human-readable |
| `run_timestamp` | ISO-8601 UTC, second resolution | wall-clock anchor |
| `data_vintage` (real-data only) | source download timestamp / vintage string | identifies the data snapshot |
| `seed` / `spawned_seed` | PCG-spawned per-replicate seed | per-replicate determinism |

## Seeds

`factortail.utils.seeds.SeedSpawner` wraps `numpy.random.SeedSequence`:
given a master seed it deterministically spawns an independent
per-replicate seed. Any single replicate can be re-executed in
isolation — the hard requirement of remark `rem:sim-reproducibility`
in the manuscript.

```python
from factortail.utils.seeds import SeedSpawner

sp = SeedSpawner(master_seed=20260524)
rng = sp.rng(replicate=7)
spawned_seed_for_replicate_7 = sp.spawned_seed(7)  # 32-bit int for CSV
```

## Run records

```python
from factortail.manifest import record_run, validate_run

record_run(
    run_id="P1_2026-05-25",
    priority="P1",
    config_hash="...",
    git_hash="abcd123",
    seed=20260524,
    csvs=["F1_tail_equivalence.csv",
          "F8_second_order.csv",
          "T_sim_results_independent.csv"],
)
validate_run("P1_2026-05-25")
```

`validate_run` raises `factortail.manifest.ReplacementError` if any
required field is missing or any CSV fails schema validation. The CLI
equivalent is

```bash
factortail validate-run P1_2026-05-25
```

## Replacement contract (App. G)

A placeholder figure or table in the LaTeX source may be replaced by a
generated artifact only when:

1. The source CSV exists and passes schema validation
   (`factortail.io.validators.validate_csv`).
2. The run record records `run_id`, `config_hash`, `git_hash`, and
   `seed` in `results/_run_<id>.json`.
3. The generated PDF has the same basename as the placeholder.
4. The caption and label remain unchanged unless the underlying
   diagnostic changes.

Conditions 1-3 are enforced by `factortail validate-run`; condition 4
is enforced by the manuscript merge process.

## Allowed metadata columns

`factortail.io.validators.ALLOWED_METADATA` lists the columns the
validator silently accepts on top of the schema columns:

```
run_id, config_hash, git_hash, code_version, run_timestamp,
data_vintage, seed, spawned_seed, model_name,
sample_start, sample_end
```

The schema-required columns (per `results/SCHEMA.md`) plus
`ALLOWED_METADATA` is the complete column allow-list for every output.

## What does *not* get committed

- Raw CRSP files (licensed; see
  [`docs/report/appendices/F_data_specs.tex`](https://github.com/osolari/FactorTail/blob/main/docs/report/appendices/F_data_specs.tex)).
- Untracked local working files (covered by the existing
  `.gitignore`).
- Build outputs (`site/`, `dist/`, `build/`, `*.egg-info/`).
