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
        "objectiveRelationships": list(objs), "reviewStatus": "approved", "version": "1.0.0",
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
       "Find the gcd of all parts before dividing.", _SIMP + _WRITE + _F2R),
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
       "Use multiplication by the scale factor, not addition.", _DIR + _SCALE + _INV),
    _m("MISC.RATIO.FRACTION_PART_OVER_PART", "Writes part over the other part",
       "Writes one part over the other part instead of the part over the whole.",
       "A fraction of the whole is the part over the TOTAL (sum of parts), not part over part.",
       "Fraction of the whole = part / (sum of parts).", _R2F),
]

ALL_IDS: Tuple[str, ...] = tuple(m["misconceptionId"] for m in MISCONCEPTIONS)
_BY_ID: Dict[str, Dict[str, Any]] = {m["misconceptionId"]: m for m in MISCONCEPTIONS}


def registry() -> List[Dict[str, Any]]:
    return [dict(m) for m in MISCONCEPTIONS]


# --------------------------------------------------------------------------- #
# Per-item diagnostics (owner 10). diagnostics_for(task, params) returns the
# applicable MISC.RATIO diagnostics for one concrete item, each carrying a
# PREDICTED wrong student response computed by an EXACT formula (never an
# arbitrary nearby wrong number) and the expectedResultCode the checker would
# return for that wrong response:
#   * ratio-answer tasks  -> RC.check_ratio(correctParts, predictedDisplay)["code"]
#   * numeric tasks       -> "incorrect"
#   * best_buy            -> "wrong-choice"
# A diagnostic whose predicted response is None, collides with the correct
# answer, or is inapplicable to the item is OMITTED — it is never counted as
# exercised coverage. Every emitted diagnostic is independently recomputable
# from {task, params} alone.
# --------------------------------------------------------------------------- #
def _ratio_diag(mid: str, correct_parts: List[int], predicted_parts: Optional[List[int]],
                require_simplest: bool) -> Optional[Dict[str, Any]]:
    """A ratio-answer diagnostic. predicted_parts is the (unsimplified, ordered) tuple the
    misconception would produce. Omitted when None, non-positive, or display-equal to the
    correct simplest-form answer."""
    if predicted_parts is None or any(p <= 0 for p in predicted_parts):
        return None
    correct_simplest = RC.simplify_parts(correct_parts)
    if RC.format_ratio(predicted_parts) == RC.format_ratio(correct_simplest):
        return None  # predicted response coincides with the correct answer -> omit
    code = RC.check_ratio(correct_simplest, RC.format_ratio(predicted_parts),
                          require_simplest=require_simplest)["code"]
    if code == "correct":
        return None
    return {"misconceptionId": mid, "domain": DOMAIN, "task": None,
            "predictedResponse": RC.format_ratio(predicted_parts),
            "predictedCanonical": {"parts": list(predicted_parts)},
            "requireSimplest": require_simplest,
            "observableError": _BY_ID[mid]["observableError"],
            "feedback": _BY_ID[mid]["feedback"],
            "expectedResultCode": code}


def _num_diag(mid: str, correct, predicted) -> Optional[Dict[str, Any]]:
    """A numeric (integer / exact-rational) diagnostic. Omitted when None or equal to the
    correct value. expectedResultCode is always 'incorrect'."""
    if predicted is None:
        return None
    cf = Fraction(correct)
    pf = Fraction(predicted)
    if pf == cf:
        return None
    disp = str(pf.numerator) if pf.denominator == 1 else f"{pf.numerator}/{pf.denominator}"
    return {"misconceptionId": mid, "domain": DOMAIN, "task": None,
            "predictedResponse": disp,
            "predictedCanonical": {"num": pf.numerator, "den": pf.denominator},
            "observableError": _BY_ID[mid]["observableError"],
            "feedback": _BY_ID[mid]["feedback"],
            "expectedResultCode": "incorrect"}


