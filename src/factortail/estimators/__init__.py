"""High-level estimator constructions used in §7.

* :func:`control_variate` — oracle and sample-split control-variate
  estimator (Proposition ``prop:vre``).
* Bernstein CI lives in :mod:`factortail.cdmc.base` and is re-exported here.
"""

from factortail.cdmc.base import bernstein_ci, sample_ci
from factortail.estimators.control_variate import ControlVariateResult, control_variate
from factortail.estimators.spectral_cv import spectral_control_variate

__all__ = [
    "ControlVariateResult",
    "bernstein_ci",
    "control_variate",
    "sample_ci",
    "spectral_control_variate",
]
