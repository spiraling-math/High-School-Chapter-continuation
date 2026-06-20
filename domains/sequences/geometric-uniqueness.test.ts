/**
 * Uniqueness-validator edge-case tests (Node built-in test runner).
 * Run:  node --test domains/sequences/geometric-uniqueness.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { Rational, rat } from "../../core/exact-math/rational.ts";
import { realRatioSolutionCount, realRatioSolutions, rationalRoot, termIndexSolutions } from "./geometric-uniqueness.ts";

test("find_r: odd exponent gives exactly one real ratio", () => {
  assert.equal(realRatioSolutionCount(rat(8), 3), 1);
  assert.ok(rationalRoot(rat(8), 3)!.equals(rat(2)));
  assert.ok(rationalRoot(rat(-8), 3)!.equals(rat(-2)));   // negative quotient, odd
  assert.ok(rationalRoot(rat(1, 8), 3)!.equals(rat(1, 2))); // fractional ratio
});

test("find_r: even exponent can give two real ratios (or none)", () => {
  assert.equal(realRatioSolutionCount(rat(9), 2), 2);
  const two = realRatioSolutions(1, rat(9), 3); // u1=1, value=9, k=3 -> m=2
  assert.equal(two.length, 2);
  assert.ok(two.some((r) => r.equals(rat(3))) && two.some((r) => r.equals(rat(-3))));
  assert.equal(realRatioSolutionCount(rat(-4), 2), 0); // no real solution
  assert.deepEqual(realRatioSolutions(1, rat(-4), 3), []);
});

test("find_r: q = 0 -> r = 0 (single)", () => {
  assert.equal(realRatioSolutionCount(rat(0), 2), 1);
  assert.ok(realRatioSolutions(5, rat(0), 4)[0]!.equals(rat(0)));
});

test("term-index: well-posed ratios give exactly one index", () => {
  assert.deepEqual(termIndexSolutions(3, rat(2), rat(24)), [4]);   // 3*2^3 = 24
  assert.deepEqual(termIndexSolutions(8, rat(1, 2), rat(1)), [4]); // 8*(1/2)^3 = 1
  assert.deepEqual(termIndexSolutions(2, rat(-3), rat(-54)), [4]); // 2*(-3)^3 = -54
});

test("term-index: degenerate ratios r in {0,1,-1} are NOT well-posed", () => {
  // r = 1: every term equals u1 -> many indices
  assert.ok(termIndexSolutions(5, rat(1), rat(5)).length > 1);
  // r = -1: u1 appears at all odd indices -> many
  assert.ok(termIndexSolutions(5, rat(-1), rat(5)).length > 1);
  // r = 0: 0 appears at every index >= 2 -> many
  assert.ok(termIndexSolutions(7, rat(0), rat(0)).length > 1);
});

void Rational;
