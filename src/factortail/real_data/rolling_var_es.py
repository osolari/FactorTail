r"""Rolling VaR/ES estimation (Algorithm ``alg:real-data``).

The protocol fits a rolling FF factor model on a window of length ``w``,
estimates marginal tails of each signed factor and residual contribution,
selects an estimator via the dependence diagnostic decision tree, and then
solves for the VaR forecast by root-finding on the survival curve.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from factortail.cdmc import independent_cdmc
from factortail.diagnostics.tail_index import hill_estimator
from factortail.utils.root_finding import invert_survival
from factortail.utils.tails import LomaxTail, TailDistribution

__all__ = ["RollingVaRConfig", "run_rolling_var_es"]

EstimatorChoice = Literal["independent", "latent_shock", "spectral", "historical"]


@dataclass
class RollingVaRConfig:
    window: int = 1000
    levels: tuple[float, ...] = (0.99, 0.995, 0.999)
    n_inner: int = 20_000
    seed: int = 20260524
    estimator: EstimatorChoice = "independent"
    # Threshold rule for Hill: top sqrt(window) of positive contributions.
    hill_top_fraction: float = 0.10


def _fit_marginal(x: np.ndarray, *, top_fraction: float) -> TailDistribution:
    """Fit a Lomax tail by Hill+method-of-moments on the positive tail."""
    pos = x[x > 0]
    if pos.size < 50:
        # Fallback: heuristic
        return LomaxTail(alpha=3.0, scale=max(np.std(x), 1e-6))
    k = max(int(top_fraction * pos.size), 20)
    hill = hill_estimator(pos, k=k)
    alpha = max(hill["alpha_hat"], 1.2)
    scale = max(hill["threshold"], 1e-6)
    return LomaxTail(alpha=alpha, scale=scale)


def _forecast_survival(
    marginals: list[TailDistribution],
    *,
    n_inner: int,
    seed: int,
) -> Callable[[float], float]:
    """Return a callable ``x -> P(L > x)`` using independent summed CdMC."""
    rng = np.random.default_rng(seed)

    def survival(x: float) -> float:
        return independent_cdmc(marginals, x=x, n=n_inner, rng=rng).mu_hat

    return survival


def run_rolling_var_es(
    returns: pd.Series,
    factors: pd.DataFrame,
    *,
    portfolio: str,
    config: RollingVaRConfig,
) -> pd.DataFrame:
    r"""Algorithm ``alg:real-data`` over a rolling window.

    Parameters
    ----------
    returns:
        Daily portfolio returns indexed by date.
    factors:
        Daily factor returns (same index as ``returns``).
    portfolio:
        Name used in the output ``portfolio`` column.
    """
    if not returns.index.equals(factors.index):
        common = returns.index.intersection(factors.index)
        returns = returns.loc[common]
        factors = factors.loc[common]
    rows: list[dict] = []
    losses = -returns  # paper convention: loss is negative return
    w = config.window
    n = len(returns)
    if n <= w + 5:
        raise ValueError(f"Need at least {w + 6} observations; got {n}")
    for t in range(w, n):
        window_factors = factors.iloc[t - w : t]
        window_losses = losses.iloc[t - w : t]
        # OLS factor fit on the window
        F = np.column_stack([np.ones(w), window_factors.to_numpy()])
        y = window_losses.to_numpy()
        beta, *_ = np.linalg.lstsq(F, y, rcond=None)
        alpha_intercept = beta[0]
        loadings = beta[1:]
        residuals = y - F @ beta
        # Loss-contribution vector: per-factor + residual
        contrib_signs = loadings  # X_{p,t} = -beta_d * f_{d,t} in the paper, sign handled later
        contributions = np.column_stack(
            [contrib_signs[k] * window_factors.iloc[:, k].to_numpy() for k in range(loadings.size)]
        )
        contributions = np.column_stack([contributions, residuals])
        # Fit marginal heavy-tailed law on positive contributions of each column.
        marginals = [
            _fit_marginal(contributions[:, j], top_fraction=config.hill_top_fraction)
            for j in range(contributions.shape[1])
        ]
        survival = _forecast_survival(
            marginals,
            n_inner=config.n_inner,
            seed=config.seed + t,
        )
        # Realized next-step loss for backtest.
        realized_factors = factors.iloc[t].to_numpy()
        realized_loss = float(alpha_intercept + loadings @ realized_factors)
        for level in config.levels:
            try:
                var = invert_survival(
                    survival,
                    target=1.0 - level,
                    lower=max(window_losses.abs().max() * 0.5, 1e-4),
                    upper=window_losses.abs().max() * 50.0,
                )
            except RuntimeError:
                var = float("nan")
            # ES via numerical tail integration.
            try:
                from factortail.utils.root_finding import expected_shortfall_from_tail

                es = expected_shortfall_from_tail(survival, var_level=level)
            except RuntimeError:
                es = float("nan")
            hit = int(realized_loss > var) if np.isfinite(var) else 0
            rows.append(
                dict(
                    date=returns.index[t],
                    portfolio=portfolio,
                    model="FF",
                    level=level,
                    loss=realized_loss,
                    var=var,
                    es=es,
                    hit=hit,
                    crisis_flag=0,
                )
            )
    return pd.DataFrame(rows)
