"""Real-subset ("interval") answer checker (oracle reference) — the `interval` answer type used for
domains and ranges.

Canonical descriptor (answer.canonical):
    {"kind": "reals"}
    {"kind": "ray", "variable": v, "endpoint": {num,den}, "inclusive": bool, "direction": "ge"|"le"}
    {"kind": "bounded", "variable": v, "lo": {num,den}, "hi": {num,den}, "loInclusive": bool, "hiInclusive": bool}
    {"kind": "reals-except", "variable": v, "points": [{num,den}, ...]}       # sorted, distinct
with v in {"x", "y"} (x for a domain, y for a range).

Accepted learner forms (ASCII-anchored, unicode conveniences normalised): inequalities
(``x >= 2``, ``2 <= x``, ``-1 < x <= 4``, ``x >= -1 and x <= 4``), interval notation (``[2, inf)``,
``(-inf, 2]``, ``[-1, 4]``), exclusions (``x != 3``, ``x =/= 3``, ``x != 3, 5``, ``all real numbers
except 3``, ``R \\ {3}``), the whole line (``all real numbers``, ``R``, ``(-inf, inf)``, ``x in R``)
and set-builder wrappers (``{x | x >= 2}``, ``{x : x != 3}``). The variable may be ``x``, ``y`` or
``f(x)``/``g(x)``/``h(x)`` (read as ``y``). Plain-text display: ``x >= 2``, ``y != 1``,
``-1 <= y <= 4``, ``all real numbers``.

Byte-for-byte counterpart of core/answer-checking/interval-checker.ts.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Tuple

from polynomial import rat_display, rat_from_json, rat_json

CODES = ("correct", "unparseable", "wrong-variable", "wrong-kind", "wrong-endpoint",
         "wrong-inclusivity", "wrong-direction", "misconception")
MAX_INPUT_LENGTH = 200

_UNICODE = (
    ("≥", ">="), ("⩾", ">="), ("≤", "<="), ("⩽", "<="), ("≠", "!="),
    ("∞", "inf"), ("ℝ", "R"), ("∈", " in "), ("−", "-"), ("–", "-"),
    ("—", "-"), ("∖", "\\"),
)
# Every digit-bearing pattern is compiled ASCII-only: Python's unicode \d would accept e.g. Arabic-Indic
# digits that the TypeScript mirror (JS \d = [0-9]) rejects — the grading-path parity lesson of ratio v1.0.0.
_A = re.ASCII
_NUM = r"-?\d+(?:\.\d+)?(?:/\d+)?"
_VAR = r"(?:x|y|[a-z]\(x\))"
_RE_INTERVAL = re.compile(r"^([\[(])(-inf|-?[\d./]+),(inf|-?[\d./]+)([\])])$", _A)
_RE_RAY = re.compile(rf"^({_VAR})(>=|<=|>|<)({_NUM})$", _A)
_RE_RAY_REV = re.compile(rf"^({_NUM})(>=|<=|>|<)({_VAR})$", _A)
_RE_BOUNDED = re.compile(rf"^({_NUM})(<=|<)({_VAR})(<=|<)({_NUM})$", _A)
_RE_BOUNDED_REV = re.compile(rf"^({_NUM})(>=|>)({_VAR})(>=|>)({_NUM})$", _A)
_RE_EXCEPT = re.compile(rf"^({_VAR})!=({_NUM}(?:,{_NUM})*)$", _A)
_RE_SETBUILDER = re.compile(rf"^\{{({_VAR})(?:inr)?[|:](.*)\}}$", _A)
_RE_WORDS_EXCEPT = re.compile(rf"^(?:allrealnumbers|allreals|realnumbers|reals|r)except({_NUM}(?:(?:,|and){_NUM})*)$", _A)
_RE_SETMINUS = re.compile(rf"^r\\\{{({_NUM}(?:,{_NUM})*)\}}$", _A)
_RE_VAR_IN_R = re.compile(rf"^{_VAR}inr$", _A)
_RE_NUMBER = re.compile(r"^(-?)(\d+)(?:\.(\d+))?(?:/(\d+))?$", _A)
_REALS_WORDS = {"allrealnumbers", "allreals", "realnumbers", "reals", "r", "(-inf,inf)"}
# The whitespace class stripped before parsing — spelled out so Python and TypeScript agree exactly.
WHITESPACE = re.compile("[ \t\n\r\f\v   -     　﻿]+")


def parse_number(s: str) -> Optional[Fraction]:
    m = _RE_NUMBER.match(s)
    if not m:
        return None
    sign, ip, fp, dp = m.group(1), m.group(2), m.group(3) or "", m.group(4)
    if len(ip) + len(fp) > 12 or (dp is not None and len(dp) > 12):
        return None
    den = 10 ** len(fp) * (int(dp) if dp is not None else 1)
    if den == 0:
        return None
    value = Fraction(int(ip + fp), den)
    return -value if sign == "-" else value


def normalize_interval(raw: str) -> Optional[str]:
    s = raw.strip()
    if len(s) > MAX_INPUT_LENGTH:
        return None
    for a, b in _UNICODE:
        s = s.replace(a, b)
    s = s.lower()
    s = WHITESPACE.sub("", s)
    s = s.replace("=/=", "!=").replace("=<", "<=").replace("=>", ">=")
    s = re.sub(r"(?<![a-z])(?:infinity|oo)(?![a-z])", "inf", s, flags=_A)
    s = s.replace("thesetof", "").replace("theset", "").replace("suchthat", "|")
    return s


def _variable_of(tok: str) -> str:
    return "x" if tok == "x" else "y"  # y, f(x), g(x), h(x) -> the output variable


def _ray(var: str, op: str, n: Fraction) -> Dict[str, Any]:
    return {"kind": "ray", "variable": var, "endpoint": n, "inclusive": op in (">=", "<="),
            "direction": "ge" if op in (">=", ">") else "le"}


def _bounded(var: str, lo: Fraction, lo_inc: bool, hi: Fraction, hi_inc: bool) -> Optional[Dict[str, Any]]:
    if not lo < hi:
        return None
    return {"kind": "bounded", "variable": var, "lo": lo, "hi": hi, "loInclusive": lo_inc, "hiInclusive": hi_inc}


def _points(text: str) -> Optional[List[Fraction]]:
    vals = []
    for part in re.split(r",|and", text, flags=_A):
        n = parse_number(part)
        if n is None:
            return None
        vals.append(n)
    vals = sorted(set(vals))
    return vals


def _parse_atom(s: str) -> Optional[Dict[str, Any]]:
    """One constraint (no conjunction). Returns a descriptor (variable None when notation carries none)."""
    if s in _REALS_WORDS or _RE_VAR_IN_R.match(s):
        return {"kind": "reals", "variable": (_variable_of(s[:-3]) if s.endswith("inr") else None)}
    m = _RE_WORDS_EXCEPT.match(s)
    if m:
        pts = _points(m.group(1))
        return None if pts is None else {"kind": "reals-except", "variable": None, "points": pts}
    m = _RE_SETMINUS.match(s)
    if m:
        pts = _points(m.group(1))
        return None if pts is None else {"kind": "reals-except", "variable": None, "points": pts}
    m = _RE_INTERVAL.match(s)
    if m:
        lb, lo_s, hi_s, rb = m.groups()
        lo_inf, hi_inf = lo_s == "-inf", hi_s == "inf"
        if lo_inf and lb != "(":
            return None
        if hi_inf and rb != ")":
            return None
        if lo_inf and hi_inf:
            return {"kind": "reals", "variable": None}
        if lo_inf:
            hi = parse_number(hi_s)
            return None if hi is None else _ray(None, "<=" if rb == "]" else "<", hi)
        if hi_inf:
            lo = parse_number(lo_s)
            return None if lo is None else _ray(None, ">=" if lb == "[" else ">", lo)
        lo, hi = parse_number(lo_s), parse_number(hi_s)
        if lo is None or hi is None:
            return None
        return _bounded(None, lo, lb == "[", hi, rb == "]")
    m = _RE_RAY.match(s)
    if m:
        n = parse_number(m.group(3))
        return None if n is None else _ray(_variable_of(m.group(1)), m.group(2), n)
    m = _RE_RAY_REV.match(s)
    if m:
        n = parse_number(m.group(1))
        flipped = {">=": "<=", "<=": ">=", ">": "<", "<": ">"}[m.group(2)]
        return None if n is None else _ray(_variable_of(m.group(3)), flipped, n)
    m = _RE_BOUNDED.match(s)
    if m:
        lo, hi = parse_number(m.group(1)), parse_number(m.group(5))
        if lo is None or hi is None:
            return None
        return _bounded(_variable_of(m.group(3)), lo, m.group(2) == "<=", hi, m.group(4) == "<=")
    m = _RE_BOUNDED_REV.match(s)
    if m:
        hi, lo = parse_number(m.group(1)), parse_number(m.group(5))
        if lo is None or hi is None:
            return None
        return _bounded(_variable_of(m.group(3)), lo, m.group(4) == ">=", hi, m.group(2) == ">=")
    m = _RE_EXCEPT.match(s)
    if m:
        pts = _points(m.group(2))
        return None if pts is None else {"kind": "reals-except", "variable": _variable_of(m.group(1)), "points": pts}
    return None


def _merge(a: Dict[str, Any], b: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Intersect two atoms: reals ∧ X = X; two opposite rays = bounded; two exclusions = union of points."""
    va, vb = a.get("variable"), b.get("variable")
    if va is not None and vb is not None and va != vb:
        return None
    var = va if va is not None else vb
    if a["kind"] == "reals":
        return dict(b, variable=var)
    if b["kind"] == "reals":
        return dict(a, variable=var)
    if a["kind"] == "ray" and b["kind"] == "ray" and a["direction"] != b["direction"]:
        lo_a, hi_a = (a, b) if a["direction"] == "ge" else (b, a)
        return _bounded(var, lo_a["endpoint"], lo_a["inclusive"], hi_a["endpoint"], hi_a["inclusive"])
    if a["kind"] == "reals-except" and b["kind"] == "reals-except":
        return {"kind": "reals-except", "variable": var, "points": sorted(set(a["points"]) | set(b["points"]))}
    return None


