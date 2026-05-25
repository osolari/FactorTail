r"""Tail and dependence diagnostics (§3, §6, §9).

* Tail-index estimators: Hill, Pickands, POT/GPD.
* Dependence: :math:`\\chi`, :math:`\\bar\\chi`, :math:`\\eta`.
* Spectral measure: empirical angular estimator on the simplex.
"""

from factortail.diagnostics.dependence import (
    chi_diagnostic,
    pairwise_dependence_table,
)
from factortail.diagnostics.spectral import empirical_spectral_measure
from factortail.diagnostics.tail_index import (
    hill_estimator,
    pickands_estimator,
    pot_gpd_estimator,
)

__all__ = [
    "chi_diagnostic",
    "empirical_spectral_measure",
    "hill_estimator",
    "pairwise_dependence_table",
    "pickands_estimator",
    "pot_gpd_estimator",
]
