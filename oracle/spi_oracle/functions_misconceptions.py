"""MISC.FUNC.* misconception registry for gen.functions.foundations (oracle reference).

Every rule is an INDEPENDENTLY recomputable wrong value over the item's rule record(s). A rule
returns its wrong value in the task's value space — a Fraction (numeric tasks), a Poly or a
``{"kind": "reciprocal-of", ...}`` marker (expression tasks), or a real-subset descriptor (domain /
range tasks) — or ``None`` when it does not apply. ``observableError`` (serialized as the distractor
rationale) and the item-specific ``feedback(ctx)`` (student-facing) contain NO internal placeholder
symbols; internal formulas live in ``expression`` (teacher/technical metadata) only.

The three ``identify_function`` records describe the structure of a wrongly chosen relation; their
wrong values are built by the generator's relation draw (``wrong`` returns None) and the validator
checks the structure of each option instead.

Mirrors domains/functions/functions-misconceptions.ts.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable, Dict, List, Optional

import functions_core as C
from polynomial import Poly, rat_display

Ctx = Dict[str, Any]
_n = rat_display


def _rule(ctx: Ctx) -> Dict[str, Any]:
    return ctx["rule"]


def _sq(ctx: Ctx) -> Optional[Fraction]:
    """The exact square root of the radicand at the evaluation input (sqrt rules)."""
    return C.sqrt_exact(C.radicand(_rule(ctx), ctx["p"]))


def _rec(poly: Poly) -> Dict[str, Any]:
    return {"kind": "reciprocal-of", "poly": poly}


# --------------------------------------------------------------------------- #
# evaluate_function
# --------------------------------------------------------------------------- #

def _eval_forgot_multiply(ctx):
    r = _rule(ctx)
    return r["a"] + ctx["p"] + r["b"] if r["kind"] == "linear" else None


def _eval_drop_constant(ctx):
    r, p = _rule(ctx), ctx["p"]
    k = r["kind"]
    if k == "linear":
        return r["a"] * p if r["b"] != 0 else None
    if k == "quadratic":
        return r["a"] * p * p + r["b"] * p if r["c"] != 0 else None
    if k == "reciprocal":
        return r["k"] / (p - r["h"]) if r["v"] != 0 and p != r["h"] else None
    t = _sq(ctx)
    return t if (t is not None and r["v"] != 0) else None


def _eval_sign_of_input(ctx):
    r, p = _rule(ctx), ctx["p"]
    if p >= 0:
        return None
    return C.eval_rule(r, -p)


def _eval_constant_sign_flipped(ctx):
    r, p = _rule(ctx), ctx["p"]
    if r["kind"] == "linear":
        return r["a"] * p - r["b"] if r["b"] != 0 else None
    if r["kind"] == "quadratic":
        return r["a"] * p * p + r["b"] * p - r["c"] if r["c"] != 0 else None
    return None


def _eval_square_negative(ctx):
    r, p = _rule(ctx), ctx["p"]
    if r["kind"] != "quadratic" or p >= 0:
        return None
    return -r["a"] * p * p + r["b"] * p + r["c"]


def _eval_square_coefficient(ctx):
    r, p = _rule(ctx), ctx["p"]
    if r["kind"] != "quadratic" or r["a"] == 1:
        return None
    return (r["a"] * p) * (r["a"] * p) + r["b"] * p + r["c"]


def _eval_square_as_double(ctx):
    r, p = _rule(ctx), ctx["p"]
    if r["kind"] != "quadratic":
        return None
    return 2 * r["a"] * p + r["b"] * p + r["c"]


def _eval_denominator_not_grouped(ctx):
    r, p = _rule(ctx), ctx["p"]
    if r["kind"] != "reciprocal" or p == 0:
        return None
    return r["k"] / p - r["h"] + r["v"]


def _eval_reciprocal_inverted(ctx):
    r, p = _rule(ctx), ctx["p"]
    if r["kind"] != "reciprocal":
        return None
    return (p - r["h"]) / r["k"] + r["v"]


def _eval_root_ignored(ctx):
    r, p = _rule(ctx), ctx["p"]
    if r["kind"] != "sqrt":
        return None
    return C.radicand(r, p) + r["v"]


def _eval_halve_instead_of_root(ctx):
    r, p = _rule(ctx), ctx["p"]
    if r["kind"] != "sqrt":
        return None
    return C.radicand(r, p) / 2 + r["v"]


def _eval_negative_root(ctx):
    r = _rule(ctx)
    if r["kind"] != "sqrt":
        return None
    t = _sq(ctx)
    return -t + r["v"] if (t is not None and t > 0) else None


# --------------------------------------------------------------------------- #
# solve_for_input  (ctx: rule, target = the given output, x0 = the true input)
# --------------------------------------------------------------------------- #

def _solve_evaluates_instead(ctx):
    r, k = _rule(ctx), ctx["target"]
    if r["kind"] == "sqrt":
        return None
    return C.eval_rule(r, k)


def _solve_wrong_inverse(ctx):
    r, k = _rule(ctx), ctx["target"]
    if r["kind"] == "linear":
        return (k + r["b"]) / r["a"] if r["b"] != 0 else None
    if r["kind"] == "sqrt":
        t = k - r["v"]
        return (t * t + r["b"]) / r["a"] if r["b"] != 0 else None
    return None


def _solve_stops_before_dividing(ctx):
    r, k = _rule(ctx), ctx["target"]
    if r["kind"] != "linear" or abs(r["a"]) == 1:
        return None
    return k - r["b"]


def _solve_divide_by_constant(ctx):
    r, k = _rule(ctx), ctx["target"]
    if r["kind"] != "linear" or r["b"] == 0 or r["b"] == r["a"]:
        return None
    return (k - r["b"]) / r["b"]


def _solve_reciprocal_not_inverted(ctx):
    r, k = _rule(ctx), ctx["target"]
    if r["kind"] != "reciprocal":
        return None
    return r["h"] + (k - r["v"]) / r["k"]


def _solve_pole_sign(ctx):
    r, k = _rule(ctx), ctx["target"]
    if r["kind"] != "reciprocal" or r["h"] == 0:
        return None
    return r["k"] / (k - r["v"]) - r["h"]


def _solve_ignores_shift(ctx):
    r, k = _rule(ctx), ctx["target"]
    if r["kind"] != "reciprocal" or r["v"] == 0 or k == 0:
        return None
    return r["h"] + r["k"] / k


def _solve_forgot_to_square(ctx):
    r, k = _rule(ctx), ctx["target"]
    if r["kind"] != "sqrt":
        return None
    return (k - r["v"] - r["b"]) / r["a"]


def _solve_square_before_isolating(ctx):
    r, k = _rule(ctx), ctx["target"]
    if r["kind"] != "sqrt" or r["v"] == 0:
        return None
    return (k * k - r["v"] - r["b"]) / r["a"]


# --------------------------------------------------------------------------- #
# domain_of_function
# --------------------------------------------------------------------------- #

def _domain_all_reals(ctx):
    r = _rule(ctx)
    return C.reals() if not C.is_polynomial_rule(r) else None


def _domain_direction_flipped(ctx):
    r = _rule(ctx)
    if r["kind"] != "sqrt":
        return None
    d = C.domain_of(r)
    return C.ray("x", d["endpoint"], True, "le" if d["direction"] == "ge" else "ge")


def _domain_strict_endpoint(ctx):
    r = _rule(ctx)
    if r["kind"] != "sqrt":
        return None
    d = C.domain_of(r)
    return C.ray("x", d["endpoint"], False, d["direction"])


def _domain_endpoint_sign(ctx):
    r = _rule(ctx)
    if r["kind"] != "sqrt" or r["b"] == 0:
        return None
    d = C.domain_of(r)
    return C.ray("x", r["b"] / r["a"], True, d["direction"])


def _domain_as_excluded_point(ctx):
    r = _rule(ctx)
    if r["kind"] != "sqrt":
        return None
    return C.reals_except("x", [-r["b"] / r["a"]])


def _domain_pole_sign(ctx):
    r = _rule(ctx)
    if r["kind"] != "reciprocal" or r["h"] == 0:
        return None
    return C.reals_except("x", [-r["h"]])


def _domain_excludes_zero(ctx):
    r = _rule(ctx)
    if r["kind"] == "reciprocal":
        return C.reals_except("x", [0]) if r["h"] != 0 else None
    if C.is_polynomial_rule(r):
        return C.reals_except("x", [0])
    return None


def _domain_pole_as_inequality(ctx):
    r = _rule(ctx)
    if r["kind"] != "reciprocal":
        return None
    return C.ray("x", r["h"], False, "ge")


def _domain_nonnegative_only(ctx):
    r = _rule(ctx)
    return C.ray("x", 0, True, "ge") if C.is_polynomial_rule(r) else None


def _domain_excludes_constant(ctx):
    r = _rule(ctx)
    if not C.is_polynomial_rule(r):
        return None
    c = r["b"] if r["kind"] == "linear" else r["c"]
    return C.reals_except("x", [c]) if c != 0 else None


# --------------------------------------------------------------------------- #
# range_of_function  (ctx: rule, restricted {p,q} for a linear rule)
# --------------------------------------------------------------------------- #

def _true_range(ctx):
    return C.range_of(_rule(ctx), ctx.get("restricted"))


def _range_all_reals(ctx):
    return C.reals()


def _range_direction_flipped(ctx):
    r = _rule(ctx)
    if r["kind"] not in ("quadratic", "sqrt"):
        return None
    t = _true_range(ctx)
    return C.ray("y", t["endpoint"], True, "le" if t["direction"] == "ge" else "ge")


def _range_uses_vertex_x(ctx):
    r = _rule(ctx)
    if r["kind"] != "quadratic":
        return None
    hx = C.vertex_x(r)
    t = _true_range(ctx)
    return C.ray("y", hx, True, t["direction"]) if hx != t["endpoint"] else None


def _range_strict_at_bound(ctx):
    r = _rule(ctx)
    if r["kind"] not in ("quadratic", "sqrt"):
        return None
    t = _true_range(ctx)
    return C.ray("y", t["endpoint"], False, t["direction"])


def _range_uses_constant_term(ctx):
    r = _rule(ctx)
    if r["kind"] != "quadratic":
        return None
    t = _true_range(ctx)
    return C.ray("y", r["c"], True, t["direction"]) if r["c"] != t["endpoint"] else None


def _range_ignores_shift(ctx):
    r = _rule(ctx)
    if r["kind"] == "sqrt":
        return C.ray("y", 0, True, "ge") if r["v"] != 0 else None
    if r["kind"] == "reciprocal":
        return C.reals_except("y", [0]) if r["v"] != 0 else None
    return None


def _domain_range_confused(ctx):
    r = _rule(ctx)
    if r["kind"] == "sqrt":
        d = C.domain_of(r)
        return C.ray("y", d["endpoint"], True, d["direction"])
    if r["kind"] == "reciprocal":
        return C.reals_except("y", [r["h"]]) if r["h"] != r["v"] else None
    if r["kind"] == "linear" and ctx.get("restricted") is not None:
        p, q = ctx["restricted"]["p"], ctx["restricted"]["q"]
        t = _true_range(ctx)
        return C.bounded("y", p, q, True, True) if (p, q) != (t["lo"], t["hi"]) else None
    return None


def _range_pole_as_inequality(ctx):
    r = _rule(ctx)
    return C.ray("y", r["v"], False, "ge") if r["kind"] == "reciprocal" else None


def _range_only_lower_bound(ctx):
    r = _rule(ctx)
    if r["kind"] != "linear" or ctx.get("restricted") is None:
        return None
    t = _true_range(ctx)
    return C.ray("y", t["lo"], True, "ge")


def _range_strict_endpoints(ctx):
    r = _rule(ctx)
    if r["kind"] != "linear" or ctx.get("restricted") is None:
        return None
    t = _true_range(ctx)
    return C.bounded("y", t["lo"], t["hi"], False, False)


# --------------------------------------------------------------------------- #
# composite_value / composite_expression  (ctx: outer, inner rules (polynomial), p)
# --------------------------------------------------------------------------- #

def _po(ctx):
    return C.rule_poly(ctx["outer"]), C.rule_poly(ctx["inner"])


def _comp_order_reversed(ctx):
    outer, inner = _po(ctx)
    if ctx["task"] == "composite_value":
        return inner.eval(outer.eval(ctx["p"]))
    rev = inner.compose(outer)
    return rev if not rev.equals(outer.compose(inner)) else None


def _comp_as_product(ctx):
    outer, inner = _po(ctx)
    if ctx["task"] == "composite_value":
        return outer.eval(ctx["p"]) * inner.eval(ctx["p"])
    return outer.mul(inner)


def _comp_as_sum(ctx):
    outer, inner = _po(ctx)
    if ctx["task"] == "composite_value":
        return outer.eval(ctx["p"]) + inner.eval(ctx["p"])
    return outer.add(inner)


def _comp_inner_only(ctx):
    outer, inner = _po(ctx)
    return inner.eval(ctx["p"]) if ctx["task"] == "composite_value" else None


def _comp_outer_at_input(ctx):
    outer, inner = _po(ctx)
    return outer.eval(ctx["p"]) if ctx["task"] == "composite_value" else None


def _comp_square_no_cross_term(ctx):
    if ctx["task"] != "composite_expression":
        return None
    o, i = ctx["outer"], ctx["inner"]
    if o["kind"] != "quadratic" or i["kind"] != "linear":
        return None
    m, n = i["a"], i["b"]
    if m == 0 or n == 0:
        return None
    # (mx + n)^2 -> m^2 x^2 + n^2 (the cross term 2mn x dropped)
    sq = Poly.quadratic(m * m, 0, n * n)
    return sq.scale(o["a"]).add(Poly.linear(m, n).scale(o["b"])).add(Poly.const(o["c"]))


# --------------------------------------------------------------------------- #
# function_from_composite  (ctx: A, B = true outer; m, c = inner; comp_p, comp_q = composite)
# --------------------------------------------------------------------------- #

def _ffc_ignores_inner(ctx):
    return Poly.linear(ctx["comp_p"], ctx["comp_q"])


def _ffc_shift_not_inverted(ctx):
    p, q, m, c = ctx["comp_p"], ctx["comp_q"], ctx["m"], ctx["c"]
    return Poly.linear(p / m, p * c / m + q)


def _ffc_scale_not_inverted(ctx):
    p, q, m, c = ctx["comp_p"], ctx["comp_q"], ctx["m"], ctx["c"]
    if m == 1:
        return None
    return Poly.linear(p * m, -p * m * c + q)


def _ffc_composes_instead(ctx):
    p, q, m, c = ctx["comp_p"], ctx["comp_q"], ctx["m"], ctx["c"]
    return Poly.linear(p * m, p * c + q)


# --------------------------------------------------------------------------- #
# inverse_expression / inverse_value  (ctx: a, b; form; k; x0)
# --------------------------------------------------------------------------- #

def _inv_as_reciprocal(ctx):
    if ctx["task"] != "inverse_expression":
        return None
    return _rec(Poly.linear(ctx["a"], ctx["b"]))


def _inv_undo_order(ctx):
    a, b = ctx["a"], ctx["b"]
    if b == 0 or a == 1:
        return None
    if ctx["task"] == "inverse_expression":
        return Poly.linear(1 / a, -b)
    if ctx.get("form") == "inverse_at":
        return ctx["k"] / a - b
    return None


def _inv_sign_error(ctx):
    a, b = ctx["a"], ctx["b"]
    if b == 0:
        return None
    if ctx["task"] == "inverse_expression":
        return Poly.linear(1 / a, b / a)
    if ctx.get("form") == "inverse_at":
        return (ctx["k"] + b) / a
    return a * ctx["x0"] - b


def _inv_negates_only(ctx):
    a, b = ctx["a"], ctx["b"]
    if ctx["task"] != "inverse_expression" or b == 0:
        return None
    return Poly.linear(a, -b)


def _inv_swaps_roles(ctx):
    a, b = ctx["a"], ctx["b"]
    if ctx["task"] != "inverse_expression" or b == 0:
        return None
    return Poly.linear(1 / b, -a / b)


def _invval_forward(ctx):
    if ctx.get("form") != "inverse_at":
        return None
    return ctx["a"] * ctx["k"] + ctx["b"]


def _invval_reciprocal(ctx):
    a, b = ctx["a"], ctx["b"]
    x = ctx["k"] if ctx.get("form") == "inverse_at" else ctx["x0"]
    fx = a * x + b
    return 1 / fx if fx != 0 else None


def _invval_applies_inverse_again(ctx):
    if ctx.get("form") != "solve_inverse_equation":
        return None
    return (ctx["x0"] - ctx["b"]) / ctx["a"]


def _invval_identity(ctx):
    if ctx.get("form") != "solve_inverse_equation":
        return None
    return ctx["x0"]


# --------------------------------------------------------------------------- #
# one_to_one_restriction  (ctx: rule quadratic)
# --------------------------------------------------------------------------- #

def _vertex_x_missing_half(ctx):
    r = _rule(ctx)
    return -r["b"] / r["a"]


def _vertex_x_sign(ctx):
    r = _rule(ctx)
    return r["b"] / (2 * r["a"])


def _vertex_y_for_x(ctx):
    r = _rule(ctx)
    hy = C.vertex_y(r)
    return hy if hy != C.vertex_x(r) else None


def _restriction_zero(ctx):
    return Fraction(0)


def _vertex_x_uses_c(ctx):
    r = _rule(ctx)
    if r["c"] == 0 or r["c"] == r["b"]:
        return None
    return -r["c"] / (2 * r["a"])


# --------------------------------------------------------------------------- #
# Feedback helpers (student-facing; built from displayed values only)
# --------------------------------------------------------------------------- #

def _fname(ctx) -> str:
    return ctx.get("name", "f")


def _fb_eval(ctx, msg_by_kind: Dict[str, Callable[[], str]]) -> str:
    """Dispatch a feedback builder on the rule kind; builders are thunks so only the matching one runs."""
    make = msg_by_kind.get(_rule(ctx)["kind"], msg_by_kind.get("*"))
    return make() if make is not None else ""


# --------------------------------------------------------------------------- #
# The registry
# --------------------------------------------------------------------------- #

def _entry(wrong: Callable[[Ctx], Any], feedback: Callable[[Ctx], str], title: str, description: str,
           observable: str, expression: str) -> Dict[str, Any]:
    return {"wrong": wrong, "feedback": feedback, "title": title, "description": description,
            "observableError": observable, "expression": expression}


MISCONCEPTIONS: Dict[str, Dict[str, Any]] = {
    # --- identify_function (structural; built by the relation draw) ---------------------------- #
    "MISC.FUNC.MANY_TO_ONE_REJECTED": _entry(
        lambda ctx: None,
        lambda ctx: "Two different inputs may share the same output. A relation fails to be a function only when ONE input has two different outputs.",
        "Rejects a many-to-one relation", "Believes a relation with a repeated output cannot be a function.",
        "Chose a relation in which two inputs share an output.", "repeated output -> 'not a function'"),
    "MISC.FUNC.CONSTANT_REJECTED": _entry(
        lambda ctx: None,
        lambda ctx: "A constant relation sends every input to the same output; each input still has exactly one output, so it is a function.",
        "Rejects a constant relation", "Believes a relation whose outputs are all equal cannot be a function.",
        "Chose a relation whose outputs are all equal.", "all outputs equal -> 'not a function'"),
    "MISC.FUNC.PATTERN_REQUIRED": _entry(
        lambda ctx: None,
        lambda ctx: "A function does not need a formula or a visible pattern. Check only that no input appears twice with different outputs.",
        "Requires a pattern", "Believes a relation must follow a formula or an ordered pattern to be a function.",
        "Chose a relation with no visible pattern.", "no pattern -> 'not a function'"),

    # --- evaluate_function ------------------------------------------------------------------- #
    "MISC.FUNC.EVAL_FORGOT_MULTIPLY": _entry(
        _eval_forgot_multiply,
        lambda ctx: f"{_n(_rule(ctx)['a'])}x means {_n(_rule(ctx)['a'])} multiplied by x, so substitute x = {_n(ctx['p'])} and multiply: {_n(_rule(ctx)['a'])} × ({_n(ctx['p'])}).",
        "Adds the coefficient instead of multiplying", "Reads ax as a + x when substituting.",
        "Added the coefficient to the input instead of multiplying.", "a + p + b"),
    "MISC.FUNC.EVAL_DROP_CONSTANT": _entry(
        _eval_drop_constant,
        lambda ctx: _fb_eval(ctx, {"linear": lambda: f"After multiplying, remember the constant term {_n(_rule(ctx)['b'])}.",
                                  "quadratic": lambda: f"After the x^2 and x terms, remember the constant term {_n(_rule(ctx)['c'])}.",
                                  "reciprocal": lambda: f"After the fraction, remember to add the constant {_n(_rule(ctx)['v'])}.",
                                  "sqrt": lambda: f"After the square root, remember to add the constant {_n(_rule(ctx)['v'])}."}),
        "Drops the constant term", "Evaluates the variable part of the rule and forgets the constant term.",
        "Left out the constant term of the rule.", "rule without its constant"),
    "MISC.FUNC.EVAL_SIGN_OF_INPUT": _entry(
        _eval_sign_of_input,
        lambda ctx: f"The input is {_n(ctx['p'])}, not {_n(-ctx['p'])}. Substitute the negative value in brackets and keep its sign.",
        "Drops the sign of a negative input", "Substitutes |x| instead of a negative input.",
        "Substituted the positive value instead of the negative input.", "f(|p|)"),
    "MISC.FUNC.EVAL_CONSTANT_SIGN_FLIPPED": _entry(
        _eval_constant_sign_flipped,
        lambda ctx: "Keep the sign of the constant term exactly as it appears in the rule.",
        "Flips the sign of the constant", "Subtracts the constant that should be added (or vice versa).",
        "Used the opposite sign on the constant term.", "a p - b  /  a p^2 + b p - c"),
    "MISC.FUNC.EVAL_SQUARE_NEGATIVE": _entry(
        _eval_square_negative,
        lambda ctx: f"({_n(ctx['p'])})^2 = {_n(ctx['p'] * ctx['p'])}: squaring a negative number gives a positive result.",
        "Squares a negative input to a negative", "Computes (-p)^2 as -p^2.",
        "Treated the square of a negative input as negative.", "-a p^2 + b p + c"),
    "MISC.FUNC.EVAL_SQUARE_COEFFICIENT": _entry(
        _eval_square_coefficient,
        lambda ctx: f"{_n(_rule(ctx)['a'])}x^2 squares only x, not the coefficient: compute x^2 first, then multiply by {_n(_rule(ctx)['a'])}.",
        "Squares the coefficient as well", "Computes a x^2 as (a x)^2.",
        "Squared the coefficient together with the input.", "(a p)^2 + b p + c"),
    "MISC.FUNC.EVAL_SQUARE_AS_DOUBLE": _entry(
        _eval_square_as_double,
        lambda ctx: f"x^2 means x × x, not 2x: ({_n(ctx['p'])})^2 = {_n(ctx['p'] * ctx['p'])}.",
        "Treats x^2 as 2x", "Doubles the input instead of squaring it.",
        "Doubled the input instead of squaring it.", "2 a p + b p + c"),
    "MISC.FUNC.EVAL_DENOMINATOR_NOT_GROUPED": _entry(
        _eval_denominator_not_grouped,
        lambda ctx: f"The whole expression {C._denominator_text(_rule(ctx)['h'])} is the denominator: evaluate it first, then divide.",
        "Ungroups the denominator", "Divides by x alone and treats the rest of the denominator as a separate term.",
        "Divided by x alone instead of by the whole denominator.", "k/p - h + v"),
    "MISC.FUNC.EVAL_RECIPROCAL_INVERTED": _entry(
        _eval_reciprocal_inverted,
        lambda ctx: f"The numerator is {_n(_rule(ctx)['k'])} and the denominator is {C._denominator_text(_rule(ctx)['h'])}; do not turn the fraction upside down.",
        "Inverts the fraction", "Divides the denominator by the numerator.",
        "Inverted the fraction when evaluating.", "(p - h)/k + v"),
    "MISC.FUNC.EVAL_ROOT_IGNORED": _entry(
        _eval_root_ignored,
        lambda ctx: f"Evaluate the expression under the root, {C.radicand_text(_rule(ctx))}, and then take its square root.",
        "Ignores the square root", "Evaluates the radicand and forgets to take the root.",
        "Did not take the square root.", "a p + b + v"),
    "MISC.FUNC.EVAL_HALVE_INSTEAD_OF_ROOT": _entry(
        _eval_halve_instead_of_root,
        lambda ctx: "A square root is not the same as halving: find the number whose square is the radicand.",
        "Halves instead of rooting", "Divides the radicand by 2 instead of taking its square root.",
        "Halved the radicand instead of taking its square root.", "(a p + b)/2 + v"),
    "MISC.FUNC.EVAL_NEGATIVE_ROOT": _entry(
        _eval_negative_root,
        lambda ctx: "The square-root symbol denotes the non-negative root, so take the positive value.",
        "Takes the negative root", "Uses the negative square root for the radical symbol.",
        "Used the negative square root.", "-sqrt(a p + b) + v"),

    # --- solve_for_input --------------------------------------------------------------------- #
    "MISC.FUNC.SOLVE_EVALUATES_INSTEAD": _entry(
        _solve_evaluates_instead,
        lambda ctx: f"{_fname(ctx)}(x) = {_n(ctx['target'])} asks for the INPUT x whose output is {_n(ctx['target'])}; do not substitute {_n(ctx['target'])} into the rule.",
        "Evaluates instead of solving", "Substitutes the given output as if it were the input.",
        "Substituted the output value into the rule instead of solving for the input.", "f(k)"),
    "MISC.FUNC.SOLVE_WRONG_INVERSE": _entry(
        _solve_wrong_inverse,
        lambda ctx: "Undo the constant with the inverse operation: a constant that is added must be subtracted from both sides (and vice versa).",
        "Wrong inverse operation on the constant", "Adds the constant instead of subtracting it when isolating the variable term.",
        "Used the wrong inverse operation on the constant.", "(k + b)/a"),
    "MISC.FUNC.SOLVE_STOPS_BEFORE_DIVIDING": _entry(
        _solve_stops_before_dividing,
        lambda ctx: f"After isolating the x term, divide both sides by the coefficient {_n(_rule(ctx)['a'])}.",
        "Stops before dividing by the coefficient", "Reports the isolated variable term as the variable.",
        "Isolated the variable term but did not divide by its coefficient.", "k - b"),
    "MISC.FUNC.SOLVE_DIVIDE_BY_CONSTANT": _entry(
        _solve_divide_by_constant,
        lambda ctx: f"Divide by the coefficient of x, {_n(_rule(ctx)['a'])}, not by the constant {_n(_rule(ctx)['b'])}.",
        "Divides by the constant", "Divides by the constant term instead of the coefficient of x.",
        "Divided by the constant term instead of by the coefficient of x.", "(k - b)/b"),
    "MISC.FUNC.SOLVE_RECIPROCAL_NOT_INVERTED": _entry(
        _solve_reciprocal_not_inverted,
        lambda ctx: f"To undo the fraction, divide {_n(_rule(ctx)['k'])} by the isolated value: x - {_n(_rule(ctx)['h'])} = {_n(_rule(ctx)['k'])} ÷ (value)." if _rule(ctx)["h"] != 0 else f"To undo the fraction, divide {_n(_rule(ctx)['k'])} by the isolated value.",
        "Does not invert the reciprocal", "Multiplies by the numerator instead of dividing the numerator by the isolated value.",
        "Treated the reciprocal like a linear coefficient.", "h + (k - v)/k0"),
    "MISC.FUNC.SOLVE_POLE_SIGN": _entry(
        _solve_pole_sign,
        lambda ctx: f"The denominator is {C._denominator_text(_rule(ctx)['h'])}; after finding its value, solve for x with the correct sign of {_n(_rule(ctx)['h'])}.",
        "Sign error at the pole", "Subtracts the shift of the denominator instead of adding it back.",
        "Used the wrong sign when undoing the shift inside the denominator.", "k0/(k - v) - h"),
    "MISC.FUNC.SOLVE_IGNORES_SHIFT": _entry(
        _solve_ignores_shift,
        lambda ctx: f"First subtract the constant {_n(_rule(ctx)['v'])} from both sides, then deal with the fraction.",
        "Ignores the vertical shift", "Does not remove the added constant before inverting the fraction.",
        "Did not subtract the constant before undoing the fraction.", "h + k0/k"),
    "MISC.FUNC.SOLVE_FORGOT_TO_SQUARE": _entry(
        _solve_forgot_to_square,
        lambda ctx: "To undo a square root, square both sides once the root is isolated.",
        "Forgets to square", "Removes the root without squaring the other side.",
        "Did not square both sides to remove the root.", "(k - v - b)/a"),
    "MISC.FUNC.SOLVE_SQUARE_BEFORE_ISOLATING": _entry(
        _solve_square_before_isolating,
        lambda ctx: f"Isolate the square root first (subtract {_n(_rule(ctx)['v'])}), and only then square both sides.",
        "Squares before isolating the root", "Squares the whole output before removing the added constant.",
        "Squared before isolating the square root.", "(k^2 - v - b)/a"),

    # --- domain_of_function ------------------------------------------------------------------ #
    "MISC.FUNC.DOMAIN_ALL_REALS": _entry(
        _domain_all_reals,
        lambda ctx: _fb_eval(ctx, {"sqrt": lambda: "A square root is only defined when the expression under it is at least 0.",
                                  "reciprocal": lambda: "A fraction is undefined when its denominator is 0; that input must be excluded."}),
        "Domain is always all reals", "Ignores the restriction imposed by a root or a denominator.",
        "Gave all real numbers although the rule has a restriction.", "R"),
    "MISC.FUNC.DOMAIN_DIRECTION_FLIPPED": _entry(
        _domain_direction_flipped,
        lambda ctx: "Solve the inequality carefully: dividing by a negative number reverses the inequality sign.",
        "Inequality direction flipped", "Reverses (or fails to reverse) the inequality when solving the radicand condition.",
        "Solved the radicand inequality in the wrong direction.", "opposite ray"),
    "MISC.FUNC.DOMAIN_STRICT_ENDPOINT": _entry(
        _domain_strict_endpoint,
        lambda ctx: "The square root of 0 is defined (it equals 0), so the endpoint belongs to the domain.",
        "Excludes the endpoint", "Uses a strict inequality, excluding the input where the radicand is 0.",
        "Excluded the endpoint where the radicand is zero.", "strict ray"),
    "MISC.FUNC.DOMAIN_ENDPOINT_SIGN": _entry(
        _domain_endpoint_sign,
        lambda ctx: f"Solve {C.radicand_text(_rule(ctx))} >= 0 step by step; watch the sign when moving the constant across.",
        "Sign error in the endpoint", "Solves the radicand inequality with a sign slip in the constant.",
        "Made a sign error solving for the boundary input.", "x >= b/a"),
    "MISC.FUNC.DOMAIN_AS_EXCLUDED_POINT": _entry(
        _domain_as_excluded_point,
        lambda ctx: "A square root needs the whole radicand to be non-negative, not merely non-zero: the answer is an inequality, not a single excluded value.",
        "Treats the root like a denominator", "Excludes the single input where the radicand is 0 instead of requiring it to be non-negative.",
        "Excluded one point instead of solving the inequality.", "x != -b/a"),
    "MISC.FUNC.DOMAIN_POLE_SIGN": _entry(
        _domain_pole_sign,
        lambda ctx: f"The denominator {C._denominator_text(_rule(ctx)['h'])} is zero when x = {_n(_rule(ctx)['h'])}.",
        "Sign error at the pole", "Excludes the negative of the pole.",
        "Excluded the input with the wrong sign.", "x != -h"),
    "MISC.FUNC.DOMAIN_EXCLUDES_ZERO": _entry(
        _domain_excludes_zero,
        lambda ctx: _fb_eval(ctx, {"reciprocal": lambda: f"The input to exclude is the one that makes the denominator 0: {C._denominator_text(_rule(ctx)['h'])} = 0.",
                                  "*": lambda: "A polynomial rule is defined for every real number, including 0."}),
        "Excludes zero by habit", "Excludes x = 0 rather than the input that actually breaks the rule.",
        "Excluded zero instead of the actual restriction.", "x != 0"),
    "MISC.FUNC.DOMAIN_POLE_AS_INEQUALITY": _entry(
        _domain_pole_as_inequality,
        lambda ctx: "A denominator only needs to be non-zero, so exclude one value; an inequality would remove too much.",
        "Turns the pole into an inequality", "Writes an inequality instead of excluding the single undefined input.",
        "Wrote an inequality instead of excluding one value.", "x > h"),
    "MISC.FUNC.DOMAIN_NONNEGATIVE_ONLY": _entry(
        _domain_nonnegative_only,
        lambda ctx: "Negative inputs are allowed: a polynomial can be evaluated at any real number.",
        "Non-negative inputs only", "Restricts a polynomial rule to x >= 0.",
        "Restricted the domain to non-negative inputs without reason.", "x >= 0"),
    "MISC.FUNC.DOMAIN_EXCLUDES_CONSTANT": _entry(
        _domain_excludes_constant,
        lambda ctx: "The constant term of a polynomial does not restrict the inputs; every real number is allowed.",
        "Excludes the constant term", "Excludes the constant of the rule as if it were a pole.",
        "Excluded the value of the constant term.", "x != c"),

    # --- range_of_function ------------------------------------------------------------------- #
    "MISC.FUNC.RANGE_ALL_REALS": _entry(
        _range_all_reals,
        lambda ctx: _fb_eval(ctx, {"quadratic": lambda: "A quadratic has a minimum or maximum value at its vertex, so its outputs are bounded on one side.",
                                  "sqrt": lambda: "A square root is never negative, so the outputs are bounded below.",
                                  "reciprocal": lambda: "A fraction with a constant numerator can never be 0, so one output value is missed.",
                                  "linear": lambda: "On a restricted domain the outputs are bounded by the images of the endpoints."}),
        "Range is always all reals", "Ignores the bound imposed by the shape of the graph.",
        "Gave all real numbers although the outputs are bounded.", "R"),
    "MISC.FUNC.RANGE_DIRECTION_FLIPPED": _entry(
        _range_direction_flipped,
        lambda ctx: _fb_eval(ctx, {"quadratic": lambda: f"The coefficient of x^2 is {_n(_rule(ctx)['a'])}: {'positive, so the vertex is a minimum' if _rule(ctx)['a'] > 0 else 'negative, so the vertex is a maximum'}.",
                                  "sqrt": lambda: "A square root gives values at least 0, so after the shift the outputs lie above the bound, not below it."}),
        "Bound on the wrong side", "Uses the wrong direction of inequality for the bounded range.",
        "Gave the inequality in the wrong direction.", "opposite ray"),
    "MISC.FUNC.RANGE_USES_VERTEX_X": _entry(
        _range_uses_vertex_x,
        lambda ctx: f"The range uses the y-coordinate of the vertex; x = {_n(C.vertex_x(_rule(ctx)))} is where the vertex is, not its value.",
        "Uses the vertex x-coordinate", "Reports the axis of symmetry as the bound of the range.",
        "Used the x-coordinate of the vertex as the bound.", "y >= -b/2a"),
    "MISC.FUNC.RANGE_STRICT_AT_BOUND": _entry(
        _range_strict_at_bound,
        lambda ctx: "The bound is attained (at the vertex, or where the radicand is 0), so the inequality is not strict.",
        "Excludes the attained bound", "Uses a strict inequality although the extreme value is attained.",
        "Excluded the attained extreme value.", "strict ray"),
    "MISC.FUNC.RANGE_USES_CONSTANT_TERM": _entry(
        _range_uses_constant_term,
        lambda ctx: f"The constant term {_n(_rule(ctx)['c'])} is the value at x = 0, not the extreme value; find the vertex first.",
        "Uses the constant term as the bound", "Takes the y-intercept as the minimum or maximum.",
        "Used the y-intercept as the extreme value.", "y >= c"),
    "MISC.FUNC.RANGE_IGNORES_SHIFT": _entry(
        _range_ignores_shift,
        lambda ctx: f"The constant {_n(_rule(ctx)['v'])} shifts every output; apply it to the base range.",
        "Ignores the vertical shift", "States the range of the unshifted base function.",
        "Ignored the vertical shift.", "base range"),
    "MISC.FUNC.DOMAIN_RANGE_CONFUSED": _entry(
        _domain_range_confused,
        lambda ctx: "The range is the set of OUTPUT values (y), not the set of allowed inputs (x).",
        "Confuses domain and range", "Gives the domain (in y) instead of the range.",
        "Gave the domain instead of the range.", "domain restated in y"),
    "MISC.FUNC.RANGE_POLE_AS_INEQUALITY": _entry(
        _range_pole_as_inequality,
        lambda ctx: "The fraction takes every value except one (positive and negative), so exclude a single value rather than writing an inequality.",
        "Turns the missing value into an inequality", "Writes y > v instead of y != v.",
        "Wrote an inequality instead of excluding one value.", "y > v"),
    "MISC.FUNC.RANGE_ONLY_LOWER_BOUND": _entry(
        _range_only_lower_bound,
        lambda ctx: "On a closed restricted domain the outputs are bounded on BOTH sides: evaluate the rule at both endpoints.",
        "States only one bound", "Reports only the lower bound of a bounded range.",
        "Gave only one of the two bounds.", "y >= min"),
    "MISC.FUNC.RANGE_STRICT_ENDPOINTS": _entry(
        _range_strict_endpoints,
        lambda ctx: "The domain includes its endpoints, so their images are attained: use <= at both ends.",
        "Open interval for a closed domain", "Uses strict inequalities although the endpoint images are attained.",
        "Excluded the attained endpoint images.", "open interval"),

    # --- composite ---------------------------------------------------------------------------- #
    "MISC.FUNC.COMP_ORDER_REVERSED": _entry(
        _comp_order_reversed,
        lambda ctx: f"({ctx['outer_name']} o {ctx['inner_name']})(x) means {ctx['outer_name']}({ctx['inner_name']}(x)): apply {ctx['inner_name']} first, then {ctx['outer_name']}.",
        "Reverses the order of composition", "Applies the outer function first.",
        "Composed the functions in the wrong order.", "inner(outer(.))"),
    "MISC.FUNC.COMP_AS_PRODUCT": _entry(
        _comp_as_product,
        lambda ctx: f"({ctx['outer_name']} o {ctx['inner_name']}) is composition, not multiplication: substitute {ctx['inner_name']}(x) into {ctx['outer_name']}.",
        "Composition as a product", "Multiplies the two functions.",
        "Multiplied the functions instead of composing them.", "f * g"),
    "MISC.FUNC.COMP_AS_SUM": _entry(
        _comp_as_sum,
        lambda ctx: f"({ctx['outer_name']} o {ctx['inner_name']}) is composition, not addition: substitute {ctx['inner_name']}(x) into {ctx['outer_name']}.",
        "Composition as a sum", "Adds the two functions.",
        "Added the functions instead of composing them.", "f + g"),
    "MISC.FUNC.COMP_INNER_ONLY": _entry(
        _comp_inner_only,
        lambda ctx: f"After finding {ctx['inner_name']}({_n(ctx['p'])}), substitute that value into {ctx['outer_name']}.",
        "Stops after the inner function", "Reports the inner value without applying the outer function.",
        "Applied only the inner function.", "inner(p)"),
    "MISC.FUNC.COMP_OUTER_AT_INPUT": _entry(
        _comp_outer_at_input,
        lambda ctx: f"Apply {ctx['inner_name']} first: the input of {ctx['outer_name']} is {ctx['inner_name']}({_n(ctx['p'])}), not {_n(ctx['p'])}.",
        "Applies only the outer function", "Evaluates the outer function directly at the input.",
        "Applied only the outer function at the input.", "outer(p)"),
    "MISC.FUNC.COMP_SQUARE_NO_CROSS_TERM": _entry(
        _comp_square_no_cross_term,
        lambda ctx: "When squaring a binomial, include the cross term: (u + w)^2 = u^2 + 2uw + w^2.",
        "Squares a binomial without the cross term", "Expands (mx + n)^2 as m^2 x^2 + n^2.",
        "Dropped the cross term when squaring the inner expression.", "a(m^2 x^2 + n^2) + b(mx + n) + c"),

    # --- function_from_composite --------------------------------------------------------------- #
    "MISC.FUNC.FFC_IGNORES_INNER": _entry(
        _ffc_ignores_inner,
        lambda ctx: "The given expression is f(g(x)), not f(x); undo g to recover f.",
        "Takes the composite as f", "Reports the composite itself as the outer function.",
        "Gave the composite instead of the outer function.", "p x + q"),
    "MISC.FUNC.FFC_SHIFT_NOT_INVERTED": _entry(
        _ffc_shift_not_inverted,
        lambda ctx: f"Let u = g(x) = {C.rule_text(C.linear(ctx['m'], ctx['c']))} and express x in terms of u: the shift {_n(ctx['c'])} must be undone, not repeated.",
        "Does not invert the inner shift", "Substitutes x + c instead of x - c when changing variable.",
        "Undid the inner shift with the wrong sign.", "p(x + c)/m + q"),
    "MISC.FUNC.FFC_SCALE_NOT_INVERTED": _entry(
        _ffc_scale_not_inverted,
        lambda ctx: f"The inner function multiplies by {_n(ctx['m'])}; to recover x, divide by {_n(ctx['m'])}, do not multiply again.",
        "Does not invert the inner scale", "Multiplies by the inner coefficient instead of dividing.",
        "Undid the inner scale by multiplying instead of dividing.", "p m (x - c) + q"),
    "MISC.FUNC.FFC_COMPOSES_INSTEAD": _entry(
        _ffc_composes_instead,
        lambda ctx: "You composed the given expression with g again; instead, work backwards from f(g(x)) to f.",
        "Composes instead of decomposing", "Substitutes g into the composite.",
        "Composed with the inner function instead of undoing it.", "p(mx + c) + q"),

    # --- inverse ------------------------------------------------------------------------------- #
    "MISC.FUNC.INV_AS_RECIPROCAL": _entry(
        _inv_as_reciprocal,
        lambda ctx: f"{_fname(ctx)}^-1 is the inverse function, not the reciprocal 1/{_fname(ctx)}(x): swap x and y and solve for y.",
        "Inverse as reciprocal", "Confuses the inverse function with the reciprocal of the function.",
        "Gave the reciprocal instead of the inverse function.", "1/(ax + b)"),
    "MISC.FUNC.INV_UNDO_ORDER": _entry(
        _inv_undo_order,
        lambda ctx: f"Undo the operations in reverse order: first undo the constant {_n(ctx['b'])}, then divide by {_n(ctx['a'])}.",
        "Undoes the operations in the wrong order", "Divides before undoing the constant.",
        "Undid the operations in the wrong order.", "x/a - b"),
    "MISC.FUNC.INV_SIGN_ERROR": _entry(
        _inv_sign_error,
        lambda ctx: f"To undo {'+ ' + _n(ctx['b']) if ctx['b'] > 0 else '- ' + _n(-ctx['b'])}, apply the opposite operation.",
        "Sign error undoing the constant", "Adds the constant that should be subtracted (or vice versa).",
        "Used the wrong sign when undoing the constant.", "(x + b)/a"),
    "MISC.FUNC.INV_NEGATES_ONLY": _entry(
        _inv_negates_only,
        lambda ctx: f"Changing the sign of the constant does not undo the function; divide by {_n(ctx['a'])} as well.",
        "Negates the constant only", "Keeps the multiplication and only flips the sign of the constant.",
        "Only changed the sign of the constant.", "ax - b"),
    "MISC.FUNC.INV_SWAPS_ROLES": _entry(
        _inv_swaps_roles,
        lambda ctx: f"Divide by the coefficient of x ({_n(ctx['a'])}), not by the constant ({_n(ctx['b'])}).",
        "Swaps the coefficient and the constant", "Divides by the constant and subtracts the coefficient.",
        "Swapped the roles of the coefficient and the constant.", "(x - a)/b"),
    "MISC.FUNC.INVVAL_FORWARD": _entry(
        _invval_forward,
        lambda ctx: f"{_fname(ctx)}^-1({_n(ctx['k'])}) is the input x with {_fname(ctx)}(x) = {_n(ctx['k'])}; do not substitute {_n(ctx['k'])} into {_fname(ctx)}.",
        "Evaluates f instead of f^-1", "Substitutes the value into f rather than solving f(x) = value.",
        "Evaluated the function instead of its inverse.", "f(k)"),
    "MISC.FUNC.INVVAL_RECIPROCAL": _entry(
        _invval_reciprocal,
        lambda ctx: f"{_fname(ctx)}^-1 means the inverse function, not 1 divided by {_fname(ctx)}.",
        "Inverse value as a reciprocal", "Computes 1/f(value).",
        "Took the reciprocal of the function value.", "1/f(.)"),
    "MISC.FUNC.INVVAL_APPLIES_INVERSE_AGAIN": _entry(
        _invval_applies_inverse_again,
        lambda ctx: f"{_fname(ctx)}^-1(k) = {_n(ctx['x0'])} means {_fname(ctx)}({_n(ctx['x0'])}) = k, so evaluate {_fname(ctx)} at {_n(ctx['x0'])}.",
        "Applies the inverse a second time", "Applies f^-1 to the given input instead of f.",
        "Applied the inverse to the given value instead of the function.", "(x0 - b)/a"),
    "MISC.FUNC.INVVAL_IDENTITY": _entry(
        _invval_identity,
        lambda ctx: f"k is not {_n(ctx['x0'])}: {_fname(ctx)}^-1(k) = {_n(ctx['x0'])} means k = {_fname(ctx)}({_n(ctx['x0'])}).",
        "Reads the equation as the identity", "Reports the given input as the unknown.",
        "Reported the given value as the answer.", "x0"),

    # --- one_to_one_restriction --------------------------------------------------------------- #
    "MISC.FUNC.VERTEX_X_MISSING_HALF": _entry(
        _vertex_x_missing_half,
        lambda ctx: f"The axis of symmetry is x = -b/(2a): divide by twice the coefficient of x^2, that is by {_n(2 * _rule(ctx)['a'])}.",
        "Axis of symmetry without the half", "Uses -b/a for the axis of symmetry.",
        "Omitted the factor 2 in the axis of symmetry.", "-b/a"),
    "MISC.FUNC.VERTEX_X_SIGN": _entry(
        _vertex_x_sign,
        lambda ctx: "The axis of symmetry is x = -b/(2a); watch the sign of the x coefficient.",
        "Axis of symmetry with the wrong sign", "Uses b/(2a) for the axis of symmetry.",
        "Used the wrong sign in the axis of symmetry.", "b/2a"),
    "MISC.FUNC.VERTEX_Y_FOR_X": _entry(
        _vertex_y_for_x,
        lambda ctx: "The restriction is on the INPUT x at the vertex, not on the value of the function there.",
        "Uses the vertex value", "Reports the minimum/maximum value instead of where it occurs.",
        "Gave the vertex value instead of its x-coordinate.", "f(-b/2a)"),
    "MISC.FUNC.RESTRICTION_ZERO": _entry(
        _restriction_zero,
        lambda ctx: "The symmetry of this parabola is not about x = 0; find the axis of symmetry from the coefficients.",
        "Assumes the restriction is x = 0", "Restricts at 0 regardless of the axis of symmetry.",
        "Assumed the axis of symmetry is x = 0.", "0"),
    "MISC.FUNC.VERTEX_X_USES_C": _entry(
        _vertex_x_uses_c,
        lambda ctx: "The axis of symmetry depends on the x coefficient and the x^2 coefficient, not on the constant term.",
        "Uses the constant term in the axis", "Substitutes the constant term for the x coefficient in -b/(2a).",
        "Used the constant term in place of the x coefficient.", "-c/2a"),
}

ELIGIBILITY: Dict[str, List[str]] = {
    "identify_function": ["MISC.FUNC.MANY_TO_ONE_REJECTED", "MISC.FUNC.CONSTANT_REJECTED", "MISC.FUNC.PATTERN_REQUIRED"],
    "evaluate_function": ["MISC.FUNC.EVAL_FORGOT_MULTIPLY", "MISC.FUNC.EVAL_DROP_CONSTANT", "MISC.FUNC.EVAL_SIGN_OF_INPUT",
                          "MISC.FUNC.EVAL_CONSTANT_SIGN_FLIPPED", "MISC.FUNC.EVAL_SQUARE_NEGATIVE", "MISC.FUNC.EVAL_SQUARE_COEFFICIENT",
                          "MISC.FUNC.EVAL_SQUARE_AS_DOUBLE", "MISC.FUNC.EVAL_DENOMINATOR_NOT_GROUPED", "MISC.FUNC.EVAL_RECIPROCAL_INVERTED",
                          "MISC.FUNC.EVAL_ROOT_IGNORED", "MISC.FUNC.EVAL_HALVE_INSTEAD_OF_ROOT", "MISC.FUNC.EVAL_NEGATIVE_ROOT"],
    "solve_for_input": ["MISC.FUNC.SOLVE_EVALUATES_INSTEAD", "MISC.FUNC.SOLVE_WRONG_INVERSE", "MISC.FUNC.SOLVE_STOPS_BEFORE_DIVIDING",
                        "MISC.FUNC.SOLVE_DIVIDE_BY_CONSTANT", "MISC.FUNC.SOLVE_RECIPROCAL_NOT_INVERTED", "MISC.FUNC.SOLVE_POLE_SIGN",
                        "MISC.FUNC.SOLVE_IGNORES_SHIFT", "MISC.FUNC.SOLVE_FORGOT_TO_SQUARE", "MISC.FUNC.SOLVE_SQUARE_BEFORE_ISOLATING"],
    "domain_of_function": ["MISC.FUNC.DOMAIN_ALL_REALS", "MISC.FUNC.DOMAIN_DIRECTION_FLIPPED", "MISC.FUNC.DOMAIN_STRICT_ENDPOINT",
                           "MISC.FUNC.DOMAIN_ENDPOINT_SIGN", "MISC.FUNC.DOMAIN_AS_EXCLUDED_POINT", "MISC.FUNC.DOMAIN_POLE_SIGN",
                           "MISC.FUNC.DOMAIN_EXCLUDES_ZERO", "MISC.FUNC.DOMAIN_POLE_AS_INEQUALITY", "MISC.FUNC.DOMAIN_NONNEGATIVE_ONLY",
                           "MISC.FUNC.DOMAIN_EXCLUDES_CONSTANT"],
    "range_of_function": ["MISC.FUNC.RANGE_DIRECTION_FLIPPED", "MISC.FUNC.RANGE_USES_VERTEX_X", "MISC.FUNC.RANGE_STRICT_AT_BOUND",
                          "MISC.FUNC.RANGE_USES_CONSTANT_TERM", "MISC.FUNC.RANGE_IGNORES_SHIFT", "MISC.FUNC.DOMAIN_RANGE_CONFUSED",
                          "MISC.FUNC.RANGE_POLE_AS_INEQUALITY", "MISC.FUNC.RANGE_ONLY_LOWER_BOUND", "MISC.FUNC.RANGE_STRICT_ENDPOINTS",
                          "MISC.FUNC.RANGE_ALL_REALS"],
    "composite_value": ["MISC.FUNC.COMP_ORDER_REVERSED", "MISC.FUNC.COMP_AS_PRODUCT", "MISC.FUNC.COMP_AS_SUM",
                        "MISC.FUNC.COMP_INNER_ONLY", "MISC.FUNC.COMP_OUTER_AT_INPUT"],
    "composite_expression": ["MISC.FUNC.COMP_ORDER_REVERSED", "MISC.FUNC.COMP_SQUARE_NO_CROSS_TERM", "MISC.FUNC.COMP_AS_PRODUCT",
                             "MISC.FUNC.COMP_AS_SUM"],
    "function_from_composite": ["MISC.FUNC.FFC_IGNORES_INNER", "MISC.FUNC.FFC_SHIFT_NOT_INVERTED", "MISC.FUNC.FFC_SCALE_NOT_INVERTED",
                                "MISC.FUNC.FFC_COMPOSES_INSTEAD"],
    "inverse_value": ["MISC.FUNC.INVVAL_FORWARD", "MISC.FUNC.INVVAL_RECIPROCAL", "MISC.FUNC.INVVAL_APPLIES_INVERSE_AGAIN",
                      "MISC.FUNC.INVVAL_IDENTITY", "MISC.FUNC.INV_UNDO_ORDER", "MISC.FUNC.INV_SIGN_ERROR"],
    "inverse_expression": ["MISC.FUNC.INV_AS_RECIPROCAL", "MISC.FUNC.INV_UNDO_ORDER", "MISC.FUNC.INV_SIGN_ERROR",
                           "MISC.FUNC.INV_NEGATES_ONLY", "MISC.FUNC.INV_SWAPS_ROLES"],
    "one_to_one_restriction": ["MISC.FUNC.VERTEX_X_MISSING_HALF", "MISC.FUNC.VERTEX_X_SIGN", "MISC.FUNC.VERTEX_Y_FOR_X",
                               "MISC.FUNC.RESTRICTION_ZERO", "MISC.FUNC.VERTEX_X_USES_C"],
}

STRUCTURAL_ONLY = ("MISC.FUNC.MANY_TO_ONE_REJECTED", "MISC.FUNC.CONSTANT_REJECTED", "MISC.FUNC.PATTERN_REQUIRED")


def rules_for(task: str) -> List[str]:
    return list(ELIGIBILITY.get(task, []))


def registry_records() -> List[Dict[str, Any]]:
    """Schema-shaped records (core/misconceptions/functions.json is generated from these)."""
    out = []
    for mid, m in MISCONCEPTIONS.items():
        out.append({
            "misconceptionId": mid,
            "domain": "functions",
            "title": m["title"],
            "description": m["description"],
            "observableError": m["observableError"],
            "distractorRule": {"summary": m["title"], "expression": m["expression"]},
            "validRange": {"levels": ["ibdp-aasl"]},
            "feedback": m["description"],
            "reviewStatus": "proposed",
            "version": "1.0.0",
        })
    return out
