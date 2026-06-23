/**
 * Cross-language byte-parity gate for gen.geometry.coordinate-lines v1.0.0.
 * The TypeScript mirror must reproduce the Python oracle's serialized output exactly,
 * for the golden seeds and the 150-seed x 2-mode parity fixture.
 *
 * Run:  node --test domains/geometry/coordinate-lines.parity.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { generate, serialize } from "./coordinate-lines.ts";

const root = fileURLToPath(new URL("../../", import.meta.url));
const golden = JSON.parse(readFileSync(root + "oracle/golden/coordinate_lines.golden.json", "utf8"));
const parity = JSON.parse(readFileSync(root + "oracle/golden/coordinate_lines.parity.json", "utf8"));

test("golden vectors match the Python oracle byte-for-byte", () => {
  for (const g of golden) {
    const got = serialize(generate(g.seed, { interactionType: "multiple-choice" }));
    assert.equal(got, g.serialized, `golden seed ${g.seed}`);
  }
});

test("parity fixture (150 seeds x 2 modes) matches the Python oracle byte-for-byte", () => {
  let mismatches = 0;
  let firstMismatch = "";
  for (const e of parity) {
    const got = serialize(generate(e.seed, { interactionType: e.mode }));
    if (got !== e.serialized) {
      mismatches++;
      if (!firstMismatch) {
        // find the first differing character to ease debugging
        let i = 0;
        while (i < Math.min(got.length, e.serialized.length) && got[i] === e.serialized[i]) i++;
        firstMismatch = `seed ${e.seed} ${e.mode} @${i}: TS …${got.slice(Math.max(0, i - 30), i + 30)}…  vs  PY …${e.serialized.slice(Math.max(0, i - 30), i + 30)}…`;
      }
    }
  }
  assert.equal(mismatches, 0, `${mismatches}/${parity.length} parity mismatches. First: ${firstMismatch}`);
});
