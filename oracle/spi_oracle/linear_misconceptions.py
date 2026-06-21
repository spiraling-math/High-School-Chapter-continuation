"""Linear-equation misconception registry (oracle reference).

Each misconception is an INDEPENDENTLY recomputable wrong-answer rule over the
reduced form ``P*x + Q = R*x + T`` (true solution ``s = (T - Q)/(P - R)``). A rule
returns its wrong value as a Fraction, or ``None`` when it does not apply.

``observableError`` (serialized as the distractor rationale) and ``feedback`` (the
student-facing message, generated from the actual displayed coefficients) MUST
contain no internal placeholder symbols (p, q, r, t, k). Internal formulas live in
``expression`` (teacher/technical metadata) only. Mirrors
domains/algebra/linear-misconceptions.ts.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Optional


def _n(value) -> str:
    f = Fraction(value)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def _term(value) -> str:
    f = Fraction(value)
    if f == 1:
        return "x"
    if f == -1:
        return "-x"
    return f"{_n(f)}x"


# --- wrong-value rules (over the reduced form) ----------------------------- #
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
    return Fraction(red["T"] - red["innerQ"], red["P"] - red["R"])


# --- student-facing feedback (item-specific, symbol-free) ------------------ #
def _fb_stops(red):
    coef = red["P"] - red["R"]
    return f"Divide both sides by {_n(coef)} to find x, not just {_term(coef)}."


def _fb_wrong_inverse(red):
    q = red["Q"]
    if q > 0:
        return f"The constant {_n(q)} is added, so subtract {_n(q)} from both sides — do not add it."
    return f"The constant {_n(q)} is subtracted, so add {_n(-q)} to both sides — do not subtract it."


def _fb_var_sign(red):
    r = red["R"]
    if r > 0:
        return f"Subtract {_term(r)} from both sides so the variable terms are collected on one side."
    return f"Add {_term(-r)} to both sides so the variable terms are collected on one side."


def _fb_const_sign(red):
    return f"Apply the inverse of {_n(red['Q'])} to both sides and keep the sign of the constant consistent."


def _fb_combine(red):
    return f"{_term(red['P'])} and {_n(red['Q'])} are unlike terms; an x-term and a constant cannot be combined."


def _fb_divide_one(red):
    coef = red["P"] - red["R"]
    return f"Divide every term on that side by {_n(coef)}, not just one term."


def _fb_divide_const(red):
    coef = red["P"] - red["R"]
    return f"Divide by the coefficient of x ({_n(coef)}), not by the constant {_n(red['Q'])}."


def _fb_ignore(red):
    return f"Do not ignore the {_n(red['Q'])}; apply its inverse to both sides."


def _fb_multiply(red):
    return f"To undo multiplication by {_n(red['P'])}, divide both sides by {_n(red['P'])}."


def _fb_reverses(red):
    return f"Divide {_n(red['T'])} by {_n(red['P'])}. Do not reverse the numerator and denominator."


def _fb_distribute(red):
    return f"Multiply every term inside the brackets by {_n(red['kMul'])}."


def _fb_slip(red):
    return "Re-check the signed arithmetic at each step."


MISCONCEPTIONS: Dict[str, Dict[str, Any]] = {
    "MISC.LINEQ.STOPS_BEFORE_DIVIDING": {
        "wrong": _stops, "feedback": _fb_stops,
        "title": "Stops before dividing by the coefficient",
        "description": "Isolates the variable term but reports it as the variable, without dividing by the coefficient.",
        "observableError": "Isolated the variable term but did not divide by its coefficient.",
        "expression": "t - q",
    },
    "MISC.LINEQ.WRONG_INVERSE": {
        "wrong": _wrong_inverse, "feedback": _fb_wrong_inverse,
        "title": "Wrong inverse operation on the constant",
        "description": "Adds the constant instead of subtracting it (or vice versa) when moving it across the equals sign.",
        "observableError": "Used the wrong inverse operation on the constant term.",
        "expression": "(t + q)/(p - r)",
    },
    "MISC.LINEQ.VAR_SIGN": {
        "wrong": _var_sign, "feedback": _fb_var_sign,
        "title": "Wrong sign moving a variable term",
        "description": "Moves the variable term to the other side without flipping its sign.",
        "observableError": "Moved the variable term to the other side without flipping its sign.",
        "expression": "(t - q)/(p + r)",
    },
    "MISC.LINEQ.CONST_SIGN": {
        "wrong": _const_sign, "feedback": _fb_const_sign,
        "title": "Wrong sign moving a constant",
        "description": "Changes the sign of a constant without applying the operation to both sides.",
        "observableError": "Changed the sign of a constant without applying the operation to both sides.",
        "expression": "(q - t)/(p - r)",
    },
    "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT": {
        "wrong": _combine_unlike, "feedback": _fb_combine,
        "title": "Combines unlike terms",
        "description": "Adds an x-term and a constant into a single coefficient of x.",
        "observableError": "Combined an x-term and a constant into a single coefficient.",
        "expression": "t/(p + q - r)",
    },
    "MISC.LINEQ.DIVIDE_ONE_TERM": {
        "wrong": _divide_one_term, "feedback": _fb_divide_one,
        "title": "Divides only one term",
        "description": "Divides one term on the side by the coefficient but not every term.",
        "observableError": "Divided only one term on the side, not every term.",
        "expression": "t/(p - r) - q",
    },
    "MISC.LINEQ.DIVIDE_BY_CONSTANT": {
        "wrong": _divide_by_constant, "feedback": _fb_divide_const,
        "title": "Divides by the constant",
        "description": "Divides by the constant term instead of by the coefficient of x.",
        "observableError": "Divided by the constant term instead of the coefficient of x.",
        "expression": "(t - q)/q",
    },
    "MISC.LINEQ.IGNORE_CONSTANT": {
        "wrong": _ignore_constant, "feedback": _fb_ignore,
        "title": "Ignores the constant",
        "description": "Reads off the right-hand value as the answer, ignoring the added or subtracted constant.",
        "observableError": "Ignored the added or subtracted constant.",
        "expression": "t",
    },
    "MISC.LINEQ.MULTIPLY_INSTEAD_OF_DIVIDE": {
        "wrong": _multiply_instead, "feedback": _fb_multiply,
        "title": "Multiplies instead of dividing",
        "description": "Multiplies both sides by the coefficient instead of dividing by it.",
        "observableError": "Multiplied by the coefficient instead of dividing by it.",
        "expression": "p * t",
    },
    "MISC.LINEQ.REVERSES_DIVISION": {
        "wrong": _reverses_division, "feedback": _fb_reverses,
        "title": "Reverses the division",
        "description": "Divides the coefficient by the constant instead of the constant by the coefficient.",
        "observableError": "Inverted the division: divided the coefficient by the value instead of the value by the coefficient.",
        "expression": "p / t",
    },
    "MISC.LINEQ.DISTRIBUTE_PARTIAL": {
        "wrong": _distribute_partial, "feedback": _fb_distribute,
        "title": "Partial distribution over brackets",
        "description": "Multiplies the factor outside the bracket by the variable term only, not the constant term.",
        "observableError": "Multiplied only the first term inside the brackets by the factor.",
        "expression": "k(px + q) -> kp*x + q",
    },
    # Diagnostic-only category — NEVER used for MC distractor generation.
    "MISC.LINEQ.SIGNED_ARITH_SLIP": {
        "wrong": lambda red: None, "feedback": _fb_slip,
        "title": "Signed-number arithmetic slip",
        "description": "A generic signed-number arithmetic error; not a deterministic distractor rule.",
        "observableError": "Made a signed-number arithmetic error.",
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
