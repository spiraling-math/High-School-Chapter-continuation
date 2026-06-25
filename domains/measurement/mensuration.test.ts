/**
 * gen.measurement.mensuration v1.0.0 — TypeScript behaviour tests (mirror the Python oracle gates).
 * Run:  node --test domains/measurement/mensuration.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { generate, validate, solve, TASKS, RATIONAL_ANSWER_TASKS, UnsupportedInteractionError } from "./mensuration.ts";
import { checkResponse, makeLength, makeArea, formatQuantity, formatValue } from "./mensuration-units.ts";
import { Rational } from "../../core/exact-math/rational.ts";
import { diagnosticsFor, diagnose, MISCONCEPTIONS, _BY_ID } from "./mensuration-misconceptions.ts";

test("unit checker: structural codes (owner D)", () => {
  const Lcm = makeLength(15, "cm"), Acm = makeArea(24, "cm");
  assert.equal(checkResponse("30/2 cm", Lcm).code, "correct");
  assert.equal(checkResponse("24 cm^2", Acm).code, "correct");
  assert.equal(checkResponse("24 cm²", Acm).code, "correct");
  assert.equal(checkResponse("15", Lcm).code, "missing-unit");
  assert.equal(checkResponse("100 cm", makeLength(1, "m")).code, "wrong-base-unit"); // no conversion
  assert.equal(checkResponse("24 cm", Acm).code, "wrong-exponent");                   // linear for area
  assert.equal(checkResponse("15 cm^2", Lcm).code, "wrong-exponent");                 // square for length
  assert.equal(checkResponse("24 m^2", Lcm).code, "wrong-dimension");
  assert.equal(checkResponse("16 cm", Lcm).code, "incorrect-value");
  assert.equal(checkResponse("15 cm long", Lcm).code, "malformed-response");
});

test("answer encoding shape (owner B)", () => {
  const half = makeLength(new Rational(15, 2), "cm");
  assert.equal(formatQuantity(half), "15/2 cm");
  assert.equal(formatValue(new Rational(24, 1)), "24");
});

test("validity sweep: every item validates; FR only", () => {
  let invalid = 0;
  for (let s = 0; s < 600; s++) if (validate(generate(s)).status !== "pass") invalid++;
  assert.equal(invalid, 0);
});

test("multiple-choice rejected for every task (owner C)", () => {
  for (const t of TASKS) {
    assert.throws(() => generate(1, { task: t, interactionType: "multiple-choice" }), UnsupportedInteractionError);
  }
});

test("rational answers only for the triangle tasks (owner F)", () => {
  for (let s = 0; s < 1500; s++) {
    const it = generate(s) as { answer: { canonical: { den: number } }; params: { task: string } };
    if (it.answer.canonical.den !== 1) assert.ok(RATIONAL_ANSWER_TASKS.includes(it.params.task));
  }
});

test("misconceptions: all exercised, recomputation sound, diagnose routes (owner K)", () => {
  const cov = new Set<string>();
  for (let s = 1; s <= 2000; s++) {
    const it = generate(s) as { params: Record<string, unknown> };
    const t = it.params.task as string;
    const a = solve(t, it.params);
    for (const d of diagnosticsFor(t, it.params, a)) {
      cov.add(d.id);
      const rule = _BY_ID[d.id]!;
      if (d.predictedResponse !== null && rule.expectedCode) {
        assert.equal(checkResponse(d.predictedResponse, a).code, rule.expectedCode, d.id);
      }
    }
  }
  assert.equal(cov.size, MISCONCEPTIONS.length);
  const it = generate(7) as { params: Record<string, unknown> };
  const a = solve(it.params.task as string, it.params);
  assert.equal(diagnose(it.params.task as string, it.params, a, formatValue(a.value))!.id, "MISC.MENS.RIGHT_NUMBER_NO_UNIT");
  assert.equal(diagnose(it.params.task as string, it.params, a, formatQuantity(a)), null);
});
