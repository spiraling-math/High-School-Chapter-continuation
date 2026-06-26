/**
 * Curriculum-graph + metadata gate for the gen.proportion.ratio family.
 * Loads the middle-school objective files together with the new SPI.MIDDLE.RATIO.* objectives and asserts
 * the full graph is a clean DAG with the twelve new objectives present and their prerequisites resolved.
 * Also enforces the owner's decisions (A, C, D): the exact twelve objective IDs via OBJECTIVE_BY_TASK (no
 * alternative spellings, no _UNITARY suffix); domain proportion / strand ratio-and-proportion / RATIO
 * segment; the per-task answer types; MISC.RATIO.* misconception references; and the
 * approved-for-implementation review status.
 *
 * Run:  node --test core/curriculum/ratio-graph.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { checkCurriculumGraph, requireObjectives, type ObjectiveLike } from "./graph-check.ts";
import {
  OBJECTIVE_BY_TASK, RATIO_OBJECTIVE_IDS, RATIO_TASKS, ANSWER_TYPES_BY_TASK,
} from "./ratio-objective-ids.ts";

const here = dirname(fileURLToPath(import.meta.url));
const objDir = join(here, "../../curriculum/objectives");
const load = (name: string): any[] => JSON.parse(readFileSync(join(objDir, name), "utf8"));

const middleObjectives: any[] = [
  ...load("SPI.MIDDLE.NUM.json"),
  ...load("SPI.MIDDLE.ALG.FOUNDATIONS.json"),
  ...load("SPI.MIDDLE.ALG.LINEQ.json"),
  ...load("SPI.MIDDLE.GEO.json"),
  ...load("SPI.MIDDLE.GEO.COORD.json"),
  ...load("SPI.MIDDLE.GEO.TRANS.json"),
  ...load("SPI.MIDDLE.STAT.json"),
  ...load("SPI.MIDDLE.MEAS.json"),
  ...load("SPI.MIDDLE.RATIO.json"),
];

test("middle-school curriculum graph (incl. RATIO) has no errors: no duplicate ids, no cycles", () => {
  const report = checkCurriculumGraph(middleObjectives as ObjectiveLike[]);
  assert.deepEqual(report.errors, [], `errors: ${report.errors.join("; ")}`);
  assert.ok(report.ok);
});

test("all twelve ratio objectives are present (exact approved IDs)", () => {
  assert.deepEqual(requireObjectives(middleObjectives as ObjectiveLike[], RATIO_OBJECTIVE_IDS), []);
});

test("OBJECTIVE_BY_TASK is the single source: 12 distinct tasks -> 12 distinct approved IDs", () => {
  assert.equal(RATIO_TASKS.length, 12);
  assert.equal(new Set(RATIO_TASKS).size, 12);
  assert.equal(new Set(RATIO_OBJECTIVE_IDS).size, 12);
  const fileIds = new Set(load("SPI.MIDDLE.RATIO.json").map((o) => o.objectiveId));
  for (const id of RATIO_OBJECTIVE_IDS) assert.ok(fileIds.has(id), `${id} must exist in SPI.MIDDLE.RATIO.json`);
  assert.equal(fileIds.size, 12, "SPI.MIDDLE.RATIO.json must contain exactly the twelve approved objectives");
});

test("the RATIO segment is used and no conflicting ID spellings appear (owner A)", () => {
  const raw = readFileSync(join(objDir, "SPI.MIDDLE.RATIO.json"), "utf8");
  const banned = ["DIRECT_PROPORTION_UNITARY", "INVERSE_PROPORTION_UNITARY", "SPI.MIDDLE.PROP.", "SPI.MIDDLE.PROPORTION."];
  for (const b of banned) assert.ok(!raw.includes(b), `banned ID form '${b}' must not appear`);
  for (const id of RATIO_OBJECTIVE_IDS) assert.ok(id.startsWith("SPI.MIDDLE.RATIO."), `${id} must use the RATIO segment`);
});

test("ratio prerequisites resolve (owner A)", () => {
  const ids = new Set(middleObjectives.map((o) => o.objectiveId));
  assert.ok(ids.has("SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"), "number prerequisite must be present");
  for (const id of RATIO_OBJECTIVE_IDS) {
    const o = middleObjectives.find((x) => x.objectiveId === id)!;
    for (const pre of o.prerequisites ?? []) assert.ok(ids.has(pre), `${id} prerequisite ${pre} must resolve`);
  }
});

test("ratio objective metadata follows the owner decisions (A, C, D)", () => {
  const byId = new Map(middleObjectives.map((o) => [o.objectiveId, o]));
  for (const t of RATIO_TASKS) {
    const o = byId.get(OBJECTIVE_BY_TASK[t])!;
    assert.equal(o.domain, "proportion", `${t} domain`);
    assert.equal(o.strand, "ratio-and-proportion", `${t} strand`);
    assert.equal(o.reviewStatus, "approved-for-implementation", `${t} reviewStatus (owner M)`);
    assert.deepEqual(o.answerTypes, ANSWER_TYPES_BY_TASK[t], `${t} answerTypes must be ${JSON.stringify(ANSWER_TYPES_BY_TASK[t])}`);
    for (const m of o.commonMisconceptions ?? []) {
      assert.ok(String(m).startsWith("MISC.RATIO."), `${t} misconception ${m} must use the MISC.RATIO.* prefix`);
    }
  }
  // best_buy is the only multiple-choice answer (owner C/D).
  assert.deepEqual(byId.get(OBJECTIVE_BY_TASK["best_buy"])!.answerTypes, ["multiple-choice"]);
});
