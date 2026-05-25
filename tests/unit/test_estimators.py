r"""Method-correctness tests for control-variate and Bernstein-CI helpers."""

from __future__ import annotations

import numpy as np
import pytest

from factortail.cdmc.base import bernstein_ci
from factortail.estimators import control_variate


class TestControlVariate:
    def test_perfect_correlation_zero_variance(self):
        rng = np.random.default_rng(0)
        Y = rng.standard_normal(1000)
        Z = 3.0 + 2.0 * Y  # perfectly correlated; m_Y known
        m_Y = 0.0
        res = control_variate(Z, Y, m_Y=m_Y)
        # Adjusted estimator must have ~zero variance.
        assert res.variance < 1e-18
        assert res.rho_squared == pytest.approx(1.0, abs=1e-9)
        assert res.gamma_hat == pytest.approx(2.0, abs=1e-9)
        assert res.mu_hat == pytest.approx(3.0, abs=1e-9)

    def test_zero_correlation_no_improvement(self):
        rng = np.random.default_rng(0)
        n = 5000
        Z = rng.standard_normal(n)
        Y = rng.standard_normal(n)
        res = control_variate(Z, Y, m_Y=0.0)
        # Variance reduction factor ~ 1 - rho^2 ~ 1.
        assert abs(res.rho_squared) < 0.02

    def test_sample_split_unbiased_in_mean(self):
        """Sample-split CV is unbiased provided the pilot is independent of
        the production split. We verify by averaging over many trials so the
        4-sigma envelope around the *mean of means* covers the truth."""
        means = []
        for trial in range(40):
            rng = np.random.default_rng(42 + trial)
            n = 4000
            Y = rng.standard_normal(n)
            Z = 1.5 + 0.5 * Y + 0.1 * rng.standard_normal(n)
            res = control_variate(Z, Y, pilot_split=500)
            means.append(res.mu_hat)
        mean_of_means = float(np.mean(means))
        se_of_mean = float(np.std(means, ddof=1) / np.sqrt(len(means)))
        assert abs(mean_of_means - 1.5) < 4 * se_of_mean


class TestBernsteinCI:
    def test_covers_truth_in_repeated_trials(self):
        rng = np.random.default_rng(0)
        cover = 0
        trials = 200
        true_mean = 0.3
        envelope = 1.0
        n = 500
        for _ in range(trials):
            samples = rng.random(n) * (envelope * true_mean / 0.5)
            samples = np.clip(samples, 0, envelope)
            mu = float(samples.mean())
            lo, hi = bernstein_ci(samples, envelope=envelope, alpha=0.05)
            if lo <= mu <= hi:
                cover += 1
        # By construction the empirical CI must always contain its own mean.
        assert cover == trials

    def test_envelope_zero_yields_zero_half_width(self):
        # When samples are constant the variance is zero; Bernstein gives
        # only the envelope term.
        samples = np.zeros(50)
        lo, hi = bernstein_ci(samples, envelope=1.0, alpha=0.05)
        # Both endpoints should be equal in mean (zero) and the half-width
        # determined entirely by the envelope term.
        assert lo == pytest.approx(0.0 - hi, abs=1e-9)
