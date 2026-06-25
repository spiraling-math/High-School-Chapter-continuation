"""gen.geometry.transformations — MISC.TRANS.* registry and per-item diagnostics (owner K).

This module is the SINGLE source of truth for transformation misconception IDs (owner K). Objective
commonMisconceptions, RULES_BY_TASK, the TypeScript mirror, tests, fixtures, and review-pack tokens all
draw from here. Five descriptor diagnostics use the owner's exact IDs (RIGHT_TYPE_WRONG_VECTOR,
RIGHT_REFLECTION_WRONG_AXIS, RIGHT_ANGLE_MISSING_CENTRE, RIGHT_CENTRE_WRONG_DIRECTION,
NAMES_REFLECTION_FOR_ROTATION); no competing DESC_* spellings exist.

Each diagnostic declares kind + applicability + predicted response + observableError + feedback +
expectedResultCode + diagnosticOnly. Following the mensuration C4 precedent: a structurally-valid-but-
wrong answer carries a canonical predicted descriptor/coordinate; an incomplete/malformed answer carries
studentResponseText + expectedResultCode and is classified parser/diagnosticOnly (never a manufactured
invalid canonical such as centre:null). A diagnostic that is inapplicable to the item, or whose predicted
response collides with the correct answer, is OMITTED — it must not count as exercised coverage (owner K).

domains/geometry/transformations-misconceptions.ts mirrors this byte-for-byte.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .transformations_core import (
    Point, QUARTER_DEGREES, apply_transform, format_display, reflection_vertical,
    reflection_horizontal, rotation_desc, translation_desc, rotate_quarter,
    reflect_x_eq_a, reflect_y_eq_b, reflect_y_eq_x, reflect_y_eq_negx,
)

DOMAIN = "geometry"


def _m(mid: str, title: str, obs: str, feedback: str, hint: str, objs: List[str]) -> Dict[str, Any]:
    return {
        "misconceptionId": mid, "domain": DOMAIN, "title": title,
        "description": obs, "observableError": obs,
        "feedback": feedback, "remediationHint": hint,
        "objectiveRelationships": list(objs),
        "reviewStatus": "proposed", "version": "1.0.0",
    }


_TR = ["SPI.MIDDLE.GEO.TRANS.TRANSLATE_POINT.01", "SPI.MIDDLE.GEO.TRANS.TRANSLATE_SHAPE.01"]
_RF = ["SPI.MIDDLE.GEO.TRANS.REFLECT_POINT.01", "SPI.MIDDLE.GEO.TRANS.REFLECT_SHAPE.01"]
_RO = ["SPI.MIDDLE.GEO.TRANS.ROTATE_POINT.01", "SPI.MIDDLE.GEO.TRANS.ROTATE_SHAPE.01"]
_DT = ["SPI.MIDDLE.GEO.TRANS.DESCRIBE_TRANSLATION.01"]
_DR = ["SPI.MIDDLE.GEO.TRANS.DESCRIBE_REFLECTION.01"]
_DO = ["SPI.MIDDLE.GEO.TRANS.DESCRIBE_ROTATION.01"]

MISCONCEPTIONS: List[Dict[str, Any]] = [
    # --- translation (6) ---
    _m("MISC.TRANS.REVERSES_VECTOR", "Subtracts the translation vector",
       "Subtracts the vector instead of adding it (moves the opposite way).",
       "A translation by (dx, dy) adds dx to x and dy to y. Move with the vector, not against it.",
       "Add each component of the vector to the matching coordinate.", _TR),
    _m("MISC.TRANS.SWAPS_DX_DY", "Swaps the vector components",
       "Adds dy to x and dx to y, swapping the two components.",
       "The first component changes x; the second changes y. Keep them in order.",
       "Match dx to x and dy to y.", _TR),
    _m("MISC.TRANS.CHANGES_ONLY_X", "Translates horizontally only",
       "Applies the x-component but leaves y unchanged.",
       "A translation moves the point in both directions at once.",
       "Add dy to y as well as dx to x.", _TR),
    _m("MISC.TRANS.CHANGES_ONLY_Y", "Translates vertically only",
       "Applies the y-component but leaves x unchanged.",
       "A translation moves the point in both directions at once.",
       "Add dx to x as well as dy to y.", _TR),
    _m("MISC.TRANS.WRONG_SIGN_ONE_COMPONENT", "Wrong sign on one component",
       "Negates one component of the vector (e.g. moves left instead of right).",
       "Check the sign of each component of the vector before adding.",
       "Keep the signs exactly as the column vector shows.", _TR),
    _m("MISC.TRANS.TRANSLATES_FROM_ORIGIN", "Reads the vector as the image point",
       "Writes the vector itself as the image, ignoring the start point.",
       "Add the vector to the point's coordinates; the vector is not the answer on its own.",
       "Image = start point + vector.", _TR),
    # --- reflection (7) ---
    _m("MISC.TRANS.REFLECTS_X_FOR_Y_AXIS", "Reflects in the wrong orthogonal line",
       "Reflects in a horizontal line when the mirror is vertical (or vice versa).",
       "A vertical mirror x = a changes x; a horizontal mirror y = b changes y.",
       "Decide which coordinate the mirror line fixes.", _RF),
    _m("MISC.TRANS.REFLECTS_Y_FOR_X_AXIS", "Confuses the x-axis and y-axis mirror",
       "Reflects in the x-axis when the mirror is the y-axis (or vice versa).",
       "The x-axis is y = 0 and changes y; the y-axis is x = 0 and changes x.",
       "Name the axis as an equation before reflecting.", _RF),
    _m("MISC.TRANS.NEGATES_WRONG_COORDINATE", "Negates the coordinate the mirror fixes",
       "Changes the coordinate that should stay the same.",
       "Reflection in x = a leaves y unchanged; reflection in y = b leaves x unchanged.",
       "Only the coordinate across the mirror moves.", _RF),
    _m("MISC.TRANS.YX_CHANGES_BOTH_SIGNS", "Confuses y = x with y = -x",
       "Uses (-y, -x) for a reflection in y = x.",
       "Reflection in y = x swaps the coordinates: (x, y) -> (y, x), with no sign change.",
       "Swap x and y for y = x; negate and swap for y = -x.", _RF),
    _m("MISC.TRANS.YNEGX_ONLY_SWAPS", "Confuses y = -x with y = x",
       "Uses (y, x) for a reflection in y = -x, missing the sign change.",
       "Reflection in y = -x gives (x, y) -> (-y, -x).",
       "For y = -x, swap AND negate both coordinates.", _RF),
    _m("MISC.TRANS.REFLECTS_X0_FOR_XA", "Uses the y-axis instead of x = a",
       "Reflects in x = 0 instead of the given vertical line x = a.",
       "Use the actual mirror line x = a, not the y-axis.",
       "Reflection in x = a gives (2a - x, y).", _RF),
    _m("MISC.TRANS.REFLECTS_Y0_FOR_YB", "Uses the x-axis instead of y = b",
       "Reflects in y = 0 instead of the given horizontal line y = b.",
       "Use the actual mirror line y = b, not the x-axis.",
       "Reflection in y = b gives (x, 2b - y).", _RF),
    # --- rotation (6) ---
    _m("MISC.TRANS.ROTATES_WRONG_DIRECTION", "Rotates the wrong way",
       "Turns clockwise when the rotation is anticlockwise (or vice versa).",
       "Check the direction; 90 deg clockwise and 90 deg anticlockwise give different images.",
       "Use the stated direction relative to the centre.", _RO),
    _m("MISC.TRANS.ROTATES_ABOUT_ORIGIN", "Rotates about the origin",
       "Rotates about (0, 0) instead of the given centre.",
       "Rotate about the marked centre, not the origin.",
       "Measure each point's position relative to the centre first.", _RO),
    _m("MISC.TRANS.USES_180_RULE_FOR_90", "Applies the half-turn rule for a quarter turn",
       "Uses the 180 deg rule (negate both) for a 90 or 270 deg rotation.",
       "A quarter turn swaps the coordinates relative to the centre; a half turn negates them.",
       "Apply the correct quarter-turn rule.", _RO),
    _m("MISC.TRANS.SWAPS_WITHOUT_SIGN", "Swaps without the sign change",
       "Swaps the centre-relative coordinates but omits the required sign change.",
       "A quarter turn swaps AND changes a sign relative to the centre.",
       "For 90 deg anticlockwise, (X, Y) -> (-Y, X).", _RO),
    _m("MISC.TRANS.ROTATES_THE_CENTRE", "Shifts by the centre as well",
       "Adds the centre a second time, shifting the whole image.",
       "Translate to the centre, turn, then translate back exactly once.",
       "The centre is used once, to measure relative position.", _RO),
    _m("MISC.TRANS.APPLIES_TO_ONE_VERTEX", "Rotates only one vertex",
       "Turns a single vertex and leaves the rest of the shape unchanged.",
       "Every vertex of the shape must be rotated about the same centre.",
       "Apply the rotation to all labelled vertices.", _RO),
    # --- descriptor diagnostics (5; owner K exact IDs) ---
    _m("MISC.TRANS.RIGHT_TYPE_WRONG_VECTOR", "Right type, wrong translation vector",
       "Names a translation but gives the reversed or mis-signed vector.",
       "Read the vector from a corresponding pair: image - source.",
       "Check the vector against every labelled vertex.", _DT),
    _m("MISC.TRANS.RIGHT_REFLECTION_WRONG_AXIS", "Right type, wrong mirror line",
       "Names a reflection but gives the wrong mirror line.",
       "The mirror line is the perpendicular bisector of each pair of corresponding points.",
       "Find the line equidistant from a point and its image.", _DR),
    _m("MISC.TRANS.RIGHT_ANGLE_MISSING_CENTRE", "Angle without a centre",
       "States the angle and direction but omits the centre of rotation.",
       "A rotation is only fully described with its centre, angle, and direction.",
       "Give the centre of rotation as well as the angle and direction.", _DO),
    _m("MISC.TRANS.RIGHT_CENTRE_WRONG_DIRECTION", "Right centre, wrong direction",
       "Gives the correct centre but the wrong direction (e.g. clockwise for anticlockwise).",
       "Check the turn direction; it determines the image for a quarter turn.",
       "Confirm the direction against a single corresponding pair.", _DO),
    _m("MISC.TRANS.NAMES_REFLECTION_FOR_ROTATION", "Names a reflection for a rotation",
       "Describes a reflection when the mapping is a rotation.",
       "Reflections reverse orientation; rotations preserve it. Check the orientation first.",
       "Compare the sense (orientation) of the source and image.", _DO),
]

ALL_IDS: Tuple[str, ...] = tuple(m["misconceptionId"] for m in MISCONCEPTIONS)


def registry() -> List[Dict[str, Any]]:
    """The schema-conformant misconception records (core/misconceptions/transformations.json)."""
    return [dict(m) for m in MISCONCEPTIONS]


# --------------------------------------------------------------------------- #
# Per-item diagnostics (owner K). A diagnostic is OMITTED when inapplicable or when its predicted
# response collides with the correct answer (so it never counts as exercised coverage).
# --------------------------------------------------------------------------- #
def _diag(mid: str, kind: str, predicted: Any, expected_code: str,
          student_text: Optional[str] = None, diagnostic_only: bool = True) -> Dict[str, Any]:
    rec = next(m for m in MISCONCEPTIONS if m["misconceptionId"] == mid)
    out: Dict[str, Any] = {
        "misconceptionId": mid, "kind": kind, "predicted": predicted,
        "observableError": rec["observableError"], "feedback": rec["feedback"],
        "expectedResultCode": expected_code, "diagnosticOnly": diagnostic_only,
    }
    if student_text is not None:
        out["studentResponseText"] = student_text
    return out


def _value_diags_translation(src: List[Point], desc: Dict[str, Any]) -> List[Tuple[str, List[Point]]]:
    v = desc["vector"]
    dx, dy = v["dx"], v["dy"]
    out: List[Tuple[str, List[Point]]] = []
    out.append(("MISC.TRANS.REVERSES_VECTOR", [(p[0] - dx, p[1] - dy) for p in src]))
    if dx != dy:
        out.append(("MISC.TRANS.SWAPS_DX_DY", [(p[0] + dy, p[1] + dx) for p in src]))
    if dy != 0:
        out.append(("MISC.TRANS.CHANGES_ONLY_X", [(p[0] + dx, p[1]) for p in src]))
    if dx != 0:
        out.append(("MISC.TRANS.CHANGES_ONLY_Y", [(p[0], p[1] + dy) for p in src]))
    if dx != 0:
        out.append(("MISC.TRANS.WRONG_SIGN_ONE_COMPONENT", [(p[0] - dx, p[1] + dy) for p in src]))
    out.append(("MISC.TRANS.TRANSLATES_FROM_ORIGIN", [(dx, dy) for _ in src]))
    return out


def _value_diags_reflection(src: List[Point], desc: Dict[str, Any]) -> List[Tuple[str, List[Point]]]:
    ax = desc["axis"]
    out: List[Tuple[str, List[Point]]] = []
    if ax["kind"] == "vertical":
        a = ax["value"]
        out.append(("MISC.TRANS.REFLECTS_X_FOR_Y_AXIS", [reflect_y_eq_b(p, a) for p in src]))
        out.append(("MISC.TRANS.NEGATES_WRONG_COORDINATE", [(p[0], -p[1]) for p in src]))
        if a != 0:
            out.append(("MISC.TRANS.REFLECTS_X0_FOR_XA", [reflect_x_eq_a(p, 0) for p in src]))
    elif ax["kind"] == "horizontal":
        b = ax["value"]
        out.append(("MISC.TRANS.REFLECTS_X_FOR_Y_AXIS", [reflect_x_eq_a(p, b) for p in src]))
        out.append(("MISC.TRANS.NEGATES_WRONG_COORDINATE", [(-p[0], p[1]) for p in src]))
        if b != 0:
            out.append(("MISC.TRANS.REFLECTS_Y0_FOR_YB", [reflect_y_eq_b(p, 0) for p in src]))
        out.append(("MISC.TRANS.REFLECTS_Y_FOR_X_AXIS", [reflect_x_eq_a(p, b) for p in src]))
    elif ax["kind"] == "diagonal":
        if ax["equation"] == "y=x":
            out.append(("MISC.TRANS.YX_CHANGES_BOTH_SIGNS", [reflect_y_eq_negx(p) for p in src]))
        else:
            out.append(("MISC.TRANS.YNEGX_ONLY_SWAPS", [reflect_y_eq_x(p) for p in src]))
    return out


def _value_diags_rotation(src: List[Point], desc: Dict[str, Any]) -> List[Tuple[str, List[Point]]]:
    c = desc["centre"]
    h, k, q = c["x"], c["y"], desc["quarterTurnsCCW"]
    out: List[Tuple[str, List[Point]]] = []
    if q != 2:
        out.append(("MISC.TRANS.ROTATES_WRONG_DIRECTION", [rotate_quarter(p, h, k, 4 - q) for p in src]))
        out.append(("MISC.TRANS.USES_180_RULE_FOR_90", [rotate_quarter(p, h, k, 2) for p in src]))
    if (h, k) != (0, 0):
        out.append(("MISC.TRANS.ROTATES_ABOUT_ORIGIN", [rotate_quarter(p, 0, 0, q) for p in src]))
    # swaps without sign change: take the q=1/3 swap but drop the sign flip on one axis
    swapped = [(p[1] - k + h, p[0] - h + k) for p in src]
    out.append(("MISC.TRANS.SWAPS_WITHOUT_SIGN", swapped))
    out.append(("MISC.TRANS.ROTATES_THE_CENTRE", [(rp[0] + h, rp[1] + k) for rp in (rotate_quarter(p, h, k, q) for p in src)]))
    if len(src) > 1:
        moved = [rotate_quarter(src[0], h, k, q)] + list(src[1:])
        out.append(("MISC.TRANS.APPLIES_TO_ONE_VERTEX", moved))
    return out


def diagnostics_for(task: str, src: List[Point], descriptor: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Applicable diagnostics for one item. Perform tasks predict a wrong coordinate/table (value
    kind); describe tasks predict a wrong descriptor (descriptor kind) or an incomplete response
    (parser kind). Collisions with the correct image are dropped (owner K)."""
    correct = [apply_transform(descriptor, p) for p in src]
    out: List[Dict[str, Any]] = []

    if task in ("translate_point", "translate_shape"):
        value_diags = _value_diags_translation(src, descriptor)
    elif task in ("reflect_point", "reflect_shape"):
        value_diags = _value_diags_reflection(src, descriptor)
    elif task in ("rotate_point", "rotate_shape"):
        value_diags = _value_diags_rotation(src, descriptor)
    else:
        value_diags = []

    if value_diags:
        is_point = task.endswith("_point")
        for mid, wrong in value_diags:
            if wrong == correct:
                continue  # collides with the correct answer -> not a usable diagnostic
            predicted = {"x": wrong[0][0], "y": wrong[0][1]} if is_point else \
                [{"x": p[0], "y": p[1]} for p in wrong]
            out.append(_diag(mid, "value", predicted, "incorrect-coordinate"))
        return out

    # --- describe tasks ---
    kind = descriptor["kind"]
    if kind == "translation":
        v = descriptor["vector"]
        wrong = translation_desc(-v["dx"], -v["dy"]) if (v["dx"], v["dy"]) != (-v["dx"], -v["dy"]) else translation_desc(v["dy"], v["dx"])
        out.append(_diag("MISC.TRANS.RIGHT_TYPE_WRONG_VECTOR", "descriptor",
                         {"canonical": wrong, "display": format_display(wrong)}, "wrong-translation-vector"))
    elif kind == "reflection":
        ax = descriptor["axis"]
        if ax["kind"] == "vertical":
            wrong = reflection_vertical(0 if ax["value"] != 0 else 1)
        elif ax["kind"] == "horizontal":
            wrong = reflection_horizontal(0 if ax["value"] != 0 else 1)
        else:
            wrong = reflection_vertical(0)
        out.append(_diag("MISC.TRANS.RIGHT_REFLECTION_WRONG_AXIS", "descriptor",
                         {"canonical": wrong, "display": format_display(wrong)}, "wrong-reflection-axis"))
    elif kind == "rotation":
        c = descriptor["centre"]
        h, k, q = c["x"], c["y"], descriptor["quarterTurnsCCW"]
        deg = QUARTER_DEGREES[q]
        direction = "" if q == 2 else " anticlockwise"
        # Angle stated, centre omitted -> incomplete; store the student's text, never an invalid canonical.
        out.append(_diag("MISC.TRANS.RIGHT_ANGLE_MISSING_CENTRE", "parser", None,
                         "missing-rotation-centre", student_text=f"rotation {deg} deg{direction}".strip()))
        if q != 2:
            wrong = rotation_desc(h, k, 4 - q)
            out.append(_diag("MISC.TRANS.RIGHT_CENTRE_WRONG_DIRECTION", "descriptor",
                             {"canonical": wrong, "display": format_display(wrong)}, "wrong-rotation-amount"))
        refl = reflection_vertical(h)
        out.append(_diag("MISC.TRANS.NAMES_REFLECTION_FOR_ROTATION", "descriptor",
                         {"canonical": refl, "display": format_display(refl)}, "wrong-transformation-type"))
    return out
