"""gen.measurement.mensuration v1.0.0 — the dimensional-quantity answer contract (owner B, D).

The architecture-proving core of the family: a STRUCTURED unit model plus a deterministic,
anchored parser / formatter / equivalence checker. Unit meaning is treated STRUCTURALLY (compare
dimension + baseUnit + exponent objects), never as an unchecked text suffix.

Quantity model (owner B):
    dimension : "length" | "area"
    baseUnit  : "mm" | "cm" | "m"
    exponent  : 1 (length) | 2 (area)        # locked to the dimension in v1.0.0
    value     : an exact fractions.Fraction  (integer or reduced rational; always positive here)

No cross-unit conversion happens in v1.0.0 (owner D): each item uses ONE declared base unit
throughout, so 100 cm is NOT accepted when 1 m is required — the checker reports wrong-base-unit
and the feedback names the required unit; it never silently converts. cm<->m conversion is a later
objective + contract extension.

The checker partitions a parsed response against the expected quantity on the (baseUnit, exponent)
grid, so all four structural reject codes are genuinely reachable and deterministic:
    base ok, exp ok   -> correct | incorrect-value
    base ok, exp wrong-> wrong-exponent     (cm vs cm^2: linear-vs-square on the SAME base unit)
    base wrong,exp ok -> wrong-base-unit     (cm vs m: the no-conversion case)
    base wrong,exp wr -> wrong-dimension     (a completely different dimensional quantity)
plus missing-unit (a bare number) and malformed-response (unreadable / trailing text / sci-notation).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, Optional, Tuple

BASE_UNITS = ("mm", "cm", "m")
DIMENSIONS = ("length", "area")

RESULT_CODES = (
    "correct",
    "incorrect-value",
    "missing-unit",
    "wrong-base-unit",
    "wrong-dimension",
    "wrong-exponent",
    "malformed-response",
)


@dataclass(frozen=True)
class Quantity:
    """An exact dimensional quantity. `value` is a Fraction; `dimension`/`exponent` are locked."""

    dimension: str
    baseUnit: str
    exponent: int
    value: Fraction

    def __post_init__(self) -> None:
        assert self.dimension in DIMENSIONS, self.dimension
        assert self.baseUnit in BASE_UNITS, self.baseUnit
        assert self.exponent in (1, 2), self.exponent
        assert (self.exponent == 1) == (self.dimension == "length"), "dimension/exponent must agree"
        assert isinstance(self.value, Fraction), type(self.value)


def make_length(value, baseUnit: str) -> Quantity:
    return Quantity("length", baseUnit, 1, Fraction(value))


def make_area(value, baseUnit: str) -> Quantity:
    return Quantity("area", baseUnit, 2, Fraction(value))


# --------------------------------------------------------------------------- #
# Formatter (Quantity -> canonical display). Stored/fixture output uses ASCII "^2".
# --------------------------------------------------------------------------- #
def format_value(value: Fraction) -> str:
    """Exact value as an integer string or a reduced 'num/den' string (never a float)."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def unit_token(baseUnit: str, exponent: int) -> str:
    """ASCII canonical unit token, e.g. 'cm' or 'cm^2'."""
    return baseUnit if exponent == 1 else f"{baseUnit}^2"


def format_quantity(q: Quantity) -> str:
    """Canonical display form, e.g. '15/2 cm' or '24 cm^2'."""
    return f"{format_value(q.value)} {unit_token(q.baseUnit, q.exponent)}"


def format_quantity_display(q: Quantity) -> str:
    """Screen-presentation variant: a typographic superscript ² instead of ASCII ^2.
    NEVER used for canonical storage / fixtures (those stay ASCII)."""
    return f"{format_value(q.value)} {q.baseUnit}" + ("²" if q.exponent == 2 else "")


def encode_quantity_answer(q: Quantity) -> Dict[str, object]:
    """Encode a Quantity as a question-item.schema.json answer.type='quantity' object (owner B).
    canonical is a normalized rational {num,den>=1}; measure is the structured unit; display is
    derived (ASCII) and NOT duplicated inside measure."""
    return {
        "type": "quantity",
        "canonical": {"num": q.value.numerator, "den": q.value.denominator},
        "measure": {"dimension": q.dimension, "baseUnit": q.baseUnit, "exponent": q.exponent},
        "display": format_quantity(q),
    }


# --------------------------------------------------------------------------- #
# Unit alias table (owner D). Canonical stored output is always the abbreviation form;
# the parser additionally accepts common English names + '^2'/'2'/'²' superscripts.
# Keys are normalized: lower-cased, internal whitespace collapsed to single spaces.
# --------------------------------------------------------------------------- #
def _build_alias_table() -> Dict[str, Tuple[str, int]]:
    table: Dict[str, Tuple[str, int]] = {}
    names = {
        "mm": ["mm", "millimetre", "millimetres", "millimeter", "millimeters"],
        "cm": ["cm", "centimetre", "centimetres", "centimeter", "centimeters"],
        "m": ["m", "metre", "metres", "meter", "meters"],
    }
    for base, forms in names.items():
        for f in forms:
            table[f] = (base, 1)  # length
            # area variants for this name form
            if f in (base,):  # abbreviation: cm^2 / cm2 / cm² (² already mapped to ^2 upstream)
                table[f"{f}^2"] = (base, 2)
                table[f"{f}2"] = (base, 2)
            table[f"{f} squared"] = (base, 2)
            table[f"square {f}"] = (base, 2)
            table[f"sq {f}"] = (base, 2)
    return table


