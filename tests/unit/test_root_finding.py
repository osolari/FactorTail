"""Root finding inverts Pareto survival exactly."""

from __future__ import annotations

import numpy as np

from factortail.utils.root_finding import (
    expected_shortfall_from_tail,
    invert_survival,
)
from factortail.utils.tails import ParetoTail


def test_invert_pareto_exact():
    d = ParetoTail(alpha=2.0, scale=1.0)
    # P(X > x) = x^{-2}; invert at target = 0.01 should give x = 10.
    x = invert_survival(d.sf, target=0.01, lower=0.5, upper=100.0)
    assert abs(x - 10.0) < 1e-4


def test_expected_shortfall_pareto_closed_form():
    """For Pareto(alpha, scale=1), ES at level tau equals
    alpha/(alpha-1) * VaR_tau."""
    d = ParetoTail(alpha=3.0, scale=1.0)
    tau = 0.99
    es = expected_shortfall_from_tail(d.sf, var_level=tau)
    var = d.ppf(np.array([tau]))[0]
    expected = (3.0 / (3.0 - 1.0)) * var
    assert abs(es - expected) / expected < 0.02
