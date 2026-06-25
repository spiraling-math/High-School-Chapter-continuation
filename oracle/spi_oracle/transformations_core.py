"""gen.geometry.transformations — exact transformation engine, descriptor model, parser,
canonicalizer, formatter, and the single result-code vocabulary (owner F, I, J).

EXACTNESS (owner F): every coordinate is an integer; the engine uses only integer add / negate /
swap. There is NO runtime trigonometry, floating point, tolerance, or irrational coordinate anywhere.

CANONICAL-FIRST DESCRIPTOR (owner C): the structured descriptor IS answer.canonical — a discriminated
union {kind: translation|reflection|rotation}. answer.display is DERIVED from it (format_display); the
descriptor is never stored twice and a formatted string is never used as the canonical value. Canonical
display uses ASCII "deg" (a screen renderer may show the degree symbol).

This module is the oracle; domains/geometry/transformations-core.ts mirrors it byte-for-byte.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

Point = Tuple[int, int]


# --------------------------------------------------------------------------- #
# The ONE result-code vocabulary (owner J). Python + TypeScript share this exact list.
# --------------------------------------------------------------------------- #
RESULT_CODES: Tuple[str, ...] = (
    "correct",
    "wrong-transformation-type",
    "wrong-translation-vector",
    "wrong-reflection-axis",
    "wrong-rotation-centre",
    "wrong-rotation-amount",
    "ambiguous-description",
    "missing-rotation-centre",
    "missing-translation-vector",
    "unsupported-reflection-line",
    "unsupported-angle",
    "contradictory-description",
    "unparsed-trailing-text",
    "malformed-response",
)

QUARTER_DEGREES: Dict[int, int] = {1: 90, 2: 180, 3: 270}


# --------------------------------------------------------------------------- #
# Exact engine (owner F)
# --------------------------------------------------------------------------- #
def apply_translation(p: Point, dx: int, dy: int) -> Point:
    return (p[0] + dx, p[1] + dy)


def reflect_x_eq_a(p: Point, a: int) -> Point:
    return (2 * a - p[0], p[1])


def reflect_y_eq_b(p: Point, b: int) -> Point:
    return (p[0], 2 * b - p[1])


def reflect_y_eq_x(p: Point) -> Point:
    return (p[1], p[0])


def reflect_y_eq_negx(p: Point) -> Point:
    return (-p[1], -p[0])


def rotate_quarter(p: Point, h: int, k: int, q: int) -> Point:
    """Rotate p by q quarter-turns ANTICLOCKWISE about (h, k). q in {1,2,3}.
    Translate to centre, apply the exact quarter-turn, translate back (owner F)."""
    x, y = p[0] - h, p[1] - k
    if q == 1:
        nx, ny = -y, x
    elif q == 2:
        nx, ny = -x, -y
    elif q == 3:
        nx, ny = y, -x
    else:
        raise ValueError(f"quarterTurnsCCW must be 1, 2, or 3 (got {q})")
    return (nx + h, ny + k)


def apply_transform(desc: Dict[str, Any], p: Point) -> Point:
    """Apply a canonical descriptor to an integer point. The single forward engine entry point.
    The independent validator must NOT call this (owner H)."""
    kind = desc["kind"]
    if kind == "translation":
        v = desc["vector"]
        return apply_translation(p, v["dx"], v["dy"])
    if kind == "reflection":
        ax = desc["axis"]
        if ax["kind"] == "vertical":
            return reflect_x_eq_a(p, ax["value"])
        if ax["kind"] == "horizontal":
            return reflect_y_eq_b(p, ax["value"])
        if ax["kind"] == "diagonal":
            return reflect_y_eq_x(p) if ax["equation"] == "y=x" else reflect_y_eq_negx(p)
        raise ValueError(f"unsupported axis kind {ax['kind']!r}")
    if kind == "rotation":
        c = desc["centre"]
        return rotate_quarter(p, c["x"], c["y"], desc["quarterTurnsCCW"])
    raise ValueError(f"unsupported transformation kind {kind!r}")


# --------------------------------------------------------------------------- #
# Descriptor constructors + canonicalizer (owner C, I)
# --------------------------------------------------------------------------- #
def translation_desc(dx: int, dy: int) -> Dict[str, Any]:
    if dx == 0 and dy == 0:
        raise ValueError("translation vector must be nonzero (owner C)")
    return {"kind": "translation", "vector": {"dx": int(dx), "dy": int(dy)}}


def reflection_vertical(a: int) -> Dict[str, Any]:
    return {"kind": "reflection", "axis": {"kind": "vertical", "value": int(a)}}


def reflection_horizontal(b: int) -> Dict[str, Any]:
    return {"kind": "reflection", "axis": {"kind": "horizontal", "value": int(b)}}


def reflection_diagonal(equation: str) -> Dict[str, Any]:
    if equation not in ("y=x", "y=-x"):
        raise ValueError("diagonal equation must be 'y=x' or 'y=-x'")
    return {"kind": "reflection", "axis": {"kind": "diagonal", "equation": equation}}


def rotation_desc(h: int, k: int, q: int) -> Dict[str, Any]:
    if q not in (1, 2, 3):
        raise ValueError("quarterTurnsCCW must be 1, 2, or 3")
    return {"kind": "rotation", "centre": {"x": int(h), "y": int(k)}, "quarterTurnsCCW": int(q)}


def canonicalize_descriptor(desc: Dict[str, Any]) -> Dict[str, Any]:
    """Return a normalized copy with keys in canonical order. Axis aliases (x-axis<->y=0,
    y-axis<->x=0) and the origin / quarter-turn direction are already normalized at construction
    or parse time; this enforces the canonical shape so equality is structural."""
    kind = desc["kind"]
    if kind == "translation":
        v = desc["vector"]
        return translation_desc(v["dx"], v["dy"])
    if kind == "reflection":
        ax = desc["axis"]
        if ax["kind"] == "vertical":
            return reflection_vertical(ax["value"])
        if ax["kind"] == "horizontal":
            return reflection_horizontal(ax["value"])
        return reflection_diagonal(ax["equation"])
    if kind == "rotation":
        c = desc["centre"]
        return rotation_desc(c["x"], c["y"], desc["quarterTurnsCCW"])
    raise ValueError(f"unsupported kind {kind!r}")


def descriptors_equal(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    return canonicalize_descriptor(a) == canonicalize_descriptor(b)


# --------------------------------------------------------------------------- #
# Display formatter (owner C, I). ASCII "deg"; the descriptor is the source of truth.
# --------------------------------------------------------------------------- #
def _axis_equation(ax: Dict[str, Any]) -> str:
    if ax["kind"] == "vertical":
        return f"x = {ax['value']}"
    if ax["kind"] == "horizontal":
        return f"y = {ax['value']}"
    return "y = x" if ax["equation"] == "y=x" else "y = -x"


def format_display(desc: Dict[str, Any]) -> str:
    kind = desc["kind"]
    if kind == "translation":
        v = desc["vector"]
        return f"translation by vector ({v['dx']}, {v['dy']})"
    if kind == "reflection":
        return f"reflection in {_axis_equation(desc['axis'])}"
    if kind == "rotation":
        c = desc["centre"]
        q = desc["quarterTurnsCCW"]
        deg = QUARTER_DEGREES[q]
        direction = "" if q == 2 else " anticlockwise"
        return f"rotation {deg} deg{direction} about ({c['x']}, {c['y']})"
    raise ValueError(f"unsupported kind {kind!r}")


def answer_object(desc: Dict[str, Any]) -> Dict[str, Any]:
    """The canonical-first answer object (owner C): the descriptor IS answer.canonical; display is
    derived; no units/measure/tolerance."""
    canon = canonicalize_descriptor(desc)
    return {"type": "transformation", "canonical": canon, "display": format_display(canon)}


# --------------------------------------------------------------------------- #
# Anchored parser + canonicalizer (owner I). Finite grammar, NOT free-form NLP.
# Returns (descriptor | None, result_code). result_code is None on a clean parse, otherwise one of
# the parse-level RESULT_CODES. The checker (transformations_checker) compares a clean parse to the
# expected descriptor to assign correct / wrong-* codes.
# --------------------------------------------------------------------------- #
_INT = r"[+-]?\d+"


def _norm(text: str) -> str:
    s = text.strip().lower()
    s = s.replace("−", "-").replace("–", "-").replace("—", "-")  # unicode minus/dashes
    s = s.replace("°", " deg ")  # degree sign -> deg
    s = s.replace("counterclockwise", "anticlockwise").replace("counter-clockwise", "anticlockwise")
    s = s.replace("anti-clockwise", "anticlockwise")
    s = s.replace("center", "centre")
    s = s.replace("half-turn", "half turn")
    s = re.sub(r"\bdegrees?\b", "deg", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _parse_vector(s: str) -> Optional[Tuple[int, int]]:
    m = re.fullmatch(rf"\(\s*({_INT})\s*,\s*({_INT})\s*\)", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.fullmatch(rf"\[\s*({_INT})\s*;\s*({_INT})\s*\]", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def _parse_centre(s: str) -> Optional[Tuple[int, int]]:
    s = s.strip()
    if s in ("the origin", "origin"):
        return (0, 0)
    m = re.fullmatch(rf"\(\s*({_INT})\s*,\s*({_INT})\s*\)", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


class ParseResult:
    __slots__ = ("descriptor", "code")

    def __init__(self, descriptor: Optional[Dict[str, Any]], code: Optional[str]):
        self.descriptor = descriptor
        self.code = code


def parse_descriptor(text: str) -> ParseResult:
    """Parse a learner description into a canonical descriptor or a parse-level result code."""
    if text is None or not str(text).strip():
        return ParseResult(None, "malformed-response")
    s = _norm(text)

    # Contradictory direction (both senses named).
    if "clockwise" in s and "anticlockwise" in s.replace("anticlockwise", "@") and "anticlockwise" in s:
        pass  # handled below after structural parse
    if re.search(r"\bclockwise\b", s) and re.search(r"\banticlockwise\b", s):
        return ParseResult(None, "contradictory-description")

    # --- translation ---------------------------------------------------------
    m = re.fullmatch(r"(?:translation|translate)(?: by)?(?: the column)?(?: vector)?\s*(.*)", s)
    if m:
        rest = m.group(1).strip()
        if not rest:
            return ParseResult(None, "missing-translation-vector")
        vec = _parse_vector(rest)
        if vec is None:
            # trailing junk after a vector?
            mv = re.match(rf"(\([^)]*\)|\[[^\]]*\])", rest)
            if mv and _parse_vector(mv.group(1)):
                return ParseResult(None, "unparsed-trailing-text")
            return ParseResult(None, "missing-translation-vector")
        if vec == (0, 0):
            return ParseResult(None, "contradictory-description")  # a 'translation' that moves nothing
        return ParseResult(translation_desc(vec[0], vec[1]), None)

    # --- reflection ----------------------------------------------------------
    m = re.fullmatch(r"reflection in (?:the )?(.*)", s)
    if m:
        line = m.group(1).strip().rstrip(".")
        return _parse_reflection_line(line)

    # --- rotation / half turn -----------------------------------------------
    if s.startswith("rotation") or s.startswith("half turn") or s.startswith("rotate"):
        return _parse_rotation(s)

    return ParseResult(None, "malformed-response")


def _parse_reflection_line(line: str) -> ParseResult:
    line = re.sub(r"\s*=\s*", "=", line)
    if line in ("x-axis", "x axis"):
        return ParseResult(reflection_horizontal(0), None)  # x-axis is y = 0
    if line in ("y-axis", "y axis"):
        return ParseResult(reflection_vertical(0), None)    # y-axis is x = 0
    m = re.fullmatch(rf"x=({_INT})", line)
    if m:
        return ParseResult(reflection_vertical(int(m.group(1))), None)
    m = re.fullmatch(rf"y=({_INT})", line)
    if m:
        return ParseResult(reflection_horizontal(int(m.group(1))), None)
    if line in ("y=x",):
        return ParseResult(reflection_diagonal("y=x"), None)
    if line in ("y=-x",):
        return ParseResult(reflection_diagonal("y=-x"), None)
    if not line:
        return ParseResult(None, "unsupported-reflection-line")
    return ParseResult(None, "unsupported-reflection-line")


def _parse_rotation(s: str) -> ParseResult:
    half = s.startswith("half turn")
    # angle
    q: Optional[int] = None
    if half:
        q = 2
    else:
        ma = re.search(rf"({_INT})\s*deg", s)
        if ma is None:
            # rotation with a centre but no angle is ambiguous; with neither -> ambiguous too.
            if re.search(r"about", s):
                return ParseResult(None, "ambiguous-description")
            return ParseResult(None, "ambiguous-description")
        ang = int(ma.group(1)) % 360
        cw = bool(re.search(r"\bclockwise\b", s))
        acw = bool(re.search(r"\banticlockwise\b", s))
        if ang == 180:
            q = 2
        elif ang == 90:
            q = 3 if cw else 1
        elif ang == 270:
            q = 1 if cw else 3
        else:
            return ParseResult(None, "unsupported-angle")
        if ang in (90, 270) and not cw and not acw:
            return ParseResult(None, "ambiguous-description")  # direction required for a quarter turn
    # centre
    mc = re.search(r"about\s+(.*)$", s)
    if mc is None:
        return ParseResult(None, "missing-rotation-centre")
    centre = _parse_centre(mc.group(1).strip().rstrip("."))
    if centre is None:
        return ParseResult(None, "missing-rotation-centre")
    return ParseResult(rotation_desc(centre[0], centre[1], q), None)
