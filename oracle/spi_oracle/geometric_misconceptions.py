"""Canonical geometric-sequence misconception registry (oracle).

Single source of truth for distractor values (exact Fraction) and their rationale
and feedback for the geometric generator's multiple-choice tasks (nth_term,
sum_n). The TypeScript registry mirrors this file exactly. `observableError` is
serialized into items as the distractor `rationale`, so it must match the TS
registry byte-for-byte.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable, Dict


def _abs(r: Fraction) -> Fraction:
    return Fraction(abs(r.numerator), r.denominator)


MISCONCEPTIONS: Dict[str, Dict[str, Any]] = {
    # ---- nth-term misconceptions --------------------------------------------
    "MISC.GEO.OFFBYONE_EXPONENT": {
        "formula": (lambda u1, r, n: u1 * r ** n),
        "expression": "u_1 * r^n",
        "title": "Off-by-one in the exponent",
        "description": "Uses r^n instead of r^(n-1).",
        "observableError": "Answer is one extra factor of the common ratio.",
        "feedback": "The nth term uses r raised to the power (n - 1), not n.",
    },
    "MISC.GEO.RATIO_AS_DIFFERENCE": {
        "formula": (lambda u1, r, n: u1 + (n - 1) * r),
        "expression": "u_1 + (n-1)*r",
        "title": "Treats the ratio like a common difference",
        "description": "Adds (n-1) lots of r instead of multiplying by r^(n-1).",
        "observableError": "Answer adds the ratio repeatedly instead of multiplying.",
        "feedback": "A geometric sequence multiplies by r each step; it does not add r.",
    },
    "MISC.GEO.FORGOT_FIRST_TERM": {
        "formula": (lambda u1, r, n: r ** (n - 1)),
        "expression": "r^(n-1)",
        "title": "Omitted the first term",
        "description": "Computes r^(n-1) but forgets the factor u_1.",
        "observableError": "Answer is the ratio power without the first term.",
        "feedback": "Multiply r^(n - 1) by the first term u_1.",
    },
    "MISC.GEO.SIGN_RATIO": {
        "formula": (lambda u1, r, n: u1 * _abs(r) ** (n - 1)),
        "expression": "u_1 * |r|^(n-1)",
        "title": "Dropped the sign of a negative ratio",
        "description": "Ignores that a negative ratio alternates the sign of the terms.",
        "observableError": "Answer has the wrong sign for a negative common ratio.",
        "feedback": "A negative common ratio makes the terms alternate in sign; keep the sign of r.",
    },
    # ---- sum (series) misconceptions ----------------------------------------
    "MISC.SERIES.GEO.FORGOT_RATIO": {
        "formula": (lambda u1, r, n: Fraction(u1 * n)),
        "expression": "u_1 * n",
        "title": "Treats the sum as n equal terms",
        "description": "Multiplies the first term by n, ignoring the common ratio.",
        "observableError": "Sum equals n times the first term, ignoring r.",
        "feedback": "The terms change by a factor of r; use S_n = u_1 (r^n - 1)/(r - 1).",
    },
    "MISC.SERIES.GEO.SUM_INVERTED_SIGN": {
        "formula": (lambda u1, r, n: u1 * (1 - r ** n) / (r - 1)),
        "expression": "u_1 (1 - r^n)/(r - 1)",
        "title": "Mismatched signs in the sum formula",
        "description": "Uses (1 - r^n) over (r - 1), inverting the sign.",
        "observableError": "Answer has the opposite sign of the correct sum.",
        "feedback": "Keep the numerator and denominator consistent: (r^n - 1)/(r - 1) or (1 - r^n)/(1 - r).",
    },
    "MISC.SERIES.GEO.OFFBYONE_SUM": {
        "formula": (lambda u1, r, n: u1 * (r ** (n + 1) - 1) / (r - 1)),
        "expression": "u_1 (r^(n+1) - 1)/(r - 1)",
        "title": "Off-by-one in the number of terms",
        "description": "Sums n+1 terms instead of n.",
        "observableError": "Answer includes one extra term.",
        "feedback": "Sum exactly n terms: the exponent in the formula is n, not n + 1.",
    },
}

NTH_TERM_RULES = [
    "MISC.GEO.OFFBYONE_EXPONENT",
    "MISC.GEO.RATIO_AS_DIFFERENCE",
    "MISC.GEO.FORGOT_FIRST_TERM",
    "MISC.GEO.SIGN_RATIO",
]
SUM_N_RULES = [
    "MISC.SERIES.GEO.FORGOT_RATIO",
    "MISC.SERIES.GEO.SUM_INVERTED_SIGN",
    "MISC.SERIES.GEO.OFFBYONE_SUM",
]


def rules_for(task: str):
    if task == "nth_term":
        return NTH_TERM_RULES
    if task == "sum_n":
        return SUM_N_RULES
    return []
