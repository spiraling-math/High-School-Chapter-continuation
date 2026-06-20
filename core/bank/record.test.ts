/**
 * Record-helper tests (Node built-in test runner).
 * Proves the separation between editable wording and protected math params.
 *
 * Run:  node --test core/bank/record.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { generate, serialize } from "../../domains/sequences/arithmetic.ts";
import { makeRecord, withWording, withLifecycle, duplicateRecord } from "./record.ts";

function rec(seed = 1, mode: "integer" | "multiple-choice" = "multiple-choice") {
  const item = generate(seed, { answerType: mode });
  return makeRecord(item, "pass", { mode });
}

test("a passing item starts at machine-validated", () => {
  assert.equal(rec().lifecycleState, "machine-validated");
});

test("wording edits never mutate the protected mathematical item", () => {
  const r = rec(42);
  const before = serialize(r.item);
  const edited = withWording(r, { title: "Quiz Q1", blocks: ["Custom stem wording."] });
  // The canonical item data is byte-for-byte unchanged.
  assert.equal(serialize(edited.item), before);
  assert.deepEqual(edited.item["params"], r.item["params"]);
  assert.equal((edited.item["answer"] as { canonical: number }).canonical,
    (r.item["answer"] as { canonical: number }).canonical);
  // The overlay carries the new wording.
  assert.equal(edited.wording.title, "Quiz Q1");
});

test("lifecycle changes never mutate the item", () => {
  const r = rec(7, "integer");
  const before = serialize(r.item);
  const moved = withLifecycle(r, "revised");
  assert.equal(serialize(moved.item), before);
  assert.equal(moved.lifecycleState, "revised");
});

test("duplicate produces an independent draft copy with a new id", () => {
  const r = rec(99);
  const copy = duplicateRecord(r, "ITEM-copy-1");
  assert.equal(copy.itemId, "ITEM-copy-1");
  assert.equal(copy.item["itemId"], "ITEM-copy-1");
  assert.equal(copy.lifecycleState, "draft");
  // Editing the copy's tags does not affect the original.
  copy.tags.push("x");
  assert.deepEqual(r.tags, []);
});
