# CLI reference

The package installs a single entry point, `factortail`.

```text
$ factortail --help

Commands:
  list-experiments     Print the priority manifest (App. G).
  replace-figure       Replace a placeholder TikZ with a generated artifact.
  run                  Execute one experiment described by a YAML config.
  run-all              Execute every experiment listed in a master YAML config.
  validate-run         Enforce App. G replacement rules for a recorded run.
  validate-schema      Validate every CSV in TARGET against the schema.
```

## `list-experiments`

Prints the seven-row priority manifest from appendix G with each row's
required CSVs and current status.

## `run --config <path>`

Dispatch a single experiment YAML. Each YAML must declare `script:` (the
generator script under `scripts/`) and the parameters that script consumes;
see `configs/F1.yaml` for the canonical example.

## `run-all --config <master.yaml>`

Master YAML has the form

```yaml
experiments:
  - configs/F1.yaml
  - configs/F8.yaml
  - ...
```

## `validate-schema <target>`

Validates each CSV in `target` (file or directory) against the schema in
`factortail.io.schema`. If `target` is a Markdown file, the command instead
asserts that every schema name is mentioned in the Markdown (used as the
pre-commit sync check for `results/SCHEMA.md`).

## `validate-run <run_id>`

Loads `results/_run_<run_id>.json` and enforces the appendix-G replacement
contract:

1. Run record exists and carries `run_id`, `config_hash`, `git_hash`,
   `seed`.
2. Every CSV named in the record exists.
3. Every CSV passes schema validation.

## `replace-figure <label>`

Resolves `<label>` to a basename and dry-runs a swap of the placeholder
TikZ file in `docs/report/figures/` for the matching generated PDF in
`results/`.
