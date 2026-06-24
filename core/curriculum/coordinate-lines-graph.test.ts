/**
 * Curriculum-graph + metadata gate for the coordinate-lines family (DECISION_LOG #41).
 * Loads the middle-school objective files together with the new
 * SPI.MIDDLE.GEO.COORD.* objectives and asserts the full graph is a clean DAG with
 * the eight new objectives present and their prerequisites resolved. Also enforces the
 * owner's metadata decisions: mathematical-only answerTypes (no "multiple-choice"),
 * the new strand value, and the approved-for-implementation review status.
 *
 * Run:  node --test core/curriculum/coordinate-lines-graph.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { checkCurriculumGraph, requireObjectives, type ObjectiveLike } from "./graph-check.ts";

const here = dirname(fileURLToPath(import.meta.url));
const objDir = join(here, "../../curriculum/objectives");
const load = (name: string): any[] => JSON.parse(readFileSync(join(objDir, name), "utf8"));

// The middle-school graph the coordinate-lines family lives in (NUM/ALG provide prereqs).
const middleObjectives: any[] = [
  ...load("SPI.MIDDLE.NUM.json"),
  ...load("SPI.MIDDLE.ALG.FOUNDATIONS.json"),
  ...load("SPI.MIDDLE.ALG.LINEQ.json"),
  ...load("SPI.MIDDLE.GEO.json"),
  ...load("SPI.MIDDLE.GEO.COORD.json"),
];

const COORD = [
  "SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01", "SPI.MIDDLE.GEO.COORD.READ_POINT.01",
  "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01", "SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01",
  "SPI.MIDDLE.GEO.COORD.MIDPOINT.01", "SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01",
  "SPI.MIDDLE.GEO.COORD.EQUATION_FROM_GRAPH.01", "SPI.MIDDLE.GEO.COORD.EQUATION_FROM_2PTS.01",
];

test("middle-school curriculum graph (incl. COORD) has no errors: no duplicate ids, no cycles", () => {
  const report = checkCurriculumGraph(middleObjectives as ObjectiveLike[]);
  assert.deepEqual(report.errors, [], `errors: ${report.errors.join("; ")}`);
  assert.ok(report.ok);
});

test("all eight coordinate-lines objectives are present", () => {
  assert.deepEqual(requireObjectives(middleObjectives as ObjectiveLike[], COORD), []);
});

test("coordinate-lines cross-domain prerequisites resolve within the loaded graph", () => {
  const ids = new Set(middleObjectives.map((o) => o.objectiveId));
  for (const need of ["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01"]) {
    assert.ok(ids.has(need), `prerequisite ${need} must be present`);
  }
  // BOTHSIDES must NOT be a hard prerequisite of any coordinate-lines objective (owner A.5).
  const coordObjs = middleObjectives.filter((o) => o.objectiveId.includes(".GEO.COORD."));
  for (const o of coordObjs) {
    assert.ok(!(o.prerequisites ?? []).includes("SPI.MIDDLE.ALG.LINEQ.BOTHSIDES.01"),
      `${o.objectiveId} must not require BOTHSIDES`);
  }
});

test("coordinate-lines objective metadata follows the owner decisions", () => {
  const byId = new Map(middleObjectives.map((o) => [o.objectiveId, o]));
  const expectAnswerTypes: Record<string, string[]> = {
    "SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01": ["coordinate"],
    "SPI.MIDDLE.GEO.COORD.READ_POINT.01": ["coordinate"],
    "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01": ["coordinate"],
    "SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01": ["integer", "exact-rational"],
    "SPI.MIDDLE.GEO.COORD.MIDPOINT.01": ["ordered-pair"],
    "SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01": ["equation"],
    "SPI.MIDDLE.GEO.COORD.EQUATION_FROM_GRAPH.01": ["equation"],
    "SPI.MIDDLE.GEO.COORD.EQUATION_FROM_2PTS.01": ["equation"],
  };
  for (const id of COORD) {
    const o = byId.get(id)!;
    assert.equal(o.strand, "coordinate-geometry-straight-line-graphs", `${id} strand`);
    assert.equal(o.reviewStatus, "approved", `${id} reviewStatus`);
    // answerTypes are MATHEMATICAL only; multiple-choice is an interaction, never an answer type.
    assert.ok(!o.answerTypes.includes("multiple-choice"), `${id} must not list multiple-choice as an answer type`);
    assert.deepEqual(o.answerTypes, expectAnswerTypes[id], `${id} answerTypes`);
  }
});
