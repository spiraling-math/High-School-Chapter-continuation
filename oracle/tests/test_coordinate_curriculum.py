"""Schema test for the coordinate-lines curriculum objectives (DECISION_LOG #41).

Confirms the new strand value `coordinate-geometry-straight-line-graphs` and the new
`approved-for-implementation` review status validate against the curriculum-objective
JSON schema, and that the eight COORD objectives carry mathematical-only answerTypes
(never `multiple-choice`, which is an interaction, not an answer type).
"""

from __future__ import annotations

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))  # oracle/ for check_conformance

from check_conformance import load_registry, check  # noqa: E402

SID = "https://spi-math.academy/schemas/curriculum-objective.schema.json"
COORD_FILE = os.path.join(ROOT, "curriculum", "objectives", "SPI.MIDDLE.GEO.COORD.json")
NEW_STRAND = "coordinate-geometry-straight-line-graphs"


class TestCoordinateCurriculum(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_registry()
        cls.schema = cls.registry[SID]
        with open(COORD_FILE, encoding="utf-8") as fh:
            cls.objectives = json.load(fh)

    def _validate(self, obj):
        errors: list = []
        check(obj, self.schema, self.registry, self.schema, obj["objectiveId"], errors)
        return errors

    def test_new_strand_validates(self):
        # The curriculum schema accepts the new strand value (strand is a free string).
        sample = dict(self.objectives[0])
        self.assertEqual(sample["strand"], NEW_STRAND)
        self.assertEqual(self._validate(sample), [])

    def test_all_coord_objectives_validate(self):
        self.assertEqual(len(self.objectives), 8)
        for obj in self.objectives:
            self.assertEqual(self._validate(obj), [], f"{obj['objectiveId']} must validate")
            self.assertEqual(obj["strand"], NEW_STRAND)
            self.assertEqual(obj["reviewStatus"], "approved-for-implementation")

    def test_answer_types_are_mathematical_only(self):
        for obj in self.objectives:
            self.assertNotIn("multiple-choice", obj["answerTypes"],
                             f"{obj['objectiveId']} must not list multiple-choice as an answer type")

    def test_unknown_strand_field_still_rejects_bad_enum_values(self):
        # Guard: the schema still rejects an out-of-enum reviewStatus, so the additive
        # 'approved-for-implementation' value did not loosen validation elsewhere.
        bad = dict(self.objectives[0])
        bad["reviewStatus"] = "totally-made-up"
        self.assertTrue(self._validate(bad))


if __name__ == "__main__":
    unittest.main(verbosity=2)
