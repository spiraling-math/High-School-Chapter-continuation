"""Build the cross-engine checker corpus for the functions family (owner lesson from ratio v1.0.0: the
Python and TypeScript parsers MUST accept and reject identically — a grading-path divergence is
invisible to generator-output parity).

Run:  python oracle/make_functions_checker_corpus.py
Writes: oracle/golden/functions_checker_corpus.json — every (input, canonical) case with the code the
Python oracle assigns; core/answer-checking/functions-checker-corpus.test.ts asserts the TypeScript
checkers produce the identical code (and misconceptionId) for every case.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))

from expression_checker import check_expression  # noqa: E402
from interval_checker import check_interval  # noqa: E402
from polynomial import Poly  # noqa: E402

OUT = os.path.join(HERE, "golden", "functions_checker_corpus.json")

QUAD = Poly.quadratic(4, -12, 10).to_json()
HALF = Poly([9, "1/2"]).to_json()
LIN = Poly.linear(6, -3).to_json()
INV = Poly(["-2/3", "1/3"]).to_json()          # (x - 2)/3
DIAG_SQ = [{"misconceptionId": "MISC.FUNC.COMP_SQUARE_NO_CROSS_TERM", "coefficients": [{"num": 9, "den": 1}, {"num": -12, "den": 1}, {"num": 4, "den": 1}]}]

EXPRESSION_INPUTS = [
    (QUAD, [], ["4x^2-12x+10", "(2x-3)^2+1", "10 - 12x + 4x²", "4x**2 - 12*x + 10", "(2x-3)(2x-3)+1",
               "(f o g)(x) = (2x-3)^2 + 1", "(f∘g)(x)=(2x-3)^2+1", "y = 4x^2 - 12x + 10", "2(2x^2 - 6x + 5)",
               "(8x^2 - 24x + 20)/2", "4·x^2 − 12·x + 10", "4X^2 - 12X + 10", "", "6x-3=0", "x^7", "(2x-3",
               "2t+1", "(x+5)/(x-1)", "x^-1", "4x-2", "4x^2-12x+9", "4x^2 - 12x + 10 + 0x", "4x^2-12x+10.0",
               "４x^2", "٤x^2", "4x^2 % 3", "1111111111111x", "4x^{2} - 12x + 10", "4x^(2)-12x+10",
               "-(-4x^2+12x-10)", "4x^2-12x+10 ", " 4 x ^ 2 - 12 x + 10", "4xx-12x+10", "4x*x-12x+10", "sqrt(x)"]),
    (QUAD, DIAG_SQ, ["4x^2-12x+9", "4x^2+9-12x", "(2x)^2 - 12x + 9", "4x^2-12x+10"]),
    (HALF, [], ["1/2x+9", "(x+18)/2", "x/2 + 9", "0.5x + 9", "9 + x/2", "0,5x + 9", "x/2+9/1", "(1/2)x + 9", "1/2*x+9", "2x+9", "x+9"]),
    (LIN, [], ["6x-3", "6x - 3", "-3+6x", "3(2x-1)", "3(2x - 1)", "6x-3=", "= 6x - 3", "6x-3-0", "6x+-3", "6*x-3", "6x - (3)"]),
    (INV, [], ["(x-2)/3", "x/3 - 2/3", "1/3x - 2/3", "(1/3)x - (2/3)", "f^-1(x) = (x-2)/3", "f^{-1}(x)=(x-2)/3", "f⁻¹(x) = (x-2)/3",
              "(x+2)/3", "x/3 - 2", "3x - 2", "1/(3x+2)", "(x-2)/(3)", "0.333x - 0.667"]),
]

RAY_X = {"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": True, "direction": "ge"}
RAY_X_LE = {"kind": "ray", "variable": "x", "endpoint": {"num": 5, "den": 2}, "inclusive": True, "direction": "le"}
RAY_Y = {"kind": "ray", "variable": "y", "endpoint": {"num": -4, "den": 1}, "inclusive": True, "direction": "ge"}
EXC = {"kind": "reals-except", "variable": "x", "points": [{"num": 3, "den": 1}]}
EXC_Y = {"kind": "reals-except", "variable": "y", "points": [{"num": 1, "den": 1}]}
BOUNDED = {"kind": "bounded", "variable": "y", "lo": {"num": -1, "den": 1}, "hi": {"num": 4, "den": 1}, "loInclusive": True, "hiInclusive": True}
REALS = {"kind": "reals"}
DIAG_STRICT = [{"misconceptionId": "MISC.FUNC.DOMAIN_STRICT_ENDPOINT", "canonical": dict(RAY_X, inclusive=False)}]

INTERVAL_INPUTS = [
    (RAY_X, [], ["x >= 2", "x>=2", "2 <= x", "x≥2", "x ⩾ 2", "[2, inf)", "[2,∞)", "[2, infinity)", "[2, oo)", "{x | x >= 2}",
                 "{x : x ≥ 2}", "{x ∈ ℝ | x ≥ 2}", "x=>2", "x <= 2", "x >= 3", "x > 2", "(2, inf)", "x != 2", "all real numbers",
                 "", "x = 2", "[5, 2]", "x >= 2 or x <= 1", "x >= 2 and x >= 3", "[2, inf]", "(-inf, 2)", "x >= two", "x ≥ 2 ≥ 1",
                 "y >= 2", "f(x) >= 2", "x >= 2.0", "x >= 4/2", "x >= ٢", "X >= 2", "x>=+2", "2=<x", "x ≥ 2, x ∈ ℝ"]),
    (RAY_X, DIAG_STRICT, ["x > 2", "(2, inf)", "x >= 2"]),
    (RAY_X_LE, [], ["x <= 2.5", "x <= 5/2", "(-inf, 5/2]", "(-inf, 2.5]", "x < 2.5", "x <= 2", "x >= 2.5", "5/2 >= x"]),
    (RAY_Y, [], ["y >= -4", "f(x) ≥ -4", "g(x)>=-4", "[-4, inf)", "-4 <= y", "x >= -4", "y > -4", "y >= 4", "y <= -4", "h(x) >= -4", "f(x)>=-4.0"]),
    (EXC, [], ["x != 3", "x =/= 3", "x ≠ 3", "x ∈ ℝ, x ≠ 3", "all real numbers except 3", "R \\ {3}", "ℝ∖{3}", "{x | x != 3}",
               "x != -3", "x != 3, 5", "x != 0", "x > 3", "all real numbers", "y != 3", "x in R, x != 3", "x!=3andx!=3", "{x ∈ R : x ≠ 3}"]),
    (EXC_Y, [], ["y != 1", "f(x) ≠ 1", "y ≠ 1", "x != 1", "y != 0", "R \\ {1}", "all real numbers except 1"]),
    (BOUNDED, [], ["-1 <= y <= 4", "4 >= y >= -1", "[-1, 4]", "y >= -1 and y <= 4", "y <= 4 and y >= -1", "{y | -1 <= y <= 4}", "-1 < y <= 4",
                   "(-1, 4)", "-1 <= y <= 5", "y >= -1", "-1 <= x <= 4", "[-1,4)", "-1<=f(x)<=4", "y >= -1, y <= 4"]),
    (REALS, [], ["all real numbers", "all reals", "R", "ℝ", "x ∈ ℝ", "(-inf, inf)", "(-∞, ∞)", "y in R", "the set of all real numbers",
                 "x >= 2", "x != 3", "real numbers", "reals", "{x | x in R}", "{x ∈ R}", "x", "any"]),
]


def build() -> None:
    expression = []
    for canonical, diagnostics, inputs in EXPRESSION_INPUTS:
        for s in inputs:
            expression.append({"input": s, "canonical": canonical, "diagnostics": diagnostics, "expected": check_expression(s, canonical, diagnostics)})
    interval = []
    for canonical, diagnostics, inputs in INTERVAL_INPUTS:
        for s in inputs:
            interval.append({"input": s, "canonical": canonical, "diagnostics": diagnostics, "expected": check_interval(s, canonical, diagnostics)})
    corpus = {"note": "Cross-engine grading corpus: codes assigned by the Python oracle; the TypeScript checkers must agree exactly.",
              "expression": expression, "interval": interval}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(corpus, fh, indent=1, ensure_ascii=False)
    codes_e = {}
    for e in expression:
        codes_e[e["expected"]["code"]] = codes_e.get(e["expected"]["code"], 0) + 1
    codes_i = {}
    for e in interval:
        codes_i[e["expected"]["code"]] = codes_i.get(e["expected"]["code"], 0) + 1
    print(f"corpus: {len(expression)} expression cases {codes_e}; {len(interval)} interval cases {codes_i}")


if __name__ == "__main__":
    build()
