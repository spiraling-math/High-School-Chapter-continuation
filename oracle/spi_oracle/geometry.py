"""Geometry (angles) generator with mathematically generated SVG diagrams.

Generator id : gen.geometry.angles-figures
Version      : 1.0.0
Stage        : SPI-Math Middle School -> Geometry -> Ch.21 (Angles, Lines, Triangles)
Spec         : docs/GENERATOR_SPEC_geometry_svg_proposal.md (owner-approved core + revisions)

v1.0.0 families (integer-degree answers only):
  F1 straight_line_missing_angle, F2 triangle_missing_angle / isosceles_base_angle,
  F3 vertically_opposite_angle / angles_at_point_missing.

The diagram IS the question: every figure is computed from the SAME params as the
prompt and answer (single source of truth). Ray directions come from a COMMITTED
integer direction table (no runtime sin/cos); coordinates are integers produced by a
single round-half-up rule; the SVG is hand-serialized canonically so it is
byte-for-byte identical between this oracle and the TypeScript mirror. Figures are
toScale:false with a visible NOT TO SCALE indicator. Mirrors domains/geometry/linear?
-> domains/geometry/angles.ts.
"""

from __future__ import annotations

import json
import os
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from .seeded_random import Mulberry32
from .difficulty import round3
from .geometry_misconceptions import MISCONCEPTIONS, rules_for

GENERATOR_ID = "gen.geometry.angles-figures"
GENERATOR_VERSION = "1.2.2"

_HERE = os.path.dirname(os.path.abspath(__file__))
_TABLE = json.load(open(os.path.join(_HERE, "..", "..", "core", "geometry", "dir-table.json"), encoding="utf-8"))
R: int = _TABLE["R"]
DIR: List[List[int]] = _TABLE["dir"]

TASKS = ("straight_line_missing_angle", "triangle_missing_angle", "isosceles_base_angle",
         "vertically_opposite_angle", "angles_at_point_missing")
MC_TASKS = ("straight_line_missing_angle", "triangle_missing_angle", "isosceles_base_angle",
            "angles_at_point_missing")  # vertically_opposite is free-response only in the current approved scope

OBJECTIVE_BY_TASK = {
    "straight_line_missing_angle": "SPI.MIDDLE.GEO.ANGLES_STRAIGHT_LINE.01",
    "triangle_missing_angle": "SPI.MIDDLE.GEO.TRIANGLE_ANGLE_SUM.01",
    "isosceles_base_angle": "SPI.MIDDLE.GEO.ISOSCELES_BASE_ANGLES.01",
    "vertically_opposite_angle": "SPI.MIDDLE.GEO.VERTICALLY_OPPOSITE_ANGLES.01",
    "angles_at_point_missing": "SPI.MIDDLE.GEO.ANGLES_AT_POINT.01",
}
FAMILY_BY_TASK = {
    "straight_line_missing_angle": "F1", "triangle_missing_angle": "F2", "isosceles_base_angle": "F2",
    "vertically_opposite_angle": "F3", "angles_at_point_missing": "F3",
}
TASK_BANDS = {
    "straight_line_missing_angle": (1, 3), "triangle_missing_angle": (2, 3),
    "isosceles_base_angle": (2, 3), "vertically_opposite_angle": (1, 2), "angles_at_point_missing": (2, 4),
}
CALCULATOR_POLICY = "calculator-not-required"
MAX_PARAM_ATTEMPTS = 400
MIN_ANGLE = 10  # every visibly represented region (including the unknown) is at least 10 degrees

# Canvas / layout constants (raw construction units; the figure is affine-fit before render).
VIEW_W, VIEW_H = 1000, 700
RAW_LEN = 1000          # raw ray length
RAW_BASE = 1200         # raw triangle base width
CX, CY = 500, 350       # plotting-box centre
SPAN_X, SPAN_Y = 760, 520
ARC_R, LBL_R, TICK = 70, 120, 22   # final-pixel radii for arcs, value labels, tick marks
# Per-angle arc radii (v1.2.0): distinct radii so each angle's arc is identifiable and
# never crowds another. Multi-region figures that share a vertex (angles on a line / at
# a point) get GRADUATED radii; triangle/isosceles vertex arcs are scaled to the SHORTEST
# adjacent side so they sit well inside the angle without meeting another vertex.
ARC_BASE, ARC_STEP = 44, 20
ARC_TRI_MAX = 56
ARC_TRI_NUM, ARC_TRI_DEN = 30, 100   # <= 30% of the shortest incident edge
ARC_DEFAULT = 62                     # single-arc figures (vertically opposite)
LBL_GAP = 30                         # the value label sits this far beyond its own arc
LEADER_R1, LEADER_R2 = 46, 96      # neutral target-leader radial extent (vertically opposite)

STYLE = (".gl{stroke:#111;stroke-width:3;fill:none}.ga{stroke:#111;stroke-width:2;fill:none}"
         ".gt{stroke:#111;stroke-width:3}.gx{stroke:#111;stroke-width:3}.gv{fill:#111}"
         "text{font-family:sans-serif;font-size:30px;fill:#111}"
         ".gn{font-size:22px;fill:#444;letter-spacing:1px}")


# --------------------------------------------------------------------------- #
def grid_round(num: int, den: int) -> int:
    """Round the exact rational num/den half-up toward +infinity. den > 0."""
    q, r = divmod(num, den)            # floor q, 0 <= r < den
    return q + 1 if 2 * r >= den else q


def _ray(o: Tuple[int, int], theta: int, length: int) -> Tuple[int, int]:
    dx, dy = DIR[theta % 360]
    return (o[0] + grid_round(dx * length, R), o[1] - grid_round(dy * length, R))


