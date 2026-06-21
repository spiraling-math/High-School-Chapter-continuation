"""Unit + property tests for the linear-equations oracle (v1.0.1).

Run:  python oracle/tests/test_linear.py
"""

import os
import re
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from spi_oracle import linear_equations as lin          # noqa: E402
from spi_oracle.linexpr import LinExpr, solve_linear, normalize  # noqa: E402
from spi_oracle.linear_misconceptions import MISCONCEPTIONS, rules_for  # noqa: E402

PLACEHOLDER = re.compile(r"(?<![A-Za-z])[pqrtk](?![A-Za-z])")


class TestLinExpr(unittest.TestCase):
    def test_ops_and_solve(self):
        self.assertEqual(solve_linear(LinExpr.coef(2, 3), LinExpr.coef(0, 11)), Fraction(4))
        self.assertEqual(solve_linear(LinExpr.coef(3, 0), LinExpr.coef(0, 2)), Fraction(2, 3))
        a, b = normalize(LinExpr.coef(5, -3), LinExpr.coef(2, 9))
        self.assertEqual((a, b), (Fraction(3), Fraction(-12)))

    def test_no_unique_solution_raises(self):
        with self.assertRaises(ValueError):
            solve_linear(LinExpr.coef(2, 3), LinExpr.coef(2, 9))


class TestSolve(unittest.TestCase):
    def test_each_task_solution(self):
        cases = {
            "one_step_add": ({"task": "one_step_add", "b": {"num": 4, "den": 1}, "c": {"num": 9, "den": 1}}, Fraction(5)),
            "one_step_mul": ({"task": "one_step_mul", "a": {"num": 3, "den": 1}, "c": {"num": 2, "den": 1}}, Fraction(2, 3)),
            "two_step": ({"task": "two_step", "a": {"num": 2, "den": 1}, "b": {"num": 3, "den": 1}, "c": {"num": 11, "den": 1}}, Fraction(4)),
            "both_sides": ({"task": "both_sides", "a": {"num": 5, "den": 1}, "b": {"num": -3, "den": 1}, "c": {"num": 2, "den": 1}, "d": {"num": 9, "den": 1}}, Fraction(4)),
        }
        for task, (params, expected) in cases.items():
            self.assertEqual(lin.solve(params), expected, task)


class TestMisconceptions(unittest.TestCase):
    def test_two_step_wrong_values(self):
        red = {"P": Fraction(2), "Q": Fraction(3), "R": Fraction(0), "T": Fraction(11),
               "kMul": None, "innerP": None, "innerQ": None}  # 2x + 3 = 11 -> 4
        self.assertEqual(MISCONCEPTIONS["MISC.LINEQ.STOPS_BEFORE_DIVIDING"]["wrong"](red), Fraction(8))
        self.assertEqual(MISCONCEPTIONS["MISC.LINEQ.WRONG_INVERSE"]["wrong"](red), Fraction(7))
        self.assertEqual(MISCONCEPTIONS["MISC.LINEQ.DIVIDE_BY_CONSTANT"]["wrong"](red), Fraction(8, 3))

    def test_signed_arith_slip_excluded_from_mc(self):
        for t in lin.TASKS:
            self.assertNotIn("MISC.LINEQ.SIGNED_ARITH_SLIP", rules_for(t))

    def test_feedback_has_no_internal_placeholders(self):
        # every feedback string, for representative reduced forms, is symbol-free
        for seed in range(1, 400):
            item = lin.generate(seed, {"interactionType": "multiple-choice"})
            red = lin._reduced(item["params"])
            for d in item["distractors"]:
                m = MISCONCEPTIONS[d["misconceptionId"]]
                fb = m["feedback"](red)
                self.assertTrue(fb)
                self.assertIsNone(PLACEHOLDER.search(fb), f"placeholder in feedback: {fb!r}")
                self.assertIsNone(PLACEHOLDER.search(d["rationale"]), f"placeholder in rationale: {d['rationale']!r}")


class TestSolutionStrategy(unittest.TestCase):
    def test_positive_coefficient_collection(self):
        # 4x + 3 = 5x - 2 -> never isolate '-x'
        for seed in range(1, 400):
            steps = lin.generate(seed, {"task": "both_sides", "interactionType": "free-response"})["solution"]["steps"]
            for st in steps:
                self.assertNotRegex(st.get("intermediateResult", ""), r"(^|=\s*)-x\s*=")

    def test_one_step_add_integer_only(self):
        for seed in range(1, 400):
            item = lin.generate(seed, {"task": "one_step_add", "interactionType": "free-response"})
            self.assertEqual(item["answer"]["type"], "integer")


class TestValidate(unittest.TestCase):
    def test_valid_items_pass(self):
        for seed in range(1, 60):
            for mode in ("free-response", "multiple-choice"):
                item = lin.generate(seed, {"interactionType": mode})
                self.assertEqual(lin.validate(item)["status"], "pass", f"seed {seed} {mode}")

    def test_tampered_answer_fails(self):
        item = lin.generate(3, {"interactionType": "multiple-choice"})
        item["answer"]["canonical"]["num"] += 1
        self.assertEqual(lin.validate(item)["status"], "fail")

    def test_legacy_answertype_is_back_compatible(self):
        for seed in (1, 7, 42, 99):
            self.assertEqual(lin.serialize(lin.generate(seed, {"answerType": "integer"})),
                             lin.serialize(lin.generate(seed, {"interactionType": "free-response"})))
            self.assertEqual(lin.serialize(lin.generate(seed, {"answerType": "multiple-choice"})),
                             lin.serialize(lin.generate(seed, {"interactionType": "multiple-choice"})))
        with self.assertRaises(ValueError):
            lin.generate(1, {"interactionType": "free-response", "answerType": "multiple-choice"})

    def test_coincidental_equality_is_not_leakage(self):
        item = lin.generate(7, {"task": "one_step_mul", "interactionType": "free-response"})
        leak = next(c for c in lin.validate(item)["checks"] if c["name"] == "no-answer-leakage")
        self.assertEqual(leak["result"], "pass")


class TestSweep(unittest.TestCase):
    def test_property_sweep(self):
        invalid = 0
        for seed in range(1, 3001):
            for mode in ("free-response", "multiple-choice"):
                if lin.validate(lin.generate(seed, {"interactionType": mode}))["status"] != "pass":
                    invalid += 1
        self.assertEqual(invalid, 0)

    def test_reproducible(self):
        for seed in (1, 99, 12345):
            a = lin.serialize(lin.generate(seed, {"interactionType": "multiple-choice"}))
            b = lin.serialize(lin.generate(seed, {"interactionType": "multiple-choice"}))
            self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main(verbosity=2)
