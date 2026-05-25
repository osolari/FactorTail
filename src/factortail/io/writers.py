"""CSV writers that always validate against the schema before writing."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from factortail import __version__
from factortail.io.schema import get_schema
from factortail.io.validators import validate_dataframe
from factortail.utils.hashing import config_hash, git_hash

__all__ = ["write_csv"]


def write_csv(
    df: pd.DataFrame,
    path: str | Path,
    *,
    schema_name: str | None = None,
    config: dict[str, Any] | None = None,
    run_id: str | None = None,
    strict: bool = True,
) -> Path:
    """Write a validated DataFrame to disk with provenance metadata stamped.

    The function injects the manuscript's mandatory metadata columns
    (run_id, config_hash, git_hash, code_version, run_timestamp) when they
    are missing.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    name = schema_name or p.stem
    schema = get_schema(name)
    df = df.copy()
    needs_meta = {"run_id", "config_hash", "git_hash", "code_version", "run_timestamp"} | set(
        schema.metadata_required
    )
    cfg_hash = config_hash(config) if config is not None else "no-config"
    defaults = {
        "run_id": run_id or "manual",
        "config_hash": cfg_hash,
        "git_hash": git_hash(),
        "code_version": __version__,
        "run_timestamp": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
    }
    for col in needs_meta:
        if col not in df.columns and col in defaults:
            df[col] = defaults[col]
    validate_dataframe(df, schema_name=name, strict=strict)
    df.to_csv(p, index=False)
    return p
