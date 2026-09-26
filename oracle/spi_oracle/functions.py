"""gen.functions.foundations v1.0.0 — Introducing Functions (oracle reference implementation).

IB Mathematics: Analysis and Approaches SL, Oxford chapter 2 (ToC 2.1, 2.2, 2.4, 2.5, 2.6).
Eleven tasks: identify_function (MC only), evaluate_function, solve_for_input, domain_of_function,
range_of_function, composite_value, composite_expression, function_from_composite, inverse_value,
inverse_expression, one_to_one_restriction. Specification: docs/GENERATOR_SPEC_functions_PROPOSAL.md.

Exact arithmetic only (fractions.Fraction, Poly). The draw order in this module is NORMATIVE for the
cross-language parity contract: domains/functions/functions.ts reproduces it byte-for-byte (golden +
task-pinned parity fixtures). Registered pending-review: never in production until owner approval.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

import functions_core as C
import functions_misconceptions as FM
from difficulty import clamp01, round3
from expression_checker import check_expression
from interval_checker import check_interval, interval_display, interval_to_json
from polynomial import Poly, rat_display, rat_from_json, rat_json
from seeded_random import Mulberry32

GENERATOR_ID = "gen.functions.foundations"
GENERATOR_VERSION = "1.0.0"
VALIDATOR_VERSION = "1.0.0"
CALCULATOR_POLICY = "calculator-not-required"
MAX_PARAM_ATTEMPTS = 256

TASKS = (
    "identify_function", "evaluate_function", "solve_for_input", "domain_of_function", "range_of_function",
    "composite_value", "composite_expression", "function_from_composite", "inverse_value", "inverse_expression",
    "one_to_one_restriction",
)

OBJECTIVE_BY_TASK = {
    "identify_function": "SPI.IBDPAASL.FUNC.IDENTIFY_FUNCTION.01",
    "evaluate_function": "SPI.IBDPAASL.FUNC.EVALUATE.01",
    "solve_for_input": "SPI.IBDPAASL.FUNC.SOLVE_FOR_INPUT.01",
    "domain_of_function": "SPI.IBDPAASL.FUNC.DOMAIN.01",
    "range_of_function": "SPI.IBDPAASL.FUNC.RANGE.01",
    "composite_value": "SPI.IBDPAASL.FUNC.COMPOSITE_VALUE.01",
    "composite_expression": "SPI.IBDPAASL.FUNC.COMPOSITE_EXPRESSION.01",
    "function_from_composite": "SPI.IBDPAASL.FUNC.FUNCTION_FROM_COMPOSITE.01",
    "inverse_value": "SPI.IBDPAASL.FUNC.INVERSE_VALUE.01",
    "inverse_expression": "SPI.IBDPAASL.FUNC.INVERSE_EXPRESSION.01",
    "one_to_one_restriction": "SPI.IBDPAASL.FUNC.ONE_TO_ONE_RESTRICTION.01",
}

TASK_BANDS = {
    "identify_function": (1, 2), "evaluate_function": (1, 3), "solve_for_input": (2, 3), "domain_of_function": (2, 4),
    "range_of_function": (3, 5), "composite_value": (2, 3), "composite_expression": (3, 5),
    "function_from_composite": (4, 5), "inverse_value": (2, 4), "inverse_expression": (3, 4), "one_to_one_restriction": (4, 5),
}

# Answer families per task (the free-response answer.type; MC items keep the same mathematical type,
# except identify_function whose mathematics IS the selection).
ANSWER_FAMILY = {
    "identify_function": "choice", "evaluate_function": "number", "solve_for_input": "number",
    "domain_of_function": "interval", "range_of_function": "interval", "composite_value": "number",
    "composite_expression": "expression", "function_from_composite": "expression", "inverse_value": "number",
    "inverse_expression": "expression", "one_to_one_restriction": "number",
}
MC_ONLY_TASKS = ("identify_function",)
MC_ELIGIBLE_TASKS = TASKS  # every task supports multiple-choice

NAMES = ("f", "g", "h")
NZ5 = [x for x in range(-5, 6) if x != 0]
NZ6 = [x for x in range(-6, 7) if x != 0]
SMALL = [x for x in range(-3, 4) if x != 0]
MAX_NUM, MAX_DEN = 10000, 144

LABELS = ("A", "B", "C", "D", "E")


class InteractionNotSupported(ValueError):
    pass


def supported_interactions(task: str) -> List[str]:
    return ["multiple-choice"] if task in MC_ONLY_TASKS else ["free-response", "multiple-choice"]


def _resolve_interaction(task: str, config: Dict[str, Any]) -> str:
    """Forward key only. The legacy `answerType` selector is NOT consulted (ratio v1.0.2 precedent): a
    legacy sweep therefore exercises every task at its default interaction and never raises."""
    requested = config.get("interactionType")
    if requested is None:
        return "multiple-choice" if task in MC_ONLY_TASKS else "free-response"
    if requested not in ("free-response", "multiple-choice"):
        raise InteractionNotSupported(f"unsupported interaction {requested!r} for {task!r}")
    if requested not in supported_interactions(task):
        raise InteractionNotSupported(f"task {task!r} does not support {requested!r} (supported: {supported_interactions(task)})")
    return requested


# --------------------------------------------------------------------------- #
# Draws (the normative RNG order)
# --------------------------------------------------------------------------- #

def _pick_name(rng: Mulberry32) -> str:
    return rng.choice(NAMES)


def _distinct(rng: Mulberry32, n: int, lo: int, hi: int) -> List[int]:
    vals: List[int] = []
    while len(vals) < n:
        v = rng.next_int(lo, hi)
        if v not in vals:
            vals.append(v)
    return vals


def _collinear(pairs: List[List[int]]) -> bool:
    (x0, y0), (x1, y1) = pairs[0], pairs[1]
    for (x, y) in pairs[2:]:
        if (x1 - x0) * (y - y0) != (y1 - y0) * (x - x0):
            return False
    return True


def _draw_identify(rng: Mulberry32) -> Dict[str, Any]:
    neg = rng.next_int(0, 1) == 1
    lo, hi = (-4 if neg else 0), 9

    def out() -> int:
        return rng.next_int(-6, 9)

    # the non-function: three distinct inputs, one of them repeated with a different output
    ins = _distinct(rng, 3, lo, hi)
    r = rng.next_int(0, 2)
    outs = [out() for _ in range(3)]
    o4 = out()
    while o4 == outs[r]:
        o4 = out()
    adjacent = rng.next_int(0, 1) == 1
    non_function = [[ins[i], outs[i]] for i in range(3)]
    if adjacent:
        non_function.insert(r + 1, [ins[r], o4])
    else:
        non_function.append([ins[r], o4])
    separated = (not adjacent) and r != 2

    # D1: many-to-one (a repeated output, not all equal)
    i1 = _distinct(rng, 4, lo, hi)
    y = out()
    o1 = [out() for _ in range(4)]
    j = rng.next_int(1, 3)
    i = rng.next_int(0, j - 1)
    o1[i] = y
    o1[j] = y
    if all(v == y for v in o1):
        kk = next(t for t in range(4) if t not in (i, j))
        o1[kk] = y + 1
    many_to_one = [[i1[t], o1[t]] for t in range(4)]

    # D2: constant
    i2 = _distinct(rng, 4, lo, hi)
    y2 = out()
    constant = [[i2[t], y2] for t in range(4)]

    # D3: pattern-free (unsorted inputs, distinct outputs, not collinear)
    i3 = _distinct(rng, 4, lo, hi)
    if i3 == sorted(i3):
        i3[0], i3[1] = i3[1], i3[0]
    o3: List[int] = []
    while len(o3) < 4:
        v = out()
        if v not in o3:
            o3.append(v)
    pattern_free = [[i3[t], o3[t]] for t in range(4)]
    if _collinear(pattern_free):
        o3[3] += 1
        while o3[3] in o3[:3]:
            o3[3] += 1
        pattern_free = [[i3[t], o3[t]] for t in range(4)]

    return {"task": "identify_function", "nonFunction": non_function,
            "functions": [{"pairs": many_to_one, "misconceptionId": "MISC.FUNC.MANY_TO_ONE_REJECTED"},
                          {"pairs": constant, "misconceptionId": "MISC.FUNC.CONSTANT_REJECTED"},
                          {"pairs": pattern_free, "misconceptionId": "MISC.FUNC.PATTERN_REQUIRED"}],
            "negativeInputs": neg, "separatedRepeat": separated}


def _draw_linear(rng: Mulberry32, a_pool=NZ5, b_lo=-6, b_hi=6) -> Dict[str, Any]:
    return C.linear(rng.choice(a_pool), rng.next_int(b_lo, b_hi))


def _draw_quadratic(rng: Mulberry32, a_pool=(1, 1, 2, -1, -2, 3)) -> Dict[str, Any]:
    return C.quadratic(rng.choice(list(a_pool)), rng.next_int(-6, 6), rng.next_int(-9, 9))


def _draw_evaluate(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    kind = rng.choice(["linear", "quadratic", "reciprocal", "sqrt"])
    name = _pick_name(rng)
    p = Fraction(rng.next_int(-6, 6))
    if kind == "linear":
        rule = C.linear(rng.choice(NZ5), rng.next_int(-9, 9))
    elif kind == "quadratic":
        rule = _draw_quadratic(rng)
    elif kind == "reciprocal":
        rule = C.reciprocal(rng.choice(NZ6), rng.next_int(-5, 5), rng.next_int(-4, 4))
        if p == rule["h"]:
            return None
    else:
        t = rng.next_int(0, 6)
        a = rng.choice(SMALL)
        v = rng.next_int(-4, 4)
        rule = C.sqrt_rule(a, t * t - a * p, v)
    return {"task": "evaluate_function", "name": name, "rule": rule, "p": p}


def _draw_solve(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    kind = rng.choice(["linear", "linear", "reciprocal", "sqrt"])
    name = _pick_name(rng)
    if kind == "linear":
        frac = rng.next_int(0, 3) == 0
        if frac:
            d = rng.choice([2, 3])
            n = rng.choice([x for x in range(-9, 10) if x % d != 0])
            x0 = Fraction(n, d)
            a = Fraction(d * rng.choice([1, -1, 2, -2]))
        else:
            x0 = Fraction(rng.next_int(-8, 8))
            a = Fraction(rng.choice(NZ5))
        b = Fraction(rng.next_int(-9, 9))
        rule = C.linear(a, b)
        target = a * x0 + b
    elif kind == "reciprocal":
        k0 = rng.choice(NZ6)
        h = rng.next_int(-5, 5)
        v = rng.next_int(-4, 4)
        divs = [d for d in range(-6, 7) if d != 0 and k0 % d == 0]
        d = rng.choice(divs)
        x0 = Fraction(h + d)
        rule = C.reciprocal(k0, h, v)
        target = Fraction(k0, d) + v
    else:
        t = rng.next_int(0, 6)
        x0 = Fraction(rng.next_int(-6, 6))
        a = rng.choice(SMALL)
        v = rng.next_int(-4, 4)
        rule = C.sqrt_rule(a, t * t - a * x0, v)
        target = Fraction(t + v)
    return {"task": "solve_for_input", "name": name, "rule": rule, "target": target, "x0": x0}


def _draw_domain(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    kind = rng.choice(["sqrt", "sqrt", "reciprocal", "reciprocal", "linear", "quadratic"])
    name = _pick_name(rng)
    if kind == "sqrt":
        rule = C.sqrt_rule(rng.choice(NZ5), rng.next_int(-6, 6), rng.next_int(-3, 3))
    elif kind == "reciprocal":
        rule = C.reciprocal(rng.choice(NZ6), rng.next_int(-6, 6), rng.next_int(-4, 4))
    elif kind == "linear":
        rule = C.linear(rng.choice(NZ5), rng.choice(NZ6))
    else:
        rule = C.quadratic(rng.choice([1, -1, 2]), rng.next_int(-6, 6), rng.choice(NZ6))
    return {"task": "domain_of_function", "name": name, "rule": rule}


def _draw_range(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    kind = rng.choice(["quadratic", "quadratic", "sqrt", "reciprocal", "linear_restricted"])
    name = _pick_name(rng)
    if kind == "quadratic":
        rule = C.quadratic(rng.choice([1, 1, 2, -1, -2, 3, -3]), rng.next_int(-6, 6), rng.next_int(-6, 6))
        return {"task": "range_of_function", "name": name, "rule": rule}
    if kind == "sqrt":
        rule = C.sqrt_rule(rng.choice(NZ5), rng.next_int(-6, 6), rng.next_int(-6, 6))
        return {"task": "range_of_function", "name": name, "rule": rule}
    if kind == "reciprocal":
        rule = C.reciprocal(rng.choice(NZ6), rng.next_int(-6, 6), rng.next_int(-6, 6))
        return {"task": "range_of_function", "name": name, "rule": rule}
    rule = C.linear(rng.choice(NZ5), rng.next_int(-6, 6))
    p = rng.next_int(-5, 4)
    q = rng.next_int(p + 1, 5)
    return {"task": "range_of_function", "name": name, "rule": rule, "restricted": {"p": Fraction(p), "q": Fraction(q)}}


def _draw_poly_rule(rng: Mulberry32, kind: str) -> Dict[str, Any]:
    if kind == "linear":
        return C.linear(rng.choice(NZ5), rng.next_int(-6, 6))
    return C.quadratic(rng.choice([1, 1, -1, 2]), rng.next_int(-3, 3), rng.next_int(-6, 6))


def _draw_composite_value(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    fk = rng.choice(["linear", "quadratic"])
    gk = rng.choice(["linear", "quadratic"])
    f = _draw_poly_rule(rng, fk)
    g = _draw_poly_rule(rng, gk)
    order = rng.choice(["fg", "gf"])
    p = Fraction(rng.next_int(-5, 5))
    return {"task": "composite_value", "f": f, "g": g, "order": order, "p": p}


def _draw_composite_expression(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    quad_slot = rng.choice(["none", "outer", "inner"])
    order = rng.choice(["fg", "gf"])
    outer_kind = "quadratic" if quad_slot == "outer" else "linear"
    inner_kind = "quadratic" if quad_slot == "inner" else "linear"
    fk, gk = (outer_kind, inner_kind) if order == "fg" else (inner_kind, outer_kind)
    f = _draw_poly_rule(rng, fk)
    g = _draw_poly_rule(rng, gk)
    return {"task": "composite_expression", "f": f, "g": g, "order": order}


def _draw_function_from_composite(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    A = Fraction(rng.choice(NZ5))
    B = Fraction(rng.next_int(-6, 6))
    m = Fraction(rng.choice([1, 1, 2, -1]))
    c = Fraction(rng.choice(NZ6))
    return {"task": "function_from_composite", "A": A, "B": B, "m": m, "c": c}


def _draw_inverse_value(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    form = rng.choice(["inverse_at", "solve_inverse_equation"])
    name = _pick_name(rng)
    a = Fraction(rng.choice(NZ5))
    b = Fraction(rng.next_int(-6, 6))
    x0 = Fraction(rng.next_int(-6, 6))
    if form == "inverse_at":
        mode = rng.next_int(0, 2)
        k = Fraction(rng.next_int(-9, 9)) if mode == 0 else a * x0 + b
        return {"task": "inverse_value", "name": name, "a": a, "b": b, "form": form, "k": k}
    return {"task": "inverse_value", "name": name, "a": a, "b": b, "form": form, "x0": x0}


def _draw_inverse_expression(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    name = _pick_name(rng)
    frac = rng.next_int(0, 3) == 0
    a = rng.choice([Fraction(1, 2), Fraction(-1, 2), Fraction(1, 3)]) if frac else Fraction(rng.choice(NZ5))
    b = Fraction(rng.next_int(-6, 6))
    return {"task": "inverse_expression", "name": name, "a": a, "b": b}


def _draw_one_to_one(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    name = _pick_name(rng)
    rule = C.quadratic(rng.choice([1, 1, -1, 2, -2, 3]), rng.choice(NZ6), rng.next_int(-6, 6))
    side = rng.choice(["ge", "le"])
    return {"task": "one_to_one_restriction", "name": name, "rule": rule, "side": side}


_DRAW = {
    "identify_function": _draw_identify, "evaluate_function": _draw_evaluate, "solve_for_input": _draw_solve,
    "domain_of_function": _draw_domain, "range_of_function": _draw_range, "composite_value": _draw_composite_value,
    "composite_expression": _draw_composite_expression, "function_from_composite": _draw_function_from_composite,
    "inverse_value": _draw_inverse_value, "inverse_expression": _draw_inverse_expression,
    "one_to_one_restriction": _draw_one_to_one,
}


# --------------------------------------------------------------------------- #
# Params encoding (public JSON <-> internal exact)
# --------------------------------------------------------------------------- #

_RAT_KEYS = ("p", "target", "x0", "A", "B", "m", "c", "a", "b", "k")


def _public_params(params: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, val in params.items():
        if key in ("rule", "f", "g"):
            out[key] = C.rule_to_json(val)
        elif key == "restricted":
            out[key] = {"p": rat_json(val["p"]), "q": rat_json(val["q"])}
        elif key in _RAT_KEYS:
            out[key] = rat_json(val)
        else:
            out[key] = val
    return out


def _internal_params(pub: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, val in pub.items():
        if key in ("rule", "f", "g"):
            out[key] = C.rule_from_json(val)
        elif key == "restricted":
            out[key] = {"p": rat_from_json(val["p"]), "q": rat_from_json(val["q"])}
        elif key in _RAT_KEYS:
            out[key] = rat_from_json(val)
        else:
            out[key] = val
    return out


def _outer_inner(params: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], str, str]:
    if params["order"] == "fg":
        return params["f"], params["g"], "f", "g"
    return params["g"], params["f"], "g", "f"


# --------------------------------------------------------------------------- #
# Guards
# --------------------------------------------------------------------------- #

def _within_caps(x: Fraction) -> bool:
    return abs(x.numerator) <= MAX_NUM and x.denominator <= MAX_DEN


def _pairs_display(pairs: List[List[int]]) -> str:
    return "{" + ", ".join(f"({x}, {y})" for x, y in pairs) + "}"


def _acceptable(task: str, params: Dict[str, Any]) -> bool:
    if task == "identify_function":
        displays = [_pairs_display(params["nonFunction"])] + [_pairs_display(f["pairs"]) for f in params["functions"]]
        return len(set(displays)) == 4
    if task == "evaluate_function":
        v = C.eval_rule(params["rule"], params["p"])
        return v is not None and _within_caps(v)
    if task == "solve_for_input":
        return _within_caps(params["target"]) and _within_caps(params["x0"]) and params["target"] != params["rule"].get("v", None)
    if task in ("composite_value",):
        outer, inner, _, _ = _outer_inner(params)
        return _within_caps(C.rule_poly(outer).eval(C.rule_poly(inner).eval(params["p"])))
    if task == "composite_expression":
        outer, inner, _, _ = _outer_inner(params)
        return C.rule_poly(outer).compose(C.rule_poly(inner)).degree() <= 2
    return True


# --------------------------------------------------------------------------- #
# Answers
# --------------------------------------------------------------------------- #

def _solve(task: str, params: Dict[str, Any]) -> Any:
    """The canonical answer value (Fraction | Poly | descriptor); identify_function is resolved at assembly."""
    if task == "evaluate_function":
        return C.eval_rule(params["rule"], params["p"])
    if task == "solve_for_input":
        r, k = params["rule"], params["target"]
        if r["kind"] == "linear":
            return (k - r["b"]) / r["a"]
        if r["kind"] == "reciprocal":
            return r["h"] + r["k"] / (k - r["v"])
        t = k - r["v"]
        return (t * t - r["b"]) / r["a"]
    if task == "domain_of_function":
        return C.domain_of(params["rule"])
    if task == "range_of_function":
        return C.range_of(params["rule"], params.get("restricted"))
    if task == "composite_value":
        outer, inner, _, _ = _outer_inner(params)
        return C.eval_rule(outer, C.eval_rule(inner, params["p"]))
    if task == "composite_expression":
        outer, inner, _, _ = _outer_inner(params)
        return C.rule_poly(outer).compose(C.rule_poly(inner))
    if task == "function_from_composite":
        return Poly.linear(params["A"], params["B"])
    if task == "inverse_value":
        a, b = params["a"], params["b"]
        if params["form"] == "inverse_at":
            return (params["k"] - b) / a
        return a * params["x0"] + b
    if task == "inverse_expression":
        a, b = params["a"], params["b"]
        return Poly.linear(1 / a, -b / a)
    if task == "one_to_one_restriction":
        return C.vertex_x(params["rule"])
    raise ValueError(task)


def _terminates(den: int) -> bool:
    while den % 2 == 0:
        den //= 2
    while den % 5 == 0:
        den //= 5
    return den == 1


def _value_display(v: Any) -> str:
    if isinstance(v, Fraction):
        return rat_display(v)
    if isinstance(v, Poly):
        return v.display()
    if isinstance(v, dict) and v.get("kind") == "reciprocal-of":
        return f"1/({v['poly'].display()})"
    return interval_display(interval_to_json(v))


def _value_json(v: Any) -> Any:
    if isinstance(v, Fraction):
        return rat_json(v)
    if isinstance(v, Poly):
        return v.to_json()
    if isinstance(v, dict) and v.get("kind") == "reciprocal-of":
        return {"kind": "reciprocal-of", "coefficients": v["poly"].to_json()["coefficients"]}
    return interval_to_json(v)


def _encode_answer(task: str, value: Any) -> Dict[str, Any]:
    fam = ANSWER_FAMILY[task]
    if fam == "number":
        return {"type": "integer" if value.denominator == 1 else "exact-rational", "canonical": rat_json(value),
                "display": rat_display(value), "accepts": {"fraction": True, "decimal": _terminates(value.denominator), "mixed": False}}
    if fam == "expression":
        return {"type": "algebraic-expression", "canonical": value.to_json(), "display": value.display()}
    return {"type": "interval", "canonical": interval_to_json(value), "display": interval_display(interval_to_json(value))}


# --------------------------------------------------------------------------- #
# Misconception context + MC distractors
# --------------------------------------------------------------------------- #

def _ctx(task: str, params: Dict[str, Any]) -> FM.Ctx:
    ctx: FM.Ctx = {"task": task}
    ctx.update({k: v for k, v in params.items() if k != "task"})
    if task in ("composite_value", "composite_expression"):
        outer, inner, on, inn = _outer_inner(params)
        ctx.update({"outer": outer, "inner": inner, "outer_name": on, "inner_name": inn, "p": params.get("p")})
    if task == "function_from_composite":
        ctx["comp_p"] = params["A"] * params["m"]
        ctx["comp_q"] = params["A"] * params["c"] + params["B"]
    if task == "inverse_value" and "x0" not in ctx:
        ctx["x0"] = None
    return ctx


def _mc_distractors(task: str, params: Dict[str, Any], rng: Mulberry32) -> Optional[List[Dict[str, Any]]]:
    """Three distinct misconception-backed distractors. The eligibility list is rotated by ONE seeded draw
    so that every eligible pathway is exercised across items (a fixed order would starve the later rules
    whenever the first three always apply) and distractor sets vary between items."""
    answer_key = _value_display(_solve(task, params))
    ctx = _ctx(task, params)
    seen = {answer_key}
    chosen: List[Dict[str, Any]] = []
    rules = FM.rules_for(task)
    offset = rng.next_int(0, len(rules) - 1)
    rules = rules[offset:] + rules[:offset]
    for mid in rules:
        w = FM.MISCONCEPTIONS[mid]["wrong"](ctx)
        if w is None:
            continue
        if isinstance(w, Fraction) and not _within_caps(w):
            continue
        key = _value_display(w)
        if key in seen:
            continue
        seen.add(key)
        chosen.append({"value": w, "misconceptionId": mid, "rationale": FM.MISCONCEPTIONS[mid]["observableError"]})
        if len(chosen) == 3:
            break
    return chosen if len(chosen) == 3 else None


def _assemble_mc(rng: Mulberry32, correct_value: Any, distractors: List[Dict[str, Any]], encode) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Mirror of core/sdk/multiple-choice.ts assembleMultipleChoice (one shuffle of the option pool)."""
    records = []
    for i, d in enumerate(distractors):
        e = encode(d["value"])
        records.append({"id": f"d{i + 1}", "value": e["value"], "display": e["display"],
                        "misconceptionId": d["misconceptionId"], "rationale": d["rationale"]})
    pool = [{"value": correct_value, "correct": True, "misconceptionId": None}]
    for d in distractors:
        pool.append({"value": d["value"], "correct": False, "misconceptionId": d["misconceptionId"]})
    shuffled = rng.shuffle(pool)
    options = []
    for i, o in enumerate(shuffled):
        e = encode(o["value"])
        opt = {"label": LABELS[i], "value": e["value"], "display": e["display"], "correct": o["correct"]}
        if o["misconceptionId"]:
            opt["misconceptionId"] = o["misconceptionId"]
        options.append(opt)
    return records, options


