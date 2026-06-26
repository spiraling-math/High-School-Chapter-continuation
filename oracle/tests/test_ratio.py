"""gen.proportion.ratio oracle tests — exact math, parser/checkers, the independent validator,
the interaction policy, role-based figure leakage, and the parity-fixture reproducibility.

  python oracle/tests/test_ratio.py
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "oracle"))

import check_conformance as cc  # noqa: E402
from spi_oracle import ratio as R  # noqa: E402
from spi_oracle import ratio_core as RC  # noqa: E402
from spi_oracle import ratio_misconceptions as RM  # noqa: E402

_REG = cc.load_registry()
_ITEM = _REG["https://spi-math.academy/schemas/question-item.schema.json"]


def _conf(item):
    e = []
    cc.check(item, _ITEM, _REG, _ITEM, "item", e)
    return e


def _valid(item):
    v = R.validate(item)
    return (v.get("valid") if isinstance(v, dict) else v), [c["name"] for c in v["checks"] if not c["ok"]]


class TestMath(unittest.TestCase):
    def test_exact_reasoning(self):
        self.assertEqual(RC.simplify_parts([4, 6]), [2, 3])
        self.assertEqual(RC.simplify_parts([6, 4]), [3, 2])
        self.assertTrue(RC.ratios_equal([2, 3], [4, 6]))
        self.assertFalse(RC.ratios_equal([2, 3], [3, 2]))
        self.assertEqual(RC.share(20, [2, 3]), [8, 12])
        self.assertEqual(RC.share(30, [2, 3, 5]), [6, 9, 15])
        self.assertIsNone(RC.share(7, [2, 3]))
        self.assertEqual(RC.missing_part(18, 1, 0, [2, 3]), 12)
        self.assertIsNone(RC.missing_part(10, 1, 0, [2, 3]))
        self.assertEqual(RC.direct_proportion(12, 3, 5), Fraction(20))
        self.assertEqual(RC.unit_rate(12, 4), Fraction(3))
        self.assertEqual(RC.inverse_proportion(4, 6, 3), 8)
        self.assertIsNone(RC.inverse_proportion(5, 6, 4))


class TestCheckers(unittest.TestCase):
    def test_ratio_codes(self):
        self.assertEqual(RC.check_ratio([2, 3], "2:3")["code"], "correct")
        self.assertEqual(RC.check_ratio([2, 3], "4:6")["code"], "equivalent-not-simplified")
        self.assertTrue(RC.check_ratio([2, 3], "4:6")["partial"])
        self.assertEqual(RC.check_ratio([2, 3], "4:6", require_simplest=False)["code"], "correct")
        self.assertEqual(RC.check_ratio([2, 3], "3:2")["code"], "wrong-order")
        self.assertEqual(RC.check_ratio([2, 3], "4:5")["code"], "wrong-ratio")
        self.assertEqual(RC.check_ratio([2, 3], "2:3:5")["code"], "wrong-number-of-parts")
        self.assertEqual(RC.check_ratio([2, 3], "0:3")["code"], "zero-or-negative-part")
        self.assertEqual(RC.check_ratio([2, 3], "2.5:3")["code"], "unsupported-term")
        self.assertEqual(RC.check_ratio([2, 3], "2:3x")["code"], "unparsed-trailing-text")
        self.assertEqual(RC.check_ratio([2, 3], "hello")["code"], "malformed-response")
        self.assertEqual(RC.check_ratio([2, 3, 5], "4:6:10")["code"], "equivalent-not-simplified")

    def test_all_nine_ratio_codes_reachable(self):
        probes = ["2:3", "4:6", "3:2", "4:5", "2:3:5", "0:3", "2.5:3", "2:3x", "hello"]
        seen = {RC.check_ratio([2, 3], p)["code"] for p in probes}
        for code in RC.RATIO_RESULT_CODES:
            self.assertIn(code, seen, f"ratio result code {code} not reachable")

    def test_choice_codes(self):
        self.assertEqual(RC.check_choice("B", "B"), "correct")
        self.assertEqual(RC.check_choice("B", "A"), "wrong-choice")
        self.assertEqual(RC.check_choice("B", "??"), "malformed-response")

    def test_parser_rejections(self):
        for bad in ["2.5:3", "0:3", "-2:3", "2:", "2:3:4:5", "2,3", "2∶3", "two to three", "2 to 3"]:
            parts, code = RC.parse_ratio(bad)
            self.assertIsNone(parts, f"{bad} should not parse")
            self.assertIsNotNone(code)
        for good in ["2:3", "2 : 3", "4:6", "2:3:5", "4 : 6 : 10"]:
            parts, code = RC.parse_ratio(good)
            self.assertIsNotNone(parts, f"{good} should parse")
            self.assertIsNone(code)

    def test_ascii_anchored_no_unicode_or_oversized(self):
        # Regression for the adversarial-review CRITICAL parity break: the ASCII-anchored parser must
        # reject EVERY non-ASCII digit (Arabic-Indic/Persian/Devanagari/Thai/fullwidth/math-bold), any
        # mixed-script term, and any oversized (>12-digit) term as unsupported-term — identically to the
        # TS mirror (domains/proportion/ratio.test.ts pins the SAME corpus + expected codes). Pinning the
        # exact codes here + there asserts Py<->TS agreement on the learner-input GRADING path, which the
        # serialize-only golden/parity fixtures structurally cannot exercise.
        UNSUPPORTED = ["٢:٣", "３:４", "२:३", "𝟚:𝟛", "۲:۳", "๒:๓", "5:３", "２:40", "١٢:٣",
                       "1000000000000000000000:3", "9007199254740993:9007199254740993",
                       "2:33333333333333333333333333", "2∶3", "2 to 3", "2,3", "2.5:3"]
        for s in UNSUPPORTED:
            self.assertEqual(RC.check_ratio([2, 3], s)["code"], "unsupported-term", f"{s!r}")
        # ASCII still grades exactly as before
        self.assertEqual(RC.check_ratio([2, 3], "2:3")["code"], "correct")
        self.assertEqual(RC.check_ratio([2, 3], "4:6")["code"], "equivalent-not-simplified")


class TestGeneratorContract(unittest.TestCase):
    def test_all_tasks_conform_and_validate(self):
        for task in R.RATIO_TASKS:
            for seed in (1, 7, 50, 999):
                it = R.generate(seed, {"task": task})
                self.assertEqual(_conf(it), [], f"{task} seed={seed} conform")
                valid, bad = _valid(it)
                self.assertTrue(valid, f"{task} seed={seed} validate {bad}")

    def test_answer_types_per_task(self):
        want = {"simplify": "ratio", "write_from_quantities": "ratio", "ratio_to_fraction": "exact-rational",
                "fraction_to_ratio": "ratio", "share_two_part": "table-completion",
                "share_three_part": "table-completion", "inverse_proportion": "integer",
                "best_buy": "multiple-choice"}
        for task, atype in want.items():
            self.assertEqual(R.generate(11, {"task": task})["answer"]["type"], atype, task)
        # integer-when-whole tasks emit integer or exact-rational
        for task in ("direct_proportion", "unit_rate", "simple_scale", "missing_part"):
            self.assertIn(R.generate(11, {"task": task})["answer"]["type"], ("integer", "exact-rational"))

    def test_interaction_policy(self):
        # best_buy is MC-only: FR raises; the FR-ineligible tasks raise on MC; MC-eligible accept MC.
        with self.assertRaises(R.InteractionNotSupported):
            R.generate(1, {"task": "best_buy", "interactionType": "free-response"})
        for fr_only in ("write_from_quantities", "share_two_part", "share_three_part", "missing_part", "unit_rate", "simple_scale"):
            with self.assertRaises(R.InteractionNotSupported):
                R.generate(1, {"task": fr_only, "interactionType": "multiple-choice"})
        for mc in ("simplify", "ratio_to_fraction", "fraction_to_ratio", "direct_proportion", "inverse_proportion"):
            it = R.generate(3, {"task": mc, "interactionType": "multiple-choice"})
            self.assertEqual(it["interactionType"], "multiple-choice")
            self.assertTrue(it.get("options"), f"{mc} MC must carry options")

    def test_best_buy_strict_min(self):
        it = R.generate(7, {"task": "best_buy"})
        self.assertEqual(it["answer"]["type"], "multiple-choice")
        valid, bad = _valid(it)
        self.assertTrue(valid, bad)

    def test_role_based_no_leakage(self):
        for task in R.RATIO_TASKS:
            it = R.generate(13, {"task": task})
            v = R.validate(it)
            names = {c["name"]: c["ok"] for c in v["checks"]}
            for chk in ("student-figure-has-no-overlay", "student-unknown-marked-not-valued",
                        "answer-key-overlay-additive", "student-and-key-share-base", "student-a11y-no-result"):
                if chk in names:
                    self.assertTrue(names[chk], f"{task} {chk}")

    def test_reproducible(self):
        for task in R.RATIO_TASKS:
            a = R.serialize(R.generate(321, {"task": task}))
            b = R.serialize(R.generate(321, {"task": task}))
            self.assertEqual(a, b)


class TestDiagnostics(unittest.TestCase):
    def test_registry_conforms(self):
        schema = _REG["https://spi-math.academy/schemas/misconception.schema.json"]
        for m in RM.registry():
            e = []
            cc.check(m, schema, _REG, schema, m["misconceptionId"], e)
            self.assertEqual(e, [], m["misconceptionId"])
        self.assertEqual(len(RM.ALL_IDS), 16)


class TestRegressionDefects(unittest.TestCase):
    """Regression guards for the five confirmed v1.0.0 defects (oracle-first; mirrored in TS)."""

    def test_best_buy_mc_option_displays_pairwise_distinct(self):
        # DEFECT 4: two non-winning options could share a unit rate -> byte-identical displays.
        # Over a wide seed sweep every best_buy MC item must have pairwise-distinct option DISPLAYS,
        # the new mc-option-displays-distinct validator must pass, and the formerly-bad seeds repro clean.
        for seed in range(1, 3001):
            it = R.generate(seed, {"task": "best_buy"})
            disps = [o["display"] for o in it["options"]]
            self.assertEqual(len(set(disps)), len(disps), f"seed {seed} duplicate displays {disps}")
            names = {c["name"]: c["ok"] for c in R.validate(it)["checks"]}
            self.assertTrue(names.get("mc-option-displays-distinct"), f"seed {seed} displays-distinct check")
        for seed in (95, 271, 314, 549, 748, 992):
            it = R.generate(seed, {"task": "best_buy"})
            disps = [o["display"] for o in it["options"]]
            self.assertEqual(len(set(disps)), len(disps), f"formerly-dup seed {seed}: {disps}")

    def test_no_task_free_response_never_raises(self):
        # DEFECT 5: a no-task free-response request must NEVER raise InteractionNotSupported, and must
        # never select an MC-only task (best_buy).
        for seed in range(1, 2501):
            it = R.generate(seed, {"interactionType": "free-response"})
            self.assertEqual(it["interactionType"], "free-response", seed)
            self.assertNotIn(it["params"]["task"], R.MC_ONLY_TASKS, f"seed {seed} picked MC-only task")

    def test_every_declared_band_reachable_per_task(self):
        # DEFECT 6/7: every band in the DECLARED inclusive range [lo,hi] is produced across a seed
        # sweep (the previously-unreachable interior band of the four 3-span tasks now occurs).
        from collections import Counter
        per = {t: Counter() for t in R.RATIO_TASKS}
        for seed in range(1, 6001):
            it = R.generate(seed)
            p = it["params"]
            per[p["task"]][it["difficulty"]["overallBand"]] += 1
        for task in R.RATIO_TASKS:
            lo, hi = R.TASK_BANDS[task]
            for band in range(lo, hi + 1):
                self.assertGreater(per[task][band], 0,
                                   f"{task} band {band} in declared range [{lo},{hi}] is unreachable")

    def test_misconception_reverse_relationships(self):
        # DEFECT 8: the two omitted reverse objectiveRelationships are present.
        by_id = {m["misconceptionId"]: m for m in RM.MISCONCEPTIONS}
        self.assertIn("SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01",
                      by_id["MISC.RATIO.NOT_SIMPLIFIED"]["objectiveRelationships"])
        self.assertIn("SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01",
                      by_id["MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE"]["objectiveRelationships"])


class TestParityFixture(unittest.TestCase):
    def test_parity_fixture_reproducible(self):
        path = os.path.join(ROOT, "oracle", "golden", "ratio.parity.json")
        if not os.path.exists(path):
            self.skipTest("parity fixture not generated")
        entries = json.load(open(path, encoding="utf-8"))
        self.assertGreaterEqual(len(entries), 300)
        for e in entries[::7]:
            self.assertEqual(R.serialize(R.generate(e["seed"], {"task": e["task"]})), e["serialized"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
