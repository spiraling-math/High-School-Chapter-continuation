/**
 * Reusable coordinate answer-checker tests. Run: node --test core/answer-checking/coordinate-checkers.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { checkOrderedPair, checkLinearEquation } from "./coordinate-checkers.ts";

test("ordered-pair: exact, order-sensitive, accepts integer + fractional components", () => {
  assert.ok(checkOrderedPair("(3, -2)", { x: { num: 3, den: 1 }, y: { num: -2, den: 1 } }));
  assert.ok(checkOrderedPair("( 3 , -2 )", { x: { num: 3, den: 1 }, y: { num: -2, den: 1 } }));
  assert.ok(checkOrderedPair("(-1, 9/2)", { x: { num: -1, den: 1 }, y: { num: 9, den: 2 } }));
  // order matters: (a, b) != (b, a)
  assert.ok(!checkOrderedPair("(-2, 3)", { x: { num: 3, den: 1 }, y: { num: -2, den: 1 } }));
  // unreduced fraction normalises to the canonical
  assert.ok(checkOrderedPair("(2/4, 3)", { x: { num: 1, den: 2 }, y: { num: 3, den: 1 } }));
  assert.ok(!checkOrderedPair("3, -2", { x: { num: 3, den: 1 }, y: { num: -2, den: 1 } }));
});

test("linear equation: accepts equivalent y = mx + c forms, rejects wrong/vertical", () => {
  const c = { m: { num: 2, den: 1 }, c: { num: -3, den: 1 } }; // y = 2x - 3
  assert.ok(checkLinearEquation("y = 2x - 3", c));
  assert.ok(checkLinearEquation("y=2x-3", c));
  assert.ok(checkLinearEquation("y = -3 + 2x", c)); // reordered
  assert.ok(!checkLinearEquation("y = 2x + 3", c)); // wrong intercept sign
  assert.ok(!checkLinearEquation("y = 3x - 3", c)); // wrong gradient

  const unit = { m: { num: 1, den: 1 }, c: { num: 5, den: 1 } }; // y = x + 5
  assert.ok(checkLinearEquation("y = x + 5", unit));
  assert.ok(checkLinearEquation("y = 5 + x", unit));

  const neg = { m: { num: -1, den: 1 }, c: { num: 0, den: 1 } }; // y = -x
  assert.ok(checkLinearEquation("y = -x", neg));

  const frac = { m: { num: 3, den: 2 }, c: { num: 1, den: 1 } }; // y = (3/2)x + 1
  assert.ok(checkLinearEquation("y = (3/2)x + 1", frac));
  assert.ok(checkLinearEquation("y = 3/2x + 1", frac));

  const constLine = { m: { num: 0, den: 1 }, c: { num: 4, den: 1 } }; // y = 4
  assert.ok(checkLinearEquation("y = 4", constLine));

  assert.ok(!checkLinearEquation("x = 3", { m: { num: 0, den: 1 }, c: { num: 3, den: 1 } })); // vertical rejected
});
