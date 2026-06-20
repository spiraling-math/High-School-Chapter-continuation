/**
 * Exact-rational checker tests (Node built-in test runner).
 * Run:  node --test core/answer-checking/rational-checker.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { checkExactRational, terminates } from "./rational-checker.ts";

const C = { num: 15, den: 4 }; // 15/4 = 3.75

test("accepts the reduced fraction and any equivalent fraction", () => {
  assert.ok(checkExactRational("15/4", C));
  assert.ok(checkExactRational("30/8", C));
  assert.ok(checkExactRational("-30/-8", C));
  assert.ok(!checkExactRational("16/4", C));
});

test("decimal accepted only when permitted", () => {
  assert.ok(!checkExactRational("3.75", C)); // default: decimal off
  assert.ok(checkExactRational("3.75", C, { decimal: true }));
  assert.ok(!checkExactRational("3.7", C, { decimal: true }));
});

test("mixed-number accepted only when enabled", () => {
  assert.ok(!checkExactRational("3 3/4", C));
  assert.ok(checkExactRational("3 3/4", C, { mixed: true }));
  assert.ok(checkExactRational("-1 1/2", { num: -3, den: 2 }, { mixed: true }));
});

test("integers and negative rationals", () => {
  assert.ok(checkExactRational("12", { num: 12, den: 1 }));
  assert.ok(checkExactRational("12/1", { num: 12, den: 1 }));
  assert.ok(checkExactRational("-2/3", { num: -2, den: 3 }));
  assert.ok(checkExactRational("2/-3", { num: -2, den: 3 }));
  assert.ok(!checkExactRational("2/3", { num: -2, den: 3 }));
});

test("rejects malformed and zero-denominator input", () => {
  assert.ok(!checkExactRational("", C));
  assert.ok(!checkExactRational("abc", C));
  assert.ok(!checkExactRational("1/0", C));
});

test("terminates() detects terminating denominators", () => {
  assert.ok(terminates(4));   // 2^2
  assert.ok(terminates(20));  // 2^2 * 5
  assert.ok(!terminates(3));
  assert.ok(!terminates(9));
});
