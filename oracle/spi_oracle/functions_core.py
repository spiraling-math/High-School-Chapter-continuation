"""Exact function-rule model for gen.functions.foundations (oracle reference).

A *rule* is a small dict with a `kind` and exact `Fraction` fields:

    linear     {kind, a, b}       a*x + b                 (a != 0)
    quadratic  {kind, a, b, c}    a*x^2 + b*x + c         (a != 0)
    reciprocal {kind, k, h, v}    k/(x - h) + v           (k != 0)
    sqrt       {kind, a, b, v}    sqrt(a*x + b) + v       (a != 0)

This module owns everything both the generator and the misconception registry need: exact
evaluation (None where the value is not an exact rational), polynomial views, the LaTeX / plain-text
/ spoken renderings of a rule, and the real-subset descriptor constructors. No floats anywhere.

Byte-for-byte counterpart of domains/functions/functions-core.ts (every rendered string is part of
the cross-language contract).
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Optional

from polynomial import Poly, poly_display, rat_display, rat_json, rat_from_json

# --------------------------------------------------------------------------- #
# Exact helpers
# --------------------------------------------------------------------------- #

def F(x) -> Fraction:
    return Fraction(x)


def isqrt_exact(n: int) -> Optional[int]:
    """Integer square root when n is a perfect square (n >= 0), else None."""
    if n < 0:
        return None
    r = 0
    while (r + 1) * (r + 1) <= n:
        r += 1
    return r if r * r == n else None


def sqrt_exact(q: Fraction) -> Optional[Fraction]:
    """Exact non-negative square root of a rational when both numerator and denominator are perfect squares."""
    q = Fraction(q)
    if q < 0:
        return None
    rn, rd = isqrt_exact(q.numerator), isqrt_exact(q.denominator)
    if rn is None or rd is None:
        return None
    return Fraction(rn, rd)


# --------------------------------------------------------------------------- #
# Rules
# --------------------------------------------------------------------------- #

def linear(a, b) -> Dict[str, Any]:
    return {"kind": "linear", "a": F(a), "b": F(b)}


def quadratic(a, b, c) -> Dict[str, Any]:
    return {"kind": "quadratic", "a": F(a), "b": F(b), "c": F(c)}


def reciprocal(k, h, v) -> Dict[str, Any]:
    return {"kind": "reciprocal", "k": F(k), "h": F(h), "v": F(v)}


def sqrt_rule(a, b, v) -> Dict[str, Any]:
    return {"kind": "sqrt", "a": F(a), "b": F(b), "v": F(v)}


def rule_to_json(rule: Dict[str, Any]) -> Dict[str, Any]:
    return {k: (v if k == "kind" else rat_json(v)) for k, v in rule.items()}


def rule_from_json(j: Dict[str, Any]) -> Dict[str, Any]:
    return {k: (v if k == "kind" else rat_from_json(v)) for k, v in j.items()}


def is_polynomial_rule(rule: Dict[str, Any]) -> bool:
    return rule["kind"] in ("linear", "quadratic")


def rule_poly(rule: Dict[str, Any]) -> Poly:
    """The polynomial view of a linear / quadratic rule."""
    if rule["kind"] == "linear":
        return Poly.linear(rule["a"], rule["b"])
    if rule["kind"] == "quadratic":
        return Poly.quadratic(rule["a"], rule["b"], rule["c"])
    raise ValueError("not a polynomial rule")


def radicand(rule: Dict[str, Any], x) -> Fraction:
    return rule["a"] * F(x) + rule["b"]


def eval_rule(rule: Dict[str, Any], x) -> Optional[Fraction]:
    """Exact value f(x), or None when it is undefined (pole) or irrational (non-square radicand)."""
    xf = F(x)
    k = rule["kind"]
    if k == "linear":
        return rule["a"] * xf + rule["b"]
    if k == "quadratic":
        return rule["a"] * xf * xf + rule["b"] * xf + rule["c"]
    if k == "reciprocal":
        if xf == rule["h"]:
            return None
        return rule["k"] / (xf - rule["h"]) + rule["v"]
    root = sqrt_exact(radicand(rule, xf))
    return None if root is None else root + rule["v"]


# --------------------------------------------------------------------------- #
# Rendering of rules: LaTeX (prompt math blocks), plain text (displays/spoken)
# --------------------------------------------------------------------------- #

def latex_rat(q: Fraction, allow_frac: bool = True) -> str:
    """LaTeX for a rational: 3, -3, \\frac{3}{4}, -\\frac{3}{4}."""
    q = F(q)
    if q.denominator == 1:
        return str(q.numerator)
    s = f"\\frac{{{abs(q.numerator)}}}{{{q.denominator}}}"
    return "-" + s if q < 0 else s


def _latex_coef_var(a: Fraction, var: str) -> str:
    """LaTeX for a*var with the coefficient's sign included: x, -x, 2x, -\\frac{1}{2}x."""
    if a == 1:
        return var
    if a == -1:
        return "-" + var
    return latex_rat(a) + var


