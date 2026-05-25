"""Schema validators enforced before any CSV may replace a placeholder."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from factortail.io.schema import get_schema

__all__ = ["ALLOWED_METADATA", "ValidationError", "validate_csv", "validate_dataframe"]


# Provenance metadata columns are *always* allowed on top of the schema-required
# columns. They are stamped by :func:`factortail.io.writers.write_csv` and the
# reproducibility contract requires them on every output.
ALLOWED_METADATA: frozenset[str] = frozenset(
    {
        "run_id",
        "config_hash",
        "git_hash",
        "code_version",
        "run_timestamp",
        "data_vintage",
        "seed",
        "spawned_seed",
        "model_name",
        "sample_start",
        "sample_end",
    }
)


class ValidationError(ValueError):
    """Raised when a CSV/DataFrame fails schema validation."""


def validate_dataframe(
    df: pd.DataFrame,
    *,
    schema_name: str,
    strict: bool = True,
) -> None:
    """Validate ``df`` against the named schema.

    Parameters
    ----------
    strict:
        If True, also require that no unexpected columns are present
        (excluding the always-allowed provenance metadata in
        :data:`ALLOWED_METADATA`).
    """
    schema = get_schema(schema_name)
    df_cols = set(df.columns)
    required = schema.all_columns()
    missing = required - df_cols
    if missing:
        raise ValidationError(f"Schema {schema_name!r}: missing columns {sorted(missing)}")
    if strict:
        extra = df_cols - required - ALLOWED_METADATA
        if extra and not all(c.startswith("_") for c in extra):
            raise ValidationError(f"Schema {schema_name!r}: unexpected columns {sorted(extra)}")
    if df.isnull().all(axis=0).any():
        all_null = df.columns[df.isnull().all(axis=0)].tolist()
        raise ValidationError(f"Schema {schema_name!r}: entirely-null columns {all_null}")


def validate_csv(path: str | Path, *, schema_name: str | None = None, strict: bool = True) -> None:
    """Validate a CSV file against the schema with name inferred from filename."""
    p = Path(path)
    name = schema_name or p.stem
    df = pd.read_csv(p)
    validate_dataframe(df, schema_name=name, strict=strict)
