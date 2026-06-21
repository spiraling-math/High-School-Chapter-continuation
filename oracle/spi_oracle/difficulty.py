"""Shared difficulty helpers (oracle).

Mirror of core/difficulty/band.ts. `round3` collapses integral results to int so
Python's json renders them like JS (e.g. 1, not 1.0); `band_from_score` maps a
weighted axis score in [0,1] to an integer band 1..5. Byte-for-byte identical to
the inline versions the approved generators previously used.
"""

from __future__ import annotations

import math


def round3(x: float):
    v = math.floor(x * 1000 + 0.5) / 1000
    return int(v) if v == int(v) else v


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def band_from_score(score: float) -> int:
    return min(5, 1 + int(clamp01(score) * 5))
