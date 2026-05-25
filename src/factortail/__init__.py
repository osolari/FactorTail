"""FactorTail: conditional Monte Carlo for multivariate heavy tails.

This package is the reference implementation of the manuscript "Conditional
Monte Carlo for Multivariate Heavy Tails: Latent Shocks, Spectral Measures,
Hidden Cones" by O. Shams Solari and F. Pourbabaee.

Module map (manuscript section -> module):

* §3 Independent baseline                 -> ``factortail.cdmc.independent``
* §4 Dependent CdMC and shock bases       -> ``factortail.cdmc.dependent``,
                                             ``factortail.cdmc.latent_shock``,
                                             ``factortail.cdmc.block``
* §5 MRV and spectral CdMC                -> ``factortail.cdmc.spectral``
* §6 Hidden regular variation             -> ``factortail.hrv``
* §7 Estimator families and efficiency    -> ``factortail.estimators``
* §8 Simulation study                     -> ``factortail.dgp`` + ``scripts/``
* §9 Real-data analysis                   -> ``factortail.real_data``
* App. E Algorithms and pseudo-code       -> entry points listed below
* App. F Data specs / IO contracts        -> ``factortail.io``
* App. G Experiment manifest              -> ``factortail.manifest``

Algorithm entry points (App. E):

* ``alg:dep-cdmc``       -> :func:`factortail.cdmc.dependent.dependent_cdmc`
* ``alg:latent-cdmc``    -> :func:`factortail.cdmc.latent_shock.latent_shock_cdmc`
* ``alg:spectral-cdmc``  -> :func:`factortail.cdmc.spectral.spectral_cdmc`
* ``alg:real-data``      -> :func:`factortail.real_data.rolling_var_es.run_rolling_var_es`

Top-level convenience imports are intentionally minimal to keep import time
low; reach into the submodules directly.
"""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["__version__"]
