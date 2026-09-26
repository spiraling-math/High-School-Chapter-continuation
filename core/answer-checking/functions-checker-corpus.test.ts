/**
 * Cross-engine grading-path parity for the functions family's checkers.
 *
 * oracle/golden/functions_checker_corpus.json holds every (input, canonical, diagnostics) case with the
 * code the Python oracle assigns; the TypeScript checkers must produce the identical result for every
 * case. This is the lesson of ratio v1.0.0 (the CRITICAL grading-path parity break that generator-output
 * parity could not see). Run:  node --test core/answer-checking/functions-checker-corpus.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { checkExpression, EXPRESSION_CODES, type ExpressionDiagnostic } from "./expression-checker.ts";
import { checkInterval, INTERVAL_CODES, type IntervalDiagnostic, type IntervalJson } from "./interval-checker.ts";
import type { PolyJson } from "../exact-math/polynomial.ts";

const root = fileURLToPath(new URL("../../", import.meta.url));
interface Case<C, D> { input: string; canonical: C; diagnostics: D[]; expected: { code: string; misconceptionId?: string } }
const corpus = JSON.parse(readFileSync(root + "oracle/golden/functions_checker_corpus.json", "utf8")) as {
  expression: Case<PolyJson, ExpressionDiagnostic>[]; interval: Case<IntervalJson, IntervalDiagnostic>[];
};

test("expression checker: every corpus case grades identically to the Python oracle", () => {
  assert.ok(corpus.expression.length >= 60, "corpus present");
  for (const c of corpus.expression) {
    const got = checkExpression(c.input, c.canonical, c.diagnostics);
    assert.deepEqual(got, c.expected, `expression input ${JSON.stringify(c.input)}`);
  }
});

test("interval checker: every corpus case grades identically to the Python oracle", () => {
  assert.ok(corpus.interval.length >= 80, "corpus present");
  for (const c of corpus.interval) {
    const got = checkInterval(c.input, c.canonical, c.diagnostics);
    assert.deepEqual(got, c.expected, `interval input ${JSON.stringify(c.input)}`);
  }
});

test("the corpus exercises every result code of both vocabularies", () => {
  const seenE = new Set(corpus.expression.map((c) => c.expected.code));
  const seenI = new Set(corpus.interval.map((c) => c.expected.code));
  for (const code of EXPRESSION_CODES) assert.ok(seenE.has(code), `expression code ${code} exercised`);
  for (const code of INTERVAL_CODES) assert.ok(seenI.has(code), `interval code ${code} exercised`);
});
