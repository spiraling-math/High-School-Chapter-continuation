/**
 * Universal validation predicate tests (Node built-in test runner).
 * Run:  node --test core/sdk/checks.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import {
  answerSolutionAgrees, promptIntsAreGivens, exactlyOneCorrectByDisplay, wrongOptionsUniqueByDisplay,
  spokenMathPresent, interactionTypeValid, answerTypeConsistent, provenanceComplete, versionFieldsPresent,
} from "./checks.ts";

test("answerSolutionAgrees", () => {
  assert.ok(answerSolutionAgrees("u_{10} = 31", "31"));
  assert.ok(!answerSolutionAgrees("u_{10} = 31", "32"));
});

test("promptIntsAreGivens", () => {
  assert.ok(promptIntsAreGivens([4, 3, 10], new Set([4, 3, 10])));
  assert.ok(!promptIntsAreGivens([4, 99], new Set([4, 3, 10])));
});

test("exactlyOneCorrectByDisplay", () => {
  const opts = [{ display: "31", correct: true }, { display: "34", correct: false }, { display: "13", correct: false }];
  assert.ok(exactlyOneCorrectByDisplay(opts, "31"));
  assert.ok(!exactlyOneCorrectByDisplay(opts, "34")); // correct option != answer
  assert.ok(!exactlyOneCorrectByDisplay([{ display: "1", correct: true }, { display: "1", correct: true }], "1")); // two correct
});

test("wrongOptionsUniqueByDisplay", () => {
  assert.ok(wrongOptionsUniqueByDisplay([{ display: "5", correct: true }, { display: "1", correct: false }, { display: "2", correct: false }]));
  assert.ok(!wrongOptionsUniqueByDisplay([{ display: "5", correct: true }, { display: "1", correct: false }, { display: "1", correct: false }]));
});

test("spokenMathPresent", () => {
  assert.ok(spokenMathPresent({ accessibility: { spokenMath: "..." } }));
  assert.ok(!spokenMathPresent({ accessibility: {} }));
  assert.ok(!spokenMathPresent({}));
});

test("interactionTypeValid", () => {
  assert.ok(interactionTypeValid("free-response"));
  assert.ok(interactionTypeValid("multiple-choice"));
  assert.ok(!interactionTypeValid("integer"));
  assert.ok(!interactionTypeValid(undefined));
});

test("answerTypeConsistent", () => {
  assert.ok(answerTypeConsistent("integer", { num: 4, den: 1 }));
  assert.ok(!answerTypeConsistent("integer", { num: 3, den: 4 })); // integer with den != 1
  assert.ok(answerTypeConsistent("exact-rational", { num: 3, den: 4 }));
  assert.ok(answerTypeConsistent("exact-rational", { num: 4, den: 1 })); // integer stored as rational is allowed
  assert.ok(answerTypeConsistent("integer", 12)); // legacy bare-number canonical (arithmetic) is fine
  assert.ok(answerTypeConsistent("multiple-choice", 31)); // other types unconstrained
});

test("provenanceComplete and versionFieldsPresent", () => {
  assert.ok(provenanceComplete({ provenance: { origin: "generated", rightsStatus: "academy-owned" } }));
  assert.ok(!provenanceComplete({ provenance: { origin: "generated" } }));
  assert.ok(versionFieldsPresent({ generatorId: "gen.x", generatorVersion: "1.0.0" }));
  assert.ok(!versionFieldsPresent({ generatorId: "gen.x" }));
});
