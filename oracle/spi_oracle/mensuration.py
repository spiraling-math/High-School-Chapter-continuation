"""gen.measurement.mensuration v1.0.0 — oracle reference (Perimeter, Area & Composite Shapes).

Eight middle-school mensuration tasks (owner A): perimeter of a rectangle; perimeter of a composite
rectilinear shape (L-shapes); area of a rectangle; area of a triangle from a shown base and
perpendicular height; area of a composite rectilinear shape by decomposition; a missing length from
a given perimeter; a missing rectangle dimension from a given area; a missing triangle base/height
from a given area. Independent Python reference; the TypeScript app mirrors it byte-for-byte
(canonical item + canonical dimensioned-figure SVG parity).

Discipline:
  * exact `Fraction` mathematics — never floats; no irrationals (no Pythagoras / surds / pi);
  * ONE canonical shape model (a discriminated union: rectangle / rectilinear_composite /
    triangle_base_height) drives the diagram, the dimension labels, the prompt, the dimensional-
    quantity answer, the worked solution, the misconception diagnostics, the accessibility text +
    data-table, and the independent validation (owner E);
  * every answer is a structured dimensional quantity (mensuration_units.Quantity), checked
    STRUCTURALLY (owner B/D); all eight tasks are FREE-RESPONSE only (owner C);
  * a canonical dimensioned-figure renderer (viewBox 0 0 1000 700, integer pixel coords via
    grid_round over exact Fraction, no trig, byte-identical Py/TS) built from a shared BASE-GEOMETRY
    fragment + STUDENT ANNOTATIONS, with the answer overlay added ONLY in the answer-key channel
    (owner J); the student figure shows only given dimensions and never the answer or a hidden side;
  * `Mulberry32` seeded generation with a bounded deterministic redraw loop;
  * direct-calculation tasks render to-scale; hidden-dimension (inverse) tasks render a normalized
    NOT-TO-SCALE diagram so the hidden value cannot be measured off the SVG (owner G);
  * an independent validator that rebuilds the shape from params, dispatches shape-specific
    invariants, recomputes the answer by a second route (composites: shoelace == decomposition),
    asserts the stored SVG byte-for-byte, and enforces the to-scale / answer-leakage / overlay-
    isolation contracts (owner G/H/J).

Deferred and deterministically excluded (owner brief): circles + pi; volume + surface area; general
triangle perimeter; trapezia + other non-rectilinear composites; Pythagoras + surds; unit
conversion; scale drawings; compound units; approximate measurements; irregular curved boundaries.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from seeded_random import Mulberry32  # noqa: E402
import mensuration_units as U  # noqa: E402
from mensuration_units import Quantity  # noqa: E402
from difficulty import band_from_score, clamp01, round3  # noqa: E402

GENERATOR_ID = "gen.measurement.mensuration"
GENERATOR_VERSION = "1.0.0"
VALIDATOR_VERSION = "1.0.0"
CALCULATOR_POLICY = "calculator-not-required"
SCHEMA_VERSION = "1.0.0"

# Single source of truth — mirrors core/curriculum/mensuration-objective-ids.ts (owner A).
TASKS = (
    "perimeter_rectangle",
    "perimeter_composite",
    "area_rectangle",
    "area_triangle",
    "area_composite",
    "missing_length_perimeter",
    "missing_dimension_area",
    "missing_triangle_base_height",
)
OBJECTIVE_BY_TASK = {
    "perimeter_rectangle": "SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01",
    "perimeter_composite": "SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01",
    "area_rectangle": "SPI.MIDDLE.MEAS.AREA.RECTANGLE.01",
    "area_triangle": "SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01",
    "area_composite": "SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01",
    "missing_length_perimeter": "SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01",
    "missing_dimension_area": "SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01",
    "missing_triangle_base_height": "SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01",
}
HIDDEN_DIMENSION_TASKS = ("missing_length_perimeter", "missing_dimension_area", "missing_triangle_base_height")
TRIANGLE_TASKS = ("area_triangle", "missing_triangle_base_height")
COMPOSITE_TASKS = ("perimeter_composite", "area_composite")
RATIONAL_ANSWER_TASKS = ("area_triangle", "missing_triangle_base_height")

# Provisional difficulty bands (owner L: confirmed reachable by the 10k distribution report).
TASK_BANDS = {
    "perimeter_rectangle": (1, 2),
    "perimeter_composite": (2, 3),
    "area_rectangle": (1, 2),
    "area_triangle": (2, 3),
    "area_composite": (3, 4),
    "missing_length_perimeter": (2, 3),
    "missing_dimension_area": (2, 3),
    "missing_triangle_base_height": (3, 4),
}

BASE_UNIT_POOL = ("mm", "cm", "m")
MAX_PARAM_ATTEMPTS = 600


def _n(rng: Mulberry32, k: int) -> int:
    return rng.next_int(0, k - 1)


def grid_round(num: int, den: int) -> int:
    """Round the exact rational num/den half-up toward +infinity. den > 0."""
    q, r = divmod(num, den)
    return q + 1 if 2 * r >= den else q


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


# --------------------------------------------------------------------------- #
# Canonical figure geometry (viewBox 0 0 1000 700).
# --------------------------------------------------------------------------- #
VIEW_W, VIEW_H = 1000, 700
SHAPE_X0, SHAPE_X1 = 320, 700        # horizontal band the shape is drawn in
SHAPE_Y0, SHAPE_Y1 = 200, 520        # top .. bottom (pixel y grows downward)
SHAPE_W = SHAPE_X1 - SHAPE_X0        # 380
SHAPE_H = SHAPE_Y1 - SHAPE_Y0        # 320
DIM_OFF = 40                         # dimension-line offset from an edge
DIM_OFF2 = 78                        # second-rank dimension offset (avoid collisions)
ARROW = 7                            # arrowhead half-length

STYLE = (
    ".cx-figure{font-family:'Segoe UI',system-ui,sans-serif}"
    ".cx-shape{fill:var(--cx-fill,#eef2f7);stroke:var(--cx-edge,#1b2733);stroke-width:3;stroke-linejoin:round}"
    ".cx-dimline{stroke:var(--cx-dim,#244);stroke-width:1.5}"
    ".cx-ext{stroke:var(--cx-dim,#244);stroke-width:1}"
    ".cx-arrow{fill:var(--cx-dim,#244)}"
    ".cx-rightangle{fill:none;stroke:var(--cx-edge,#1b2733);stroke-width:1.5}"
    ".cx-altitude{stroke:var(--cx-edge,#1b2733);stroke-width:1.5;stroke-dasharray:5 4}"
    ".cx-dimlbl{fill:var(--cx-dim,#244);font-size:19px}"
    ".cx-unknown{fill:var(--cx-unknown,#b91c1c);font-size:21px;font-weight:600}"
    ".cx-nts{fill:var(--cx-nts,#92400e);font-size:17px;font-weight:600;letter-spacing:1px}"
    ".cx-cut{stroke:var(--cx-cut,#2563eb);stroke-width:2;stroke-dasharray:6 4}"
    ".cx-result{fill:var(--cx-result,#166534);font-size:21px;font-weight:600}"
    ".cx-keylbl{fill:var(--cx-result,#166534);font-size:19px;font-weight:600}"
)


# --------------------------------------------------------------------------- #
# Shape model (discriminated union) — owner E
# --------------------------------------------------------------------------- #
def _rect_vertices(w: int, h: int) -> List[Tuple[Fraction, Fraction]]:
    """Counter-clockwise from the origin (bottom-left)."""
    return [(Fraction(0), Fraction(0)), (Fraction(w), Fraction(0)),
            (Fraction(w), Fraction(h)), (Fraction(0), Fraction(h))]


def _lshape_vertices(W: int, H: int, a: int, b: int, corner: str) -> List[Tuple[Fraction, Fraction]]:
    """A W×H rectangle with an a×b rectangular notch removed from one corner, traced
    counter-clockwise. `corner` ∈ {TL,TR,BL,BR}. a<W, b<H. Perimeter is always 2(W+H)."""
    f = Fraction
    if corner == "TR":
        pts = [(0, 0), (W, 0), (W, H - b), (W - a, H - b), (W - a, H), (0, H)]
    elif corner == "TL":
        pts = [(0, 0), (W, 0), (W, H), (a, H), (a, H - b), (0, H - b)]
    elif corner == "BR":
        pts = [(0, 0), (W - a, 0), (W - a, b), (W, b), (W, H), (0, H)]
    else:  # BL
        pts = [(a, 0), (W, 0), (W, H), (0, H), (0, b), (a, b)]
    return [(f(x), f(y)) for x, y in pts]


def _lshape_decomposition(W: int, H: int, a: int, b: int, corner: str, mode: str) -> List[Dict[str, Any]]:
    """Return the rectangles whose disjoint union (additive) or bounding-minus-notch (subtractive)
    equals the L-shape, each as {x0,y0,w,h,sign}. sign +1 add, -1 subtract."""
    if mode == "subtractive":
        notch = {"TR": (W - a, H - b), "TL": (0, H - b), "BR": (W - a, 0), "BL": (0, 0)}[corner]
        return [
            {"x0": 0, "y0": 0, "w": W, "h": H, "sign": 1},
            {"x0": notch[0], "y0": notch[1], "w": a, "h": b, "sign": -1},
        ]
    # additive: a full-width band + the remaining tab
    if corner == "TR":
        return [{"x0": 0, "y0": 0, "w": W, "h": H - b, "sign": 1},
                {"x0": 0, "y0": H - b, "w": W - a, "h": b, "sign": 1}]
    if corner == "TL":
        return [{"x0": 0, "y0": 0, "w": W, "h": H - b, "sign": 1},
                {"x0": a, "y0": H - b, "w": W - a, "h": b, "sign": 1}]
    if corner == "BR":
        return [{"x0": 0, "y0": b, "w": W, "h": H - b, "sign": 1},
                {"x0": 0, "y0": 0, "w": W - a, "h": b, "sign": 1}]
    return [{"x0": 0, "y0": b, "w": W, "h": H - b, "sign": 1},  # BL
            {"x0": a, "y0": 0, "w": W - a, "h": b, "sign": 1}]


def _build_shape(task: str, p: Dict[str, Any]) -> Dict[str, Any]:
    """The canonical shape model for an item (reconstructed purely from params)."""
    bu = p["baseUnit"]
    if p["kind"] == "rectangle":
        w, h = p["width"], p["height"]
        return {"kind": "rectangle", "baseUnit": bu, "width": w, "height": h,
                "vertices": _rect_vertices(w, h), "bbox": (w, h)}
    if p["kind"] == "rectilinear_composite":
        W, H, a, b, corner = p["W"], p["H"], p["a"], p["b"], p["corner"]
        return {"kind": "rectilinear_composite", "baseUnit": bu, "W": W, "H": H, "a": a, "b": b,
                "corner": corner, "decompMode": p["decompMode"],
                "vertices": _lshape_vertices(W, H, a, b, corner),
                "decomposition": _lshape_decomposition(W, H, a, b, corner, p["decompMode"]),
                "bbox": (W, H)}
    # triangle_base_height
    base, height, apex = p["base"], p["height"], p["apexOffset"]
    return {"kind": "triangle_base_height", "baseUnit": bu, "base": base, "height": height,
            "apexOffset": apex,
            "vertices": [(Fraction(0), Fraction(0)), (Fraction(base), Fraction(0)),
                         (Fraction(apex), Fraction(height))],
            "bbox": (base, height)}


# --------------------------------------------------------------------------- #
# Geometry math (independent routes) — owner H
# --------------------------------------------------------------------------- #
def _polygon_area_shoelace(verts: List[Tuple[Fraction, Fraction]]) -> Fraction:
    """Exact polygon area via the shoelace formula (technical validator only — owner I)."""
    n = len(verts)
    s = Fraction(0)
    for i in range(n):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def _polygon_perimeter(verts: List[Tuple[Fraction, Fraction]]) -> Fraction:
    """Exact exterior perimeter (axis-aligned edges -> |dx|+|dy| with one term zero)."""
    n = len(verts)
    per = Fraction(0)
    for i in range(n):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % n]
        per += abs(x2 - x1) + abs(y2 - y1)
    return per


def _is_closed_orthogonal_simple(verts: List[Tuple[Fraction, Fraction]]) -> Tuple[bool, str]:
    """Closure + axis-aligned edges + no zero-length/duplicate-consecutive + non-self-intersection
    for an axis-aligned rectilinear polygon."""
    n = len(verts)
    if n < 4:
        return False, "too few vertices"
    edges = []
    for i in range(n):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % n]
        if (x1, y1) == (x2, y2):
            return False, "zero-length edge / duplicate vertex"
        if x1 != x2 and y1 != y2:
            return False, "non-orthogonal edge"
        edges.append(((x1, y1), (x2, y2)))
    # Non-self-intersection: no two non-adjacent edges share a point (axis-aligned segment test).
    for i in range(n):
        for j in range(i + 1, n):
            if j == i or (i == 0 and j == n - 1) or j == i + 1:
                continue
            if _segments_touch(edges[i], edges[j]):
                return False, "self-intersection"
    return True, ""


def _segments_touch(e1, e2) -> bool:
    (ax1, ay1), (ax2, ay2) = e1
    (bx1, by1), (bx2, by2) = e2
    axlo, axhi = sorted((ax1, ax2)); aylo, ayhi = sorted((ay1, ay2))
    bxlo, bxhi = sorted((bx1, bx2)); bylo, byhi = sorted((by1, by2))
    ix_lo, ix_hi = max(axlo, bxlo), min(axhi, bxhi)
    iy_lo, iy_hi = max(aylo, bylo), min(ayhi, byhi)
    return ix_lo <= ix_hi and iy_lo <= iy_hi


def _rects_overlap(r1: Dict[str, Any], r2: Dict[str, Any]) -> bool:
    """True if two axis-aligned rectangles share positive-area interior."""
    ax0, ay0, ax1, ay1 = r1["x0"], r1["y0"], r1["x0"] + r1["w"], r1["y0"] + r1["h"]
    bx0, by0, bx1, by1 = r2["x0"], r2["y0"], r2["x0"] + r2["w"], r2["y0"] + r2["h"]
    return min(ax1, bx1) > max(ax0, bx0) and min(ay1, by1) > max(ay0, by0)


def _decomposition_area(decomp: List[Dict[str, Any]]) -> Fraction:
    return sum((Fraction(r["w"] * r["h"]) * r["sign"] for r in decomp), Fraction(0))


# --------------------------------------------------------------------------- #
# Backward construction — owner G (one guaranteed exact, uniquely-determined answer)
# --------------------------------------------------------------------------- #
_GOOD_RATIO = Fraction(7, 2)   # max bbox aspect ratio for to-scale figures (else redraw)


def _ratio_ok(w, h) -> bool:
    lo, hi = sorted((Fraction(w), Fraction(h)))
    return lo > 0 and hi / lo <= _GOOD_RATIO


def _draw_perimeter_rectangle(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    w = rng.next_int(3, 19); h = rng.next_int(2, 14)
    if w == h or not _ratio_ok(w, h):
        return None
    return {"task": "perimeter_rectangle", "kind": "rectangle", "baseUnit": _pick_unit(rng),
            "width": w, "height": h}


def _draw_area_rectangle(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    w = rng.next_int(3, 18); h = rng.next_int(2, 13)
    if not _ratio_ok(w, h):
        return None
    return {"task": "area_rectangle", "kind": "rectangle", "baseUnit": _pick_unit(rng),
            "width": w, "height": h}


def _draw_area_triangle(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    base = rng.next_int(3, 18); height = rng.next_int(2, 13)
    apex = rng.next_int(0, base)               # altitude foot on the base segment (owner E)
    if not _ratio_ok(base, height):
        return None
    return {"task": "area_triangle", "kind": "triangle_base_height", "baseUnit": _pick_unit(rng),
            "base": base, "height": height, "apexOffset": apex}


def _draw_lshape(rng: Mulberry32, task: str) -> Optional[Dict[str, Any]]:
    W = rng.next_int(8, 18); H = rng.next_int(6, 14)
    a = rng.next_int(2, W - 3); b = rng.next_int(2, H - 3)
    corner = ("TR", "TL", "BR", "BL")[_n(rng, 4)]
    mode = "subtractive" if _n(rng, 2) == 0 else "additive"
    if a >= W or b >= H or W - a < 2 or H - b < 2 or not _ratio_ok(W, H):
        return None
    return {"task": task, "kind": "rectilinear_composite", "baseUnit": _pick_unit(rng),
            "W": W, "H": H, "a": a, "b": b, "corner": corner, "decompMode": mode}


def _draw_missing_length_perimeter(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    w = rng.next_int(3, 18); h = rng.next_int(2, 14)
    if w == h:
        return None
    hidden = "height" if _n(rng, 2) == 0 else "width"
    return {"task": "missing_length_perimeter", "kind": "rectangle", "baseUnit": _pick_unit(rng),
            "width": w, "height": h, "given": "perimeter", "hidden": hidden,
            "perimeter": 2 * (w + h)}


def _draw_missing_dimension_area(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    w = rng.next_int(3, 18); h = rng.next_int(2, 13)
    if w == h:           # else the hidden side equals the given side (answer would be on the figure)
        return None
    hidden = "height" if _n(rng, 2) == 0 else "width"
    return {"task": "missing_dimension_area", "kind": "rectangle", "baseUnit": _pick_unit(rng),
            "width": w, "height": h, "given": "area", "hidden": hidden, "area": w * h}


def _draw_missing_triangle(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    base = rng.next_int(3, 18); height = rng.next_int(2, 13)
    apex = rng.next_int(0, base)
    if base == height:   # else the hidden measurement equals the given one (answer on the figure)
        return None
    hidden = "height" if _n(rng, 2) == 0 else "base"
    return {"task": "missing_triangle_base_height", "kind": "triangle_base_height",
            "baseUnit": _pick_unit(rng), "base": base, "height": height, "apexOffset": apex,
            "given": "area", "hidden": hidden, "area2": base * height}  # area2 = 2*area (exact int)


def _pick_unit(rng: Mulberry32) -> str:
    return BASE_UNIT_POOL[_n(rng, 3)]


_DRAW = {
    "perimeter_rectangle": _draw_perimeter_rectangle,
    "area_rectangle": _draw_area_rectangle,
    "area_triangle": _draw_area_triangle,
    "perimeter_composite": lambda r: _draw_lshape(r, "perimeter_composite"),
    "area_composite": lambda r: _draw_lshape(r, "area_composite"),
    "missing_length_perimeter": _draw_missing_length_perimeter,
    "missing_dimension_area": _draw_missing_dimension_area,
    "missing_triangle_base_height": _draw_missing_triangle,
}


# --------------------------------------------------------------------------- #
# Solver -> exact dimensional Quantity — owner F
# --------------------------------------------------------------------------- #
def _solve(task: str, p: Dict[str, Any]) -> Quantity:
    bu = p["baseUnit"]
    if task == "perimeter_rectangle":
        return U.make_length(2 * (p["width"] + p["height"]), bu)
    if task == "area_rectangle":
        return U.make_area(p["width"] * p["height"], bu)
    if task == "area_triangle":
        return U.make_area(Fraction(p["base"] * p["height"], 2), bu)
    if task == "perimeter_composite":
        return U.make_length(2 * (p["W"] + p["H"]), bu)
    if task == "area_composite":
        return U.make_area(p["W"] * p["H"] - p["a"] * p["b"], bu)
    if task == "missing_length_perimeter":
        known = p["width"] if p["hidden"] == "height" else p["height"]
        return U.make_length(Fraction(p["perimeter"], 2) - known, bu)
    if task == "missing_dimension_area":
        known = p["width"] if p["hidden"] == "height" else p["height"]
        return U.make_length(Fraction(p["area"], known), bu)
    if task == "missing_triangle_base_height":
        known = p["base"] if p["hidden"] == "height" else p["height"]
        return U.make_length(Fraction(p["area2"], known), bu)
    raise ValueError(task)


def _is_exact_acceptable(task: str, p: Dict[str, Any], q: Quantity) -> bool:
    """Owner F exactness policy + value positivity."""
    if q.value <= 0:
        return False
    if task in RATIONAL_ANSWER_TASKS:
        return True
    return q.value.denominator == 1  # integer-only tasks


# --------------------------------------------------------------------------- #
# Layout: shape coords -> integer pixels. To-scale for direct tasks; normalized
# schematic (NOT TO SCALE) for hidden-dimension tasks (owner G).
# --------------------------------------------------------------------------- #
def _layout(shape: Dict[str, Any], to_scale: bool) -> List[Tuple[int, int]]:
    verts = shape["vertices"]
    bw, bh = shape["bbox"]
    if to_scale:
        sx = Fraction(SHAPE_W, 1) / Fraction(bw)
        sy = Fraction(SHAPE_H, 1) / Fraction(bh)
        s = min(sx, sy)
        usedw = grid_round((Fraction(bw) * s).numerator, (Fraction(bw) * s).denominator)
        usedh = grid_round((Fraction(bh) * s).numerator, (Fraction(bh) * s).denominator)
        x0 = SHAPE_X0 + (SHAPE_W - usedw) // 2
        ybot = SHAPE_Y1 - (SHAPE_H - usedh) // 2
        out = []
        for (x, y) in verts:
            px = x0 + grid_round((x * s).numerator, (x * s).denominator)
            py = ybot - grid_round((y * s).numerator, (y * s).denominator)
            out.append((px, py))
        return out
    # Schematic (NOT TO SCALE): a FIXED canonical template per shape kind that ignores ALL actual
    # measurements, so no hidden length can be recovered by measuring the figure (owner G).
    fixed_w, fixed_h = 360, 250
    x0 = SHAPE_X0 + (SHAPE_W - fixed_w) // 2
    ybot = SHAPE_Y1 - (SHAPE_H - fixed_h) // 2
    if shape["kind"] == "rectangle":
        tmpl = [(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)),
                (Fraction(1), Fraction(1)), (Fraction(0), Fraction(1))]
    elif shape["kind"] == "triangle_base_height":
        tmpl = [(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)),
                (Fraction(2, 5), Fraction(1))]
    else:  # composites are never hidden-dimension tasks; fall back to proportional
        tmpl = [(Fraction(x, 1) / Fraction(bw), Fraction(y, 1) / Fraction(bh)) for (x, y) in verts]
    out = []
    for (fx, fy) in tmpl:
        px = x0 + grid_round((fx * fixed_w).numerator, (fx * fixed_w).denominator)
        py = ybot - grid_round((fy * fixed_h).numerator, (fy * fixed_h).denominator)
        out.append((px, py))
    return out


# --------------------------------------------------------------------------- #
# Dimension-rendering primitives — owner J
# --------------------------------------------------------------------------- #
def _arrow(out: List[str], x: int, y: int, dx: int, dy: int) -> None:
    """A small filled arrowhead at (x,y) pointing in (dx,dy) ∈ {(±1,0),(0,±1)} — distinct from a
    geometric vertex (it sits on a dimension line, not a shape corner)."""
    if dx != 0:
        tip = (x, y); back = x - dx * ARROW
        out.append(f'<polygon class="cx-arrow" points="{tip[0]},{tip[1]} {back},{y-4} {back},{y+4}"/>')
    else:
        tip = (x, y); back = y - dy * ARROW
        out.append(f'<polygon class="cx-arrow" points="{tip[0]},{tip[1]} {x-4},{back} {x+4},{back}"/>')


def _dim_h(out: List[str], x1: int, x2: int, yedge: int, off: int, label: str, cls: str = "cx-dimlbl") -> None:
    """Horizontal dimension between x1..x2 at pixel-y `yedge`, drawn `off` pixels below (off>0) or
    above (off<0) the edge, with extension lines + inward arrowheads + a centred label."""
    yd = yedge + off
    out.append(f'<line class="cx-ext" x1="{x1}" y1="{yedge}" x2="{x1}" y2="{yd + (4 if off>0 else -4)}"/>')
    out.append(f'<line class="cx-ext" x2="{x2}" y1="{yedge}" x1="{x2}" y2="{yd + (4 if off>0 else -4)}"/>')
    out.append(f'<line class="cx-dimline" x1="{x1}" y1="{yd}" x2="{x2}" y2="{yd}"/>')
    _arrow(out, x1, yd, 1, 0); _arrow(out, x2, yd, -1, 0)
    ty = yd - 8 if off > 0 else yd + 20
    out.append(f'<text class="{cls}" x="{(x1+x2)//2}" y="{ty}" text-anchor="middle">{_esc(label)}</text>')


def _dim_v(out: List[str], y1: int, y2: int, xedge: int, off: int, label: str, cls: str = "cx-dimlbl") -> None:
    """Vertical dimension between y1..y2 at pixel-x `xedge`, drawn `off` pixels right (off>0) or
    left (off<0) of the edge."""
    xd = xedge + off
    out.append(f'<line class="cx-ext" x1="{xedge}" y1="{y1}" x2="{xd + (4 if off>0 else -4)}" y2="{y1}"/>')
    out.append(f'<line class="cx-ext" x1="{xedge}" y2="{y2}" x2="{xd + (4 if off>0 else -4)}" y1="{y2}"/>')
    out.append(f'<line class="cx-dimline" x1="{xd}" y1="{y1}" x2="{xd}" y2="{y2}"/>')
    _arrow(out, xd, y1, 0, 1); _arrow(out, xd, y2, 0, -1)
    anchor = "start" if off > 0 else "end"
    tx = xd + 8 if off > 0 else xd - 8
    out.append(f'<text class="{cls}" x="{tx}" y="{(y1+y2)//2+6}" text-anchor="{anchor}">{_esc(label)}</text>')


def _right_angle(out: List[str], cx: int, cy: int, sx: int, sy: int, size: int = 14) -> None:
    """A right-angle marker square at corner (cx,cy); (sx,sy)∈{±1} aims the marker into the shape."""
    x1, y1 = cx + sx * size, cy
    x2, y2 = cx + sx * size, cy + sy * size
    x3, y3 = cx, cy + sy * size
    out.append(f'<polyline class="cx-rightangle" points="{x1},{y1} {x2},{y2} {x3},{y3}"/>')


def _label_value(value: int, unit: str) -> str:
    return f"{value} {unit}"


# --------------------------------------------------------------------------- #
# SVG channels: base geometry (shared) + student annotations + answer overlay (key only)
# --------------------------------------------------------------------------- #
def _base_group(task: str, p: Dict[str, Any], shape: Dict[str, Any], px: List[Tuple[int, int]]) -> List[str]:
    """The shape outline + structural markers — BYTE-IDENTICAL across student + answer-key (owner J)."""
    out: List[str] = ['<g class="cx-base">']
    pts = " ".join(f"{x},{y}" for x, y in px)
    out.append(f'<polygon class="cx-shape" points="{pts}"/>')
    if shape["kind"] == "triangle_base_height":
        # foot of the altitude on the base + the perpendicular-height marker + dashed altitude
        v0, v1, v2 = px
        footx = v2[0]; footy = v0[1]
        out.append(f'<line class="cx-altitude" x1="{footx}" y1="{footy}" x2="{v2[0]}" y2="{v2[1]}"/>')
        sx = 1 if v2[0] <= (v0[0] + v1[0]) // 2 else -1
        _right_angle(out, footx, footy, sx, -1, 13)
    elif shape["kind"] == "rectangle":
        x0 = min(x for x, _ in px); y1 = max(y for _, y in px)
        _right_angle(out, x0, y1, 1, -1, 13)
    out.append("</g>")
    return out


def _annot_group(task: str, p: Dict[str, Any], shape: Dict[str, Any], px: List[Tuple[int, int]]) -> List[str]:
    """Given-dimension labels (+ NOT TO SCALE banner for hidden-dim tasks). Shows ONLY given
    dimensions; never the answer or a hidden side (owner G/J). Identical across both channels."""
    out: List[str] = ['<g class="cx-annot">']
    unit = p["baseUnit"]
    kind = shape["kind"]
    if kind == "rectangle":
        (bx0, by0), (bx1, by1), (tx1, ty1), (tx0, ty0) = px
        w, h = p["width"], p["height"]
        hide = p.get("hidden")
        # bottom = width, right = height
        if hide != "width":
            _dim_h(out, bx0, bx1, by0, DIM_OFF, _label_value(w, unit))
        else:
            _dim_h(out, bx0, bx1, by0, DIM_OFF, "?", "cx-unknown")
        if hide != "height":
            _dim_v(out, ty1, by1, bx1, DIM_OFF, _label_value(h, unit))
        else:
            _dim_v(out, ty1, by1, bx1, DIM_OFF, "?", "cx-unknown")
    elif kind == "triangle_base_height":
        v0, v1, v2 = px
        base, height = p["base"], p["height"]
        hide = p.get("hidden")
        if hide != "base":
            _dim_h(out, v0[0], v1[0], v0[1], DIM_OFF, _label_value(base, unit))
        else:
            _dim_h(out, v0[0], v1[0], v0[1], DIM_OFF, "?", "cx-unknown")
        # height label beside the altitude
        footx = v2[0]
        if hide != "height":
            out.append(f'<text class="cx-dimlbl" x="{footx+10}" y="{(v0[1]+v2[1])//2}" text-anchor="start">{_esc(_label_value(height, unit))}</text>')
        else:
            out.append(f'<text class="cx-unknown" x="{footx+10}" y="{(v0[1]+v2[1])//2}" text-anchor="start">?</text>')
    else:  # rectilinear_composite — label the four defining edges; derived edges stay unlabelled
        _annot_composite(out, p, shape, px, unit)
    if task in HIDDEN_DIMENSION_TASKS:
        out.append(f'<text class="cx-nts" x="{VIEW_W//2}" y="170" text-anchor="middle">NOT TO SCALE</text>')
    out.append("</g>")
    return out


def _annot_composite(out: List[str], p: Dict[str, Any], shape: Dict[str, Any], px, unit: str) -> None:
    """Label the W (bottom), H (a full vertical side), and the two notch edges a,b; leave the two
    derived edges (W−a, H−b) unlabelled so the student derives them (owner: missing exterior length)."""
    W, H, a, b, corner = p["W"], p["H"], p["a"], p["b"], p["corner"]
    xs = [x for x, _ in px]; ys = [y for _, y in px]
    x_left, x_right = min(xs), max(xs)
    y_top, y_bot = min(ys), max(ys)
    _dim_h(out, x_left, x_right, y_bot, DIM_OFF, _label_value(W, unit))
    # a full-height side depends on the notch corner: pick the side with no notch
    full_left = corner in ("TR", "BR")
    if full_left:
        _dim_v(out, y_top, y_bot, x_left, -DIM_OFF, _label_value(H, unit))
    else:
        _dim_v(out, y_top, y_bot, x_right, DIM_OFF, _label_value(H, unit))
    # notch edges a (horizontal) and b (vertical) — the pair meeting at the reflex vertex
    _label_notch(out, px, shape["vertices"], a, b, unit)


def _label_notch(out: List[str], px, verts, a: int, b: int, unit: str) -> None:
    """Label the two indent (notch) edges — the pair meeting at the single reflex vertex, which is
    the unique vertex strictly interior to the bounding box. The horizontal one is a, vertical b."""
    xs = [x for x, _ in verts]; ys = [y for _, y in verts]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    r = next((i for i, (x, y) in enumerate(verts) if xmin < x < xmax and ymin < y < ymax), None)
    if r is None:
        return
    n = len(px)
    for j in (r - 1, r):  # the two edges incident to the reflex vertex
        x1, y1 = px[j % n]; x2, y2 = px[(j + 1) % n]
        midx, midy = (x1 + x2) // 2, (y1 + y2) // 2
        if y1 == y2:  # horizontal notch edge -> a
            out.append(f'<text class="cx-dimlbl" x="{midx}" y="{midy-8}" text-anchor="middle">{_esc(_label_value(a, unit))}</text>')
        else:         # vertical notch edge -> b
            out.append(f'<text class="cx-dimlbl" x="{midx+8}" y="{midy}" text-anchor="start">{_esc(_label_value(b, unit))}</text>')


def _overlay_group(task: str, p: Dict[str, Any], shape: Dict[str, Any], px, answer: Quantity) -> List[str]:
    """Answer-key ONLY: the missing side (for hidden-dim tasks), the decomposition cut line (for
    composite area), and the final result. Never emitted in the student channel (owner J)."""
    out: List[str] = ['<g class="cx-overlay">']
    unit = p["baseUnit"]
    kind = shape["kind"]
    if task in HIDDEN_DIMENSION_TASKS:
        val = U.format_value(answer.value)
        if kind == "rectangle":
            (bx0, by0), (bx1, by1), (tx1, ty1), (tx0, ty0) = px
            if p["hidden"] == "width":
                out.append(f'<text class="cx-keylbl" x="{(bx0+bx1)//2}" y="{by0+DIM_OFF-8}" text-anchor="middle">{_esc(_label_value(val, unit))}</text>')
            else:
                out.append(f'<text class="cx-keylbl" x="{bx1+DIM_OFF+8}" y="{(ty1+by1)//2+6}" text-anchor="start">{_esc(_label_value(val, unit))}</text>')
        elif kind == "triangle_base_height":
            v0, v1, v2 = px
            if p["hidden"] == "base":
                out.append(f'<text class="cx-keylbl" x="{(v0[0]+v1[0])//2}" y="{v0[1]+DIM_OFF-8}" text-anchor="middle">{_esc(_label_value(val, unit))}</text>')
            else:
                out.append(f'<text class="cx-keylbl" x="{v2[0]+10}" y="{(v0[1]+v2[1])//2}" text-anchor="start">{_esc(_label_value(val, unit))}</text>')
    if task == "area_composite":
        _overlay_cut(out, p, shape, px)
    out.append(f'<text class="cx-result" x="{VIEW_W//2}" y="{VIEW_H-40}" text-anchor="middle">{_esc(U.format_quantity(answer))}</text>')
    out.append("</g>")
    return out


def _overlay_cut(out: List[str], p: Dict[str, Any], shape: Dict[str, Any], px) -> None:
    """Dashed decomposition cut line for the additive split of an L-shape (answer key)."""
    # Cut between the two additive rectangles: a horizontal line at the notch height.
    decomp = _lshape_decomposition(p["W"], p["H"], p["a"], p["b"], p["corner"], "additive")
    # The shared edge is the top of the first (band) rectangle.
    r0 = decomp[0]
    bw, bh = shape["bbox"]
    xs = [x for x, _ in px]; ys = [y for _, y in px]
    x_left, x_right = min(xs), max(xs); y_bot = max(ys); y_top = min(ys)
    cut_frac = Fraction(r0["h"], bh)
    cy = y_bot - grid_round((cut_frac * (y_bot - y_top)).numerator, (cut_frac * (y_bot - y_top)).denominator)
    out.append(f'<line class="cx-cut" x1="{x_left}" y1="{cy}" x2="{x_right}" y2="{cy}"/>')


def _render(task: str, p: Dict[str, Any], shape: Dict[str, Any], answer: Quantity, channel: str, acc: Dict[str, Any]) -> str:
    to_scale = task not in HIDDEN_DIMENSION_TASKS
    px = _layout(shape, to_scale)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" role="img" class="cx-figure" aria-label="{_esc(acc["alt"])}">',
        f"<title>{_esc(acc['title'])}</title>",
        f"<desc>{_esc(acc['desc'])}</desc>",
        f"<style>{STYLE}</style>",
    ]
    out += _base_group(task, p, shape, px)
    out += _annot_group(task, p, shape, px)
    if channel == "answer-key":
        out += _overlay_group(task, p, shape, px, answer)
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------- #
# Prompt / solution / difficulty / accessibility
# --------------------------------------------------------------------------- #
_TASK_PROMPT = {
    "perimeter_rectangle": "Work out the perimeter of the rectangle shown. Give your answer in the correct units.",
    "perimeter_composite": "Work out the perimeter of the shape shown by adding the lengths around its outside. Give your answer in the correct units.",
    "area_rectangle": "Work out the area of the rectangle shown. Give your answer in the correct square units.",
    "area_triangle": "Work out the area of the triangle using its base and the perpendicular height shown. Give your answer in the correct square units.",
    "area_composite": "Work out the area of the shape shown by splitting it into rectangles. Give your answer in the correct square units.",
    "missing_length_perimeter": "The perimeter of the rectangle is given. Work out the missing side length marked “?”. Give your answer in the correct units.",
    "missing_dimension_area": "The area of the rectangle is given. Work out the missing side length marked “?”. Give your answer in the correct units.",
    "missing_triangle_base_height": "The area of the triangle is given. Work out the missing measurement marked “?”. Give your answer in the correct units.",
}


def _prompt(task: str, p: Dict[str, Any]) -> Dict[str, Any]:
    unit = p["baseUnit"]
    blocks = [{"kind": "media-ref", "ref": "fig-1"}]
    pre = ""
    if task == "missing_length_perimeter":
        pre = f"The perimeter of this rectangle is {2*(p['width']+p['height'])} {unit}. "
    elif task == "missing_dimension_area":
        pre = f"The area of this rectangle is {p['area']} {unit}^2. "
    elif task == "missing_triangle_base_height":
        pre = f"The area of this triangle is {U.format_value(Fraction(p['area2'],2))} {unit}^2. "
    instr = pre + _TASK_PROMPT[task]
    blocks.append({"kind": "text", "text": instr})
    return {"blocks": blocks, "instruction": instr}


def _solution(task: str, p: Dict[str, Any], answer: Quantity) -> Dict[str, Any]:
    """Student-facing worked solution (owner I): curriculum methods only, no shoelace; every
    solution ends with the exact result + the correct dimensional unit."""
    unit = p["baseUnit"]
    steps: List[Dict[str, Any]] = []
    final = U.format_quantity(answer)

    def step(t: str, r: str) -> None:
        steps.append({"number": len(steps) + 1, "transformation": t, "intermediateResult": r})

    if task == "perimeter_rectangle":
        w, h = p["width"], p["height"]
        step("Add the four side lengths", f"{w} + {h} + {w} + {h} {unit}")
        step("Or use 2 × (length + width)", f"2 × ({w} + {h}) = {final}")
    elif task == "area_rectangle":
        w, h = p["width"], p["height"]
        step("Multiply length by width", f"{w} × {h}")
        step("State the area in square units", final)
    elif task == "area_triangle":
        b, h = p["base"], p["height"]
        step("Multiply base by perpendicular height", f"{b} × {h} = {b*h}")
        step("Halve the product (½ × base × height)", final)
    elif task == "perimeter_composite":
        step("Find any unlabelled outer edge from the given lengths", "use width − part and height − part")
        step("Add every edge around the outside once (no inside lines)", final)
    elif task == "area_composite":
        W, H, a, b = p["W"], p["H"], p["a"], p["b"]
        if p["decompMode"] == "subtractive":
            step("Area of the surrounding rectangle", f"{W} × {H} = {W*H}")
            step("Subtract the missing corner rectangle", f"{W*H} − {a} × {b} = {final}")
        else:
            d = _lshape_decomposition(W, H, a, b, p["corner"], "additive")
            r0, r1 = d[0], d[1]
            step("Split into two rectangles and find each area", f"{r0['w']}×{r0['h']} and {r1['w']}×{r1['h']}")
            step("Add the rectangle areas", final)
    elif task == "missing_length_perimeter":
        known = p["width"] if p["hidden"] == "height" else p["height"]
        P = p["perimeter"]
        step("Halve the perimeter to get length + width", f"{P} ÷ 2 = {P//2}")
        step("Subtract the known side", f"{P//2} − {known} = {final}")
    elif task == "missing_dimension_area":
        known = p["width"] if p["hidden"] == "height" else p["height"]
        step("Divide the area by the known side", f"{p['area']} ÷ {known} = {final}")
    elif task == "missing_triangle_base_height":
        known = p["base"] if p["hidden"] == "height" else p["height"]
        step("Double the area (undo the ½)", f"2 × {U.format_value(Fraction(p['area2'],2))} = {p['area2']}")
        step("Divide by the known measurement", f"{p['area2']} ÷ {known} = {final}")
    return {"steps": steps}


# Per-task structural floors for the weighted difficulty axes (owner L: a single source of truth;
# ranges provisional until the 10k distribution report proves every declared band is reachable).
# numericalComplexity is computed from the actual numbers and spans ~0.05..0.19 of the score, which
# carries each task across exactly one band boundary so BOTH ends of its declared range are reached.
_AXIS_FLOORS = {
    "perimeter_rectangle":          {"reasoningSteps": 0.05, "interpretationDemand": 0.10, "informationDensity": 0.10},
    "area_rectangle":               {"reasoningSteps": 0.08, "interpretationDemand": 0.12, "informationDensity": 0.10},
    "area_triangle":                {"reasoningSteps": 0.45, "interpretationDemand": 0.35, "informationDensity": 0.25},
    "perimeter_composite":          {"reasoningSteps": 0.37, "interpretationDemand": 0.40, "informationDensity": 0.35},
    "area_composite":               {"reasoningSteps": 0.70, "interpretationDemand": 0.55, "informationDensity": 0.60},
    "missing_length_perimeter":     {"reasoningSteps": 0.40, "interpretationDemand": 0.40, "informationDensity": 0.25},
    "missing_dimension_area":       {"reasoningSteps": 0.40, "interpretationDemand": 0.40, "informationDensity": 0.25},
    "missing_triangle_base_height": {"reasoningSteps": 0.70, "interpretationDemand": 0.50, "informationDensity": 0.30},
}


def _difficulty(task: str, p: Dict[str, Any]) -> Dict[str, Any]:
    lo, hi = TASK_BANDS[task]
    fl = _AXIS_FLOORS[task]
    nmax = max(_task_numbers(p) or [1])
    numeric = clamp01((nmax - 2) / 18.0)
    axes = {
        "numericalComplexity": round3(numeric),
        "reasoningSteps": round3(fl["reasoningSteps"]),
        "interpretationDemand": round3(fl["interpretationDemand"]),
        "informationDensity": round3(fl["informationDensity"]),
        "representation": 0.5,
        "scaffolding": round3(0.4 if task in HIDDEN_DIMENSION_TASKS else 0.25),
    }
    # Weighted CLOSED-enum axes feed band_from_score (weights sum to 1.0), then clamp to the range.
    score = (0.40 * fl["reasoningSteps"] + 0.22 * fl["interpretationDemand"]
             + 0.20 * numeric + 0.18 * fl["informationDensity"])
    band = max(lo, min(hi, band_from_score(score)))
    return {"overallBand": band, "axes": axes}


def _task_numbers(p: Dict[str, Any]) -> List[int]:
    keys = ("width", "height", "base", "W", "H", "a", "b")
    return [int(p[k]) for k in keys if k in p]


# --------------------------------------------------------------------------- #
# Accessibility — owner 13 (data table lists GIVEN dims only; never the computed answer)
# --------------------------------------------------------------------------- #
def _accessibility(task: str, p: Dict[str, Any], shape: Dict[str, Any]) -> Dict[str, Any]:
    unit = p["baseUnit"]
    unit_word = {"mm": "millimetres", "cm": "centimetres", "m": "metres"}[unit]
    kind = shape["kind"]
    rows: List[Dict[str, str]] = []
    nts = " The figure is not drawn to scale." if task in HIDDEN_DIMENSION_TASKS else ""

    if kind == "rectangle":
        if p.get("hidden") != "width":
            rows.append({"label": "width", "value": f"{p['width']} {unit}"})
        if p.get("hidden") != "height":
            rows.append({"label": "height", "value": f"{p['height']} {unit}"})
        shape_word = "rectangle"
    elif kind == "triangle_base_height":
        if p.get("hidden") != "base":
            rows.append({"label": "base", "value": f"{p['base']} {unit}"})
        if p.get("hidden") != "height":
            rows.append({"label": "perpendicular height", "value": f"{p['height']} {unit}"})
        shape_word = "triangle with a perpendicular height marked"
    else:
        rows.append({"label": "overall width", "value": f"{p['W']} {unit}"})
        rows.append({"label": "overall height", "value": f"{p['H']} {unit}"})
        rows.append({"label": "notch width", "value": f"{p['a']} {unit}"})
        rows.append({"label": "notch height", "value": f"{p['b']} {unit}"})
        shape_word = "L-shaped composite rectilinear shape"

    if task == "missing_length_perimeter":
        rows.append({"label": "perimeter (given)", "value": f"{p['perimeter']} {unit}"})
    elif task == "missing_dimension_area":
        rows.append({"label": "area (given)", "value": f"{p['area']} {unit} squared"})
    elif task == "missing_triangle_base_height":
        rows.append({"label": "area (given)", "value": f"{U.format_value(Fraction(p['area2'],2))} {unit} squared"})

    given = "; ".join(f"{r['label']} {r['value']}" for r in rows)
    spoken = f"A {shape_word} measured in {unit_word}. Given measurements: {given}.{nts}"
    alt = f"A {shape_word} with labelled measurements."
    desc = spoken
    dataTable = {"caption": f"Given measurements of the {shape_word}",
                 "columns": ["measurement", "value"],
                 "rows": [[r["label"], r["value"]] for r in rows]}
    return {"spoken": spoken, "alt": alt, "desc": desc, "title": alt, "dataTable": dataTable}


# --------------------------------------------------------------------------- #
# Generate
# --------------------------------------------------------------------------- #
class UnsupportedInteractionError(ValueError):
    """Raised when a multiple-choice item is requested (owner C: FR-only in v1.0.0)."""


def generate(seed: int, task: Optional[str] = None, interaction: str = "free-response") -> Dict[str, Any]:
    if interaction != "free-response":
        raise UnsupportedInteractionError(
            f"gen.measurement.mensuration v1.0.0 supports only free-response; got '{interaction}'.")
    pool = [task] if task else list(TASKS)
    rng = Mulberry32(seed)
    chosen: Optional[Dict[str, Any]] = None
    answer: Optional[Quantity] = None
    for _ in range(MAX_PARAM_ATTEMPTS):
        t = pool[_n(rng, len(pool))]
        drawn = _DRAW[t](rng)
        if drawn is None:
            continue
        q = _solve(t, drawn)
        if not _is_exact_acceptable(t, drawn, q):
            continue
        chosen, answer = drawn, q
        break
    if chosen is None or answer is None:
        raise RuntimeError("could not find acceptable mensuration parameters")

    t = chosen["task"]
    shape = _build_shape(t, chosen)
    acc = _accessibility(t, chosen, shape)
    student_svg = _render(t, chosen, shape, answer, "student", acc)
    key_svg = _render(t, chosen, shape, answer, "answer-key", acc)

    item: Dict[str, Any] = {
        "itemId": f"ITEM-{GENERATOR_ID.replace('.', '-')}-{seed}-{t}",
        "schemaVersion": SCHEMA_VERSION,
        "objectiveIds": [OBJECTIVE_BY_TASK[t]],
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "seed": seed,
        "params": dict(chosen),
        "interactionType": "free-response",
        "prompt": _prompt(t, chosen),
        "answer": U.encode_quantity_answer(answer),
        "solution": _solution(t, chosen, answer),
        "difficulty": _difficulty(t, chosen),
        "calculatorPolicy": CALCULATOR_POLICY,
        "media": [{
            "id": "fig-1", "kind": "svg", "svg": student_svg,
            "toScale": t not in HIDDEN_DIMENSION_TASKS,
            "altText": acc["alt"], "longDescription": acc["spoken"],
            "dataTableFallback": acc["dataTable"],
            "spec": {"answerKeySvg": key_svg, "notToScale": t in HIDDEN_DIMENSION_TASKS},
        }],
        "accessibility": {"spokenMath": acc["spoken"], "altText": acc["alt"],
                          "longDescription": acc["spoken"], "nonColorIndicators": True},
        "provenance": {"origin": "generated", "rightsStatus": "academy-owned",
                       "originalityNote": "Original parameterized item; the figure is generated from the same shape model."},
        "lifecycle": {"state": "generated"},
    }
    return item


def serialize(item: Dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def describe() -> Dict[str, Any]:
    return {
        "id": GENERATOR_ID, "version": GENERATOR_VERSION,
        "title": "Mensuration — perimeter, area & composite shapes",
        "domain": "measurement",
        "objectiveIds": [OBJECTIVE_BY_TASK[t] for t in TASKS],
        "interactionTypes": ["free-response"],
        "answerTypes": ["quantity"],
        "tasks": list(TASKS),
        "difficultyRanges": {OBJECTIVE_BY_TASK[t]: list(TASK_BANDS[t]) for t in TASKS},
    }


def render(item: Dict[str, Any], mode: str = "full") -> str:
    lines = [b.get("text") or f"[figure {b.get('ref')}]" for b in item["prompt"]["blocks"]]
    if mode == "answer-only":
        return f"Answer: {item['answer']['display']}"
    out = list(lines)
    if mode == "full":
        out += ["", "Solution:"]
        for s in item["solution"]["steps"]:
            out.append(f"  {s['number']}. {s.get('transformation','')}: {s.get('intermediateResult','')}")
    out.append(f"Answer: {item['answer']['display']}")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Independent validator — owner G/H/J
# --------------------------------------------------------------------------- #
def validate(item: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "result": "pass" if ok else "fail", "detail": detail})

    p = item["params"]
    task = p["task"]
    add("objective-mapping", item.get("objectiveIds") == [OBJECTIVE_BY_TASK.get(task)], str(item.get("objectiveIds")))
    add("interaction-free-response-only", item.get("interactionType") == "free-response", str(item.get("interactionType")))

    # Rebuild the shape + recompute the answer independently.
    shape = _build_shape(task, p)
    answer = _solve(task, p)
    ans = item["answer"]

    # Answer contract (structural).
    enc = U.encode_quantity_answer(answer)
    add("answer-type-quantity", ans.get("type") == "quantity", str(ans.get("type")))
    add("answer-canonical-matches", ans.get("canonical") == enc["canonical"], str(ans.get("canonical")))
    add("answer-measure-matches", ans.get("measure") == enc["measure"], str(ans.get("measure")))
    add("answer-display-derived", ans.get("display") == enc["display"], str(ans.get("display")))
    add("answer-exactness-policy", _is_exact_acceptable(task, p, answer), U.format_quantity(answer))
    add("answer-no-legacy-units", "units" not in ans, "legacy units must not appear on a quantity answer")

    # Shape-specific invariants (dispatched by kind — owner E).
    verts = shape["vertices"]
    if shape["kind"] == "rectangle":
        add("rectangle-positive", p["width"] > 0 and p["height"] > 0, f"{p['width']}x{p['height']}")
        add("rectangle-closed-rect", len(verts) == 4, str(len(verts)))
    elif shape["kind"] == "rectilinear_composite":
        ok_closed, why = _is_closed_orthogonal_simple(verts)
        add("composite-closed-orthogonal-simple", ok_closed, why)
        # exterior perimeter from the boundary
        per = _polygon_perimeter(verts)
        add("composite-exterior-perimeter", per == 2 * (p["W"] + p["H"]), str(per))
        # decomposition: non-overlapping (additive) + union == polygon area; two area routes agree
        decomp = shape["decomposition"]
        adds = [r for r in decomp if r["sign"] > 0]
        overlap = any(_rects_overlap(adds[i], adds[j]) for i in range(len(adds)) for j in range(i + 1, len(adds)))
        add("composite-decomposition-non-overlapping", not overlap, "additive rectangles must be disjoint")
        shoe = _polygon_area_shoelace(verts)
        deco = _decomposition_area(decomp)
        add("composite-shoelace-equals-decomposition", shoe == deco == (p["W"] * p["H"] - p["a"] * p["b"]), f"shoelace={shoe} decomp={deco}")
    else:  # triangle
        base, height, apex = p["base"], p["height"], p["apexOffset"]
        add("triangle-non-collinear", height > 0 and base > 0, f"{base}x{height}")
        add("triangle-foot-on-base", 0 <= apex <= base, str(apex))
        # area by base*height/2 and the inverse route reproduce each other
        area = Fraction(base * height, 2)
        add("triangle-area-half-base-height", _polygon_area_shoelace(verts) == area, str(area))

    # Missing-dimension uniqueness + substitution (owner H).
    if task in HIDDEN_DIMENSION_TASKS:
        add("missing-one-unknown", p.get("hidden") in ("width", "height", "base"), str(p.get("hidden")))
        add("missing-substitution-restores", _substitution_restores(task, p, answer), "given must be restored")

    # Figure contract (owner G/J).
    media = item["media"][0]
    student_svg = media["svg"]
    key_svg = media["spec"]["answerKeySvg"]
    add("svg-realises-data-student", student_svg == _render(task, p, shape, answer, "student", _accessibility(task, p, shape)), "byte parity")
    add("svg-realises-data-key", key_svg == _render(task, p, shape, answer, "answer-key", _accessibility(task, p, shape)), "byte parity")

    base_s = _extract_group(student_svg, "cx-base"); base_k = _extract_group(key_svg, "cx-base")
    annot_s = _extract_group(student_svg, "cx-annot"); annot_k = _extract_group(key_svg, "cx-annot")
    add("answer-key-base-geometry-identical", base_s == base_k and base_s != "", "base geometry must be byte-identical across channels")
    add("answer-key-overlay-additive-only", annot_s == annot_k, "student annotations must be unchanged in the key channel")
    add("student-figure-has-no-overlay", "cx-overlay" not in student_svg, "student figure must not contain an answer overlay")
    add("answer-key-has-overlay", "cx-overlay" in key_svg, "answer key must add the overlay group")

    # Answer-leakage (owner G): the exact answer must not appear as a STANDALONE label in the
    # student figure or a11y. A token-aware test (digit/superscript boundaries) so that a hidden
    # answer like "8 mm" is not falsely flagged when it is only a substring of a GIVEN value such
    # as the perimeter "28 mm" or area "55 cm squared".
    ans_str = U.format_quantity(answer)
    add("no-result-in-student-figure", not _has_quantity_token(student_svg, ans_str), ans_str)
    add("student-a11y-does-not-state-result", not _has_quantity_token(item["accessibility"]["spokenMath"], ans_str), "spoken math must not state the computed answer")

    # To-scale policy + NOT-TO-SCALE banner (owner G).
    should_scale = task not in HIDDEN_DIMENSION_TASKS
    add("to-scale-policy-matches-task", bool(media.get("toScale")) == should_scale, str(media.get("toScale")))
    if not should_scale:
        add("not-to-scale-banner-present", "NOT TO SCALE" in student_svg, "hidden-dimension figures must be marked NOT TO SCALE")
        add("hidden-dimension-not-measurable-from-svg", _hidden_not_measurable(task, p, student_svg), "schematic pixels must not encode the hidden length")

    overall = "pass" if all(c["result"] == "pass" for c in checks) else "fail"
    return {"status": overall, "validatorVersion": VALIDATOR_VERSION, "checks": checks}


def _substitution_restores(task: str, p: Dict[str, Any], answer: Quantity) -> bool:
    v = answer.value
    if task == "missing_length_perimeter":
        known = p["width"] if p["hidden"] == "height" else p["height"]
        return 2 * (v + known) == p["perimeter"]
    if task == "missing_dimension_area":
        known = p["width"] if p["hidden"] == "height" else p["height"]
        return v * known == p["area"]
    if task == "missing_triangle_base_height":
        known = p["base"] if p["hidden"] == "height" else p["height"]
        return v * known == p["area2"]
    return False


def _hidden_not_measurable(task: str, p: Dict[str, Any], svg: str) -> bool:
    """The schematic uses a FIXED pixel box independent of true lengths, so the hidden value cannot
    be recovered by measuring the SVG. Confirm the schematic layout does not scale with the hidden
    value: re-render with the hidden value perturbed and require identical base geometry."""
    shape = _build_shape(task, p)
    px_a = _layout(shape, to_scale=False)
    p2 = dict(p)
    if p2["hidden"] in ("height", "width") and shape["kind"] == "rectangle":
        p2["width"], p2["height"] = p2["width"] + 3, p2["height"] + 5
    elif shape["kind"] == "triangle_base_height":
        p2["base"], p2["height"] = p2["base"] + 3, p2["height"] + 5
    px_b = _layout(_build_shape(task, p2), to_scale=False)
    return px_a == px_b  # fixed schematic -> identical pixels regardless of the actual lengths


def _has_quantity_token(text: str, qstr: str) -> bool:
    """True if qstr (e.g. '8 mm' or '24 cm^2') appears as a standalone quantity — not preceded by a
    digit (so '8 mm' inside '28 mm' does not count) and not extended into a larger unit (so the
    length '8 mm' is not matched inside the area '8 mm^2')."""
    pat = r"(?<!\d)" + re.escape(qstr) + r"(?!\s*squared)(?![\d²])(?!\^2)"
    return re.search(pat, text) is not None


def _extract_group(svg: str, cls: str) -> str:
    open_tag = f'<g class="{cls}">'
    i = svg.find(open_tag)
    if i < 0:
        return ""
    depth = 0
    j = i
    while j < len(svg):
        if svg.startswith("<g", j):
            depth += 1
        elif svg.startswith("</g>", j):
            depth -= 1
            if depth == 0:
                return svg[i:j + 4]
        j += 1
    return ""
