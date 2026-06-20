/**
 * Wording-overlay tests (Node built-in test runner).
 * Proves the display overlay never mutates the protected mathematical item.
 *
 * Run:  node --test apps/generator-studio/wording.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { generate, serialize } from "../../domains/sequences/arithmetic.ts";
import { displayItem, wordingTexts } from "./wording.ts";

test("displayItem overrides prompt text without mutating the item", () => {
  const item = generate(1, { answerType: "multiple-choice" });
  const before = serialize(item);
  const shown = displayItem(item, { blocks: ["Custom line one.", "Custom line two."] });
  // Original item is unchanged.
  assert.equal(serialize(item), before);
  // Displayed prompt uses the overrides.
  const blocks = (shown["prompt"] as { blocks: Array<{ text?: string }> }).blocks;
  assert.equal(blocks[0]?.text, "Custom line one.");
  assert.equal(blocks[1]?.text, "Custom line two.");
  // Math data is shared/identical.
  assert.deepEqual(shown["params"], item["params"]);
  assert.equal((shown["answer"] as { canonical: number }).canonical,
    (item["answer"] as { canonical: number }).canonical);
});

test("displayItem with no overlay returns the item unchanged", () => {
  const item = generate(5, { answerType: "integer" });
  assert.equal(displayItem(item), item);
  assert.equal(displayItem(item, {}), item);
});

test("wordingTexts returns overlay text when present, else original", () => {
  const item = generate(2, { answerType: "integer" });
  const original = wordingTexts(item);
  assert.equal(original.length, 2);
  const edited = wordingTexts(item, { blocks: ["X"] });
  assert.equal(edited[0], "X");
  assert.equal(edited[1], original[1]); // untouched block falls back to original
});
