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

test("canonical-first 'algebraic-expression' and 'interval' answers: shape enforced additively (gen.functions.foundations)", () => {
  const base = genArith(3, { answerType: "integer" }) as Record<string, Json>;
  const withAnswer = (answer: Json): Record<string, Json> => ({ ...base, answer });
  // algebraic-expression: the polynomial object IS the canonical value
  assert.deepEqual(validateItem(withAnswer({ type: "algebraic-expression", display: "4x^2 - 12x + 10",
    canonical: { variable: "x", coefficients: [{ num: 10, den: 1 }, { num: -12, den: 1 }, { num: 4, den: 1 }] } })), []);
  assert.ok(validateItem(withAnswer({ type: "algebraic-expression", canonical: "4x^2 - 12x + 10" })).length > 0, "a string canonical is rejected");
  assert.ok(validateItem(withAnswer({ type: "algebraic-expression", canonical: { variable: "t", coefficients: [{ num: 1, den: 1 }] } })).length > 0, "variable must be x");
  assert.ok(validateItem(withAnswer({ type: "algebraic-expression", canonical: { variable: "x", coefficients: [] } })).length > 0, "at least one coefficient");
  assert.ok(validateItem(withAnswer({ type: "algebraic-expression", canonical: { variable: "x", coefficients: [{ num: 1, den: 0 }] } })).length > 0, "den >= 1");
  // interval: the real-subset descriptor, one exact field set per kind
  const good: Json[] = [
    { kind: "reals" },
    { kind: "ray", variable: "x", endpoint: { num: 2, den: 1 }, inclusive: true, direction: "ge" },
    { kind: "bounded", variable: "y", lo: { num: -1, den: 1 }, hi: { num: 4, den: 1 }, loInclusive: true, hiInclusive: true },
    { kind: "reals-except", variable: "x", points: [{ num: 3, den: 1 }] },
  ];
  for (const c of good) assert.deepEqual(validateItem(withAnswer({ type: "interval", canonical: c, display: "d" })), [], JSON.stringify(c));
  assert.ok(validateItem(withAnswer({ type: "interval", canonical: { kind: "ray", variable: "x", endpoint: { num: 2, den: 1 } } })).length > 0, "ray needs inclusive + direction");
  assert.ok(validateItem(withAnswer({ type: "interval", canonical: { kind: "reals", variable: "x" } })).length > 0, "reals carries no other field");
  assert.ok(validateItem(withAnswer({ type: "interval", canonical: { kind: "segment" } })).length > 0, "unknown kind");
  assert.ok(validateItem(withAnswer({ type: "interval", canonical: { kind: "ray", variable: "z", endpoint: { num: 2, den: 1 }, inclusive: true, direction: "ge" } })).length > 0, "variable x|y only");
  assert.ok(validateItem(withAnswer({ type: "interval", canonical: { kind: "reals-except", variable: "x", points: [] } })).length > 0, "at least one excluded point");
  // an integer answer is untouched by the new rules
  assert.deepEqual(validateItem(base), []);
});
