"""Unit + property tests for the linear-equations oracle.

Run:  python oracle/tests/test_linear.py
"""

import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from spi_oracle import linear_equations as lin          # noqa: E402
from spi_oracle.linexpr import LinExpr, solve_linear, normalize  # noqa: E402
from spi_oracle.linear_misconceptions import MISCONCEPTIONS, rules_for  # noqa: E402


class TestLinExpr(unittest.TestCase):
    def test_ops_and_solve(self):
        self.assertEqual(solve_linear(LinExpr.coef(2, 3), LinExpr.coef(0, 11)), Fraction(4))
        self.assertEqual(solve_linear(LinExpr.coef(3, 0), LinExpr.coef(0, 2)), Fraction(2, 3))
        self.assertEqual(solve_linear(LinExpr.coef(5, -3), LinExpr.coef(2, 9)), Fraction(4))
        a, b = normalize(LinExpr.coef(5, -3), LinExpr.coef(2, 9))
        self.assertEqual((a, b), (Fraction(3), Fraction(-12)))

    def test_no_unique_solution_raises(self):
        with self.assertRaises(ValueError):
            solve_linear(LinExpr.coef(2, 3), LinExpr.coef(2, 9))

    def test_bracket_expansion(self):
        e = LinExpr.coef(2, -1).scale(Fraction(3))   # 3(2x - 1) = 6x - 3
        self.assertEqual((e.a, e.b), (Fraction(6), Fraction(-3)))


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
        # 2x + 3 = 11 ; P=2,Q=3,R=0,T=11 ; s=4
        red = {"P": Fraction(2), "Q": Fraction(3), "R": Fraction(0), "T": Fraction(11),
               "kMul": None, "innerP": None, "innerQ": None}
        self.assertEqual(MISCONCEPTIONS["MISC.LINEQ.STOPS_BEFORE_DIVIDING"]["wrong"](red), Fraction(8))      # t-q
        self.assertEqual(MISCONCEPTIONS["MISC.LINEQ.WRONG_INVERSE"]["wrong"](red), Fraction(14, 2))          # (t+q)/(p-r)
        self.assertEqual(MISCONCEPTIONS["MISC.LINEQ.DIVIDE_ONE_TERM"]["wrong"](red), Fraction(11, 2) - 3)    # t/(p-r) - q
        self.assertEqual(MISCONCEPTIONS["MISC.LINEQ.DIVIDE_BY_CONSTANT"]["wrong"](red), Fraction(8, 3))      # (t-q)/q

    def test_one_step_mul_rules(self):
        red = {"P": Fraction(5), "Q": Fraction(0), "R": Fraction(0), "T": Fraction(20),
               "kMul": None, "innerP": None, "innerQ": None}  # 5x = 20 -> 4
        self.assertEqual(MISCONCEPTIONS["MISC.LINEQ.STOPS_BEFORE_DIVIDING"]["wrong"](red), Fraction(20))
        self.assertEqual(MISCONCEPTIONS["MISC.LINEQ.MULTIPLY_INSTEAD_OF_DIVIDE"]["wrong"](red), Fraction(100))
        self.assertEqual(MISCONCEPTIONS["MISC.LINEQ.REVERSES_DIVISION"]["wrong"](red), Fraction(5, 20))

    def test_signed_arith_slip_is_diagnostic_only(self):
        red = {"P": Fraction(2), "Q": Fraction(3), "R": Fraction(0), "T": Fraction(11),
               "kMul": None, "innerP": None, "innerQ": None}
        self.assertIsNone(MISCONCEPTIONS["MISC.LINEQ.SIGNED_ARITH_SLIP"]["wrong"](red))
        for ids in (rules_for(t) for t in lin.TASKS):
            self.assertNotIn("MISC.LINEQ.SIGNED_ARITH_SLIP", ids)


class TestValidate(unittest.TestCase):
    def test_valid_items_pass(self):
        for seed in range(1, 60):
            for mode in ("integer", "multiple-choice"):
                item = lin.generate(seed, {"answerType": mode})
                self.assertEqual(lin.validate(item)["status"], "pass", f"seed {seed} {mode}")

    def test_tampered_answer_fails(self):
        item = lin.generate(3, {"answerType": "multiple-choice"})
        item["answer"]["canonical"]["num"] += 1
        self.assertEqual(lin.validate(item)["status"], "fail")

    def test_coincidental_equality_is_not_leakage(self):
        # 2x = 2 has solution 1, and the coefficient 2 appears; this is not leakage.
        item = lin.generate(7, {"task": "one_step_mul", "answerType": "integer"})
        v = lin.validate(item)
        leak = next(c for c in v["checks"] if c["name"] == "no-answer-leakage")
        self.assertEqual(leak["result"], "pass")


class TestSweep(unittest.TestCase):
    def test_property_sweep(self):
        invalid = 0
        for seed in range(1, 3001):
            for mode in ("integer", "multiple-choice"):
                if lin.validate(lin.generate(seed, {"answerType": mode}))["status"] != "pass":
                    invalid += 1
        self.assertEqual(invalid, 0)

    def test_reproducible(self):
        for seed in (1, 99, 12345):
            a = lin.serialize(lin.generate(seed, {"answerType": "multiple-choice"}))
            b = lin.serialize(lin.generate(seed, {"answerType": "multiple-choice"}))
            self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main(verbosity=2)
