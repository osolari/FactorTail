r"""Latent-shock CdMC (``alg:latent-cdmc``).

Apply independent summed CdMC in shock space. Given a factor matrix
:math:`B \in \mathbb R^{N \times K}`, exposure :math:`a \in \mathbb R^N`,
and independent heavy-tailed shocks :math:`Z_k`, define
:math:`q = B^\top a`, so :math:`L = a^\top X = q^\top Z + a^\top E`. The
estimator runs the independent CdMC on the signed shock contributions
``q_k Z_k`` and adds the idiosyncratic axis terms.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from factortail.cdmc.base import CdMCResult, bernstein_ci
from factortail.cdmc.independent import _T_values, envelope
from factortail.utils.tails import TailDistribution
from factortail.utils.timing import runtime_seconds

__all__ = ["latent_shock_cdmc"]


def latent_shock_cdmc(
    *,
    B: NDArray[np.float64],
    exposure: NDArray[np.float64],
    shocks: list[TailDistribution],
    idiosyncratic: list[TailDistribution] | None = None,
    x: float,
    n: int,
    rng: np.random.Generator | None = None,
    seed: int | None = None,
) -> CdMCResult:
    r"""Algorithm ``alg:latent-cdmc``.

    The shock contributions ``Y_k = q_k Z_k`` (with :math:`q_k > 0`) form an
    independent collection whose sum tail we approximate by independent
    summed CdMC. Idiosyncratic ``a_i E_i`` contributions are added as
    additional independent terms.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    B = np.asarray(B, dtype=float)
    exposure = np.asarray(exposure, dtype=float)
    q = B.T @ exposure
    K = len(shocks)
    # Construct effective marginals for active shocks (q_k > 0). For q_k < 0,
    # the shock contributes to the left tail; we drop it for the right tail.
    effective_margs: list[TailDistribution] = []
    effective_signs: list[float] = []
    for k in range(K):
        if abs(q[k]) < 1e-15:
            continue
        # Y_k = q_k Z_k -> right tail iff q_k > 0.
        scale_factor = abs(q[k])
        from factortail.utils.tails import (
            BurrTail,
            LomaxTail,
            ParetoTail,
            StudentTTail,
        )

        sh = shocks[k]
        scaled: TailDistribution
        if isinstance(sh, ParetoTail):
            scaled = ParetoTail(alpha=sh.alpha, scale=sh.scale * scale_factor)
        elif isinstance(sh, LomaxTail):
            scaled = LomaxTail(alpha=sh.alpha, scale=sh.scale * scale_factor)
        elif isinstance(sh, BurrTail):
            scaled = BurrTail(k=sh.k, d=sh.d, scale=sh.scale * scale_factor)
        elif isinstance(sh, StudentTTail):
            scaled = StudentTTail(alpha=sh.alpha, scale=sh.scale * scale_factor)
        else:
            raise TypeError(f"Unsupported shock type for latent CdMC: {type(sh)}")
        effective_margs.append(scaled)
        effective_signs.append(np.sign(q[k]))
    if idiosyncratic is not None:
        for i, eps in enumerate(idiosyncratic):
            scale_factor = abs(exposure[i])
            if scale_factor < 1e-15:
                continue
            from factortail.utils.tails import (
                BurrTail,
                LomaxTail,
                ParetoTail,
                StudentTTail,
            )

            scaled_eps: TailDistribution
            if isinstance(eps, ParetoTail):
                scaled_eps = ParetoTail(alpha=eps.alpha, scale=eps.scale * scale_factor)
            elif isinstance(eps, LomaxTail):
                scaled_eps = LomaxTail(alpha=eps.alpha, scale=eps.scale * scale_factor)
            elif isinstance(eps, BurrTail):
                scaled_eps = BurrTail(k=eps.k, d=eps.d, scale=eps.scale * scale_factor)
            elif isinstance(eps, StudentTTail):
                scaled_eps = StudentTTail(alpha=eps.alpha, scale=eps.scale * scale_factor)
            else:
                raise TypeError(f"Unsupported idiosyncratic type: {type(eps)}")
            effective_margs.append(scaled_eps)
            effective_signs.append(np.sign(exposure[i]))
    signs = np.array(effective_signs, dtype=float)
    # Now run independent CdMC on the effective margins, but only positive-sign
    # contributions count toward the right tail.
    Ntot = len(effective_margs)
    if Ntot == 0:
        return CdMCResult(
            mu_hat=0.0,
            variance=0.0,
            n=n,
            runtime_seconds=0.0,
            ci_low=0.0,
            ci_high=0.0,
            extra={"estimator": "latent_shock_cdmc", "active_shocks": 0},
        )
    Y = np.column_stack([m.rvs(n, rng) for m in effective_margs]) * signs[None, :]
    with runtime_seconds() as elapsed:
        T = _T_values(Y, x)
        kernel = np.column_stack([m.sf(T[:, i]) for i, m in enumerate(effective_margs)])
        kernel = kernel * (signs[None, :] > 0)
        Z = kernel.sum(axis=1)
        mu_hat = float(Z.mean())
        var = float(Z.var(ddof=1)) if n > 1 else float("nan")
    B_env = envelope(effective_margs, x)
    lo, hi = bernstein_ci(Z, envelope=B_env, alpha=0.05)
    return CdMCResult(
        mu_hat=mu_hat,
        variance=var,
        n=n,
        runtime_seconds=float(elapsed[0]),
        ci_low=lo,
        ci_high=hi,
        extra={
            "estimator": "latent_shock_cdmc",
            "active_shocks": int((signs > 0).sum()),
            "envelope": B_env,
            "q": q.tolist(),
        },
    )
