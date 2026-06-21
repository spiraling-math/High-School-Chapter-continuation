/**
 * Difficulty band helper tests (Node built-in test runner).
 * Run:  node --test core/difficulty/band.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { round3, clamp01, bandFromScore } from "./band.ts";

test("round3 rounds half-up to 3 decimals; integers stay integral", () => {
  assert.equal(round3(0.7111), 0.711);
  assert.equal(round3(0.7116), 0.712);
  assert.equal(round3(1), 1);
  assert.equal(round3(0), 0);
});

test("clamp01 clamps to [0,1]", () => {
  assert.equal(clamp01(-0.5), 0);
  assert.equal(clamp01(1.5), 1);
  assert.equal(clamp01(0.3), 0.3);
});

test("bandFromScore maps the score to 1..5", () => {
  assert.equal(bandFromScore(0), 1);
  assert.equal(bandFromScore(0.19), 1);
  assert.equal(bandFromScore(0.2), 2);
  assert.equal(bandFromScore(0.55), 3);
  assert.equal(bandFromScore(0.8), 5);
  assert.equal(bandFromScore(1), 5);
  assert.equal(bandFromScore(1.4), 5); // clamps
});
