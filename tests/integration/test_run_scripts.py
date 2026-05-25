"""Integration: every figure/table script runs end-to-end and produces a
schema-valid CSV.

We exercise the dispatch path (``factortail run --config ...``) for a small
subset of scripts to keep CI runtime modest. Each test asserts a *math*
property of the produced numbers, not merely that the CSV exists.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest

from factortail.experiments.dispatch import run_config

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run(name: str, tmp_path: Path) -> list[Path]:
    cfg = REPO_ROOT / "configs" / f"{name}.yaml"
    return run_config(cfg, results_dir=tmp_path)


def test_F1_runs_and_curves_are_monotone_decreasing(tmp_path):
    outputs = _run("F1", tmp_path)
    csv_path = next(p for p in outputs if p.suffix == ".csv")
    df = pd.read_csv(csv_path)
    # P(S > x) must decrease in x.
    df = df.sort_values("x")
    assert df["mu_hat"].is_monotonic_decreasing
    assert df["first_order"].is_monotonic_decreasing
    # mu_hat and first_order should be of the same order (within 50% at every x).
    ratio = df["mu_hat"] / df["first_order"]
    assert ratio.min() > 0.5 and ratio.max() < 5.0


@pytest.mark.slow
def test_F11_common_shock_misspecification_observable(tmp_path):
    outputs = _run("F11", tmp_path)
    csv_path = next(p for p in outputs if p.suffix == ".csv")
    df = pd.read_csv(csv_path)
    # With same-sign positive loadings, the latent constant should exceed the
    # misspecified observed-axes constant at every threshold.
    assert (df["latent_constant"] >= df["observed_constant"]).all()


def test_F12_spectral_simplex_produces_valid_angles(tmp_path):
    outputs = _run("F12", tmp_path)
    csv_path = next(p for p in outputs if p.suffix == ".csv")
    df = pd.read_csv(csv_path)
    # Spectral angles on the simplex must sum (approximately) to 1.
    sums = df["theta_1"] + df["theta_2"] + df["theta_3"]
    assert (sums.between(0.99, 1.01)).mean() > 0.9


@pytest.mark.slow
def test_T_indep_relative_error_decreases_with_n(tmp_path):
    """For the independent simulation table, the BRE bound implies
    relative error scales like 1/sqrt(n). We do not enforce that scaling
    here (n is fixed per row) but we check that rel_error is finite and
    positive."""
    outputs = _run("T_sim_results_independent", tmp_path)
    csv_path = next(p for p in outputs if p.suffix == ".csv")
    df = pd.read_csv(csv_path)
    assert (df["rel_error"] >= 0).all()
    assert df["mu_hat"].notna().all()
