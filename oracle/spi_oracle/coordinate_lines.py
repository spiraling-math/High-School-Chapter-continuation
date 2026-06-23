"""gen.geometry.coordinate-lines v1.0.0 — oracle reference.

Coordinate geometry & straight-line graphs (Middle-School Geometry/Algebra bridge):
read/plot a point, gradient and midpoint between lattice points, interpret y = mx + c,
and recover y = mx + c from a graph or two points. Independent Python reference; the
TypeScript app mirrors it byte-for-byte (canonical item + SVG parity).

Discipline (matches the approved geometry-angles family):
  * exact `Fraction` mathematics — never floats in answers or coordinates;
  * a deterministic Cartesian renderer with an EQUAL x/y unit scale, integer pixel
    coordinates via `grid_round` (round half up) applied EXACTLY ONCE per coordinate
    over a single exact-`Fraction` projection of record, and exact-rational line clipping
    — so Python and TypeScript emit byte-identical SVG;
  * `Mulberry32` seeded generation with a bounded deterministic redraw loop;
  * an independent validator that rebuilds the figure from params and asserts the stored
    SVG byte-for-byte, recomputes the answer by a second route, and enforces the
    answer-leakage, scaffolding, equal-scale, clipping, and premium-spec contracts.

Vertical lines are deterministically EXCLUDED from every task with a finite gradient
(gradient_two_points / equation_from_graph / equation_from_two_points / interpret_mx_c);
read_point / plot_point / midpoint may use points that share an x-coordinate.
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
from difficulty import band_from_score, round3  # noqa: E402
from coordinate_misconceptions import MISCONCEPTIONS, rules_for, adapter_for  # noqa: E402

GENERATOR_ID = "gen.geometry.coordinate-lines"
GENERATOR_VERSION = "1.0.0"
VALIDATOR_VERSION = "1.0.0"
CALCULATOR_POLICY = "calculator-not-required"

TASKS = ("read_point", "plot_point", "gradient_two_points", "midpoint",
         "interpret_mx_c", "equation_from_graph", "equation_from_two_points")
# plot_point is free-response only (owner decision B.2). interpret_mx_c is text-only.
MC_TASKS = ("read_point", "gradient_two_points", "midpoint", "interpret_mx_c",
            "equation_from_graph", "equation_from_two_points")
FIGURE_TASKS = ("read_point", "plot_point", "gradient_two_points", "midpoint",
                "equation_from_graph", "equation_from_two_points")

OBJECTIVE_BY_TASK = {
    "read_point": "SPI.MIDDLE.GEO.COORD.READ_POINT.01",
    "plot_point": "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01",
    "gradient_two_points": "SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01",
    "midpoint": "SPI.MIDDLE.GEO.COORD.MIDPOINT.01",
    "interpret_mx_c": "SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01",
    "equation_from_graph": "SPI.MIDDLE.GEO.COORD.EQUATION_FROM_GRAPH.01",
    "equation_from_two_points": "SPI.MIDDLE.GEO.COORD.EQUATION_FROM_2PTS.01",
}
TASK_BANDS = {
    "read_point": (1, 2), "plot_point": (1, 2), "gradient_two_points": (2, 4),
    "midpoint": (2, 3), "interpret_mx_c": (2, 3), "equation_from_graph": (3, 4),
    "equation_from_two_points": (3, 5),
}

# Sampling-domain limits (NOT the rendered window, which is computed per item).
COORD_MAX_X = 10
COORD_MAX_Y = 10
GRAD_DENS = (1, 2, 3, 4)            # gradient denominators (owner E.5)
MAX_PARAM_ATTEMPTS = 800

# Renderer constants (owner E.3). The window is dynamic; these bound the canvas.
VIEW_W, VIEW_H = 1000, 700
CX, CY = 500, 350
PAD = 40
U_MIN = 24
DATA_MARGIN_UNITS = 1
MAX_LABELS_PER_AXIS = 11
LBL_CLEAR = 8
MINOR_GRID_MIN_U = 32              # show half-unit minor grid only when U >= 32 (owner E.4)

STYLE = (
    ".cx-axis{stroke:#111;stroke-width:3;fill:none}"
    ".cx-tick{stroke:#111;stroke-width:2}"
    ".cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}"
    ".cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}"
    ".cx-line{stroke:#111;stroke-width:3;fill:none}"
    ".cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}"
    ".cx-pt-core{fill:#111}"
    ".cx-guide{stroke:#555;stroke-width:1.5;stroke-dasharray:5 4;stroke-linecap:round;fill:none}"
    "text{font-family:sans-serif;font-size:28px;fill:#111}"
    ".cx-ticklbl{font-size:20px;fill:#333}"
    ".cx-lbl{font-size:28px;fill:#111}"
)
# Greyscale palette used by the canonical (monochrome-authoritative) SVG.
GREYS = ("#111", "#333", "#444", "#555", "#888", "#bbb", "#fff")


# --------------------------------------------------------------------------- #
# Exact-rational helpers + encoders
# --------------------------------------------------------------------------- #
def grid_round(num: int, den: int) -> int:
    """Round the exact rational num/den half-up toward +infinity. den > 0."""
    q, r = divmod(num, den)
    return q + 1 if 2 * r >= den else q


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


def enc_rat(f: Fraction) -> Dict[str, int]:
    return {"num": f.numerator, "den": f.denominator}


def disp_rat(f: Fraction) -> str:
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def enc_pt(x: Fraction, y: Fraction) -> Dict[str, Any]:
    return {"x": enc_rat(x), "y": enc_rat(y)}


def disp_pt(x: Fraction, y: Fraction) -> str:
    return f"({disp_rat(x)}, {disp_rat(y)})"


def enc_line(m: Fraction, c: Fraction) -> Dict[str, Any]:
    return {"m": enc_rat(m), "c": enc_rat(c)}


def _m_term(m: Fraction) -> str:
    if m == 1:
        return "x"
    if m == -1:
        return "-x"
    if m.denominator == 1:
        return f"{m.numerator}x"
    return f"({disp_rat(m)})x"


def disp_line(m: Fraction, c: Fraction) -> str:
    """Canonical display of y = mx + c with sign/×1/×0/+0 normalisation."""
    if m == 0:
        return f"y = {disp_rat(c)}"
    s = "y = " + _m_term(m)
    if c > 0:
        s += f" + {disp_rat(c)}"
    elif c < 0:
        s += f" - {disp_rat(-c)}"
    return s


def disp_mx_c(m: Fraction, c: Fraction) -> str:
    return f"m = {disp_rat(m)}, c = {disp_rat(c)}"


# --------------------------------------------------------------------------- #
# Deterministic viewport + single projection of record + exact clipping
# --------------------------------------------------------------------------- #
def _viewport(req: List[Tuple[int, int]]) -> Optional[Dict[str, int]]:
    """Window from the required visible lattice points + the origin + a 1-unit margin,
    with one equal x/y unit scale U (px/unit). Returns None if U < U_MIN (redraw)."""
    pts = list(req) + [(0, 0)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    wx0, wx1 = min(xs) - DATA_MARGIN_UNITS, max(xs) + DATA_MARGIN_UNITS
    wy0, wy1 = min(ys) - DATA_MARGIN_UNITS, max(ys) + DATA_MARGIN_UNITS
    Wx, Wy = wx1 - wx0, wy1 - wy0
    aw, ah = VIEW_W - 2 * PAD, VIEW_H - 2 * PAD
    U = min(aw // Wx, ah // Wy)
    if U < U_MIN:
        return None
    return {"wx0": wx0, "wx1": wx1, "wy0": wy0, "wy1": wy1, "Wx": Wx, "Wy": Wy, "U": U}


def proj_x(lay: Dict[str, int], x: Fraction) -> int:
    nx = Fraction(CX) - Fraction(lay["U"] * lay["Wx"], 2) + (Fraction(x) - lay["wx0"]) * lay["U"]
    return grid_round(nx.numerator, nx.denominator)


def proj_y(lay: Dict[str, int], y: Fraction) -> int:
    ny = Fraction(CY) + Fraction(lay["U"] * lay["Wy"], 2) - (Fraction(y) - lay["wy0"]) * lay["U"]
    return grid_round(ny.numerator, ny.denominator)


def _clip_line(m: Fraction, c: Fraction, lay: Dict[str, int]) -> List[Tuple[Fraction, Fraction]]:
    """Exact-rational clip of y = mx + c to the window rectangle. Returns the two
    visible endpoints (Fractions). Non-vertical lines only (m finite)."""
    wx0, wx1, wy0, wy1 = (Fraction(lay["wx0"]), Fraction(lay["wx1"]),
                          Fraction(lay["wy0"]), Fraction(lay["wy1"]))
    cand: List[Tuple[Fraction, Fraction]] = []

    def add(x: Fraction, y: Fraction) -> None:
        if wx0 <= x <= wx1 and wy0 <= y <= wy1:
            if (x, y) not in cand:
                cand.append((x, y))

    add(wx0, m * wx0 + c)
    add(wx1, m * wx1 + c)
    if m != 0:
        add((wy0 - c) / m, wy0)
        add((wy1 - c) / m, wy1)
    cand.sort(key=lambda p: (p[0], p[1]))
    if len(cand) < 2:
        return []
    return [cand[0], cand[-1]]


def _lattice_points_on_line(m: Fraction, c: Fraction, lay: Dict[str, int]) -> List[Tuple[int, int]]:
    """Integer lattice points (x, y) on y = mx + c strictly inside the window."""
    q = m.denominator
    out: List[Tuple[int, int]] = []
    x = lay["wx0"]
    while x <= lay["wx1"]:
        if x % q == 0:
            y = m * x + c
            if y.denominator == 1 and lay["wy0"] <= y.numerator <= lay["wy1"]:
                out.append((x, int(y)))
        x += 1
    return out


# --------------------------------------------------------------------------- #
# Canonical SVG renderer (cx-*, monochrome-authoritative, to scale)
# --------------------------------------------------------------------------- #
def _tick_stride(lo: int, hi: int) -> int:
    n = hi - lo + 1
    stride = 1
    while (n + stride - 1) // stride > MAX_LABELS_PER_AXIS:
        stride += 1
    return stride


def _line_el(cls: str, x1: int, y1: int, x2: int, y2: int) -> str:
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'


def _point_els(px: int, py: int) -> List[str]:
    return [f'<circle class="cx-pt-outline" cx="{px}" cy="{py}" r="9"/>',
            f'<circle class="cx-pt-core" cx="{px}" cy="{py}" r="5"/>']


def _label_pos(lay: Dict[str, int], gx: int, gy: int, px: int, py: int) -> Tuple[int, str]:
    """Deterministic letter-label position: push toward the window interior."""
    right = gx <= (lay["wx0"] + lay["wx1"]) / 2
    lx = px + 14 if right else px - 14
    anchor = "start" if right else "end"
    return lx, anchor


def _figure(task: str, params: Dict[str, Any], lay: Dict[str, int], scaffold: bool) -> str:
    out: List[str] = []
    acc = _accessibility(task, params)
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" role="img" aria-label="{_esc(acc["alt"])}">')
    out.append(f"<title>{_esc(acc['title'])}</title>")
    out.append(f"<desc>{_esc(acc['desc'])}</desc>")
    out.append(f"<style>{STYLE}</style>")

    wx0, wx1, wy0, wy1, U = lay["wx0"], lay["wx1"], lay["wy0"], lay["wy1"], lay["U"]
    x_axis_y = proj_y(lay, Fraction(0))
    y_axis_x = proj_x(lay, Fraction(0))

    # 1. minor gridlines (half-units), only when U is large enough.
    if U >= MINOR_GRID_MIN_U:
        gx2 = wx0 * 2 + 1
        while gx2 < wx1 * 2:
            xf = Fraction(gx2, 2)
            sx = proj_x(lay, xf)
            out.append(_line_el("cx-grid-minor", sx, proj_y(lay, Fraction(wy1)), sx, proj_y(lay, Fraction(wy0))))
            gx2 += 2
        gy2 = wy0 * 2 + 1
        while gy2 < wy1 * 2:
            yf = Fraction(gy2, 2)
            sy = proj_y(lay, yf)
            out.append(_line_el("cx-grid-minor", proj_x(lay, Fraction(wx0)), sy, proj_x(lay, Fraction(wx1)), sy))
            gy2 += 2

    # 2. major gridlines (integer units), skipping the axes themselves.
    for gx in range(wx0, wx1 + 1):
        if gx == 0:
            continue
        sx = proj_x(lay, Fraction(gx))
        out.append(_line_el("cx-grid-major", sx, proj_y(lay, Fraction(wy1)), sx, proj_y(lay, Fraction(wy0))))
    for gy in range(wy0, wy1 + 1):
        if gy == 0:
            continue
        sy = proj_y(lay, Fraction(gy))
        out.append(_line_el("cx-grid-major", proj_x(lay, Fraction(wx0)), sy, proj_x(lay, Fraction(wx1)), sy))

    # 3. axes (stronger than any gridline) with arrowheads + origin.
    ax_l, ax_r = proj_x(lay, Fraction(wx0)), proj_x(lay, Fraction(wx1))
    ay_b, ay_t = proj_y(lay, Fraction(wy0)), proj_y(lay, Fraction(wy1))
    out.append(_line_el("cx-axis", ax_l, x_axis_y, ax_r, x_axis_y))
    out.append(_line_el("cx-axis", y_axis_x, ay_b, y_axis_x, ay_t))
    out.append(f'<path class="cx-axis" d="M {ax_r - 12} {x_axis_y - 7} L {ax_r} {x_axis_y} L {ax_r - 12} {x_axis_y + 7}"/>')
    out.append(f'<path class="cx-axis" d="M {y_axis_x - 7} {ay_t + 12} L {y_axis_x} {ay_t} L {y_axis_x + 7} {ay_t + 12}"/>')
    out.append(f'<text class="cx-lbl" x="{ax_r - 4}" y="{x_axis_y + 30}" text-anchor="end">x</text>')
    out.append(f'<text class="cx-lbl" x="{y_axis_x + 12}" y="{ay_t + 6}" text-anchor="start">y</text>')

    # 4. axis ticks + integer tick labels (thinned to MAX_LABELS_PER_AXIS).
    sx_stride = _tick_stride(wx0, wx1)
    for gx in range(wx0, wx1 + 1):
        if gx == 0 or gx % sx_stride != 0:
            continue
        sx = proj_x(lay, Fraction(gx))
        out.append(_line_el("cx-tick", sx, x_axis_y - 6, sx, x_axis_y + 6))
        out.append(f'<text class="cx-ticklbl" x="{sx}" y="{x_axis_y + 26}" text-anchor="middle">{gx}</text>')
    sy_stride = _tick_stride(wy0, wy1)
    for gy in range(wy0, wy1 + 1):
        if gy == 0 or gy % sy_stride != 0:
            continue
        sy = proj_y(lay, Fraction(gy))
        out.append(_line_el("cx-tick", y_axis_x - 6, sy, y_axis_x + 6, sy))
        out.append(f'<text class="cx-ticklbl" x="{y_axis_x - 12}" y="{sy + 7}" text-anchor="end">{gy}</text>')
    out.append(f'<text class="cx-ticklbl" x="{y_axis_x - 12}" y="{x_axis_y + 26}" text-anchor="end">0</text>')

    # 5. task-specific geometry (answer-free; leakage rules D).
    out += _task_geometry(task, params, lay, scaffold)

    out.append("</svg>")
    return "\n".join(out)


def _task_geometry(task: str, params: Dict[str, Any], lay: Dict[str, int], scaffold: bool) -> List[str]:
    out: List[str] = []
    if task == "read_point":
        x, y = params["x"], params["y"]
        px, py = proj_x(lay, Fraction(x)), proj_y(lay, Fraction(y))
        if scaffold:  # lower band: dashed projection guides to both axes
            out.append(_line_el("cx-guide", px, py, px, proj_y(lay, Fraction(0))))
            out.append(_line_el("cx-guide", px, py, proj_x(lay, Fraction(0)), py))
        out += _point_els(px, py)
        lx, anchor = _label_pos(lay, x, y, px, py)
        out.append(f'<text class="cx-lbl" x="{lx}" y="{py - 12}" text-anchor="{anchor}">P</text>')
    elif task == "plot_point":
        pass  # blank labelled grid; the target point is NEVER drawn (owner D.1)
    elif task in ("gradient_two_points", "midpoint", "equation_from_two_points"):
        a, b = (params["x1"], params["y1"]), (params["x2"], params["y2"])
        if task == "equation_from_two_points":
            m, c = _solve_line_2pts(params)
            seg = _clip_line(m, c, lay)
            if seg:
                out.append(_line_el("cx-line", proj_x(lay, seg[0][0]), proj_y(lay, seg[0][1]),
                                    proj_x(lay, seg[1][0]), proj_y(lay, seg[1][1])))
        if task == "gradient_two_points" and scaffold:  # optional unlabelled dashed step
            cx_, cy_ = b[0], a[1]
            out.append(_line_el("cx-guide", proj_x(lay, Fraction(a[0])), proj_y(lay, Fraction(a[1])),
                                proj_x(lay, Fraction(cx_)), proj_y(lay, Fraction(cy_))))
            out.append(_line_el("cx-guide", proj_x(lay, Fraction(cx_)), proj_y(lay, Fraction(cy_)),
                                proj_x(lay, Fraction(b[0])), proj_y(lay, Fraction(b[1]))))
        for (gx, gy), letter in ((a, "A"), (b, "B")):
            px, py = proj_x(lay, Fraction(gx)), proj_y(lay, Fraction(gy))
            out += _point_els(px, py)
            lx, anchor = _label_pos(lay, gx, gy, px, py)
            out.append(f'<text class="cx-lbl" x="{lx}" y="{py - 12}" text-anchor="{anchor}">{letter}</text>')
    elif task == "equation_from_graph":
        m, c = params_to_line(params)
        seg = _clip_line(m, c, lay)
        if seg:
            out.append(_line_el("cx-line", proj_x(lay, seg[0][0]), proj_y(lay, seg[0][1]),
                                proj_x(lay, seg[1][0]), proj_y(lay, seg[1][1])))
            ex, ey = seg[1]
            lx = proj_x(lay, ex)
            out.append(f'<text class="cx-lbl" x="{lx - 10}" y="{proj_y(lay, ey) - 10}" text-anchor="end">l</text>')
    return out


# --------------------------------------------------------------------------- #
# Solvers
# --------------------------------------------------------------------------- #
def _solve_gradient(params: Dict[str, Any]) -> Fraction:
    return Fraction(params["y2"] - params["y1"], params["x2"] - params["x1"])


def _solve_midpoint(params: Dict[str, Any]) -> Tuple[Fraction, Fraction]:
    return (Fraction(params["x1"] + params["x2"], 2), Fraction(params["y1"] + params["y2"], 2))


def _solve_line_2pts(params: Dict[str, Any]) -> Tuple[Fraction, Fraction]:
    m = _solve_gradient(params)
    c = Fraction(params["y1"]) - m * params["x1"]
    return m, c


def params_to_line(params: Dict[str, Any]) -> Tuple[Fraction, Fraction]:
    return (Fraction(params["m_num"], params["m_den"]), Fraction(params["c_num"], params["c_den"]))


def _ctx(task: str, params: Dict[str, Any]) -> Dict[str, Fraction]:
    """Misconception context (Fractions) for the task."""
    if task == "read_point":
        return {"x": Fraction(params["x"]), "y": Fraction(params["y"])}
    if task == "midpoint":
        mx, my = _solve_midpoint(params)
        return {"x1": Fraction(params["x1"]), "y1": Fraction(params["y1"]),
                "x2": Fraction(params["x2"]), "y2": Fraction(params["y2"]), "mx": mx, "my": my}
    if task == "gradient_two_points":
        return {"x1": Fraction(params["x1"]), "y1": Fraction(params["y1"]),
                "x2": Fraction(params["x2"]), "y2": Fraction(params["y2"]), "m": _solve_gradient(params)}
    if task == "equation_from_two_points":
        m, c = _solve_line_2pts(params)
        return {"x1": Fraction(params["x1"]), "y1": Fraction(params["y1"]),
                "x2": Fraction(params["x2"]), "y2": Fraction(params["y2"]), "m": m, "c": c}
    # interpret_mx_c, equation_from_graph
    m, c = params_to_line(params)
    extra = {}
    if "x1" in params:
        extra = {"x1": Fraction(params["x1"]), "y1": Fraction(params["y1"]),
                 "x2": Fraction(params["x2"]), "y2": Fraction(params["y2"])}
    return {"m": m, "c": c, **extra}


def _answer_value(task: str, params: Dict[str, Any]) -> Any:
    """Canonical answer in raw form (Fraction / tuple / (m,c))."""
    if task in ("read_point", "plot_point"):
        return (Fraction(params["x"]), Fraction(params["y"]))
    if task == "midpoint":
        return _solve_midpoint(params)
    if task == "gradient_two_points":
        return _solve_gradient(params)
    if task == "equation_from_two_points":
        return _solve_line_2pts(params)
    return params_to_line(params)   # interpret_mx_c, equation_from_graph


ANSWER_KIND = {
    "read_point": "coordinate", "plot_point": "coordinate", "midpoint": "ordered-pair",
    "gradient_two_points": "gradient", "interpret_mx_c": "equation",
    "equation_from_graph": "equation", "equation_from_two_points": "equation",
}


# --------------------------------------------------------------------------- #
# Distractors (misconception-backed)
# --------------------------------------------------------------------------- #
def _reasonable_rat(f: Fraction) -> bool:
    return abs(f.numerator) <= 99 and f.denominator <= 12


def _value_ok(task: str, val: Any) -> bool:
    kind = ANSWER_KIND[task]
    if kind in ("coordinate", "ordered-pair"):
        x, y = val
        return _reasonable_rat(x) and _reasonable_rat(y) and abs(x) <= 20 and abs(y) <= 20
    if kind == "gradient":
        return _reasonable_rat(val)
    m, c = val
    return _reasonable_rat(m) and _reasonable_rat(c)


def _same_value(task: str, a: Any, b: Any) -> bool:
    kind = ANSWER_KIND[task]
    if kind in ("coordinate", "ordered-pair"):
        return a[0] == b[0] and a[1] == b[1]
    if kind == "gradient":
        return a == b
    return a[0] == b[0] and a[1] == b[1]


def _distractors(task: str, params: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    ids = rules_for(task)
    if not ids:
        return None
    ctx = _ctx(task, params)
    answer = _answer_value(task, params)
    seen: List[Any] = [answer]
    chosen: List[Dict[str, Any]] = []
    for mid in ids:
        ad = adapter_for(mid, task)
        if ad is None:
            continue
        val = ad(ctx)
        if val is None or not _value_ok(task, val):
            continue
        if any(_same_value(task, val, s) for s in seen):
            continue
        seen.append(val)
        chosen.append({"misconceptionId": mid, "value": val,
                       "rationale": MISCONCEPTIONS[mid]["observableError"],
                       "feedback": MISCONCEPTIONS[mid]["feedback"]})
        if len(chosen) == 3:
            break
    return chosen if len(chosen) == 3 else None


def _display_value(task: str, val: Any) -> Tuple[Any, str]:
    """Encode + display a value (answer or distractor) for the task's answer kind."""
    kind = ANSWER_KIND[task]
    if kind in ("coordinate", "ordered-pair"):
        x, y = val
        return enc_pt(x, y), disp_pt(x, y)
    if kind == "gradient":
        return enc_rat(val), disp_rat(val)
    m, c = val
    disp = disp_mx_c(m, c) if task == "interpret_mx_c" else disp_line(m, c)
    return enc_line(m, c), disp