def latex_poly(p: Poly) -> str:
    """LaTeX for a polynomial, descending degree, e.g. x^{2} - 4x + 1, -\\frac{1}{2}x + 3, 0."""
    out = ""
    for d in range(len(p.c) - 1, -1, -1):
        c = p.c[d]
        if c == 0:
            continue
        var = "" if d == 0 else ("x" if d == 1 else f"x^{{{d}}}")
        if out == "":
            out = latex_rat(c) if d == 0 else _latex_coef_var(c, var)
        else:
            mag = abs(c)
            body = latex_rat(mag) if d == 0 else _latex_coef_var(mag, var)
            out += (" - " if c < 0 else " + ") + body
    return out if out else "0"


def _shift_latex(v: Fraction) -> str:
    if v == 0:
        return ""
    return (" - " + latex_rat(abs(v))) if v < 0 else (" + " + latex_rat(v))


def _shift_text(v: Fraction) -> str:
    if v == 0:
        return ""
    return (" - " + rat_display(abs(v))) if v < 0 else (" + " + rat_display(v))


def _denominator_latex(h: Fraction) -> str:
    if h == 0:
        return "x"
    return f"x - {latex_rat(h)}" if h > 0 else f"x + {latex_rat(abs(h))}"


def _denominator_text(h: Fraction) -> str:
    if h == 0:
        return "x"
    return f"x - {rat_display(h)}" if h > 0 else f"x + {rat_display(abs(h))}"


def _radicand_poly(rule: Dict[str, Any]) -> Poly:
    return Poly.linear(rule["a"], rule["b"])


def radicand_latex(rule: Dict[str, Any]) -> str:
    """ax + b for a > 0; b - |a|x for a < 0 (reads naturally: \\sqrt{5 - 2x})."""
    a, b = rule["a"], rule["b"]
    if a > 0 or b == 0:
        return latex_poly(_radicand_poly(rule))
    return f"{latex_rat(b)} - {_latex_coef_var(abs(a), 'x')}"


def radicand_text(rule: Dict[str, Any]) -> str:
    a, b = rule["a"], rule["b"]
    if a > 0 or b == 0:
        return poly_display(_radicand_poly(rule).c)
    mag = abs(a)
    coef = "x" if mag == 1 else (f"{mag.numerator}x" if mag.denominator == 1 else f"({rat_display(mag)})x")
    return f"{rat_display(b)} - {coef}"


def rule_latex(rule: Dict[str, Any]) -> str:
    k = rule["kind"]
    if k in ("linear", "quadratic"):
        return latex_poly(rule_poly(rule))
    if k == "reciprocal":
        kk = rule["k"]
        frac = f"\\frac{{{latex_rat(abs(kk))}}}{{{_denominator_latex(rule['h'])}}}"
        return ("-" if kk < 0 else "") + frac + _shift_latex(rule["v"])
    return f"\\sqrt{{{radicand_latex(rule)}}}" + _shift_latex(rule["v"])


