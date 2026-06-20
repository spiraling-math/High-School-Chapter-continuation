"""Deterministic, cross-language seeded PRNG (mulberry32).

mulberry32 is a small, fast 32-bit PRNG. Implemented here with explicit 32-bit
unsigned arithmetic so that this Python implementation and the canonical
JavaScript implementation produce byte-identical output for the same seed.

Canonical JavaScript reference (the production TypeScript port must match):

    function mulberry32(a) {
      return function() {
        a |= 0; a = (a + 0x6D2B79F5) | 0;
        var t = Math.imul(a ^ (a >>> 15), 1 | a);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      }
    }

All operations below mask to 32 bits and use logical right shift, matching the
JS unsigned (>>>) semantics. The derived helpers (next_int, choice, shuffle)
are also part of the cross-language contract: the TypeScript port must derive
integers and choices in exactly the same way, or seeds will not reproduce.
"""

from __future__ import annotations

from typing import List, Sequence, TypeVar

_UINT32 = 0xFFFFFFFF
T = TypeVar("T")


def _imul(a: int, b: int) -> int:
    """32-bit integer multiply returning the low 32 bits (like Math.imul)."""
    return (a * b) & _UINT32


class Mulberry32:
    """A seeded mulberry32 generator with deterministic helpers."""

    def __init__(self, seed: int) -> None:
        # Normalise the seed to a 32-bit unsigned integer.
        self._state = seed & _UINT32

    def next_uint32(self) -> int:
        """Return the next raw 32-bit unsigned integer."""
        self._state = (self._state + 0x6D2B79F5) & _UINT32
        a = self._state
        t = _imul(a ^ (a >> 15), 1 | a)
        t = ((t + _imul(t ^ (t >> 7), 61 | t)) & _UINT32) ^ t
        return (t ^ (t >> 14)) & _UINT32

    def next_float(self) -> float:
        """Return the next float in the half-open interval [0, 1)."""
        return self.next_uint32() / 4294967296.0

    def next_int(self, lo: int, hi: int) -> int:
        """Return a deterministic integer in the inclusive range [lo, hi].

        Uses floor(next_float() * span). This is the cross-language contract;
        the TypeScript port must use the identical derivation.
        """
        if hi < lo:
            raise ValueError("next_int requires lo <= hi")
        span = hi - lo + 1
        return lo + int(self.next_float() * span)

    def choice(self, items: Sequence[T]) -> T:
        """Return a deterministic element from a non-empty sequence."""
        if not items:
            raise ValueError("choice requires a non-empty sequence")
        return items[self.next_int(0, len(items) - 1)]

    def shuffle(self, items: Sequence[T]) -> List[T]:
        """Return a new list, Fisher-Yates shuffled deterministically.

        Iterates i from len-1 down to 1, swapping with j in [0, i]. The TS port
        must use the identical loop direction and index derivation.
        """
        result = list(items)
        for i in range(len(result) - 1, 0, -1):
            j = self.next_int(0, i)
            result[i], result[j] = result[j], result[i]
        return result
