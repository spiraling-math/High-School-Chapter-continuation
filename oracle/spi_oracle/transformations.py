"""gen.geometry.transformations v1.0.0 — generator, family-local Cartesian renderer, and validator.

RENDERER REUSE (owner L): this family REUSES the approved Cartesian visual contract + theme
(cartesian-theme, the common CSS variables, presentationSvg/exportSvg modes, the accessibility
contract). It does NOT import the private coordinate-lines projection / gridRound / label-placement
implementation; those primitives are reimplemented family-locally here (tx_grid_round / _viewport /
proj_*) and a parity test pins them. The approved coordinate-lines files are never edited.

CHANNELS (owner N): the base geometry + student annotations are byte-identical between the student and
answer-key SVG; the answer key adds ONLY a solution-overlay group. Perform tasks hide the image from the
student; describe tasks show both figures but never name the transformation in the student channel.

EXACT (owner F): integer coordinates only; no trig/float/tolerance/irrational. Source markers are filled
circles with solid edges; image markers are open squares with dashed edges — distinct WITHOUT colour
(owner M). Image labels use A′..D′ (U+2032).

domains/geometry/transformations.ts mirrors this byte-for-byte.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from .seeded_random import Mulberry32
from .difficulty import band_from_score
from . import transformations_core as TC
from . import transformations_shapes as TS
from . import transformations_misconceptions as TM
from .transformations_checker import check_description

GENERATOR_ID = "gen.geometry.transformations"
GENERATOR_VERSION = "1.0.0"
VALIDATOR_VERSION = "1.0.0"

OBJECTIVE_BY_TASK = {
    "translate_point": "SPI.MIDDLE.GEO.TRANS.TRANSLATE_POINT.01",
    "translate_shape": "SPI.MIDDLE.GEO.TRANS.TRANSLATE_SHAPE.01",
    "reflect_point": "SPI.MIDDLE.GEO.TRANS.REFLECT_POINT.01",
    "reflect_shape": "SPI.MIDDLE.GEO.TRANS.REFLECT_SHAPE.01",
    "rotate_point": "SPI.MIDDLE.GEO.TRANS.ROTATE_POINT.01",
    "rotate_shape": "SPI.MIDDLE.GEO.TRANS.ROTATE_SHAPE.01",
    "describe_translation": "SPI.MIDDLE.GEO.TRANS.DESCRIBE_TRANSLATION.01",
    "describe_reflection": "SPI.MIDDLE.GEO.TRANS.DESCRIBE_REFLECTION.01",
    "describe_rotation": "SPI.MIDDLE.GEO.TRANS.DESCRIBE_ROTATION.01",
}
SUPPORTED_INTERACTIONS = ("free-response",)
FAMILY_KIND = {
    "translate_point": "translation", "translate_shape": "translation", "describe_translation": "translation",
    "reflect_point": "reflection", "reflect_shape": "reflection", "describe_reflection": "reflection",
    "rotate_point": "rotation", "rotate_shape": "rotation", "describe_rotation": "rotation",
}


class InteractionNotSupported(Exception):
    """Raised when an unsupported interaction (e.g. multiple-choice) is requested (owner A)."""


# --------------------------------------------------------------------------- #
# Family-local projection (owner L — mirrored, NOT imported)
# --------------------------------------------------------------------------- #
VIEW_W, VIEW_H, PAD, U_MIN, MARGIN = 1000, 700, 70, 34, 1
CX, CY = VIEW_W // 2, VIEW_H // 2


def tx_grid_round(num: int, den: int) -> int:
    q, r = divmod(num, den)
    return q + 1 if 2 * r >= den else q


def _viewport(pts: List[TC.Point]) -> Optional[Dict[str, int]]:
    xs = [p[0] for p in pts] + [0]
    ys = [p[1] for p in pts] + [0]
    wx0, wx1 = min(xs) - MARGIN, max(xs) + MARGIN
    wy0, wy1 = min(ys) - MARGIN, max(ys) + MARGIN
    Wx, Wy = wx1 - wx0, wy1 - wy0
    U = min((VIEW_W - 2 * PAD) // Wx, (VIEW_H - 2 * PAD) // Wy)
    if U < U_MIN:
        return None
    return {"wx0": wx0, "wx1": wx1, "wy0": wy0, "wy1": wy1, "Wx": Wx, "Wy": Wy, "U": U}


def proj_x(lay: Dict[str, int], x: int) -> int:
    num = CX * 2 - lay["U"] * lay["Wx"] + 2 * (x - lay["wx0"]) * lay["U"]
    return tx_grid_round(num, 2)


def proj_y(lay: Dict[str, int], y: int) -> int:
    num = CY * 2 + lay["U"] * lay["Wy"] - 2 * (y - lay["wy0"]) * lay["U"]
    return tx_grid_round(num, 2)


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


# tx-* classes; theme variables resolve via cartesian-theme (owner L). Monochrome-authoritative.
STYLE = (
    ".tx-grid{stroke:#bbb;stroke-width:0.75;fill:none}"
    ".tx-axis{stroke:#111;stroke-width:2.5;fill:none}"
    ".tx-src-edge{stroke:#111;stroke-width:3;fill:none}"
    ".tx-src-core{fill:#111}"
    ".tx-img-edge{stroke:#111;stroke-width:3;fill:none;stroke-dasharray:8 5}"
    ".tx-img-open{fill:#fff;stroke:#111;stroke-width:3}"
    ".tx-mirror{stroke:#111;stroke-width:2;stroke-dasharray:2 6;fill:none}"
    ".tx-vec{stroke:#111;stroke-width:3;fill:none;marker-end:url(#tx-arrow)}"
    ".tx-centre{fill:#111;stroke:#fff;stroke-width:2}"
    "text{font-family:sans-serif;font-size:26px;fill:#111}"
    ".tx-ticklbl{font-size:18px;fill:#333}"
    ".tx-lbl{font-size:26px;fill:#111}"
)
LABEL_W_PER_CHAR, LABEL_H = 16, 24
CAND_OFFSETS = [(14, -14, "start"), (-14, -14, "end"), (14, 18, "start"),
                (-14, 18, "end"), (0, -18, "middle"), (0, 26, "middle")]


# --------------------------------------------------------------------------- #
# Deterministic label placement with complete bounding-box clearance (owner M)
# --------------------------------------------------------------------------- #
def _bbox(cx: int, cy: int, w: int, h: int) -> Tuple[int, int, int, int]:
    return (cx - w // 2, cy - h, cx + w // 2, cy)


def _overlap(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> bool:
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def _place_labels(items: List[Tuple[str, int, int]]) -> List[Dict[str, Any]]:
    """items: (text, px, py) screen anchors. Returns placements with a clear bounding box, choosing
    the first candidate offset that avoids every other label box, every marker, and the canvas edge."""
    placed: List[Dict[str, Any]] = []
    marker_boxes = [_bbox(px, py + 9, 22, 22) for _, px, py in items]
    for text, px, py in items:
        w = LABEL_W_PER_CHAR * len(text) + 6
        chosen = None
        for dx, dy, anchor in CAND_OFFSETS:
            lx, ly = px + dx, py + dy
            cx = lx + (w // 2 if anchor == "start" else -w // 2 if anchor == "end" else 0)
            box = _bbox(cx, ly + LABEL_H, w, LABEL_H)
            if box[0] < 4 or box[1] < 4 or box[2] > VIEW_W - 4 or box[3] > VIEH_H_GUARD():
                continue
            if any(_overlap(box, pb["box"]) for pb in placed):
                continue
            if any(_overlap(box, mb) for mb in marker_boxes):
                continue
            chosen = {"text": text, "x": lx, "y": ly, "anchor": anchor, "box": box}
            break
        if chosen is None:
            dx, dy, anchor = CAND_OFFSETS[0]
            lx, ly = px + dx, py + dy
            cx = lx + w // 2
            chosen = {"text": text, "x": lx, "y": ly, "anchor": anchor,
                      "box": _bbox(cx, ly + LABEL_H, w, LABEL_H), "clearanceFailed": True}
        placed.append(chosen)
    return placed


def VIEH_H_GUARD() -> int:  # canvas lower bound for a label box
    return VIEW_H - 4


# --------------------------------------------------------------------------- #
# SVG building blocks
# --------------------------------------------------------------------------- #
def _grid_axes(lay: Dict[str, int]) -> List[str]:
    out: List[str] = []
    wx0, wx1, wy0, wy1 = lay["wx0"], lay["wx1"], lay["wy0"], lay["wy1"]
    for gx in range(wx0, wx1 + 1):
        if gx == 0:
            continue
        sx = proj_x(lay, gx)
        out.append(f'<line class="tx-grid" x1="{sx}" y1="{proj_y(lay, wy1)}" x2="{sx}" y2="{proj_y(lay, wy0)}"/>')
    for gy in range(wy0, wy1 + 1):
        if gy == 0:
            continue
        sy = proj_y(lay, gy)
        out.append(f'<line class="tx-grid" x1="{proj_x(lay, wx0)}" y1="{sy}" x2="{proj_x(lay, wx1)}" y2="{sy}"/>')
    ax_y, ay_x = proj_y(lay, 0), proj_x(lay, 0)
    out.append(f'<line class="tx-axis" x1="{proj_x(lay, wx0)}" y1="{ax_y}" x2="{proj_x(lay, wx1)}" y2="{ax_y}"/>')
    out.append(f'<line class="tx-axis" x1="{ay_x}" y1="{proj_y(lay, wy0)}" x2="{ay_x}" y2="{proj_y(lay, wy1)}"/>')
    for gx in range(wx0, wx1 + 1):
        if gx == 0:
            continue
        sx = proj_x(lay, gx)
        out.append(f'<text class="tx-ticklbl" x="{sx}" y="{ax_y + 22}" text-anchor="middle">{gx}</text>')
    for gy in range(wy0, wy1 + 1):
        if gy == 0:
            continue
        sy = proj_y(lay, gy)
        out.append(f'<text class="tx-ticklbl" x="{ay_x - 10}" y="{sy + 6}" text-anchor="end">{gy}</text>')
    out.append(f'<text class="tx-ticklbl" x="{ay_x - 10}" y="{ax_y + 22}" text-anchor="end">0</text>')
    return out


def _object_els(verts: List[TC.Point], lay: Dict[str, int], image: bool) -> List[str]:
    out: List[str] = []
    pts = [(proj_x(lay, v[0]), proj_y(lay, v[1])) for v in verts]
    if len(pts) >= 2:
        edge = "tx-img-edge" if image else "tx-src-edge"
        d = "M " + " L ".join(f"{x} {y}" for x, y in pts)
        if len(pts) >= 3:
            d += " Z"
        out.append(f'<path class="{edge}" d="{d}"/>')
    for x, y in pts:
        if image:
            out.append(f'<rect class="tx-img-open" x="{x - 7}" y="{y - 7}" width="14" height="14"/>')
        else:
            out.append(f'<circle class="tx-src-core" cx="{x}" cy="{y}" r="6"/>')
    return out


def _label_els(placed: List[Dict[str, Any]]) -> List[str]:
    return [f'<text class="tx-lbl" x="{p["x"]}" y="{p["y"]}" text-anchor="{p["anchor"]}">{_esc(p["text"])}</text>'
            for p in placed]


def _overlay_els(task: str, desc: Dict[str, Any], src: List[TC.Point], img: List[TC.Point],
                 lay: Dict[str, int]) -> List[str]:
    """The answer-key-only solution overlay (owner N). Names/draws the transformation."""
    out: List[str] = ['<g class="tx-overlay">']
    kind = desc["kind"]
    if kind == "translation":
        # one representative vector arrow from a source vertex to its image
        sx, sy = proj_x(lay, src[0][0]), proj_y(lay, src[0][1])
        ix, iy = proj_x(lay, img[0][0]), proj_y(lay, img[0][1])
        out.append(f'<line class="tx-vec" x1="{sx}" y1="{sy}" x2="{ix}" y2="{iy}"/>')
    elif kind == "reflection":
        ax = desc["axis"]
        wx0, wx1, wy0, wy1 = lay["wx0"], lay["wx1"], lay["wy0"], lay["wy1"]
        if ax["kind"] == "vertical":
            x = proj_x(lay, ax["value"])
            out.append(f'<line class="tx-mirror" x1="{x}" y1="{proj_y(lay, wy0)}" x2="{x}" y2="{proj_y(lay, wy1)}"/>')
        elif ax["kind"] == "horizontal":
            y = proj_y(lay, ax["value"])
            out.append(f'<line class="tx-mirror" x1="{proj_x(lay, wx0)}" y1="{y}" x2="{proj_x(lay, wx1)}" y2="{y}"/>')
        else:
            lo, hi = max(wx0, wy0), min(wx1, wy1) if ax["equation"] == "y=x" else None
            if ax["equation"] == "y=x":
                a, b = max(wx0, wy0), min(wx1, wy1)
                out.append(f'<line class="tx-mirror" x1="{proj_x(lay, a)}" y1="{proj_y(lay, a)}" x2="{proj_x(lay, b)}" y2="{proj_y(lay, b)}"/>')
            else:
                a = max(wx0, -wy1); b = min(wx1, -wy0)
                out.append(f'<line class="tx-mirror" x1="{proj_x(lay, a)}" y1="{proj_y(lay, -a)}" x2="{proj_x(lay, b)}" y2="{proj_y(lay, -b)}"/>')
    elif kind == "rotation":
        c = desc["centre"]
        cx, cy = proj_x(lay, c["x"]), proj_y(lay, c["y"])
        out.append(f'<circle class="tx-centre" cx="{cx}" cy="{cy}" r="6"/>')
    out.append("</g>")
    return out


def _arrow_defs() -> str:
    return ('<defs><marker id="tx-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" '
            'orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#111"/></marker></defs>')


def render(task: str, params: Dict[str, Any], answer_key: bool) -> str:
    """Render the student (answer_key=False) or answer-key (answer_key=True) SVG. The base geometry +
    student annotations are byte-identical across channels; the key appends only the overlay group."""
    src, img, desc = params["source"], params["image"], params["descriptor"]
    obj = params["objectType"]
    perform = not task.startswith("describe")
    lay = params["layout"]
    acc = _accessibility(task, params)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" role="img" aria-label="{_esc(acc["alt"])}">']
    out.append(f"<title>{_esc(acc['title'])}</title><desc>{_esc(acc['desc'])}</desc>")
    out.append(f"<style>{STYLE}</style>{_arrow_defs()}")
    out += _grid_axes(lay)

    # base geometry + student annotations (identical in both channels)
    out += _object_els(src, lay, image=False)
    label_items = [(lab, proj_x(lay, v[0]), proj_y(lay, v[1])) for lab, v in zip(TS.SOURCE_LABELS[obj], src)]
    show_image_in_student = not perform  # describe tasks show the image to the student (owner N)
    if show_image_in_student:
        out += _object_els(img, lay, image=True)
        label_items += [(lab, proj_x(lay, v[0]), proj_y(lay, v[1])) for lab, v in zip(TS.image_labels(obj), img)]
    placed = _place_labels(label_items)
    params["_labelPlacements"] = placed
    out += _label_els(placed)

    if answer_key:
        if perform:
            # the key reveals the image first, then the overlay (owner N)
            out += _object_els(img, lay, image=True)
            img_labels = _place_labels([(lab, proj_x(lay, v[0]), proj_y(lay, v[1]))
                                        for lab, v in zip(TS.image_labels(obj), img)])
            out += _label_els(img_labels)
        out += _overlay_els(task, desc, src, img, lay)

    out.append("</svg>")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Parameter draw
# --------------------------------------------------------------------------- #
GRID = 6  # coordinates drawn from [-GRID, GRID]


def _rand_point(rng: Mulberry32, lo: int = -GRID, hi: int = GRID) -> TC.Point:
    return (rng.next_int(lo, hi), rng.next_int(lo, hi))


def _rand_triangle(rng: Mulberry32) -> List[TC.Point]:
    for _ in range(60):
        v = [_rand_point(rng, -4, 4) for _ in range(3)]
        if not TS.is_collinear(v) and len({v[0], v[1], v[2]}) == 3:
            return v
    return [(0, 0), (3, 0), (0, 2)]


def _rand_quad(rng: Mulberry32) -> List[TC.Point]:
    for _ in range(80):
        cx, cy = rng.next_int(-2, 2), rng.next_int(-2, 2)
        offs = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
        v = [(cx + ox * rng.next_int(1, 3), cy + oy * rng.next_int(1, 3)) for ox, oy in offs]
        if len(set(v)) == 4 and TS.is_simple_quad(v) and TS.signed_area2(v) != 0:
            return v
    return [(1, 1), (-1, 1), (-1, -1), (1, -1)]


def _rand_segment(rng: Mulberry32) -> List[TC.Point]:
    for _ in range(40):
        a, b = _rand_point(rng, -4, 4), _rand_point(rng, -4, 4)
        if a != b:
            return [a, b]
    return [(-2, -1), (3, 2)]


def _draw_object(rng: Mulberry32, obj: str) -> List[TC.Point]:
    return {"point": lambda: [_rand_point(rng)], "segment": lambda: _rand_segment(rng),
            "triangle": lambda: _rand_triangle(rng), "quadrilateral": lambda: _rand_quad(rng)}[obj]()


def _draw_descriptor(rng: Mulberry32, kind: str) -> Dict[str, Any]:
    if kind == "translation":
        while True:
            dx, dy = rng.next_int(-5, 5), rng.next_int(-5, 5)
            if (dx, dy) != (0, 0):
                return TC.translation_desc(dx, dy)
    if kind == "reflection":
        choice = rng.next_int(0, 3)
        if choice == 0:
            return TC.reflection_vertical(rng.next_int(-3, 3))
        if choice == 1:
            return TC.reflection_horizontal(rng.next_int(-3, 3))
        if choice == 2:
            return TC.reflection_diagonal("y=x")
        return TC.reflection_diagonal("y=-x")
    # rotation
    return TC.rotation_desc(rng.next_int(-3, 3), rng.next_int(-3, 3), rng.next_int(1, 3))


def _object_for_task(task: str, rng: Mulberry32) -> str:
    if task.endswith("_point"):
        return "point"
    if task.startswith("describe"):
        return "triangle" if rng.next_int(0, 1) == 0 else "quadrilateral"
    # shape perform tasks: segment / triangle / quadrilateral
    return ["segment", "triangle", "quadrilateral"][rng.next_int(0, 2)]


def _in_grid(verts: List[TC.Point], bound: int = GRID + 2) -> bool:
    return all(-bound <= v[0] <= bound and -bound <= v[1] <= bound for v in verts)


def _params(seed: int, task: str) -> Dict[str, Any]:
    rng = Mulberry32(seed)
    kind = FAMILY_KIND[task]
    for _ in range(200):
        obj = _object_for_task(task, rng)
        src = _draw_object(rng, obj)
        desc = _draw_descriptor(rng, kind)
        img = [TC.apply_transform(desc, p) for p in src]
        if not _in_grid(src) or not _in_grid(img):
            continue
        if TS.is_unchanged(src, img):
            continue
        lay = _viewport(src + img)
        if lay is None:
            continue
        if task.startswith("describe"):
            # describe item is valid iff exactly one descriptor of the EXPECTED family fits (owner D)
            uniq = TS.unique_descriptor(kind, src, img)
            if uniq is None or not TC.descriptors_equal(uniq, desc):
                continue
        return {"task": task, "objectType": obj, "source": src, "image": img,
                "descriptor": desc, "kind": kind, "layout": lay}
    raise RuntimeError(f"could not draw a valid item for {task} seed={seed}")


# --------------------------------------------------------------------------- #
# Answer encoding (owner B)
# --------------------------------------------------------------------------- #
def _coord(p: TC.Point) -> Dict[str, int]:
    return {"x": p[0], "y": p[1]}


def _answer(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if task.endswith("_point"):
        p = params["image"][0]
        return {"type": "coordinate", "canonical": _coord(p), "display": f"({p[0]}, {p[1]})"}
    if task.startswith("describe"):
        return TC.answer_object(params["descriptor"])
    # shape -> table-completion, one cell per labelled image vertex, correspondence by label (owner B)
    obj = params["objectType"]
    cells = [{"location": lab, "value": _coord(v)}
             for lab, v in zip(TS.image_labels(obj), params["image"])]
    disp = ", ".join(f"{c['location']}=({c['value']['x']}, {c['value']['y']})" for c in cells)
    return {"type": "table-completion", "canonical": {"cells": cells}, "display": disp}


# --------------------------------------------------------------------------- #
# Difficulty (owner: difficulty + edge-case policy)
# --------------------------------------------------------------------------- #
TASK_BANDS = {
    "translate_point": (1, 2), "translate_shape": (2, 3), "reflect_point": (2, 3),
    "reflect_shape": (2, 3), "rotate_point": (2, 3), "rotate_shape": (3, 4),
    "describe_translation": (2, 3), "describe_reflection": (3, 4), "describe_rotation": (3, 4),
}


def _round3(x: float):
    r = round(x, 3)
    return int(r) if r == int(r) else r  # int when whole (parity-critical)


def _is_high_complexity(task: str, params: Dict[str, Any]) -> bool:
    """A deterministic structural lever selecting the upper of a task's two declared bands. Each lever
    varies across seeds so BOTH declared bands are reachable (owner O band-reachability)."""
    kind = params["kind"]
    obj = params["objectType"]
    desc = params["descriptor"]
    if kind == "translation" and task.endswith("_point"):
        v = desc["vector"]
        return abs(v["dx"]) + abs(v["dy"]) >= 5            # larger vectors -> harder
    if kind == "reflection":
        return desc["axis"]["kind"] == "diagonal"          # y=x / y=-x are harder than x=a / y=b
    if kind == "rotation":
        return desc["quarterTurnsCCW"] != 2                # quarter turns harder than a half turn
    return obj == "quadrilateral"                          # translate_shape / describe_translation


def _difficulty(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    kind = params["kind"]
    obj = params["objectType"]
    desc = params["descriptor"]
    high = _is_high_complexity(task, params)
    lo, hi = TASK_BANDS[task]
    band = hi if high else lo

    # Descriptive axes (transparency only; the band is the structural lever above). All exact (owner F).
    mags = [abs(v[0]) + abs(v[1]) for v in params["source"] + params["image"]]
    nc = min(1.0, (max(mags) if mags else 0) / 24.0)
    ev = 0.0
    rs = {"translation": 0.30, "reflection": 0.50, "rotation": 0.70}[kind]
    if task.startswith("describe"):
        rs = min(1.0, rs + 0.20)
    elif not task.endswith("_point"):
        rs = min(1.0, rs + 0.10)
    ab = {"point": 0.20, "segment": 0.35, "triangle": 0.45, "quadrilateral": 0.60}[obj]
    if task.startswith("describe"):
        ab = min(1.0, ab + 0.20)
    if high:
        ab = min(1.0, ab + 0.10)
    axes = {"numericalComplexity": _round3(nc), "exactVsApproximate": _round3(ev),
            "reasoningSteps": _round3(rs), "abstraction": _round3(ab)}
    return {"overallBand": band, "axes": axes}


# --------------------------------------------------------------------------- #
# Accessibility (owner N: no leakage of the answer/transformation in perform/student text)
# --------------------------------------------------------------------------- #
def _obj_phrase(obj: str) -> str:
    return {"point": "point", "segment": "line segment", "triangle": "triangle",
            "quadrilateral": "quadrilateral"}[obj]


def _src_label_str(obj: str) -> str:
    return "".join(TS.SOURCE_LABELS[obj])


def _accessibility(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    obj = params["objectType"]
    src = params["source"]
    perform = not task.startswith("describe")
    src_desc = "; ".join(f"{lab} at ({v[0]}, {v[1]})" for lab, v in zip(TS.SOURCE_LABELS[obj], src))
    if perform:
        instr = _instruction(task, params)
        alt = f"A coordinate grid showing {_obj_phrase(obj)} {_src_label_str(obj)} with vertices {src_desc}. {instr}"
        title = f"Coordinate grid with {_obj_phrase(obj)} {_src_label_str(obj)}"
        desc = f"{_obj_phrase(obj).capitalize()} {_src_label_str(obj)}: {src_desc}. The image is not shown."
        table = [["Vertex", "Coordinates"]] + [[lab, f"({v[0]}, {v[1]})"] for lab, v in zip(TS.SOURCE_LABELS[obj], src)]
    else:
        img = params["image"]
        img_desc = "; ".join(f"{lab} at ({v[0]}, {v[1]})" for lab, v in zip(TS.image_labels(obj), img))
        alt = (f"A coordinate grid showing {_obj_phrase(obj)} {_src_label_str(obj)} ({src_desc}) and its image "
               f"({img_desc}). Describe the single transformation that maps the object onto its image.")
        title = f"Coordinate grid with an object and its image"
        desc = f"Object {_src_label_str(obj)}: {src_desc}. Image: {img_desc}."
        table = ([["Vertex", "Object", "Image"]]
                 + [[TS.SOURCE_LABELS[obj][i], f"({src[i][0]}, {src[i][1]})", f"({img[i][0]}, {img[i][1]})"]
                    for i in range(len(src))])
    return {"alt": alt, "title": title, "desc": desc, "dataTable": table,
            "spokenMath": alt, "longDescription": f"{title}. {desc}"}


# --------------------------------------------------------------------------- #
# Prompt + solution
# --------------------------------------------------------------------------- #
def _vec_phrase(desc: Dict[str, Any]) -> str:
    v = desc["vector"]
    return f"({v['dx']}, {v['dy']})"


def _instruction(task: str, params: Dict[str, Any]) -> str:
    obj = params["objectType"]
    desc = params["descriptor"]
    lab = _src_label_str(obj)
    if task.startswith("translate"):
        return f"Translate {_obj_phrase(obj)} {lab} by the vector {_vec_phrase(desc)}."
    if task.startswith("reflect"):
        return f"Reflect {_obj_phrase(obj)} {lab} in {TC._axis_equation(desc['axis'])}."
    if task.startswith("rotate"):
        c = desc["centre"]; q = desc["quarterTurnsCCW"]; deg = TC.QUARTER_DEGREES[q]
        dirn = "" if q == 2 else " anticlockwise"
        return f"Rotate {_obj_phrase(obj)} {lab} {deg}°{dirn} about ({c['x']}, {c['y']})."
    # describe
    img_lab = "".join(TS.image_labels(obj))
    fam = {"translation": "translation", "reflection": "reflection", "rotation": "rotation"}[params["kind"]]
    return f"Describe fully the {fam} that maps {lab} onto {img_lab}."


def _prompt(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    obj = params["objectType"]
    perform = not task.startswith("describe")
    instr = _instruction(task, params)
    if perform and task.endswith("_point"):
        ask = "Give the coordinates of the image."
    elif perform:
        ask = f"Give the coordinates of each image vertex ({''.join(TS.image_labels(obj))})."
    else:
        ask = "Give the full description of the transformation."
    return {"blocks": [{"kind": "text", "text": f"{instr} {ask}"}]}


def _solution(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    desc = params["descriptor"]; src = params["source"]; img = params["image"]; obj = params["objectType"]
    steps: List[Dict[str, Any]] = []
    if task.startswith("describe"):
        ans = TC.answer_object(desc)["display"]
        steps.append({"number": 1, "transformation": "Compare corresponding labelled vertices to identify the transformation.",
                      "intermediateResult": "; ".join(f"{a}->{b}" for a, b in zip(TS.SOURCE_LABELS[obj], TS.image_labels(obj)))})
        steps.append({"number": 2, "transformation": "Determine the parameters from the correspondence.",
                      "intermediateResult": ans})
        return {"steps": steps}
    kind = params["kind"]
    if kind == "translation":
        rule = "Add the vector to each coordinate."
    elif kind == "reflection":
        rule = f"Apply the reflection rule for {TC._axis_equation(desc['axis'])}."
    else:
        rule = "Measure each vertex from the centre and apply the quarter-turn rule."
    steps.append({"number": 1, "transformation": rule,
                  "intermediateResult": "; ".join(f"({s[0]}, {s[1]})->({t[0]}, {t[1]})" for s, t in zip(src, img))})
    return {"steps": steps}


# --------------------------------------------------------------------------- #
# Public generate()
# --------------------------------------------------------------------------- #
def generate(seed: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    config = config or {}
    interaction = config.get("interactionType", "free-response")
    if interaction not in SUPPORTED_INTERACTIONS:
        raise InteractionNotSupported(
            f"gen.geometry.transformations supports only free-response in v1.0.0 (requested {interaction!r})")
    task = config.get("task")
    if task is None:
        task = _TASKS[Mulberry32(seed).next_int(0, len(_TASKS) - 1)]
    if task not in OBJECTIVE_BY_TASK:
        raise ValueError(f"unknown task {task!r}")

    params = _params(seed, task)
    student_svg = render(task, params, answer_key=False)
    key_svg = render(task, params, answer_key=True)
    acc = _accessibility(task, params)
    diff = _difficulty(task, params)
    ans = _answer(task, params)

    item: Dict[str, Any] = {
        "itemId": f"ITEM-TRANS-{task}-{seed}",
        "schemaVersion": "1.0.0",
        "objectiveIds": [OBJECTIVE_BY_TASK[task]],
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "seed": seed,
        "interactionType": "free-response",
        "prompt": _prompt(task, params),
        "answer": ans,
        "solution": _solution(task, params),
        "media": [{
            "id": "fig-1",
            "kind": "svg",
            "svg": student_svg,
            "spec": {"answerKeySvg": key_svg, "labelPlacements": params.get("_labelPlacements", [])},
            "toScale": True,
            "altText": acc["alt"],
            "longDescription": acc["longDescription"],
            "dataTableFallback": {"columns": acc["dataTable"][0], "rows": acc["dataTable"][1:]},
        }],
        "provenance": {"origin": "generated", "rightsStatus": "academy-owned"},
        "lifecycle": {"state": "generated"},
        "accessibility": {
            "spokenMath": acc["spokenMath"],
            "altText": acc["alt"],
            "longDescription": acc["longDescription"],
            "nonColorIndicators": True,
        },
        "difficulty": diff,
        "params": {
            "task": task,
            "objectType": params["objectType"],
            "transformationKind": params["kind"],
            "descriptor": TC.canonicalize_descriptor(params["descriptor"]),
            "source": [_coord(p) for p in params["source"]],
            "image": [_coord(p) for p in params["image"]],
        },
    }
    return item


_TASKS = list(OBJECTIVE_BY_TASK.keys())
TASKS = _TASKS


# --------------------------------------------------------------------------- #
# Independent validator (owner H, G, M, N) — re-derives everything from params; NEVER trusts the
# forward engine output stored in the item. Returns {valid, checks:[{name, ok, detail}]}.
# --------------------------------------------------------------------------- #
def _pts(coords: List[Dict[str, int]]) -> List[TC.Point]:
    return [(c["x"], c["y"]) for c in coords]


def validate(item: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    p = item["params"]
    task = p["task"]
    obj = p["objectType"]
    kind = p["transformationKind"]
    desc = p["descriptor"]
    src = _pts(p["source"])
    img = _pts(p["image"])
    perform = not task.startswith("describe")

    # not the identity (owner D/E)
    add("object-not-unchanged", not TS.is_unchanged(src, img))

    # independent re-derivation of the image (owner H) — does not call apply_transform
    if kind == "translation":
        v = desc["vector"]
        add("inverse-transformation-restores-source",
            TS.verify_translation(src, img, v["dx"], v["dy"]) and (v["dx"], v["dy"]) != (0, 0))
    elif kind == "reflection":
        add("reflection-axis-condition", TS.verify_reflection(src, img, desc["axis"]))
    else:
        c = desc["centre"]
        add("rotation-quarter-turn-agreement", TS.verify_rotation(src, img, c["x"], c["y"], desc["quarterTurnsCCW"]))

    # congruence by squared distances (owner G) + orientation rule
    add("congruence-squared-distances", TS.congruent_in_correspondence(src, img, obj))
    if obj in ("triangle", "quadrilateral"):
        so, io = TS.orientation_sign(src), TS.orientation_sign(img)
        if kind == "reflection":
            add("orientation-reversed", so == -io and so != 0)
        else:
            add("orientation-preserved", so == io and so != 0)

    # stored answer agrees with the descriptor (owner H)
    ans = item["answer"]
    if perform and task.endswith("_point"):
        add("answer-agrees-with-descriptor", ans["type"] == "coordinate" and ans["canonical"] == {"x": img[0][0], "y": img[0][1]})
    elif perform:
        cells = ans["canonical"]["cells"]
        by_label = {c["location"]: (c["value"]["x"], c["value"]["y"]) for c in cells}
        want = {lab: v for lab, v in zip(TS.image_labels(obj), img)}
        add("answer-agrees-with-descriptor", ans["type"] == "table-completion" and by_label == want)
        add("no-vertex-omitted-or-mislabelled", set(by_label) == set(want) and len(cells) == len(img))
    else:
        add("answer-agrees-with-descriptor",
            ans["type"] == "transformation" and TC.descriptors_equal(ans["canonical"], desc))
        add("descriptor-display-derived", ans["display"] == TC.format_display(TC.canonicalize_descriptor(ans["canonical"])))
        # describe items: exactly one descriptor of the EXPECTED family fits (owner D)
        uniq = TS.unique_descriptor(kind, src, img)
        add("descriptor-unique", uniq is not None and TC.descriptors_equal(uniq, desc))

    # channels (owner N): base geometry identical, key is additive
    media = item["media"][0]
    student = media["svg"]
    key = media["spec"]["answerKeySvg"]
    add("answer-key-base-geometry-identical", key.startswith(student[: student.rindex("</svg>")]))
    add("answer-key-overlay-additive-only", len(key) >= len(student) and student != key)

    # leakage (owner N): the perform student channel must not draw the image or list its vertices.
    # (The instruction legitimately states the given vector/centre/axis, so we check STRUCTURE — the
    # hidden image figure and the source-only data table — not coordinate substrings.)
    if perform:
        add("perform-student-image-hidden", '<rect class="tx-img-open"' not in student)
        rows = media["dataTableFallback"]["rows"]
        src_strs = sorted(f"({v[0]}, {v[1]})" for v in src)
        add("perform-student-table-source-only",
            len(rows) == len(src) and sorted(r[1] for r in rows) == src_strs)
    else:
        add("describe-student-shows-both-figures", '<rect class="tx-img-open"' in student)
        add("describe-student-no-descriptor-named", TC.format_display(desc) not in student)

    # label clearance (owner M)
    placements = media["spec"].get("labelPlacements", [])
    add("label-inside-canvas", all(not pl.get("clearanceFailed") for pl in placements))
    add("label-bbox-clearance", _labels_pairwise_clear(placements))

    valid = all(c["ok"] for c in checks)
    return {"valid": valid, "validatorVersion": VALIDATOR_VERSION, "checks": checks}


def _labels_pairwise_clear(placements: List[Dict[str, Any]]) -> bool:
    boxes = [tuple(pl["box"]) for pl in placements if "box" in pl]
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if _overlap(boxes[i], boxes[j]):
                return False
    return True


def serialize(item: Dict[str, Any]) -> str:
    """Canonical JSON (sorted keys, compact) — the byte-for-byte parity contract with the TS mirror,
    matching json.dumps(sort_keys=True, ensure_ascii=False, separators=(',', ':'))."""
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def describe() -> Dict[str, Any]:
    return {
        "generatorId": GENERATOR_ID,
        "version": GENERATOR_VERSION,
        "title": "Coordinate transformations",
        "domain": "geometry",
        "strand": "coordinate-transformations",
        "objectiveIds": list(OBJECTIVE_BY_TASK.values()),
        "tasks": list(_TASKS),
        "interactionTypes": list(SUPPORTED_INTERACTIONS),
        "answerTypes": ["coordinate", "table-completion", "transformation"],
        "approvalStatus": "pending-review",
    }
