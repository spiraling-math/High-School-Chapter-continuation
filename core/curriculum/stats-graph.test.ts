/**
 * Curriculum-graph + metadata gate for the gen.stats.data-handling family.
 * Loads the middle-school objective files together with the new SPI.MIDDLE.STAT.*
 * objectives and asserts the full graph is a clean DAG with the eleven new
 * objectives present and their prerequisites resolved. Also enforces the owner's
 * decisions (A, C, I, M): the exact eleven objective IDs via OBJECTIVE_BY_TASK
 * (no alternative spellings), the new domain/strand, mathematical-only answerTypes
 * (no "multiple-choice"), and curriculum-approved review status (v1.0.2).
 *
 * Run:  node --test core/curriculum/stats-graph.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { checkCurriculumGraph, requireObjectives, type ObjectiveLike } from "./graph-check.ts";
import { OBJECTIVE_BY_TASK, STAT_OBJECTIVE_IDS, STAT_TASKS } from "./stats-objective-ids.ts";

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
];

test("middle-school curriculum graph (incl. STAT) has no errors: no duplicate ids, no cycles", () => {
  const report = checkCurriculumGraph(middleObjectives as ObjectiveLike[]);
  assert.deepEqual(report.errors, [], `errors: ${report.errors.join("; ")}`);
  assert.ok(report.ok);
});

test("all eleven statistics objectives are present (exact approved IDs)", () => {
  assert.deepEqual(requireObjectives(middleObjectives as ObjectiveLike[], STAT_OBJECTIVE_IDS), []);
});

test("OBJECTIVE_BY_TASK is the single source: 11 distinct tasks -> 11 distinct approved IDs", () => {
  assert.equal(STAT_TASKS.length, 11);
  assert.equal(new Set(STAT_TASKS).size, 11);
  assert.equal(new Set(STAT_OBJECTIVE_IDS).size, 11);
  // Every mapped ID exists in the curriculum file; nothing extra is in the STAT file.
  const statFileIds = new Set(load("SPI.MIDDLE.STAT.json").map((o) => o.objectiveId));
  for (const id of STAT_OBJECTIVE_IDS) assert.ok(statFileIds.has(id), `${id} must exist in SPI.MIDDLE.STAT.json`);
  assert.equal(statFileIds.size, 11, "SPI.MIDDLE.STAT.json must contain exactly the eleven approved objectives");
});

test("no conflicting objective-ID spellings appear in the STAT file (owner A)", () => {
  const raw = readFileSync(join(objDir, "SPI.MIDDLE.STAT.json"), "utf8");
  const banned = [
    "READ.BAR.01", "READ.BAR_VALUE.01", "READ.PICTOGRAM_VALUE.01", "READ.TABLE.01",
    "READ.LINE.01", "FREQ.COMPLETE.01", "FREQ.MEAN_TABLE.01", "AVG.MEAN_FREQ.01",
  ];
  for (const b of banned) assert.ok(!raw.includes(b), `banned ID form '${b}' must not appear`);
});

test("statistics cross-domain prerequisites resolve within the loaded graph", () => {
  const ids = new Set(middleObjectives.map((o) => o.objectiveId));
  assert.ok(ids.has("SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"), "SIGNED_OPERATIONS prerequisite must be present");
});

test("statistics objective metadata follows the owner decisions", () => {
  const byId = new Map(middleObjectives.map((o) => [o.objectiveId, o]));
  const expectAnswerTypes: Record<string, string[]> = {
    "SPI.MIDDLE.STAT.READ.BAR_CHART.01": ["integer"],
    "SPI.MIDDLE.STAT.READ.PICTOGRAM.01": ["integer"],
    "SPI.MIDDLE.STAT.READ.TABLE_VALUE.01": ["integer"],
    "SPI.MIDDLE.STAT.READ.LINE_GRAPH.01": ["integer"],
    "SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01": ["table-completion"],
    "SPI.MIDDLE.STAT.AVG.MEAN_LIST.01": ["integer", "exact-rational"],
    "SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01": ["integer", "exact-rational"],
    "SPI.MIDDLE.STAT.AVG.MODE_LIST.01": ["integer"],
    "SPI.MIDDLE.STAT.AVG.RANGE_LIST.01": ["integer"],
    "SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01": ["integer", "exact-rational"],
    "SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01": ["fraction"],
  };
  for (const id of STAT_OBJECTIVE_IDS) {
    const o = byId.get(id)!;
    assert.equal(o.domain, "statistics", `${id} domain`);
    assert.equal(o.strand, "data-handling-and-probability", `${id} strand`);
    assert.equal(o.reviewStatus, "approved", `${id} reviewStatus (curriculum-approved at v1.0.2)`);
    assert.ok(!o.answerTypes.includes("multiple-choice"), `${id} must not list multiple-choice as an answer type`);
    assert.deepEqual(o.answerTypes, expectAnswerTypes[id], `${id} answerTypes`);
  }
});