def rule_text(rule: Dict[str, Any]) -> str:
    """Plain-text rule, e.g. 2x - 3, x^2 - 4x + 1, 3/(x - 2) + 1, -2/x, sqrt(5 - 2x) - 1."""
    k = rule["kind"]
    if k in ("linear", "quadratic"):
        return rule_poly(rule).display()
    if k == "reciprocal":
        den = _denominator_text(rule["h"])
        den_txt = den if rule["h"] == 0 else f"({den})"
        return f"{rat_display(rule['k'])}/{den_txt}" + _shift_text(rule["v"])
    return f"sqrt({radicand_text(rule)})" + _shift_text(rule["v"])


def rule_kind_label(rule: Dict[str, Any]) -> str:
    return {"linear": "linear", "quadratic": "quadratic", "reciprocal": "reciprocal", "sqrt": "square-root"}[rule["kind"]]


# --------------------------------------------------------------------------- #
# Real-subset descriptors (exact) used by domain / range tasks
# --------------------------------------------------------------------------- #

def reals() -> Dict[str, Any]:
    return {"kind": "reals", "variable": None}


def ray(variable: str, endpoint, inclusive: bool, direction: str) -> Dict[str, Any]:
    return {"kind": "ray", "variable": variable, "endpoint": F(endpoint), "inclusive": bool(inclusive), "direction": direction}


def bounded(variable: str, lo, hi, lo_inc: bool = True, hi_inc: bool = True) -> Dict[str, Any]:
    return {"kind": "bounded", "variable": variable, "lo": F(lo), "hi": F(hi), "loInclusive": bool(lo_inc), "hiInclusive": bool(hi_inc)}


def reals_except(variable: str, points: List) -> Dict[str, Any]:
    return {"kind": "reals-except", "variable": variable, "points": sorted(set(F(p) for p in points))}


def descriptor_key(d: Dict[str, Any]) -> str:
    """A variable-blind identity key for dedupe (the set, not the letter)."""
    k = d["kind"]
    if k == "reals":
        return "reals"
    if k == "ray":
        return f"ray:{d['endpoint']}:{int(d['inclusive'])}:{d['direction']}"
    if k == "bounded":
        return f"bounded:{d['lo']}:{d['hi']}:{int(d['loInclusive'])}:{int(d['hiInclusive'])}"
    return "except:" + ",".join(str(p) for p in d["points"])


def domain_of(rule: Dict[str, Any]) -> Dict[str, Any]:
    """The largest possible domain of a rule, as an exact descriptor in x."""
    k = rule["kind"]
    if k in ("linear", "quadratic"):
        return reals()
    if k == "reciprocal":
        return reals_except("x", [rule["h"]])
    a, b = rule["a"], rule["b"]
    return ray("x", -b / a, True, "ge" if a > 0 else "le")


def vertex_x(rule: Dict[str, Any]) -> Fraction:
    return -rule["b"] / (2 * rule["a"])


def vertex_y(rule: Dict[str, Any]) -> Fraction:
    return rule["c"] - rule["b"] * rule["b"] / (4 * rule["a"])


def range_of(rule: Dict[str, Any], restricted: Optional[Dict[str, Fraction]] = None) -> Dict[str, Any]:
    """The range of a rule in y: quadratic (vertex), sqrt (y >= v), reciprocal (y != v), or a linear rule
    on the closed restricted domain [p, q] (endpoint images, ordered)."""
    k = rule["kind"]
    if k == "quadratic":
        return ray("y", vertex_y(rule), True, "ge" if rule["a"] > 0 else "le")
    if k == "sqrt":
        return ray("y", rule["v"], True, "ge")
    if k == "reciprocal":
        return reals_except("y", [rule["v"]])
    assert restricted is not None, "a linear rule needs a restricted domain to have a bounded range"
    fp, fq = eval_rule(rule, restricted["p"]), eval_rule(rule, restricted["q"])
    return bounded("y", min(fp, fq), max(fp, fq), True, True)
