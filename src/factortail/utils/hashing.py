"""Provenance helpers: config hashing, file checksums, git commit lookup."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

__all__ = ["config_hash", "file_sha256", "git_hash"]


def config_hash(config: dict[str, Any]) -> str:
    """Deterministic SHA-256 of a config dict via canonical JSON.

    The hash is stable across Python versions because the serialization sorts
    keys and uses fixed separators. Values must be JSON-serializable.
    """
    serialized = json.dumps(config, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def file_sha256(path: str | Path, *, chunk_size: int = 1 << 20) -> str:
    """Stream-hash a file with SHA-256."""
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def git_hash(repo_path: str | Path | None = None) -> str:
    """Return the current short git commit, or ``"unknown"`` if unavailable."""
    cwd = str(repo_path) if repo_path else None
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=cwd,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"
    return out.decode("ascii").strip()
