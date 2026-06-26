/**
 * Unit tests for gen.proportion.ratio (TypeScript mirror).
 *
 * Covers: ratio math + parser + both checker vocabularies; all 12 tasks generate + validate;
 * per-task answer types; the interaction policy (best_buy MC-only rejects FR; FR-ineligible tasks
 * reject MC; MC-eligible accept MC) via InteractionNotSupported; role-based leakage; the 16 diagnostics.
 *
 * Run:  node --test domains/proportion/ratio.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { Rational } from "../../core/exact-math/rational.ts";
import * as RC from "./ratio-core.ts";
import * as RM from "./ratio-misconceptions.ts";
import {
  generate,
  validate,
  serialize,
  describe,
  RATIO_TASKS,
  OBJECTIVE_BY_TASK,
  MC_ELIGIBLE_TASKS,
  MC_ONLY_TASKS,
  GENERATOR_ID,
  GENERATOR_VERSION,
  VALIDATOR_VERSION,
  InteractionNotSupported,
} from "./ratio.ts";

// --------------------------------------------------------------------------- //
// Ratio math (owner 6)
// --------------------------------------------------------------------------- //
test("gcdList / simplifyParts preserve order and reduce by the full gcd", () => {
  assert.equal(RC.gcdList([12, 10, 8]), 2);
  assert.deepEqual(RC.simplifyParts([12, 10, 8]), [6, 5, 4]);
  assert.deepEqual(RC.simplifyParts([4, 6]), [2, 3]);
  assert.deepEqual(RC.simplifyParts([3, 2]), [3, 2]); // 2:3 != 3:2 (order preserved)
  assert.equal(RC.gcdList([7]), 7);
  assert.equal(RC.gcdList([0, 0]), 1); // gcd_list falls back to 1
});

test("ratiosEqual is order-sensitive; cross-multiply test", () => {
  assert.ok(RC.ratiosEqual([2, 3], [4, 6]));
  assert.ok(!RC.ratiosEqual([2, 3], [3, 2]));
  assert.ok(!RC.ratiosEqual([2, 3], [2, 3, 5]));
  assert.ok(RC.crossMultiplyEqual(2, 3, 4, 6));
  assert.ok(!RC.crossMultiplyEqual(2, 3, 3, 2));
});

test("share / missingPart / inverse are integer-exact or null", () => {
  assert.deepEqual(RC.share(30, [2, 3]), [12, 18]);
  assert.equal(RC.share(31, [2, 3]), null); // not divisible
  assert.equal(RC.missingPart(12, 0, 1, [2, 3]), 18);
  assert.equal(RC.missingPart(13, 0, 1, [2, 3]), null); // 2 does not divide 13
  assert.equal(RC.inverseProportion(6, 4, 3), 8); // 6*4=24, /3 = 8
  assert.equal(RC.inverseProportion(6, 4, 5), null); // 24 not divisible by 5
});

test("unitRate / directProportion / scaleValue produce exact Rationals", () => {
  assert.ok(RC.unitRate(7, 2).equals(new Rational(7, 2)));
  assert.ok(RC.directProportion(10, 4, 6).equals(new Rational(15, 1)));
  assert.ok(RC.scaleValue(8, new Rational(3, 4)).equals(new Rational(6, 1)));
});

// --------------------------------------------------------------------------- //
// Parser (owner G) — full branch coverage
// --------------------------------------------------------------------------- //
test("parseRatio accepts clean ASCII-colon ratios", () => {
  assert.deepEqual(RC.parseRatio("2:3"), [[2, 3], null]);
  assert.deepEqual(RC.parseRatio(" 2 : 3 "), [[2, 3], null]);
  assert.deepEqual(RC.parseRatio("4:6:10"), [[4, 6, 10], null]);
});

test("parseRatio rejects with the exact result-code vocabulary", () => {
  assert.deepEqual(RC.parseRatio(""), [null, "malformed-response"]);
  assert.deepEqual(RC.parseRatio(null), [null, "malformed-response"]);
  assert.deepEqual(RC.parseRatio("23"), [null, "malformed-response"]); // no colon
  assert.deepEqual(RC.parseRatio("2:3:5:7"), [null, "wrong-number-of-parts"]);
  assert.deepEqual(RC.parseRatio("2:"), [null, "malformed-response"]); // missing part
  assert.deepEqual(RC.parseRatio("2::3"), [null, "malformed-response"]);
  assert.deepEqual(RC.parseRatio("2.5:3"), [null, "unsupported-term"]); // decimal
  assert.deepEqual(RC.parseRatio("0:3"), [null, "zero-or-negative-part"]);
  assert.deepEqual(RC.parseRatio("-2:3"), [null, "zero-or-negative-part"]);
  assert.deepEqual(RC.parseRatio("2x:3"), [null, "unparsed-trailing-text"]);
  assert.deepEqual(RC.parseRatio("2 cats:3"), [null, "unparsed-trailing-text"]);
  assert.deepEqual(RC.parseRatio("2,3"), [null, "unsupported-term"]); // comma
  assert.deepEqual(RC.parseRatio("2 to 3"), [null, "unsupported-term"]); // word form
  assert.deepEqual(RC.parseRatio("2∶ 3"), [null, "unsupported-term"]); // U+2236
});

test("ASCII-anchored parser: unicode digits + oversized terms -> unsupported-term (Py<->TS parity corpus)", () => {
  // Regression for the adversarial-review CRITICAL parity break. oracle/tests/test_ratio.py pins the SAME
  // corpus + expected codes; pinning both engines asserts byte-for-byte agreement on the GRADING path,
  // which the serialize-only golden/parity fixtures cannot exercise (generated items never carry unicode
  // digits — only learner free-text does).
  const unsupported = ["٢:٣", "３:４", "२:३", "𝟚:𝟛", "۲:۳", "๒:๓", "5:３", "２:40", "١٢:٣",
    "1000000000000000000000:3", "9007199254740993:9007199254740993",
    "2:33333333333333333333333333", "2∶3", "2 to 3", "2,3", "2.5:3"];
  for (const s of unsupported) {
    assert.equal(RC.checkRatio([2, 3], s).code, "unsupported-term", JSON.stringify(s));
  }
  assert.equal(RC.checkRatio([2, 3], "2:3").code, "correct");
  assert.equal(RC.checkRatio([2, 3], "4:6").code, "equivalent-not-simplified");
});

// --------------------------------------------------------------------------- //
// Checkers — both vocabularies (owner F)
// --------------------------------------------------------------------------- //
test("checkRatio: correct / equivalent-not-simplified / wrong-order / wrong-ratio", () => {
  assert.deepEqual(RC.checkRatio([2, 3], "2:3", true), { code: "correct", partial: false });
  assert.deepEqual(RC.checkRatio([2, 3], "4:6", true), { code: "equivalent-not-simplified", partial: true });
  assert.deepEqual(RC.checkRatio([2, 3], "4:6", false), { code: "correct", partial: false });
  assert.deepEqual(RC.checkRatio([2, 3], "3:2", true), { code: "wrong-order", partial: false });
  assert.deepEqual(RC.checkRatio([2, 3], "5:7", true), { code: "wrong-ratio", partial: false });
  assert.deepEqual(RC.checkRatio([2, 3], "2:3:5", true), { code: "wrong-number-of-parts", partial: false });
  assert.deepEqual(RC.checkRatio([2, 3], "oops", true), { code: "malformed-response", partial: false });
});

test("checkChoice: correct / wrong-choice / malformed-response", () => {
  assert.equal(RC.checkChoice("B", "b"), "correct");
  assert.equal(RC.checkChoice("B", "A"), "wrong-choice");
  assert.equal(RC.checkChoice("B", ""), "malformed-response");
  assert.equal(RC.checkChoice("B", "12"), "malformed-response");
});

test("result-code vocabularies are exactly the documented tuples", () => {
  assert.deepEqual([...RC.RATIO_RESULT_CODES], [
    "correct",
    "equivalent-not-simplified",
    "wrong-order",
    "wrong-ratio",
    "wrong-number-of-parts",
    "zero-or-negative-part",
    "unsupported-term",
    "unparsed-trailing-text",
    "malformed-response",
  ]);
  assert.deepEqual([...RC.CHOICE_RESULT_CODES], ["correct", "wrong-choice", "malformed-response"]);
});

// --------------------------------------------------------------------------- //
// Floor-division / non-negative remainder discipline
// --------------------------------------------------------------------------- //
test("inverseProportion uses exact floor semantics (positive operands only)", () => {
  // q1*v1 divisible by q2 -> exact; mirror of Python //.
  assert.equal(RC.inverseProportion(4, 9, 6), 6); // 36/6
});

// --------------------------------------------------------------------------- //
// All 12 tasks generate + validate (free-response)
// --------------------------------------------------------------------------- //
test("all 12 tasks generate and validate across many seeds (free-response)", () => {
  assert.equal(RATIO_TASKS.length, 12);
  for (const task of RATIO_TASKS) {
    const fr = MC_ONLY_TASKS.includes(task) ? "multiple-choice" : "free-response";
    for (let seed = 1; seed <= 25; seed++) {
      const item = generate(seed, { interactionType: fr, task });
      const v = validate(item);
      assert.equal(v.valid, true, `validate ${task} seed ${seed}: ${JSON.stringify(v.checks.filter((c: { ok: boolean }) => !c.ok))}`);
      assert.equal(item.objectiveIds[0], OBJECTIVE_BY_TASK[task]);
    }
  }
});

test("validate returns BOTH shapes: {valid, checks[].ok} and {status, checks[].result}", () => {
  const item = generate(1, { interactionType: "free-response", task: "simplify" });
  const v = validate(item);
  assert.equal(typeof v.valid, "boolean");
  assert.equal(v.status, v.valid ? "pass" : "fail");
  assert.equal(v.validatorVersion, VALIDATOR_VERSION);
  for (const c of v.checks) {
    assert.ok("ok" in c && "result" in c);
    assert.equal(c.result, c.ok ? "pass" : "fail");
  }
});

// --------------------------------------------------------------------------- //
// Per-task answer types (owner D)
// --------------------------------------------------------------------------- //
test("each task carries the documented answer type", () => {
  const expect: Record<string, string> = {
    simplify: "ratio",
    write_from_quantities: "ratio",
    fraction_to_ratio: "ratio",
    ratio_to_fraction: "exact-rational",
    unit_rate: "exact-rational",
    simple_scale: "exact-rational",
    direct_proportion: "exact-rational",
    missing_part: "integer",
    inverse_proportion: "integer",
    share_two_part: "table-completion",
    share_three_part: "table-completion",
    best_buy: "multiple-choice",
  };
  for (const task of RATIO_TASKS) {
    let found: string | null = null;
    for (let seed = 1; seed <= 40 && found === null; seed++) {
      const interaction = MC_ONLY_TASKS.includes(task) ? "multiple-choice" : "free-response";
      const item = generate(seed, { interactionType: interaction, task });
      const t = item.answer.type as string;
      // direct_proportion/unit_rate/simple_scale can collapse to integer when whole; the doc type is
      // the family's general type, but integer is an accepted exact specialisation.
      if (["direct_proportion", "unit_rate", "simple_scale", "ratio_to_fraction"].includes(task)) {
        assert.ok(t === "exact-rational" || t === "integer", `${task} type ${t}`);
        found = t;
      } else {
        assert.equal(t, expect[task], `${task} answer type`);
        found = t;
      }
    }
    assert.ok(found !== null);
  }
});

// --------------------------------------------------------------------------- //
// Interaction policy (owner C) via InteractionNotSupported
// --------------------------------------------------------------------------- //
test("best_buy is MC-only: rejects an explicit free-response request", () => {
  assert.throws(
    () => generate(1, { interactionType: "free-response", task: "best_buy" }),
    InteractionNotSupported,
  );
  // default (no interactionType) yields multiple-choice
  const def = generate(1, { task: "best_buy" });
  assert.equal(def.interactionType, "multiple-choice");
});

test("FR-only tasks reject an explicit multiple-choice request", () => {
  const frOnly = RATIO_TASKS.filter((t) => !MC_ELIGIBLE_TASKS.includes(t));
  assert.ok(frOnly.length > 0);
  for (const task of frOnly) {
    assert.throws(
      () => generate(1, { interactionType: "multiple-choice", task }),
      InteractionNotSupported,
      `${task} should reject MC`,
    );
  }
});

test("MC-eligible non-best_buy tasks accept multiple-choice and assemble 4 options", () => {
  const eligible = MC_ELIGIBLE_TASKS.filter((t) => !MC_ONLY_TASKS.includes(t));
  for (const task of eligible) {
    let made = false;
    for (let seed = 1; seed <= 60 && !made; seed++) {
      const item = generate(seed, { interactionType: "multiple-choice", task });
      assert.equal(item.interactionType, "multiple-choice");
      assert.equal(item.options.length, 4);
      assert.equal(item.options.filter((o: { correct: boolean }) => o.correct).length, 1);
      assert.equal(item.distractors.length, 3);
      assert.equal(validate(item).valid, true, `MC validate ${task} seed ${seed}`);
      made = true;
    }
    assert.ok(made, `${task} should produce an MC item`);
  }
});

test("an unsupported interactionType string raises InteractionNotSupported", () => {
  assert.throws(
    () => generate(1, { interactionType: "drag-and-drop", task: "simplify" }),
    InteractionNotSupported,
  );
});

// --------------------------------------------------------------------------- //
// Role-based leakage (owner J)
// --------------------------------------------------------------------------- //
test("student figure marks the unknown with '?' and never its value; key overlay is additive", () => {
  for (const task of ["share_two_part", "missing_part", "direct_proportion", "best_buy"]) {
    const interaction = MC_ONLY_TASKS.includes(task) ? "multiple-choice" : "free-response";
    const item = generate(3, { interactionType: interaction, task });
    const student = item.media[0].svg as string;
    const key = item.media[0].spec.answerKeySvg as string;
    assert.ok(student.indexOf('<g class="rt-student">') !== -1, `${task} student group`);
    assert.ok(student.indexOf('<g class="rt-overlay">') === -1, `${task} student has no overlay`);
    assert.ok(key.indexOf('<g class="rt-overlay">') !== -1, `${task} key overlay`);
    assert.ok(key.indexOf('<g class="rt-student">') === -1, `${task} key has no student group`);
    // shared base group is byte-identical
    const base = (s: string): string => {
      const a = s.indexOf('<g class="rt-base">');
      const b = s.indexOf("</g>", a);
      return s.slice(a, b);
    };
    assert.equal(base(student), base(key), `${task} shared base`);
    assert.notEqual(student, key);
  }
});

// --------------------------------------------------------------------------- //
// Diagnostics (owner 10) — the 16 misconceptions
// --------------------------------------------------------------------------- //
test("the registry declares exactly 16 MISC.RATIO.* misconceptions", () => {
  assert.equal(RM.MISCONCEPTIONS.length, 16);
  assert.equal(RM.ALL_IDS.length, 16);
  assert.ok(RM.ALL_IDS.every((id) => id.startsWith("MISC.RATIO.")));
  assert.equal(new Set(RM.ALL_IDS).size, 16);
});

test("diagnosticsFor returns recomputable, applicable diagnostics with the expected result code", () => {
  // simplify: parts 12:10:8 -> NOT_SIMPLIFIED / EQUIVALENT_NOT_SIMPLIFIED / ADDS_PARTS_WRONG.
  const ds = RM.diagnosticsFor("simplify", { task: "simplify", parts: [12, 10, 8] });
  assert.ok(ds.length >= 1);
  for (const d of ds) {
    assert.ok(RM.ALL_IDS.includes(d.misconceptionId));
    assert.ok(d.observableError && d.feedback && d.expectedResultCode);
    // a ratio diagnostic's predicted display must NOT equal the correct answer
    if (d.predictedCanonical && "parts" in d.predictedCanonical) {
      assert.notEqual(RC.formatRatio(d.predictedCanonical.parts), "6:5:4");
    }
  }
});

test("every task surfaces at least one diagnostic for a representative item", () => {
  const probes: Record<string, Record<string, unknown>> = {
    simplify: { task: "simplify", parts: [12, 10, 8] },
    write_from_quantities: { task: "write_from_quantities", quantities: [4, 6], labels: ["a", "b"] },
    ratio_to_fraction: { task: "ratio_to_fraction", parts: [2, 3], partIndex: 0 },
    fraction_to_ratio: { task: "fraction_to_ratio", num: 2, den: 5 },
    share_two_part: { task: "share_two_part", total: 30, parts: [2, 3], labels: ["A", "B"] },
    share_three_part: { task: "share_three_part", total: 60, parts: [1, 2, 3], labels: ["A", "B", "C"] },
    missing_part: { task: "missing_part", parts: [2, 3], knownIndex: 0, missingIndex: 1, knownValue: 12 },
    direct_proportion: { task: "direct_proportion", quantity: 4, total: 10, target: 6 },
    inverse_proportion: { task: "inverse_proportion", q1: 6, v1: 4, q2: 3 },
    unit_rate: { task: "unit_rate", total: 7, quantity: 2 },
    best_buy: {
      task: "best_buy",
      correctLabel: "B",
      options: [
        { label: "A", packSize: 6, totalAmount: 72 },
        { label: "B", packSize: 10, totalAmount: 40 },
      ],
    },
    simple_scale: { task: "simple_scale", value: 8, factorNum: 3, factorDen: 4 },
  };
  for (const task of RATIO_TASKS) {
    const ds = RM.diagnosticsFor(task, probes[task] as Record<string, unknown>);
    assert.ok(ds.length >= 1, `${task} should surface a diagnostic`);
  }
});

// --------------------------------------------------------------------------- //
// describe() + constants
// --------------------------------------------------------------------------- //
test("describe() reports the generator metadata", () => {
  const d = describe();
  assert.equal(d.generatorId, GENERATOR_ID);
  assert.equal(d.version, GENERATOR_VERSION);
  assert.equal(GENERATOR_ID, "gen.proportion.ratio");
  assert.equal(d.tasks.length, 12);
  assert.deepEqual(d.answerTypes, ["ratio", "exact-rational", "integer", "table-completion", "multiple-choice"]);
  assert.equal(d.approvalStatus, "pending-review");
});

test("serialize is stable and round-trips through JSON", () => {
  const item = generate(42, { interactionType: "free-response", task: "share_two_part" });
  const s = serialize(item);
  assert.equal(serialize(item), s);
  const parsed = JSON.parse(s);
  assert.equal(parsed.itemId, "ITEM-RATIO-share_two_part-42");
});
