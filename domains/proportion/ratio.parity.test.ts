/**
 * Cross-language byte-parity gate for gen.proportion.ratio v1.0.0.
 * The TypeScript mirror must reproduce the Python oracle's serialized output exactly, for the
 * golden vectors (16 entries) and the 360-entry task-pinned parity fixture.
 *
 * Run:  node --test domains/proportion/ratio.parity.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { generate, serialize, validate } from "./ratio.ts";

const root = fileURLToPath(new URL("../../", import.meta.url));
const golden = JSON.parse(readFileSync(root + "oracle/golden/ratio.golden.json", "utf8"));
const parity = JSON.parse(readFileSync(root + "oracle/golden/ratio.parity.json", "utf8"));

function firstDiff(got: string, want: string): string {
  let i = 0;
  while (i < Math.min(got.length, want.length) && got[i] === want[i]) i++;
  return `@${i}: TS …${got.slice(Math.max(0, i - 50), i + 40)}…  vs  PY …${want.slice(Math.max(0, i - 50), i + 40)}…`;
}

function configFor(e: { task: string | null; interaction: string | null }): Record<string, string> {
  // Reconstruct the EXACT generation config. A null interaction marks the default-interaction path
  // (no interactionType supplied -> full 12-task draw pool); passing an explicit interactionType there
  // would take a narrowed pool and shift the RNG draw index. So only set interactionType when present.
  const cfg: Record<string, string> = {};
  if (e.interaction !== null && e.interaction !== undefined) {
    cfg.interactionType = e.interaction;
  }
  if (e.task !== null && e.task !== undefined) {
    cfg.task = e.task;
  }
  return cfg;
}

test("golden vectors match the Python oracle byte-for-byte (and validation agrees)", () => {
  for (const g of golden) {
    const item = generate(g.seed, configFor(g));
    assert.equal(
      serialize(item),
      g.serialized,
      `golden seed ${g.seed} task ${g.task}\n${firstDiff(serialize(item), g.serialized)}`,
    );
    if ("valid" in g) {
      assert.equal(validate(item).valid, g.valid, `golden validation seed ${g.seed} task ${g.task}`);
    }
  }
});

test("task-pinned parity fixture (360 entries) matches the Python oracle byte-for-byte", () => {
  let mismatches = 0;
  let firstMismatch = "";
  for (const e of parity) {
    const got = serialize(generate(e.seed, { interactionType: e.interaction, task: e.task }));
    if (got !== e.serialized) {
      mismatches++;
      if (!firstMismatch) {
        firstMismatch = `seed ${e.seed} ${e.task} ${firstDiff(got, e.serialized)}`;
      }
    }
  }
  assert.equal(mismatches, 0, `${mismatches}/${parity.length} parity mismatches. First: ${firstMismatch}`);
});

test("a few media SVGs match the Python oracle character-for-character", () => {
  const withMedia = parity.filter((e: { serialized: string }) => e.serialized.indexOf('"media":[') !== -1);
  let checked = 0;
  for (const e of withMedia.slice(0, 12)) {
    const item = generate(e.seed, { interactionType: e.interaction, task: e.task });
    const want = JSON.parse(e.serialized);
    assert.equal(item.media[0].svg, want.media[0].svg, `student SVG seed ${e.seed} ${e.task}`);
    assert.equal(item.media[0].spec.answerKeySvg, want.media[0].spec.answerKeySvg, `key SVG seed ${e.seed} ${e.task}`);
    checked++;
  }
  assert.ok(checked > 0, "expected at least one media SVG to check");
});
