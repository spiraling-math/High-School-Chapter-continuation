"""gen.geometry.transformations — labelled object model, exact congruence + orientation checks
(owner G), the INDEPENDENT validator (owner H), describe-task family-specific uniqueness (owner D),
and the fixed-point policy (owner E).

The validator NEVER calls the forward engine apply_transform (owner H). Translation, reflection, and
rotation images are confirmed by independent re-derivation from labelled correspondences; describe
items are confirmed by reconstructing candidates WITHIN the expected transformation family and
requiring exactly one. All arithmetic is exact integer / Fraction — no trig, float, or tolerance.

domains/geometry/transformations-shapes.ts mirrors this byte-for-byte.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from .transformations_core import (
    Point, reflection_vertical, reflection_horizontal, reflection_diagonal,
    rotation_desc, translation_desc,
)

# A labelled object: object type + labels (source) + integer vertices, correspondence by index/label.
OBJECT_VERTEX_COUNT = {"point": 1, "segment": 2, "triangle": 3, "quadrilateral": 4}
SOURCE_LABELS = {
    "point": ["P"], "segment": ["A", "B"], "triangle": ["A", "B", "C"],
    "quadrilateral": ["A", "B", "C", "D"],
}
PRIME = "′"  # U+2032 PRIME — canonical image-label suffix (owner B)


def image_labels(obj_type: str) -> List[str]:
    return [lab + PRIME for lab in SOURCE_LABELS[obj_type]]


# --------------------------------------------------------------------------- #
# Exact metric primitives (owner G)
# --------------------------------------------------------------------------- #
def sq_dist(p: Point, q: Point) -> int:
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def _pairwise_sq_dists(verts: List[Point]) -> List[int]:
    n = len(verts)
    return [sq_dist(verts[i], verts[j]) for i in range(n) for j in range(i + 1, n)]


def signed_area2(verts: List[Point]) -> int:
    """Twice the signed area of the polygon (shoelace). >0 anticlockwise, <0 clockwise, 0 degenerate."""
    n = len(verts)
    s = 0
    for i in range(n):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return s


def orientation_sign(verts: List[Point]) -> int:
    a = signed_area2(verts)
    return (a > 0) - (a < 0)


def is_collinear(verts: List[Point]) -> bool:
    return signed_area2(verts) == 0


def _segments_cross(a: Point, b: Point, c: Point, d: Point) -> bool:
    """Do open segments ab and cd properly intersect? Exact integer orientation test."""
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    d1, d2, d3, d4 = o(c, d, a), o(c, d, b), o(a, b, c), o(a, b, d)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and d1 != 0 and d2 != 0 and d3 != 0 and d4 != 0:
        return True
    return False


def is_simple_quad(verts: List[Point]) -> bool:
    """A quadrilateral boundary A-B-C-D-A is simple iff its two pairs of non-adjacent edges
    do not cross (owner G)."""
    a, b, c, d = verts
    return not (_segments_cross(a, b, c, d) or _segments_cross(b, c, d, a))


def congruent_in_correspondence(source: List[Point], image: List[Point], obj_type: str) -> bool:
    """Exact congruence by squared distances in label correspondence (owner G).
    Segment: the one squared length. Triangle: all 3 pairwise squared distances + non-collinear.
    Quadrilateral: all 6 pairwise squared distances (4 sides + 2 diagonals) + simple boundary.
    Orientation is checked separately by the per-transform validators, not here."""
    if obj_type == "point":
        return True
    if _pairwise_sq_dists(source) != _pairwise_sq_dists(image):
        return False
    if obj_type == "triangle":
        return not is_collinear(source) and not is_collinear(image)
    if obj_type == "quadrilateral":
        return is_simple_quad(source) and is_simple_quad(image)
    return True  # segment: single squared length already compared


def is_unchanged(source: List[Point], image: List[Point]) -> bool:
    return list(source) == list(image)


# --------------------------------------------------------------------------- #
# Independent per-transform image verification (owner H) — NOT via apply_transform.
# Each returns True iff the image is exactly the named transformation of the source, in
# label correspondence, allowing valid fixed points (owner E).
# --------------------------------------------------------------------------- #
def verify_translation(source: List[Point], image: List[Point], dx: int, dy: int) -> bool:
    if dx == 0 and dy == 0:
        return False
    return all((t[0] - s[0], t[1] - s[1]) == (dx, dy) for s, t in zip(source, image))


def verify_reflection(source: List[Point], image: List[Point], axis: Dict[str, Any]) -> bool:
    for s, t in zip(source, image):
        if axis["kind"] == "vertical":           # x = a: midpoint x = a, perpendicular is horizontal
            if not (s[1] == t[1] and s[0] + t[0] == 2 * axis["value"]):
                return False
        elif axis["kind"] == "horizontal":       # y = b
            if not (s[0] == t[0] and s[1] + t[1] == 2 * axis["value"]):
                return False
        elif axis["kind"] == "diagonal":
            if axis["equation"] == "y=x":
                if not (s[0] == t[1] and s[1] == t[0]):
                    return False
            else:                                 # y = -x
                if not (s[0] == -t[1] and s[1] == -t[0]):
                    return False
    return True


def _rotation_relation(s: Point, t: Point, h: int, k: int, q: int) -> bool:
    X, Y = s[0] - h, s[1] - k
    if q == 1:
        rx, ry = -Y, X
    elif q == 2:
        rx, ry = -X, -Y
    else:
        rx, ry = Y, -X
    return (t[0] - h, t[1] - k) == (rx, ry)


def verify_rotation(source: List[Point], image: List[Point], h: int, k: int, q: int) -> bool:
    """Independent: equal squared distance from the centre, the exact centre-relative quarter-turn
    relation, preserved orientation (for polygons), and inverse-rotation restoring every vertex."""
    inv = {1: 3, 2: 2, 3: 1}[q]
    for s, t in zip(source, image):
        if sq_dist(s, (h, k)) != sq_dist(t, (h, k)):
            return False
        if not _rotation_relation(s, t, h, k, q):
            return False
        if not _rotation_relation(t, s, h, k, inv):  # inverse restores the source
            return False
    return True


# --------------------------------------------------------------------------- #
# Candidate reconstruction WITHIN one family (owner D, H) — for describe-task uniqueness.
# Each returns the list of distinct supported descriptors of that family mapping every labelled
# source vertex onto its corresponding image vertex. Fixed points are tolerated (owner E).
# --------------------------------------------------------------------------- #
def reconstruct_translations(source: List[Point], image: List[Point]) -> List[Dict[str, Any]]:
    dx, dy = image[0][0] - source[0][0], image[0][1] - source[0][1]
    if (dx, dy) == (0, 0):
        return []
    return [translation_desc(dx, dy)] if verify_translation(source, image, dx, dy) else []


def reconstruct_reflections(source: List[Point], image: List[Point]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    moving = [(s, t) for s, t in zip(source, image) if s != t]
    if not moving:
        return out
    s0, t0 = moving[0]
    # vertical x = a
    if (s0[0] + t0[0]) % 2 == 0:
        a = (s0[0] + t0[0]) // 2
        cand = reflection_vertical(a)
        if verify_reflection(source, image, cand["axis"]):
            out.append(cand)
    # horizontal y = b
    if (s0[1] + t0[1]) % 2 == 0:
        b = (s0[1] + t0[1]) // 2
        cand = reflection_horizontal(b)
        if verify_reflection(source, image, cand["axis"]) and cand not in out:
            out.append(cand)
    for eq in ("y=x", "y=-x"):
        cand = reflection_diagonal(eq)
        if verify_reflection(source, image, cand["axis"]) and cand not in out:
            out.append(cand)
    return out


def _solve_centre(s: Point, t: Point, q: int) -> Optional[Point]:
    sx, sy = s
    tx, ty = t
    if q == 2:
        hx, ky = Fraction(sx + tx, 2), Fraction(sy + ty, 2)
    elif q == 1:
        hx = Fraction(tx - ty + sx + sy, 2)
        ky = Fraction(tx + ty - sx + sy, 2)
    else:  # q == 3
        hx = Fraction(tx + ty - sy + sx, 2)
        ky = Fraction(sx + sy - tx + ty, 2)
    if hx.denominator != 1 or ky.denominator != 1:
        return None
    return (int(hx), int(ky))


def reconstruct_rotations(source: List[Point], image: List[Point]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    moving = [(s, t) for s, t in zip(source, image) if s != t]
    if not moving:
        return out
    s0, t0 = moving[0]
    for q in (1, 2, 3):
        centre = _solve_centre(s0, t0, q)
        if centre is None:
            continue
        if verify_rotation(source, image, centre[0], centre[1], q):
            out.append(rotation_desc(centre[0], centre[1], q))
    return out


_RECONSTRUCT = {
    "translation": reconstruct_translations,
    "reflection": reconstruct_reflections,
    "rotation": reconstruct_rotations,
}


def describe_candidates(kind: str, source: List[Point], image: List[Point]) -> List[Dict[str, Any]]:
    """All supported descriptors of `kind` that map the complete labelled source onto the image."""
    return _RECONSTRUCT[kind](source, image)


def unique_descriptor(kind: str, source: List[Point], image: List[Point]) -> Optional[Dict[str, Any]]:
    """The single descriptor of the EXPECTED family (owner D), or None if zero or >1 fit, or the
    whole labelled object is unchanged (owner D/E)."""
    if is_unchanged(source, image):
        return None
    cands = describe_candidates(kind, source, image)
    return cands[0] if len(cands) == 1 else None
