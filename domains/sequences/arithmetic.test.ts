/**
 * Arithmetic-sequences generator parity tests (Node built-in test runner).
 *
 * The decisive test asserts the TypeScript generator's canonical serialization
 * is byte-for-byte identical to the Python oracle's committed golden vectors —
 * proving the two independent implementations agree (Principle 4).
 *
 * Run:  node --test domains/sequences/arithmetic.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { generate, serialize, solve, ALL_TASKS } from "./arithmetic.ts";

const here = dirname(fileURLToPath(import.meta.url));
const golden: Array<{ seed: number; serialized: string; validation: string }> = JSON.parse(
  readFileSync(join(here, "../../oracle/golden/arithmetic_sequences.golden.json"), "utf8"),
);

test("byte-for-byte parity with the Python oracle golden vectors", () => {
  for (const g of golden) {
    const item = generate(g.seed, { answerType: "multiple-choice" });
    assert.equal(serialize(item), g.serialized, `serialization mismatch at seed ${g.seed}`);
  }
});

test("known closed-form values", () => {
  assert.equal(solve({ task: "nth_term", a1: 4, d: 3, n: 10 }), 31);
  assert.equal(solve({ task: "nth_term", a1: 20, d: -3, n: 7 }), 2);
  assert.equal(solve({ task: "sum_n", a1: 1, d: 2, n: 10 }), 100);
  assert.equal(solve({ task: "find_d", a1: 4, d: 3, n: 10 }), 3);
  assert.equal(solve({ task: "find_n_for_value", a1: 4, d: 3, n: 10 }), 10);
});

test("is reproducible: same seed -> identical serialization", () => {
  for (const s of [1, 42, 123456789, 2147483647, 555]) {
    assert.equal(
      serialize(generate(s, { answerType: "multiple-choice" })),
      serialize(generate(s, { answerType: "multiple-choice" })),
    );
  }
});

test("rejects invalid configuration", () => {
  assert.throws(() => generate(1, { task: "bogus" as never }));
  assert.throws(() => generate(1, { task: "find_d", answerType: "multiple-choice" }));
});

test("multiple-choice items have exactly one correct option and 3 distinct distractors", () => {
  for (let s = 1; s <= 2000; s++) {
    const item = generate(s, { answerType: "multiple-choice" });
    const options = item["options"] as Array<{ value: number; correct: boolean }>;
    const answer = (item["answer"] as { canonical: number }).canonical;
    const correct = options.filter((o) => o.correct);
    const wrong = options.filter((o) => !o.correct).map((o) => o.value);
    assert.equal(correct.length, 1, `seed ${s}`);
    assert.equal(correct[0]!.value, answer, `seed ${s}`);
    assert.equal(new Set(wrong).size, wrong.length, `dup distractor at seed ${s}`);
    assert.ok(!wrong.includes(answer), `distractor==answer at seed ${s}`);
    assert.ok(wrong.length >= 3, `<3 distractors at seed ${s}`);
  }
});

test("every task type is reachable in integer mode", () => {
  const seen = new Set<string>();
  for (let s = 1; s <= 2000; s++) {
    seen.add((generate(s, { answerType: "integer" })["params"] as { task: string }).task);
  }
  assert.deepEqual([...seen].sort(), [...ALL_TASKS].sort());
});