def _choice_diag(mid: str, correct_label: str, predicted_label: Optional[str]) -> Optional[Dict[str, Any]]:
    """A best-buy choice diagnostic. Omitted when None or equal to the correct option."""
    if predicted_label is None or predicted_label == correct_label:
        return None
    return {"misconceptionId": mid, "domain": DOMAIN, "task": None,
            "predictedResponse": predicted_label,
            "predictedCanonical": predicted_label,
            "observableError": _BY_ID[mid]["observableError"],
            "feedback": _BY_ID[mid]["feedback"],
            "expectedResultCode": "wrong-choice"}


def diagnostics_for(task: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Optional[Dict[str, Any]]] = []

    if task == "simplify":
        parts = params["parts"]                      # the unsimplified given parts
        g = RC.gcd_list(parts)
        # NOT_SIMPLIFIED: divide by a PROPER factor of the gcd (not the full gcd).
        partial_div = None
        for d in range(2, g):
            if g % d == 0:
                partial_div = d
                break
        if partial_div is not None:
            out.append(_ratio_diag("MISC.RATIO.NOT_SIMPLIFIED", parts,
                                   [p // partial_div for p in parts], require_simplest=True))
        # EQUIVALENT_NOT_SIMPLIFIED: leaves the ratio exactly as given (unsimplified).
        if g > 1:
            out.append(_ratio_diag("MISC.RATIO.EQUIVALENT_NOT_SIMPLIFIED", parts,
                                   list(parts), require_simplest=True))
        # ADDS_PARTS_WRONG: collapses two parts into their sum (drops a part / wrong combine).
        if len(parts) >= 2:
            simp = RC.simplify_parts(parts)
            out.append(_ratio_diag("MISC.RATIO.ADDS_PARTS_WRONG", parts,
                                   [simp[0] + simp[1]] + simp[2:], require_simplest=True))

    elif task == "write_from_quantities":
        q = params["quantities"]
        simp = RC.simplify_parts(q)
        # REVERSED_ORDER: writes the parts in reversed order.
        out.append(_ratio_diag("MISC.RATIO.REVERSED_ORDER", simp, list(reversed(simp)),
                               require_simplest=False))
        # NOT_SIMPLIFIED: gives the raw quantities without simplifying.
        if RC.gcd_list(q) > 1:
            out.append(_ratio_diag("MISC.RATIO.NOT_SIMPLIFIED", simp, list(q),
                                   require_simplest=True))

    elif task == "ratio_to_fraction":
        a, b = params["parts"][0], params["parts"][1]
        idx = params["partIndex"]
        part = params["parts"][idx]
        other = params["parts"][1 - idx]
        correct = Fraction(part, a + b)
        # FRACTION_PART_OVER_PART: writes the part over the OTHER part, not the whole.
        if other != 0:
            out.append(_num_diag("MISC.RATIO.FRACTION_PART_OVER_PART", correct, Fraction(part, other)))
        # REVERSED_ORDER: gives the OTHER part's fraction of the whole (reads the wrong part).
        out.append(_num_diag("MISC.RATIO.REVERSED_ORDER", correct, Fraction(other, a + b)))
        # PART_AS_WHOLE: uses the part itself as the whole (gives 1) — surfaced as 1/1.
        out.append(_num_diag("MISC.RATIO.PART_AS_WHOLE", correct, Fraction(1, 1)))

    elif task == "fraction_to_ratio":
        num, den = params["num"], params["den"]
        rest = den - num
        correct = RC.simplify_parts([num, rest])
        # REVERSED_ORDER: writes rest:part instead of part:rest.
        out.append(_ratio_diag("MISC.RATIO.REVERSED_ORDER", correct,
                               list(reversed(RC.simplify_parts([num, rest]))), require_simplest=False))
        # PART_AS_WHOLE: writes part:whole (num:den) instead of part:rest.
        out.append(_ratio_diag("MISC.RATIO.PART_AS_WHOLE", correct,
                               RC.simplify_parts([num, den]), require_simplest=False))
        # ADDS_PARTS_WRONG: writes whole:part (den:num) — combines the whole with the part wrongly.
        out.append(_ratio_diag("MISC.RATIO.ADDS_PARTS_WRONG", correct,
                               RC.simplify_parts([den, num]), require_simplest=False))
        # NOT_SIMPLIFIED: gives part:rest without simplifying.
        if RC.gcd_list([num, rest]) > 1:
            out.append(_ratio_diag("MISC.RATIO.NOT_SIMPLIFIED", correct, [num, rest],
                                   require_simplest=True))

    elif task in ("share_two_part", "share_three_part"):
        total = params["total"]
        parts = params["parts"]
        labels = params["labels"]
        shares = RC.share(total, parts)
        s = sum(parts)
        one = total // s
        # WRONG_TOTAL_PARTS: divides by the number of parts (count), not the sum of parts.
        if len(parts) != s and total % len(parts) == 0:
            wrong_one = total // len(parts)
            predicted = [{"location": lab, "value": wrong_one * p} for lab, p in zip(labels, parts)]
            d = _table_diag("MISC.RATIO.WRONG_TOTAL_PARTS", shares, labels, predicted)
            if d is not None:
                out.append(d)
        # DIVIDES_BY_ONE_PART: divides the whole by a single part value instead of the sum.
        if parts[0] != s and total % parts[0] == 0:
            wrong_one = total // parts[0]
            predicted = [{"location": lab, "value": wrong_one * p} for lab, p in zip(labels, parts)]
            d = _table_diag("MISC.RATIO.DIVIDES_BY_ONE_PART", shares, labels, predicted)
            if d is not None:
                out.append(d)
        # PART_AS_WHOLE: gives each labelled share the value of one part (treats a part as the whole).
        if task == "share_two_part":
            predicted = [{"location": lab, "value": one * 1} for lab in labels]  # all equal one-part
            # only meaningful when shares differ; reuse the one-part value as the answer for each
            predicted = [{"location": lab, "value": p} for lab, p in zip(labels, parts)]
            d = _table_diag("MISC.RATIO.PART_AS_WHOLE", shares, labels, predicted)
            if d is not None:
                out.append(d)

    elif task == "missing_part":
        parts = params["parts"]
        ki = params["knownIndex"]
        mi = params["missingIndex"]
        kv = params["knownValue"]
        one = kv // parts[ki]
        correct = one * parts[mi]
        # DIVIDES_BY_ONE_PART: uses the known value itself as one part (multiplies kv by the ratio).
        out.append(_num_diag("MISC.RATIO.DIVIDES_BY_ONE_PART", correct, kv * parts[mi]))
        # MULTIPLIES_NOT_DIVIDES_UNITARY: multiplies to find one unit instead of dividing.
        out.append(_num_diag("MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY", correct,
                             kv * parts[ki] * parts[mi]))

    elif task == "direct_proportion":
        quantity = params["quantity"]
        total = params["total"]
        target = params["target"]
        correct = Fraction(total, quantity) * target
        # ADDITIVE_NOT_MULTIPLICATIVE: adds the difference (target - quantity) to the total.
        out.append(_num_diag("MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE", correct,
                             Fraction(total + (target - quantity))))
        # INVERSE_FOR_DIRECT: applies the inverse product rule (total*quantity/target).
        if target != 0:
            out.append(_num_diag("MISC.RATIO.INVERSE_FOR_DIRECT", correct,
                                 Fraction(total * quantity, target)))
        # DIVIDES_NOT_MULTIPLIES_UNITARY: divides by the target instead of multiplying.
        if target != 0:
            out.append(_num_diag("MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY", correct,
                                 Fraction(total, quantity * target)))

    elif task == "inverse_proportion":
        q1, v1, q2 = params["q1"], params["v1"], params["q2"]
        correct = (q1 * v1) // q2
        # DIRECT_FOR_INVERSE: scales directly (v1 * q2 / q1) instead of using the product invariant.
        if q1 != 0:
            out.append(_num_diag("MISC.RATIO.DIRECT_FOR_INVERSE", correct, Fraction(v1 * q2, q1)))
        # MULTIPLIES_NOT_DIVIDES_UNITARY: gives the product q1*v1 (forgets to divide by q2).
        out.append(_num_diag("MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY", correct, Fraction(q1 * v1)))
        # ADDITIVE_NOT_MULTIPLICATIVE: adds the change (q2 - q1) to v1.
        out.append(_num_diag("MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE", correct,
                             Fraction(v1 + (q2 - q1))))

    elif task == "unit_rate":
        total = params["total"]
        quantity = params["quantity"]
        correct = Fraction(total, quantity)
        # DIVIDES_NOT_MULTIPLIES_UNITARY: inverts the rate (quantity / total).
        if total != 0:
            out.append(_num_diag("MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY", correct,
                                 Fraction(quantity, total)))

    elif task == "best_buy":
        # Correction #4: cost-like tokens. NO_UNIT_RATE_COMPARE ignores item count and picks by the raw
        # token total (highest tokenCost); LOWEST_PRICE_NOT_BEST picks the fewest total tokens (cheapest)
        # rather than the lowest tokens-per-item. Both are WRONG directions (never the cost-per-item min).
        options = params["options"]
        correct_label = params["correctLabel"]
        # NO_UNIT_RATE_COMPARE: compares by raw token total -> picks the largest token cost.
        by_total = max(options, key=lambda o: (o["tokenCost"], o["label"]))
        out.append(_choice_diag("MISC.RATIO.NO_UNIT_RATE_COMPARE", correct_label, by_total["label"]))
        # LOWEST_PRICE_NOT_BEST: picks the smallest total tokens (cheapest), not the lowest cost-per-item.
        by_lowest = min(options, key=lambda o: (o["tokenCost"], o["label"]))
        out.append(_choice_diag("MISC.RATIO.LOWEST_PRICE_NOT_BEST", correct_label, by_lowest["label"]))

    elif task == "simple_scale":
        value = params["value"]
        fnum, fden = params["factorNum"], params["factorDen"]
        factor = Fraction(fnum, fden)
        correct = Fraction(value) * factor
        # SCALE_WRONG_DIRECTION: divides instead of multiplies (or vice versa) -> applies the reciprocal.
        if fnum != 0:
            out.append(_num_diag("MISC.RATIO.SCALE_WRONG_DIRECTION", correct,
                                 Fraction(value) * Fraction(fden, fnum)))
        # ADDITIVE_NOT_MULTIPLICATIVE: adds the scale parts (value + fnum - fden) instead of scaling.
        out.append(_num_diag("MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE", correct,
                             Fraction(value + fnum - fden)))

    # Correction #6: DEDUPE colliding predictions. When two applicable diagnostics for the SAME item
    # predict the IDENTICAL student response, only ONE is a distinct exercised pathway. Keep the FIRST
    # in deterministic registry/emit order (the canonical diagnostic for that predicted response) and
    # DROP the colliding duplicate so it is never counted as exercised. Keying on predictedResponse (the
    # observable student answer) is exact: identical predicted responses are grading-indistinguishable.
    deduped: List[Dict[str, Any]] = []
    seen_predictions: set = set()
    for d in out:
        if d is None:
            continue
        key = d["predictedResponse"]
        if key in seen_predictions:
            continue  # collided duplicate -> omitted (not counted as exercised)
        seen_predictions.add(key)
        deduped.append(d)
    return deduped


def _table_diag(mid: str, correct_cells: List[int], labels: List[str],
                predicted: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """A table-completion (sharing) diagnostic. Omitted when the predicted cell set equals the
    correct shares. expectedResultCode is 'incorrect'."""
    if predicted is None:
        return None
    if any(c["value"] < 0 for c in predicted):
        return None
    correct_by_label = {lab: val for lab, val in zip(labels, correct_cells)}
    pred_by_label = {c["location"]: c["value"] for c in predicted}
    if pred_by_label == correct_by_label:
        return None
    return {"misconceptionId": mid, "domain": DOMAIN, "task": None,
            "predictedResponse": ", ".join(f"{c['location']}={c['value']}" for c in predicted),
            "predictedCanonical": {"cells": list(predicted)},
            "observableError": _BY_ID[mid]["observableError"],
            "feedback": _BY_ID[mid]["feedback"],
            "expectedResultCode": "incorrect"}
