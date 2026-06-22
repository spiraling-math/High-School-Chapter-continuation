/**
 * Stability-gate harness tests (Node built-in test runner).
 *
 * Runs the SDK harness against BOTH curriculum-approved generators, proving the
 * SDK surface works without changing any generator output. The full 10,000-seed
 * sweep lives in the oracle drivers; this is a fast in-suite subset.
 *
 * Run:  node --test core/sdk/harness.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { GENERATORS } from "./sequence-registry.ts";
import { runStabilityGate } from "./harness.ts";

const SEEDS = 2000;

for (const gen of GENERATORS) {
  test(`${gen.id} v${gen.version} passes the stability gate (${SEEDS} seeds)`, () => {
    const report = runStabilityGate(gen, { seeds: SEEDS, reproducibilitySpotCheck: 200 });
    assert.deepEqual(report.invalid, [], `invalid items: ${JSON.stringify(report.invalid.slice(0, 3))}`);
    assert.ok(report.reproducible, "serialization must be reproducible");
    // Every declared task is exercised, and difficulty bands vary.
    const declaredTasks = gen.tasks.map((t) => t.value).sort();
    assert.deepEqual(Object.keys(report.tasks).sort(), declaredTasks, `task coverage ${JSON.stringify(report.tasks)}`);
    assert.ok(Object.keys(report.bands).length > 1, `band variety ${JSON.stringify(report.bands)}`);
  });
}

test("the registered generators are the approved set", () => {
  assert.deepEqual(GENERATORS.map((g) => `${g.id}@${g.version}`), [
    "gen.sequences.arithmetic@1.1.0",
    "gen.sequences.geometric@1.1.0",
    "gen.algebra.linear-equations@1.0.1",
    "gen.geometry.angles-figures@1.1.0",
  ]);
});