# --------------------------------------------------------------------------- #
# Prompts + spoken text
# --------------------------------------------------------------------------- #

def _defined_by(name: str, rule: Dict[str, Any], suffix: str = "") -> List[Dict[str, Any]]:
    return [{"kind": "text", "text": f"The function {name} is defined by"},
            {"kind": "math", "latex": f"{name}(x) = {C.rule_latex(rule)}{suffix}"}]


def _two_functions(f: Dict[str, Any], g: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"kind": "text", "text": "The functions f and g are defined by"},
            {"kind": "math", "latex": f"f(x) = {C.rule_latex(f)}, \\qquad g(x) = {C.rule_latex(g)}"}]


def _prompt(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    n = params.get("name", "f")
    if task == "identify_function":
        return {"instruction": "Identify",
                "blocks": [{"kind": "text", "text": "Exactly one of the following relations is not a function. Which one?"}]}
    if task == "evaluate_function":
        return {"instruction": "Evaluate", "blocks": _defined_by(n, params["rule"]) +
                [{"kind": "text", "text": f"Find the value of {n}({rat_display(params['p'])})."}]}
    if task == "solve_for_input":
        return {"instruction": "Solve", "blocks": _defined_by(n, params["rule"]) +
                [{"kind": "text", "text": f"Find the value of x for which {n}(x) = {rat_display(params['target'])}."}]}
    if task == "domain_of_function":
        return {"instruction": "State the domain", "blocks": _defined_by(n, params["rule"]) +
                [{"kind": "text", "text": f"State the largest possible domain of {n}."}]}
    if task == "range_of_function":
        suffix = ""
        if "restricted" in params:
            suffix = f", \\quad {C.latex_rat(params['restricted']['p'])} \\leq x \\leq {C.latex_rat(params['restricted']['q'])}"
        return {"instruction": "State the range", "blocks": _defined_by(n, params["rule"], suffix) +
                [{"kind": "text", "text": f"State the range of {n}."}]}
    if task == "composite_value":
        _, _, on, inn = _outer_inner(params)
        return {"instruction": "Evaluate", "blocks": _two_functions(params["f"], params["g"]) +
                [{"kind": "text", "text": "Find the value of"},
                 {"kind": "math", "latex": f"({on} \\circ {inn})({C.latex_rat(params['p'])})"}]}
    if task == "composite_expression":
        _, _, on, inn = _outer_inner(params)
        return {"instruction": "Find the composite", "blocks": _two_functions(params["f"], params["g"]) +
                [{"kind": "text", "text": "Find an expression for"},
                 {"kind": "math", "latex": f"({on} \\circ {inn})(x)"},
                 {"kind": "text", "text": "Expand and simplify your answer."}]}
    if task == "function_from_composite":
        g = C.linear(params["m"], params["c"])
        comp = Poly.linear(params["A"] * params["m"], params["A"] * params["c"] + params["B"])
        return {"instruction": "Find the outer function",
                "blocks": [{"kind": "text", "text": "The functions f and g are defined by"},
                           {"kind": "math", "latex": f"g(x) = {C.rule_latex(g)}, \\qquad (f \\circ g)(x) = {C.latex_poly(comp)}"},
                           {"kind": "text", "text": "Find an expression for f(x)."}]}
    if task == "inverse_value":
        rule = C.linear(params["a"], params["b"])
        if params["form"] == "inverse_at":
            return {"instruction": "Evaluate the inverse", "blocks": _defined_by(n, rule) +
                    [{"kind": "text", "text": "Find the value of"},
                     {"kind": "math", "latex": f"{n}^{{-1}}({C.latex_rat(params['k'])})"}]}
        return {"instruction": "Solve", "blocks": _defined_by(n, rule) +
                [{"kind": "text", "text": "Find the value of k for which"},
                 {"kind": "math", "latex": f"{n}^{{-1}}(k) = {C.latex_rat(params['x0'])}"}]}
    if task == "inverse_expression":
        rule = C.linear(params["a"], params["b"])
        return {"instruction": "Find the inverse", "blocks": _defined_by(n, rule) +
                [{"kind": "text", "text": "Find an expression for"},
                 {"kind": "math", "latex": f"{n}^{{-1}}(x)"}]}
    side = params["side"]
    word = "least" if side == "ge" else "greatest"
    cmp_latex = "\\geq" if side == "ge" else "\\leq"
    return {"instruction": "Find the restriction",
            "blocks": _defined_by(n, params["rule"], f", \\quad x {cmp_latex} k") +
            [{"kind": "text", "text": f"The domain of {n} is restricted so that the inverse function {n}^-1 exists. "
                                       f"Find the {word} possible value of k."}]}


def _spoken(task: str, params: Dict[str, Any], options: Optional[List[Dict[str, Any]]] = None) -> str:
    n = params.get("name", "f")
    if task == "identify_function":
        parts = []
        for o in options or []:
            pairs = "; ".join(f"({x}, {y})" for x, y in o["value"])
            parts.append(f"Option {o['label']}: the ordered pairs {pairs}.")
        return "Exactly one of the following relations is not a function. Which one? " + " ".join(parts)
    if task in ("evaluate_function", "solve_for_input", "domain_of_function", "range_of_function", "one_to_one_restriction"):
        r = params["rule"]
        head = f"The function {n} is defined by {n}(x) = {C.rule_text(r)}"
        if task == "evaluate_function":
            return f"{head}. Find the value of {n}({rat_display(params['p'])})."
        if task == "solve_for_input":
            return f"{head}. Find the value of x for which {n}(x) = {rat_display(params['target'])}."
        if task == "domain_of_function":
            return f"{head}. State the largest possible domain of {n}."
        if task == "range_of_function":
            if "restricted" in params:
                head += f", for {rat_display(params['restricted']['p'])} <= x <= {rat_display(params['restricted']['q'])}"
            return f"{head}. State the range of {n}."
        word = "least" if params["side"] == "ge" else "greatest"
        cmp = ">=" if params["side"] == "ge" else "<="
        return (f"{head}, for x {cmp} k. The domain of {n} is restricted so that the inverse function {n}^-1 exists. "
                f"Find the {word} possible value of k.")
    if task in ("composite_value", "composite_expression"):
        _, _, on, inn = _outer_inner(params)
        head = f"The functions f and g are defined by f(x) = {C.rule_text(params['f'])} and g(x) = {C.rule_text(params['g'])}."
        if task == "composite_value":
            return f"{head} Find the value of ({on} o {inn})({rat_display(params['p'])}), that is {on} of {inn} of {rat_display(params['p'])}."
        return f"{head} Find an expression for ({on} o {inn})(x), that is {on} of {inn} of x. Expand and simplify your answer."
    if task == "function_from_composite":
        g = C.linear(params["m"], params["c"])
        comp = Poly.linear(params["A"] * params["m"], params["A"] * params["c"] + params["B"])
        return (f"The functions f and g are defined by g(x) = {C.rule_text(g)} and (f o g)(x) = {comp.display()}. "
                f"Find an expression for f(x).")
    rule = C.linear(params["a"], params["b"])
    head = f"The function {n} is defined by {n}(x) = {C.rule_text(rule)}."
    if task == "inverse_value":
        if params["form"] == "inverse_at":
            return f"{head} Find the value of {n} inverse of {rat_display(params['k'])}."
        return f"{head} Find the value of k for which {n} inverse of k equals {rat_display(params['x0'])}."
    return f"{head} Find an expression for {n} inverse of x."


# --------------------------------------------------------------------------- #
# Worked solutions
# --------------------------------------------------------------------------- #

def _sum_text(terms: List[Fraction]) -> str:
    out = ""
    for i, t in enumerate(terms):
        if i == 0:
            out = rat_display(t)
        else:
            out += (" - " if t < 0 else " + ") + rat_display(abs(t))
    return out


def _bracket(x: Fraction) -> str:
    return f"({rat_display(x)})" if x < 0 else rat_display(x)


def _coef_times(a: Fraction, operand: str) -> str:
    """a·operand with ±1 implicit and the operand bracketed after a coefficient: 5, -5, 2(5), 2(-3), (1/2)(5)."""
    if a == 1:
        return operand
    if a == -1:
        return "-" + operand
    wrapped = operand if operand.startswith("(") else f"({operand})"
    return (f"({rat_display(a)})" if a.denominator != 1 else rat_display(a)) + wrapped


def _substituted(rule: Dict[str, Any], p: Fraction) -> str:
    k = rule["kind"]
    bp = _bracket(p)
    if k == "linear":
        return _coef_times(rule["a"], bp) + C._shift_text(rule["b"])
    if k == "quadratic":
        s = _coef_times(rule["a"], f"{bp}^2")
        if rule["b"] != 0:
            s += (" - " if rule["b"] < 0 else " + ") + _coef_times(abs(rule["b"]), bp)
        return s + C._shift_text(rule["c"])
    if k == "reciprocal":
        den = f"({bp} - {rat_display(rule['h'])})" if rule["h"] > 0 else (f"({bp} + {rat_display(-rule['h'])})" if rule["h"] < 0 else bp)
        return f"{rat_display(rule['k'])}/{den}" + C._shift_text(rule["v"])
    return "sqrt(" + _coef_times(rule["a"], bp) + C._shift_text(rule["b"]) + ")" + C._shift_text(rule["v"])


class _Steps:
    def __init__(self) -> None:
        self.steps: List[Dict[str, Any]] = []
        self.prev: Optional[int] = None

    def add(self, transformation: str, intermediate: Optional[str] = None, rule: Optional[str] = None,
            explanation: Optional[str] = None, marks: Optional[int] = None, depends: bool = True) -> None:
        n = len(self.steps) + 1
        st: Dict[str, Any] = {"number": n, "transformation": transformation}
        if rule is not None:
            st["ruleOrTheorem"] = rule
        if intermediate is not None:
            st["intermediateResult"] = intermediate
        if explanation is not None:
            st["explanation"] = explanation
        if depends and self.prev is not None:
            st["dependsOn"] = [self.prev]
        if marks is not None:
            st["marks"] = marks
        self.steps.append(st)
        self.prev = n


def _solution(task: str, params: Dict[str, Any], answer_display: str, options: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    S = _Steps()
    n = params.get("name", "f")
    if task == "identify_function":
        S.add("List the inputs of each relation", explanation="A relation is a function when no input is paired with two different outputs.")
        pairs = params["nonFunction"]
        seen: Dict[int, int] = {}
        rep = None
        for x, y in pairs:
            if x in seen and seen[x] != y:
                rep = (x, seen[x], y)
                break
            seen.setdefault(x, y)
        label = next(o["label"] for o in (options or []) if o["correct"])
        S.add("Find the relation with a repeated input and two different outputs",
              intermediate=f"Relation {label}: the input {rep[0]} is paired with both {rep[1]} and {rep[2]}")
        S.add("State the relation that is not a function", intermediate=label, marks=1)
        return {"steps": S.steps}
    if task == "evaluate_function":
        r, p = params["rule"], params["p"]
        S.add(f"Substitute x = {rat_display(p)} into the rule", intermediate=f"{n}({rat_display(p)}) = {_substituted(r, p)}",
              explanation="Replace every x by the input, keeping a negative input in brackets.")
        if r["kind"] == "linear":
            S.add("Multiply, then add the constant", intermediate=f"= {_sum_text([r['a'] * p, r['b']] if r['b'] != 0 else [r['a'] * p])}")
        elif r["kind"] == "quadratic":
            S.add("Square first, then multiply and add", intermediate=f"= {_sum_text([r['a'] * p * p, r['b'] * p, r['c']])}")
        elif r["kind"] == "reciprocal":
            S.add("Evaluate the denominator, then divide", intermediate=f"= {rat_display(r['k'])}/{_bracket(p - r['h'])}" + C._shift_text(r["v"]))
        else:
            rad = C.radicand(r, p)
            S.add("Evaluate the radicand, then take the square root", intermediate=f"= sqrt({rat_display(rad)})" + C._shift_text(r["v"])
                  + f" = {rat_display(C.sqrt_exact(rad))}" + C._shift_text(r["v"]))
        S.add("State the value", intermediate=f"{n}({rat_display(p)}) = {answer_display}", marks=1)
        return {"steps": S.steps}
    if task == "solve_for_input":
        r, k, x0 = params["rule"], params["target"], params["x0"]
        S.add("Set up the equation", intermediate=f"{C.rule_text(r)} = {rat_display(k)}", explanation=f"{n}(x) = {rat_display(k)} means the rule equals {rat_display(k)}.")
        if r["kind"] == "linear":
            if r["b"] != 0:
                S.add(f"{'Subtract' if r['b'] > 0 else 'Add'} {rat_display(abs(r['b']))} {'from' if r['b'] > 0 else 'to'} both sides",
                      intermediate=f"{C.rule_text(C.linear(r['a'], 0))} = {rat_display(k - r['b'])}")
            if r["a"] != 1:
                S.add(f"Divide both sides by {rat_display(r['a'])}", intermediate=f"x = {rat_display(x0)}")
        elif r["kind"] == "reciprocal":
            den = C._denominator_text(r["h"])
            if r["v"] != 0:
                S.add(f"{'Subtract' if r['v'] > 0 else 'Add'} {rat_display(abs(r['v']))} {'from' if r['v'] > 0 else 'to'} both sides",
                      intermediate=f"{rat_display(r['k'])}/({den}) = {rat_display(k - r['v'])}")
            S.add("Multiply both sides by the denominator and divide by the value",
                  intermediate=f"{den} = {rat_display(r['k'] / (k - r['v']))}", explanation="The denominator equals the numerator divided by the value of the fraction.")
            if r["h"] != 0:
                S.add(f"{'Add' if r['h'] > 0 else 'Subtract'} {rat_display(abs(r['h']))} {'to' if r['h'] > 0 else 'from'} both sides", intermediate=f"x = {rat_display(x0)}")
        else:
            t = k - r["v"]
            if r["v"] != 0:
                S.add(f"{'Subtract' if r['v'] > 0 else 'Add'} {rat_display(abs(r['v']))} {'from' if r['v'] > 0 else 'to'} both sides to isolate the root",
                      intermediate=f"sqrt({C.radicand_text(r)}) = {rat_display(t)}")
            S.add("Square both sides", intermediate=f"{C.radicand_text(r)} = {rat_display(t * t)}", explanation="Squaring undoes the square root once it is isolated.")
            S.add("Solve the linear equation", intermediate=f"x = {rat_display(x0)}")
        S.add("State the solution", intermediate=f"x = {answer_display}", marks=1)
        S.add("Verify by substitution", intermediate=f"{n}({rat_display(x0)}) = {rat_display(k)}", explanation="The rule returns the required output, confirming the solution.")
        return {"steps": S.steps}
    if task == "domain_of_function":
        r = params["rule"]
        if r["kind"] == "sqrt":
            S.add("Identify the restriction", intermediate=f"{C.radicand_text(r)} >= 0", rule="A square root is defined only for a non-negative radicand.")
            expl = "Dividing both sides by a negative number reverses the inequality." if r["a"] < 0 else None
            S.add("Solve the inequality", intermediate=answer_display, explanation=expl)
        elif r["kind"] == "reciprocal":
            S.add("Identify the restriction", intermediate=f"{C._denominator_text(r['h'])} != 0", rule="A fraction is undefined when its denominator is zero.")
            S.add("Solve for the excluded input", intermediate=answer_display)
        else:
            S.add("Identify the restriction", intermediate="none", rule="A polynomial can be evaluated at every real number.")
        S.add("State the domain", intermediate=answer_display, marks=1)
        return {"steps": S.steps}
    if task == "range_of_function":
        r = params["rule"]
        if r["kind"] == "quadratic":
            hx, hy = C.vertex_x(r), C.vertex_y(r)
            S.add("Find the axis of symmetry", intermediate=f"x = -({rat_display(r['b'])})/(2({rat_display(r['a'])})) = {rat_display(hx)}", rule="x = -b/(2a)")
            S.add("Find the value at the vertex", intermediate=f"{n}({rat_display(hx)}) = {rat_display(hy)}")
            S.add("Determine the direction of opening",
                  intermediate=f"a = {rat_display(r['a'])} {'> 0, so the vertex is a minimum' if r['a'] > 0 else '< 0, so the vertex is a maximum'}")
        elif r["kind"] == "sqrt":
            S.add("Start from the base range", intermediate=f"sqrt({C.radicand_text(r)}) >= 0", rule="A square root is never negative and equals 0 at the domain endpoint.")
            S.add("Apply the vertical shift", intermediate=f"{n}(x) >= {rat_display(r['v'])}")
        elif r["kind"] == "reciprocal":
            S.add("Start from the base range", intermediate=f"{rat_display(r['k'])}/({C._denominator_text(r['h'])}) != 0",
                  rule="A fraction with a non-zero constant numerator is never zero but takes every other value.")
            S.add("Apply the vertical shift", intermediate=f"{n}(x) != {rat_display(r['v'])}")
        else:
            p, q = params["restricted"]["p"], params["restricted"]["q"]
            fp, fq = C.eval_rule(r, p), C.eval_rule(r, q)
            S.add("Evaluate at the endpoints of the domain", intermediate=f"{n}({rat_display(p)}) = {rat_display(fp)}, {n}({rat_display(q)}) = {rat_display(fq)}",
                  rule="A linear function is monotonic, so its extreme values occur at the endpoints.")
            S.add("Order the images", intermediate=f"{rat_display(min(fp, fq))} <= y <= {rat_display(max(fp, fq))}")
        S.add("State the range", intermediate=answer_display, marks=1)
        return {"steps": S.steps}
    if task == "composite_value":
        outer, inner, on, inn = _outer_inner(params)
        p = params["p"]
        gv = C.eval_rule(inner, p)
        S.add(f"Evaluate the inner function {inn} at {rat_display(p)}", intermediate=f"{inn}({rat_display(p)}) = {rat_display(gv)}",
              explanation=f"({on} o {inn})(x) = {on}({inn}(x)): the inner function is applied first.")
        S.add(f"Evaluate the outer function {on} at {rat_display(gv)}", intermediate=f"{on}({rat_display(gv)}) = {answer_display}")
        S.add("State the value", intermediate=f"({on} o {inn})({rat_display(p)}) = {answer_display}", marks=1)
        return {"steps": S.steps}
    if task == "composite_expression":
        outer, inner, on, inn = _outer_inner(params)
        S.add(f"Substitute {inn}(x) into {on}", intermediate=f"{on}({inn}(x)) = {_substituted_expr(outer, inner)}",
              explanation=f"Replace every x in {on}(x) by the whole expression {inn}(x).")
        S.add("Expand and collect like terms", intermediate=f"= {answer_display}")
        S.add("State the composite", intermediate=f"({on} o {inn})(x) = {answer_display}", marks=1)
        return {"steps": S.steps}
    if task == "function_from_composite":
        m, c, A, B = params["m"], params["c"], params["A"], params["B"]
        comp = Poly.linear(A * m, A * c + B)
        g = C.linear(m, c)
        S.add("Write f(g(x)) equal to the given composite", intermediate=f"f({C.rule_text(g)}) = {comp.display()}")
        S.add("Let u = g(x) and express x in terms of u", intermediate=f"x = {Poly.linear(1 / m, -c / m).display('u')}",
              explanation="Undo the inner function to change the variable.")
        S.add("Substitute and simplify", intermediate=f"f(u) = {Poly.linear(A, B).display('u')}")
        S.add("State the outer function", intermediate=f"f(x) = {answer_display}", marks=1)
        return {"steps": S.steps}
    if task == "inverse_value":
        a, b = params["a"], params["b"]
        rule = C.linear(a, b)
        if params["form"] == "inverse_at":
            k = params["k"]
            S.add(f"Let {n}^-1({rat_display(k)}) = x, so {n}(x) = {rat_display(k)}", intermediate=f"{C.rule_text(rule)} = {rat_display(k)}",
                  explanation="The inverse function reverses the input and output.")
            S.add("Solve for x", intermediate=f"x = {answer_display}")
            S.add("State the value", intermediate=f"{n}^-1({rat_display(k)}) = {answer_display}", marks=1)
        else:
            x0 = params["x0"]
            S.add(f"Rewrite {n}^-1(k) = {rat_display(x0)} as k = {n}({rat_display(x0)})", explanation="The inverse function reverses the input and output.")
            S.add(f"Evaluate {n} at {rat_display(x0)}", intermediate=f"k = {_substituted(rule, x0)} = {answer_display}")
            S.add("State the value", intermediate=f"k = {answer_display}", marks=1)
        return {"steps": S.steps}
    if task == "inverse_expression":
        a, b = params["a"], params["b"]
        rule = C.linear(a, b)
        S.add(f"Write y = {n}(x)", intermediate=f"y = {C.rule_text(rule)}")
        S.add("Swap x and y", intermediate=f"x = {Poly.linear(a, b).display('y')}", explanation="The inverse reverses the roles of input and output.")
        S.add("Solve for y", intermediate=f"y = {answer_display}", explanation="Undo the operations in reverse order.")
        S.add("State the inverse function", intermediate=f"{n}^-1(x) = {answer_display}", marks=1)
        S.add("Verify", intermediate=f"{n}({answer_display}) = x", explanation="Composing the function with its inverse returns the input.")
        return {"steps": S.steps}
    r = params["rule"]
    hx = C.vertex_x(r)
    S.add("Find the axis of symmetry", intermediate=f"x = -({rat_display(r['b'])})/(2({rat_display(r['a'])})) = {rat_display(hx)}", rule="x = -b/(2a)")
    S.add("Restrict the domain at the vertex",
          explanation=f"{n} takes each value twice on either side of the axis of symmetry, so it is one-to-one only on one side of x = {rat_display(hx)}.")
    S.add("State the value of k", intermediate=f"k = {answer_display}", marks=1)
    return {"steps": S.steps}


def _substituted_expr(outer: Dict[str, Any], inner: Dict[str, Any]) -> str:
    inner_txt = C.rule_text(inner)
    if outer["kind"] == "linear":
        a = outer["a"]
        head = f"({inner_txt})" if a == 1 else (f"-({inner_txt})" if a == -1 else f"{rat_display(a)}({inner_txt})")
        return head + C._shift_text(outer["b"])
    a, b, c = outer["a"], outer["b"], outer["c"]
    head = f"({inner_txt})^2" if a == 1 else (f"-({inner_txt})^2" if a == -1 else f"{rat_display(a)}({inner_txt})^2")
    if b != 0:
        mag = abs(b)
        head += (" - " if b < 0 else " + ") + (f"({inner_txt})" if mag == 1 else f"{rat_display(mag)}({inner_txt})")
    return head + C._shift_text(c)


# --------------------------------------------------------------------------- #
# Difficulty
# --------------------------------------------------------------------------- #

def _kind_tier(kind: str) -> int:
    return {"linear": 0, "quadratic": 1, "reciprocal": 2, "sqrt": 2}[kind]


def _band(task: str, params: Dict[str, Any]) -> int:
    lo, hi = TASK_BANDS[task]
    if task == "identify_function":
        return 2 if (params["negativeInputs"] or params["separatedRepeat"]) else 1
    if task == "evaluate_function":
        v = C.eval_rule(params["rule"], params["p"])
        tier = _kind_tier(params["rule"]["kind"]) + (1 if (params["p"] < 0 or v.denominator != 1) else 0)
        return min(1 + min(tier, 2), hi)
    if task == "solve_for_input":
        r = params["rule"]
        return 2 if (r["kind"] == "linear" and params["x0"].denominator == 1) else 3
    if task == "domain_of_function":
        r = params["rule"]
        if C.is_polynomial_rule(r):
            return 2
        if r["kind"] == "reciprocal":
            return 2 if r["h"] == 0 else 3
        endpoint = -r["b"] / r["a"]
        return 3 if (r["a"] > 0 and endpoint.denominator == 1) else 4
    if task == "range_of_function":
        r = params["rule"]
        if r["kind"] == "linear":
            return 3
        if r["kind"] == "sqrt":
            return 3 if r["v"] == 0 else 4
        if r["kind"] == "reciprocal":
            return 4
        return 4 if (r["a"] > 0 and C.vertex_y(r).denominator == 1) else 5
    if task == "composite_value":
        both_linear = params["f"]["kind"] == "linear" and params["g"]["kind"] == "linear"
        return 2 if (both_linear and params["p"] >= 0) else 3
    if task == "composite_expression":
        outer, inner, _, _ = _outer_inner(params)
        if outer["kind"] == "linear" and inner["kind"] == "linear":
            return 3
        hard = (outer["kind"] == "quadratic" and (inner["a"] < 0 or abs(inner["a"]) != 1 or outer["a"] != 1))
        return 5 if hard else 4
    if task == "function_from_composite":
        return 4 if params["m"] == 1 else 5
    if task == "inverse_value":
        if params["form"] == "inverse_at":
            return 2 if _solve(task, params).denominator == 1 else 3
        return 4 if (abs(params["a"]) >= 2 and params["b"] != 0) else 3
    if task == "inverse_expression":
        return 3 if abs(params["a"]) == 1 else 4
    r = params["rule"]
    return 4 if (r["a"] == 1 and r["b"].numerator % 2 == 0) else 5


_STEPS = {"identify_function": 0.25, "evaluate_function": 0.3, "solve_for_input": 0.5, "domain_of_function": 0.45,
          "range_of_function": 0.6, "composite_value": 0.45, "composite_expression": 0.65, "function_from_composite": 0.8,
          "inverse_value": 0.5, "inverse_expression": 0.65, "one_to_one_restriction": 0.7}
_ALG = {"identify_function": 0.1, "evaluate_function": 0.3, "solve_for_input": 0.5, "domain_of_function": 0.4,
        "range_of_function": 0.55, "composite_value": 0.4, "composite_expression": 0.75, "function_from_composite": 0.85,
        "inverse_value": 0.5, "inverse_expression": 0.7, "one_to_one_restriction": 0.6}
_ABS = {"identify_function": 0.5, "evaluate_function": 0.25, "solve_for_input": 0.35, "domain_of_function": 0.6,
        "range_of_function": 0.7, "composite_value": 0.5, "composite_expression": 0.65, "function_from_composite": 0.85,
        "inverse_value": 0.6, "inverse_expression": 0.7, "one_to_one_restriction": 0.85}
_REP = {"identify_function": 0.4, "evaluate_function": 0.2, "solve_for_input": 0.25, "domain_of_function": 0.55,
        "range_of_function": 0.6, "composite_value": 0.35, "composite_expression": 0.45, "function_from_composite": 0.5,
        "inverse_value": 0.4, "inverse_expression": 0.45, "one_to_one_restriction": 0.55}
_CONN = {"identify_function": 0.1, "evaluate_function": 0.1, "solve_for_input": 0.3, "domain_of_function": 0.3,
         "range_of_function": 0.5, "composite_value": 0.4, "composite_expression": 0.5, "function_from_composite": 0.7,
         "inverse_value": 0.5, "inverse_expression": 0.55, "one_to_one_restriction": 0.8}


def _difficulty(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    band = _band(task, params)
    lo, hi = TASK_BANDS[task]
    span = max(1, hi - lo)
    lever = Fraction(band - lo, span)  # 0..1 within the declared range
    bump = float(lever) * 0.2
    axes = {
        "numericalComplexity": round3(clamp01(0.25 + bump)),
        "algebraicComplexity": round3(clamp01(_ALG[task] + bump)),
        "reasoningSteps": round3(clamp01(_STEPS[task] + bump)),
        "abstraction": round3(clamp01(_ABS[task] + bump)),
        "representation": round3(clamp01(_REP[task] + bump)),
        "requiredConnections": round3(clamp01(_CONN[task] + bump)),
        "exactVsApproximate": round3(clamp01(0.0)),
    }
    return {"overallBand": band, "axes": axes}


# --------------------------------------------------------------------------- #
# generate
# --------------------------------------------------------------------------- #

def _encode_choice(task: str):
    if task == "identify_function":
        return lambda v: {"value": v, "display": _pairs_display(v)}
    return lambda v: {"value": _value_json(v), "display": _value_display(v)}


def generate(seed: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    config = config or {}
    explicit = config.get("task")
    if explicit is not None and explicit not in OBJECTIVE_BY_TASK:
        raise ValueError(f"unknown task {explicit!r}")

    rng = Mulberry32(seed)
    if explicit is None:
        requested = config.get("interactionType")
        pool = [t for t in TASKS if t not in MC_ONLY_TASKS] if requested == "free-response" else list(TASKS)
        task = rng.choice(pool)
    else:
        task = explicit

    interaction = _resolve_interaction(task, config)
    mc = interaction == "multiple-choice"

    params: Dict[str, Any] = {}
    distractors: Optional[List[Dict[str, Any]]] = None
    ok = False
    for _ in range(MAX_PARAM_ATTEMPTS):
        drawn = _DRAW[task](rng)
        if drawn is None or not _acceptable(task, drawn):
            continue
        if mc and task != "identify_function":
            ds = _mc_distractors(task, drawn, rng)
            if ds is None:
                continue
            distractors = ds
        params, ok = drawn, True
        break
    if not ok:
        raise RuntimeError(f"could not draw acceptable functions params for {task} seed={seed}")

    options: Optional[List[Dict[str, Any]]] = None
    records: Optional[List[Dict[str, Any]]] = None
    if task == "identify_function":
        ds = [{"value": f["pairs"], "misconceptionId": f["misconceptionId"],
               "rationale": FM.MISCONCEPTIONS[f["misconceptionId"]]["observableError"]} for f in params["functions"]]
        records, options = _assemble_mc(rng, params["nonFunction"], ds, _encode_choice(task))
        label = next(o["label"] for o in options if o["correct"])
        answer: Dict[str, Any] = {"type": "multiple-choice", "canonical": label, "display": label}
    else:
        value = _solve(task, params)
        answer = _encode_answer(task, value)
        if mc:
            records, options = _assemble_mc(rng, value, distractors or [], _encode_choice(task))

    item: Dict[str, Any] = {
        "itemId": f"ITEM-FUNC-{task}-{seed}",
        "schemaVersion": "1.0.0",
        "objectiveIds": [OBJECTIVE_BY_TASK[task]],
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "seed": seed,
        "params": _public_params(params),
        "interactionType": interaction,
        "prompt": _prompt(task, params),
        "answer": answer,
        "solution": _solution(task, params, answer["display"], options),
        "difficulty": _difficulty(task, params),
        "calculatorPolicy": CALCULATOR_POLICY,
        "accessibility": {"spokenMath": _spoken(task, params, options), "nonColorIndicators": True},
        "provenance": {"origin": "generated", "rightsStatus": "academy-owned",
                       "originalityNote": "Original parameterized item; structure abstracted from the IB AA SL functions syllabus."},
        "lifecycle": {"state": "generated"},
    }
    if options is not None:
        item["distractors"] = records
        item["options"] = options
    return item


# --------------------------------------------------------------------------- #
# validate (independent)
# --------------------------------------------------------------------------- #

# Internal coefficient names must never leak into student-facing feedback as bare symbols. The English
# article "a", the change-of-variable letter "u" and the textbook formula "-b/(2a)" are not leaks.
_PLACEHOLDER = re.compile(r"(?<![A-Za-z])[bcmpqtv](?![A-Za-z])")
_ALLOWED_FRAGMENTS = ("-b/(2a)",)


def _has_placeholder(text: str) -> bool:
    t = text
    for frag in _ALLOWED_FRAGMENTS:
        t = t.replace(frag, " ")
    return bool(_PLACEHOLDER.search(t))


def _prompt_text(item: Dict[str, Any]) -> str:
    parts = [b.get("text", "") + " " + b.get("latex", "") for b in item["prompt"]["blocks"]]
    parts.append(item["accessibility"].get("spokenMath", ""))
    return " ".join(parts)


def _explicit_reveal(task: str, item: Dict[str, Any], params: Dict[str, Any]) -> bool:
    """The requested quantity must never be stated with its answer in the prompt or spoken text."""
    disp = item["answer"]["display"]
    n = params.get("name", "f")
    txt = _prompt_text(item)
    if task == "identify_function":
        return False
    if task == "evaluate_function":
        tok = f"{n}({rat_display(params['p'])}) ="
    elif task in ("solve_for_input",):
        tok = "x ="
    elif task in ("domain_of_function", "range_of_function"):
        return f"= {disp}" in txt or f"is {disp}" in txt
    elif task == "composite_value":
        _, _, on, inn = _outer_inner(params)
        tok = f"({on} o {inn})({rat_display(params['p'])}) ="
    elif task == "composite_expression":
        _, _, on, inn = _outer_inner(params)
        tok = f"({on} o {inn})(x) ="
    elif task == "function_from_composite":
        tok = "f(x) ="
    elif task == "inverse_value":
        tok = f"{n}^-1({rat_display(params['k'])}) =" if params["form"] == "inverse_at" else "k ="
    elif task == "inverse_expression":
        tok = f"{n}^-1(x) ="
    else:
        tok = "k ="
    return f"{tok} {disp}" in txt


def _is_function_relation(pairs: List[List[int]]) -> bool:
    seen: Dict[int, int] = {}
    for x, y in pairs:
        if x in seen and seen[x] != y:
            return False
        seen.setdefault(x, y)
    return True


def _structure_matches(pairs: List[List[int]], mid: str) -> bool:
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    if len(set(xs)) != len(xs):
        return False
    if mid == "MISC.FUNC.MANY_TO_ONE_REJECTED":
        return len(set(ys)) < len(ys) and len(set(ys)) > 1
    if mid == "MISC.FUNC.CONSTANT_REJECTED":
        return len(set(ys)) == 1
    if mid == "MISC.FUNC.PATTERN_REQUIRED":
        return len(set(ys)) == len(ys) and xs != sorted(xs) and not _collinear(pairs)
    return False


def _reparses(task: str, answer: Dict[str, Any]) -> bool:
    fam = ANSWER_FAMILY[task]
    if fam == "choice":
        return answer["canonical"] == answer["display"]
    if fam == "number":
        return Fraction(answer["display"]) == rat_from_json(answer["canonical"])
    if fam == "expression":
        return check_expression(answer["display"], answer["canonical"])["code"] == "correct"
    return check_interval(answer["display"], answer["canonical"])["code"] == "correct"


def _canonical_normalized(task: str, answer: Dict[str, Any]) -> bool:
    fam = ANSWER_FAMILY[task]
    if fam == "number":
        c = answer["canonical"]
        f = Fraction(c["num"], c["den"])
        return f.numerator == c["num"] and f.denominator == c["den"] and c["den"] >= 1
    if fam == "expression":
        coeffs = answer["canonical"]["coefficients"]
        if answer["canonical"]["variable"] != "x" or not coeffs:
            return False
        last = coeffs[-1]
        stripped = len(coeffs) == 1 or last["num"] != 0
        reduced = all(Fraction(t["num"], t["den"]).denominator == t["den"] and t["den"] >= 1 for t in coeffs)
        return stripped and reduced
    if fam == "interval":
        c = answer["canonical"]
        if c["kind"] == "bounded":
            return rat_from_json(c["lo"]) < rat_from_json(c["hi"])
        if c["kind"] == "reals-except":
            pts = [rat_from_json(p) for p in c["points"]]
            return pts == sorted(set(pts)) and len(pts) >= 1
        return True
    return True


def validate(item: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "result": "pass" if ok else "fail", "detail": detail})

    pub = item["params"]
    task = pub["task"]
    params = _internal_params(pub)
    answer = item["answer"]
    fam = ANSWER_FAMILY[task]
    interaction = item.get("interactionType")

    add("params-in-domain", task in OBJECTIVE_BY_TASK and _acceptable(task, params), f"task={task}")
    add("interaction-type", interaction in supported_interactions(task), str(interaction))
    add("objective-mapping", item["objectiveIds"] == [OBJECTIVE_BY_TASK[task]], ",".join(item["objectiveIds"]))
    expected_type = {"choice": ("multiple-choice",), "number": ("integer", "exact-rational"), "expression": ("algebraic-expression",),
                     "interval": ("interval",)}[fam]
    add("answer-type-consistency", answer["type"] in expected_type
        and (fam != "number" or (answer["type"] == "integer") == (answer["canonical"]["den"] == 1)), answer["type"])
    add("canonical-form-normalized", _canonical_normalized(task, answer), json.dumps(answer["canonical"])[:80])
    add("display-reparses-to-canonical", _reparses(task, answer), answer["display"])

    # --- independent mathematical confirmation per task ---------------------------------------- #
    if task == "identify_function":
        opts = item.get("options") or []
        non_fn = [o for o in opts if not _is_function_relation(o["value"])]
        add("exactly-one-non-function", len(non_fn) == 1 and non_fn[0]["correct"] and non_fn[0]["label"] == answer["canonical"],
            ",".join(o["label"] for o in non_fn))
        structural = all(_structure_matches(o["value"], o.get("misconceptionId", "")) for o in opts if not o["correct"])
        add("distractor-structure-matches-misconception", structural, "")
        add("options-distinct-displays", len({o["display"] for o in opts}) == len(opts) == 4, "")
    elif task == "evaluate_function":
        r, p = params["rule"], params["p"]
        want = rat_from_json(answer["canonical"])
        if C.is_polynomial_rule(r):
            got = C.rule_poly(r).eval(p)
            ok = got == want
        elif r["kind"] == "reciprocal":
            ok = p != r["h"] and (r["k"] + r["v"] * (p - r["h"])) == want * (p - r["h"])
        else:
            t = want - r["v"]
            ok = t >= 0 and t * t == C.radicand(r, p)
        add("value-recomputed-independently", ok, f"{rat_display(want)}")
    elif task == "solve_for_input":
        x = rat_from_json(answer["canonical"])
        add("solution-satisfies-equation", C.eval_rule(params["rule"], x) == params["target"], f"x={rat_display(x)}")
    elif task == "domain_of_function":
        r = params["rule"]
        c = answer["canonical"]
        if r["kind"] == "sqrt":
            e = rat_from_json(c["endpoint"]) if c["kind"] == "ray" else None
            inside = e + (1 if c.get("direction") == "ge" else -1) if e is not None else None
            outside = e - (1 if c.get("direction") == "ge" else -1) if e is not None else None
            ok = (c["kind"] == "ray" and c["variable"] == "x" and c["inclusive"] and C.radicand(r, e) == 0
                  and C.radicand(r, inside) > 0 and C.radicand(r, outside) < 0)
        elif r["kind"] == "reciprocal":
            pts = [rat_from_json(p) for p in c.get("points", [])]
            ok = (c["kind"] == "reals-except" and c["variable"] == "x" and len(pts) == 1 and pts[0] - r["h"] == 0
                  and C.eval_rule(r, pts[0] + 1) is not None and C.eval_rule(r, pts[0] - 1) is not None)
        else:
            ok = c["kind"] == "reals" and all(C.eval_rule(r, Fraction(x)) is not None for x in (-1, 0, 1))
        add("domain-boundary-probe", ok, c["kind"])
    elif task == "range_of_function":
        r = params["rule"]
        c = answer["canonical"]
        if r["kind"] == "quadratic":
            k = rat_from_json(c["endpoint"]) if c["kind"] == "ray" else None
            hx = C.vertex_x(r)
            side = 1 if c.get("direction") == "ge" else -1
            ok = (c["kind"] == "ray" and c["variable"] == "y" and c["inclusive"] and C.eval_rule(r, hx) == k
                  and all(side * (C.eval_rule(r, hx + t) - k) > 0 for t in (1, 2, -1, -2)))
        elif r["kind"] == "sqrt":
            e = -r["b"] / r["a"]
            ok = (c["kind"] == "ray" and c["variable"] == "y" and c["inclusive"] and c["direction"] == "ge"
                  and C.eval_rule(r, e) == rat_from_json(c["endpoint"]) and C.radicand(r, e + (1 if r["a"] > 0 else -1)) > 0)
        elif r["kind"] == "reciprocal":
            pts = [rat_from_json(p) for p in c.get("points", [])]
            ok = (c["kind"] == "reals-except" and c["variable"] == "y" and len(pts) == 1
                  and C.eval_rule(r, r["h"] + 1) != pts[0] and C.eval_rule(r, r["h"] - 1) != pts[0]
                  and C.eval_rule(r, r["h"] + 1) - pts[0] == -(C.eval_rule(r, r["h"] - 1) - pts[0]))
        else:
            p, q = params["restricted"]["p"], params["restricted"]["q"]
            imgs = sorted([C.eval_rule(r, p), C.eval_rule(r, q)])
            ok = (c["kind"] == "bounded" and c["variable"] == "y" and c["loInclusive"] and c["hiInclusive"]
                  and rat_from_json(c["lo"]) == imgs[0] and rat_from_json(c["hi"]) == imgs[1] and p < q)
        add("range-attained-and-bounded", ok, c["kind"])
    elif task == "composite_value":
        outer, inner, _, _ = _outer_inner(params)
        want = rat_from_json(answer["canonical"])
        got = C.rule_poly(outer).eval(C.rule_poly(inner).eval(params["p"]))
        add("composite-recomputed-stepwise", got == want, rat_display(got))
    elif task == "composite_expression":
        outer, inner, _, _ = _outer_inner(params)
        stored = Poly.from_json(answer["canonical"])
        po, pi = C.rule_poly(outer), C.rule_poly(inner)
        agree = all(stored.eval(x) == po.eval(pi.eval(x)) for x in (-2, -1, 0, 1, 2))
        add("composite-pointwise-agreement", agree, stored.display())
        add("degree-bound", stored.degree() <= 2, str(stored.degree()))
    elif task == "function_from_composite":
        stored = Poly.from_json(answer["canonical"])
        g = Poly.linear(params["m"], params["c"])
        given = Poly.linear(params["A"] * params["m"], params["A"] * params["c"] + params["B"])
        add("recomposes-to-given", stored.compose(g).equals(given), stored.display())
    elif task == "inverse_value":
        a, b = params["a"], params["b"]
        v = rat_from_json(answer["canonical"])
        if params["form"] == "inverse_at":
            add("inverse-value-satisfies-forward", a * v + b == params["k"], rat_display(v))
        else:
            add("inverse-value-satisfies-forward", (v - b) / a == params["x0"], rat_display(v))
    elif task == "inverse_expression":
        stored = Poly.from_json(answer["canonical"])
        f = Poly.linear(params["a"], params["b"])
        add("inverse-round-trip", f.compose(stored).equals(Poly.x()) and stored.compose(f).equals(Poly.x()), stored.display())
    else:
        r = params["rule"]
        h = rat_from_json(answer["canonical"])
        add("axis-of-symmetry-probe", all(C.eval_rule(r, h + t) == C.eval_rule(r, h - t) for t in (1, 2, 3)), rat_display(h))

    # --- solution, leakage, MC -------------------------------------------------------------- #
    steps = item["solution"]["steps"]
    add("answer-solution-agree", answer["display"] in (steps[-1].get("intermediateResult") or ""), "")
    add("no-answer-leakage", not _explicit_reveal(task, item, params), "")

    if task != "identify_function" and item.get("distractors"):
        ds = item["distractors"]
        mids = [d["misconceptionId"] for d in ds]
        add("distractors-distinct-misconceptions", len(set(mids)) == len(mids), ",".join(mids))
        add("min-three-distractors", len(ds) >= 3, str(len(ds)))
        ctx = _ctx(task, params)
        for d in ds:
            m = FM.MISCONCEPTIONS.get(d["misconceptionId"])
            add("distractor-misconception-known", m is not None and d["misconceptionId"] in FM.rules_for(task), d["misconceptionId"])
            if m is None:
                continue
            expected = m["wrong"](ctx)
            add("distractor-value-matches-rule", expected is not None and _value_display(expected) == d["display"]
                and _value_json(expected) == d["value"], d["misconceptionId"])
            add("distractor-rationale-matches", d.get("rationale") == m["observableError"], d["misconceptionId"])
            fb = m["feedback"](ctx)
            add("distractor-feedback-present", bool(fb), d["misconceptionId"])
            add("distractor-feedback-clean", not _has_placeholder(fb), fb)
            add("distractor-not-answer", d["display"] != answer["display"], d["display"])
    if item.get("options"):
        opts = item["options"]
        correct = [o for o in opts if o["correct"]]
        expected_display = answer["display"] if task != "identify_function" else _pairs_display(params["nonFunction"])
        add("exactly-one-correct", len(correct) == 1 and correct[0]["display"] == expected_display, "")
        wrong = [o["display"] for o in opts if not o["correct"]]
        add("distractors-unique", len(set(wrong)) == len(wrong), "")
        add("options-labelled-in-order", [o["label"] for o in opts] == list(LABELS[:len(opts)]), "")

    add("a11y-fields-present", bool(item.get("accessibility", {}).get("spokenMath")), "")
    add("provenance-complete", bool(item.get("provenance", {}).get("origin")) and bool(item["provenance"].get("rightsStatus")), "")
    add("version-fields-present", bool(item.get("generatorId")) and bool(item.get("generatorVersion")), "")

    status = "pass" if all(c["result"] == "pass" for c in checks) else "fail"
    return {"status": status, "validatorVersion": VALIDATOR_VERSION, "checks": checks}


# --------------------------------------------------------------------------- #
# render / serialize / describe
# --------------------------------------------------------------------------- #

def render(item: Dict[str, Any], mode: str = "full") -> str:
    lines = []
    for b in item["prompt"]["blocks"]:
        lines.append(b.get("text") or b.get("latex") or "")
    for o in item.get("options", []):
        lines.append(f"  {o['label']}. {o['display']}")
    if mode == "answer-only":
        return f"Answer: {item['answer']['display']}"
    out = list(lines)
    if mode == "full":
        out += ["", "Solution:"]
        for s in item["solution"]["steps"]:
            bit = s.get("intermediateResult") or s.get("ruleOrTheorem") or s.get("explanation") or ""
            out.append(f"  {s['number']}. {s.get('transformation', '')}: {bit}")
    out.append(f"Answer: {item['answer']['display']}")
    return "\n".join(out)


def serialize(item: Dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def describe() -> Dict[str, Any]:
    return {
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "title": "Introducing Functions (IB AA SL): notation, domain and range, composition, inverses",
        "description": "Eleven exact tasks over linear, quadratic, reciprocal and square-root rules: identify a function from ordered pairs, "
                       "evaluate, solve f(x)=k, domain, range, composite value/expression, recover the outer function, inverse value/expression, "
                       "one-to-one restriction.",
        "status": "in-development",
        "supportedObjectives": sorted(set(OBJECTIVE_BY_TASK.values())),
        "supportedQuestionTypes": ["integer", "exact-rational", "algebraic-expression", "interval", "multiple-choice"],
        "rngAlgorithm": "mulberry32",
        "parameterSpec": {
            "task": {"type": "enum", "enumValues": list(TASKS)},
            "name": {"type": "enum", "enumValues": list(NAMES), "description": "Function name for single-function tasks."},
            "rule": {"type": "string", "description": "The exact rule record {kind, ...} with rational fields."},
            "p": {"type": "integer", "description": "Evaluation input (evaluate / composite value), -6..6."},
            "order": {"type": "enum", "enumValues": ["fg", "gf"], "description": "Which composition is requested."},
            "form": {"type": "enum", "enumValues": ["inverse_at", "solve_inverse_equation"]},
            "side": {"type": "enum", "enumValues": ["ge", "le"], "description": "Restriction side for one_to_one_restriction."},
        },
        "operations": {"describe": True, "generate": True, "solve": True, "validate": True,
                       "generateDistractors": True, "generateSolution": True, "render": True, "serialize": True},
        "canonicalMethod": "Backward construction (perfect-square radicands, divisor-chosen poles, chosen inputs) with closed-form answers: "
                           "substitution, inverse operations, rule-type case analysis for domain/range, symbolic polynomial composition, "
                           "(x-b)/a inverses, -b/(2a) vertex.",
        "independentValidationMethod": "Horner re-evaluation on coefficient vectors, substitution of the stored solution, boundary probes of "
                                       "radicands/denominators, vertex/symmetry probes, five-point polynomial identity, recomposition, "
                                       "inverse round-trip, and re-parsing of every display through the family's own checkers.",
        "misconceptionMappings": sorted(FM.MISCONCEPTIONS.keys()),
        "testStrategy": {"seedSweepCount": 10000, "goldenSeeds": [1, 42, 123456789, 2147483647]},
    }
