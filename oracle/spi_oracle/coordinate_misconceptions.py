"""Coordinate-geometry misconception registry (oracle reference).

Each misconception is one clearly-defined conceptual error with a TASK-SPECIFIC
deterministic value adapter (owner decision H: a semantic id may be reused across
tasks when the underlying error is genuinely the same; the task is recorded separately
in analytics). Adapters take a task context of exact `Fraction` values and return the
WRONG value in the task's natural shape:

  * point tasks (read_point, midpoint)      -> (Fraction x, Fraction y)
  * gradient task (gradient_two_points)     -> Fraction
  * equation tasks (interpret/equation_*)   -> (Fraction m, Fraction c)   [a Line]

Return `None` when the misconception does not apply (e.g. a reciprocal of a zero
gradient). The generator skips any distractor that is None, equals the answer, repeats
another distractor, or is out of the reasonable display domain, and regenerates the
parameters until three DISTINCT misconception-backed distractors exist (else the task
falls back to free-response). `observableError` (the distractor rationale) and
`feedback` (the student message) use only legitimate domain vocabulary — gradient,
intercept, x, y, m, c — and contain no internal placeholder symbols.

Mirrors domains/geometry/coordinate-misconceptions.ts byte-for-byte in behaviour.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable, Dict, List, Optional, Tuple

Pt = Tuple[Fraction, Fraction]


def _recip(a: Fraction) -> Optional[Fraction]:
    return None if a == 0 else 1 / a


# Each entry: title, observableError, feedback, and `adapt` mapping task -> adapter.
# An adapter receives the context dict `c` (Fractions) and returns the wrong value.
MISCONCEPTIONS: Dict[str, Dict[str, Any]] = {
    # --- coordinate reading / plotting ------------------------------------- #
    "MISC.COORD.AXIS_SWAP": {
        "title": "Swaps the coordinate order",
        "observableError": "Wrote the coordinates in the wrong order (y before x).",
        "feedback": "Write the x-coordinate first, then the y-coordinate: (x, y).",
        "adapt": {
            "read_point": lambda c: (c["y"], c["x"]),
            "midpoint": lambda c: (c["my"], c["mx"]),
        },
    },
    "MISC.COORD.COORD_SIGN_FLIP": {
        "title": "Sign error on a coordinate",
        "observableError": "Reversed the sign of a coordinate.",
        "feedback": "Check the sign of each coordinate against its axis direction; left and down are negative.",
        "adapt": {},  # objective-level metadata; not used as an MC distractor in v1.0.0
    },
    "MISC.COORD.POINT_REFLECT_X": {
        "title": "Reflects across the x-axis",
        "observableError": "Read the y-coordinate with the wrong sign (reflected across the x-axis).",
        "feedback": "Read the y-coordinate by its height above or below the x-axis; below the axis is negative.",
        "adapt": {"read_point": lambda c: (c["x"], -c["y"])},
    },
    "MISC.COORD.POINT_REFLECT_Y": {
        "title": "Reflects across the y-axis",
        "observableError": "Read the x-coordinate with the wrong sign (reflected across the y-axis).",
        "feedback": "Read the x-coordinate by its distance left or right of the y-axis; left of the axis is negative.",
        "adapt": {"read_point": lambda c: (-c["x"], c["y"])},
    },
    # --- gradient ---------------------------------------------------------- #
    "MISC.COORD.GRADIENT_INVERTED": {
        "title": "Inverts the gradient (run over rise)",
        "observableError": "Divided the change in x by the change in y instead of the other way round.",
        "feedback": "Gradient is rise over run: divide the change in y by the change in x.",
        "adapt": {
            "gradient_two_points": lambda c: (None if c["y2"] == c["y1"] else (c["x2"] - c["x1"]) / (c["y2"] - c["y1"])),
            "equation_from_graph": lambda c: (None if c["y2"] == c["y1"] else ((c["x2"] - c["x1"]) / (c["y2"] - c["y1"]), c["c"])),
            "equation_from_two_points": lambda c: (None if c["y2"] == c["y1"] else ((c["x2"] - c["x1"]) / (c["y2"] - c["y1"]), c["c"])),
        },
    },
    "MISC.COORD.GRADIENT_SIGN": {
        "title": "Sign error in the gradient",
        "observableError": "Subtracted the coordinates in inconsistent orders, flipping the sign of the gradient.",
        "feedback": "Subtract the x-coordinates and the y-coordinates in the SAME order; keep the signs consistent.",
        "adapt": {
            "gradient_two_points": lambda c: -c["m"],
            "equation_from_two_points": lambda c: (-c["m"], c["c"]),
        },
    },
    "MISC.COORD.GRADIENT_SUM_BOTH": {
        "title": "Adds instead of subtracting",
        "observableError": "Added the coordinates instead of subtracting them.",
        "feedback": "Gradient uses the DIFFERENCES: (y2 - y1) divided by (x2 - x1), not the sums.",
        "adapt": {
            "gradient_two_points": lambda c: (None if (c["x2"] + c["x1"]) == 0 else (c["y2"] + c["y1"]) / (c["x2"] + c["x1"])),
        },
    },
    # --- midpoint ---------------------------------------------------------- #
    "MISC.COORD.MIDPOINT_DIFFERENCE": {
        "title": "Uses the difference, not the average",
        "observableError": "Halved the difference of the coordinates instead of their average.",
        "feedback": "Midpoint averages the coordinates: add them and divide by 2, do not subtract.",
        "adapt": {"midpoint": lambda c: ((c["x2"] - c["x1"]) / 2, (c["y2"] - c["y1"]) / 2)},
    },
    "MISC.COORD.MIDPOINT_SUM_NO_HALF": {
        "title": "Adds without halving",
        "observableError": "Added the coordinates but did not divide by 2.",
        "feedback": "After adding each pair of coordinates, divide by 2 to find the midpoint.",
        "adapt": {"midpoint": lambda c: (c["x1"] + c["x2"], c["y1"] + c["y2"])},
    },
    # --- y = mx + c -------------------------------------------------------- #
    "MISC.COORD.MC_SWAPPED": {
        "title": "Swaps gradient and intercept",
        "observableError": "Read the gradient as the intercept and the intercept as the gradient.",
        "feedback": "In y = mx + c the gradient m multiplies x; the intercept c is the constant term.",
        "adapt": {
            "interpret_mx_c": lambda c: (c["c"], c["m"]),
            "equation_from_graph": lambda c: (c["c"], c["m"]),
            "equation_from_two_points": lambda c: (c["c"], c["m"]),
        },
    },
    "MISC.COORD.INTERCEPT_SIGN": {
        "title": "Sign error on the intercept",
        "observableError": "Gave the y-intercept with the wrong sign.",
        "feedback": "Read the y-intercept where the line crosses the y-axis, keeping its sign (below the origin is negative).",
        "adapt": {
            "interpret_mx_c": lambda c: (c["m"], -c["c"]),
            "equation_from_graph": lambda c: (c["m"], -c["c"]),
            "equation_from_two_points": lambda c: (c["m"], -c["c"]),
        },
    },
    "MISC.COORD.READS_X_INTERCEPT": {
        "title": "Reads the x-intercept as c",
        "observableError": "Used the x-intercept instead of the y-intercept.",
        "feedback": "The y-intercept c is where the line meets the y-axis (x = 0), not where it meets the x-axis.",
        "adapt": {
            "interpret_mx_c": lambda c: (None if c["m"] == 0 else (c["m"], -c["c"] / c["m"])),
            "equation_from_graph": lambda c: (None if c["m"] == 0 else (c["m"], -c["c"] / c["m"])),
        },
    },
}

_ELIGIBILITY: Dict[str, List[str]] = {
    "read_point": ["MISC.COORD.AXIS_SWAP", "MISC.COORD.POINT_REFLECT_X", "MISC.COORD.POINT_REFLECT_Y"],
    "plot_point": [],  # free-response only (owner decision B.2)
    "gradient_two_points": ["MISC.COORD.GRADIENT_INVERTED", "MISC.COORD.GRADIENT_SIGN", "MISC.COORD.GRADIENT_SUM_BOTH"],
    "midpoint": ["MISC.COORD.MIDPOINT_DIFFERENCE", "MISC.COORD.MIDPOINT_SUM_NO_HALF", "MISC.COORD.AXIS_SWAP"],
    "interpret_mx_c": ["MISC.COORD.MC_SWAPPED", "MISC.COORD.INTERCEPT_SIGN", "MISC.COORD.READS_X_INTERCEPT"],
    "equation_from_graph": ["MISC.COORD.GRADIENT_INVERTED", "MISC.COORD.INTERCEPT_SIGN", "MISC.COORD.READS_X_INTERCEPT"],
    "equation_from_two_points": ["MISC.COORD.GRADIENT_INVERTED", "MISC.COORD.GRADIENT_SIGN", "MISC.COORD.INTERCEPT_SIGN"],
}


def rules_for(task: str) -> List[str]:
    return list(_ELIGIBILITY.get(task, []))


def adapter_for(mid: str, task: str) -> Optional[Callable[[Dict[str, Fraction]], Any]]:
    return MISCONCEPTIONS[mid]["adapt"].get(task)
