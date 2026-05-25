"""PCG-style seed spawning for reproducible replicate-level randomness.

The manuscript reproducibility contract (Remark ``sim-reproducibility``)
requires a master seed plus independent per-replicate spawned seeds so any
single replicate can be re-executed in isolation. We rely on
``numpy.random.SeedSequence``, which implements the recommended hierarchical
seeding scheme.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = ["SeedSpawner", "spawn_seeds"]


@dataclass(frozen=True)
class SeedSpawner:
    """Reproducible per-replicate seed generator.

    Parameters
    ----------
    master_seed:
        Master seed (entropy source). Any non-negative integer.

    Examples
    --------
    >>> sp = SeedSpawner(42)
    >>> rng = sp.rng(replicate=7)
    >>> _ = rng.normal()
    """

    master_seed: int

    def seed_sequence(self) -> np.random.SeedSequence:
        return np.random.SeedSequence(self.master_seed)

    def spawn(self, n: int) -> list[np.random.SeedSequence]:
        return list(self.seed_sequence().spawn(n))

    def rng(self, replicate: int) -> np.random.Generator:
        ss = self.seed_sequence().spawn(replicate + 1)[replicate]
        return np.random.default_rng(ss)

    def spawned_seed(self, replicate: int) -> int:
        ss = self.seed_sequence().spawn(replicate + 1)[replicate]
        return int(ss.generate_state(1, dtype=np.uint32)[0])


def spawn_seeds(master_seed: int, n: int) -> list[int]:
    """Return ``n`` deterministic 32-bit seeds derived from ``master_seed``."""
    ss = np.random.SeedSequence(master_seed)
    return [int(child.generate_state(1, dtype=np.uint32)[0]) for child in ss.spawn(n)]
