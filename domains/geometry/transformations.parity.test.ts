/**
 * Cross-language byte-parity gate for gen.geometry.transformations v1.0.0.
 * The TypeScript mirror must reproduce the Python oracle's serialized output exactly, for the
 * golden vectors (13 entries) and the 360-entry task-pinned parity fixture.
 *
 * Run:  node --test domains/geometry/transformations.parity.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { generate, serialize, validate } from "./transformations.ts";

const root = fileURLToPath(new URL("../../", import.meta.url));
const golden = JSON.parse(readFileSync(root + "oracle/golden/transformations.golden.json", "utf8"));
const parity = JSON.parse(readFileSync(root + "oracle/golden/transformations.parity.json", "utf8"));

function firstDiff(got: string, want: string): string {
  let i = 0;
  while (i < Math.min(got.length, want.length) && got[i] === want[i]) i++;
  return `@${i}: TS …${got.slice(Math.max(0, i - 50), i + 40)}…  vs  PY …${want.slice(Math.max(0, i - 50), i + 40)}…`;
}

test("golden vectors match the Python oracle byte-for-byte (and validation agrees)", () => {
  for (const g of golden) {
    const item = generate(
      g.seed,
      g.task ? { interactionType: "free-response", task: g.task } : { interactionType: "free-response" },
    );
    assert.equal(serialize(item), g.serialized, `golden seed ${g.seed} task ${g.task}\n${firstDiff(serialize(item), g.serialized)}`);
    if ("valid" in g) {
      assert.equal(validate(item).valid, g.valid, `golden validation seed ${g.seed} task ${g.task}`);
    }
  }
});

test("task-pinned parity fixture (360 entries) matches the Python oracle byte-for-byte", () => {
  let mismatches = 0;
  let firstMismatch = "";
  for (const e of parity) {
    const got = serialize(generate(e.seed, { interactionType: e.mode, task: e.task }));
    if (got !== e.serialized) {
      mismatches++;
      if (!firstMismatch) {
        firstMismatch = `seed ${e.seed} ${e.task} ${firstDiff(got, e.serialized)}`;
      }
    }
  }
  assert.equal(mismatches, 0, `${mismatches}/${parity.length} parity mismatches. First: ${firstMismatch}`);
});

test("every generated item validates (all 9 tasks, several seeds)", () => {
  for (const task of Object.keys(
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    {
      translate_point: 1,
      translate_shape: 1,
      reflect_point: 1,
      reflect_shape: 1,
      rotate_point: 1,
      rotate_shape: 1,
      describe_translation: 1,
      describe_reflection: 1,
      describe_rotation: 1,
    },
  )) {
    for (let seed = 1; seed <= 20; seed++) {
      const item = generate(seed, { interactionType: "free-response", task });
      assert.equal(validate(item).valid, true, `validate ${task} seed ${seed}`);
    }
  }
});
