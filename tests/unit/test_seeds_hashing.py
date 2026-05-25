"""Reproducibility tests for seeds and config hashing."""

from __future__ import annotations

from factortail.utils.hashing import config_hash
from factortail.utils.seeds import SeedSpawner, spawn_seeds


class TestSeedSpawner:
    def test_replicate_independence(self):
        sp = SeedSpawner(42)
        rng_a = sp.rng(0)
        rng_b = sp.rng(0)
        # Same replicate index => identical streams.
        assert rng_a.normal() == rng_b.normal()
        rng_c = sp.rng(1)
        # Different replicate index => different streams.
        assert rng_a.normal() != rng_c.normal()

    def test_master_seed_uniqueness(self):
        a = SeedSpawner(1).rng(0).normal()
        b = SeedSpawner(2).rng(0).normal()
        assert a != b


def test_spawn_seeds_deterministic():
    a = spawn_seeds(42, 5)
    b = spawn_seeds(42, 5)
    assert a == b
    c = spawn_seeds(43, 5)
    assert c != a


def test_config_hash_deterministic_and_order_independent():
    a = {"foo": 1, "bar": [2, 3]}
    b = {"bar": [2, 3], "foo": 1}
    assert config_hash(a) == config_hash(b)
    c = {"foo": 1, "bar": [3, 2]}
    assert config_hash(a) != config_hash(c)
