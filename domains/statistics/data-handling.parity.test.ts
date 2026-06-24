/**
 * Cross-language byte-parity gate for gen.stats.data-handling v1.0.0.
 * The TypeScript mirror must reproduce the Python oracle's serialized output exactly,
 * for the golden seeds (19 entries) and the 300-entry parity fixture.
 *
 * Run:  node --test domains/statistics/data-handling.parity.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { generate, serialize, validate } from "./data-handling.ts";

const root = fileURLToPath(new URL("../../", import.meta.url));
const golden = JSON.parse(readFileSync(root + "oracle/golden/data_handling.golden.json", "utf8"));
const parity = JSON.parse(readFileSync(root + "oracle/golden/data_handling.parity.json", "utf8"));

test("golden vectors match the Python oracle byte-for-byte (and validation status agrees)", () => {
  for (const g of golden) {
    const item = generate(g.seed, g.config);
    const got = serialize(item);
    assert.equal(got, g.serialized, `golden seed ${g.seed} ${JSON.stringify(g.config)}`);
    assert.equal(validate(item).status, g.validation, `golden validation seed ${g.seed} ${JSON.stringify(g.config)}`);
  }
});

test("parity fixture (300 entries) matches the Python oracle byte-for-byte", () => {
  let mismatches = 0;
  let firstMismatch = "";
  for (const e of parity) {
    const got = serialize(generate(e.seed, { interactionType: e.mode }));
    if (got !== e.serialized) {
      mismatches++;
      if (!firstMismatch) {
        let i = 0;
        while (i < Math.min(got.length, e.serialized.length) && got[i] === e.serialized[i]) i++;
        firstMismatch = `seed ${e.seed} ${e.mode} @${i}: TS …${got.slice(Math.max(0, i - 30), i + 30)}…  vs  PY …${e.serialized.slice(Math.max(0, i - 30), i + 30)}…`;
      }
    }
  }
  assert.equal(mismatches, 0, `${mismatches}/${parity.length} parity mismatches. First: ${firstMismatch}`);
});
