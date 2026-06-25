/**
 * Cross-language byte-parity gate for gen.measurement.mensuration v1.0.0.
 * The TypeScript mirror must reproduce the Python oracle's serialized output exactly, for the
 * golden vectors (12 entries) and the 304-entry task-pinned free-response parity fixture, and the
 * validation status must agree.
 *
 * Run:  node --test domains/measurement/mensuration.parity.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { generate, serialize, validate } from "./mensuration.ts";

const root = fileURLToPath(new URL("../../", import.meta.url));
const golden = JSON.parse(readFileSync(root + "oracle/golden/mensuration.golden.json", "utf8"));
const parity = JSON.parse(readFileSync(root + "oracle/golden/mensuration.parity.json", "utf8"));

test("golden vectors match the Python oracle byte-for-byte (and validation status agrees)", () => {
  for (const g of golden) {
    const item = generate(g.seed, g.task
      ? { interactionType: "free-response", task: g.task }
      : { interactionType: "free-response" });
    assert.equal(serialize(item), g.serialized, `golden seed ${g.seed} task ${g.task}`);
    assert.equal(validate(item).status, g.validation, `golden validation seed ${g.seed} task ${g.task}`);
  }
});

test("task-pinned parity fixture (304 entries) matches the Python oracle byte-for-byte", () => {
  let mismatches = 0;
  let firstMismatch = "";
  for (const e of parity) {
    const got = serialize(generate(e.seed, { interactionType: e.mode, task: e.task }));
    if (got !== e.serialized) {
      mismatches++;
      if (!firstMismatch) {
        let i = 0;
        while (i < Math.min(got.length, e.serialized.length) && got[i] === e.serialized[i]) i++;
        firstMismatch = `seed ${e.seed} ${e.task} @${i}: TS …${got.slice(Math.max(0, i - 40), i + 30)}…  vs  PY …${e.serialized.slice(Math.max(0, i - 40), i + 30)}…`;
      }
    }
  }
  assert.equal(mismatches, 0, `${mismatches}/${parity.length} parity mismatches. First: ${firstMismatch}`);
});
