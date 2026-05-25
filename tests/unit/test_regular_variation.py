"""Tests for closed-form regular-variation tools."""

from __future__ import annotations

import numpy as np

from factortail.utils.regular_variation import (
    first_order_sum_tail,
    second_order_sum_tail,
)
from factortail.utils.tails import LomaxTail, ParetoTail


def test_first_order_pareto_is_sum_of_sf():
    margs = [ParetoTail(alpha=2.0, scale=1.0), ParetoTail(alpha=2.0, scale=1.5)]
    x = np.array([5.0, 10.0])
    expected = margs[0].sf(x) + margs[1].sf(x)
    assert np.allclose(first_order_sum_tail(margs, x), expected, rtol=1e-12)


def test_second_order_reduces_to_first_for_n_equals_one():
    margs = [ParetoTail(alpha=2.0, scale=1.0)]
    x = np.array([5.0, 10.0, 20.0])
    fo = first_order_sum_tail(margs, x)
    so = second_order_sum_tail(margs, x)
    # For N=1, mu_{-1} = 0 so the correction is zero.
    assert np.allclose(fo, so, rtol=1e-12)


def test_second_order_changes_sign_with_finite_mean():
    margs = [LomaxTail(alpha=3.0, scale=1.0)] * 3
    x = np.array([4.0, 8.0, 15.0])
    fo = first_order_sum_tail(margs, x)
    so = second_order_sum_tail(margs, x)
    # All margins have positive mean; the leave-one-out correction should
    # increase the tail estimate at moderate x.
    assert np.all(so >= fo - 1e-12)
