"""Tests for the App. G replacement contract."""

from __future__ import annotations

import pandas as pd
import pytest

from factortail.io.writers import write_csv
from factortail.manifest import (
    ReplacementError,
    load_manifest,
    record_run,
    validate_run,
)


def test_load_manifest_default_has_seven_rows():
    rows = load_manifest()
    priorities = {r.priority for r in rows}
    assert priorities == {"P1", "P2", "P3", "P4", "P5", "P6", "P7"}


def test_validate_run_rejects_missing_csv(tmp_path):
    record_run(
        run_id="r1",
        priority="P1",
        config_hash="cfg",
        git_hash="gh",
        seed=1,
        csvs=["F1_tail_equivalence.csv"],
        results_dir=tmp_path,
    )
    with pytest.raises(ReplacementError):
        validate_run("r1", results_dir=tmp_path)


def test_validate_run_passes_when_csv_valid(tmp_path):
    df = pd.DataFrame(
        {
            "seed": [1],
            "design": ["d"],
            "x": [1.0],
            "n": [10],
            "mu_hat": [0.1],
            "ci_low": [0.0],
            "ci_high": [0.2],
            "first_order": [0.1],
            "second_order": [0.1],
            "runtime_seconds": [0.01],
        }
    )
    write_csv(df, tmp_path / "F1_tail_equivalence.csv", config={"x": 1})
    record_run(
        run_id="r2",
        priority="P1",
        config_hash="cfg",
        git_hash="gh",
        seed=1,
        csvs=["F1_tail_equivalence.csv"],
        results_dir=tmp_path,
    )
    validate_run("r2", results_dir=tmp_path)  # should not raise
