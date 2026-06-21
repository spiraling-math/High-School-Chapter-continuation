/**
 * Runtime schema-validation tests (Node built-in test runner).
 * Run:  node --test core/schema/runtime-validate.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { generate as genArith } from "../../domains/sequences/arithmetic.ts";
import { generate as genGeo } from "../../domains/sequences/geometric.ts";
import { validateItem, assertValidItem, SchemaValidationError } from "./runtime-validate.ts";
import type { Json } from "../serialization/canonical.ts";

test("real generated items pass the schema (both generators, MC + free-response)", () => {
  for (let s = 1; s <= 40; s++) {
    for (const mode of ["integer", "multiple-choice"] as const) {
      assert.deepEqual(validateItem(genArith(s, { answerType: mode })), [], `arith seed ${s} ${mode}`);
      assert.deepEqual(validateItem(genGeo(s, { answerType: mode })), [], `geo seed ${s} ${mode}`);
    }
  }
});

test("a missing required field is reported with path, expected and received", () => {
  const item = genArith(3, { answerType: "integer" }) as Record<string, Json>;
  delete item["provenance"];
  const errs = validateItem(item);
  assert.ok(errs.length > 0);
  const e = errs.find((x) => x.message.includes("provenance") || x.expected.includes("provenance"));
  assert.ok(e, "reports the missing provenance");
  assert.ok(e!.itemId.startsWith("ITEM-"), "carries the item id");
  assert.equal(e!.generatorId, "gen.sequences.arithmetic");
});

test("an unknown extra property is rejected (additionalProperties:false)", () => {
  const item = genArith(5, { answerType: "integer" }) as Record<string, Json>;
  item["bogusField"] = 1;
  const errs = validateItem(item);
  assert.ok(errs.some((e) => e.expected.includes("bogusField") || e.received !== undefined), "rejects unknown field");
});

test("a wrong-typed field reports expected vs received", () => {
  const item = genArith(9, { answerType: "integer" }) as Record<string, Json>;
  (item["objectiveIds"] as unknown) = "not-an-array";
  const errs = validateItem(item);
  const e = errs.find((x) => x.field === "/objectiveIds");
  assert.ok(e, "reports objectiveIds");
  assert.ok(e!.expected.includes("array"));
  assert.equal(e!.received, '"not-an-array"');
});

test("assertValidItem throws SchemaValidationError carrying the errors", () => {
  const item = genArith(2, { answerType: "integer" }) as Record<string, Json>;
  delete item["answer"];
  assert.throws(() => assertValidItem(item, "unit-test"), (err: unknown) => {
    assert.ok(err instanceof SchemaValidationError);
    assert.ok((err as SchemaValidationError).errors.length > 0);
    assert.match((err as Error).message, /unit-test/);
    return true;
  });
});
