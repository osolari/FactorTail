r"""Data-generating processes for the simulation study (§8).

Six families, one module each:

* Family I   :mod:`factortail.dgp.family1_independent`
* Family II  :mod:`factortail.dgp.family2_latent_shock`
* Family III :mod:`factortail.dgp.family3_block`
* Family IV  :mod:`factortail.dgp.family4_copula`
* Family V   :mod:`factortail.dgp.family5_mrv`
* Family VI  :mod:`factortail.dgp.family6_hidden_cones`

Each module exposes a ``sample`` function with signature
``sample(size: int, rng: np.random.Generator) -> ndarray`` producing the
underlying loss-contribution vectors :math:`X \in \mathbb R^N` used by every
estimator family in the manuscript.
"""

from factortail.dgp.family1_independent import IndependentINID
from factortail.dgp.family2_latent_shock import CommonShockModel, LatentFactorModel
from factortail.dgp.family3_block import BlockModel
from factortail.dgp.family4_copula import CopulaModel
from factortail.dgp.family5_mrv import RadialAngularMRV
from factortail.dgp.family6_hidden_cones import HiddenConeMixture

__all__ = [
    "IndependentINID",
    "CommonShockModel",
    "LatentFactorModel",
    "BlockModel",
    "CopulaModel",
    "RadialAngularMRV",
    "HiddenConeMixture",
]
