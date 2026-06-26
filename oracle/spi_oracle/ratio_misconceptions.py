"""gen.proportion.ratio — MISC.RATIO.* registry (16) and per-item diagnostics (owner 10).

Single source of truth for ratio misconception IDs. Objective commonMisconceptions, the TypeScript mirror,
review-pack tokens, and tests all draw from here. Each diagnostic declares applicability, a predicted
student response computed by an EXACT formula (never an arbitrary nearby wrong number), the observable
error, targeted feedback, the expected checker result code, and is independently recomputable. A
diagnostic that is inapplicable to an item, or whose predicted response collides with the correct answer,
is OMITTED (never counted as exercised coverage).

domains/proportion/ratio-misconceptions.ts mirrors this byte-for-byte.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from . import ratio_core as RC

DOMAIN = "proportion"


def _m(mid: str, title: str, obs: str, feedback: str, hint: str, objs: List[str]) -> Dict[str, Any]:
    return {
        "misconceptionId": mid, "domain": DOMAIN, "title": title,
        "description": obs, "observableError": obs, "feedback": feedback, "remediationHint": hint,
        "objectiveRelationships": list(objs), "reviewStatus": "proposed", "version": "1.0.0",
    }


_SIMP = ["SPI.MIDDLE.RATIO.SIMPLIFY.01"]
_WRITE = ["SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01"]
_R2F = ["SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01"]
_F2R = ["SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01"]
_SHARE = ["SPI.MIDDLE.RATIO.SHARE_TWO_PART.01", "SPI.MIDDLE.RATIO.SHARE_THREE_PART.01"]
_MISS = ["SPI.MIDDLE.RATIO.MISSING_PART.01"]
_DIR = ["SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01"]
_INV = ["SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01"]
_RATE = ["SPI.MIDDLE.RATIO.UNIT_RATE.01"]
_BUY = ["SPI.MIDDLE.RATIO.BEST_BUY.01"]
_SCALE = ["SPI.MIDDLE.RATIO.SIMPLE_SCALE.01"]

MISCONCEPTIONS: List[Dict[str, Any]] = [
    _m("MISC.RATIO.NOT_SIMPLIFIED", "Does not simplify fully",
       "Divides the parts by a common factor but not by the full greatest common divisor.",
       "Divide every part by their GREATEST common divisor so no common factor remains.",
       "Find the gcd of all parts before dividing.", _SIMP + _WRITE),
    _m("MISC.RATIO.EQUIVALENT_NOT_SIMPLIFIED", "Leaves the ratio unsimplified",
       "Gives an equivalent ratio that is not in simplest form when simplest form is required.",
       "An equivalent ratio is correct in value but the task asks for simplest form.",
       "Keep dividing until the parts share no common factor.", _SIMP),
    _m("MISC.RATIO.REVERSED_ORDER", "Reverses the order of the ratio",
       "Writes the parts in the wrong order (e.g. b:a instead of a:b).",
       "Order matters in a ratio: 2:3 is not the same as 3:2. Match each part to the named quantity.",
       "Write the parts in the order the quantities are named.", _WRITE + _F2R),
    _m("MISC.RATIO.ADDS_PARTS_WRONG", "Combines the ratio parts incorrectly",
       "Adds or combines the ratio parts incorrectly when forming or simplifying the ratio.",
       "Keep the parts separate; only divide each by the common factor.",
       "Do not add the parts together when simplifying.", _SIMP + _SHARE),
    _m("MISC.RATIO.PART_AS_WHOLE", "Treats one part as the whole",
       "Uses a single part as the total instead of the sum of all parts.",
       "The whole is the SUM of all the parts, not one part.",
       "Add all the parts to find the total before sharing.", _R2F + _SHARE),
    _m("MISC.RATIO.WRONG_TOTAL_PARTS", "Uses the wrong total number of parts",
       "Counts the wrong number of total parts when sharing.",
       "Add every part of the ratio to get the total number of parts.",
       "Total parts = sum of all the ratio parts.", _SHARE),
    _m("MISC.RATIO.DIVIDES_BY_ONE_PART", "Divides by one part instead of the total",
       "Divides the whole by a single ratio part instead of by the total number of parts.",
       "Divide the whole by the TOTAL number of parts to find the value of one part.",
       "One part = whole / (sum of parts).", _SHARE + _MISS),
    _m("MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY", "Multiplies when it should divide",
       "Multiplies to find one unit instead of dividing.",
       "To find one unit, DIVIDE the total by the quantity.",
       "One unit = total / quantity.", _MISS + _DIR),
    _m("MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY", "Divides when it should multiply",
       "Divides by the required quantity instead of multiplying after finding one unit.",
       "After finding one unit, MULTIPLY by the required quantity.",
       "Result = one unit x required quantity.", _DIR + _RATE),
    _m("MISC.RATIO.DIRECT_FOR_INVERSE", "Uses direct proportion for an inverse problem",
       "Scales directly when the quantities are inversely proportional.",
       "When one quantity goes up the other goes DOWN: use the product invariant, not direct scaling.",
       "Use q1 x v1 = q2 x v2 for inverse proportion.", _INV),
    _m("MISC.RATIO.INVERSE_FOR_DIRECT", "Uses inverse proportion for a direct problem",
       "Applies the inverse rule when the quantities are directly proportional.",
       "When both quantities grow together, use the unitary (direct) method, not the inverse rule.",
       "Find one unit, then multiply.", _DIR),
    _m("MISC.RATIO.NO_UNIT_RATE_COMPARE", "Compares without a unit rate",
       "Compares the options by raw total instead of normalising to a unit rate.",
       "Compare value for money by the rate PER ONE UNIT, not by the total.",
       "Find each option's unit rate before comparing.", _BUY),
    _m("MISC.RATIO.LOWEST_PRICE_NOT_BEST", "Chooses the cheapest, not the best value",
       "Picks the lowest total price instead of the lowest unit rate.",
       "The best value has the lowest cost PER UNIT, which is not always the cheapest pack.",
       "Compare unit rates, then choose the smallest.", _BUY),
    _m("MISC.RATIO.SCALE_WRONG_DIRECTION", "Scales in the wrong direction",
       "Multiplies when it should divide (or vice versa) when applying the scale.",
       "Check whether the value should grow or shrink, then scale the right way.",
       "Decide the direction of the scale before multiplying or dividing.", _SCALE),
    _m("MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE", "Adds instead of scaling",
       "Adds a constant difference instead of multiplying by the scale factor.",
       "Proportion is MULTIPLICATIVE: multiply by the scale factor, do not add a difference.",
       "Use multiplication by the scale factor, not addition.", _DIR + _SCALE),
    _m("MISC.RATIO.FRACTION_PART_OVER_PART", "Writes part over the other part",
       "Writes one part over the other part instead of the part over the whole.",
       "A fraction of the whole is the part over the TOTAL (sum of parts), not part over part.",
       "Fraction of the whole = part / (sum of parts).", _R2F),
]

ALL_IDS: Tuple[str, ...] = tuple(m["misconceptionId"] for m in MISCONCEPTIONS)


def registry() -> List[Dict[str, Any]]:
    return [dict(m) for m in MISCONCEPTIONS]
