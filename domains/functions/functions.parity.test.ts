/**
 * Cross-language byte-parity gate for gen.functions.foundations v1.0.0.
 * The TypeScript mirror must reproduce the Python oracle's serialized output exactly, for the
 * golden vectors (25 entries: default no-task draw at the four golden seeds, every task at seed 1,
 * every task in multiple-choice at seed 2) and the 420-entry task-pinned parity fixture (20 seeds x
 * 11 tasks x every supported interaction), and the validation status must agree.
 *
 * Run:  node --test domains/functions/functions.parity.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { generate, serialize, validate } from "./functions.ts";

const root = fileURLToPath(new URL("../../", import.meta.url));
const golden = JSON.parse(readFileSync(root + "oracle/golden/functions.golden.json", "utf8"));
const parity = JSON.parse(readFileSync(root + "oracle/golden/functions.parity.json", "utf8"));

function firstDiff(got: string, want: string): string {
  let i = 0;
  while (i < Math.min(got.length, want.length) && got[i] === want[i]) i++;
  return `@${i}: TS …${got.slice(Math.max(0, i - 60), i + 50)}…  vs  PY …${want.slice(Math.max(0, i - 60), i + 50)}…`;
}

function configFor(e: { task: string | null; interaction: string | null }): Record<string, string> {
  // Reconstruct the EXACT generation config. A null interaction marks the default-interaction path (no
  // interactionType supplied -> the full 11-task draw pool); passing an explicit interactionType there
  // would narrow the pool and shift the RNG draw index. So only set interactionType when present.
  const cfg: Record<string, string> = {};
  if (e.interaction !== null && e.interaction !== undefined) cfg.interactionType = e.interaction;
  if (e.task !== null && e.task !== undefined) cfg.task = e.task;
  return cfg;
}

test("golden vectors (25) match the Python oracle byte-for-byte (and validation status agrees)", () => {
  assert.equal(golden.length, 25);
  for (const g of golden) {
    const item = generate(g.seed, configFor(g));
    const got = serialize(item);
    assert.equal(got, g.serialized, `golden seed ${g.seed} task ${g.task} ${g.interaction}\n${firstDiff(got, g.serialized)}`);
    assert.equal(validate(item).status === "pass", g.valid, `golden validation seed ${g.seed} task ${g.task}`);
  }
});

test("task-pinned parity fixture (420 entries) matches the Python oracle byte-for-byte", () => {
  assert.equal(parity.length, 420);
  let mismatches = 0;
  let firstMismatch = "";
  for (const e of parity) {
    const got = serialize(generate(e.seed, { interactionType: e.interaction, task: e.task }));
    if (got !== e.serialized) {
      mismatches++;
      if (!firstMismatch) firstMismatch = `seed ${e.seed} ${e.task} ${e.interaction} ${firstDiff(got, e.serialized)}`;
    }
  }
  assert.equal(mismatches, 0, `${mismatches}/${parity.length} parity mismatches. First: ${firstMismatch}`);
});

test("every parity item validates in TypeScript (independent validator agrees with the oracle sweep)", () => {
  const failing: string[] = [];
  for (const e of parity) {
    const v = validate(generate(e.seed, { interactionType: e.interaction, task: e.task }));
    if (v.status !== "pass") {
      failing.push(`${e.seed}/${e.task}/${e.interaction}: ` + v.checks.filter((c: { result: string }) => c.result === "fail").map((c: { name: string }) => c.name).join(","));
    }
  }
  assert.deepEqual(failing, []);
});