def parse_interval(raw: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Return ('correct', descriptor-with-Fractions) on a successful parse, else ('unparseable', None).
    The descriptor's ``variable`` is None when the notation carried no variable (interval notation)."""
    s = normalize_interval(raw)
    if s is None or s == "":
        return ("unparseable", None)
    m = _RE_SETBUILDER.match(s)
    declared: Optional[str] = None
    if m:
        declared = _variable_of(m.group(1))
        s = m.group(2)
        if s in ("", "r", "inr"):
            return ("correct", {"kind": "reals", "variable": declared})
    # A single atom first (interval notation contains commas of its own); then conjunctions.
    acc: Optional[Dict[str, Any]] = _parse_atom(s)
    if acc is None:
        parts = [p for p in re.split(r"and|,(?=[a-z(\[])", s, flags=_A) if p != ""]
        if not parts:
            return ("unparseable", None)
        for part in parts:
            atom = _parse_atom(part)
            if atom is None:
                return ("unparseable", None)
            acc = atom if acc is None else _merge(acc, atom)
            if acc is None:
                return ("unparseable", None)
    if declared is not None:
        if acc.get("variable") is not None and acc["variable"] != declared:
            return ("unparseable", None)
        acc = dict(acc, variable=declared)
    return ("correct", acc)


# --- canonical JSON encoding ------------------------------------------------------------------- #
def interval_to_json(d: Dict[str, Any]) -> Dict[str, Any]:
    k = d["kind"]
    if k == "reals":
        return {"kind": "reals"}
    if k == "ray":
        return {"kind": "ray", "variable": d["variable"], "endpoint": rat_json(d["endpoint"]),
                "inclusive": bool(d["inclusive"]), "direction": d["direction"]}
    if k == "bounded":
        return {"kind": "bounded", "variable": d["variable"], "lo": rat_json(d["lo"]), "hi": rat_json(d["hi"]),
                "loInclusive": bool(d["loInclusive"]), "hiInclusive": bool(d["hiInclusive"])}
    return {"kind": "reals-except", "variable": d["variable"], "points": [rat_json(p) for p in sorted(set(d["points"]))]}


def interval_from_json(j: Dict[str, Any]) -> Dict[str, Any]:
    k = j["kind"]
    if k == "reals":
        return {"kind": "reals", "variable": None}
    if k == "ray":
        return {"kind": "ray", "variable": j["variable"], "endpoint": rat_from_json(j["endpoint"]),
                "inclusive": bool(j["inclusive"]), "direction": j["direction"]}
    if k == "bounded":
        return {"kind": "bounded", "variable": j["variable"], "lo": rat_from_json(j["lo"]), "hi": rat_from_json(j["hi"]),
                "loInclusive": bool(j["loInclusive"]), "hiInclusive": bool(j["hiInclusive"])}
    return {"kind": "reals-except", "variable": j["variable"], "points": [rat_from_json(p) for p in j["points"]]}


def interval_display(j: Dict[str, Any]) -> str:
    """Plain text: ``all real numbers``, ``x >= 2``, ``y < -1/2``, ``-1 <= y <= 4``, ``x != 3``, ``x != 1, 3``."""
    d = interval_from_json(j) if "endpoint" in j or "lo" in j or "points" in j or j.get("kind") == "reals" else j
    k = d["kind"]
    if k == "reals":
        return "all real numbers"
    v = d["variable"]
    if k == "ray":
        op = (">=" if d["inclusive"] else ">") if d["direction"] == "ge" else ("<=" if d["inclusive"] else "<")
        return f"{v} {op} {rat_display(d['endpoint'])}"
    if k == "bounded":
        lo_op = "<=" if d["loInclusive"] else "<"
        hi_op = "<=" if d["hiInclusive"] else "<"
        return f"{rat_display(d['lo'])} {lo_op} {v} {hi_op} {rat_display(d['hi'])}"
    return f"{v} != " + ", ".join(rat_display(p) for p in d["points"])


def same_set(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """Set equality ignoring the variable letter."""
    if a["kind"] != b["kind"]:
        return False
    k = a["kind"]
    if k == "reals":
        return True
    if k == "ray":
        return a["endpoint"] == b["endpoint"] and a["inclusive"] == b["inclusive"] and a["direction"] == b["direction"]
    if k == "bounded":
        return (a["lo"] == b["lo"] and a["hi"] == b["hi"] and a["loInclusive"] == b["loInclusive"]
                and a["hiInclusive"] == b["hiInclusive"])
    return sorted(a["points"]) == sorted(b["points"])


def check_interval(raw: str, canonical: Dict[str, Any], diagnostics: Sequence[Dict[str, Any]] = ()) -> Dict[str, Any]:
    """Grade a learner input against a canonical real-subset descriptor (JSON form).

    ``diagnostics``: optional [{misconceptionId, canonical}] wrong forms the item knows about.
    """
    code, got = parse_interval(raw)
    if got is None:
        return {"code": code}
    want = interval_from_json(canonical)
    expected_var = want.get("variable")
    if expected_var is not None and got.get("variable") is not None and got["variable"] != expected_var:
        return {"code": "wrong-variable"}
    if same_set(got, want):
        return {"code": "correct"}
    for d in diagnostics:
        if same_set(got, interval_from_json(d["canonical"])):
            return {"code": "misconception", "misconceptionId": d["misconceptionId"]}
    if got["kind"] != want["kind"]:
        return {"code": "wrong-kind"}
    k = want["kind"]
    if k == "ray":
        if got["direction"] != want["direction"]:
            return {"code": "wrong-direction"}
        if got["endpoint"] != want["endpoint"]:
            return {"code": "wrong-endpoint"}
        return {"code": "wrong-inclusivity"}
    if k == "bounded":
        if got["lo"] != want["lo"] or got["hi"] != want["hi"]:
            return {"code": "wrong-endpoint"}
        return {"code": "wrong-inclusivity"}
    return {"code": "wrong-endpoint"}  # reals-except with different points
