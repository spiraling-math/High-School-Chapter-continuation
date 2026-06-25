"""gen.geometry.transformations — describe-task answer checker (owner I, J).

Maps a learner's free-text description against the expected canonical descriptor, returning exactly one
code from the single RESULT_CODES vocabulary (owner J). Parse-level failures (malformed / missing-* /
unsupported-* / contradictory / ambiguous / unparsed-trailing) come straight from the anchored parser;
a clean parse is then compared structurally to assign correct / wrong-transformation-type /
wrong-translation-vector / wrong-reflection-axis / wrong-rotation-centre / wrong-rotation-amount.

domains/geometry/transformations-checker.ts mirrors this byte-for-byte.
"""

from __future__ import annotations

from typing import Any, Dict

from .transformations_core import descriptors_equal, parse_descriptor


def check_description(expected: Dict[str, Any], student_text: str) -> str:
    pr = parse_descriptor(student_text)
    if pr.code is not None:
        return pr.code
    got = pr.descriptor
    assert got is not None
    if got["kind"] != expected["kind"]:
        return "wrong-transformation-type"
    if descriptors_equal(got, expected):
        return "correct"
    if got["kind"] == "translation":
        return "wrong-translation-vector"
    if got["kind"] == "reflection":
        return "wrong-reflection-axis"
    # rotation: distinguish a wrong centre from a wrong amount (centre takes priority).
    if got["centre"] != expected["centre"]:
        return "wrong-rotation-centre"
    return "wrong-rotation-amount"
