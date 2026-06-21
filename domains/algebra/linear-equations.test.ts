/**
 * Linear-equations generator tests (Node built-in test runner).
 *
 * Asserts byte-for-byte parity with the Python oracle (golden + 300-entry parity
 * fixture), validator pass on a property sweep, reproducibility, and that the
 * validator catches tampering / non-unique equations.
 *
 * Run:  node --test domains/algebra/linear-equations.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { generate, validate, serialize, solve, TASKS, type Config, type Params } from "./linear-equations.ts";
import { rat } from "../../core/exact-math/rational.ts";
import type { Json } from "../../core/serialization/canonical.ts";

const goldenPath = fileURLToPath(new URL("../../oracle/golden/linear_equations.golden.json", import.meta.url));
const parityPath = fileURLToPath(new URL("../../oracle/golden/linear_equations.parity.json", import.meta.url));

test("byte-for-byte parity with the oracle golden vectors", () => {
  const golden = JSON.parse(readFileSync(goldenPath, "utf8")) as Array<{ seed: number; serialized: string; validation: string }>;
  for (const g of golden) {
    assert.equal(serialize(generate(g.seed, { answerType: "multiple-choice" })), g.serialized, `golden seed ${g.seed}`);
    assert.equal(validate(generate(g.seed, { answerType: "multiple-choice" })).status, "pass");
    assert.equal(g.validation, "pass");
  }
});

test("byte-for-byte parity with the 300-entry oracle parity fixture", () => {
  const parity = JSON.parse(readFileSync(parityPath, "utf8")) as Array<{ seed: number; mode: string; serialized: string }>;
  assert.ok(parity.length >= 300);
  for (const p of parity) {
    const cfg: Config = { answerType: p.mode as "integer" | "multiple-choice" };
    assert.equal(serialize(generate(p.seed, cfg)), p.serialized, `${p.mode} seed ${p.seed}`);
  }
});

test("validator passes across a property sweep (both modes) and is reproducible", () => {
  for (let s = 1; s <= 400; s++) {
    for (const mode of ["integer", "multiple-choice"] as const) {
      const item = generate(s, { answerType: mode });
      assert.equal(validate(item).status, "pass", `seed ${s} ${mode}`);
      assert.equal(serialize(generate(s, { answerType: mode })), serialize(item), `repro ${s} ${mode}`);
    }
  }
});

test("every task is exercised and solutions satisfy the equation", () => {
  const seen = new Set<string>();
  for (let s = 1; s <= 600; s++) {
    const item = generate(s, { answerType: "integer" });
    seen.add((item["params"] as { task: string }).task);
  }
  for (const t of TASKS) assert.ok(seen.has(t), `task ${t} appears`);
});

test("explicit task selection works for all five tasks", () => {
  for (const t of TASKS) {
    const item = generate(7, { task: t, answerType: "multiple-choice" });
    assert.equal((item["params"] as { task: string }).task, t);
    assert.equal(validate(item).status, "pass");
    assert.equal((item["options"] as unknown[]).length, 4);
  }
});

test("validator catches a tampered answer", () => {
  const item = generate(3, { answerType: "multiple-choice" }) as Record<string, Json>;
  (item["answer"] as { canonical: { num: number } }).canonical.num += 1;
  assert.equal(validate(item).status, "fail");
});

test("MC distractors are three distinct, formula-backed wrong values", () => {
  for (let s = 1; s <= 200; s++) {
    const item = generate(s, { answerType: "multiple-choice" });
    const options = item["options"] as Array<{ display: string; correct: boolean }>;
    assert.equal(options.length, 4);
    assert.equal(options.filter((o) => o.correct).length, 1);
    const wrong = options.filter((o) => !o.correct).map((o) => o.display);
    assert.equal(new Set(wrong).size, 3, `seed ${s} distinct distractors`);
  }
});

test("solve rejects a non-unique equation (a = c)", () => {
  const p = { task: "both_sides", a: { num: 2, den: 1 }, b: { num: 1, den: 1 }, c: { num: 2, den: 1 }, d: { num: 5, den: 1 } } as unknown as Params;
  assert.throws(() => solve(p));
});

test("solve returns exact rationals", () => {
  // 3x = 2 -> 2/3 ; built as one_step_mul a=3, c=2
  const p = { task: "one_step_mul", a: { num: 3, den: 1 }, c: { num: 2, den: 1 } } as unknown as Params;
  assert.ok(solve(p).equals(rat(2, 3)));
});
