"""Exact univariate polynomial over rationals (oracle reference).

Dense coefficient vector, ASCENDING degree, ``fractions.Fraction`` entries, always canonical
(trailing zero coefficients stripped; the zero polynomial is ``[0]``). Intentionally NOT a CAS:
only the operations the functions family needs — add / sub / neg / scale / mul / pow / compose /
eval / degree / equality / JSON encoding / plain-text display. No factoring, no rational functions,
no radicals.

Byte-for-byte counterpart of core/exact-math/polynomial.ts (the display strings are part of the
cross-language contract: ``4x^2 - 12x + 10``, ``(1/2)x + 9``, ``-x + 5``, ``0``).
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, Iterable, List, Sequence


def rat_display(value) -> str:
    """Plain-text rational: ``3``, ``-3``, ``3/4``, ``-3/4`` (sign on the numerator)."""
    f = Fraction(value)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def rat_json(value) -> Dict[str, int]:
    f = Fraction(value)
    return {"num": f.numerator, "den": f.denominator}


def rat_from_json(d: Dict[str, int]) -> Fraction:
    return Fraction(int(d["num"]), int(d["den"]))


class Poly:
    """A polynomial in one variable with exact rational coefficients."""

    __slots__ = ("c",)

    def __init__(self, coeffs: Iterable[Any]) -> None:
        c: List[Fraction] = [Fraction(v) for v in coeffs]
        while len(c) > 1 and c[-1] == 0:
            c.pop()
        if not c:
            c = [Fraction(0)]
        self.c = tuple(c)

    # --- constructors -------------------------------------------------------- #
    @staticmethod
    def const(v) -> "Poly":
        return Poly([v])

    @staticmethod
    def x() -> "Poly":
        return Poly([0, 1])

    @staticmethod
    def linear(a, b) -> "Poly":
        """a*x + b."""
        return Poly([b, a])

    @staticmethod
    def quadratic(a, b, c) -> "Poly":
        """a*x^2 + b*x + c."""
        return Poly([c, b, a])

    @staticmethod
    def from_json(d: Dict[str, Any]) -> "Poly":
        return Poly([rat_from_json(t) for t in d["coefficients"]])

    # --- queries ------------------------------------------------------------- #
    def degree(self) -> int:
        """Degree; the zero polynomial reports 0."""
        return len(self.c) - 1

    def is_zero(self) -> bool:
        return len(self.c) == 1 and self.c[0] == 0

    def is_constant(self) -> bool:
        return len(self.c) == 1

    def coef(self, k: int) -> Fraction:
        return self.c[k] if k < len(self.c) else Fraction(0)

    def equals(self, o: "Poly") -> bool:
        return self.c == o.c

    # --- arithmetic ---------------------------------------------------------- #
    def add(self, o: "Poly") -> "Poly":
        n = max(len(self.c), len(o.c))
        return Poly([self.coef(i) + o.coef(i) for i in range(n)])

    def neg(self) -> "Poly":
        return Poly([-v for v in self.c])

    def sub(self, o: "Poly") -> "Poly":
        return self.add(o.neg())

    def scale(self, k) -> "Poly":
        kf = Fraction(k)
        return Poly([v * kf for v in self.c])

    def mul(self, o: "Poly") -> "Poly":
        out = [Fraction(0)] * (len(self.c) + len(o.c) - 1)
        for i, a in enumerate(self.c):
            for j, b in enumerate(o.c):
                out[i + j] += a * b
        return Poly(out)

    def pow(self, n: int) -> "Poly":
        if n < 0:
            raise ValueError("Poly.pow: exponent must be a non-negative integer")
        r = Poly.const(1)
        for _ in range(n):
            r = r.mul(self)
        return r

    def compose(self, inner: "Poly") -> "Poly":
        """self(inner(x)) by Horner's scheme over polynomials."""
        r = Poly.const(0)
        for coef in reversed(self.c):
            r = r.mul(inner).add(Poly.const(coef))
        return r

    def eval(self, x) -> Fraction:
        """Horner evaluation at an exact rational."""
        xf = Fraction(x)
        r = Fraction(0)
        for coef in reversed(self.c):
            r = r * xf + coef
        return r

    # --- encoding ------------------------------------------------------------ #
    def to_json(self, variable: str = "x") -> Dict[str, Any]:
        return {"variable": variable, "coefficients": [rat_json(v) for v in self.c]}

    def display(self, variable: str = "x") -> str:
        return poly_display(self.c, variable)


def _var_power(variable: str, d: int) -> str:
    return variable if d == 1 else f"{variable}^{d}"


def poly_display(coeffs: Sequence[Fraction], variable: str = "x") -> str:
    """Plain-text display, descending degree, zero terms omitted, +/-1 coefficients implicit on
    variable terms, fractional coefficients bracketed: ``4x^2 - 12x + 10``, ``(1/2)x + 9``,
    ``(-1/2)x + 9``, ``-x + 5``, ``x^2 - 4``, ``0``."""
    terms: List[str] = []
    for d in range(len(coeffs) - 1, -1, -1):
        c = Fraction(coeffs[d])
        if c == 0:
            continue
        leading = not terms
        if d == 0:
            body = rat_display(abs(c)) if not leading else rat_display(c)
        else:
            a = abs(c) if not leading else c
            v = _var_power(variable, d)
            if a == 1:
                body = v
            elif a == -1:
                body = "-" + v
            elif a.denominator == 1:
                body = f"{a.numerator}{v}"
            else:
                body = f"({rat_display(a)}){v}"
        if leading:
            terms.append(body)
        else:
            terms.append((" - " if c < 0 else " + ") + body)
    return "".join(terms) if terms else "0"
