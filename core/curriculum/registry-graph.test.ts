/**
 * Global registry-graph tests (§7, §7.5, §11).
 *
 * Asserts: the global report has the 8 buckets; ok===true on current data with
 * newReferencedUndefined empty; knownBaselineReferencedUndefined equals the committed
 * baseline; the §11 G1-G13 predicates; and ADVERSARIAL cases proving the gate FAILS on a
 * synthetic duplicate id / cycle / NEW referenced-undefined / live->retired / unresolved
 * generator ref. All adversarial cases use in-memory objective lists; no real file is touched.
 *
 * Run:  node --test core/curriculum/registry-graph.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { loadRegistry, type ObjectiveRecord } from "./objective-registry.ts";
import { checkGlobalGraph, loadKnownBaseline } from "./registry-graph.ts";
import { buildCoverageReport } from "./generator-capability.ts";

const registry = loadRegistry();
const baseline = loadKnownBaseline();
const report = checkGlobalGraph(registry.all(), baseline);

/** Minimal helper to build a synthetic approved objective. */
function obj(id: string, over: Partial<ObjectiveRecord> = {}): ObjectiveRecord {
  const [, stageSeg, domainSeg] = id.split(".");
  const stageMap: Record<string, string> = { MIDDLE: "middle-school", IBDPAASL: "ibdp-aasl" };
  const domainMap: Record<string, string> = { RATIO: "proportion", NUM: "number", ALG: "algebra", GEO: "geometry" };
  return {
    objectiveId: id,
    stage: stageMap[stageSeg ?? ""] ?? "middle-school",
    domain: domainMap[domainSeg ?? ""] ?? "proportion",
    objectiveWording: "synthetic",
    answerTypes: ["integer"],
    reviewStatus: "approved",
    version: "1.0.0",
    sourceFile: "(synthetic)",
    ...over,
  };
}

// ---- current-data assertions ----------------------------------------------

test("the global report has the eight buckets", () => {
  for (const key of [
    "errors", "warnings", "knownBaselineReferencedUndefined", "newReferencedUndefined",
    "retiredDependence", "placeholderDependence", "invalidCrossDomain", "danglingRelated",
  ]) {
    assert.ok(key in report, `report must carry bucket '${key}'`);
  }
});

test("ok===true on current data; 81 objectives (70 approved + 11 proposed); newReferencedUndefined empty", () => {
  assert.equal(report.objectiveCount, 81);
  assert.deepEqual(report.errors, [], `errors: ${report.errors.join("; ")}`);
  assert.deepEqual(report.newReferencedUndefined, []);
  assert.equal(report.ok, true);
});

test("knownBaselineReferencedUndefined equals the committed baseline (sorted)", () => {
  assert.deepEqual(report.knownBaselineReferencedUndefined, [...baseline].sort());
  assert.equal(report.knownBaselineReferencedUndefined.length, 5);
});

test("retired/placeholder/invalidCrossDomain are clean on current data", () => {
  assert.deepEqual(report.retiredDependence, []);
  assert.deepEqual(report.placeholderDependence, []);
  assert.deepEqual(report.invalidCrossDomain, []);
});

test("danglingRelated reports the pre-existing lateral links (non-blocking)", () => {
  // relatedObjectives may point at not-yet-defined ids; these are warnings, never errors.
  assert.ok(report.danglingRelated.length >= 0);
  for (const e of report.danglingRelated) assert.ok(!registry.has(e.to));
});

// ---- adversarial cases (synthetic; real files untouched) -------------------

test("ADVERSARIAL: duplicate id fails the gate (G2)", () => {
  const list = [obj("SPI.MIDDLE.RATIO.SIMPLIFY.01"), obj("SPI.MIDDLE.RATIO.SIMPLIFY.01")];
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some((e) => e.includes("duplicate")), r.errors.join("; "));
});

test("ADVERSARIAL: prerequisite cycle fails the gate (G6)", () => {
  const list = [
    obj("SPI.MIDDLE.RATIO.A.01", { prerequisites: ["SPI.MIDDLE.RATIO.B.01"] }),
    obj("SPI.MIDDLE.RATIO.B.01", { prerequisites: ["SPI.MIDDLE.RATIO.A.01"] }),
  ];
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some((e) => e.includes("cycle")), r.errors.join("; "));
});

test("ADVERSARIAL: NEW referenced-undefined prerequisite fails the gate (G5)", () => {
  const list = [obj("SPI.MIDDLE.RATIO.A.01", { prerequisites: ["SPI.MIDDLE.RATIO.NEVER_DEFINED.01"] })];
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, false);
  assert.deepEqual(r.newReferencedUndefined, ["SPI.MIDDLE.RATIO.NEVER_DEFINED.01"]);
  assert.ok(r.errors.some((e) => e.includes("new referenced-undefined")));
});

