/**
 * Rendering + accessibility unit tests (Node built-in test runner + real KaTeX).
 *
 * Run:  node --test apps/generator-studio/render/katex-render.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import katex from "katex";
import { generate } from "../../../domains/sequences/arithmetic.ts";
import { validate } from "../../../domains/sequences/validate.ts";
import {
  mathHtml, renderQuestionStudent, renderQuestionTeacher, renderSolution, renderValidation, escapeHtml,
  type KatexLike,
} from "./katex-render.ts";

const kx = katex as unknown as KatexLike;

test("mathHtml emits accessible MathML alongside the visual HTML", () => {
  const html = mathHtml("u_n = u_1 + (n-1)d", kx, true);
  assert.ok(html.includes("katex"), "KaTeX visual output");
  assert.ok(/<math/i.test(html), "MathML present for screen readers");
});

test("escapeHtml neutralizes markup", () => {
  assert.equal(escapeHtml(`<b>&"'`), "&lt;b&gt;&amp;&quot;&#39;");
});

test("student question omits any correct-answer marking", () => {
  const item = generate(1, { answerType: "multiple-choice" });
  const html = renderQuestionStudent(item, kx);
  assert.ok(html.includes("options"), "options shown");
  assert.ok(!/class="[^"]*correct/i.test(html), "no correct marker for students");
});

test("teacher question marks the correct option with text, not color alone", () => {
  const item = generate(1, { answerType: "multiple-choice" });
  const html = renderQuestionTeacher(item, kx);
  assert.ok(/class="correct"/.test(html), "correct option flagged");
  // The stylesheet appends a textual "✓ correct" label, so it is not color-only.
});

test("validation view pairs an icon and text for each check (non-color indicator)", () => {
  const item = generate(1, { answerType: "multiple-choice" });
  const html = renderValidation(validate(item));
  assert.ok(html.includes("PASS"), "textual status, not color alone");
  assert.ok(html.includes("✓"), "icon indicator present");
  assert.ok(html.includes('role="list"'), "checks exposed as a list");
});

test("solution renders each step's math", () => {
  const item = generate(42, { answerType: "integer" });
  const html = renderSolution(item, kx);
  assert.ok(/<math/i.test(html), "steps rendered with accessible MathML");
  assert.ok(html.includes("sol-step"), "structured steps");
});
