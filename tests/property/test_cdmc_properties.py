r"""Hypothesis property tests for CdMC estimators and regular variation."""

from __future__ import annotations

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from factortail.cdmc import independent_cdmc
from factortail.utils.regular_variation import first_order_sum_tail, second_order_sum_tail
from factortail.utils.tails import LomaxTail, ParetoTail

CONSERVATIVE = settings(
    max_examples=40,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.large_base_example],
)


@CONSERVATIVE
@given(
    alpha=st.floats(min_value=1.5, max_value=4.0, allow_nan=False, allow_infinity=False),
    N=st.integers(min_value=2, max_value=5),
    x_factor=st.floats(min_value=10.0, max_value=100.0),
)
def test_independent_cdmc_finite_and_positive(alpha: float, N: int, x_factor: float) -> None:
    margs = [ParetoTail(alpha=alpha, scale=1.0) for _ in range(N)]
    res = independent_cdmc(margs, x=float(x_factor), n=2000, seed=42)
    assert np.isfinite(res.mu_hat)
    assert res.mu_hat > 0
    assert np.isfinite(res.variance)
    assert res.variance >= 0


@CONSERVATIVE
@given(
    alpha=st.floats(min_value=1.5, max_value=4.0, allow_nan=False, allow_infinity=False),
    N=st.integers(min_value=2, max_value=5),
)
def test_first_order_sum_tail_monotone_decreasing(alpha: float, N: int) -> None:
    margs = [ParetoTail(alpha=alpha, scale=1.0) for _ in range(N)]
    x = np.array([5.0, 10.0, 20.0, 40.0, 80.0])
    fo = first_order_sum_tail(margs, x)
    assert np.all(np.diff(fo) <= 1e-15)
    assert np.all(fo > 0)


@CONSERVATIVE
@given(
    alpha=st.floats(min_value=1.5, max_value=4.0, allow_nan=False, allow_infinity=False),
    N=st.integers(min_value=2, max_value=5),
)
def test_second_order_at_least_first_order_for_lomax(alpha: float, N: int) -> None:
    """For Lomax margins (positive mean), the leave-one-out correction is
    non-negative, so second_order >= first_order pointwise."""
    margs = [LomaxTail(alpha=alpha, scale=1.0) for _ in range(N)]
    x = np.array([5.0, 10.0, 20.0])
    fo = first_order_sum_tail(margs, x)
    so = second_order_sum_tail(margs, x)
    assert np.all(so + 1e-15 >= fo)


@CONSERVATIVE
@given(
    alpha=st.floats(min_value=1.5, max_value=3.5),
    N=st.integers(min_value=2, max_value=4),
)
def test_envelope_dominates_mu_hat(alpha: float, N: int) -> None:
    r"""The deterministic envelope :math:`B(x) = \sum_i sf_i(x/N)` must
    dominate the CdMC point estimate (the envelope bounds every replicate
    of ``Z``, hence the sample mean)."""
    margs = [ParetoTail(alpha=alpha, scale=1.0) for _ in range(N)]
    x = 30.0
    res = independent_cdmc(margs, x=x, n=2000, seed=7)
    envelope = res.extra["envelope"]
    assert res.mu_hat <= envelope + 1e-12
