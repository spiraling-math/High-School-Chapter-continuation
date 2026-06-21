"""Linear-equation misconception registry (oracle reference).

Each misconception is an INDEPENDENTLY recomputable wrong-answer rule over the
reduced form ``P*x + Q = R*x + T`` (true solution ``s = (T - Q)/(P - R)``). A rule
returns its wrong value as a Fraction, or ``None`` when it does not apply to the
given parameters. ``observableError`` is serialized into items as the distractor
rationale, so it MUST match domains/algebra/linear-misconceptions.ts byte-for-byte.

Approved set (owner curriculum review, 2026-06-21). DISTRIBUTE_NONE is deferred;
SIGNED_ARITH_SLIP is a diagnostic-only category (excluded from MC generation).
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Optional


# red = {P, Q, R, T, kMul, innerP, innerQ}  (Fractions; bracket fields None otherwise)
def _stops(red):
    if abs(red["P"] - red["R"]) == 1:
        return None
    return red["T"] - red["Q"]


def _wrong_inverse(red):
    if red["Q"] == 0:
        return None
    return Fraction(red["T"] + red["Q"], red["P"] - red["R"])


def _var_sign(red):
    if red["R"] == 0 or (red["P"] + red["R"]) == 0:
        return None
    return Fraction(red["T"] - red["Q"], red["P"] + red["R"])


def _const_sign(red):
    if red["Q"] == 0:
        return None
    return Fraction(red["Q"] - red["T"], red["P"] - red["R"])


def _combine_unlike(red):
    denom = red["P"] + red["Q"] - red["R"]
    if red["Q"] == 0 or denom == 0:
        return None
    return Fraction(red["T"], denom)


def _divide_one_term(red):
    if red["Q"] == 0:
        return None
    return Fraction(red["T"], red["P"] - red["R"]) - red["Q"]


def _divide_by_constant(red):
    if red["Q"] == 0 or red["Q"] == (red["P"] - red["R"]):
        return None
    return Fraction(red["T"] - red["Q"], red["Q"])


def _ignore_constant(red):
    if red["Q"] == 0:
        return None
    return red["T"]


def _multiply_instead(red):
    if red["T"] == 0 or red["P"] == 1 or red["P"] == -1:
        return None
    return red["P"] * red["T"]


def _reverses_division(red):
    if red["T"] == 0:
        return None
    return Fraction(red["P"], red["T"])


def _distribute_partial(red):
    if red["kMul"] is None or red["kMul"] == 1 or red["innerQ"] == 0:
        return None
    # k(px + q) -> kp*x + q  (multiplier applied only to the variable term)
    return Fraction(red["T"] - red["innerQ"], red["P"] - red["R"])


MISCONCEPTIONS: Dict[str, Dict[str, Any]] = {
    "MISC.LINEQ.STOPS_BEFORE_DIVIDING": {
        "wrong": _stops,
        "title": "Stops before dividing by the coefficient",
        "description": "Isolates the variable term but reports it as the variable, without dividing by the coefficient.",
        "observableError": "Isolated the variable term but did not divide by its coefficient.",
        "feedback": "You have isolated the variable term, but not the variable. Divide both sides by the coefficient of x.",
        "expression": "t - q",
    },
    "MISC.LINEQ.WRONG_INVERSE": {
        "wrong": _wrong_inverse,
        "title": "Wrong inverse operation on the constant",
        "description": "Adds the constant instead of subtracting it (or vice versa) when moving it across the equals sign.",
        "observableError": "Used the wrong inverse operation on the constant term.",
        "feedback": "Use the inverse operation on the constant term and apply it to both sides.",
        "expression": "(t + q)/(p - r)",
    },
    "MISC.LINEQ.VAR_SIGN": {
        "wrong": _var_sign,
        "title": "Wrong sign moving a variable term",
        "description": "Moves the variable term to the other side without flipping its sign.",
        "observableError": "Moved the variable term with the wrong sign (used p + r instead of p - r).",
        "feedback": "Subtract rx from both sides. The new variable coefficient is p - r, not p + r.",
        "expression": "(t - q)/(p + r)",
    },
    "MISC.LINEQ.CONST_SIGN": {
        "wrong": _const_sign,
        "title": "Wrong sign moving a constant",
        "description": "Changes the sign of a constant without applying the operation to both sides.",
        "observableError": "Changed the sign of a constant without applying the operation to both sides.",
        "feedback": "Apply the same subtraction to both sides and check the order of the constants.",
        "expression": "(q - t)/(p - r)",
    },
    "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT": {
        "wrong": _combine_unlike,
        "title": "Combines unlike terms",
        "description": "Adds an x-term and a constant into a single coefficient of x.",
        "observableError": "Combined an x-term and a constant into a single coefficient.",
        "feedback": "An x-term and a constant are unlike terms. Their coefficients cannot be combined.",
        "expression": "t/(p + q - r)",
    },
    "MISC.LINEQ.DIVIDE_ONE_TERM": {
        "wrong": _divide_one_term,
        "title": "Divides only one term",
        "description": "Divides one term on the side by the coefficient but not every term.",
        "observableError": "Divided only one term on the side, not every term.",
        "feedback": "When dividing an equation, divide every term on the relevant side by the coefficient.",
        "expression": "t/(p - r) - q",
    },
    "MISC.LINEQ.DIVIDE_BY_CONSTANT": {
        "wrong": _divide_by_constant,
        "title": "Divides by the constant",
        "description": "Divides by the constant term instead of by the coefficient of x.",
        "observableError": "Divided by the constant term instead of the coefficient of x.",
        "feedback": "Divide by the coefficient of x, not by the constant term.",
        "expression": "(t - q)/q",
    },
    "MISC.LINEQ.IGNORE_CONSTANT": {
        "wrong": _ignore_constant,
        "title": "Ignores the constant",
        "description": "Reads off the right-hand value as the answer, ignoring the added or subtracted constant.",
        "observableError": "Ignored the added or subtracted constant.",
        "feedback": "Apply the inverse of the constant to both sides; do not ignore it.",
        "expression": "t",
    },
    "MISC.LINEQ.MULTIPLY_INSTEAD_OF_DIVIDE": {
        "wrong": _multiply_instead,
        "title": "Multiplies instead of dividing",
        "description": "Multiplies both sides by the coefficient instead of dividing by it.",
        "observableError": "Multiplied by the coefficient instead of dividing by it.",
        "feedback": "To undo multiplication by p, divide both sides by p.",
        "expression": "p * t",
    },
    "MISC.LINEQ.REVERSES_DIVISION": {
        "wrong": _reverses_division,
        "title": "Reverses the division",
        "description": "Divides the coefficient by the constant instead of the constant by the coefficient.",
        "observableError": "Inverted the division: used p/t instead of t/p.",
        "feedback": "The equation gives x = t/p, not p/t.",
        "expression": "p / t",
    },
    "MISC.LINEQ.DISTRIBUTE_PARTIAL": {
        "wrong": _distribute_partial,
        "title": "Partial distribution over brackets",
        "description": "Multiplies the factor outside the bracket by the variable term only, not the constant term.",
        "observableError": "Multiplied only the first term inside the brackets by the factor.",
        "feedback": "Multiply every term inside the brackets by the factor outside.",
        "expression": "k(px + q) -> kp*x + q",
    },
    # Diagnostic-only category — NEVER used for MC distractor generation.
    "MISC.LINEQ.SIGNED_ARITH_SLIP": {
        "wrong": lambda red: None,
        "title": "Signed-number arithmetic slip",
        "description": "A generic signed-number arithmetic error; not a deterministic distractor rule.",
        "observableError": "Made a signed-number arithmetic error.",
        "feedback": "Re-check the signed arithmetic at each step.",
        "expression": "(diagnostic only)",
    },
}


_ELIGIBILITY = {
    "one_step_add": ["MISC.LINEQ.IGNORE_CONSTANT", "MISC.LINEQ.WRONG_INVERSE",
                     "MISC.LINEQ.CONST_SIGN", "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT"],
    "one_step_mul": ["MISC.LINEQ.STOPS_BEFORE_DIVIDING", "MISC.LINEQ.MULTIPLY_INSTEAD_OF_DIVIDE",
                     "MISC.LINEQ.REVERSES_DIVISION"],
    "two_step": ["MISC.LINEQ.STOPS_BEFORE_DIVIDING", "MISC.LINEQ.WRONG_INVERSE",
                 "MISC.LINEQ.DIVIDE_ONE_TERM", "MISC.LINEQ.DIVIDE_BY_CONSTANT",
                 "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT"],
    "both_sides": ["MISC.LINEQ.STOPS_BEFORE_DIVIDING", "MISC.LINEQ.WRONG_INVERSE",
                   "MISC.LINEQ.VAR_SIGN", "MISC.LINEQ.CONST_SIGN",
                   "MISC.LINEQ.DIVIDE_ONE_TERM", "MISC.LINEQ.DIVIDE_BY_CONSTANT",
                   "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT"],
    "brackets": ["MISC.LINEQ.DISTRIBUTE_PARTIAL", "MISC.LINEQ.STOPS_BEFORE_DIVIDING",
                 "MISC.LINEQ.WRONG_INVERSE", "MISC.LINEQ.VAR_SIGN", "MISC.LINEQ.CONST_SIGN",
                 "MISC.LINEQ.DIVIDE_ONE_TERM", "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT"],
}


def rules_for(task: str) -> List[str]:
    return list(_ELIGIBILITY.get(task, []))
