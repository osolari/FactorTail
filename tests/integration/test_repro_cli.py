r"""Integration test: ``factortail repro`` re-runs and verifies CSVs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from factortail.cli import main

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.slow
def test_repro_F1(tmp_path: Path) -> None:
    """End-to-end: run F1, record the run, then `factortail repro` it."""
    runner = CliRunner()
    res = runner.invoke(
        main,
        ["run", "--config", str(REPO_ROOT / "configs/F1.yaml"), "--results-dir", str(tmp_path)],
    )
    assert res.exit_code == 0, res.output
    assert (tmp_path / "F1_tail_equivalence.csv").exists()

    # Hand-write a run record.
    record = {
        "run_id": "test_repro",
        "priority": "P1",
        "config_hash": "test",
        "git_hash": "test",
        "seed": 20260524,
        "csvs": ["F1_tail_equivalence.csv"],
    }
    (tmp_path / "_run_test_repro.json").write_text(json.dumps(record))

    # Repro should regenerate F1 and find it byte-identical (modulo
    # provenance metadata).
    res = runner.invoke(
        main,
        [
            "repro",
            "test_repro",
            "--results-dir",
            str(tmp_path),
            "--configs-dir",
            str(REPO_ROOT / "configs"),
        ],
    )
    assert res.exit_code == 0, res.output
    assert "byte-identical" in res.output
