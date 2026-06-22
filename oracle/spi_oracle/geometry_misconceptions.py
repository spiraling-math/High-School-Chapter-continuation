"""Geometry (angles) misconception registry (oracle reference).

Every misconception is computed ONLY from the displayed givens, has a deterministic
formula, an applicability condition, an item-specific placeholder-free student
feedback string, and is independently recomputed by the validator. The validator
rejects any distractor equal to the answer or to another distractor; the generator
deterministically regenerates parameters until three distinct distractors exist.

`observableError` (serialized as the distractor rationale) and `feedback` (shown to
students) contain no internal symbols. Mirrors domains/geometry/geometry-misconceptions.ts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def _sum(g) -> int:
    return sum(g["givens"])


# wrong(g) -> int or None.  g has: givens (list), apex, theta (per family).
MISCONCEPTIONS: Dict[str, Dict[str, Any]] = {
    # --- F1 straight line --------------------------------------------------- #
    "MISC.GEOM.LINE.USES_360": {
        "wrong": lambda g: 360 - _sum(g),
        "title": "Uses 360 on a straight line",
        "observableError": "Subtracted from 360 instead of 180.",
        "feedback": "Angles on a straight line sum to 180 degrees, not 360. Subtract the given angles from 180.",
        "expression": "360 - sum(givens)",
    },
    "MISC.GEOM.LINE.RETURNS_SUM_GIVENS": {
        "wrong": lambda g: _sum(g),
        "title": "Returns the sum of the givens",
        "observableError": "Gave the sum of the given angles.",
        "feedback": "You added the given angles. Subtract their total from 180 to find the unknown.",
        "expression": "sum(givens)",
    },
    "MISC.GEOM.LINE.FORGOT_ONE_GIVEN": {
        "wrong": lambda g: (180 - (_sum(g) - g["givens"][-1])) if len(g["givens"]) >= 2 else None,
        "title": "Forgot one given angle",
        "observableError": "Left out one of the given angles.",
        "feedback": "Include every given angle. Subtract the total of all of them from 180.",
        "expression": "180 - sum(all but one given)",
    },
    # --- F2 triangle -------------------------------------------------------- #
    "MISC.GEOM.TRI.USES_360": {
        "wrong": lambda g: 360 - _sum(g),
        "title": "Uses 360 for a triangle",
        "observableError": "Used a 360-degree sum for a triangle.",
        "feedback": "The interior angles of a triangle sum to 180 degrees, not 360.",
        "expression": "360 - A - B",
    },
    "MISC.GEOM.TRI.RETURNS_SUM_GIVENS": {
        "wrong": lambda g: _sum(g),
        "title": "Returns the sum of the givens",
        "observableError": "Gave the sum of the two known angles.",
        "feedback": "You added the two known angles. Subtract their total from 180.",
        "expression": "A + B",
    },
    "MISC.GEOM.TRI.SUBTRACTS_ONLY_ONE_GIVEN": {
        "wrong": lambda g: 180 - g["givens"][0],
        "title": "Subtracts only one given",
        "observableError": "Subtracted only one known angle from 180.",
        "feedback": "Subtract both known angles from 180, not just one.",
        "expression": "180 - A",
    },
    # --- F2 isosceles ------------------------------------------------------- #
    "MISC.GEOM.ISO.FORGOT_TO_HALVE": {
        "wrong": lambda g: 180 - g["apex"],
        "title": "Forgot to halve",
        "observableError": "Did not halve after subtracting the apex.",
        "feedback": "After subtracting the apex from 180, share the result equally between the two base angles (divide by 2).",
        "expression": "180 - apex",
    },
    "MISC.GEOM.ISO.HALVES_180_ONLY": {
        "wrong": lambda g: (90 - g["apex"]) if (90 - g["apex"]) > 0 else None,
        "title": "Halved 180 instead of (180 - apex)",
        "observableError": "Used 90 - apex instead of (180 - apex) divided by 2.",
        "feedback": "Subtract the apex from 180 first, then divide by 2.",
        "expression": "90 - apex",
    },
    "MISC.GEOM.ISO.APEX_EQUALS_BASE": {
        "wrong": lambda g: g["apex"],
        "title": "Base equals apex",
        "observableError": "Took the base angle to equal the apex.",
        "feedback": "The base angles are not equal to the apex; use base = (180 - apex) divided by 2.",
        "expression": "apex",
    },
    # --- F3 angles at a point ---------------------------------------------- #
    "MISC.GEOM.POINT.USES_180": {
        "wrong": lambda g: (180 - _sum(g)) if (180 - _sum(g)) > 0 else None,
        "title": "Uses 180 around a point",
        "observableError": "Used a 180-degree sum instead of 360.",
        "feedback": "Angles around a point sum to 360 degrees, not 180.",
        "expression": "180 - sum(givens)",
    },
    "MISC.GEOM.POINT.RETURNS_SUM_GIVENS": {
        "wrong": lambda g: _sum(g),
        "title": "Returns the sum of the givens",
        "observableError": "Gave the sum of the given angles.",
        "feedback": "You added the given angles. Subtract their total from 360.",
        "expression": "sum(givens)",
    },
    "MISC.GEOM.POINT.FORGOT_ONE_GIVEN": {
        "wrong": lambda g: (360 - (_sum(g) - g["givens"][-1])) if len(g["givens"]) >= 2 else None,
        "title": "Forgot one given angle",
        "observableError": "Left out one of the given angles.",
        "feedback": "Include every given angle; subtract their total from 360.",
        "expression": "360 - sum(all but one given)",
    },
    # --- F3 vertically opposite (diagnostic only; never used for MC) -------- #
    "MISC.GEOM.VO.USES_SUPPLEMENTARY": {
        "wrong": lambda g: 180 - g["theta"],
        "title": "Uses the supplementary angle",
        "observableError": "Used the supplementary angle (180 - given) instead of the equal vertically opposite angle.",
        "feedback": "Vertically opposite angles are equal, so the answer equals the given angle (do not use 180 minus the angle).",
        "expression": "180 - theta",
    },
}

_ELIGIBILITY = {
    "straight_line_missing_angle": ["MISC.GEOM.LINE.USES_360", "MISC.GEOM.LINE.RETURNS_SUM_GIVENS", "MISC.GEOM.LINE.FORGOT_ONE_GIVEN"],
    "triangle_missing_angle": ["MISC.GEOM.TRI.USES_360", "MISC.GEOM.TRI.RETURNS_SUM_GIVENS", "MISC.GEOM.TRI.SUBTRACTS_ONLY_ONE_GIVEN"],
    "isosceles_base_angle": ["MISC.GEOM.ISO.FORGOT_TO_HALVE", "MISC.GEOM.ISO.HALVES_180_ONLY", "MISC.GEOM.ISO.APEX_EQUALS_BASE"],
    "vertically_opposite_angle": [],  # free-response only in the current approved scope
    "angles_at_point_missing": ["MISC.GEOM.POINT.USES_180", "MISC.GEOM.POINT.RETURNS_SUM_GIVENS", "MISC.GEOM.POINT.FORGOT_ONE_GIVEN"],
}


def rules_for(task: str) -> List[str]:
    return list(_ELIGIBILITY.get(task, []))
