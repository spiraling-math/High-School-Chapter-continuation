"""Minimal linear-expression algebra over exact rationals (oracle reference).

Represents ``a*x + b`` using fractions.Fraction. Intentionally NOT a CAS: only
the operations needed for verified linear-polynomial work are provided
(add / sub / scale / eval / normalize / solve). A higher degree is not
representable, so linearity is guaranteed by construction.

Byte-for-byte counterpart of core/exact-math/linexpr.ts.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple


class LinExpr:
    """a*x + b, with a and b exact rationals."""

    __slots__ = ("a", "b")

    def __init__(self, a: Fraction, b: Fraction) -> None:
        self.a = Fraction(a)
        self.b = Fraction(b)

    @staticmethod
    def coef(a, b) -> "LinExpr":
        return LinExpr(Fraction(a), Fraction(b))

    def add(self, o: "LinExpr") -> "LinExpr":
        return LinExpr(self.a + o.a, self.b + o.b)

    def sub(self, o: "LinExpr") -> "LinExpr":
        return LinExpr(self.a - o.a, self.b - o.b)

    def scale(self, k: Fraction) -> "LinExpr":
        return LinExpr(self.a * k, self.b * k)

    def eval(self, x: Fraction) -> Fraction:
        return self.a * x + self.b

    def is_constant(self) -> bool:
        return self.a == 0


def normalize(lhs: LinExpr, rhs: LinExpr) -> Tuple[Fraction, Fraction]:
    """Reduce ``lhs = rhs`` to ``A*x + B = 0`` and return (A, B)."""
    return (lhs.a - rhs.a, lhs.b - rhs.b)


def solve_linear(lhs: LinExpr, rhs: LinExpr) -> Fraction:
    """Solve for x; require a unique solution (A != 0)."""
    a, b = normalize(lhs, rhs)
    if a == 0:
        raise ValueError("not a unique-solution linear equation (A = 0)")
    return Fraction(-b, a)


def lin(a, b) -> LinExpr:
    return LinExpr.coef(a, b)
