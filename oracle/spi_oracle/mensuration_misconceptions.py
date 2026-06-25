"""MISC.MENS.* — mensuration misconception & diagnostic registry (owner K).

All eight mensuration tasks are FREE-RESPONSE in v1.0.0, so these are not four-option distractors:
they are deterministic FREE-RESPONSE DIAGNOSTICS. Each rule predicts the exact wrong response a
student holding the misconception would give, which drives (a) targeted feedback when a real student
response matches, and (b) the review pack's misconception-calculation column. Every rule defines:
applicability, the exact predicted wrong response, the observable error, targeted feedback, an
independent recomputation, and collision/inapplicability behaviour (a rule is suppressed for an item
when its predicted response is not actually distinct from the correct answer).

Three groups (owner K):
  1. Mathematical diagnostics — a wrong VALUE with the correct dimensional unit.
  2. Unit diagnostics — the right NUMBER with the wrong unit (drives the structural checker codes).
  3. Non-numeric pedagogical — USES_SLOPING_SIDE: diagnostic-only, never a manufactured irrational
     distractor.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable, Dict, List, Optional

import mensuration_units as U
from mensuration_units import Quantity

GROUP_MATH = "mathematical"
GROUP_UNIT = "unit"
GROUP_PEDAGOGICAL = "pedagogical"


def _val_quantity(answer: Quantity, value) -> Quantity:
    """A same-dimension, same-unit quantity carrying a different (wrong) value."""
    return Quantity(answer.dimension, answer.baseUnit, answer.exponent, Fraction(value))


def _other_base(base: str) -> str:
    return {"mm": "cm", "cm": "m", "m": "cm"}[base]


# --------------------------------------------------------------------------- #
# Adapters: (task, params, answer) -> Optional[(predicted_response_str, expected_result_code)]
# A None return means the rule does not apply to this item (inapplicability / collision).
# --------------------------------------------------------------------------- #
def _value_response(answer: Quantity, wrong_value) -> Optional[str]:
    if Fraction(wrong_value) == answer.value or Fraction(wrong_value) <= 0:
        return None  # not a distinct, sensible wrong answer -> suppress
    return U.format_quantity(_val_quantity(answer, wrong_value))


def _adapt_adds_two_sides(task, p, ans) -> Optional[str]:
    if task != "perimeter_rectangle":
        return None
    return _value_response(ans, p["width"] + p["height"])


def _adapt_area_for_perimeter(task, p, ans) -> Optional[str]:
    if task == "perimeter_rectangle":
        return _value_response(ans, p["width"] * p["height"])
    if task == "perimeter_composite":
        return _value_response(ans, p["W"] * p["H"] - p["a"] * p["b"])
    return None


def _adapt_perimeter_for_area(task, p, ans) -> Optional[str]:
    if task == "area_rectangle":
        return _value_response(ans, 2 * (p["width"] + p["height"]))
    if task == "area_composite":
        return _value_response(ans, 2 * (p["W"] + p["H"]))
    return None


def _adapt_adds_dims_for_area(task, p, ans) -> Optional[str]:
    if task == "area_rectangle":
        return _value_response(ans, p["width"] + p["height"])
    if task == "area_composite":
        return _value_response(ans, p["W"] + p["H"])
    return None


def _adapt_forgets_to_halve(task, p, ans) -> Optional[str]:
    if task == "area_triangle":
        return _value_response(ans, p["base"] * p["height"])  # base*height, not /2
    if task == "missing_triangle_base_height":
        known = p["base"] if p["hidden"] == "height" else p["height"]
        return _value_response(ans, Fraction(p["area2"], 2 * known))  # divides area (not 2*area)
    return None


def _adapt_omits_indented_edge(task, p, ans) -> Optional[str]:
    if task != "perimeter_composite":
        return None
    return _value_response(ans, 2 * (p["W"] + p["H"]) - p["a"])  # drops one indent edge (length a)


def _adapt_counts_internal_edge(task, p, ans) -> Optional[str]:
    if task != "perimeter_composite":
        return None
    return _value_response(ans, 2 * (p["W"] + p["H"]) + (p["W"] - p["a"]))  # adds an internal cut edge


def _adapt_subtracts_wrong_rectangle(task, p, ans) -> Optional[str]:
    if task != "area_composite":
        return None
    return _value_response(ans, p["W"] * p["H"] - (p["W"] - p["a"]) * p["b"])  # subtracts the wrong sub-rectangle


def _adapt_right_number_no_unit(task, p, ans) -> Optional[str]:
    return U.format_value(ans.value)  # the bare number, no unit


def _adapt_linear_units_for_area(task, p, ans) -> Optional[str]:
    if ans.dimension != "area":
        return None
    return U.format_quantity(U.make_length(ans.value, ans.baseUnit))  # right number, linear unit


def _adapt_square_units_for_perimeter(task, p, ans) -> Optional[str]:
    if ans.dimension != "length":
        return None
    return U.format_quantity(U.make_area(ans.value, ans.baseUnit))  # right number, square unit


def _adapt_wrong_base_unit(task, p, ans) -> Optional[str]:
    other = _other_base(ans.baseUnit)
    return U.format_quantity(Quantity(ans.dimension, other, ans.exponent, ans.value))


def _adapt_sloping_side(task, p, ans) -> Optional[str]:
    return None  # diagnostic-only — never a manufactured (irrational) numeric distractor


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
MISCONCEPTIONS: List[Dict[str, Any]] = [
    # --- Group 1: mathematical diagnostics (wrong value, correct unit) ---
    {"id": "MISC.MENS.ADDS_TWO_SIDES_RECT", "group": GROUP_MATH,
     "title": "Adds only two sides of a rectangle",
     "observableError": "Adds one length and one width instead of all four sides.",
     "feedback": "A rectangle has four sides. Add all four (or use 2 × (length + width)).",
     "expectedCode": "incorrect-value", "adapter": _adapt_adds_two_sides},
    {"id": "MISC.MENS.USES_AREA_FOR_PERIMETER", "group": GROUP_MATH,
     "title": "Uses area when perimeter is required",
     "observableError": "Multiplies the sides (area) when the question asks for the distance around.",
     "feedback": "Perimeter is the distance around the outside — add the side lengths, do not multiply.",
     "expectedCode": "incorrect-value", "adapter": _adapt_area_for_perimeter},
    {"id": "MISC.MENS.USES_PERIMETER_FOR_AREA", "group": GROUP_MATH,
     "title": "Uses perimeter when area is required",
     "observableError": "Adds the sides (perimeter) when the question asks for the space inside.",
     "feedback": "Area is the space inside — multiply, do not add the sides.",
     "expectedCode": "incorrect-value", "adapter": _adapt_perimeter_for_area},
    {"id": "MISC.MENS.ADDS_DIMS_FOR_AREA", "group": GROUP_MATH,
     "title": "Adds dimensions instead of multiplying for area",
     "observableError": "Adds length and width instead of multiplying them.",
     "feedback": "Area of a rectangle is length × width, not length + width.",
     "expectedCode": "incorrect-value", "adapter": _adapt_adds_dims_for_area},
    {"id": "MISC.MENS.FORGETS_TO_HALVE", "group": GROUP_MATH,
     "title": "Forgets to halve base × height for a triangle",
     "observableError": "Computes base × height without halving.",
     "feedback": "A triangle is half of the surrounding rectangle — remember the ½ (÷ 2).",
     "expectedCode": "incorrect-value", "adapter": _adapt_forgets_to_halve},
    {"id": "MISC.MENS.OMITS_INDENTED_EDGE", "group": GROUP_MATH,
     "title": "Omits an indented edge from a composite perimeter",
     "observableError": "Misses one of the step edges when tracing the outside.",
     "feedback": "Trace the whole outside boundary — include every step edge of the indent.",
     "expectedCode": "incorrect-value", "adapter": _adapt_omits_indented_edge},
    {"id": "MISC.MENS.COUNTS_INTERNAL_EDGE", "group": GROUP_MATH,
     "title": "Counts an internal decomposition edge in a perimeter",
     "observableError": "Includes a cutting line used to split the shape as if it were an outer edge.",
     "feedback": "Only the outside edges count for perimeter — a line you draw to split the shape is not part of it.",
     "expectedCode": "incorrect-value", "adapter": _adapt_counts_internal_edge},
    {"id": "MISC.MENS.SUBTRACTS_WRONG_RECTANGLE", "group": GROUP_MATH,
     "title": "Subtracts the wrong rectangle in a composite area",
     "observableError": "Subtracts a rectangle that is not the missing corner.",
     "feedback": "Subtract exactly the missing corner rectangle (its width × its height).",
     "expectedCode": "incorrect-value", "adapter": _adapt_subtracts_wrong_rectangle},
    # --- Group 2: unit diagnostics (right number, wrong unit) ---
    {"id": "MISC.MENS.RIGHT_NUMBER_NO_UNIT", "group": GROUP_UNIT,
     "title": "Right number, no unit",
     "observableError": "Gives the correct number but omits the unit.",
     "feedback": "Always state the unit. A measurement is not complete without it.",
     "expectedCode": "missing-unit", "adapter": _adapt_right_number_no_unit},
    {"id": "MISC.MENS.LINEAR_UNITS_FOR_AREA", "group": GROUP_UNIT,
     "title": "Linear units given for an area",
     "observableError": "Labels an area with a length unit (e.g. cm instead of cm^2).",
     "feedback": "Area is measured in SQUARE units — write cm^2, not cm.",
     "expectedCode": "wrong-exponent", "adapter": _adapt_linear_units_for_area},
    {"id": "MISC.MENS.SQUARE_UNITS_FOR_PERIMETER", "group": GROUP_UNIT,
     "title": "Square units given for a perimeter / length",
     "observableError": "Labels a length with a square unit (e.g. cm^2 instead of cm).",
     "feedback": "A perimeter or length is measured in LINEAR units — write cm, not cm^2.",
     "expectedCode": "wrong-exponent", "adapter": _adapt_square_units_for_perimeter},
    {"id": "MISC.MENS.WRONG_BASE_UNIT", "group": GROUP_UNIT,
     "title": "Right number, wrong base unit",
     "observableError": "Gives the correct number with a different base unit from the figure.",
     "feedback": "Use the unit shown on the figure. Do not change between mm, cm and m here.",
     "expectedCode": "wrong-base-unit", "adapter": _adapt_wrong_base_unit},
    # --- Group 3: non-numeric pedagogical ---
    {"id": "MISC.MENS.USES_SLOPING_SIDE", "group": GROUP_PEDAGOGICAL,
     "title": "Uses a sloping side instead of the perpendicular height",
     "observableError": "Reads a slanted side of the triangle as the height.",
     "feedback": "Use the perpendicular height (the line marked with a right angle), not a sloping side.",
     "expectedCode": None, "adapter": _adapt_sloping_side},
]

_BY_ID = {m["id"]: m for m in MISCONCEPTIONS}

# Eligibility per task (which diagnostics the review pack must exercise) — owner K.
TASK_DIAGNOSTICS: Dict[str, List[str]] = {
    "perimeter_rectangle": ["MISC.MENS.ADDS_TWO_SIDES_RECT", "MISC.MENS.USES_AREA_FOR_PERIMETER",
                            "MISC.MENS.SQUARE_UNITS_FOR_PERIMETER", "MISC.MENS.WRONG_BASE_UNIT", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
    "perimeter_composite": ["MISC.MENS.OMITS_INDENTED_EDGE", "MISC.MENS.COUNTS_INTERNAL_EDGE",
                            "MISC.MENS.USES_AREA_FOR_PERIMETER", "MISC.MENS.SQUARE_UNITS_FOR_PERIMETER", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
    "area_rectangle": ["MISC.MENS.ADDS_DIMS_FOR_AREA", "MISC.MENS.USES_PERIMETER_FOR_AREA",
                       "MISC.MENS.LINEAR_UNITS_FOR_AREA", "MISC.MENS.WRONG_BASE_UNIT", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
    "area_triangle": ["MISC.MENS.FORGETS_TO_HALVE", "MISC.MENS.USES_SLOPING_SIDE",
                      "MISC.MENS.LINEAR_UNITS_FOR_AREA", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
    "area_composite": ["MISC.MENS.SUBTRACTS_WRONG_RECTANGLE", "MISC.MENS.ADDS_DIMS_FOR_AREA",
                       "MISC.MENS.USES_PERIMETER_FOR_AREA", "MISC.MENS.LINEAR_UNITS_FOR_AREA", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
    # Owner C4: only list rules that have a GENUINE deterministic pathway for the task (no inapplicable
    # value rules with a null prediction). USES_AREA_FOR_PERIMETER / USES_PERIMETER_FOR_AREA do not map
    # cleanly to the inverse tasks and are dropped from them; the unit diagnostics + the pedagogical
    # note remain.
    "missing_length_perimeter": ["MISC.MENS.SQUARE_UNITS_FOR_PERIMETER",
                                 "MISC.MENS.WRONG_BASE_UNIT", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
    "missing_dimension_area": ["MISC.MENS.SQUARE_UNITS_FOR_PERIMETER",
                               "MISC.MENS.WRONG_BASE_UNIT", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
    "missing_triangle_base_height": ["MISC.MENS.FORGETS_TO_HALVE", "MISC.MENS.USES_SLOPING_SIDE",
                                     "MISC.MENS.SQUARE_UNITS_FOR_PERIMETER", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
}

# Group -> diagnostic kind (owner C4 reporting buckets).
_GROUP_KIND = {GROUP_MATH: "numeric", GROUP_UNIT: "unit", GROUP_PEDAGOGICAL: "pedagogical"}


def diagnostics_for(task: str, params: Dict[str, Any], answer: Quantity) -> List[Dict[str, Any]]:
    """Every APPLICABLE diagnostic for this item (owner C4). A numeric/unit diagnostic always carries
    a non-null predicted response + the structural result code that response triggers (recomputed
    independently). A pedagogical diagnostic is diagnosticOnly (no numeric-response claim). A
    value/unit rule whose adapter returns null is INAPPLICABLE and is omitted entirely — never emitted
    as a null prediction with a numeric code."""
    out: List[Dict[str, Any]] = []
    for mid in TASK_DIAGNOSTICS.get(task, []):
        rule = _BY_ID[mid]
        kind = _GROUP_KIND[rule["group"]]
        base = {"id": mid, "title": rule["title"], "group": rule["group"], "kind": kind,
                "observableError": rule["observableError"], "feedback": rule["feedback"], "appliesTo": task}
        if rule["group"] == GROUP_PEDAGOGICAL:
            out.append({**base, "diagnosticOnly": True, "predictedResponse": None, "resultCode": None,
                        "distinctFromAnswer": True})
            continue
        predicted = rule["adapter"](task, params, answer)
        if predicted is None:
            continue  # inapplicable for this item — do NOT emit a null-with-code record
        res = U.check_response(predicted, answer)
        out.append({**base, "diagnosticOnly": False, "predictedResponse": predicted,
                    "resultCode": res["code"], "distinctFromAnswer": not res["correct"]})
    return out


def diagnose(task: str, params: Dict[str, Any], answer: Quantity, response: str) -> Optional[Dict[str, Any]]:
    """Best-matching misconception for an actual free-response string (targeted FR feedback). First
    tries an exact value/unit match against a predicted wrong response; otherwise falls back to the
    structural result code (e.g. any missing-unit -> RIGHT_NUMBER_NO_UNIT)."""
    res = U.check_response(response, answer)
    if res["correct"]:
        return None
    norm = response.strip()
    for entry in diagnostics_for(task, params, answer):
        pred = entry["predictedResponse"]
        if pred is not None and U.check_response(norm, answer)["code"] == res["code"]:
            # match by structural code AND (for value rules) equal parsed value
            if entry["group"] == "unit":
                if entry["resultCode"] == res["code"]:
                    return {"id": entry["id"], "feedback": entry["feedback"], "resultCode": res["code"]}
            else:
                pr = U.parse_quantity(pred)[0]; sr = U.parse_quantity(norm)[0]
                if pr is not None and sr is not None and pr.value == sr.value and pr.exponent == sr.exponent:
                    return {"id": entry["id"], "feedback": entry["feedback"], "resultCode": res["code"]}
    # structural fallback for unit errors
    fallback = {"missing-unit": "MISC.MENS.RIGHT_NUMBER_NO_UNIT",
                "wrong-base-unit": "MISC.MENS.WRONG_BASE_UNIT"}.get(res["code"])
    if fallback and fallback in _BY_ID:
        return {"id": fallback, "feedback": _BY_ID[fallback]["feedback"], "resultCode": res["code"]}
    return {"id": None, "feedback": res["feedback"], "resultCode": res["code"]}
