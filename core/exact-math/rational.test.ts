/**
 * Exact Rational tests (Node built-in test runner).
 * Run:  node --test core/exact-math/rational.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { Rational, rat } from "./rational.ts";

test("reduces to lowest terms with positive denominator (matches Fraction)", () => {
  assert.deepEqual(rat(2, 4).toJSON(), { num: 1, den: 2 });
  assert.deepEqual(rat(-3, -6).toJSON(), { num: 1, den: 2 });
  assert.deepEqual(rat(5, -10).toJSON(), { num: -1, den: 2 });
  assert.deepEqual(rat(0, 7).toJSON(), { num: 0, den: 1 });
  assert.equal(rat(12, 1).toString(), "12");
  assert.equal(rat(3, 2).toString(), "3/2");
  assert.equal(rat(-1, 2).toString(), "-1/2");
});

test("arithmetic is exact", () => {
  assert.ok(rat(1, 2).add(rat(1, 3)).equals(rat(5, 6)));
  assert.ok(rat(1, 2).sub(rat(1, 3)).equals(rat(1, 6)));
  assert.ok(rat(2, 3).mul(rat(3, 4)).equals(rat(1, 2)));
  assert.ok(rat(1, 2).div(rat(2, 3)).equals(rat(3, 4)));
  assert.ok(rat(5).div(rat(1).sub(rat(1, 3))).equals(rat(15, 2))); // sum to infinity shape
});

test("integer powers", () => {
  assert.ok(rat(1, 2).pow(3).equals(rat(1, 8)));
  assert.ok(rat(-2).pow(3).equals(rat(-8)));
  assert.ok(rat(3).pow(0).equals(rat(1)));
});

test("helpers", () => {
  assert.ok(rat(4, 2).isInteger());
  assert.ok(!rat(3, 2).isInteger());
  assert.ok(rat(0).isZero());
  assert.equal(rat(-1, 2).cmpAbs(rat(1, 1)), -1); // |−1/2| < |1|
  assert.equal(rat(3, 2).cmpAbs(rat(1)), 1);
  assert.throws(() => rat(1, 0));
  assert.throws(() => rat(1).div(rat(0)));
});
