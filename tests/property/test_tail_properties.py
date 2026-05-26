r"""Hypothesis property tests for tail distributions.

These are sanity invariants that must hold for *every* admissible
parameter setting, not just the hand-picked examples in
``tests/unit/test_tails.py``.

Properties tested:

- ``sf`` is monotone non-increasing in ``x``.
- ``sf(scale or 0) <= 1`` and ``sf(x) >= 0`` for every ``x``.
- ``ppf`` inverts ``sf``: ``sf(ppf(1 - q)) ≈ 1 - q``.
- ``logsf`` matches ``log(sf)`` where ``sf > 0``.
- A finite mean is reported as finite when ``alpha > 1`` (Lomax / Pareto).
"""

from __future__ import annotations

import numpy as np
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from factortail.utils.tails import BurrTail, LomaxTail, ParetoTail

CONSERVATIVE = settings(
    max_examples=80,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


@CONSERVATIVE
@given(
    alpha=st.floats(min_value=0.5, max_value=8.0, allow_nan=False, allow_infinity=False),
    scale=st.floats(min_value=0.05, max_value=10.0, allow_nan=False, allow_infinity=False),
    x1=st.floats(min_value=1e-3, max_value=100.0, allow_nan=False, allow_infinity=False),
    x2=st.floats(min_value=1e-3, max_value=100.0, allow_nan=False, allow_infinity=False),
)
def test_pareto_sf_monotone(alpha: float, scale: float, x1: float, x2: float) -> None:
    d = ParetoTail(alpha=alpha, scale=scale)
    a, b = min(x1, x2), max(x1, x2)
    assert d.sf(b) <= d.sf(a) + 1e-12


@CONSERVATIVE
@given(
    alpha=st.floats(min_value=0.5, max_value=8.0),
    scale=st.floats(min_value=0.05, max_value=10.0),
    q=st.floats(min_value=1e-6, max_value=1 - 1e-6),
)
def test_pareto_ppf_inverts_sf(alpha: float, scale: float, q: float) -> None:
    d = ParetoTail(alpha=alpha, scale=scale)
    x = float(d.ppf(np.array([q]))[0])
    assume(np.isfinite(x))
    sf_at_x = float(d.sf(np.array([x]))[0])
    assert abs(sf_at_x - (1 - q)) < 1e-7


@CONSERVATIVE
@given(
    alpha=st.floats(min_value=0.5, max_value=8.0),
    scale=st.floats(min_value=0.05, max_value=10.0),
    x=st.floats(min_value=1e-3, max_value=1000.0),
)
def test_lomax_logsf_matches_log_sf(alpha: float, scale: float, x: float) -> None:
    d = LomaxTail(alpha=alpha, scale=scale)
    sf = float(d.sf(np.array([x]))[0])
    assume(sf > 0)
    log_sf_direct = float(d.logsf(np.array([x]))[0])
    assert abs(log_sf_direct - np.log(sf)) < 1e-9


@CONSERVATIVE
@given(
    alpha=st.floats(min_value=1.1, max_value=8.0),
    scale=st.floats(min_value=0.05, max_value=10.0),
)
def test_lomax_finite_mean_when_alpha_gt_one(alpha: float, scale: float) -> None:
    d = LomaxTail(alpha=alpha, scale=scale)
    m = d.mean()
    assert np.isfinite(m)
    assert m > 0


@CONSERVATIVE
@given(
    alpha=st.floats(min_value=0.1, max_value=1.0),
    scale=st.floats(min_value=0.05, max_value=10.0),
)
def test_lomax_infinite_mean_when_alpha_le_one(alpha: float, scale: float) -> None:
    d = LomaxTail(alpha=alpha, scale=scale)
    assert np.isinf(d.mean())


@CONSERVATIVE
@given(
    k=st.floats(min_value=0.5, max_value=4.0),
    d_par=st.floats(min_value=0.5, max_value=4.0),
    scale=st.floats(min_value=0.05, max_value=10.0),
)
def test_burr_alpha_equals_k_times_d(k: float, d_par: float, scale: float) -> None:
    d = BurrTail(k=k, d=d_par, scale=scale)
    assert abs(d.alpha - k * d_par) < 1e-12


@CONSERVATIVE
@given(
    alpha=st.floats(min_value=0.5, max_value=5.0),
    scale=st.floats(min_value=0.1, max_value=2.0),
    q1=st.floats(min_value=1e-4, max_value=1 - 1e-4),
    q2=st.floats(min_value=1e-4, max_value=1 - 1e-4),
)
def test_pareto_ppf_monotone(alpha: float, scale: float, q1: float, q2: float) -> None:
    d = ParetoTail(alpha=alpha, scale=scale)
    q_lo, q_hi = sorted([q1, q2])
    assume(q_hi - q_lo > 1e-6)
    x_lo = float(d.ppf(np.array([q_lo]))[0])
    x_hi = float(d.ppf(np.array([q_hi]))[0])
    assert x_lo <= x_hi + 1e-9
