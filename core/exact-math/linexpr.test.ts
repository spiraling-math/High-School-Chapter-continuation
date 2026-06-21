/**
 * LinExpr tests (Node built-in test runner).
 * Run:  node --test core/exact-math/linexpr.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { rat } from "./rational.ts";
import { LinExpr, lin, normalize, solveLinear } from "./linexpr.ts";

test("add/sub/scale/eval over exact rationals", () => {
  const e = lin(2, 3).add(lin(1, -5)); // 3x - 2
  assert.ok(e.a.equals(rat(3)) && e.b.equals(rat(-2)));
  const k = lin(2, 4).scale(rat(3)); // 6x + 12
  assert.ok(k.a.equals(rat(6)) && k.b.equals(rat(12)));
  assert.ok(lin(2, 1).eval(rat(3)).equals(rat(7))); // 2*3+1
  assert.ok(lin(1, 2).sub(lin(0, 5)).b.equals(rat(-3)));
});

test("solveLinear returns the exact (possibly rational) root", () => {
  // 2x + 3 = 11  -> x = 4
  assert.ok(solveLinear(lin(2, 3), lin(0, 11)).equals(rat(4)));
  // 3x = 2 -> x = 2/3
  assert.ok(solveLinear(lin(3, 0), lin(0, 2)).equals(rat(2, 3)));
  // 5x - 3 = 2x + 9 -> x = 4
  assert.ok(solveLinear(lin(5, -3), lin(2, 9)).equals(rat(4)));
  // x + 4 = 4 -> x = 0
  assert.ok(solveLinear(lin(1, 4), lin(0, 4)).equals(rat(0)));
});

test("normalize reduces to A·x + B = 0", () => {
  const { A, B } = normalize(lin(5, -3), lin(2, 9)); // 3x - 12 = 0
  assert.ok(A.equals(rat(3)) && B.equals(rat(-12)));
});

test("solveLinear rejects A = 0 (no unique solution)", () => {
  assert.throws(() => solveLinear(lin(2, 3), lin(2, 9))); // 0x - 6 = 0 (no solution)
  assert.throws(() => solveLinear(lin(2, 3), lin(2, 3))); // 0 = 0 (infinitely many)
});

test("bracket expansion via scale: 3(2x - 1) = 6x - 3", () => {
  const expanded = LinExpr.coef(2, -1).scale(rat(3));
  assert.ok(expanded.a.equals(rat(6)) && expanded.b.equals(rat(-3)));
});
