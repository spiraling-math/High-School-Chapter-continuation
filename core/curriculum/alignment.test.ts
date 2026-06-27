/**
 * Standards-alignment tests (§9, §11 G11).
 *
 * Asserts: the pilot conforms to schemas/standard-alignment.schema.json (validated via
 * the bundled Ajv 2020); every linkedSpiObjectiveIds entry resolves to a real, non-retired
 * SPI objective; the pilot status is "proposed"; and the direction is alignment -> SPI
 * (the record carries the SPI ids it links TO). Also exercises the G11 dangling-SPI-id
 * error path with a synthetic record (no real file touched).
 *
 * Run:  node --test core/curriculum/alignment.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import { loadRegistry } from "./objective-registry.ts";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "../..");
const schema = JSON.parse(readFileSync(join(root, "schemas/standard-alignment.schema.json"), "utf8"));
const pilot = JSON.parse(readFileSync(join(root, "curriculum/alignments/pilot.json"), "utf8")) as Record<string, unknown>[];

const ajv = new (Ajv2020 as unknown as typeof import("ajv/dist/2020.js").default)({ allErrors: true, strict: false });
const validate = ajv.compile(schema);

const registry = loadRegistry();

test("the pilot is a tiny set of 1-2 records", () => {
  assert.ok(Array.isArray(pilot));
  assert.ok(pilot.length >= 1 && pilot.length <= 2, "pilot must be 1-2 records (design proof, not a deliverable)");
});

test("every pilot record conforms to standard-alignment.schema.json", () => {
  for (const rec of pilot) {
    const ok = validate(rec);
    assert.ok(ok, `pilot record invalid: ${JSON.stringify(validate.errors)}`);
  }
});

test("every linkedSpiObjectiveIds resolves to a real, non-retired SPI objective (G11)", () => {
  for (const rec of pilot) {
    const links = rec["linkedSpiObjectiveIds"] as string[];
    assert.ok(Array.isArray(links) && links.length >= 1, "each record must carry >=1 SPI link");
    for (const id of links) {
      const o = registry.byId(id);
      assert.ok(o, `linked SPI objective ${id} must exist`);
      assert.notEqual(o.reviewStatus, "retired", `${id} must not be retired`);
    }
  }
});

test("every pilot record has status 'proposed' (enters at proposed, §9.7 rule 4)", () => {
  for (const rec of pilot) assert.equal(rec["status"], "proposed");
});

test("direction is alignment -> SPI (record carries the SPI ids it links TO)", () => {
  for (const rec of pilot) {
    // The record names an external standardSet/standardId and links OUT to SPI ids.
    assert.ok(typeof rec["standardSet"] === "string");
    assert.ok(typeof rec["standardId"] === "string");
    assert.ok(Array.isArray(rec["linkedSpiObjectiveIds"]));
    // It must NOT carry any reverse "linkedStandardIds" on the objective side.
    assert.equal((rec as Record<string, unknown>)["linkedStandardIds"], undefined);
  }
});

test("the pilot links ratio objectives (the family with zero inline alignments)", () => {
  const allLinks = pilot.flatMap((r) => r["linkedSpiObjectiveIds"] as string[]);
  for (const id of allLinks) assert.ok(id.startsWith("SPI.MIDDLE.RATIO."), `${id} must be a ratio objective`);
  // both structural cases present: one-to-one and one-to-many
  assert.ok(pilot.some((r) => (r["linkedSpiObjectiveIds"] as string[]).length === 1));
  assert.ok(pilot.some((r) => (r["linkedSpiObjectiveIds"] as string[]).length >= 2));
});

test("G11 negative: a dangling SPI link is rejected by the resolver", () => {
  const bad = {
    standardSet: "IGCSE-0580", standardVersion: "2025", standardId: "0580/X",
    linkedSpiObjectiveIds: ["SPI.MIDDLE.RATIO.DOES_NOT_EXIST.01"],
    alignmentType: "exact", status: "proposed",
  };
  // schema-valid in shape, but the SPI link must fail to resolve in the registry.
  assert.ok(validate(bad), "shape is schema-valid");
  assert.equal(registry.has("SPI.MIDDLE.RATIO.DOES_NOT_EXIST.01"), false);
});

test("schema rejects an out-of-enum alignmentType / status", () => {
  assert.equal(validate({
    standardSet: "X", standardVersion: "1", standardId: "Y",
    linkedSpiObjectiveIds: ["SPI.MIDDLE.RATIO.SIMPLIFY.01"],
    alignmentType: "bogus", status: "proposed",
  }), false);
  assert.equal(validate({
    standardSet: "X", standardVersion: "1", standardId: "Y",
    linkedSpiObjectiveIds: ["SPI.MIDDLE.RATIO.SIMPLIFY.01"],
    alignmentType: "exact", status: "bogus",
  }), false);
});
