r"""VaR/ES backtests.

* Kupiec (1995) unconditional coverage test.
* Christoffersen (1998) conditional coverage / independence test.
* Engle-Manganelli (2004) dynamic-quantile test (regression-based).
* Acerbi-Szekely (2014) ES exceedance-residual test.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

__all__ = ["acerbi_szekely_es", "christoffersen_test", "dq_test", "kupiec_test"]


def kupiec_test(hits: np.ndarray, *, level: float) -> dict[str, float]:
    r"""Kupiec unconditional coverage likelihood-ratio test.

    Null: :math:`E[\mathbf 1_{L_t > VaR_t}] = 1 - \tau`.
    """
    hits = np.asarray(hits, dtype=int)
    n = len(hits)
    x = int(hits.sum())
    p = 1.0 - level
    if x == 0:
        log_lr = -2.0 * (n * np.log(1 - p))
    elif x == n:
        log_lr = -2.0 * (n * np.log(p))
    else:
        ll0 = x * np.log(p) + (n - x) * np.log(1 - p)
        ll1 = x * np.log(x / n) + (n - x) * np.log((n - x) / n)
        log_lr = -2.0 * (ll0 - ll1)
    p_val = 1.0 - stats.chi2.cdf(log_lr, df=1)
    return {
        "statistic": float(log_lr),
        "p_value": float(p_val),
        "observed_hits": x,
        "expected_hits": n * p,
    }


def christoffersen_test(hits: np.ndarray, *, level: float) -> dict[str, float]:
    """Christoffersen conditional coverage test (independence + UC)."""
    hits = np.asarray(hits, dtype=int)
    n = len(hits)
    if n < 2:
        return {"statistic": float("nan"), "p_value": float("nan")}
    n00 = int(((hits[:-1] == 0) & (hits[1:] == 0)).sum())
    n01 = int(((hits[:-1] == 0) & (hits[1:] == 1)).sum())
    n10 = int(((hits[:-1] == 1) & (hits[1:] == 0)).sum())
    n11 = int(((hits[:-1] == 1) & (hits[1:] == 1)).sum())
    pi_01 = n01 / max(n00 + n01, 1)
    pi_11 = n11 / max(n10 + n11, 1)
    pi = (n01 + n11) / max(n - 1, 1)
    if pi <= 0 or pi >= 1:
        return {"statistic": 0.0, "p_value": 1.0}

    def safe_log(x: float) -> float:
        return float(np.log(max(x, 1e-300)))

    ll0 = (n00 + n10) * safe_log(1 - pi) + (n01 + n11) * safe_log(pi)
    ll1 = (
        n00 * safe_log(max(1 - pi_01, 1e-300))
        + n01 * safe_log(max(pi_01, 1e-300))
        + n10 * safe_log(max(1 - pi_11, 1e-300))
        + n11 * safe_log(max(pi_11, 1e-300))
    )
    lr_ind = -2.0 * (ll0 - ll1)
    # Combine with Kupiec for conditional coverage.
    uc = kupiec_test(hits, level=level)
    cc_stat = uc["statistic"] + lr_ind
    cc_p = 1.0 - stats.chi2.cdf(cc_stat, df=2)
    return {
        "statistic": float(cc_stat),
        "p_value": float(cc_p),
        "independence_stat": float(lr_ind),
    }


def dq_test(hits: np.ndarray, *, level: float, lags: int = 4) -> dict[str, float]:
    """Engle-Manganelli dynamic-quantile test."""
    hits = np.asarray(hits, dtype=float)
    n = len(hits)
    if n <= lags + 2:
        return {"statistic": float("nan"), "p_value": float("nan")}
    p = 1.0 - level
    hits_c = hits - p
    X = np.column_stack(
        [np.ones(n - lags)] + [hits_c[lags - i : n - i] for i in range(1, lags + 1)]
    )
    y = hits_c[lags:]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    stat = float(beta @ (X.T @ X) @ beta) / (p * (1 - p))
    df = X.shape[1]
    p_val = 1.0 - stats.chi2.cdf(stat, df=df)
    return {"statistic": stat, "p_value": float(p_val), "df": df}


def acerbi_szekely_es(
    losses: np.ndarray, var: np.ndarray, es: np.ndarray, *, level: float
) -> dict[str, float]:
    """Acerbi-Szekely Z2 ES backtest statistic."""
    losses = np.asarray(losses, dtype=float)
    var = np.asarray(var, dtype=float)
    es = np.asarray(es, dtype=float)
    p = 1.0 - level
    n = len(losses)
    excess = (losses > var).astype(float) * losses / np.where(es != 0, es, 1.0)
    Z2 = float(excess.sum() / (n * p) - 1.0)
    return {"statistic": Z2, "p_value": float("nan")}  # p-values require simulation
