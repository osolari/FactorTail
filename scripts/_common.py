"""Shared helpers for ``scripts/generate_*.py`` entry points.

* :func:`load_config` resolves a YAML config relative to the script's CWD.
* :func:`cli` is a tiny argparse wrapper that every script reuses.
* :func:`stamp_provenance` ensures the produced DataFrame carries the
  manifest-required metadata columns.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from factortail import __version__
from factortail.utils.hashing import config_hash, git_hash

__all__ = ["RunContext", "cli", "load_config", "stamp_provenance"]


@dataclass(frozen=True)
class RunContext:
    config_path: Path
    results_dir: Path
    config: dict[str, Any]

    @property
    def run_id(self) -> str:
        return self.config.get("run_id", self.config_path.stem)

    @property
    def config_hash(self) -> str:
        return config_hash(self.config)


def load_config(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text())


def cli(default_config: str, description: str) -> RunContext:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--config", default=default_config, type=Path)
    parser.add_argument("--results-dir", default=Path("results"), type=Path)
    args = parser.parse_args()
    cfg = load_config(args.config)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    return RunContext(config_path=args.config, results_dir=args.results_dir, config=cfg)


def stamp_provenance(df: pd.DataFrame, *, ctx: RunContext) -> pd.DataFrame:
    df = df.copy()
    df["run_id"] = ctx.run_id
    df["config_hash"] = ctx.config_hash
    df["git_hash"] = git_hash()
    df["code_version"] = __version__
    df["run_timestamp"] = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
    return df
