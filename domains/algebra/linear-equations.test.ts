/**
 * Linear-equations generator tests (Node built-in test runner) — v1.0.1.
 *
 * Byte-for-byte parity with the Python oracle (golden + 300-entry fixture),
 * validator pass on a property sweep, reproducibility, interaction/answer-type
 * consistency, legacy back-compatibility, placeholder-free student feedback, the
 * positive-coefficient strategy, and difficulty-band coverage per task.
 *
 * Run:  node --test domains/algebra/linear-equations.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  generate, validate, serialize, solve, distractorFeedback, TASKS, type Config, type Params,
} from "./linear-equations.ts";
import { rat } from "../../core/exact-math/rational.ts";
import type { Json } from "../../core/serialization/canonical.ts";

const goldenPath = fileURLToPath(new URL("../../oracle/golden/linear_equations.golden.json", import.meta.url));
const parityPath = fileURLToPath(new URL("../../oracle/golden/linear_equations.parity.json", import.meta.url));
const PLACEHOLDER = /(?<![A-Za-z])[pqrtk](?![A-Za-z])/;

test("byte-for-byte parity with the oracle golden vectors", () => {
  const golden = JSON.parse(readFileSync(goldenPath, "utf8")) as Array<{ seed: number; serialized: string; validation: string }>;
  for (const g of golden) {
    assert.equal(serialize(generate(g.seed, { interactionType: "multiple-choice" })), g.serialized, `golden seed ${g.seed}`);
    assert.equal(validate(generate(g.seed, { interactionType: "multiple-choice" })).status, "pass");
    assert.equal(g.validation, "pass");
  }
});

test("byte-for-byte parity with the 300-entry oracle parity fixture", () => {
  const parity = JSON.parse(readFileSync(parityPath, "utf8")) as Array<{ seed: number; mode: string; serialized: string }>;
  assert.ok(parity.length >= 300);
  for (const p of parity) {
    const cfg: Config = { interactionType: p.mode as "free-response" | "multiple-choice" };
    assert.equal(serialize(generate(p.seed, cfg)), p.serialized, `${p.mode} seed ${p.seed}`);
  }
});

test("validator passes across a property sweep (both interaction types) and is reproducible", () => {
  for (let s = 1; s <= 400; s++) {
    for (const mode of ["free-response", "multiple-choice"] as const) {
      const item = generate(s, { interactionType: mode });
      assert.equal(validate(item).status, "pass", `seed ${s} ${mode}`);
      assert.equal(serialize(generate(s, { interactionType: mode })), serialize(item), `repro ${s} ${mode}`);
    }
  }
});

test("legacy answerType is back-compatible and conflicts are rejected", () => {
  for (let s = 1; s <= 200; s++) {
    assert.equal(serialize(generate(s, { answerType: "integer" })), serialize(generate(s, { interactionType: "free-response" })), `seed ${s} FR`);
    assert.equal(serialize(generate(s, { answerType: "multiple-choice" })), serialize(generate(s, { interactionType: "multiple-choice" })), `seed ${s} MC`);
  }
  assert.throws(() => generate(7, { interactionType: "free-response", answerType: "multiple-choice" } as Config));
});

test("interaction type and canonical answer type are consistent", () => {
  for (let s = 1; s <= 300; s++) {
    for (const mode of ["free-response", "multiple-choice"] as const) {
      const item = generate(s, { interactionType: mode });
      assert.equal(item["interactionType"], mode);
      const a = item["answer"] as { type: string; canonical: { den: number } };
      assert.ok(a.type === "integer" || a.type === "exact-rational", `answer type ${a.type}`);
      if (a.type === "integer") assert.equal(a.canonical.den, 1);
    }
  }
});

test("one_step_add is integer-only (never exact-rational)", () => {
  for (let s = 1; s <= 600; s++) {
    const item = generate(s, { task: "one_step_add", interactionType: "free-response" });
    assert.equal((item["answer"] as { type: string }).type, "integer", `seed ${s}`);
  }
});

test("student-facing distractor feedback and rationale contain no internal placeholders", () => {
  for (let s = 1; s <= 600; s++) {
    const item = generate(s, { interactionType: "multiple-choice" });
    for (const fb of distractorFeedback(item)) {
      assert.ok(fb.length > 0, "feedback present");
      assert.ok(!PLACEHOLDER.test(fb), `placeholder in feedback: "${fb}"`);
    }
    for (const d of item["distractors"] as Array<{ rationale: string }>) {
      assert.ok(!PLACEHOLDER.test(d.rationale), `placeholder in rationale: "${d.rationale}"`);
    }
  }
});

test("variables-both-sides collect to a positive coefficient", () => {
  // 4x + 3 = 5x - 2  -> collect on the right, never '-x = -5'
  const p = { task: "both_sides", a: { num: 4, den: 1 }, b: { num: 3, den: 1 }, c: { num: 5, den: 1 }, d: { num: -2, den: 1 } } as unknown as Params;
  const item = { params: p } as unknown as Record<string, Json>;
  const sol = (generate(7, { task: "both_sides", interactionType: "free-response" })["solution"] as { steps: Array<{ intermediateResult?: string }> });
  void item;
  // No solution step should isolate a NEGATIVE unit coefficient like '-x ='.
  for (let s = 1; s <= 400; s++) {
    const steps = (generate(s, { task: "both_sides", interactionType: "free-response" })["solution"] as { steps: Array<{ intermediateResult?: string }> }).steps;
    for (const st of steps) assert.ok(!/(^|=\s*)-x\s*=/.test(st.intermediateResult ?? ""), `seed ${s}: negative unit coefficient`);
  }
  void sol;
  assert.ok(solve(p).equals(rat(5)));
});

test("difficulty bands cover each task's approved range", () => {
  const bands: Record<string, Set<number>> = {};
  for (const t of TASKS) bands[t] = new Set<number>();
  for (let s = 1; s <= 6000; s++) {
    const item = generate(s, { interactionType: "free-response" });
    bands[(item["params"] as { task: string }).task]!.add((item["difficulty"] as { overallBand: number }).overallBand);
  }
  const expected: Record<string, number[]> = {
    one_step_add: [1, 2], one_step_mul: [1, 2], two_step: [2, 3], both_sides: [3, 4], brackets: [3, 4, 5],
  };
  for (const t of TASKS) for (const b of expected[t]!) assert.ok(bands[t]!.has(b), `task ${t} should produce band ${b} (got ${[...bands[t]!].sort()})`);
});

test("every task is exercised", () => {
  const seen = new Set<string>();
  for (let s = 1; s <= 600; s++) seen.add((generate(s, { interactionType: "free-response" })["params"] as { task: string }).task);
  for (const t of TASKS) assert.ok(seen.has(t), `task ${t} appears`);
});

test("explicit task selection works for all five tasks", () => {
  for (const t of TASKS) {
    const item = generate(7, { task: t, interactionType: "multiple-choice" });
    assert.equal((item["params"] as { task: string }).task, t);
    assert.equal(validate(item).status, "pass");
    assert.equal((item["options"] as unknown[]).length, 4);
  }
});

test("validator catches a tampered answer", () => {
  const item = generate(3, { interactionType: "multiple-choice" }) as Record<string, Json>;
  (item["answer"] as { canonical: { num: number } }).canonical.num += 1;
  assert.equal(validate(item).status, "fail");
});

test("MC distractors are three distinct, formula-backed wrong values", () => {
  for (let s = 1; s <= 200; s++) {
    const options = generate(s, { interactionType: "multiple-choice" })["options"] as Array<{ display: string; correct: boolean }>;
    assert.equal(options.length, 4);
    assert.equal(options.filter((o) => o.correct).length, 1);
    const wrong = options.filter((o) => !o.correct).map((o) => o.display);
    assert.equal(new Set(wrong).size, 3, `seed ${s} distinct distractors`);
  }
});

test("solve rejects a non-unique equation and returns exact rationals", () => {
  const nonUnique = { task: "both_sides", a: { num: 2, den: 1 }, b: { num: 1, den: 1 }, c: { num: 2, den: 1 }, d: { num: 5, den: 1 } } as unknown as Params;
  assert.throws(() => solve(nonUnique));
  const rational = { task: "one_step_mul", a: { num: 3, den: 1 }, c: { num: 2, den: 1 } } as unknown as Params;
  assert.ok(solve(rational).equals(rat(2, 3)));
});
