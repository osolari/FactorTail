"""Lightweight wall-clock timing helpers for runtime reporting."""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

__all__ = ["StopWatch", "runtime_seconds"]


@dataclass
class StopWatch:
    """Minimal monotonic stopwatch with a final ``elapsed`` attribute."""

    label: str = ""
    elapsed: float = field(default=0.0, init=False)
    _t0: float = field(default=0.0, init=False)

    def __enter__(self) -> StopWatch:
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *exc) -> None:
        self.elapsed = time.perf_counter() - self._t0


@contextmanager
def runtime_seconds() -> Iterator[list[float]]:
    """Context manager that yields a single-element list with elapsed seconds."""
    holder: list[float] = [0.0]
    t0 = time.perf_counter()
    try:
        yield holder
    finally:
        holder[0] = time.perf_counter() - t0
