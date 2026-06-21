/**
 * Shared MC option-assembly tests (Node built-in test runner).
 * Run:  node --test core/sdk/multiple-choice.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { Mulberry32 } from "../seeded-random/mulberry32.ts";
import { assembleMultipleChoice, type McDistractor } from "./multiple-choice.ts";

const encodeInt = (v: number) => ({ value: v, display: String(v) });
const D = (value: number, id: string, rationale: string): McDistractor<number> => ({ value, misconceptionId: id, rationale });

test("preserves values, ids, misconception metadata, and rationales", () => {
  const ds = [D(10, "M.A", "ra"), D(20, "M.B", "rb"), D(30, "M.C", "rc")];
  const { distractors, options } = assembleMultipleChoice(new Mulberry32(1), 5, ds, encodeInt);
  assert.deepEqual(distractors, [
    { id: "d1", value: 10, display: "10", misconceptionId: "M.A", rationale: "ra" },
    { id: "d2", value: 20, display: "20", misconceptionId: "M.B", rationale: "rb" },
    { id: "d3", value: 30, display: "30", misconceptionId: "M.C", rationale: "rc" },
  ]);
  // Exactly one correct option; the correct option carries no misconceptionId.
  const correct = options.filter((o) => o["correct"]);
  assert.equal(correct.length, 1);
  assert.equal(correct[0]!["value"], 5);
  assert.ok(!("misconceptionId" in correct[0]!));
  // Labels are A..D in order.
  assert.deepEqual(options.map((o) => o["label"]), ["A", "B", "C", "D"]);
});

test("deterministic ordering: same seed → identical option order", () => {
  const ds = [D(10, "M.A", "ra"), D(20, "M.B", "rb"), D(30, "M.C", "rc")];
  const a = assembleMultipleChoice(new Mulberry32(42), 5, ds, encodeInt).options.map((o) => o["value"]);
  const b = assembleMultipleChoice(new Mulberry32(42), 5, ds, encodeInt).options.map((o) => o["value"]);
  const c = assembleMultipleChoice(new Mulberry32(43), 5, ds, encodeInt).options.map((o) => o["value"]);
  assert.deepEqual(a, b);
  assert.notDeepEqual(a, c); // different seed generally reorders
});

test("duplicate options are preserved faithfully (dedup is the generator's job)", () => {
  const ds = [D(10, "M.A", "ra"), D(10, "M.B", "rb"), D(30, "M.C", "rc")]; // two 10s
  const { options } = assembleMultipleChoice(new Mulberry32(1), 5, ds, encodeInt);
  const wrong = options.filter((o) => !o["correct"]).map((o) => o["value"]);
  assert.equal(wrong.filter((v) => v === 10).length, 2); // helper does not deduplicate
});

test("answer collision is visible (helper does not silently drop it)", () => {
  const ds = [D(5, "M.A", "ra"), D(20, "M.B", "rb"), D(30, "M.C", "rc")]; // 5 == correct
  const { options } = assembleMultipleChoice(new Mulberry32(1), 5, ds, encodeInt);
  // exactly one is flagged correct, but a wrong option collides with the answer value
  assert.equal(options.filter((o) => o["correct"]).length, 1);
  assert.ok(options.filter((o) => !o["correct"]).some((o) => o["value"] === 5));
});

test("insufficient distractors: helper assembles what it is given", () => {
  const { options } = assembleMultipleChoice(new Mulberry32(1), 5, [D(10, "M.A", "ra")], encodeInt);
  assert.equal(options.length, 2); // 1 correct + 1 wrong; the ≥3 rule is enforced by the generator
});
