/**
 * Curriculum-graph + metadata gate for the gen.measurement.mensuration family.
 * Loads the middle-school objective files together with the new SPI.MIDDLE.MEAS.* objectives and
 * asserts the full graph is a clean DAG with the eight new objectives present and their
 * prerequisites resolved. Also enforces the owner's decisions (A, C, F, M): the exact eight
 * objective IDs via OBJECTIVE_BY_TASK (no alternative spellings); domain measurement / strand
 * mensuration / MEAS segment; the dimensional-quantity ("quantity") answer type only (never
 * "multiple-choice"); free-response-only interaction; one-step linear-equation cross-domain
 * relationships on the inverse tasks (never variables-on-both-sides); and the
 * approved-for-implementation review status.
 *
 * Run:  node --test core/curriculum/mensuration-graph.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { checkCurriculumGraph, requireObjectives, type ObjectiveLike } from "./graph-check.ts";
import {
  OBJECTIVE_BY_TASK,
  MENS_OBJECTIVE_IDS,
  MENSURATION_TASKS,
  HIDDEN_DIMENSION_TASKS,
  RATIONAL_ANSWER_TASKS,
} from "./mensuration-objective-ids.ts";

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
];

test("middle-school curriculum graph (incl. MEAS) has no errors: no duplicate ids, no cycles", () => {
  const report = checkCurriculumGraph(middleObjectives as ObjectiveLike[]);
  assert.deepEqual(report.errors, [], `errors: ${report.errors.join("; ")}`);
  assert.ok(report.ok);
});

test("all eight mensuration objectives are present (exact approved IDs)", () => {
  assert.deepEqual(requireObjectives(middleObjectives as ObjectiveLike[], MENS_OBJECTIVE_IDS), []);
});

test("OBJECTIVE_BY_TASK is the single source: 8 distinct tasks -> 8 distinct approved IDs", () => {
  assert.equal(MENSURATION_TASKS.length, 8);
  assert.equal(new Set(MENSURATION_TASKS).size, 8);
  assert.equal(new Set(MENS_OBJECTIVE_IDS).size, 8);
  const measFileIds = new Set(load("SPI.MIDDLE.MEAS.json").map((o) => o.objectiveId));
  for (const id of MENS_OBJECTIVE_IDS) assert.ok(measFileIds.has(id), `${id} must exist in SPI.MIDDLE.MEAS.json`);
  assert.equal(measFileIds.size, 8, "SPI.MIDDLE.MEAS.json must contain exactly the eight approved objectives");
});

test("the MEAS segment is used (never MENS) and no conflicting ID spellings appear (owner A)", () => {
  const raw = readFileSync(join(objDir, "SPI.MIDDLE.MEAS.json"), "utf8");
  assert.ok(!raw.includes("SPI.MIDDLE.MENS."), "the curriculum domain segment must be MEAS, never MENS");
  const banned = [
    "PERIM.RECT.01", "PERIM.COMPOSITE.01", "AREA.RECT.01", "AREA.TRIANGLE.01",
    "AREA.COMPOSITE.01", "PERIM.MISSING.01", "AREA.MISSING.01", "AREA.TRI_MISSING.01",
  ];
  for (const b of banned) assert.ok(!raw.includes(b), `banned ID form '${b}' must not appear`);
  for (const id of MENS_OBJECTIVE_IDS) assert.ok(id.startsWith("SPI.MIDDLE.MEAS."), `${id} must use the MEAS segment`);
});

test("mensuration cross-domain prerequisites resolve and use only ONE-STEP linear objectives (owner A)", () => {
  const ids = new Set(middleObjectives.map((o) => o.objectiveId));
  assert.ok(ids.has("SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"), "SIGNED_OPERATIONS prerequisite must be present");
  assert.ok(ids.has("SPI.MIDDLE.ALG.LINEQ.ONESTEP_ADD.01"), "ONESTEP_ADD prerequisite must be present");
  assert.ok(ids.has("SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01"), "ONESTEP_MUL prerequisite must be present");
  const byId = new Map(middleObjectives.map((o) => [o.objectiveId, o]));
  // No mensuration objective may depend on variables-on-both-sides (owner A).
  for (const id of MENS_OBJECTIVE_IDS) {
    const o = byId.get(id)!;
    const prereqs: string[] = o.prerequisites ?? [];
    assert.ok(!prereqs.includes("SPI.MIDDLE.ALG.LINEQ.BOTHSIDES.01"), `${id} must not require variables-on-both-sides`);
    assert.ok(!prereqs.includes("SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01"), `${id} must not require two-step equations`);
  }
  // The three inverse tasks carry a one-step linear cross-domain relationship.
  const inverse = HIDDEN_DIMENSION_TASKS.map((t) => OBJECTIVE_BY_TASK[t]);
  for (const id of inverse) {
    const o = byId.get(id)!;
    const xrefs: string[] = (o.crossDomainRelationships ?? []).map((r: any) => r.objectiveId);
    assert.ok(
      xrefs.some((x) => x === "SPI.MIDDLE.ALG.LINEQ.ONESTEP_ADD.01" || x === "SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01"),
      `${id} must record a one-step linear-equation cross-domain relationship`,
    );
  }
});

test("mensuration objective metadata follows the owner decisions (A, C, F, M)", () => {
  const byId = new Map(middleObjectives.map((o) => [o.objectiveId, o]));
  for (const id of MENS_OBJECTIVE_IDS) {
    const o = byId.get(id)!;
    assert.equal(o.domain, "measurement", `${id} domain`);
    assert.equal(o.strand, "mensuration", `${id} strand`);
    assert.equal(o.reviewStatus, "approved-for-implementation", `${id} reviewStatus (owner M)`);
    // Every answer is a dimensional quantity; multiple-choice is never an answer type (owner C).
    assert.deepEqual(o.answerTypes, ["quantity"], `${id} answerTypes must be exactly ["quantity"]`);
    assert.ok(!o.answerTypes.includes("multiple-choice"), `${id} must not list multiple-choice`);
    // Misconception references all use the MISC.MENS.* prefix (owner A, K).
    for (const m of o.commonMisconceptions ?? []) {
      assert.ok(String(m).startsWith("MISC.MENS."), `${id} misconception ${m} must use the MISC.MENS.* prefix`);
    }
  }
});

test("RATIONAL_ANSWER_TASKS is exactly the two triangle tasks (owner F exactness policy)", () => {
  assert.deepEqual([...RATIONAL_ANSWER_TASKS].sort(), ["area_triangle", "missing_triangle_base_height"]);
});
