/**
 * Extended cross-language parity test (Node built-in test runner).
 *
 * Asserts the TypeScript generator reproduces the Python oracle's serialized
 * output byte-for-byte across many seeds in both modes — far beyond the four
 * curated golden seeds. Fixture: oracle/golden/arithmetic_sequences.parity.json
 *
 * Run:  node --test domains/sequences/parity.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { generate, serialize } from "./arithmetic.ts";

const here = dirname(fileURLToPath(import.meta.url));
const fixture: Array<{ seed: number; mode: "integer" | "multiple-choice"; serialized: string }> =
  JSON.parse(readFileSync(join(here, "../../oracle/golden/arithmetic_sequences.parity.json"), "utf8"));

test(`byte-for-byte parity across ${fixture.length} oracle fixture entries`, () => {
  let mismatches = 0;
  let firstMismatch = "";
  for (const f of fixture) {
    const got = serialize(generate(f.seed, { answerType: f.mode }));
    if (got !== f.serialized) {
      mismatches++;
      if (!firstMismatch) firstMismatch = `seed ${f.seed} (${f.mode})\n got: ${got}\n exp: ${f.serialized}`;
    }
  }
  assert.equal(mismatches, 0, `${mismatches} parity mismatch(es). First:\n${firstMismatch}`);
});
