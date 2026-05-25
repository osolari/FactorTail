"""Pre-commit hook: verify SCHEMA.md mentions every Python schema entry.

This script lives in ``scripts/_dev/`` because it is a dev-time tool, not a
figure generator. It is wired up from ``.pre-commit-config.yaml``.
"""

from __future__ import annotations

import sys
from pathlib import Path

from factortail.io.schema import all_schema_names


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    md = repo_root / "results" / "SCHEMA.md"
    if not md.exists():
        print(f"SCHEMA.md not found at {md}", file=sys.stderr)
        return 1
    text = md.read_text()
    missing = [name for name in all_schema_names() if name not in text]
    if missing:
        print("SCHEMA.md missing entries:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 1
    print(f"OK: SCHEMA.md mentions all {len(all_schema_names())} schemas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