def _mid(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    return (grid_round(a[0] + b[0], 2), grid_round(a[1] + b[1], 2))


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


# --------------------------------------------------------------------------- #
# A Figure is a dict of raw points + primitive lists. Angles are math-degrees.
def _cum(values: List[int]) -> List[int]:
    out, s = [0], 0
    for v in values:
        s += v
        out.append(s)
    return out


def _build_figure(params: Dict[str, Any]) -> Dict[str, Any]:
    """Return the raw FigureModel: points (name->raw int xy) + primitive lists."""
    task = params["task"]
    pts: Dict[str, Tuple[int, int]] = {}
    segs: List[Tuple[str, str, str]] = []
    arcs: List[Tuple[str, int, int]] = []          # (vertex, startDir, measure) — CCW region
    alabels: List[Tuple[str, int, int, str]] = []  # (vertex, startDir, measure, text)
    leaders: List[Tuple[str, int, int, int]] = []  # (vertex, dir, r1, r2) — neutral target marker
    ticks: List[Tuple[str, str, int]] = []         # (a, b, side-math-angle)
    plabels: List[Tuple[str, int, int, str, str]] = []  # (name, ox, oy, text, anchor)

    if task == "straight_line_missing_angle":
        regions = params["regions"]
        uidx = params["unknownIndex"]
        bounds = _cum(regions)            # 0 .. 180
        O = (0, 0)
        pts["O"] = O
        names = []
        for i, ang in enumerate(bounds):
            n = f"B{i}"
            pts[n] = _ray(O, ang, RAW_LEN)
            names.append(n)
        segs.append((names[0], names[-1], "gl"))                  # baseline (0 to 180)
        for i in range(1, len(bounds) - 1):                       # interior rays
            segs.append(("O", names[i], "gl"))
        for j in range(len(regions)):
            arcs.append(("O", bounds[j], regions[j]))
            alabels.append(("O", bounds[j], regions[j], "x" if j == uidx else f"{regions[j]}°"))

    elif task in ("triangle_missing_angle", "isosceles_base_angle"):
        if task == "triangle_missing_angle":
            A, B = params["A"], params["B"]
        else:
            apex = params["apex"]
            A = B = (180 - apex) // 2
        L, Rr = (0, 0), (RAW_BASE, 0)
        P = _apex(L, Rr, A, B)
        pts.update({"L": L, "R": Rr, "P": P})
        segs += [("L", "R", "gl"), ("L", "P", "gl"), ("R", "P", "gl")]
        # interior angle at each vertex = (startDir, measure) sweeping CCW through the
        # triangle interior, so the arc is concave toward the vertex (not the exterior).
        if task == "triangle_missing_angle":
            arcs += [("L", 0, A), ("R", 180 - B, B), ("P", (A + 180) % 360, 180 - A - B)]
            alabels += [("L", 0, A, f"{A}°"), ("R", 180 - B, B, f"{B}°"),
                        ("P", (A + 180) % 360, 180 - A - B, "x")]
            plabels += [("L", -34, 30, "A", "end"), ("R", 34, 30, "B", "start"), ("P", 0, -18, "C", "middle")]
        else:
            # apex labelled with its value; left base angle is x; equal legs carry single ticks
            arcs += [("P", (A + 180) % 360, 180 - A - B), ("L", 0, A)]
            alabels += [("P", (A + 180) % 360, 180 - A - B, f"{apex}°"), ("L", 0, A, "x")]
            ticks += [("L", "P", A), ("R", "P", 180 - B)]

    elif task == "vertically_opposite_angle":
        theta = params["theta"]
        O = (0, 0)
        pts["O"] = O
        pts["E0"] = _ray(O, 0, RAW_LEN)
        pts["E180"] = _ray(O, 180, RAW_LEN)
        pts["Et"] = _ray(O, theta, RAW_LEN)
        pts["Et2"] = _ray(O, theta + 180, RAW_LEN)
        segs += [("E180", "E0", "gl"), ("Et2", "Et", "gl")]       # two full straight lines
        # ONLY the given angle gets an arc. The target (x) is a label in the directly-
        # opposite region (no matching arc that would announce the equality); the adaptive
        # label placer adds a neutral leader if that sector is too narrow for the label.
        arcs += [("O", 0, theta)]
        alabels += [("O", 0, theta, f"{theta}°"), ("O", 180, theta, "x")]

    elif task == "angles_at_point_missing":
        regions = params["regions"]
        uidx = params["unknownIndex"]
        bounds = _cum(regions)            # 0 .. 360 (last == 360 wraps to 0)
        O = (0, 0)
        pts["O"] = O
        m = len(regions)
        for i in range(m):                # m rays
            pts[f"Rr{i}"] = _ray(O, bounds[i], RAW_LEN)
            segs.append(("O", f"Rr{i}", "gl"))
        for j in range(m):
            arcs.append(("O", bounds[j], regions[j]))
            alabels.append(("O", bounds[j], regions[j], "x" if j == uidx else f"{regions[j]}°"))

    return {"points": pts, "segs": segs, "arcs": arcs, "alabels": alabels,
            "leaders": leaders, "ticks": ticks, "plabels": plabels}


def _apex(L: Tuple[int, int], Rr: Tuple[int, int], A: int, B: int) -> Tuple[int, int]:
    """Intersection of the ray from L at base angle A and the ray from R at (180-B).
    Exact rational, then grid_round. For A==B the apex lands exactly on the axis,
    giving exactly equal squared leg lengths."""
    dLx, dLy = DIR[A % 360][0], -DIR[A % 360][1]
    dRx, dRy = DIR[(180 - B) % 360][0], -DIR[(180 - B) % 360][1]
    W = Rr[0] - L[0]
    det = dLx * dRy - dLy * dRx
    s = Fraction(W * dRy, det)
    ax = Fraction(L[0]) + s * dLx
    ay = Fraction(L[1]) + s * dLy
    return (grid_round(ax.numerator, ax.denominator), grid_round(ay.numerator, ay.denominator))


# --------------------------------------------------------------------------- #
def _layout(points: Dict[str, Tuple[int, int]]) -> Dict[str, Tuple[int, int]]:
    """Uniform integer affine fit of the raw points into the plotting box (centred)."""
    xs = [p[0] for p in points.values()]
    ys = [p[1] for p in points.values()]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    bw, bh = max(maxx - minx, 1), max(maxy - miny, 1)
    sx, sy = Fraction(SPAN_X, bw), Fraction(SPAN_Y, bh)
    s = sx if sx <= sy else sy
    out: Dict[str, Tuple[int, int]] = {}
    for name, (x, y) in points.items():
        nx = Fraction(CX) - Fraction(bw) * s / 2 + Fraction(x - minx) * s
        ny = Fraction(CY) - Fraction(bh) * s / 2 + Fraction(y - miny) * s
        out[name] = (grid_round(nx.numerator, nx.denominator), grid_round(ny.numerator, ny.denominator))
    return out


def _ray_at(v: Tuple[int, int], theta: int, radius: int) -> Tuple[int, int]:
    return (v[0] + grid_round(DIR[theta % 360][0] * radius, R), v[1] - grid_round(DIR[theta % 360][1] * radius, R))


def _isqrt(n: int) -> int:
    """Exact integer floor square root (pure integer; no float / no trig)."""
    if n < 2:
        return n
    x, y = n, (n + 1) // 2
    while y < x:
        x, y = y, (y + n // y) // 2
    return x


def _edge_len(p: Tuple[int, int], q: Tuple[int, int]) -> int:
    return _isqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def _arc_radii(fig: Dict[str, Any], P: Dict[str, Tuple[int, int]]) -> List[int]:
    """One radius per arc so each angle's arc is visually distinct and well-sized.

    - Multi-region figures that share a single vertex (angles on a line / around a
      point): GRADUATED radii by region index, so the arcs read as separate rings
      rather than one continuous circle.
    - Triangle / isosceles vertex arcs: scaled to <= ARC_TRI_NUM/ARC_TRI_DEN of the
      SHORTEST incident edge (capped at ARC_TRI_MAX), so each arc sits inside its angle
      and two arcs sharing a side cannot meet.
    - Single-arc figures (vertically opposite): a fixed default.
    """
    arcs = fig["arcs"]
    same_vertex = len({a[0] for a in arcs}) == 1 and len(arcs) >= 2
    radii: List[int] = []
    for j, (vn, start, measure) in enumerate(arcs):
        if same_vertex:
            radii.append(ARC_BASE + j * ARC_STEP)
        else:
            inc = [_edge_len(P[a], P[b]) for (a, b, _cls) in fig["segs"] if vn in (a, b)]
            radii.append(min(ARC_TRI_MAX, min(inc) * ARC_TRI_NUM // ARC_TRI_DEN) if inc else ARC_DEFAULT)
    return radii


def _label_radii(fig: Dict[str, Any], arc_radii: List[int]) -> List[int]:
    rmap = {(vn, start, measure): r for (vn, start, measure), r in zip(fig["arcs"], arc_radii)}
    return [rmap.get((vn, start, measure), ARC_DEFAULT) + LBL_GAP for (vn, start, measure, _t) in fig["alabels"]]


def _arc_path(v: Tuple[int, int], start: int, measure: int, radius: int) -> str:
    """Arc of the CCW sector [start, start+measure] (measure = the region angle).

    Reflex-correct: large-arc-flag = 1 iff measure > 180 (exactly 180 -> 0, a
    semicircle); sweep-flag is always 0 (CCW in math = the intended interior sector).
    Endpoints lie on the boundary rays at `radius` from the vertex.
    """
    e1 = _ray_at(v, start, radius)
    e2 = _ray_at(v, start + measure, radius)
    large = 1 if measure > 180 else 0
    return f"M {e1[0]} {e1[1]} A {radius} {radius} 0 {large} 0 {e2[0]} {e2[1]}"


# --- Adaptive label placement (v1.2.1) ------------------------------------- #
# Integer label-box model (30px sans-serif): per-char advance, ascent, descent.
LBL_CHARW = {"x": 16, "°": 11}
LBL_ASC, LBL_DESC = 22, 8
LBL_CLEAR = 8        # minimum px clearance: label box to any ray / arc / vertex / label / leader
CANVAS_M = 12        # keep label boxes this far inside the viewBox
CAPTION_TOP = 666    # labels stay above the NOT TO SCALE caption (y=685)
LBL_R0_GAP = 36      # a label starts this far beyond its own arc
LBL_STEP = 16        # radial search step
LEAD_IN = 8          # leader inner endpoint sits this far beyond the arc, inside the sector
LEAD_BACK = 12       # leader stops this far short of the label box
ARC_SAMPLES = 8      # arc is sampled at this many points for label-arc clearance
NARROW_DEG = 30      # sectors below this need an inside-fit OR a leader (unambiguous attribution)
PERP_LIST = (28, -28, 56, -56, 84, -84, 112, -112, 140, -140)


def _text_w(text: str) -> int:
    return sum(LBL_CHARW.get(c, 17) for c in text)


def _box_make(x: int, y: int, w: int) -> Tuple[int, int, int, int]:
    return (x - w // 2, y - LBL_ASC, x + (w - w // 2), y + LBL_DESC)


def _box_in_canvas(b: Tuple[int, int, int, int]) -> bool:
    return b[0] >= CANVAS_M and b[2] <= VIEW_W - CANVAS_M and b[1] >= CANVAS_M and b[3] <= CAPTION_TOP


def _boxes_clear(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int], c: int) -> bool:
    return a[2] + c <= b[0] or b[2] + c <= a[0] or a[3] + c <= b[1] or b[3] + c <= a[1]


def _pt_box_d2(px: int, py: int, b: Tuple[int, int, int, int]) -> int:
    dx = max(b[0] - px, 0, px - b[2])
    dy = max(b[1] - py, 0, py - b[3])
    return dx * dx + dy * dy


def _orient(ax: int, ay: int, bx: int, by: int, cx: int, cy: int) -> int:
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def _on_seg(ax: int, ay: int, bx: int, by: int, cx: int, cy: int) -> bool:
    return min(ax, bx) <= cx <= max(ax, bx) and min(ay, by) <= cy <= max(ay, by)


def _seg_intersect(ax, ay, bx, by, cx, cy, dx, dy) -> bool:
    d1, d2 = _orient(cx, cy, dx, dy, ax, ay), _orient(cx, cy, dx, dy, bx, by)
    d3, d4 = _orient(ax, ay, bx, by, cx, cy), _orient(ax, ay, bx, by, dx, dy)
    if (d1 > 0) != (d2 > 0) and (d3 > 0) != (d4 > 0):
        return True
    if d1 == 0 and _on_seg(cx, cy, dx, dy, ax, ay):
        return True
    if d2 == 0 and _on_seg(cx, cy, dx, dy, bx, by):
        return True
    if d3 == 0 and _on_seg(ax, ay, bx, by, cx, cy):
        return True
    if d4 == 0 and _on_seg(ax, ay, bx, by, dx, dy):
        return True
    return False


def _seg_clear_box(ax, ay, bx, by, box, c) -> bool:
    """Segment AB stays at least c px away from the box (box inflated by c, no contact)."""
    L = (box[0] - c, box[1] - c, box[2] + c, box[3] + c)
    if L[0] <= ax <= L[2] and L[1] <= ay <= L[3]:
        return False
    if L[0] <= bx <= L[2] and L[1] <= by <= L[3]:
        return False
    corners = [(L[0], L[1]), (L[2], L[1]), (L[2], L[3]), (L[0], L[3])]
    for i in range(4):
        cx, cy = corners[i]
        ex, ey = corners[(i + 1) % 4]
        if _seg_intersect(ax, ay, bx, by, cx, cy, ex, ey):
            return False
    return True


def _arc_clear_box(box, v, ar, start, measure, c) -> bool:
    cc = c * c
    for i in range(ARC_SAMPLES + 1):
        ang = start + (measure * i) // ARC_SAMPLES
        pt = _ray_at(v, ang, ar)
        if _pt_box_d2(pt[0], pt[1], box) < cc:
            return False
    return True


def _point_along(ax, ay, bx, by, back) -> Tuple[int, int]:
    """Point on segment A->B that stops `back` px short of B (integer, floor div)."""
    length = _isqrt((bx - ax) ** 2 + (by - ay) ** 2)
    if length <= back:
        return (ax, ay)
    t = length - back
    return (ax + (bx - ax) * t // length, ay + (by - ay) * t // length)


def _box_inside_wedge(box, v, start, measure) -> bool:
    return all(_in_ccw_wedge(start, measure, v, (cx, cy)) for cx in (box[0], box[2]) for cy in (box[1], box[3]))


def _place_labels(P: Dict[str, Tuple[int, int]], fig: Dict[str, Any]):
    """Adaptively place each angle label and return (placements, leaders).

    placements[k] = (x, y, "middle", text) aligned with fig['alabels']; leaders[k] is a
    ((ix,iy),(ox,oy)) neutral leader or None. A label is placed INSIDE its sector when its
    full bounding box fits with clearance; otherwise it is a callout in clear space joined
    to the sector by a short neutral leader. Returns None if any label cannot be placed
    (the figure is then rejected and re-drawn). Deterministic integer geometry.
    """
    arc_radii = _arc_radii(fig, P)
    rmap = {(vn, s, m): r for (vn, s, m), r in zip(fig["arcs"], arc_radii)}
    seg_lines = [(P[a], P[b]) for (a, b, _c) in fig["segs"]]
    arcs = [(P[vn], r, s, m) for (vn, s, m), r in zip(fig["arcs"], arc_radii)]
    vertices = list(fig["points"].values())
    placed = []  # obstacle boxes (vertex letters, then placed angle labels)
    for (name, ox, oy, text, anchor) in fig["plabels"]:
        p = P[name]
        w = _text_w(text)
        left = p[0] + ox - (w // 2 if anchor == "middle" else (w if anchor == "end" else 0))
        placed.append((left, p[1] + oy - LBL_ASC, left + w, p[1] + oy + LBL_DESC))

    def ok(box, leader=None) -> bool:
        if not _box_in_canvas(box):
            return False
        if any(not _seg_clear_box(A[0], A[1], B[0], B[1], box, LBL_CLEAR) for (A, B) in seg_lines):
            return False
        if any(not _arc_clear_box(box, av, r, s, m, LBL_CLEAR) for (av, r, s, m) in arcs):
            return False
        if any(_pt_box_d2(vx, vy, box) < LBL_CLEAR * LBL_CLEAR for (vx, vy) in vertices):
            return False
        if any(not _boxes_clear(box, pb, LBL_CLEAR) for pb in placed):
            return False
        if leader is not None and any(
                not _seg_clear_box(leader[0][0], leader[0][1], leader[1][0], leader[1][1], pb, LBL_CLEAR) for pb in placed):
            return False
        return True

    placements, leaders = [], []
    for (vn, start, measure, text) in fig["alabels"]:
        v = P[vn]
        w = _text_w(text)
        bis = (start + measure // 2) % 360
        ar = rmap.get((vn, start, measure), ARC_DEFAULT)
        s = DIR[(measure // 2) % 360][1]                       # R*sin(measure/2)
        r_fit = ((w // 2 + LBL_CLEAR) * R + s - 1) // s if s > 0 else 10 ** 9
        chosen = None
        leader_seg = None
        # 1) INSIDE the sector (no leader) when the whole box fits with clearance.
        r_in = max(ar + LBL_R0_GAP, r_fit)
        for i in range(4):
            pos = _ray_at(v, bis, r_in + i * LBL_STEP)
            box = _box_make(pos[0], pos[1], w)
            if _box_inside_wedge(box, v, start, measure) and ok(box):
                chosen = pos
                break
        # 2) CALLOUT in clear space, joined to the sector by a neutral leader.
        if chosen is None:
            inner = _ray_at(v, bis, ar + LEAD_IN)
            if _in_ccw_wedge(start, measure, v, inner):
                for ri in range(7):
                    base = _ray_at(v, bis, ar + LBL_R0_GAP + ri * LBL_STEP)
                    for perp in PERP_LIST:
                        sx = base[0] + grid_round(DIR[(bis + 90) % 360][0] * perp, R)
                        sy = base[1] - grid_round(DIR[(bis + 90) % 360][1] * perp, R)
                        box = _box_make(sx, sy, w)
                        end = _point_along(inner[0], inner[1], sx, sy, w // 2 + LEAD_BACK)
                        seg = (inner, end)
                        if ok(box, seg):
                            chosen, leader_seg = (sx, sy), seg
                            break
                    if chosen is not None:
                        break
        if chosen is None:
            return None
        placements.append((chosen[0], chosen[1], "middle", text))
        leaders.append(leader_seg)
        placed.append(_box_make(chosen[0], chosen[1], w))
    # Final pass: no leader may cross ANY other label box (incl. later-placed ones).
    n_pl = len(fig["plabels"])
    for k, seg in enumerate(leaders):
        if seg is None:
            continue
        for idx, b in enumerate(placed):
            if idx == n_pl + k:
                continue
            if not _seg_clear_box(seg[0][0], seg[0][1], seg[1][0], seg[1][1], b, LBL_CLEAR):
                return None
    return placements, leaders


def _text_elements(P: Dict[str, Tuple[int, int]], fig: Dict[str, Any]):
    """All text labels (plabels then placed alabels) and the label leaders, or None."""
    placed = _place_labels(P, fig)
    if placed is None:
        return None
    placements, leaders = placed
    texts: List[Tuple[int, int, str, str]] = []
    for (name, ox, oy, text, anchor) in fig["plabels"]:
        p = P[name]
        texts.append((p[0] + ox, p[1] + oy, anchor, text))
    texts.extend(placements)
    return texts, leaders


def _labels_ok(params: Dict[str, Any]) -> bool:
    """Every angle label can be placed with full clearance (else reject + re-draw)."""
    fig = _build_figure(params)
    return _place_labels(_layout(fig["points"]), fig) is not None


def canonical_svg(fig: Dict[str, Any], alt: str, title: str, desc: str) -> str:
    P = _layout(fig["points"])
    out: List[str] = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" role="img" aria-label="{_esc(alt)}">')
    out.append(f"<title>{_esc(title)}</title>")
    out.append(f"<desc>{_esc(desc)}</desc>")
    out.append(f"<style>{STYLE}</style>")
    for (a, b, cls) in fig["segs"]:
        out.append(f'<line class="{cls}" x1="{P[a][0]}" y1="{P[a][1]}" x2="{P[b][0]}" y2="{P[b][1]}"/>')
    for (vn, start, measure), radius in zip(fig["arcs"], _arc_radii(fig, P)):
        out.append(f'<path class="ga" d="{_arc_path(P[vn], start, measure, radius)}"/>')
    for (a, b, ang) in fig["ticks"]:
        m = _mid(P[a], P[b])
        d = (grid_round(DIR[(ang + 90) % 360][0] * TICK, R), -grid_round(DIR[(ang + 90) % 360][1] * TICK, R))
        out.append(f'<line class="gt" x1="{m[0] - d[0]}" y1="{m[1] - d[1]}" x2="{m[0] + d[0]}" y2="{m[1] + d[1]}"/>')
    texts, leaders = _text_elements(P, fig)
    for seg in leaders:
        if seg is not None:
            out.append(f'<line class="gx" x1="{seg[0][0]}" y1="{seg[0][1]}" x2="{seg[1][0]}" y2="{seg[1][1]}"/>')
    for (x, y, anchor, text) in texts:
        out.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}">{_esc(text)}</text>')
    out.append('<text class="gn" x="500" y="685" text-anchor="middle">NOT TO SCALE</text>')
    out.append("</svg>")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
def _ctx(params: Dict[str, Any]) -> Dict[str, Any]:
    """Misconception/solution context, from the displayed givens only."""
    task = params["task"]
    if task in ("straight_line_missing_angle", "angles_at_point_missing"):
        regions, uidx = params["regions"], params["unknownIndex"]
        givens = [regions[i] for i in range(len(regions)) if i != uidx]
        return {"givens": givens}
    if task == "triangle_missing_angle":
        return {"givens": [params["A"], params["B"]]}
    if task == "isosceles_base_angle":
        return {"apex": params["apex"], "givens": [params["apex"]]}
    return {"theta": params["theta"], "givens": [params["theta"]]}


def solve(params: Dict[str, Any]) -> int:
    task = params["task"]
    g = _ctx(params)
    if task == "straight_line_missing_angle":
        return 180 - sum(g["givens"])
    if task == "triangle_missing_angle":
        return 180 - params["A"] - params["B"]
    if task == "isosceles_base_angle":
        return (180 - params["apex"]) // 2
    if task == "vertically_opposite_angle":
        return params["theta"]
    if task == "angles_at_point_missing":
        return 360 - sum(g["givens"])
    raise ValueError(f"unknown task: {task}")


def generate_distractors(params: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    task = params["task"]
    g = _ctx(params)
    correct = solve(params)
    chosen: List[Dict[str, Any]] = []
    seen = {correct}
    for mid in rules_for(task):
        w = MISCONCEPTIONS[mid]["wrong"](g)
        if w is None or not (1 <= w <= 359) or w in seen:
            continue
        seen.add(w)
        chosen.append({"value": w, "misconceptionId": mid, "rationale": MISCONCEPTIONS[mid]["observableError"]})
        if len(chosen) == 3:
            break
    return chosen if len(chosen) == 3 else None


# --------------------------------------------------------------------------- #
def _accessibility(params: Dict[str, Any]) -> Dict[str, Any]:
    task = params["task"]
    g = _ctx(params)
    gv = ", ".join(f"{v} degrees" for v in g["givens"])
    # Descriptions are INFORMATION-EQUIVALENT to the visible diagram: they convey the
    # same givens and spatial configuration but never the theorem, calculation, or
    # answer the student is being assessed on (see _a11y_equivalent_ok).
    if task == "straight_line_missing_angle":
        title = "Angles on a straight line"
        alt = "Diagram: angles adjacent on one side of a straight line, with an unknown angle x."
        desc = (f"Angles of {gv} and an unknown angle x are adjacent, in order, along one side of a straight line.")
    elif task == "triangle_missing_angle":
        title = "Triangle ABC"
        alt = "Diagram: a triangle with two known angles and an unknown angle x."
        desc = (f"Triangle ABC has an interior angle of {params['A']} degrees at A, an interior angle of {params['B']} "
                f"degrees at B, and an unknown interior angle x at C.")
    elif task == "isosceles_base_angle":
        title = "Isosceles triangle"
        alt = "Diagram: a triangle with two sides marked equal, an apex angle, and an unknown base angle x."
        desc = (f"Triangle ABC has its two slanted sides marked equal with single tick marks. The angle at the apex is "
                f"{params['apex']} degrees, and the unknown base angle is marked x.")
    elif task == "vertically_opposite_angle":
        title = "Two intersecting straight lines"
        alt = "Diagram: two straight lines crossing at a point, with a given angle and the angle x in the opposite region."
        desc = (f"Two straight lines cross at a point, forming four angles. One angle measures {params['theta']} degrees, "
                f"and the unknown angle x is in the region directly opposite it.")
    else:
        title = "Angles around a point"
        alt = "Diagram: angles meeting consecutively around a point, with an unknown angle x."
        desc = (f"Angles of {gv} and an unknown angle x are arranged consecutively, with no gaps, around a single point.")
    data_rows = [[f"angle {i + 1}", f"{v} degrees"] for i, v in enumerate(g["givens"])]
    data_rows.append(["x", "unknown"])
    return {"title": title, "alt": alt, "desc": desc,
            "dataTable": {"columns": ["angle", "value"], "rows": data_rows}}


# Theorem/answer phrasings that accessibility text must NEVER contain (it must be
# information-EQUIVALENT to the diagram, not easier). Bare value strings like
# "180 degrees" are NOT banned, since a given angle may legitimately be 180.
_A11Y_BANNED = ("sum", "add up", "full turn", "straight angle", "are equal", "is equal",
                "equal to", "base angles", "make a straight", "make a full", "add to")
_A11Y_REQUIRED = {
    "straight_line_missing_angle": ("straight line", "adjacent"),
    "triangle_missing_angle": ("triangle abc",),
    "isosceles_base_angle": ("marked equal", "apex"),
    "vertically_opposite_angle": ("opposite", "cross"),
    "angles_at_point_missing": ("around", "consecutively"),
}


def _a11y_equivalent_ok(params: Dict[str, Any], acc: Dict[str, Any]) -> bool:
    """The diagram's accessible text conveys the same givens/configuration as the
    visible figure but states no theorem, calculation, or answer."""
    task = params["task"]
    g = _ctx(params)
    blob = (acc["desc"] + " " + acc["alt"]).lower()
    if any(b in blob for b in _A11Y_BANNED):
        return False
    if not all(r in blob for r in _A11Y_REQUIRED[task]):
        return False
    if "unknown" not in acc["desc"].lower():
        return False
    return all(f"{v} degrees" in acc["desc"] for v in g["givens"])


def _in_ccw_wedge(start: int, measure: int, v: Tuple[int, int], pt: Tuple[int, int]) -> bool:
    """Is point pt inside the CCW sector [start, start+measure] at vertex v?
    Integer test in the math frame (+y up). Used to verify a label/leader is in the
    intended region (and, for reflex, NOT in the minor complement)."""
    us = DIR[start % 360]
    ue = DIR[(start + measure) % 360]
    pm = (pt[0] - v[0], -(pt[1] - v[1]))             # math frame, relative to vertex
    cs = us[0] * pm[1] - us[1] * pm[0]               # > 0 if pm is CCW of the start ray
    ce = pm[0] * ue[1] - pm[1] * ue[0]               # > 0 if pm is CW of the end ray
    if measure < 180:
        return cs > 0 and ce > 0
    if measure > 180:
        return not (cs < 0 and ce < 0)               # not inside the minor complement
    return cs > 0                                    # exactly 180: the CCW half-plane


def generate_solution(params: Dict[str, Any]) -> Dict[str, Any]:
    task = params["task"]
    g = _ctx(params)
    ans = solve(params)
    if task == "straight_line_missing_angle":
        s = " + ".join(str(v) for v in g["givens"])
        return {"steps": [
            {"number": 1, "transformation": "State the angle fact", "ruleOrTheorem": "Angles on a straight line sum to 180 degrees"},
            {"number": 2, "transformation": "Form the equation", "intermediateResult": f"x = 180 - ({s})", "dependsOn": [1]},
            {"number": 3, "transformation": "Evaluate", "intermediateResult": f"x = {ans}°", "dependsOn": [2], "marks": 1}]}
    if task == "triangle_missing_angle":
        return {"steps": [
            {"number": 1, "transformation": "State the angle fact", "ruleOrTheorem": "The interior angles of a triangle sum to 180 degrees"},
            {"number": 2, "transformation": "Form the equation", "intermediateResult": f"x = 180 - ({params['A']} + {params['B']})", "dependsOn": [1]},
            {"number": 3, "transformation": "Evaluate", "intermediateResult": f"x = {ans}°", "dependsOn": [2], "marks": 1}]}
    if task == "isosceles_base_angle":
        return {"steps": [
            {"number": 1, "transformation": "State the angle fact", "ruleOrTheorem": "Base angles of an isosceles triangle are equal; the three angles sum to 180 degrees"},
            {"number": 2, "transformation": "Form the equation", "intermediateResult": f"x = (180 - {params['apex']}) / 2", "dependsOn": [1]},
            {"number": 3, "transformation": "Evaluate", "intermediateResult": f"x = {ans}°", "dependsOn": [2], "marks": 1}]}
    if task == "vertically_opposite_angle":
        return {"steps": [
            {"number": 1, "transformation": "State the angle fact", "ruleOrTheorem": "Vertically opposite angles are equal"},
            {"number": 2, "transformation": "Apply", "intermediateResult": f"x = {params['theta']}°", "dependsOn": [1], "marks": 1}]}
    s = " + ".join(str(v) for v in g["givens"])
    return {"steps": [
        {"number": 1, "transformation": "State the angle fact", "ruleOrTheorem": "Angles around a point sum to 360 degrees"},
        {"number": 2, "transformation": "Form the equation", "intermediateResult": f"x = 360 - ({s})", "dependsOn": [1]},
        {"number": 3, "transformation": "Evaluate", "intermediateResult": f"x = {ans}°", "dependsOn": [2], "marks": 1}]}


def _difficulty(params: Dict[str, Any]) -> Dict[str, Any]:
    task = params["task"]
    g = _ctx(params)
    given_count = len(g["givens"])
    non_mult5 = any(v % 5 != 0 for v in g["givens"]) or (solve(params) % 5 != 0)
    obtuse = any(v > 90 for v in g["givens"])
    factors = (1 if given_count >= 3 else 0) + (1 if non_mult5 else 0) + (1 if obtuse else 0)
    lo, hi = TASK_BANDS[task]
    band = lo + min(factors, hi - lo)
    axes = {
        "numericalComplexity": round3(min(1.0, given_count / 4.0)),
        "reasoningSteps": 0.5 if task != "vertically_opposite_angle" else 0.25,
        "representation": 0.6,  # diagram interpretation is intrinsic
        "abstraction": round3(0.3 + (0.2 if non_mult5 else 0.0)),
    }
    return {"overallBand": band, "axes": axes}


# --------------------------------------------------------------------------- #
def _draw_params(rng: Mulberry32, explicit_task) -> Dict[str, Any]:
    task = explicit_task if explicit_task is not None else rng.choice(list(TASKS))
    if task == "straight_line_missing_angle":
        return {"task": task, **_partition(rng, 180, rng.choice([2, 3, 4]))}
    if task == "triangle_missing_angle":
        a = rng.next_int(MIN_ANGLE, 180 - 2 * MIN_ANGLE)
        b = rng.next_int(MIN_ANGLE, 180 - MIN_ANGLE - a)
        return {"task": task, "A": a, "B": b}
    if task == "isosceles_base_angle":
        apex = 2 * rng.next_int(MIN_ANGLE, 80)        # even, 20..160
        return {"task": task, "apex": apex}
    if task == "vertically_opposite_angle":
        return {"task": task, "theta": rng.next_int(MIN_ANGLE, 170)}
    # angles_at_point_missing
    return {"task": task, **_partition(rng, 360, rng.choice([3, 4]))}


def _partition(rng: Mulberry32, total: int, m: int) -> Dict[str, Any]:
    parts: List[int] = []
    remaining = total
    for i in range(m - 1):
        hi = remaining - MIN_ANGLE * (m - 1 - i)
        part = rng.next_int(MIN_ANGLE, hi)
        parts.append(part)
        remaining -= part
    parts.append(remaining)
    uidx = rng.next_int(0, m - 1)
    return {"regions": parts, "unknownIndex": uidx}


def _acceptable(params: Dict[str, Any], answer_type: str) -> Optional[List[Dict[str, Any]]]:
    if not _guards_ok(params):
        return None
    if answer_type == "multiple-choice":
        if params["task"] not in MC_TASKS:
            return None
        return generate_distractors(params)
    return []


def _guards_ok(params: Dict[str, Any]) -> bool:
    task = params["task"]
    ans = solve(params)
    g = _ctx(params)
    if not all(v >= MIN_ANGLE for v in g["givens"]):
        return False
    if task in ("straight_line_missing_angle", "triangle_missing_angle", "isosceles_base_angle"):
        if not (MIN_ANGLE <= ans <= 180 - MIN_ANGLE):
            return False
    if task == "vertically_opposite_angle":
        if not (MIN_ANGLE <= ans <= 170):
            return False
    if task == "angles_at_point_missing":
        if not (MIN_ANGLE <= ans <= 360 - MIN_ANGLE):
            return False
    if task == "isosceles_base_angle":
        if params["apex"] % 2 != 0 or not (20 <= params["apex"] <= 160):
            return False
    if task in ("straight_line_missing_angle", "angles_at_point_missing"):
        if sum(params["regions"]) != (180 if task == "straight_line_missing_angle" else 360):
            return False
    if not _labels_ok(params):  # realisability: angle/vertex labels must not collide
        return False
    return True


def generate(seed: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    config = config or {}
    answer_type = "multiple-choice" if _resolve_interaction(config) == "multiple-choice" else "integer"
    explicit_task = config.get("task")
    if explicit_task is not None and explicit_task not in TASKS:
        raise ValueError(f"unknown task: {explicit_task}")
    if answer_type == "multiple-choice" and explicit_task is not None and explicit_task not in MC_TASKS:
        raise ValueError("vertically_opposite_angle is free-response only in geometry v1.2.x (current approved scope)")

    rng = Mulberry32(seed)
    params: Dict[str, Any] = {}
    distractors: Optional[List[Dict[str, Any]]] = None
    ok = False
    for _ in range(MAX_PARAM_ATTEMPTS):
        params = _draw_params(rng, explicit_task)
        result = _acceptable(params, answer_type)
        if result is None:
            continue
        distractors = result
        ok = True
        break
    if not ok:
        raise RuntimeError("could not find acceptable geometry parameters")

    task = params["task"]
    ans = solve(params)
    fig = _build_figure(params)
    acc = _accessibility(params)
    svg = canonical_svg(fig, acc["alt"], acc["title"], acc["desc"])
    interaction = "multiple-choice" if answer_type == "multiple-choice" else "free-response"

    item: Dict[str, Any] = {
        "itemId": f"ITEM-{GENERATOR_ID.replace('.', '-')}-{seed}-{task}",
        "schemaVersion": "1.0.0",
        "objectiveIds": [OBJECTIVE_BY_TASK[task]],
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "seed": seed,
        "params": dict(params),
        "interactionType": interaction,
        "prompt": {"instruction": "Find", "blocks": [
            {"kind": "text", "text": "Find the size of the unknown angle x, in degrees."},
            {"kind": "media-ref", "ref": "fig-1"}]},
        "answer": {"type": "integer", "canonical": {"num": ans, "den": 1}, "display": f"{ans}°", "units": "degrees"},
        "solution": generate_solution(params),
        "difficulty": _difficulty(params),
        "calculatorPolicy": CALCULATOR_POLICY,
        "media": [{"id": "fig-1", "kind": "svg", "svg": svg, "toScale": False,
                   "altText": acc["alt"], "longDescription": acc["desc"], "dataTableFallback": acc["dataTable"]}],
        "accessibility": {"spokenMath": acc["desc"], "altText": acc["alt"], "longDescription": acc["desc"], "nonColorIndicators": True},
        "provenance": {"origin": "generated", "rightsStatus": "academy-owned",
                       "originalityNote": "Original parameterized item; diagram generated from the same parameters."},
        "lifecycle": {"state": "generated"},
    }

    if answer_type == "multiple-choice":
        ds = distractors or []
        item["distractors"] = [
            {"id": f"d{i+1}", "value": d["value"], "display": f"{d['value']}°",
             "misconceptionId": d["misconceptionId"], "rationale": d["rationale"]}
            for i, d in enumerate(ds)]
        pool = [{"value": ans, "correct": True, "misconceptionId": None}]
        pool += [{"value": d["value"], "correct": False, "misconceptionId": d["misconceptionId"]} for d in ds]
        shuffled = rng.shuffle(pool)
        labels = ["A", "B", "C", "D", "E"]
        item["options"] = [
            {"label": labels[i], "value": o["value"], "display": f"{o['value']}°", "correct": o["correct"],
             **({"misconceptionId": o["misconceptionId"]} if o["misconceptionId"] else {})}
            for i, o in enumerate(shuffled)]
    return item


def _resolve_interaction(config: Dict[str, Any]) -> str:
    it = config.get("interactionType")
    at = config.get("answerType")
    from_it = it if it in ("free-response", "multiple-choice") else None
    from_at = "multiple-choice" if at == "multiple-choice" else ("free-response" if at == "integer" else None)
    if from_it and from_at and from_it != from_at:
        raise ValueError(f"conflicting configuration: interactionType={it} vs answerType={at}")
    return from_it or from_at or "free-response"


def serialize(item: Dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def render(item: Dict[str, Any], mode: str = "full") -> str:
    lines = [b.get("text") or f"[figure {b.get('ref')}]" for b in item["prompt"]["blocks"]]
    if "options" in item:
        for o in item["options"]:
            lines.append(f"  {o['label']}. {o['display']}")
    if mode == "answer-only":
        return f"Answer: x = {item['answer']['display']}"
    out = list(lines)
    if mode == "full":
        out += ["", "Solution:"]
        for s in item["solution"]["steps"]:
            bit = s.get("intermediateResult") or s.get("ruleOrTheorem") or ""
            out.append(f"  {s['number']}. {s.get('transformation','')}: {bit}")
    out.append(f"Answer: x = {item['answer']['display']}")
    return "\n".join(out)


def describe() -> Dict[str, Any]:
    return {
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "title": "Geometry — Angles (SVG diagrams)",
        "description": "Angle-reasoning items with mathematically generated SVG diagrams: angles on a straight line, triangle angle sum, isosceles base angles, vertically opposite angles, and angles around a point.",
        "status": "in-development",
        "supportedObjectives": sorted(set(OBJECTIVE_BY_TASK.values())),
        "supportedQuestionTypes": ["integer"],
        "rngAlgorithm": "mulberry32",
        "parameterSpec": {
            "task": {"type": "enum", "enumValues": list(TASKS)},
            "regions": {"type": "array", "description": "F1/F3 angle regions in order (sum 180 or 360)."},
            "unknownIndex": {"type": "integer", "description": "Index of the unknown region."},
            "A": {"type": "integer"}, "B": {"type": "integer"},
            "apex": {"type": "integer", "description": "Isosceles apex (even, 20..160)."},
            "theta": {"type": "integer", "description": "Given angle for vertically opposite."},
        },
        "operations": {"describe": True, "generate": True, "solve": True, "validate": True,
                       "generateDistractors": True, "generateSolution": True, "render": True, "serialize": True},
        "canonicalMethod": "Closure: x = 180 - sum (line/triangle), (180 - apex)/2 (isosceles), equal (vertically opposite), 360 - sum (point). Diagram from a committed integer direction table; canonical SVG.",
        "independentValidationMethod": "Recompute the figure from params and assert byte-identical SVG; re-derive the answer by an independent route; recompute each distractor from its rule.",
        "misconceptionMappings": sorted(MISCONCEPTIONS.keys()),
        "testStrategy": {"seedSweepCount": 10000, "goldenSeeds": [1, 42, 123456789, 2147483647]},
    }


# --------------------------------------------------------------------------- #
def _has_placeholder(text: str) -> bool:
    return re.search(r"(?<![A-Za-z])[pqrtk](?![A-Za-z])", text) is not None


def validate(item: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "result": "pass" if ok else "fail", "detail": detail})

    params = item["params"]
    task = params["task"]
    g = _ctx(params)
    canon = item["answer"]["canonical"]
    ans = canon["num"] if canon["den"] == 1 else None

    add("params-in-domain", _guards_ok(params), f"task={task}")
    typ = item["answer"]["type"]
    add("answer-type-consistency", typ == "integer" and canon["den"] == 1, f"type={typ}, den={canon['den']}")
    add("units-degrees", item["answer"].get("units") == "degrees", str(item["answer"].get("units")))
    add("interaction-type", item.get("interactionType") in ("free-response", "multiple-choice"), str(item.get("interactionType")))

    # Independent re-derivation of the closure (a second route from the givens).
    if task == "straight_line_missing_angle":
        indep = 180 - sum(g["givens"])
        add("closure-agreement", indep == ans and sum(params["regions"]) == 180, f"{indep} vs {ans}")
    elif task == "triangle_missing_angle":
        indep = 180 - params["A"] - params["B"]
        add("closure-agreement", indep == ans, f"{indep} vs {ans}")
    elif task == "isosceles_base_angle":
        indep = (180 - params["apex"]) // 2
        add("closure-agreement", indep == ans and (180 - params["apex"]) % 2 == 0, f"{indep} vs {ans}")
    elif task == "vertically_opposite_angle":
        add("closure-agreement", params["theta"] == ans, f"{params['theta']} vs {ans}")
    else:
        indep = 360 - sum(g["givens"])
        add("closure-agreement", indep == ans and sum(params["regions"]) == 360, f"{indep} vs {ans}")

    # Diagram-to-data consistency: rebuild the figure from params and assert the
    # stored SVG is byte-identical to the recomputed canonical SVG (no atan2 here).
    fig = _build_figure(params)
    acc = _accessibility(params)
    rebuilt = canonical_svg(fig, acc["alt"], acc["title"], acc["desc"])
    stored_svg = item["media"][0]["svg"] if item.get("media") else ""
    add("svg-realises-data", rebuilt == stored_svg, "recomputed SVG matches stored SVG byte-for-byte")
    add("media-present", bool(item.get("media")) and item["media"][0]["kind"] == "svg", "one svg media asset")
    add("not-to-scale", item["media"][0].get("toScale") is False and "NOT TO SCALE" in stored_svg, "toScale false + label")
    add("labels-non-overlapping", _labels_ok(params), "angle/vertex label boxes do not collide")

    # --- Semantic arc checks: PARSE the emitted SVG arc commands and verify they
    # realise each FigureModel region's measure, sector direction, and major/minor
    # nature (this is what catches a reflex region drawn with its minor arc).
    P = _layout(fig["points"])
    arc_radii = _arc_radii(fig, P)
    arc_cmds = re.findall(r'<path class="ga" d="M (-?\d+) (-?\d+) A (\d+) (\d+) 0 (\d) (\d) (-?\d+) (-?\d+)"/>', stored_svg)
    region_ok = (len(arc_cmds) == len(fig["arcs"]))
    large_ok = sweep_ok = region_ok
    for k, (vn, start, measure) in enumerate(fig["arcs"]):
        if k >= len(arc_cmds):
            break
        x1, y1, rx, ry, large, sweep, x2, y2 = (int(t) for t in arc_cmds[k])
        V, rr = P[vn], arc_radii[k]
        region_ok = region_ok and (x1, y1) == _ray_at(V, start, rr) and (x2, y2) == _ray_at(V, start + measure, rr) and rx == rr and ry == rr
        large_ok = large_ok and large == (1 if measure > 180 else 0)
        sweep_ok = sweep_ok and sweep == 0
    add("arc-region-measure-agreement", bool(region_ok), "arc endpoints realise each region's (start, measure, radius)")
    add("arc-large-flag-correct", bool(large_ok), "large-arc-flag = 1 iff region exceeds 180 degrees")
    add("arc-sweep-correct", bool(sweep_ok), "sweep-flag = 0 (CCW interior sector)")

    # Consecutive partition arcs tile the angle: each region starts where the previous
    # ended (region_ok above ties each parsed arc to these start/measure rays).
    if task in ("straight_line_missing_angle", "angles_at_point_missing"):
        chain = len(arc_cmds) == len(fig["arcs"])
        for k in range(len(fig["arcs"]) - 1):
            chain = chain and (fig["arcs"][k][1] + fig["arcs"][k][2]) % 360 == fig["arcs"][k + 1][1] % 360
        add("arc-matches-cyclic-region", bool(chain), "arcs tile the angle consecutively")

    # --- Adaptive label-placement clearances. Recompute the placement (svg-realises-data
    # ties it to the stored SVG) and test the COMPLETE label bounding boxes against every
    # ray, arc, vertex, label, and leader, with a documented minimum clearance (LBL_CLEAR).
    placed = _place_labels(P, fig)
    add("label-placement-feasible", placed is not None, f"all labels placed with >= {LBL_CLEAR}px clearance")
    if placed is not None:
        placements, lleaders = placed
        plabel_boxes = []
        for (name, ox, oy, t, anchor) in fig["plabels"]:
            wl = _text_w(t)
            left = P[name][0] + ox - (wl // 2 if anchor == "middle" else (wl if anchor == "end" else 0))
            plabel_boxes.append((left, P[name][1] + oy - LBL_ASC, left + wl, P[name][1] + oy + LBL_DESC))
        alabel_boxes = [_box_make(x, y, _text_w(t)) for (x, y, _a, t) in placements]
        all_boxes = plabel_boxes + alabel_boxes
        seg_lines = [(P[a], P[b]) for (a, b, _c) in fig["segs"]]
        vertices = list(fig["points"].values())

        add("labels-within-canvas", all(_box_in_canvas(b) for b in alabel_boxes), f"boxes inside [{CANVAS_M}, {VIEW_W - CANVAS_M}] x [{CANVAS_M}, {CAPTION_TOP}]")
        add("label-label-clearance",
            all(_boxes_clear(all_boxes[i], all_boxes[j], LBL_CLEAR) for i in range(len(all_boxes)) for j in range(i + 1, len(all_boxes))),
            f"label boxes clear each other by >= {LBL_CLEAR}px")
        add("label-ray-clearance",
            all(_seg_clear_box(A[0], A[1], B[0], B[1], b, LBL_CLEAR) for b in alabel_boxes for (A, B) in seg_lines),
            f"labels clear every drawn line by >= {LBL_CLEAR}px")
        add("label-arc-clearance",
            all(_arc_clear_box(b, P[vn], rr, s, m, LBL_CLEAR) for b in alabel_boxes for (vn, s, m), rr in zip(fig["arcs"], arc_radii)),
            f"labels clear every arc by >= {LBL_CLEAR}px")
        add("label-vertex-clearance",
            all(_pt_box_d2(vx, vy, b) >= LBL_CLEAR * LBL_CLEAR for b in alabel_boxes for (vx, vy) in vertices),
            f"labels clear every vertex by >= {LBL_CLEAR}px")
        lead_ok = True
        for k, seg in enumerate(lleaders):
            if seg is None:
                continue
            others = plabel_boxes + [b for j, b in enumerate(alabel_boxes) if j != k]
            if any(not _seg_clear_box(seg[0][0], seg[0][1], seg[1][0], seg[1][1], b, LBL_CLEAR) for b in others):
                lead_ok = False
        add("leader-does-not-cross-label", lead_ok, "no leader crosses another label box")

        attrib_ok = small_ok = reflex_ok = True
        for k, (vn, start, measure, text) in enumerate(fig["alabels"]):
            attributable = _box_inside_wedge(alabel_boxes[k], P[vn], start, measure) or (
                lleaders[k] is not None and _in_ccw_wedge(start, measure, P[vn], lleaders[k][0]))
            attrib_ok = attrib_ok and attributable
            if measure < NARROW_DEG:
                small_ok = small_ok and attributable
            if measure > 180:
                reflex_ok = reflex_ok and attributable
        add("label-inside-intended-region", attrib_ok, "every label is inside its sector or led into it")
        add("small-sector-label-unambiguous", small_ok, f"narrow (< {NARROW_DEG} deg) labels are inside or led into their sector")
        add("reflex-region-rendered-correctly", bool(reflex_ok and large_ok), "regions > 180 use the reflex arc with an attributable label")

    # Vertically opposite must not reveal the equality: the target (x) is a label in the
    # opposite region (with a leader if narrow); only the given angle carries an arc.
    if task == "vertically_opposite_angle":
        ga = stored_svg.count('<path class="ga"')
        gt = stored_svg.count('class="gt"')
        add("no-theorem-revealing-markers", ga == 1 and gt == 0, f"ga={ga} gt={gt}")
        ok_target = placed is not None
        if placed is not None:
            theta = params["theta"]
            placements, lleaders = placed
            for k, (vn, start, measure, text) in enumerate(fig["alabels"]):
                if text == "x":
                    box = _box_make(placements[k][0], placements[k][1], _text_w("x"))
                    led = lleaders[k] is not None and _in_ccw_wedge(180, theta, P["O"], lleaders[k][0])
                    ok_target = _box_inside_wedge(box, P["O"], 180, theta) or led
        add("target-region-unambiguous", bool(ok_target), "the x label (or its leader) lies in the opposite region")

    add("a11y-equivalent-information", _a11y_equivalent_ok(params, acc), "accessible text is equivalent, not easier (no theorem/answer)")
    # Harden against a TAMPERED stored description: the stored accessibility text and the
    # media long description must equal the canonical (recomputed) text byte-for-byte.
    a_store = item.get("accessibility", {})
    media0 = item["media"][0] if item.get("media") else {}
    add("a11y-text-canonical",
        a_store.get("longDescription") == acc["desc"] and a_store.get("altText") == acc["alt"]
        and a_store.get("spokenMath") == acc["desc"] and media0.get("longDescription") == acc["desc"]
        and media0.get("altText") == acc["alt"],
        "stored accessibility/media text matches the canonical description")

    # The unknown region is labelled 'x' (not its value); only the givens are drawn.
    numeric = sorted(int(t[:-1]) for (_, _, _, t) in fig["alabels"] if t.endswith("°"))
    x_count = sum(1 for (_, _, _, t) in fig["alabels"] if t == "x")
    add("no-answer-leakage", x_count == 1 and numeric == sorted(g["givens"]),
        f"x-labels={x_count}, drawn givens={numeric}")

    last_step = item["solution"]["steps"][-1].get("intermediateResult", "")
    add("answer-solution-agree", item["answer"]["display"] in last_step, f"final step '{last_step}'")

    if "distractors" in item:
        ds = item["distractors"]
        mids = [d.get("misconceptionId") for d in ds]
        add("distractors-distinct-misconceptions", len(set(mids)) == len(mids), str(mids))
        add("min-three-distractors", len(ds) >= 3, f"{len(ds)}")
        for d in ds:
            mid = d.get("misconceptionId")
            m = MISCONCEPTIONS.get(mid)
            add("distractor-misconception-known", m is not None, str(mid))
            if m:
                expected = m["wrong"](g)
                add("distractor-value-matches-rule", expected is not None and expected == d["value"], f"{mid}: {expected} vs {d['value']}")
                add("distractor-rationale-matches", d.get("rationale") == m["observableError"], str(mid))
                fb = m["feedback"]
                add("distractor-feedback-present", bool(fb), str(mid))
                add("distractor-feedback-clean", not _has_placeholder(fb), fb)
                add("distractor-not-answer", d["value"] != ans, f"{d['value']} vs {ans}")

    if "options" in item:
        correct = [o for o in item["options"] if o["correct"]]
        add("exactly-one-correct", len(correct) == 1 and correct[0]["display"] == item["answer"]["display"], "")
        wrong = [o["display"] for o in item["options"] if not o["correct"]]
        add("distractors-unique", len(wrong) == len(set(wrong)), str(wrong))

    a = item.get("accessibility", {})
    add("a11y-fields-present", bool(a.get("spokenMath") and a.get("altText") and a.get("longDescription")), "")
    add("a11y-no-answer-in-text", "unknown" in a.get("longDescription", "") and item["answer"]["display"] not in a.get("longDescription", ""), "description marks x as unknown, not its value")
    prov = item.get("provenance", {})
    add("provenance-complete", bool(prov.get("origin") and prov.get("rightsStatus")), "")
    add("version-fields-present", bool(item.get("generatorId") and item.get("generatorVersion")), "")

    status = "pass" if all(c["result"] == "pass" for c in checks) else "fail"
    return {"status": status, "validatorVersion": "1.2.2", "checks": checks}
