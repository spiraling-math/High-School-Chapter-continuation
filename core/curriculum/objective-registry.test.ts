/**
 * Objective registry (read-only index) tests.
 *
 * Asserts the registry loads all 81 objectives (70 approved from the eleven frozen files + 11
 * PROPOSED pending-review functions objectives from SPI.IBDPAASL.FUNC.json), the query API behaves,
 * and the variable-depth ID grammar parser accepts the real ids (§3, §5).
 *
 * Run:  node --test core/curriculum/objective-registry.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import {
  loadRegistry,
  parseObjectiveId,
  OBJECTIVE_ID_PATTERN,
  OBJECTIVE_FILES,
  APPROVED_OBJECTIVE_FILES,
  PROPOSED_OBJECTIVE_FILES,
} from "./objective-registry.ts";

const registry = loadRegistry();

test("registry loads all 81 objectives from the 11 approved + 1 proposed files", () => {
  assert.equal(registry.count, 81);
  assert.equal(registry.all().length, 81);
  assert.equal(APPROVED_OBJECTIVE_FILES.length, 11, "the frozen Phase-1 approved set stays eleven files");
  assert.deepEqual([...PROPOSED_OBJECTIVE_FILES], ["SPI.IBDPAASL.FUNC.json"]);
  assert.equal(OBJECTIVE_FILES.length, 12);
});

test("approved files hold exactly the 70 approved objectives; the proposed file holds 11 `proposed` records", () => {
  const approved = registry.all().filter((o) => (APPROVED_OBJECTIVE_FILES as readonly string[]).includes(o.sourceFile ?? ""));
  const proposed = registry.all().filter((o) => (PROPOSED_OBJECTIVE_FILES as readonly string[]).includes(o.sourceFile ?? ""));
  assert.equal(approved.length, 70);
  assert.equal(proposed.length, 11);
  assert.ok(approved.every((o) => o.reviewStatus !== "proposed"), "no proposed record may live in an approved file");
  assert.ok(proposed.every((o) => o.reviewStatus === "proposed"), "every functions record is reviewStatus: proposed");
  assert.ok(proposed.every((o) => o.objectiveId.startsWith("SPI.IBDPAASL.FUNC.")));
});

test("every objectiveId is globally unique", () => {
  const ids = registry.all().map((o) => o.objectiveId);
  assert.equal(new Set(ids).size, 81);
});

test("byId / has resolve a real objective", () => {
  const o = registry.byId("SPI.MIDDLE.RATIO.SIMPLIFY.01");
  assert.ok(o, "SIMPLIFY.01 must resolve");
  assert.equal(o.domain, "proportion");
  assert.equal(o.stage, "middle-school");
  assert.ok(registry.has("SPI.MIDDLE.RATIO.SIMPLIFY.01"));
  assert.equal(registry.byId("SPI.MIDDLE.NOPE.MISSING.01"), undefined);
  assert.equal(registry.has("SPI.MIDDLE.NOPE.MISSING.01"), false);
});

test("byStage partitions middle-school (61) and ibdp-aasl (9 approved + 11 proposed)", () => {
  assert.equal(registry.byStage("middle-school").length, 61);
  assert.equal(registry.byStage("ibdp-aasl").length, 20);
});

test("byDomain reflects the §2 census", () => {
  assert.equal(registry.byDomain("geometry").length, 22);
  assert.equal(registry.byDomain("proportion").length, 12);
  assert.equal(registry.byDomain("statistics").length, 11);
  assert.equal(registry.byDomain("functions").length, 11); // proposed (pending-review)
  assert.equal(registry.byDomain("sequences-and-series").length, 9);
  assert.equal(registry.byDomain("measurement").length, 8);
  assert.equal(registry.byDomain("algebra").length, 7);
  assert.equal(registry.byDomain("number").length, 1);
});

test("byStrand resolves a known strand", () => {
  assert.equal(registry.byStrand("ratio-and-proportion").length, 12);
  assert.equal(registry.byStrand("introducing-functions").length, 11);
});

test("all() returns a copy (immutable surface)", () => {
  const a = registry.all();
  a.pop();
  assert.equal(registry.count, 81, "mutating the returned array must not affect the registry");
});

test("ID grammar regex accepts every real id and the depth-5/6 shapes", () => {
  for (const o of registry.all()) {
    assert.ok(OBJECTIVE_ID_PATTERN.test(o.objectiveId), `${o.objectiveId} must match the pattern`);
    const parts = parseObjectiveId(o.objectiveId);
    assert.ok(parts, `${o.objectiveId} must parse`);
  }
  // a depth-5 id (no sub-segment) and a depth-6 id (one sub-segment)
  const five = parseObjectiveId("SPI.MIDDLE.RATIO.SIMPLIFY.01");
  assert.deepEqual(five, { stage: "MIDDLE", domain: "RATIO", sub: [], micro: "SIMPLIFY", nn: "01" });
  const six = parseObjectiveId("SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01");
  assert.deepEqual(six, { stage: "IBDPAASL", domain: "SEQSER", sub: ["ARITH"], micro: "NTH_TERM", nn: "01" });
});

test("ID grammar regex rejects malformed ids", () => {
  for (const bad of [
    "SPI.MIDDLE.RATIO.SIMPLIFY",        // no NN
    "SPI.MIDDLE.RATIO.SIMPLIFY.1",      // single-digit NN
    "SPI.middle.RATIO.SIMPLIFY.01",     // lowercase stage
    "spi.MIDDLE.RATIO.SIMPLIFY.01",     // lowercase prefix
    "SPI.MIDDLE.01",                    // too short
    "SPI.MIDDLE.RATIO.SIMP-LIFY.01",    // hyphen
  ]) {
    assert.equal(OBJECTIVE_ID_PATTERN.test(bad), false, `${bad} must be rejected by the pattern`);
  }
  assert.equal(parseObjectiveId("SPI.MIDDLE.01"), null);
});