_ALIAS = _build_alias_table()

# Anchored number: a fraction a/b, OR an exact terminating decimal a.b, OR an integer.
# Order matters (fraction, then decimal, then integer); scientific notation is NOT matched here,
# so it falls through to the trailing-text reject.
_NUM_RE = re.compile(r"^([+-]?\d+\s*/\s*\d+|[+-]?\d+\.\d+|[+-]?\d+)")


def _normalize(s: str) -> str:
    """Normalize Unicode minus + superscript-two; trim outer whitespace."""
    return (
        s.replace("−", "-")  # Unicode MINUS SIGN -> ASCII hyphen-minus
        .replace("²", "^2")  # SUPERSCRIPT TWO -> ASCII ^2
        .strip()
    )


def _parse_number(num: str) -> Optional[Fraction]:
    num = num.replace(" ", "")
    try:
        if "/" in num:
            n, d = num.split("/", 1)
            if d == "0" or d.lstrip("+-") == "0":
                return None
            return Fraction(int(n), int(d))
        if "." in num:
            whole, frac = num.split(".", 1)
            if not frac.isdigit():
                return None
            sign = -1 if whole.lstrip("+-") != whole and whole.startswith("-") else 1
            whole_digits = whole.lstrip("+-")
            value = Fraction(int(whole_digits or "0") * (10 ** len(frac)) + int(frac), 10 ** len(frac))
            return sign * value
        return Fraction(int(num), 1)
    except (ValueError, ZeroDivisionError):
        return None


def parse_quantity(text: str) -> Tuple[Optional[Quantity], Optional[str]]:
    """Anchored, deterministic parse of a student response.

    Returns (Quantity, None) on success, or (None, code) where code is 'missing-unit' (a number
    with no unit) or 'malformed-response' (no leading number, scientific notation, trailing
    unparsed text, an unrecognised unit, or multiple/garbled unit tokens).
    """
    if text is None:
        return None, "malformed-response"
    norm = _normalize(text)
    if norm == "":
        return None, "malformed-response"
    m = _NUM_RE.match(norm)
    if not m:
        return None, "malformed-response"  # no leading number (e.g. a bare unit)
    value = _parse_number(m.group(0))
    if value is None:
        return None, "malformed-response"
    rest = norm[m.end():].strip()
    if rest == "":
        return None, "missing-unit"
    unit_key = re.sub(r"\s+", " ", rest.lower()).strip()
    if unit_key not in _ALIAS:
        return None, "malformed-response"  # trailing text, sci-notation tail, or unknown unit
    base, exponent = _ALIAS[unit_key]
    dimension = "length" if exponent == 1 else "area"
    return Quantity(dimension, base, exponent, value), None


# --------------------------------------------------------------------------- #
# Equivalence checker (the contract). Structural, deterministic, no conversion.
# --------------------------------------------------------------------------- #
def _base_phrase(base: str) -> str:
    return {"mm": "millimetres (mm)", "cm": "centimetres (cm)", "m": "metres (m)"}[base]


def _expected_phrase(q: Quantity) -> str:
    if q.dimension == "length":
        return f"a length in {_base_phrase(q.baseUnit)}"
    return f"an area in square {q.baseUnit} ({unit_token(q.baseUnit, 2)})"


def check_response(text: str, expected: Quantity) -> Dict[str, object]:
    """Check a free-response string against the expected dimensional quantity.

    Accepts any mathematically-equivalent numerical form (e.g. '30/2' for 15) WITH the correct
    unit. Returns {code, correct, feedback, parsed?} where code is one of RESULT_CODES. Treats
    unit meaning structurally; never converts between base units."""
    parsed, code = parse_quantity(text)

    if code == "missing-unit":
        return _result("missing-unit", expected,
                       f"You gave a number but no unit. This answer needs {_expected_phrase(expected)}.")
    if code == "malformed-response":
        return _result("malformed-response", expected,
                       "I could not read your answer. Write a number and a unit, for example 12 cm or 24 cm^2.")

    assert parsed is not None
    base_match = parsed.baseUnit == expected.baseUnit
    exp_match = parsed.exponent == expected.exponent

    if base_match and exp_match:
        if parsed.value == expected.value:
            return _result("correct", expected, "Correct.", parsed)
        return _result("incorrect-value", expected,
                       f"The unit is right, but the number is not. Re-check your working — the answer is {format_quantity(expected)}.",
                       parsed)

    if base_match and not exp_match:
        # Right base unit, wrong power: the linear-vs-square confusion (distinguish length/area).
        if expected.exponent == 2:
            msg = (f"An area is measured in SQUARE units ({unit_token(expected.baseUnit, 2)}); "
                   f"you used linear units ({unit_token(parsed.baseUnit, 1)}).")
        else:
            msg = (f"A length is measured in LINEAR units ({unit_token(expected.baseUnit, 1)}); "
                   f"you used square units ({unit_token(parsed.baseUnit, 2)}).")
        return _result("wrong-exponent", expected, msg, parsed)

    if not base_match and exp_match:
        # Right power, wrong base unit: never convert — name the required unit (owner D).
        return _result("wrong-base-unit", expected,
                       f"This answer must be given in {_base_phrase(expected.baseUnit)}, using the unit shown on the figure — do not convert from {_base_phrase(parsed.baseUnit)}.",
                       parsed)

    # Different base AND power: a completely different kind of measurement.
    return _result("wrong-dimension", expected,
                   f"This answer should be {_expected_phrase(expected)}; {format_quantity(parsed)} is a different kind of measurement.",
                   parsed)


