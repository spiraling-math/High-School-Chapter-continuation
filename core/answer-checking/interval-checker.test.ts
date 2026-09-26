/**
 * Interval (real-subset) checker tests. Run:  node --test core/answer-checking/interval-checker.test.ts
 * The Python mirror is held to the same pins in oracle/tests/test_functions_checkers.py.
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { checkInterval, parseInterval, intervalDisplay, intervalToJson, type IntervalJson } from "./interval-checker.ts";

const RAY_X: IntervalJson = { kind: "ray", variable: "x", endpoint: { num: 2, den: 1 }, inclusive: true, direction: "ge" };
const RAY_Y: IntervalJson = { kind: "ray", variable: "y", endpoint: { num: -4, den: 1 }, inclusive: true, direction: "ge" };
const EXC: IntervalJson = { kind: "reals-except", variable: "x", points: [{ num: 3, den: 1 }] };
const BOUNDED: IntervalJson = { kind: "bounded", variable: "y", lo: { num: -1, den: 1 }, hi: { num: 4, den: 1 }, loInclusive: true, hiInclusive: true };
const REALS: IntervalJson = { kind: "reals" };

test("every accepted form of x >= 2", () => {
  for (const s of ["x >= 2", "x>=2", "2 <= x", "x≥2", "x ⩾ 2", "[2, inf)", "[2,∞)", "[2, infinity)", "[2, oo)", "{x | x >= 2}", "{x : x ≥ 2}", "{x ∈ ℝ | x ≥ 2}", "x=>2"]) {
    assert.deepEqual(checkInterval(s, RAY_X), { code: "correct" }, s);
  }
});

test("ranges read y, f(x), g(x); a domain written in y is wrong-variable (and vice versa)", () => {
  for (const s of ["y >= -4", "f(x) ≥ -4", "g(x)>=-4", "[-4, inf)", "-4 <= y"]) assert.deepEqual(checkInterval(s, RAY_Y), { code: "correct" }, s);
  assert.equal(checkInterval("x >= -4", RAY_Y).code, "wrong-variable");
  assert.equal(checkInterval("y >= 2", RAY_X).code, "wrong-variable");
});

test("exclusions and the whole line", () => {
  for (const s of ["x != 3", "x =/= 3", "x ≠ 3", "x ∈ ℝ, x ≠ 3", "all real numbers except 3", "R \\ {3}", "ℝ∖{3}", "{x | x != 3}"]) {
    assert.deepEqual(checkInterval(s, EXC), { code: "correct" }, s);
  }
  for (const s of ["all real numbers", "all reals", "R", "ℝ", "x ∈ ℝ", "(-inf, inf)", "(-∞, ∞)", "y in R", "the set of all real numbers"]) {
    assert.deepEqual(checkInterval(s, REALS), { code: "correct" }, s);
  }
});

test("bounded intervals from chained inequalities, conjunctions and interval notation", () => {
  for (const s of ["-1 <= y <= 4", "4 >= y >= -1", "[-1, 4]", "y >= -1 and y <= 4", "y <= 4 and y >= -1", "{y | -1 <= y <= 4}"]) {
    assert.deepEqual(checkInterval(s, BOUNDED), { code: "correct" }, s);
  }
  assert.equal(checkInterval("-1 < y <= 4", BOUNDED).code, "wrong-inclusivity");
  assert.equal(checkInterval("(-1, 4)", BOUNDED).code, "wrong-inclusivity");
  assert.equal(checkInterval("-1 <= y <= 5", BOUNDED).code, "wrong-endpoint");
  assert.equal(checkInterval("y >= -1", BOUNDED).code, "wrong-kind");
});

test("ray diagnostics: direction, endpoint, inclusivity, kind, misconception, unparseable", () => {
  assert.equal(checkInterval("x <= 2", RAY_X).code, "wrong-direction");
  assert.equal(checkInterval("x >= 3", RAY_X).code, "wrong-endpoint");
  assert.equal(checkInterval("x > 2", RAY_X).code, "wrong-inclusivity");
  assert.equal(checkInterval("(2, inf)", RAY_X).code, "wrong-inclusivity");
  assert.equal(checkInterval("x != 2", RAY_X).code, "wrong-kind");
  assert.equal(checkInterval("all real numbers", RAY_X).code, "wrong-kind");
  assert.deepEqual(checkInterval("x > 2", RAY_X, [{ misconceptionId: "MISC.FUNC.DOMAIN_STRICT_ENDPOINT", canonical: { ...RAY_X, inclusive: false } }]),
    { code: "misconception", misconceptionId: "MISC.FUNC.DOMAIN_STRICT_ENDPOINT" });
  for (const s of ["", "x = 2", "[5, 2]", "x >= 2 or x <= 1", "x >= 2 and x >= 3", "[2, inf]", "(-inf, 2)", "x >= two", "x ≥ 2 ≥ 1"]) {
    assert.equal(checkInterval(s, RAY_X).code, s === "(-inf, 2)" ? "wrong-direction" : "unparseable", s);
  }
});

test("display strings (cross-language contract) and display → parse round trip", () => {
  const cases: Array<[IntervalJson, string]> = [
    [REALS, "all real numbers"], [RAY_X, "x >= 2"], [RAY_Y, "y >= -4"], [EXC, "x != 3"], [BOUNDED, "-1 <= y <= 4"],
    [{ kind: "ray", variable: "x", endpoint: { num: -5, den: 2 }, inclusive: false, direction: "le" }, "x < -5/2"],
    [{ kind: "reals-except", variable: "y", points: [{ num: 1, den: 1 }, { num: 3, den: 1 }] }, "y != 1, 3"],
  ];
  for (const [c, d] of cases) {
    assert.equal(intervalDisplay(c), d);
    assert.deepEqual(checkInterval(d, c), { code: "correct" }, `round trip ${d}`);
  }
  const parsed = parseInterval("x >= 1/2").interval!;
  assert.deepEqual(intervalToJson(parsed), { kind: "ray", variable: "x", endpoint: { num: 1, den: 2 }, inclusive: true, direction: "ge" });
});

test("decimal endpoints are exact rationals; ASCII digits only", () => {
  assert.equal(checkInterval("x <= 2.5", { kind: "ray", variable: "x", endpoint: { num: 5, den: 2 }, inclusive: true, direction: "le" }).code, "correct");
  assert.equal(checkInterval("x >= ٢", RAY_X).code, "unparseable");
});
