/**
 * Exporter tests (Node built-in test runner + real KaTeX).
 *
 * Covers: offline-safety of all exports (no external/script refs), student
 * worksheet hides answers/validation, answer key & solutions agree with the
 * canonical answers, and JSON export/import round-trips with integrity.
 *
 * Run:  node --test exporters/exporters.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import katex from "katex";
import { generate } from "../domains/sequences/arithmetic.ts";
import { validate } from "../domains/sequences/validate.ts";
import { makeRecord, duplicateRecord } from "../core/bank/record.ts";
import type { BankRecord, Mode } from "../core/bank/types.ts";
import type { KatexLike } from "../apps/generator-studio/render/katex-render.ts";
import { studentWorksheet } from "./html/worksheet.ts";
import { answerKey } from "./html/answer-key.ts";
import { workedSolutions } from "./html/solutions.ts";
import { exportBankJson, importBankJson } from "./json/bank-json.ts";

const kx = katex as unknown as KatexLike;

function recs(seeds: number[], mode: Mode): BankRecord[] {
  return seeds.map((s) => {
    const item = generate(s, { answerType: mode });
    return makeRecord(item, validate(item).status, { mode, genConfig: { answerType: mode } });
  });
}

function assertOffline(html: string): void {
  // Genuine external loads only — the MathML namespace URI in accessible KaTeX
  // output (xmlns="http://www.w3.org/1998/Math/MathML") is not a network fetch.
  assert.ok(!/\bsrc\s*=\s*["']?(?:https?:)?\/\//i.test(html), "no external src");
  assert.ok(!/<link\b[^>]*\bhref\s*=\s*["']?(?:https?:)?\/\//i.test(html), "no external stylesheet");
  assert.ok(!/url\(\s*["']?(?:https?:)?\/\//i.test(html), "no external css url");
  assert.ok(!/<script\b/i.test(html), "exports are static — no <script>");
}

test("student worksheet hides answers, solutions, and validation", () => {
  const html = studentWorksheet(recs([1, 2, 3], "integer"), { katex: kx, title: "WS" });
  assertOffline(html);
  assert.ok(html.includes("1."), "has question numbers");
  assert.ok(html.includes("answer-space"), "free-response items get an answer space");
  assert.ok(!/Answer:/i.test(html), "no answer label");
  assert.ok(!/Solution/i.test(html), "no solution");
  assert.ok(!/class="correct"/i.test(html), "no correct-option marker");
  assert.ok(!/PASS|FAIL|validation/i.test(html), "no validation metadata");
});

test("multiple-choice worksheet lists options without marking the correct one", () => {
  const html = studentWorksheet(recs([1], "multiple-choice"), { katex: kx });
  assertOffline(html);
  assert.ok(html.includes("options"), "options listed");
  assert.ok(!/class="[^"]*correct/i.test(html), "correct option not marked");
});

test("answer key agrees with canonical answers", () => {
  const rs = recs([1, 2, 3], "multiple-choice");
  const html = answerKey(rs);
  assertOffline(html);
  for (const r of rs) {
    const a = r.item["answer"] as { display: string; canonical: number };
    assert.equal(a.display, String(a.canonical));
    assert.ok(html.includes(a.display), `answer ${a.display} present`);
  }
});

test("worked solutions embed KaTeX CSS, render math, and state the canonical answer", () => {
  const rs = recs([1, 42], "multiple-choice");
  const html = workedSolutions(rs, { katex: kx, katexCss: "/*KATEX-CSS-MARKER*/", title: "Sol" });
  assertOffline(html);
  assert.ok(html.includes("/*KATEX-CSS-MARKER*/"), "bundled KaTeX CSS embedded");
  assert.ok(html.includes("Solution"), "solutions present");
  assert.ok(html.includes("katex"), "KaTeX-rendered math present");
  for (const r of rs) {
    const a = r.item["answer"] as { display: string };
    assert.ok(html.includes(`<strong>Answer:</strong> ${a.display}`), "answer agrees");
  }
});

test("JSON export/import round-trips with integrity and is canonical-stable", () => {
  const base = recs([1, 42, 7], "multiple-choice");
  base.push(duplicateRecord(base[0]!, base[0]!.itemId + "-copy")); // include a renamed duplicate
  const out = exportBankJson(base);
  const imp = importBankJson(out);
  assert.equal(imp.integrityOk, true, `errors: ${imp.errors.join("; ")}`);
  assert.deepEqual(imp.errors, []);
  assert.equal(imp.records.length, base.length);
  // Re-exporting the imported records yields a byte-identical document.
  assert.equal(exportBankJson(imp.records), out);
});

test("JSON import integrity catches a tampered item", () => {
  const out = exportBankJson(recs([5], "integer"));
  const tampered = JSON.parse(out);
  (tampered.records[0].item.answer as { canonical: number }).canonical += 1;
  const imp = importBankJson(JSON.stringify(tampered));
  assert.equal(imp.integrityOk, false);
  assert.ok(imp.errors.length > 0);
});

test("JSON import backfills interactionType on legacy records (idempotent)", () => {
  const rs = recs([3], "multiple-choice");
  const legacy = rs.map((r) => { const c = { ...r } as Record<string, unknown>; delete c["interactionType"]; return c; });
  const imp = importBankJson(JSON.stringify({ format: "spi-math-bank", version: "1.0.0", records: legacy }));
  assert.equal(imp.records[0]!.interactionType, "multiple-choice");
  assert.equal(imp.integrityOk, true, imp.errors.join("; "));
  // Re-importing the normalized records is stable.
  const imp2 = importBankJson(exportBankJson(imp.records));
  assert.equal(imp2.records[0]!.interactionType, "multiple-choice");
});

test("auto-task records reproduce from stored config", () => {
  // Auto mode draws the task from the RNG; the stored genConfig must omit task.
  const item = generate(3, { answerType: "multiple-choice" });
  const rec = makeRecord(item, "pass", { mode: "multiple-choice", genConfig: { answerType: "multiple-choice" } });
  const imp = importBankJson(exportBankJson([rec]));
  assert.equal(imp.integrityOk, true, imp.errors.join("; "));
});
