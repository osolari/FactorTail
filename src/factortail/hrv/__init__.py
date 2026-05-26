r"""Hidden regular variation (§6).

Hidden-cone mixture estimator, Ledford-Tawn :math:`\eta` diagnostic, and
direct cone-mass estimator.
"""

from factortail.hrv.cone_mass import cone_mass_alpha, is_interior
from factortail.hrv.ledford_tawn import ledford_tawn_eta
from factortail.hrv.mixture_estimator import hrv_mixture_estimator

__all__ = [
    "cone_mass_alpha",
    "hrv_mixture_estimator",
    "is_interior",
    "ledford_tawn_eta",
]
