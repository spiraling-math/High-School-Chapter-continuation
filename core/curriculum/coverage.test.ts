/**
 * Coverage report tests (§8, §10).
 *
 * Asserts the report's buckets are internally consistent: coveredApproved +
 * coveredPending + definedUncovered partition the 81 existing objectives (70 approved + 11
 * proposed functions objectives reached only by the pending-review functions family); orphanedTasks
 * is empty (every approved family's task resolves to a real objective); and the committed
 * docs/review/objective_coverage_report.json matches a freshly-computed report.
 *
 * Run:  node --test core/curriculum/coverage.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import { loadRegistry } from "./objective-registry.ts";
import { buildCoverageReport } from "./generator-capability.ts";
import { loadKnownBaseline } from "./registry-graph.ts";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const registry = loadRegistry();
const report = buildCoverageReport(registry);

test("covered + definedUncovered partition the 81 existing objectives", () => {
  const covered = new Set([...report.coveredApproved, ...report.coveredPending]);
  const uncovered = new Set(report.definedUncovered);
  // no overlap
  for (const id of covered) assert.ok(!uncovered.has(id), `${id} cannot be both covered and uncovered`);
  // partition is total over the 81
  assert.equal(covered.size + uncovered.size, 81);
  assert.equal(report.objectiveTotal, 81);
  assert.equal(
    report.byGeneratorTier.G2_approved + report.byGeneratorTier.G1_pendingOnly + report.byGeneratorTier.G0_noGenerator,
    81,
  );
});

test("nine approved families fully covered (G2=66); the eleven proposed functions objectives are G1 (pending only)", () => {
  assert.equal(report.byGeneratorTier.G2_approved, 66);
  assert.equal(report.byGeneratorTier.G1_pendingOnly, 11);
  assert.equal(report.byGeneratorTier.G0_noGenerator, 4);
  assert.ok(report.coveredPending.every((id) => id.startsWith("SPI.IBDPAASL.FUNC.")), "only the functions objectives are pending-only");
  assert.ok(report.coveredApproved.every((id) => !id.startsWith("SPI.IBDPAASL.FUNC.")), "a pending-review family never counts as approved coverage");
});

test("definedUncovered are exactly the foundational/non-task-mapped objectives", () => {
  assert.deepEqual(report.definedUncovered, [
    "SPI.MIDDLE.ALG.EXPAND_BRACKETS.01",
    "SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01",
    "SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01",
    "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01",
  ]);
});

test("orphanedTasks empty for the approved fleet (every task resolves)", () => {
  assert.deepEqual(report.orphanedTasks, []);
});

test("referenced-undefined: zero NEW, baseline-five recorded (consistent with §7.5)", () => {
  assert.deepEqual(report.newReferencedUndefined, []);
  assert.deepEqual(report.knownBaselineReferencedUndefined, [...loadKnownBaseline()].sort());
});

test("byGenerator covers all ten generators with the expected task counts", () => {
  const expected: Record<string, number> = {
    "gen.sequences.arithmetic": 4,
    "gen.sequences.geometric": 5,
    "gen.algebra.linear-equations": 5,
    "gen.geometry.angles-figures": 5,
    "gen.geometry.coordinate-lines": 7,
    "gen.stats.data-handling": 11,
    "gen.measurement.mensuration": 8,
    "gen.geometry.transformations": 9,
    "gen.proportion.ratio": 12,
    "gen.functions.foundations": 11,
  };
  for (const [gid, n] of Object.entries(expected)) {
    assert.equal(report.byGenerator[gid]?.length, n, `${gid} should cover ${n} objectives`);
  }
});

test("the committed coverage report matches a freshly computed one", () => {
  const path = join(ROOT, "docs/review/objective_coverage_report.json");
  if (!existsSync(path)) return; // tolerated if not yet generated
  const committed = JSON.parse(readFileSync(path, "utf8"));
  assert.equal(committed.objectiveTotal, report.objectiveTotal);
  assert.deepEqual(committed.coveredApproved, report.coveredApproved);
  assert.deepEqual(committed.definedUncovered, report.definedUncovered);
  assert.deepEqual(committed.byGeneratorTier, report.byGeneratorTier);
});
