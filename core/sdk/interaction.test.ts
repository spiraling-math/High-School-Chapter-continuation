/**
 * TD-1 interaction-resolver tests (Node built-in test runner).
 * Run:  node --test core/sdk/interaction.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { resolveInteractionType, legacyAnswerType } from "./interaction.ts";

test("maps the legacy answerType selector back-compatibly", () => {
  assert.equal(resolveInteractionType({ answerType: "multiple-choice" }), "multiple-choice");
  assert.equal(resolveInteractionType({ answerType: "integer" }), "free-response"); // legacy "integer" == free-response
  assert.equal(resolveInteractionType({}), "free-response");
});

test("prefers explicit interactionType when present", () => {
  assert.equal(resolveInteractionType({ interactionType: "multiple-choice", answerType: "integer" }), "multiple-choice");
  assert.equal(resolveInteractionType({ interactionType: "free-response", answerType: "multiple-choice" }), "free-response");
});

test("legacyAnswerType is the inverse mapping", () => {
  assert.equal(legacyAnswerType("multiple-choice"), "multiple-choice");
  assert.equal(legacyAnswerType("free-response"), "integer");
});
