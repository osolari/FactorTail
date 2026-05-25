"""YAML-driven experiment dispatch.

Each experiment YAML names a generator script (``scripts/generate_*.py``)
and the parameters to pass to it. ``factortail run`` and ``factortail
run-all`` use :mod:`factortail.experiments.dispatch` to map a config file
to one or more script invocations.
"""

from factortail.experiments import dispatch

__all__ = ["dispatch"]
