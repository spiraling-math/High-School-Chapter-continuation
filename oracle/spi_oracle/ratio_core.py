"""gen.proportion.ratio — exact Ratio model, proportional reasoning, the anchored ratio parser /
canonicalizer / formatter / equivalence checker, the single result-code vocabulary, and the answer
encoders (owner E, F, G + math model 6).

EXACTNESS (owner): every value is an integer or an exact Fraction. There is NO floating point, NO
tolerance, and NO irrational anywhere. A ratio is an ORDERED tuple of POSITIVE integers; the canonical
(simplest) form divides every part by their gcd and PRESERVES order (2:3 != 3:2; 2:3 == 4:6).

CANONICAL-FIRST RATIO ANSWER (owner B): the simplest-form ordered integer tuple {parts} IS
answer.canonical; answer.display ('2:3') is derived; the tuple is never stored twice and a formatted
string is never the canonical value.

domains/proportion/ratio-core.ts mirrors this byte-for-byte.
"""

from __future__ import annotations

import re
from fractions import Fraction
from math import gcd
from typing import Any, Dict, List, Optional, Tuple


# --------------------------------------------------------------------------- #
# The ONE ratio result-code vocabulary (owner F). Lower-kebab; no UPPER_SNAKE / slash forms.
# --------------------------------------------------------------------------- #
RATIO_RESULT_CODES: Tuple[str, ...] = (
    "correct",
    "equivalent-not-simplified",
    "wrong-order",
    "wrong-ratio",
    "wrong-number-of-parts",
    "zero-or-negative-part",
    "unsupported-term",
    "unparsed-trailing-text",
    "malformed-response",
)
# The best-buy / choice vocabulary (owner F).
CHOICE_RESULT_CODES: Tuple[str, ...] = ("correct", "wrong-choice", "malformed-response")


# --------------------------------------------------------------------------- #
# Exact ratio model + proportional reasoning (owner 6)
# --------------------------------------------------------------------------- #
def gcd_list(parts: List[int]) -> int:
    g = 0
    for p in parts:
        g = gcd(g, abs(p))
    return g or 1


