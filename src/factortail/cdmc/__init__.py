r"""Conditional Monte Carlo estimators.

Each estimator implements the :class:`CdMCResult` contract and follows the
algorithms in appendix E of the manuscript.

* :func:`factortail.cdmc.independent.independent_cdmc`  -> §3 baseline.
* :func:`factortail.cdmc.dependent.dependent_cdmc`      -> :math:`\\texttt{alg:dep-cdmc}`.
* :func:`factortail.cdmc.latent_shock.latent_shock_cdmc` -> :math:`\\texttt{alg:latent-cdmc}`.
* :func:`factortail.cdmc.block.block_cdmc`              -> §4 block estimator.
* :func:`factortail.cdmc.spectral.spectral_cdmc`        -> :math:`\\texttt{alg:spectral-cdmc}`.
"""

from factortail.cdmc.base import CdMCResult, bernstein_ci, sample_ci
from factortail.cdmc.block import block_cdmc, fit_block_tail
from factortail.cdmc.copula_kernel import (
    build_copula_kernel,
    build_copula_kernel_batched,
    build_copula_sampler,
)
from factortail.cdmc.dependent import dependent_cdmc
from factortail.cdmc.independent import independent_cdmc
from factortail.cdmc.latent_shock import latent_shock_cdmc
from factortail.cdmc.spectral import spectral_cdmc

__all__ = [
    "CdMCResult",
    "bernstein_ci",
    "block_cdmc",
    "build_copula_kernel",
    "build_copula_kernel_batched",
    "build_copula_sampler",
    "dependent_cdmc",
    "fit_block_tail",
    "independent_cdmc",
    "latent_shock_cdmc",
    "sample_ci",
    "spectral_cdmc",
]