def format_decimal(value: Fraction) -> Optional[str]:
    """Exact terminating-decimal string for `value`, or None if it does not terminate."""
    d = value.denominator
    twos = fives = 0
    t = d
    while t % 2 == 0:
        t //= 2; twos += 1
    while t % 5 == 0:
        t //= 5; fives += 1
    if t != 1:
        return None
    k = max(twos, fives)
    if k == 0:
        return str(value.numerator)
    scaled = value.numerator * (10 ** k // d)
    s = str(abs(scaled)).rjust(k + 1, "0")
    s = s[:-k] + "." + s[-k:]
    return ("-" if scaled < 0 else "") + s


def checker_evidence(ans: Quantity) -> list:
    """The shared quantity-checker evidence matrix (owner D/C3): GENUINELY-DIFFERENT accepted forms
    (no-space, extra-space, unreduced fraction, terminating decimal, Unicode superscript), every
    reject code, and every malformed-response category. Each entry is {scenario, response,
    expectedCode, genuinelyDifferent}; the canonical form is the only non-genuinely-different one."""
    val = format_value(ans.value)
    tok = unit_token(ans.baseUnit, ans.exponent)
    other = {"mm": "cm", "cm": "m", "m": "cm"}[ans.baseUnit]
    ev: list = []

    def add(scenario: str, resp: str, code: str, diff: bool = False) -> None:
        ev.append({"scenario": scenario, "response": resp, "expectedCode": code, "genuinelyDifferent": diff})

    add("canonical form", format_quantity(ans), "correct", False)
    add("no-space unit form", f"{val}{tok}", "correct", True)
    add("extra-space form", f"{val}  {tok}", "correct", True)
    if ans.value.denominator != 1:
        # raw doubled integers (Fraction would auto-reduce, defeating the "unreduced" intent)
        add("unreduced fraction form", f"{ans.value.numerator * 2}/{ans.value.denominator * 2} {tok}", "correct", True)
        dec = format_decimal(ans.value)
        if dec is not None:
            add("terminating decimal form", f"{dec} {tok}", "correct", True)
    if ans.exponent == 2:
        add("Unicode superscript form", f"{val} {ans.baseUnit}²", "correct", True)

    add("bare number (no unit)", val, "missing-unit")
    add("wrong base unit (no conversion)", format_quantity(Quantity(ans.dimension, other, ans.exponent, ans.value)), "wrong-base-unit")
    add("incorrect value, correct unit", format_quantity(Quantity(ans.dimension, ans.baseUnit, ans.exponent, ans.value + 1)), "incorrect-value")
    if ans.dimension == "area":
        add("linear units for an area", format_quantity(make_length(ans.value, ans.baseUnit)), "wrong-exponent")
        add("different dimensional quantity", format_quantity(make_length(ans.value, other)), "wrong-dimension")
    else:
        add("square units for a length", format_quantity(make_area(ans.value, ans.baseUnit)), "wrong-exponent")
        add("different dimensional quantity", format_quantity(make_area(ans.value, other)), "wrong-dimension")

    add("scientific notation", f"{val}e2 {tok}", "malformed-response")
    add("trailing unparsed text", f"{format_quantity(ans)} long", "malformed-response")
    add("conflicting unit tokens", f"{val} {ans.baseUnit} {other}", "malformed-response")
    add("malformed fraction", f"{ans.value.numerator}/ {tok}", "malformed-response")
    add("malformed exponent", f"{val} {ans.baseUnit}^3", "malformed-response")
    add("unsupported compound unit", f"{val} {ans.baseUnit}/s", "malformed-response")
    add("empty response", "", "malformed-response")
    add("multiple numerical expressions", f"{val} {tok} {val} {tok}", "malformed-response")
    return ev


def _result(code: str, expected: Quantity, feedback: str, parsed: Optional[Quantity] = None) -> Dict[str, object]:
    out: Dict[str, object] = {
        "code": code,
        "correct": code == "correct",
        "feedback": feedback,
        "expected": format_quantity(expected),
    }
    if parsed is not None:
        out["parsed"] = format_quantity(parsed)
    return out
