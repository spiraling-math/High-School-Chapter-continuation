/**
 * Curriculum-graph integrity tests (Node built-in test runner).
 * Loads the approved objective data and validates the graph.
 * Run:  node --test core/curriculum/graph-check.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { checkCurriculumGraph, requireObjectives, type ObjectiveLike } from "./graph-check.ts";

const here = dirname(fileURLToPath(import.meta.url));
const objDir = join(here, "../../curriculum/objectives");
const objectives: ObjectiveLike[] = [
  ...JSON.parse(readFileSync(join(objDir, "SPI.IBDPAASL.SEQSER.ARITH.json"), "utf8")),
  ...JSON.parse(readFileSync(join(objDir, "SPI.IBDPAASL.SEQSER.GEO.json"), "utf8")),
];

const APPROVED = [
  "SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01", "SPI.IBDPAASL.SEQSER.ARITH.SUM_N.01",
  "SPI.IBDPAASL.SEQSER.ARITH.COMMON_DIFF.01", "SPI.IBDPAASL.SEQSER.ARITH.TERM_INDEX.01",
  "SPI.IBDPAASL.SEQSER.GEO.NTH_TERM.01", "SPI.IBDPAASL.SEQSER.GEO.SUM_N.01",
  "SPI.IBDPAASL.SEQSER.GEO.COMMON_RATIO.01", "SPI.IBDPAASL.SEQSER.GEO.TERM_INDEX.01",
  "SPI.IBDPAASL.SEQSER.GEO.SUM_INFINITE.01",
];

test("approved objective graph has no errors (no duplicate ids, no cycles)", () => {
  const report = checkCurriculumGraph(objectives);
  assert.deepEqual(report.errors, [], `errors: ${report.errors.join("; ")}`);
  assert.ok(report.ok);
  assert.equal(report.objectiveCount, 9);
});

test("all nine approved objectives are present", () => {
  assert.deepEqual(requireObjectives(objectives, APPROVED), []);
});

test("cycle detection works (synthetic)", () => {
  const cyclic: ObjectiveLike[] = [
    { objectiveId: "A", prerequisites: ["B"] },
    { objectiveId: "B", prerequisites: ["A"] },
  ];
  const r = checkCurriculumGraph(cyclic);
  assert.ok(!r.ok);
  assert.ok(r.errors.some((e) => e.includes("cycle")));
});

test("duplicate-id detection works (synthetic)", () => {
  const dup: ObjectiveLike[] = [{ objectiveId: "X" }, { objectiveId: "X" }];
  const r = checkCurriculumGraph(dup);
  assert.ok(r.errors.some((e) => e.includes("duplicate")));
});
