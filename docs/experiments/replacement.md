# Replacement rules

Appendix G of the manuscript specifies four conditions for a generated
artifact to replace a placeholder figure or table:

1. **CSV exists and passes schema validation.**
   `factortail.io.validators.validate_csv` enforces the column set defined
   in `factortail.io.schema`.
2. **Run record records `run_id`, `config_hash`, `git_hash`, `seed`.**
   `factortail.manifest.record_run` writes
   `results/_run_<id>.json` with the required fields.
3. **The generated PDF has the same basename as the placeholder.** Each
   `scripts/generate_*.py` writes both `<basename>.csv` and `<basename>.pdf`
   (and `.png`).
4. **Caption and label are unchanged unless the underlying diagnostic
   changes.** Enforced manually during the manuscript merge; the
   `(PLANNED.)` and `(PARTIAL.)` prefixes are dropped only when every
   placeholder cell in the artifact has been replaced.

The CLI command

```bash
factortail validate-run <run_id>
```

enforces conditions 1-3 automatically. The CLI

```bash
factortail replace-figure <label>
```

stages the swap of the placeholder TikZ file for the generated PDF/TeX
(currently dry-run).

## Provenance metadata always allowed

The validator allows the provenance columns
(`run_id`, `config_hash`, `git_hash`, `code_version`, `run_timestamp`) and
the real-data extensions (`data_vintage`, `sample_start`, `sample_end`,
`model_name`, `seed`, `spawned_seed`) on top of the schema columns. See
`factortail.io.validators.ALLOWED_METADATA`.
