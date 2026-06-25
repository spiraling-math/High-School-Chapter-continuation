/**
 * Curriculum-graph + metadata gate for the gen.geometry.transformations family.
 * Loads the middle-school objective files together with the new SPI.MIDDLE.GEO.TRANS.* objectives and
 * asserts the full graph is a clean DAG with the nine new objectives present and their prerequisites
 * resolved. Also enforces the owner's decisions (A, B, P): the exact nine objective IDs via
 * OBJECTIVE_BY_TASK (no alternative spellings); domain geometry / strand coordinate-transformations /
 * GEO.TRANS segment; the per-task answer types (coordinate / table-completion / transformation; never
 * multiple-choice); coordinate-lines (GEO.COORD) prerequisites; MISC.TRANS.* misconception references;
 * and the approved-for-implementation review status.
 *
 * Run:  node --test core/curriculum/transformations-graph.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { checkCurriculumGraph, requireObjectives, type ObjectiveLike } from "./graph-check.ts";
import {
  OBJECTIVE_BY_TASK, TRANS_OBJECTIVE_IDS, TRANSFORMATIONS_TASKS, ANSWER_TYPE_BY_TASK,
} from "./transformations-objective-ids.ts";

const here = dirname(fileURLToPath(import.meta.url));
const objDir = join(here, "../../curriculum/objectives");
const load = (name: string): any[] => JSON.parse(readFileSync(join(objDir, name), "utf8"));

const middleObjectives: any[] = [
  ...load("SPI.MIDDLE.NUM.json"),
  ...load("SPI.MIDDLE.ALG.FOUNDATIONS.json"),
  ...load("SPI.MIDDLE.ALG.LINEQ.json"),
  ...load("SPI.MIDDLE.GEO.json"),
  ...load("SPI.MIDDLE.GEO.COORD.json"),
  ...load("SPI.MIDDLE.STAT.json"),
  ...load("SPI.MIDDLE.MEAS.json"),
  ...load("SPI.MIDDLE.GEO.TRANS.json"),
];

test("middle-school curriculum graph (incl. GEO.TRANS) has no errors: no duplicate ids, no cycles", () => {
  const report = checkCurriculumGraph(middleObjectives as ObjectiveLike[]);
  assert.deepEqual(report.errors, [], `errors: ${report.errors.join("; ")}`);
  assert.ok(report.ok);
});

test("all nine transformation objectives are present (exact approved IDs)", () => {
  assert.deepEqual(requireObjectives(middleObjectives as ObjectiveLike[], TRANS_OBJECTIVE_IDS), []);
});

test("OBJECTIVE_BY_TASK is the single source: 9 distinct tasks -> 9 distinct approved IDs", () => {
  assert.equal(TRANSFORMATIONS_TASKS.length, 9);
  assert.equal(new Set(TRANSFORMATIONS_TASKS).size, 9);
  assert.equal(new Set(TRANS_OBJECTIVE_IDS).size, 9);
  const fileIds = new Set(load("SPI.MIDDLE.GEO.TRANS.json").map((o) => o.objectiveId));
  for (const id of TRANS_OBJECTIVE_IDS) assert.ok(fileIds.has(id), `${id} must exist in SPI.MIDDLE.GEO.TRANS.json`);
  assert.equal(fileIds.size, 9, "SPI.MIDDLE.GEO.TRANS.json must contain exactly the nine approved objectives");
});

test("the GEO.TRANS segment is used and no conflicting ID spellings appear (owner A)", () => {
  const raw = readFileSync(join(objDir, "SPI.MIDDLE.GEO.TRANS.json"), "utf8");
  const banned = ["TRANS.TRANSLATEPOINT", "TRANS.REFLECTPOINT", "TRANS.ROTATEPOINT", "TRANS.DESCRIBE.01", "GEO.TRANSFORM."];
  for (const b of banned) assert.ok(!raw.includes(b), `banned ID form '${b}' must not appear`);
  for (const id of TRANS_OBJECTIVE_IDS) assert.ok(id.startsWith("SPI.MIDDLE.GEO.TRANS."), `${id} must use the GEO.TRANS segment`);
});

test("transformation prerequisites resolve and cite the approved coordinate-lines objectives (owner A)", () => {
  const ids = new Set(middleObjectives.map((o) => o.objectiveId));
  for (const dep of ["SPI.MIDDLE.GEO.COORD.READ_POINT.01", "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01",
    "SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]) {
    assert.ok(ids.has(dep), `${dep} prerequisite must be present`);
  }
});

test("transformation objective metadata follows the owner decisions (A, B, P)", () => {
  const byId = new Map(middleObjectives.map((o) => [o.objectiveId, o]));
  for (const t of TRANSFORMATIONS_TASKS) {
    const o = byId.get(OBJECTIVE_BY_TASK[t])!;
    assert.equal(o.domain, "geometry", `${t} domain`);
    assert.equal(o.strand, "coordinate-transformations", `${t} strand`);
    assert.equal(o.reviewStatus, "approved-for-implementation", `${t} reviewStatus (owner P)`);
    assert.deepEqual(o.answerTypes, [ANSWER_TYPE_BY_TASK[t]], `${t} answerTypes must be exactly ["${ANSWER_TYPE_BY_TASK[t]}"]`);
    assert.ok(!o.answerTypes.includes("multiple-choice"), `${t} must not list multiple-choice`);
    for (const m of o.commonMisconceptions ?? []) {
      assert.ok(String(m).startsWith("MISC.TRANS."), `${t} misconception ${m} must use the MISC.TRANS.* prefix`);
    }
  }
});