def simplify_parts(parts: List[int]) -> List[int]:
    """Divide every part by the gcd, preserving order (owner 6). parts must be positive integers."""
    g = gcd_list(parts)
    return [p // g for p in parts]


def is_simplest(parts: List[int]) -> bool:
    return gcd_list(parts) == 1


def ratios_equal(a: List[int], b: List[int]) -> bool:
    """Order-sensitive equivalence: a ~ b iff same length and simplest forms are identical (owner 6).
    For two parts this is the cross-multiplication test a0*b1 == a1*b0."""
    return len(a) == len(b) and simplify_parts(a) == simplify_parts(b)


def cross_multiply_equal(a0: int, a1: int, b0: int, b1: int) -> bool:
    """a0:a1 == b0:b1 iff a0*b1 == a1*b0 (owner 6)."""
    return a0 * b1 == a1 * b0


def total_parts(parts: List[int]) -> int:
    return sum(parts)


def share(total: int, parts: List[int]) -> Optional[List[int]]:
    """Exact integer sharing by the total-parts method: requires total divisible by sum(parts)."""
    s = sum(parts)
    if s == 0 or total % s != 0:
        return None
    one = total // s
    return [one * p for p in parts]


def missing_part(known_value: int, known_index: int, missing_index: int, parts: List[int]) -> Optional[int]:
    """Integer missing-part (owner E): requires parts[known_index] divides known_value."""
    k = parts[known_index]
    if k == 0 or known_value % k != 0:
        return None
    return (known_value // k) * parts[missing_index]


def unit_rate(total: int, quantity: int) -> Fraction:
    """Exact amount per one unit (owner 6)."""
    return Fraction(total, quantity)


def direct_proportion(total: int, quantity: int, target: int) -> Fraction:
    """Unitary method: one unit = total/quantity, result = one_unit * target (owner 6)."""
    return Fraction(total, quantity) * target


def inverse_proportion(q1: int, v1: int, q2: int) -> Optional[int]:
    """Product invariant q1*v1 = q2*v2 (owner 6); integer-only in v1.0.0 (owner E-style redraw on non-integer)."""
    prod = q1 * v1
    if q2 == 0 or prod % q2 != 0:
        return None
    return prod // q2


def scale_value(value: int, factor: Fraction) -> Fraction:
    """Apply an exact scale factor to a value (owner I)."""
    return Fraction(value) * factor


# --------------------------------------------------------------------------- #
# Anchored parser / canonicalizer / formatter (owner G)
# --------------------------------------------------------------------------- #
def format_ratio(parts: List[int]) -> str:
    """ASCII colon display (owner G): '2:3' / '2:3:5'."""
    return ":".join(str(p) for p in parts)


def canonicalize(parts: List[int]) -> List[int]:
    return simplify_parts(parts)


_TERM = r"[^:]+"


def parse_ratio(text: str) -> Tuple[Optional[List[int]], Optional[str]]:
    """Parse a learner ratio into a list of positive integers, or a parse-level result code.

    Accepts ASCII-colon ratios with optional surrounding spaces: '2:3', '2 : 3', '4:6', '2:3:5',
    '4 : 6 : 10'. Rejects (owner G): decimals, zero/negative parts, missing parts, extra trailing text,
    more than three parts, comma-separated, unsupported unicode ratio symbols, and the word form '2 to 3'.
    Returns (parts, None) on a clean parse, otherwise (None, code)."""
    if text is None or not str(text).strip():
        return None, "malformed-response"
    s = str(text).strip()
    # ASCII-anchored parser (owner G): ANY non-ASCII character -> unsupported-term. This rejects the
    # unicode ratio colon U+2236 AND every non-ASCII DIGIT (Arabic-Indic ٢, Persian ۲, Devanagari २,
    # Thai ๒, fullwidth ３, mathematical-bold 𝟚, ...). Python's re \d and int() are Unicode-aware, so
    # without this guard '٢:٣' would silently parse to [2,3] while the ASCII-only TS mirror rejects it —
    # a grading-path parity break. The guard makes BOTH engines return the identical code.
    if not s.isascii():
        return None, "unsupported-term"
    # unsupported word form -> unsupported-term (named, not silently parsed)
    if re.search(r"\bto\b", s, re.IGNORECASE):
        return None, "unsupported-term"
    if "," in s:
        return None, "unsupported-term"  # comma-separated not supported in v1.0.0
    if ":" not in s:
        return None, "malformed-response"
    raw = s.split(":")
    if len(raw) < 2:
        return None, "malformed-response"
    if len(raw) > 3:
        return None, "wrong-number-of-parts"
    parts: List[int] = []
    for tok in raw:
        t = tok.strip()
        if t == "":
            return None, "malformed-response"           # missing part (e.g. '2::3' or '2:')
        if re.fullmatch(r"-?\d+\.\d+", t):
            return None, "unsupported-term"              # decimal term
        m = re.fullmatch(r"(-?\d+)", t)
        if m is None:
            # trailing junk after a number, e.g. '2x' or '3 cats'
            if re.match(r"-?\d+\S", t) or re.match(r"-?\d+\s+\S", t):
                return None, "unparsed-trailing-text"
            return None, "malformed-response"
        # Exactness/parity cap (owner exactness): bound a term to <= 12 digits so every parsed value
        # is < 10^12 < 2^53. The TS mirror parses with parseInt (a JS double); without this cap a huge
        # term would round in TS but stay exact in Python, diverging the parsed value and the verdict.
        if len(m.group(1).lstrip("-")) > 12:
            return None, "unsupported-term"
        v = int(m.group(1))
        if v <= 0:
            return None, "zero-or-negative-part"
        parts.append(v)
    return parts, None


# --------------------------------------------------------------------------- #
# Equivalence checker (owner F) — order-sensitive; simplest-form policy per task.
# --------------------------------------------------------------------------- #
def check_ratio(expected_parts: List[int], student_text: str, require_simplest: bool = True) -> Dict[str, Any]:
    """Return {code, partial}. `expected_parts` is the canonical (simplest, ordered) answer.
    require_simplest=True (the default for SIMPLIFY-style tasks) flags an equivalent-but-unsimplified
    answer as equivalent-not-simplified with partial=True; require_simplest=False accepts any equivalent."""
    parts, code = parse_ratio(student_text)
    if code is not None:
        return {"code": code, "partial": False}
    exp = simplify_parts(expected_parts)
    if len(parts) != len(exp):
        return {"code": "wrong-number-of-parts", "partial": False}
    s_simp = simplify_parts(parts)
    if s_simp == exp:
        if parts == exp:
            return {"code": "correct", "partial": False}
        # equivalent but not in simplest form
        if require_simplest:
            return {"code": "equivalent-not-simplified", "partial": True}
        return {"code": "correct", "partial": False}
    if sorted(s_simp) == sorted(exp):       # same multiset, different order -> wrong order
        return {"code": "wrong-order", "partial": False}
    return {"code": "wrong-ratio", "partial": False}


def check_choice(expected_id: str, student_text: str) -> str:
    """Best-buy / choice checking (owner F/H): the answer is the selected labelled option id."""
    if student_text is None or not str(student_text).strip():
        return "malformed-response"
    sel = str(student_text).strip().upper()
    if not re.fullmatch(r"[A-Z]", sel):
        return "malformed-response"
    return "correct" if sel == expected_id.upper() else "wrong-choice"


# --------------------------------------------------------------------------- #
# Answer encoders (owner B, D) — canonical-first; display derived.
# --------------------------------------------------------------------------- #
def ratio_answer(parts: List[int]) -> Dict[str, Any]:
    canon = simplify_parts(parts)
    return {"type": "ratio", "canonical": {"parts": canon}, "display": format_ratio(canon)}


def rational_answer(value: Fraction) -> Dict[str, Any]:
    """Integer-when-whole (answer.type 'integer', den 1) else 'exact-rational' (owner D)."""
    t = "integer" if value.denominator == 1 else "exact-rational"
    disp = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    return {"type": t, "canonical": {"num": value.numerator, "den": value.denominator}, "display": disp}


def integer_answer(n: int) -> Dict[str, Any]:
    return {"type": "integer", "canonical": {"num": int(n), "den": 1}, "display": str(int(n))}


def table_answer(cells: List[Tuple[str, int]]) -> Dict[str, Any]:
    """Label-keyed table completion (owner C): correspondence by location label, not row order."""
    enc = [{"location": loc, "value": int(val)} for loc, val in cells]
    disp = ", ".join(f"{loc}={val}" for loc, val in cells)
    return {"type": "table-completion", "canonical": {"cells": enc}, "display": disp}


def mc_answer(option_id: str) -> Dict[str, Any]:
    """Best-buy multiple-choice (owner D/H): canonical IS the selected labelled option id."""
    return {"type": "multiple-choice", "canonical": option_id, "display": option_id}
