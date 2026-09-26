/**
 * Expression-checker tests (grammar, codes, equivalence). Run:  node --test core/answer-checking/expression-checker.test.ts
 * The Python mirror is held to the same pins in oracle/tests/test_functions_checkers.py, and both engines are
 * pinned to one corpus by functions-checker-corpus.test.ts.
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { checkExpression, parseExpression, normalizeExpression } from "./expression-checker.ts";
import { Poly } from "../exact-math/polynomial.ts";

const CANON = Poly.quadratic(4, -12, 10).toJson();

test("accepts every equivalent written form of 4x^2 - 12x + 10", () => {
  for (const s of ["4x^2-12x+10", "(2x-3)^2+1", "10 - 12x + 4x²", "4x**2 - 12*x + 10", "(2x-3)(2x-3)+1",
    "(f o g)(x) = (2x-3)^2 + 1", "y = 4x^2 - 12x + 10", "2(2x^2 - 6x + 5)", "(8x^2 - 24x + 20)/2", "4·x^2 − 12·x + 10"]) {
    assert.deepEqual(checkExpression(s, CANON), { code: "correct" }, s);
  }
});

test("coefficient-literal convention: 1/2x is (1/2)x; x/2 divides; decimals are exact", () => {
  const half = Poly.linear(new Poly([0]).coef(0).add(Poly.const(1).coef(0)).div(Poly.const(2).coef(0)), 9).toJson(); // (1/2)x + 9
  for (const s of ["1/2x+9", "(x+18)/2", "x/2 + 9", "0.5x + 9", "9 + x/2"]) assert.deepEqual(checkExpression(s, half), { code: "correct" }, s);
});

test("result codes", () => {
  assert.equal(checkExpression("", CANON).code, "unparseable");
  assert.equal(checkExpression("6x-3=0", CANON).code, "unparseable");
  assert.equal(checkExpression("x^7", CANON).code, "unparseable");
  assert.equal(checkExpression("(2x-3", CANON).code, "unparseable");
  assert.equal(checkExpression("2t+1", CANON).code, "wrong-variable");
  assert.equal(checkExpression("(x+5)/(x-1)", CANON).code, "not-polynomial");
  assert.equal(checkExpression("x^-1", CANON).code, "not-polynomial");
  assert.equal(checkExpression("4x-2", CANON).code, "wrong-degree");
  assert.equal(checkExpression("4x^2-12x+9", CANON).code, "wrong-coefficients");
  assert.deepEqual(checkExpression("4x^2-12x+9", CANON, [{ misconceptionId: "MISC.FUNC.COMP_SQUARE_NO_CROSS_TERM", coefficients: [{ num: 9, den: 1 }, { num: -12, den: 1 }, { num: 4, den: 1 }] }]),
    { code: "misconception", misconceptionId: "MISC.FUNC.COMP_SQUARE_NO_CROSS_TERM" });
});

test("unary minus and implicit multiplication", () => {
  assert.equal(parseExpression("-x^2").poly!.display(), "-x^2");
  assert.equal(parseExpression("--x").poly!.display(), "x");
  assert.equal(parseExpression("3(x+1)(x-2)").poly!.display(), "3x^2 - 3x - 6");
  assert.equal(parseExpression("x(x-4)").poly!.display(), "x^2 - 4x");
  assert.equal(parseExpression("-2^2").poly!.display(), "-4");
  assert.equal(parseExpression("2x·3").poly!.display(), "6x");
});

test("ASCII anchoring: non-ASCII digits and stray symbols are rejected, length is capped", () => {
  assert.equal(checkExpression("４x^2", CANON).code, "unparseable");
  assert.equal(checkExpression("٤x^2", CANON).code, "unparseable");
  assert.equal(checkExpression("4x^2 % 3", CANON).code, "unparseable");
  assert.equal(normalizeExpression("x".repeat(201)), null);
  assert.equal(checkExpression("1".repeat(13) + "x", CANON).code, "unparseable");
});
