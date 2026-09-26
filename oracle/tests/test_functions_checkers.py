"""Oracle tests for the functions family's shared infrastructure: the exact polynomial, the
algebraic-expression checker and the interval (real-subset) checker.

  python oracle/tests/test_functions_checkers.py

The TypeScript mirrors are held to the same pins (core/exact-math/polynomial.test.ts,
core/answer-checking/*.test.ts) and both engines to one corpus (functions_checker_corpus.json).
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "oracle", "spi_oracle"))
sys.path.insert(0, os.path.join(ROOT, "oracle"))

from polynomial import Poly, poly_display  # noqa: E402
from expression_checker import CODES as E_CODES, check_expression, parse_expression, normalize_expression  # noqa: E402
from interval_checker import CODES as I_CODES, check_interval, parse_interval, interval_display, interval_to_json  # noqa: E402

QUAD = Poly.quadratic(4, -12, 10).to_json()
RAY_X = {"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": True, "direction": "ge"}
RAY_Y = {"kind": "ray", "variable": "y", "endpoint": {"num": -4, "den": 1}, "inclusive": True, "direction": "ge"}
EXC = {"kind": "reals-except", "variable": "x", "points": [{"num": 3, "den": 1}]}
BOUNDED = {"kind": "bounded", "variable": "y", "lo": {"num": -1, "den": 1}, "hi": {"num": 4, "den": 1}, "loInclusive": True, "hiInclusive": True}
REALS = {"kind": "reals"}


class TestPolynomial(unittest.TestCase):
    def test_canonical_form_and_degree(self):
        p = Poly([1, 2, 0, 0])
        self.assertEqual(p.to_json(), {"variable": "x", "coefficients": [{"num": 1, "den": 1}, {"num": 2, "den": 1}]})
        self.assertEqual(p.degree(), 1)
        self.assertEqual(Poly([0, 0, 0]).degree(), 0)
        self.assertTrue(Poly([]).is_zero())

    def test_arithmetic_and_compose(self):
        f, g = Poly.linear(2, -3), Poly.quadratic(1, 0, 1)
        self.assertEqual(f.mul(f).display(), "4x^2 - 12x + 9")
        self.assertEqual(f.pow(2).display(), "4x^2 - 12x + 9")
        self.assertEqual(f.add(g).display(), "x^2 + 2x - 2")
        self.assertEqual(g.sub(f).display(), "x^2 - 2x + 4")
        self.assertEqual(f.scale(Fraction(1, 2)).display(), "x - 3/2")
        self.assertEqual(g.compose(f).display(), "4x^2 - 12x + 10")
        self.assertEqual(f.compose(g).display(), "2x^2 - 1")
        self.assertEqual(g.compose(f).eval(4), 26)
        self.assertEqual(f.compose(g).eval(Fraction(1, 2)), Fraction(-1, 2))
        self.assertTrue(Poly.x().compose(f).equals(f))

    def test_display_contract(self):
        self.assertEqual(Poly.linear(Fraction(1, 2), 9).display(), "(1/2)x + 9")
        self.assertEqual(Poly.linear(Fraction(-1, 2), 9).display(), "(-1/2)x + 9")
        self.assertEqual(Poly.linear(-1, 5).display(), "-x + 5")
        self.assertEqual(Poly.linear(1, -5).display(), "x - 5")
        self.assertEqual(Poly.quadratic(1, 0, -4).display(), "x^2 - 4")
        self.assertEqual(Poly.quadratic(-2, 3, 0).display(), "-2x^2 + 3x")
        self.assertEqual(Poly.quadratic(1, Fraction(-1, 3), Fraction(2, 3)).display(), "x^2 - (1/3)x + 2/3")
        self.assertEqual(Poly([0]).display(), "0")
        self.assertEqual(poly_display([Fraction(7)]), "7")
        self.assertEqual(Poly.const(Fraction(-3, 4)).display(), "-3/4")

    def test_json_round_trip(self):
        p = Poly.quadratic(Fraction(1, 3), -2, 5)
        self.assertTrue(Poly.from_json(p.to_json()).equals(p))


class TestExpressionChecker(unittest.TestCase):
    def test_equivalent_forms_accepted(self):
        for s in ["4x^2-12x+10", "(2x-3)^2+1", "10 - 12x + 4x²", "4x**2 - 12*x + 10", "(2x-3)(2x-3)+1",
                  "(f o g)(x) = (2x-3)^2 + 1", "y = 4x^2 - 12x + 10", "2(2x^2 - 6x + 5)", "(8x^2 - 24x + 20)/2", "4·x^2 − 12·x + 10"]:
            self.assertEqual(check_expression(s, QUAD), {"code": "correct"}, s)

    def test_coefficient_literal_convention(self):
        half = Poly([9, Fraction(1, 2)]).to_json()
        for s in ["1/2x+9", "(x+18)/2", "x/2 + 9", "0.5x + 9", "9 + x/2"]:
            self.assertEqual(check_expression(s, half), {"code": "correct"}, s)

    def test_codes(self):
        self.assertEqual(check_expression("", QUAD)["code"], "unparseable")
        self.assertEqual(check_expression("6x-3=0", QUAD)["code"], "unparseable")
        self.assertEqual(check_expression("x^7", QUAD)["code"], "unparseable")
        self.assertEqual(check_expression("(2x-3", QUAD)["code"], "unparseable")
        self.assertEqual(check_expression("2t+1", QUAD)["code"], "wrong-variable")
        self.assertEqual(check_expression("(x+5)/(x-1)", QUAD)["code"], "not-polynomial")
        self.assertEqual(check_expression("x^-1", QUAD)["code"], "not-polynomial")
        self.assertEqual(check_expression("4x-2", QUAD)["code"], "wrong-degree")
        self.assertEqual(check_expression("4x^2-12x+9", QUAD)["code"], "wrong-coefficients")
        diag = [{"misconceptionId": "MISC.FUNC.COMP_SQUARE_NO_CROSS_TERM", "coefficients": [{"num": 9, "den": 1}, {"num": -12, "den": 1}, {"num": 4, "den": 1}]}]
        self.assertEqual(check_expression("4x^2-12x+9", QUAD, diag), {"code": "misconception", "misconceptionId": "MISC.FUNC.COMP_SQUARE_NO_CROSS_TERM"})

    def test_unary_minus_and_implicit_multiplication(self):
        self.assertEqual(parse_expression("-x^2")[1].display(), "-x^2")
        self.assertEqual(parse_expression("--x")[1].display(), "x")
        self.assertEqual(parse_expression("3(x+1)(x-2)")[1].display(), "3x^2 - 3x - 6")
        self.assertEqual(parse_expression("x(x-4)")[1].display(), "x^2 - 4x")
        self.assertEqual(parse_expression("-2^2")[1].display(), "-4")
        self.assertEqual(parse_expression("2x·3")[1].display(), "6x")

    def test_ascii_anchoring(self):
        self.assertEqual(check_expression("４x^2", QUAD)["code"], "unparseable")
        self.assertEqual(check_expression("٤x^2", QUAD)["code"], "unparseable")
        self.assertEqual(check_expression("4x^2 % 3", QUAD)["code"], "unparseable")
        self.assertIsNone(normalize_expression("x" * 201))
        self.assertEqual(check_expression("1" * 13 + "x", QUAD)["code"], "unparseable")


class TestIntervalChecker(unittest.TestCase):
    def test_accepted_forms_of_a_ray(self):
        for s in ["x >= 2", "x>=2", "2 <= x", "x≥2", "x ⩾ 2", "[2, inf)", "[2,∞)", "[2, infinity)", "[2, oo)",
                  "{x | x >= 2}", "{x : x ≥ 2}", "{x ∈ ℝ | x ≥ 2}", "x=>2"]:
            self.assertEqual(check_interval(s, RAY_X), {"code": "correct"}, s)

    def test_range_variables(self):
        for s in ["y >= -4", "f(x) ≥ -4", "g(x)>=-4", "[-4, inf)", "-4 <= y"]:
            self.assertEqual(check_interval(s, RAY_Y), {"code": "correct"}, s)
        self.assertEqual(check_interval("x >= -4", RAY_Y)["code"], "wrong-variable")
        self.assertEqual(check_interval("y >= 2", RAY_X)["code"], "wrong-variable")

    def test_exclusions_and_reals(self):
        for s in ["x != 3", "x =/= 3", "x ≠ 3", "x ∈ ℝ, x ≠ 3", "all real numbers except 3", "R \\ {3}", "ℝ∖{3}", "{x | x != 3}"]:
            self.assertEqual(check_interval(s, EXC), {"code": "correct"}, s)
        for s in ["all real numbers", "all reals", "R", "ℝ", "x ∈ ℝ", "(-inf, inf)", "(-∞, ∞)", "y in R", "the set of all real numbers"]:
            self.assertEqual(check_interval(s, REALS), {"code": "correct"}, s)

    def test_bounded(self):
        for s in ["-1 <= y <= 4", "4 >= y >= -1", "[-1, 4]", "y >= -1 and y <= 4", "y <= 4 and y >= -1", "{y | -1 <= y <= 4}"]:
            self.assertEqual(check_interval(s, BOUNDED), {"code": "correct"}, s)
        self.assertEqual(check_interval("-1 < y <= 4", BOUNDED)["code"], "wrong-inclusivity")
        self.assertEqual(check_interval("(-1, 4)", BOUNDED)["code"], "wrong-inclusivity")
        self.assertEqual(check_interval("-1 <= y <= 5", BOUNDED)["code"], "wrong-endpoint")
        self.assertEqual(check_interval("y >= -1", BOUNDED)["code"], "wrong-kind")

    def test_ray_diagnostics(self):
        self.assertEqual(check_interval("x <= 2", RAY_X)["code"], "wrong-direction")
        self.assertEqual(check_interval("x >= 3", RAY_X)["code"], "wrong-endpoint")
        self.assertEqual(check_interval("x > 2", RAY_X)["code"], "wrong-inclusivity")
        self.assertEqual(check_interval("(2, inf)", RAY_X)["code"], "wrong-inclusivity")
        self.assertEqual(check_interval("x != 2", RAY_X)["code"], "wrong-kind")
        self.assertEqual(check_interval("all real numbers", RAY_X)["code"], "wrong-kind")
        diag = [{"misconceptionId": "MISC.FUNC.DOMAIN_STRICT_ENDPOINT", "canonical": dict(RAY_X, inclusive=False)}]
        self.assertEqual(check_interval("x > 2", RAY_X, diag), {"code": "misconception", "misconceptionId": "MISC.FUNC.DOMAIN_STRICT_ENDPOINT"})
        for s in ["", "x = 2", "[5, 2]", "x >= 2 or x <= 1", "x >= 2 and x >= 3", "[2, inf]", "x >= two", "x ≥ 2 ≥ 1"]:
            self.assertEqual(check_interval(s, RAY_X)["code"], "unparseable", s)
        self.assertEqual(check_interval("(-inf, 2)", RAY_X)["code"], "wrong-direction")

    def test_display_round_trip(self):
        cases = [(REALS, "all real numbers"), (RAY_X, "x >= 2"), (RAY_Y, "y >= -4"), (EXC, "x != 3"), (BOUNDED, "-1 <= y <= 4"),
                 ({"kind": "ray", "variable": "x", "endpoint": {"num": -5, "den": 2}, "inclusive": False, "direction": "le"}, "x < -5/2"),
                 ({"kind": "reals-except", "variable": "y", "points": [{"num": 1, "den": 1}, {"num": 3, "den": 1}]}, "y != 1, 3")]
        for c, d in cases:
            self.assertEqual(interval_display(c), d)
            self.assertEqual(check_interval(d, c), {"code": "correct"}, d)
        code, parsed = parse_interval("x >= 1/2")
        self.assertEqual(interval_to_json(parsed), {"kind": "ray", "variable": "x", "endpoint": {"num": 1, "den": 2}, "inclusive": True, "direction": "ge"})

    def test_decimals_and_ascii_digits(self):
        self.assertEqual(check_interval("x <= 2.5", {"kind": "ray", "variable": "x", "endpoint": {"num": 5, "den": 2}, "inclusive": True, "direction": "le"})["code"], "correct")
        self.assertEqual(check_interval("x >= ٢", RAY_X)["code"], "unparseable")


class TestCorpus(unittest.TestCase):
    """The committed corpus is what the TypeScript checkers are pinned to; it must be reproducible from the
    Python checkers and must exercise every code of both vocabularies."""

    def test_corpus_reproducible_and_complete(self):
        path = os.path.join(ROOT, "oracle", "golden", "functions_checker_corpus.json")
        corpus = json.load(open(path, encoding="utf-8"))
        for c in corpus["expression"]:
            self.assertEqual(check_expression(c["input"], c["canonical"], c["diagnostics"]), c["expected"], c["input"])
        for c in corpus["interval"]:
            self.assertEqual(check_interval(c["input"], c["canonical"], c["diagnostics"]), c["expected"], c["input"])
        self.assertEqual(set(E_CODES), {c["expected"]["code"] for c in corpus["expression"]})
        self.assertEqual(set(I_CODES), {c["expected"]["code"] for c in corpus["interval"]})


if __name__ == "__main__":
    unittest.main(verbosity=2)
