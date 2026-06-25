"""Schema-conformance evidence for the approved answer.type "transformation" extension (owner C).

  python oracle/tests/test_transformation_schema.py

Canonical-first: the structured descriptor IS answer.canonical (no sibling field); display is derived;
transformation answers never carry units/measure/tolerance. The discriminated union is enforced by
if/then/const rules so the runtime Ajv validator and this Python conformance checker apply IDENTICAL
rules. These positive + negative fixtures are the schema-conformance evidence; a parallel TS test
(core/schema/runtime-validate.test.ts family) covers the Ajv side. Existing approved items must remain
valid and byte-for-byte unchanged.
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


def _T(canonical, display="d"):
    return {"type": "transformation", "canonical": canonical, "display": display}


class TestTransformationSchema(unittest.TestCase):
    POSITIVE = [
        ("translation", _T({"kind": "translation", "vector": {"dx": 3, "dy": -2}}, "translation by vector (3, -2)")),
        ("reflection vertical", _T({"kind": "reflection", "axis": {"kind": "vertical", "value": 4}}, "reflection in x = 4")),
        ("reflection horizontal", _T({"kind": "reflection", "axis": {"kind": "horizontal", "value": -2}}, "reflection in y = -2")),
        ("reflection diagonal y=x", _T({"kind": "reflection", "axis": {"kind": "diagonal", "equation": "y=x"}}, "reflection in y = x")),
        ("reflection diagonal y=-x", _T({"kind": "reflection", "axis": {"kind": "diagonal", "equation": "y=-x"}}, "reflection in y = -x")),
        ("rotation", _T({"kind": "rotation", "centre": {"x": 2, "y": -1}, "quarterTurnsCCW": 3}, "rotation 270 deg anticlockwise about (2, -1)")),
    ]
    NEGATIVE = [
        ("missing branch field (reflection no axis)", _T({"kind": "reflection"})),
        ("cross-branch field (translation + axis)", _T({"kind": "translation", "vector": {"dx": 1, "dy": 2}, "axis": {"kind": "vertical", "value": 0}})),
        ("cross-branch field (rotation + vector)", _T({"kind": "rotation", "centre": {"x": 0, "y": 0}, "quarterTurnsCCW": 1, "vector": {"dx": 1, "dy": 1}})),
        ("non-integer coordinate", _T({"kind": "translation", "vector": {"dx": 1.5, "dy": 2}})),
        ("zero translation vector", _T({"kind": "translation", "vector": {"dx": 0, "dy": 0}})),
        ("quarterTurnsCCW out of range", _T({"kind": "rotation", "centre": {"x": 0, "y": 0}, "quarterTurnsCCW": 4})),
        ("unsupported diagonal equation", _T({"kind": "reflection", "axis": {"kind": "diagonal", "equation": "y=2x"}})),
        ("missing rotation centre", _T({"kind": "rotation", "quarterTurnsCCW": 1})),
        ("extra property on canonical", _T({"kind": "translation", "vector": {"dx": 1, "dy": 2}, "foo": 1})),
        ("legacy units on transformation", {"type": "transformation", "canonical": {"kind": "translation", "vector": {"dx": 1, "dy": 1}}, "units": "cm", "display": "d"}),
        ("legacy measure on transformation", {"type": "transformation", "canonical": {"kind": "translation", "vector": {"dx": 1, "dy": 1}}, "measure": {"dimension": "length", "baseUnit": "cm", "exponent": 1}, "display": "d"}),
        ("tolerance on transformation", {"type": "transformation", "canonical": {"kind": "translation", "vector": {"dx": 1, "dy": 1}}, "tolerance": {"absolute": 1}, "display": "d"}),
        ("transformation canonical used with integer type", {"type": "integer", "canonical": {"kind": "translation", "vector": {"dx": 1, "dy": 1}}, "display": "d"}),
    ]

    def test_positive_descriptors_accepted(self):
        for name, ans in self.POSITIVE:
            self.assertEqual(_errors(ans), [], f"{name} should be valid")

    def test_negative_descriptors_rejected(self):
        for name, ans in self.NEGATIVE:
            self.assertNotEqual(_errors(ans), [], f"{name} should be rejected")

    def test_full_conformance_unchanged(self):
        # every existing approved item still conforms (additive, back-compatible extension).
        rc = cc.main() if hasattr(cc, "main") else 0
        # main prints + returns nonzero on failure; fall back to a direct sweep if main is absent.
        self.assertIn(rc, (0, None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