test("ADVERSARIAL: a baseline referenced-undefined id does NOT fail the gate (G5, §7.5)", () => {
  const knownId = [...baseline][0]!;
  const list = [obj("SPI.MIDDLE.RATIO.A.01", { prerequisites: [knownId] })];
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, true, "a known-baseline reference must not gate");
  assert.deepEqual(r.knownBaselineReferencedUndefined, [knownId]);
  assert.deepEqual(r.newReferencedUndefined, []);
});

test("ADVERSARIAL: live->retired dependence fails the gate (G7)", () => {
  const list = [
    obj("SPI.MIDDLE.RATIO.A.01", { prerequisites: ["SPI.MIDDLE.RATIO.OLD.01"] }),
    obj("SPI.MIDDLE.RATIO.OLD.01", { reviewStatus: "retired" }),
  ];
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, false);
  assert.equal(r.retiredDependence.length, 1);
  assert.ok(r.errors.some((e) => e.includes("live->retired")));
});

test("ADVERSARIAL: approved->placeholder dependence is a WARNING, not an error (G7)", () => {
  const list = [
    obj("SPI.MIDDLE.RATIO.A.01", { prerequisites: ["SPI.MIDDLE.RATIO.PLAN.01"] }),
    obj("SPI.MIDDLE.RATIO.PLAN.01", { reviewStatus: "draft" }),
  ];
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, true);
  assert.equal(r.placeholderDependence.length, 1);
  assert.ok(r.warnings.some((w) => w.includes("placeholder")));
});

test("ADVERSARIAL: bad ID grammar fails the gate (G1)", () => {
  const list = [obj("SPI.MIDDLE.RATIO.SIMPLIFY")]; // missing .NN
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some((e) => e.includes("G1")), r.errors.join("; "));
});

test("ADVERSARIAL: unknown stage segment fails the gate (G1)", () => {
  const list = [obj("SPI.PRIMARY.RATIO.SIMPLIFY.01", { stage: "primary" })];
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some((e) => e.includes("unknown stage segment")), r.errors.join("; "));
});

test("ADVERSARIAL: stage segment/field mismatch fails the gate (G1)", () => {
  const list = [obj("SPI.MIDDLE.RATIO.SIMPLIFY.01", { stage: "ibdp-aasl" })];
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some((e) => e.includes("stage segment")), r.errors.join("; "));
});

test("ADVERSARIAL: unknown domain segment fails the gate (G4)", () => {
  const list = [obj("SPI.MIDDLE.NOPE.SIMPLIFY.01", { domain: "proportion" })];
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some((e) => e.includes("unknown domain segment")), r.errors.join("; "));
});

test("ADVERSARIAL: invalid stage field fails the gate (G3)", () => {
  const list = [obj("SPI.MIDDLE.RATIO.SIMPLIFY.01", { stage: "not-a-stage" })];
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some((e) => e.includes("G3")), r.errors.join("; "));
});

test("ADVERSARIAL: unknown strand fails the gate (G4 present-or-valid)", () => {
  const list = [obj("SPI.MIDDLE.RATIO.SIMPLIFY.01", { strand: "not-a-strand" })];
  const r = checkGlobalGraph(list, baseline);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some((e) => e.includes("unknown strand")), r.errors.join("; "));
});

test("ADVERSARIAL: unresolved generator objective ref fails coverage join (G9-equivalent)", () => {
  // A generator pointing at a missing/retired objective surfaces as an orphanedTask.
  // Build a registry missing one objective the ratio generator maps to.
  const trimmed = registry.all().filter((o) => o.objectiveId !== "SPI.MIDDLE.RATIO.SIMPLIFY.01");
  const reg = loadRegistry; // sanity ref; we rebuild from trimmed below
  void reg;
  const fakeRegistry = {
    all: () => trimmed,
    byId: (id: string) => trimmed.find((o) => o.objectiveId === id),
    has: (id: string) => trimmed.some((o) => o.objectiveId === id),
    byStage: () => [],
    byDomain: () => [],
    byStrand: () => [],
    count: trimmed.length,
  };
  const cov = buildCoverageReport(fakeRegistry, undefined, baseline);
  assert.ok(cov.orphanedTasks.length >= 1, "a missing generator-referenced objective must orphan its task");
  assert.ok(cov.orphanedTasks.some((t) => t.objectiveId === "SPI.MIDDLE.RATIO.SIMPLIFY.01"));
});
