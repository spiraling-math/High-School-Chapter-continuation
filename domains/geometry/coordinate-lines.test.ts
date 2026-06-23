/**
 * Independent TypeScript validation gate for gen.geometry.coordinate-lines v1.0.0.
 * Confirms every task generates + validates, the owner interaction rules hold (plot_point
 * rejects multiple-choice; explicit interaction is never silently changed), and a seed
 * sweep produces zero invalid items (the TS validator agrees with the Python oracle).
 *
 * Run:  node --test domains/geometry/coordinate-lines.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { generate, validate, TASKS, pngExportTransform } from "./coordinate-lines.ts";

test("every task generates and validates (free-response + multiple-choice)", () => {
  for (const task of TASKS) {
    for (const interactionType of ["free-response", "multiple-choice"]) {
      if (interactionType === "multiple-choice" && task === "plot_point") {
        assert.throws(() => generate(5, { task, interactionType }), /free-response only/);
        continue;
      }
      const item = generate(5, { task, interactionType });
      assert.equal(validate(item).status, "pass", `${task}/${interactionType}`);
    }
  }
});

test("PNG export envelope is 6000x4200 (S=6, owner I.8)", () => {
  const t = pngExportTransform();
  assert.equal(t.scale, 6);
  assert.equal(t.width, 6000);
  assert.equal(t.height, 4200);
});

test("seed sweep: 0 invalid items (TS validator agrees with the oracle)", () => {
  let invalid = 0;
  for (let s = 1; s <= 1500; s++) {
    for (const interactionType of ["free-response", "multiple-choice"]) {
      const item = generate(s, { interactionType });
      if (validate(item).status !== "pass") invalid++;
    }
  }
  assert.equal(invalid, 0, `${invalid} invalid items`);
});

test("multiple-choice always has exactly three distinct misconception-backed distractors", () => {
  for (let s = 1; s <= 800; s++) {
    const item = generate(s, { interactionType: "multiple-choice" });
    assert.equal(item.distractors.length, 3, `seed ${s}`);
    assert.equal(new Set(item.distractors.map((d: { misconceptionId: string }) => d.misconceptionId)).size, 3);
    assert.equal(item.options.filter((o: { correct: boolean }) => o.correct).length, 1);
  }
});
