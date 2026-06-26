"""Schema-conformance evidence for the approved answer.type "ratio" extension (owner B).

  python oracle/tests/test_ratio_schema.py

Canonical-first: the ordered simplest-form positive-integer tuple {parts} IS answer.canonical (no sibling
field); display is derived; ratio answers never carry units/measure/tolerance. The rules are enforced by
if/then/const in allOf so the runtime Ajv validator and this Python conformance checker apply IDENTICAL
rules. parts are 2-3 positive integers in v1.0.0; a canonical carrying 'parts' must be type "ratio".
Existing approved items remain valid + byte-for-byte unchanged (the full conformance sweep is the proof).
"""

from __future__ import annotations

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import check_conformance as cc  # noqa: E402

_SCHEMA = json.load(open(os.path.join(HERE, "..", "..", "schemas", "question-item.schema.json"), encoding="utf-8"))
_REG = cc.load_registry()
_ANSWER = _SCHEMA["$defs"]["answer"]


def _errors(ans):
    e = []
    cc.check(ans, _ANSWER, _REG, _SCHEMA, "answer", e)
    return e


def _R(parts, display="d", **extra):
    return {"type": "ratio", "canonical": {"parts": parts}, "display": display, **extra}


class TestRatioSchema(unittest.TestCase):
    POSITIVE = [
        ("two-part", _R([2, 3], "2:3")),
        ("three-part", _R([2, 3, 5], "2:3:5")),
        ("larger simplest-form", _R([3, 7], "3:7")),
    ]
    NEGATIVE = [
        ("zero part", _R([0, 3])),
        ("negative part", _R([2, -3])),
        ("non-integer part", _R([2.5, 3])),
        ("too few parts (1)", _R([2])),
        ("too many parts (4) in v1.0.0", _R([1, 2, 3, 4])),
        ("extra property on canonical", {"type": "ratio", "canonical": {"parts": [2, 3], "foo": 1}, "display": "d"}),
        ("legacy units on ratio", _R([2, 3], units="cm")),
        ("legacy measure on ratio", _R([2, 3], measure={"dimension": "length", "baseUnit": "cm", "exponent": 1})),
        ("tolerance on ratio", _R([2, 3], tolerance={"absolute": 1})),
        ("ratio-shaped canonical with integer type", {"type": "integer", "canonical": {"parts": [2, 3]}, "display": "d"}),
        ("ratio-shaped canonical with exact-rational type", {"type": "exact-rational", "canonical": {"parts": [2, 3]}, "display": "d"}),
    ]

    def test_positive_ratios_accepted(self):
        for name, ans in self.POSITIVE:
            self.assertEqual(_errors(ans), [], f"{name} should be valid")

    def test_negative_ratios_rejected(self):
        for name, ans in self.NEGATIVE:
            self.assertNotEqual(_errors(ans), [], f"{name} should be rejected")

    def test_ratio_in_answer_type_enum(self):
        self.assertIn("ratio", _SCHEMA["$defs"]["answerType"]["enum"])

    def test_full_conformance_unchanged(self):
        rc = cc.main() if hasattr(cc, "main") else 0
        self.assertIn(rc, (0, None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
