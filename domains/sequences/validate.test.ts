/**
 * Validator tests (Node built-in test runner).
 *
 * Mirrors the oracle's validator tests: valid items pass, corrupted items are
 * caught, and a property sweep confirms every generated item validates.
 * Also cross-checks against the oracle's recorded golden validation status.
 *
 * Run:  node --test domains/sequences/validate.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { generate } from "./arithmetic.ts";
import { validate } from "./validate.ts";
import type { Json } from "../../core/serialization/canonical.ts";

const here = dirname(fileURLToPath(import.meta.url));
const golden: Array<{ seed: number; serialized: string; validation: string }> = JSON.parse(
  readFileSync(join(here, "../../oracle/golden/arithmetic_sequences.golden.json"), "utf8"),
);

test("validates generated items (matches oracle golden validation status)", () => {
  for (const g of golden) {
    const item = JSON.parse(g.serialized) as Record<string, Json>;
    const result = validate(item);
    assert.equal(result.status, "pass", `seed ${g.seed}`);
    assert.equal(result.status, g.validation, `oracle disagreement at seed ${g.seed}`);
  }
});

test("catches a corrupted answer", () => {
  const item = generate(1, { answerType: "integer" });
  (item["answer"] as { canonical: number }).canonical += 1;
  const result = validate(item);
  assert.equal(result.status, "fail");
  assert.equal(result.checks.find((c) => c.name === "arith-iterative-agreement")?.result, "fail");
});

test("catches an out-of-domain parameter (d = 0)", () => {
  const item = generate(1, { answerType: "integer" });
  (item["params"] as { d: number }).d = 0;
  const result = validate(item);
  assert.equal(result.status, "fail");
  assert.equal(result.checks.find((c) => c.name === "params-in-domain")?.result, "fail");
});

test("property sweep: every generated item validates (2000 seeds x 2 modes)", () => {
  for (let s = 1; s <= 2000; s++) {
    for (const mode of ["integer", "multiple-choice"] as const) {
      const item = generate(s, { answerType: mode });
      const result = validate(item);
      assert.equal(result.status, "pass", `seed ${s} (${mode}): ${JSON.stringify(result.checks.filter((c) => c.result === "fail"))}`);
    }
  }
});
