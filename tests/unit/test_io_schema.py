"""Tests for schema definitions and validators."""

from __future__ import annotations

import pandas as pd
import pytest

from factortail.io.schema import SCHEMA, all_schema_names, get_schema
from factortail.io.validators import ValidationError, validate_dataframe
from factortail.io.writers import write_csv


def test_every_schema_has_unique_columns():
    for name, schema in SCHEMA.items():
        assert len(set(schema.columns)) == len(schema.columns), name


def test_get_schema_strips_csv_suffix():
    s = get_schema("F1_tail_equivalence.csv")
    assert s.name == "F1_tail_equivalence"


def test_validate_rejects_missing_column():
    df = pd.DataFrame({"seed": [1], "design": ["x"], "x": [1.0]})
    with pytest.raises(ValidationError):
        validate_dataframe(df, schema_name="F1_tail_equivalence")


def test_write_csv_adds_provenance(tmp_path):
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
    out = write_csv(df, tmp_path / "F1_tail_equivalence.csv", config={"foo": "bar"})
    written = pd.read_csv(out)
    assert "config_hash" in written.columns
    assert written.loc[0, "config_hash"] != "no-config"


def test_all_schema_names_listed():
    names = list(all_schema_names())
    assert "F1_tail_equivalence" in names
    assert "T_data_panels" in names
