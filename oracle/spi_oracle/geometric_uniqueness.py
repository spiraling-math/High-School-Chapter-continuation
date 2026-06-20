"""Independent uniqueness validators for geometric reverse tasks (oracle).

Mirror of domains/sequences/geometric-uniqueness.ts. Computes complete real
solution sets so the validator can confirm a generated item has exactly the
response the prompt and canonical answer claim.
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Optional


def real_ratio_solution_count(q: Fraction, m: int) -> int:
    """Number of real r with r^m = q (m = k-1 >= 1)."""
    if m % 2 == 1:
        return 1
    if q < 0:
        return 0
    if q == 0:
        return 1
    return 2


def _iroot(x: int, m: int) -> Optional[int]:
    if x == 0:
        return 0
    r = round(x ** (1.0 / m))
    for c in (r - 1, r, r + 1):
        if c >= 0 and c ** m == x:
            return c
    return None


def rational_root(q: Fraction, m: int) -> Optional[Fraction]:
    if q == 0:
        return Fraction(0)
    sign = 1 if q > 0 else -1
    ra = _iroot(abs(q.numerator), m)
    rb = _iroot(q.denominator, m)
    if ra is None or rb is None:
        return None
    if m % 2 == 0 and sign < 0:
        return None
    return Fraction((sign if m % 2 == 1 else 1) * ra, rb)


def real_ratio_solutions(u1: int, value: Fraction, k: int) -> List[Fraction]:
    m = k - 1
    q = Fraction(value, u1)
    principal = rational_root(q, m)
    if principal is None:
        return []
    if m % 2 == 1:
        return [principal]
    if principal == 0:
        return [Fraction(0)]
    return [principal, -principal]


def term_index_solutions(u1: int, r: Fraction, value: Fraction, max_n: int = 40) -> List[int]:
    out: List[int] = []
    t = Fraction(u1)
    for n in range(1, max_n + 1):
        if t == value:
            out.append(n)
        t *= r
    return out
