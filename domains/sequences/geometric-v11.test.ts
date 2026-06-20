/**
 * Geometric v1.1.0 answer-type-model + validation tests (Node test runner).
 * Run:  node --test domains/sequences/geometric-v11.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { generate, validate } from "./geometric.ts";
import { checkExactRational } from "../../core/answer-checking/rational-checker.ts";

test("fractional answers are exact-rational, free-response; integers are integer-typed", () => {
  let foundFraction = false;
  for (let s = 1; s < 5000 && !foundFraction; s++) {
    const it = generate(s, { task: "nth_term", answerType: "integer" });
    const a = it["answer"] as { type: string; canonical: { den: number } };
    if (a.canonical.den !== 1) {
      assert.equal(a.type, "exact-rational");
      assert.equal(it["interactionType"], "free-response");
      foundFraction = true;
    }
  }
  assert.ok(foundFraction, "expected at least one fractional answer");

  const fn = generate(1, { task: "find_n_for_value", answerType: "integer" });
  const fa = fn["answer"] as { type: string; canonical: { den: number } };
  assert.equal(fa.type, "integer");
  assert.equal(fa.canonical.den, 1);
});

test("validator rejects an answer whose type contradicts its value", () => {
  const it = generate(1, { task: "nth_term", answerType: "integer" });
  (it["answer"] as { type: string }).type = "integer";
  (it["answer"] as { canonical: { num: number; den: number } }).canonical = { num: 3, den: 4 };
  const r = validate(it);
  assert.equal(r.status, "fail");
  assert.equal(r.checks.find((c) => c.name === "answer-type-consistency")?.result, "fail");
});

test("find_r items pass the real-ratio uniqueness check; find_n items pass term-index uniqueness", () => {
  let fr = 0, fn = 0;
  for (let s = 1; s <= 3000 && (fr < 5 || fn < 5); s++) {
    const it = generate(s, { answerType: "integer" });
    const task = (it["params"] as { task: string }).task;
    const r = validate(it);
    assert.equal(r.status, "pass", `seed ${s} ${task}`);
    if (task === "find_r") { fr++; assert.equal(r.checks.find((c) => c.name === "find_r-unique-real-ratio")?.result, "pass"); }
    if (task === "find_n_for_value") { fn++; assert.equal(r.checks.find((c) => c.name === "term-index-unique")?.result, "pass"); }
  }
  assert.ok(fr >= 5 && fn >= 5, `coverage fr=${fr} fn=${fn}`);
});

test("exact-rational checker accepts equivalent forms of a generated answer", () => {
  const it = generate(7, { task: "sum_infinite", answerType: "integer" });
  const a = it["answer"] as { canonical: { num: number; den: number }; display: string; accepts: { decimal: boolean } };
  // The reduced form and an equivalent fraction (doubled) both check correct.
  assert.ok(checkExactRational(a.display, a.canonical));
  assert.ok(checkExactRational(`${a.canonical.num * 2}/${a.canonical.den * 2}`, a.canonical));
  // A different value is rejected.
  assert.ok(!checkExactRational(`${a.canonical.num + 1}/${a.canonical.den}`, a.canonical));
});
