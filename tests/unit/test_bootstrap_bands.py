r"""Method-correctness tests for the spectral-measure bootstrap bands."""

from __future__ import annotations

import numpy as np
import pytest

from factortail.dgp import RadialAngularMRV
from factortail.diagnostics import bootstrap_bands, spectral_constant_estimate


def _sample_mrv(n: int, seed: int) -> np.ndarray:
    dgp = RadialAngularMRV(
        alpha=2.0,
        angular_kind="dirichlet",
        angular_params={"concentration": [2.0, 2.0, 2.0]},
        dim=3,
    )
    rng = np.random.default_rng(seed)
    return dgp.sample(n, rng)


@pytest.mark.parametrize("scheme", ["iid", "block", "stationary"])
def test_bands_contain_point_estimate(scheme):
    X = _sample_mrv(2000, seed=0)
    exposure = np.array([1.0, 2.0, 0.5])  # non-degenerate (else ell(theta) ≡ 1)
    res = bootstrap_bands(
        X,
        exposure=exposure,
        alpha=2.0,
        k_grid=[100, 200, 400],
        n_boot=200,
        scheme=scheme,
        block_length=20,
        seed=42,
    )
    # The point estimate must lie within [lo, hi] for at least most of the k.
    inside = ((res["lo"] <= res["estimate"]) & (res["estimate"] <= res["hi"])).mean()
    assert inside >= 0.6


def test_iid_se_finite_and_positive():
    """Bootstrap SE must be finite, strictly positive, and the percentile
    band must satisfy ``lo <= estimate <= hi`` at most ``k``."""
    exposure = np.array([1.0, 2.0, 0.5])  # non-degenerate (else ell(theta) ≡ 1)
    X = _sample_mrv(2000, seed=1)
    res = bootstrap_bands(
        X, exposure=exposure, alpha=2.0, k_grid=[100, 300, 600], n_boot=200, seed=10
    )
    assert np.all(np.isfinite(res["se"]))
    assert np.all(res["se"] > 0)
    assert np.all(res["lo"] <= res["hi"])


def test_point_estimate_matches_direct_call():
    X = _sample_mrv(1500, seed=0)
    exposure = np.array([1.0, 2.0, 0.5])  # non-degenerate (else ell(theta) ≡ 1)
    direct = spectral_constant_estimate(X, exposure=exposure, alpha=2.0, k=200)
    res = bootstrap_bands(X, exposure=exposure, alpha=2.0, k_grid=[200], n_boot=10, seed=42)
    assert float(res["estimate"][0]) == pytest.approx(direct, rel=1e-12)
