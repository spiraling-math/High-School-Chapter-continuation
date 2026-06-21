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

test("accepts canonical-only interactionType", () => {
  assert.equal(resolveInteractionType({ interactionType: "multiple-choice" }), "multiple-choice");
  assert.equal(resolveInteractionType({ interactionType: "free-response" }), "free-response");
});

test("accepts matching dual fields; rejects conflicting dual fields", () => {
  assert.equal(resolveInteractionType({ interactionType: "multiple-choice", answerType: "multiple-choice" }), "multiple-choice");
  assert.equal(resolveInteractionType({ interactionType: "free-response", answerType: "integer" }), "free-response");
  assert.throws(() => resolveInteractionType({ interactionType: "multiple-choice", answerType: "integer" }));
  assert.throws(() => resolveInteractionType({ interactionType: "free-response", answerType: "multiple-choice" }));
});

test("legacyAnswerType is the inverse mapping", () => {
  assert.equal(legacyAnswerType("multiple-choice"), "multiple-choice");
  assert.equal(legacyAnswerType("free-response"), "integer");
});
