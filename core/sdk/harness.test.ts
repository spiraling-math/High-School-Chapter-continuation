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
import { GENERATORS, generatorsForMode, approvedGenerators } from "./sequence-registry.ts";
import { approvalStatusOf } from "./generator-module.ts";
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

test("the registered generators are the expected set", () => {
  assert.deepEqual(GENERATORS.map((g) => `${g.id}@${g.version}`), [
    "gen.sequences.arithmetic@1.1.0",
    "gen.sequences.geometric@1.1.0",
    "gen.algebra.linear-equations@1.0.1",
    "gen.geometry.angles-figures@1.2.3",
    "gen.geometry.coordinate-lines@1.0.2",
    "gen.stats.data-handling@1.0.2",
    "gen.measurement.mensuration@1.0.1",
    "gen.geometry.transformations@1.0.2",
  ]);
});

test("approval lifecycle: all eight families curriculum-approved (transformations approved at v1.0.2)", () => {
  // gen.geometry.transformations was curriculum-approved at v1.0.2 (DECISION_LOG.md #57; tag
  // approved-transformations-v1.0.2), joining the seven earlier families. With no pending-review
  // generators registered, normal and review modes coincide; the gate still hides any future
  // pending-review/rejected generator.
  for (const id of ["gen.sequences.arithmetic", "gen.sequences.geometric", "gen.algebra.linear-equations",
    "gen.geometry.angles-figures", "gen.geometry.coordinate-lines", "gen.stats.data-handling",
    "gen.measurement.mensuration", "gen.geometry.transformations"]) {
    assert.equal(approvalStatusOf(GENERATORS.find((g) => g.id === id)!), "approved");
  }
  const normal = generatorsForMode("normal").map((g) => g.id);
  const review = generatorsForMode("review").map((g) => g.id);
  assert.ok(normal.includes("gen.geometry.transformations"), "transformations now visible in normal mode + production");
  assert.deepEqual(approvedGenerators().map((g) => g.id), normal, "approved set == normal-mode set");
  assert.equal(normal.length, 8);
  assert.equal(review.length, 8);
  assert.ok(normal.every((id) => approvalStatusOf(GENERATORS.find((g) => g.id === id)!) === "approved"));
});
