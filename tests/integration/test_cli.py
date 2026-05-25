"""Integration tests for the ``factortail`` CLI."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from click.testing import CliRunner

from factortail.cli import main

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_list_experiments():
    runner = CliRunner()
    res = runner.invoke(main, ["list-experiments"])
    assert res.exit_code == 0
    for p in ("P1", "P2", "P7"):
        assert p in res.output


def test_validate_schema_md():
    runner = CliRunner()
    res = runner.invoke(main, ["validate-schema", str(REPO_ROOT / "results/SCHEMA.md")])
    assert res.exit_code == 0
    assert "OK" in res.output


def test_validate_schema_rejects_bad_csv(tmp_path):
    bad = tmp_path / "F1_tail_equivalence.csv"
    bad.write_text("foo,bar\n1,2\n")
    runner = CliRunner()
    res = runner.invoke(main, ["validate-schema", str(bad)])
    assert res.exit_code != 0
    assert "FAIL" in res.output


def test_cli_run_F1(tmp_path):
    runner = CliRunner()
    res = runner.invoke(
        main,
        ["run", "--config", str(REPO_ROOT / "configs/F1.yaml"), "--results-dir", str(tmp_path)],
    )
    assert res.exit_code == 0
    assert (tmp_path / "F1_tail_equivalence.csv").exists()