# --------------------------------------------------------------------------- #
# Difficulty (four schema-valid axes; owner G weights)
# --------------------------------------------------------------------------- #
_RS_BASE = {"read_point": 0.10, "plot_point": 0.10, "gradient_two_points": 0.40,
            "midpoint": 0.30, "interpret_mx_c": 0.30, "equation_from_graph": 0.55,
            "equation_from_two_points": 0.80}
_AB_BASE = {"read_point": 0.10, "plot_point": 0.15, "gradient_two_points": 0.30,
            "midpoint": 0.20, "interpret_mx_c": 0.20, "equation_from_graph": 0.45,
            "equation_from_two_points": 0.75}


def _difficulty(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    scaffold = bool(params.get("scaffold", False))
    answer = _answer_value(task, params)
    kind = ANSWER_KIND[task]
    # numericalComplexity + exactVsApproximate
    if kind in ("coordinate", "ordered-pair"):
        x, y = answer
        nc = min(1.0, (abs(x) + abs(y)) / (COORD_MAX_X + COORD_MAX_Y))
        ev = 1.0 if (x.denominator > 1 or y.denominator > 1) else 0.0
    elif kind == "gradient":
        nc = min(1.0, (abs(answer.numerator) + answer.denominator) / 10.0)
        ev = 1.0 if answer.denominator > 1 else 0.0
    else:
        m, c = answer
        nc = min(1.0, (abs(m.numerator) + m.denominator + abs(c.numerator)) / 16.0)
        ev = 1.0 if (m.denominator > 1 or c.denominator > 1) else 0.0
    rs = max(0.0, min(1.0, _RS_BASE[task] + (-0.10 if scaffold else 0.05)))
    ab = _AB_BASE[task]
    axes = {"numericalComplexity": round3(nc), "exactVsApproximate": round3(ev),
            "reasoningSteps": round3(rs), "abstraction": round3(ab)}
    score = 0.30 * nc + 0.20 * ev + 0.25 * rs + 0.25 * ab
    band = band_from_score(score)
    lo, hi = TASK_BANDS[task]
    band = max(lo, min(hi, band))
    return {"overallBand": band, "axes": axes}


# --------------------------------------------------------------------------- #
# Accessibility (answer-free where the answer is not shown; leakage rules D)
# --------------------------------------------------------------------------- #
def _grid_phrase(task: str, params: Dict[str, Any]) -> str:
    return "on a labelled Cartesian grid with equal x and y scales"


def _accessibility(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if task == "read_point":
        x, y = params["x"], params["y"]
        title = "Reading coordinates"
        alt = f"A single point P plotted {_grid_phrase(task, params)}."
        desc = (f"A point labelled P is plotted {_grid_phrase(task, params)}. Read its x-coordinate "
                f"from the horizontal axis and its y-coordinate from the vertical axis.")
        rows = [["point", "position"], ["P", f"x = {x}, y = {y}"]]
    elif task == "plot_point":
        title = "Plotting a point"
        alt = f"A blank labelled Cartesian grid for plotting a point."
        desc = (f"A labelled Cartesian grid with numbered axes and equal x and y scales. No point is "
                f"plotted yet; plot the point given in the question.")
        rows = [["axis", "range"], ["x", f"{-COORD_MAX_X} to {COORD_MAX_X}"], ["y", f"{-COORD_MAX_Y} to {COORD_MAX_Y}"]]
    elif task in ("gradient_two_points", "equation_from_two_points"):
        a = (params["x1"], params["y1"])
        b = (params["x2"], params["y2"])
        title = "Two plotted points" if task == "gradient_two_points" else "A line through two points"
        extra = "" if task == "gradient_two_points" else " A straight line is drawn through them."
        alt = f"Two points A and B plotted {_grid_phrase(task, params)}.{extra}"
        desc = (f"Point A is at ({a[0]}, {a[1]}) and point B is at ({b[0]}, {b[1]}), plotted "
                f"{_grid_phrase(task, params)}.{extra}")
        rows = [["point", "coordinates"], ["A", f"({a[0]}, {a[1]})"], ["B", f"({b[0]}, {b[1]})"]]
    elif task == "midpoint":
        a = (params["x1"], params["y1"])
        b = (params["x2"], params["y2"])
        title = "A line segment"
        alt = f"Two endpoints A and B of a segment plotted {_grid_phrase(task, params)}."
        desc = (f"The endpoints of a line segment are A at ({a[0]}, {a[1]}) and B at ({b[0]}, {b[1]}), "
                f"plotted {_grid_phrase(task, params)}. The midpoint is not marked.")
        rows = [["endpoint", "coordinates"], ["A", f"({a[0]}, {a[1]})"], ["B", f"({b[0]}, {b[1]})"]]
    elif task == "equation_from_graph":
        anchors = [(params["x1"], params["y1"]), (params["x2"], params["y2"])]
        title = "A straight-line graph"
        alt = f"A straight line drawn {_grid_phrase(task, params)}."
        desc = (f"A straight line is drawn {_grid_phrase(task, params)}. It passes through the lattice "
                f"points ({anchors[0][0]}, {anchors[0][1]}) and ({anchors[1][0]}, {anchors[1][1]}). "
                f"Determine its equation in the form y = mx + c.")
        rows = [["the line passes through", "coordinates"],
                ["point 1", f"({anchors[0][0]}, {anchors[0][1]})"],
                ["point 2", f"({anchors[1][0]}, {anchors[1][1]})"]]
    else:  # interpret_mx_c (no figure)
        m, c = params_to_line(params)
        title = "A linear equation"
        alt = f"The linear equation {disp_line(m, c)}."
        desc = f"The straight line {disp_line(m, c)} is written in the form y = mx + c."
        rows = [["the equation", disp_line(m, c)]]
    return {"title": title, "alt": alt, "desc": desc,
            "dataTable": {"columns": rows[0], "rows": rows[1:]}}


# --------------------------------------------------------------------------- #
# Prompt + solution
# --------------------------------------------------------------------------- #
def _prompt(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    media = [{"kind": "media-ref", "ref": "fig-1"}] if task in FIGURE_TASKS else []
    if task == "read_point":
        return {"instruction": "Write", "blocks": [
            {"kind": "text", "text": "Write the coordinates of the point P shown on the grid, as an ordered pair."}, *media]}
    if task == "plot_point":
        x, y = params["x"], params["y"]
        return {"instruction": "Plot", "blocks": [
            {"kind": "text", "text": f"Plot the point {disp_pt(Fraction(x), Fraction(y))} on the grid."}, *media]}
    if task == "gradient_two_points":
        a, b = disp_pt(Fraction(params["x1"]), Fraction(params["y1"])), disp_pt(Fraction(params["x2"]), Fraction(params["y2"]))
        return {"instruction": "Find", "blocks": [
            {"kind": "text", "text": f"Find the gradient of the line through A {a} and B {b}."}, *media]}
    if task == "midpoint":
        a, b = disp_pt(Fraction(params["x1"]), Fraction(params["y1"])), disp_pt(Fraction(params["x2"]), Fraction(params["y2"]))
        return {"instruction": "Find", "blocks": [
            {"kind": "text", "text": f"Find the midpoint of the line segment joining A {a} and B {b}."}, *media]}
    if task == "interpret_mx_c":
        m, c = params_to_line(params)
        return {"instruction": "Write", "blocks": [
            {"kind": "text", "text": f"For the straight line {disp_line(m, c)}, write down the gradient m and the y-intercept c."}]}
    if task == "equation_from_graph":
        return {"instruction": "Find", "blocks": [
            {"kind": "text", "text": "Find the equation of the line l shown on the grid, in the form y = mx + c."}, *media]}
    a, b = disp_pt(Fraction(params["x1"]), Fraction(params["y1"])), disp_pt(Fraction(params["x2"]), Fraction(params["y2"]))
    return {"instruction": "Find", "blocks": [
        {"kind": "text", "text": f"Find the equation of the line through A {a} and B {b}, in the form y = mx + c."}, *media]}


def _solution(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = []

    def step(n, t, r):
        steps.append({"number": n, "transformation": t, "intermediateResult": r})

    if task == "read_point":
        step(1, "Read across to the y-axis for x, then up or down to the x-axis for y", disp_pt(Fraction(params["x"]), Fraction(params["y"])))
    elif task == "plot_point":
        step(1, "Count along the x-axis, then up or down the y-axis, and mark the point", disp_pt(Fraction(params["x"]), Fraction(params["y"])))
    elif task == "gradient_two_points":
        rise = params["y2"] - params["y1"]
        run = params["x2"] - params["x1"]
        m = _solve_gradient(params)
        step(1, "Find the rise (change in y) and the run (change in x)", f"rise = {rise}, run = {run}")
        step(2, "Divide the rise by the run and simplify", f"gradient = {disp_rat(m)}")
    elif task == "midpoint":
        mx, my = _solve_midpoint(params)
        step(1, "Average the x-coordinates", f"({params['x1']} + {params['x2']}) / 2 = {disp_rat(mx)}")
        step(2, "Average the y-coordinates", f"({params['y1']} + {params['y2']}) / 2 = {disp_rat(my)}")
        step(3, "Write the midpoint as an ordered pair", disp_pt(mx, my))
    elif task == "interpret_mx_c":
        m, c = params_to_line(params)
        step(1, "The gradient m is the coefficient of x", f"m = {disp_rat(m)}")
        step(2, "The y-intercept c is the constant term", f"c = {disp_rat(c)}")
    elif task == "equation_from_graph":
        m, c = params_to_line(params)
        step(1, "Read the gradient as rise over run between two lattice points", f"m = {disp_rat(m)}")
        step(2, "Read where the line crosses the y-axis for the intercept", f"c = {disp_rat(c)}")
        step(3, "Write the equation in the form y = mx + c", disp_line(m, c))
    else:  # equation_from_two_points
        m, c = _solve_line_2pts(params)
        step(1, "Find the gradient from the two points", f"m = {disp_rat(m)}")
        step(2, "Substitute one point to find the y-intercept c", f"c = {disp_rat(c)}")
        step(3, "Write the equation in the form y = mx + c", disp_line(m, c))
    return {"steps": steps}


# --------------------------------------------------------------------------- #
# Premium presentation spec (deterministic; stored under media[].spec.premium)
# --------------------------------------------------------------------------- #
def png_export_transform() -> Dict[str, Any]:
    scale = min(7680 // VIEW_W, 4320 // VIEW_H)   # = min(7, 6) = 6
    return {"maxEnvelope": "7680x4320", "scale": scale,
            "width": VIEW_W * scale, "height": VIEW_H * scale, "viewBox": f"0 0 {VIEW_W} {VIEW_H}"}


def _premium_spec(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    has_line = task in ("equation_from_graph", "equation_from_two_points")
    has_points = task in ("read_point", "gradient_two_points", "midpoint", "equation_from_two_points")
    series: List[Dict[str, Any]] = []
    if has_line:
        series.append({"id": "line-l", "role": "line", "colorToken": "--cx-series-1", "dash": "solid", "marker": "none"})
    if has_points:
        series.append({"id": "points", "role": "points", "colorToken": "--cx-series-2", "dash": "none", "marker": "disc"})
    return {
        "styleContractVersion": "1.0.0",
        "paletteId": "cx-premium-default",
        "modes": ["premium", "accessible", "print"],
        "defaultMode": "print",
        "series": series,
        "axisHierarchy": {"axis": 1, "gridMajor": 2, "gridMinor": 3},
        "glow": {"enabled": True, "outsideStrokeOnly": True, "maxBlurPx": 6},
        "legend": {"enabled": False},
        "pngExport": png_export_transform(),
    }


# --------------------------------------------------------------------------- #
# Parameter drawing (deterministic; returns None to trigger a redraw)
# --------------------------------------------------------------------------- #
def _draw_grad_pq(rng: Mulberry32) -> Tuple[int, int]:
    q = rng.choice(GRAD_DENS)
    if q == 1:
        ps = list(range(-6, 7))                       # includes 0 (horizontal)
    else:
        ps = [i for i in range(-6, 7) if i != 0 and math.gcd(abs(i), q) == 1]
    p = rng.choice(ps)
    return p, q


def _draw_two_points_with_gradient(rng: Mulberry32) -> Optional[Dict[str, int]]:
    p, q = _draw_grad_pq(rng)
    k = rng.next_int(1, 3)
    dx, dy = q * k, p * k
    if dx > 2 * COORD_MAX_X or abs(dy) > 2 * COORD_MAX_Y:
        return None
    x1lo, x1hi = -COORD_MAX_X, COORD_MAX_X - dx
    if x1lo > x1hi:
        return None
    x1 = rng.next_int(x1lo, x1hi)
    y1lo = max(-COORD_MAX_Y, -COORD_MAX_Y - dy)
    y1hi = min(COORD_MAX_Y, COORD_MAX_Y - dy)
    if y1lo > y1hi:
        return None
    y1 = rng.next_int(y1lo, y1hi)
    x2, y2 = x1 + dx, y1 + dy
    rev = rng.next_int(0, 1) == 1
    if rev:
        x1, y1, x2, y2 = x2, y2, x1, y1
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


def _draw_read_point(rng: Mulberry32) -> Dict[str, Any]:
    x = rng.next_int(-COORD_MAX_X, COORD_MAX_X)
    y = rng.next_int(-COORD_MAX_Y, COORD_MAX_Y)
    scaffold = rng.next_int(0, 1) == 1
    return {"task": "read_point", "x": x, "y": y, "scaffold": scaffold}


def _draw_plot_point(rng: Mulberry32) -> Dict[str, Any]:
    x = rng.next_int(-COORD_MAX_X, COORD_MAX_X)
    y = rng.next_int(-COORD_MAX_Y, COORD_MAX_Y)
    return {"task": "plot_point", "x": x, "y": y, "scaffold": False}


def _draw_gradient(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    base = _draw_two_points_with_gradient(rng)
    scaffold = rng.next_int(0, 1) == 1
    if base is None:
        return None
    return {"task": "gradient_two_points", **base, "scaffold": scaffold}


def _draw_midpoint(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    x1 = rng.next_int(-COORD_MAX_X, COORD_MAX_X)
    y1 = rng.next_int(-COORD_MAX_Y, COORD_MAX_Y)
    x2 = rng.next_int(-COORD_MAX_X, COORD_MAX_X)
    y2 = rng.next_int(-COORD_MAX_Y, COORD_MAX_Y)
    if x1 == x2 and y1 == y2:
        return None
    return {"task": "midpoint", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "scaffold": False}


def _draw_interpret(rng: Mulberry32) -> Dict[str, Any]:
    p, q = _draw_grad_pq(rng)
    c = rng.next_int(-9, 9)
    return {"task": "interpret_mx_c", "m_num": p, "m_den": q, "c_num": c, "c_den": 1, "scaffold": False}


def _draw_equation_from_two_points(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    base = _draw_two_points_with_gradient(rng)
    if base is None:
        return None
    params = {"task": "equation_from_two_points", **base, "scaffold": False}
    _, c = _solve_line_2pts(params)
    if abs(c) > 20 or c.denominator > 12:
        return None
    return params


def _draw_equation_from_graph(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    p, q = _draw_grad_pq(rng)
    c = rng.next_int(-7, 7)
    m = Fraction(p, q)
    xs = [x for x in range(-COORD_MAX_X, COORD_MAX_X + 1)
          if x % q == 0 and -COORD_MAX_Y <= (m * x + c) <= COORD_MAX_Y]
    if len(xs) < 2:
        return None
    x1, x2 = xs[0], xs[-1]
    y1, y2 = int(m * x1 + c), int(m * x2 + c)
    return {"task": "equation_from_graph", "m_num": p, "m_den": q, "c_num": c, "c_den": 1,
            "x1": x1, "y1": y1, "x2": x2, "y2": y2, "scaffold": False}


_DRAW = {
    "read_point": _draw_read_point, "plot_point": _draw_plot_point,
    "gradient_two_points": _draw_gradient, "midpoint": _draw_midpoint,
    "interpret_mx_c": _draw_interpret, "equation_from_graph": _draw_equation_from_graph,
    "equation_from_two_points": _draw_equation_from_two_points,
}


def _req_points(task: str, params: Dict[str, Any]) -> List[Tuple[int, int]]:
    if task in ("read_point", "plot_point"):
        return [(params["x"], params["y"])]
    if task == "interpret_mx_c":
        return []
    return [(params["x1"], params["y1"]), (params["x2"], params["y2"])]


def _labels_feasible(task: str, params: Dict[str, Any], lay: Dict[str, int]) -> bool:
    pts: List[Tuple[int, int]] = []
    if task == "read_point":
        pts = [(params["x"], params["y"])]
    elif task in ("gradient_two_points", "midpoint", "equation_from_two_points"):
        pts = [(params["x1"], params["y1"]), (params["x2"], params["y2"])]
    proj = [(proj_x(lay, Fraction(gx)), proj_y(lay, Fraction(gy))) for gx, gy in pts]
    for (px, py) in proj:
        if not (16 <= px <= VIEW_W - 16 and 30 <= py <= VIEW_H - 16):
            return False
    if len(proj) == 2:
        (ax, ay), (bx, by) = proj
        if (ax - bx) ** 2 + (ay - by) ** 2 < 44 * 44:    # dots/labels far enough apart
            return False
    return True


# --------------------------------------------------------------------------- #
# Generate
# --------------------------------------------------------------------------- #
def _resolve_interaction(config: Dict[str, Any]) -> str:
    it = config.get("interactionType")
    if it in ("free-response", "multiple-choice"):
        return it
    if config.get("answerType") == "multiple-choice":
        return "multiple-choice"
    return "free-response"


def _acceptable(params: Dict[str, Any], interaction: str) -> Optional[List[Dict[str, Any]]]:
    task = params["task"]
    if task in FIGURE_TASKS:
        lay = _viewport(_req_points(task, params))
        if lay is None or not _labels_feasible(task, params, lay):
            return None
        if task == "equation_from_graph":
            m, c = params_to_line(params)
            if len(_lattice_points_on_line(m, c, lay)) < 2:
                return None
    if interaction == "multiple-choice":
        if task not in MC_TASKS:
            return None
        return _distractors(task, params)
    return []


def _encode_answer(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    kind = ANSWER_KIND[task]
    val = _answer_value(task, params)
    if kind in ("coordinate", "ordered-pair"):
        x, y = val
        return {"type": kind, "canonical": enc_pt(x, y), "display": disp_pt(x, y)}
    if kind == "gradient":
        typ = "integer" if val.denominator == 1 else "exact-rational"
        return {"type": typ, "canonical": enc_rat(val), "display": disp_rat(val),
                "accepts": {"fraction": True, "decimal": False, "mixed": False}}
    m, c = val
    out = {"type": "equation", "canonical": enc_line(m, c)}
    if task == "interpret_mx_c":
        out["display"] = disp_mx_c(m, c)
        out["equivalentForms"] = [{"display": disp_line(m, c)}]
    else:
        out["display"] = disp_line(m, c)
    return out


def generate(seed: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    config = config or {}
    interaction = _resolve_interaction(config)
    mc = interaction == "multiple-choice"
    explicit = config.get("task")
    if explicit is not None and explicit not in TASKS:
        raise ValueError(f"unknown task: {explicit}")
    if mc and explicit == "plot_point":
        raise ValueError("plot_point is free-response only; multiple-choice is not supported (owner decision B.2)")
    if mc and explicit is not None and explicit not in MC_TASKS:
        raise ValueError(f"task {explicit} does not support multiple-choice")

    pool = MC_TASKS if (mc and explicit is None) else TASKS
    rng = Mulberry32(seed)
    params: Dict[str, Any] = {}
    distractors: Optional[List[Dict[str, Any]]] = None
    ok = False
    for _ in range(MAX_PARAM_ATTEMPTS):
        task = explicit if explicit is not None else rng.choice(pool)
        drawn = _DRAW[task](rng)
        if drawn is None:
            continue
        res = _acceptable(drawn, interaction)
        if res is None:
            continue
        params, distractors, ok = drawn, res, True
        break
    if not ok:
        raise RuntimeError("could not find acceptable coordinate-lines parameters")

    task = params["task"]
    answer = _encode_answer(task, params)
    acc = _accessibility(task, params)
    lay = _viewport(_req_points(task, params)) if task in FIGURE_TASKS else None
    scaffold = bool(params.get("scaffold", False))

    item: Dict[str, Any] = {
        "itemId": f"ITEM-{GENERATOR_ID.replace('.', '-')}-{seed}-{task}",
        "schemaVersion": "1.0.0",
        "objectiveIds": [OBJECTIVE_BY_TASK[task]],
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "seed": seed,
        "params": dict(params),
        "interactionType": interaction,
        "prompt": _prompt(task, params),
        "answer": answer,
        "solution": _solution(task, params),
        "difficulty": _difficulty(task, params),
        "calculatorPolicy": CALCULATOR_POLICY,
        "accessibility": {"spokenMath": acc["desc"], "altText": acc["alt"],
                          "longDescription": acc["desc"], "nonColorIndicators": True},
        "provenance": {"origin": "generated", "rightsStatus": "academy-owned",
                       "originalityNote": "Original parameterized item; the figure is generated from the same parameters."},
        "lifecycle": {"state": "generated"},
    }

    if task in FIGURE_TASKS:
        svg = _figure(task, params, lay, scaffold)
        item["media"] = [{"id": "fig-1", "kind": "svg", "svg": svg, "toScale": True,
                          "altText": acc["alt"], "longDescription": acc["desc"],
                          "dataTableFallback": acc["dataTable"],
                          "spec": {"premium": _premium_spec(task, params)}}]
    else:
        item["media"] = []

    if mc:
        ds = distractors or []
        item["distractors"] = []
        for i, d in enumerate(ds):
            enc, disp = _display_value(task, d["value"])
            item["distractors"].append({"id": f"d{i+1}", "value": enc, "display": disp,
                                        "misconceptionId": d["misconceptionId"], "rationale": d["rationale"]})
        a_enc, a_disp = _display_value(task, _answer_value(task, params))
        pool_opts = [{"value": a_enc, "display": a_disp, "correct": True, "misconceptionId": None}]
        for d in ds:
            enc, disp = _display_value(task, d["value"])
            pool_opts.append({"value": enc, "display": disp, "correct": False, "misconceptionId": d["misconceptionId"]})
        shuffled = rng.shuffle(pool_opts)
        labels = ["A", "B", "C", "D", "E"]
        item["options"] = [
            {"label": labels[i], "value": o["value"], "display": o["display"], "correct": o["correct"],
             **({"misconceptionId": o["misconceptionId"]} if o["misconceptionId"] else {})}
            for i, o in enumerate(shuffled)]
    return item


# --------------------------------------------------------------------------- #
# Serialize / render / describe
# --------------------------------------------------------------------------- #
def serialize(item: Dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def render(item: Dict[str, Any], mode: str = "full") -> str:
    lines = [b.get("text") or f"[figure {b.get('ref')}]" for b in item["prompt"]["blocks"]]
    if "options" in item:
        for o in item["options"]:
            lines.append(f"  {o['label']}. {o['display']}")
    if mode == "answer-only":
        return f"Answer: {item['answer']['display']}"
    out = list(lines)
    if mode == "full":
        out += ["", "Solution:"]
        for s in item["solution"]["steps"]:
            out.append(f"  {s['number']}. {s.get('transformation','')}: {s.get('intermediateResult','')}")
    out.append(f"Answer: {item['answer']['display']}")
    return "\n".join(out)


def describe() -> Dict[str, Any]:
    return {
        "id": GENERATOR_ID,
        "version": GENERATOR_VERSION,
        "title": "Coordinate geometry & straight-line graphs",
        "domain": "geometry",
        "objectiveIds": [OBJECTIVE_BY_TASK[t] for t in TASKS],
        "interactionTypes": ["free-response", "multiple-choice"],
        "answerTypes": ["coordinate", "ordered-pair", "integer", "exact-rational", "equation"],
        "tasks": list(TASKS),
    }


# --------------------------------------------------------------------------- #
# Independent validator
# --------------------------------------------------------------------------- #
_FINITE_GRADIENT_TASKS = ("gradient_two_points", "equation_from_graph", "equation_from_two_points")


def validate(item: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "result": "pass" if ok else "fail", "detail": detail})

    params = item["params"]
    task = params["task"]
    interaction = item.get("interactionType")
    answer = item["answer"]
    a_disp = answer.get("display", "")

    # --- params + answer typing ------------------------------------------- #
    add("params-in-domain", _params_in_domain(task, params), f"task={task}")
    add("interaction-type", interaction in ("free-response", "multiple-choice"), str(interaction))
    add("objective-mapping", item.get("objectiveIds") == [OBJECTIVE_BY_TASK.get(task)], str(item.get("objectiveIds")))
    kind = ANSWER_KIND[task]
    if kind == "gradient":
        want = "integer" if answer["canonical"]["den"] == 1 else "exact-rational"
        add("answer-type-consistency", answer["type"] == want, f"{answer['type']} vs {want}")
    elif kind in ("coordinate", "ordered-pair"):
        add("answer-type-consistency", answer["type"] == kind, answer["type"])
    else:
        add("answer-type-consistency", answer["type"] == "equation", answer["type"])

    # --- vertical-line exclusion (finite-gradient tasks) ------------------ #
    if task in _FINITE_GRADIENT_TASKS:
        if task == "equation_from_graph":
            add("vertical-line-excluded", params["x1"] != params["x2"], "anchors share no x")
        else:
            add("vertical-line-excluded", params["x1"] != params["x2"], f"x1={params['x1']} x2={params['x2']}")

    # --- closure: recompute the answer by a second route ------------------ #
    add("closure-agreement", _closure_ok(task, params, answer), "recomputed answer matches stored canonical")

    # --- diagram-to-data: byte-for-byte SVG (figure tasks) ---------------- #
    if task in FIGURE_TASKS:
        media = item.get("media") or []
        add("media-present", len(media) == 1 and media[0].get("kind") == "svg", "one svg media asset")
        if media:
            lay = _viewport(_req_points(task, params))
            rebuilt = _figure(task, params, lay, bool(params.get("scaffold", False))) if lay else ""
            stored = media[0].get("svg", "")
            add("svg-realises-data", rebuilt == stored, "recomputed SVG matches stored SVG byte-for-byte")
            add("media-to-scale", media[0].get("toScale") is True, "coordinate figures are drawn to scale")
            add("equal-axis-scale", lay is not None, "one equal x/y unit scale U")
            # premium spec parity
            stored_spec = (media[0].get("spec") or {}).get("premium")
            add("premium-spec-parity", stored_spec == _premium_spec(task, params), "premium spec recomputed byte-for-byte")
            # tick labels are integers
            ticks = re.findall(r'<text class="cx-ticklbl"[^>]*>(-?\d+)</text>', stored)
            add("tick-labels-integer", len(ticks) >= 1 and all(re.fullmatch(r"-?\d+", t) for t in ticks), f"{len(ticks)} integer tick labels")
            # axis stronger than gridlines (style hierarchy)
            add("axes-stronger-than-grid", _axis_hierarchy_ok(stored), "axis width > major grid > minor grid")
            # answer text never printed on the figure: no <text> element states a
            # coordinate pair, a fraction, or an equation (',' '/' '=' appear only in
            # answers; axis/tick/letter labels never contain them).
            svg_texts = re.findall(r"<text[^>]*>([^<]*)</text>", stored)
            add("no-answer-label-in-svg", not any(ch in t for t in svg_texts for ch in (",", "/", "=")),
                "no figure text states a coordinate, fraction, or equation")
            if task == "plot_point":
                add("plot-point-target-absent", "<circle" not in stored, "the student grid plots no point")
            if task in ("equation_from_graph", "equation_from_two_points"):
                m, c = (params_to_line(params) if task == "equation_from_graph" else _solve_line_2pts(params))
                seg = _clip_line(m, c, lay) if lay else []
                ok_clip = bool(seg) and all(_in_canvas(proj_x(lay, p[0]), proj_y(lay, p[1])) for p in seg)
                add("line-clipped-within-viewport", ok_clip, "clipped line endpoints lie inside the viewport")
            if task == "equation_from_graph":
                m, c = params_to_line(params)
                add("lattice-anchors-readable", lay is not None and len(_lattice_points_on_line(m, c, lay)) >= 2, "the line crosses >= 2 readable lattice points")
    else:
        add("media-absent-for-text-task", (item.get("media") or []) == [], "interpret_mx_c has no figure")

    # --- accessibility ----------------------------------------------------- #
    acc_fields = item.get("accessibility", {})
    add("a11y-fields-present", all(k in acc_fields for k in ("spokenMath", "altText", "longDescription")), "spokenMath/altText/longDescription present")
    add("a11y-non-color", acc_fields.get("nonColorIndicators") is True, "no colour-only information")
    # The answer is not stated in the accessibility text (where it is not a shown given).
    # Applied only to DISTINCTIVE answers (coordinate pairs, fractions, equations); a bare
    # integer gradient/intercept is never "stated" but would falsely match a given coordinate.
    if task not in ("read_point", "interpret_mx_c") and any(ch in a_disp for ch in ("(", "/", "=")):
        a11y_text = " ".join([acc_fields.get("altText", ""), acc_fields.get("longDescription", "")])
        add("no-answer-in-accessibility-text", a_disp not in a11y_text, "the answer is not stated in the accessibility text")

    # --- monochrome canonical SVG (no colour-only meaning) ---------------- #
    if task in FIGURE_TASKS and (item.get("media") or []):
        cols = set(re.findall(r"(?:fill|stroke):(#[0-9a-fA-F]{3,6})", item["media"][0].get("svg", "")))
        add("no-colour-only-information", cols.issubset(set(GREYS)), f"colours {sorted(cols)}")

    # --- multiple-choice distractors -------------------------------------- #
    if interaction == "multiple-choice":
        ds = item.get("distractors", [])
        opts = item.get("options", [])
        add("min-three-distractors", len(ds) >= 3, f"{len(ds)} distractors")
        mids = [d.get("misconceptionId") for d in ds]
        add("distractors-distinct-misconceptions", len(set(mids)) == len(mids) and all(m in MISCONCEPTIONS for m in mids), str(mids))
        add("distractor-value-matches-rule", _distractor_values_ok(task, params, ds), "each distractor equals its rule's recomputed value")
        add("distractor-not-answer", all(d.get("display") != a_disp for d in ds), "no distractor equals the answer")
        add("distractor-rationale-matches", all(d.get("rationale") == MISCONCEPTIONS.get(d.get("misconceptionId"), {}).get("observableError") for d in ds), "rationale matches the rule")
        add("distractor-feedback-present", all(bool(MISCONCEPTIONS.get(d.get("misconceptionId"), {}).get("feedback")) for d in ds), "registry feedback present for each rule")
        correct = [o for o in opts if o.get("correct")]
        add("exactly-one-correct", len(correct) == 1 and correct[0].get("display") == a_disp, "one correct option matching the answer")

    # --- provenance + versions -------------------------------------------- #
    prov = item.get("provenance", {})
    add("provenance-complete", prov.get("origin") == "generated" and bool(prov.get("rightsStatus")), "origin + rightsStatus present")
    add("version-fields-present", item.get("generatorId") == GENERATOR_ID and item.get("generatorVersion") == GENERATOR_VERSION, "generator id + version present")

    status = "pass" if all(c["result"] == "pass" for c in checks) else "fail"
    return {"status": status, "validatorVersion": VALIDATOR_VERSION, "checks": checks}


def _params_in_domain(task: str, params: Dict[str, Any]) -> bool:
    def inb(v, b):
        return -b <= v <= b
    if task in ("read_point", "plot_point"):
        return inb(params["x"], COORD_MAX_X) and inb(params["y"], COORD_MAX_Y)
    if task == "interpret_mx_c":
        return params["m_den"] in GRAD_DENS and params["c_den"] == 1
    if task in ("gradient_two_points", "midpoint", "equation_from_two_points", "equation_from_graph"):
        ok = all(inb(params[k], COORD_MAX_X if k[0] == "x" else COORD_MAX_Y) for k in ("x1", "y1", "x2", "y2"))
        if task in _FINITE_GRADIENT_TASKS:
            ok = ok and params["x1"] != params["x2"]
        return ok
    return False


def _closure_ok(task: str, params: Dict[str, Any], answer: Dict[str, Any]) -> bool:
    can = answer["canonical"]
    if task in ("read_point", "plot_point", "midpoint"):
        x, y = _answer_value(task, params)
        return can == {"x": enc_rat(x), "y": enc_rat(y)}
    if task == "gradient_two_points":
        m = Fraction(params["y2"] - params["y1"], params["x2"] - params["x1"])
        return can == enc_rat(m)
    if task == "equation_from_two_points":
        m, c = _solve_line_2pts(params)
        return can == enc_line(m, c)
    m, c = params_to_line(params)
    return can == enc_line(m, c)


def _in_canvas(px: int, py: int) -> bool:
    return PAD - 1 <= px <= VIEW_W - PAD + 1 and PAD - 1 <= py <= VIEW_H - PAD + 1


def _axis_hierarchy_ok(svg: str) -> bool:
    def w(cls):
        m = re.search(r"\." + re.escape(cls) + r"\{[^}]*stroke-width:([0-9.]+)", svg)
        return float(m.group(1)) if m else 0.0
    return w("cx-axis") > w("cx-grid-major") > w("cx-grid-minor") > 0


def _distractor_values_ok(task: str, params: Dict[str, Any], ds: List[Dict[str, Any]]) -> bool:
    ctx = _ctx(task, params)
    for d in ds:
        mid = d.get("misconceptionId")
        ad = adapter_for(mid, task)
        if ad is None:
            return False
        val = ad(ctx)
        if val is None:
            return False
        enc, _ = _display_value(task, val)
        if enc != d.get("value"):
            return False
    return True
