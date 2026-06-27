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
// Regression guards for the five confirmed v1.0.0 defects (mirror of oracle/tests/test_ratio.py)
// --------------------------------------------------------------------------- //
test("DEFECT 4: best_buy MC option displays are pairwise distinct across many seeds", () => {
  for (let seed = 1; seed <= 3000; seed++) {
    const item = generate(seed, { task: "best_buy" });
    const disps = (item.options as { display: string }[]).map((o) => o.display);
    assert.equal(new Set(disps).size, disps.length, `seed ${seed} duplicate displays ${JSON.stringify(disps)}`);
    const names: Record<string, boolean> = {};
    for (const c of validate(item).checks as { name: string; ok: boolean }[]) {
      names[c.name] = c.ok;
    }
    assert.equal(names["mc-option-displays-distinct"], true, `seed ${seed} displays-distinct check`);
  }
  for (const seed of [95, 271, 314, 549, 748, 992]) {
    const item = generate(seed, { task: "best_buy" });
    const disps = (item.options as { display: string }[]).map((o) => o.display);
    assert.equal(new Set(disps).size, disps.length, `formerly-dup seed ${seed}: ${JSON.stringify(disps)}`);
  }
});

test("DEFECT 5: a no-task free-response request never raises and never picks an MC-only task", () => {
  for (let seed = 1; seed <= 2500; seed++) {
    const item = generate(seed, { interactionType: "free-response" });
    assert.equal(item.interactionType, "free-response", `seed ${seed}`);
    assert.ok(!MC_ONLY_TASKS.includes(item.params.task as string), `seed ${seed} picked MC-only task`);
  }
});

test("DEFECT 6/7: every declared band in [lo,hi] is reachable for every task", () => {
  const TASK_BANDS: Record<string, [number, number]> = {
    simplify: [1, 3],
    write_from_quantities: [1, 3],
    ratio_to_fraction: [2, 3],
    fraction_to_ratio: [2, 3],
    share_two_part: [2, 3],
    share_three_part: [3, 4],
    missing_part: [2, 3],
    direct_proportion: [2, 4],
    inverse_proportion: [3, 4],
    unit_rate: [2, 3],
    best_buy: [3, 4],
    simple_scale: [2, 4],
  };
  const per: Record<string, Record<number, number>> = {};
  for (const t of RATIO_TASKS) per[t] = {};
  for (let seed = 1; seed <= 6000; seed++) {
    const item = generate(seed);
    const t = item.params.task as string;
    const b = item.difficulty.overallBand as number;
    per[t]![b] = (per[t]![b] || 0) + 1;
  }
  for (const task of RATIO_TASKS) {
    const [lo, hi] = TASK_BANDS[task] as [number, number];
    for (let band = lo; band <= hi; band++) {
      assert.ok((per[task]![band] || 0) > 0, `${task} band ${band} in [${lo},${hi}] is unreachable`);
    }
  }
});

test("DEFECT 8: the two omitted reverse objectiveRelationships are present", () => {
  const byId: Record<string, { objectiveRelationships: string[] }> = {};
  for (const m of RM.MISCONCEPTIONS) byId[m.misconceptionId as string] = m;
  assert.ok(
    byId["MISC.RATIO.NOT_SIMPLIFIED"]!.objectiveRelationships.includes(
      "SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01",
    ),
  );
  assert.ok(
    byId["MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE"]!.objectiveRelationships.includes(
      "SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01",
    ),
  );
});

// --------------------------------------------------------------------------- //
// v1.0.1 owner REVISE corrections #3/#4/#5/#6 (mirror of oracle/tests/test_ratio.py)
// --------------------------------------------------------------------------- //
const COUNT_NOUNS = new Set(["books", "apples", "pencils", "eggs"]);

test("version bump: generator + validator are 1.0.2; item schemaVersion stays 1.0.0", () => {
  assert.equal(GENERATOR_VERSION, "1.0.2");
  assert.equal(VALIDATOR_VERSION, "1.0.2");
  const item = generate(1, { task: "simplify" });
  assert.equal(item.schemaVersion, "1.0.0");
  assert.equal(item.generatorVersion, "1.0.2");
  assert.equal(validate(item).validatorVersion, "1.0.2");
});

test("CORRECTION #3: no fractional count noun in direct_proportion / unit_rate; context checks pass", () => {
  for (let seed = 1; seed <= 3000; seed++) {
    for (const task of ["direct_proportion", "unit_rate"]) {
      const it = generate(seed, { task });
      const p = it.params;
      const amount = (task === "direct_proportion" ? p.givenLabel : p.amountLabel) as string;
      const den = it.answer.canonical.den as number;
      if (COUNT_NOUNS.has(amount)) {
        assert.equal(den, 1, `${task} seed ${seed}: fractional ${amount}`);
      }
      const names: Record<string, boolean> = {};
      for (const c of validate(it).checks as { name: string; ok: boolean }[]) names[c.name] = c.ok;
      for (const chk of [
        "context-answer-compatible",
        "discrete-count-answer-integer",
        "rational-answer-uses-continuous-or-average-context",
        "no-fractional-books-students-sheets-or-people",
      ]) {
        assert.equal(names[chk], true, `${task} seed ${seed} ${chk}`);
      }
      if (task === "unit_rate") assert.equal(names["unit-rate-context-allows-rational"], true);
    }
  }
});

test("CORRECTION #4: best_buy marks lowest cost per item; cost-like tokens, no currency", () => {
  for (let seed = 1; seed <= 3000; seed++) {
    const it = generate(seed, { task: "best_buy" });
    const p = it.params;
    const instr = it.prompt.instruction as string;
    assert.ok(instr.indexOf("tokens") !== -1, `seed ${seed} missing tokens`);
    for (const sym of ["$", "£", "€", "¥"]) assert.equal(instr.indexOf(sym), -1, `seed ${seed} currency ${sym}`);
    assert.ok(instr.indexOf(`the lowest cost per ${p.item}`) !== -1, `seed ${seed} prompt wording`);
    // correct option is the strict-min tokens-per-item
    const rates: Record<string, Rational> = {};
    for (const o of p.options as { label: string; tokenCost: number; itemCount: number }[]) {
      rates[o.label] = new Rational(o.tokenCost, o.itemCount);
    }
    let min: Rational | null = null;
    for (const r of Object.values(rates)) if (min === null || r.num * min.den < min.num * r.den) min = r;
    const winners = Object.keys(rates).filter((l) => (rates[l] as Rational).equals(min as Rational));
    assert.equal(winners.length, 1, `seed ${seed} not unique min`);
    assert.equal(p.correctLabel, winners[0], `seed ${seed} correct != min`);
    const names: Record<string, boolean> = {};
    for (const c of validate(it).checks as { name: string; ok: boolean }[]) names[c.name] = c.ok;
    for (const chk of [
      "best-buy-rate-direction-consistent",
      "best-buy-context-has-cost-like-denominator",
      "best-buy-strict-minimum-cost-per-unit",
      "best-buy-prompt-matches-validator",
      "best-buy-feedback-matches-rate-direction",
      "no-lowest-product-amount-as-best-value",
    ]) {
      assert.equal(names[chk], true, `seed ${seed} ${chk}`);
    }
  }
});

test("CORRECTION #4: best_buy diagnostics predict WRONG options only", () => {
  for (let seed = 1; seed <= 1500; seed++) {
    const it = generate(seed, { task: "best_buy" });
    const p = it.params;
    for (const d of RM.diagnosticsFor("best_buy", p)) {
      assert.notEqual(d.predictedResponse, p.correctLabel, `seed ${seed} diagnostic hits correct option`);
    }
  }
});

test("CORRECTION #5: simple_scale is dimensionless, grammatical, bare-number answer", () => {
  for (let seed = 1; seed <= 3000; seed++) {
    const it = generate(seed, { task: "simple_scale" });
    const p = it.params;
    const instr = it.prompt.instruction as string;
    for (const tok of ["cm", "km", "centimetre", "kilometre", "metre", " m "]) {
      assert.equal(instr.indexOf(tok), -1, `seed ${seed} measurement unit ${tok}`);
    }
    assert.ok(!/\b1 (model|plan|drawing|map|real|actual|ground) units\b/.test(instr), `seed ${seed} bad singular`);
    const f = new Rational(it.answer.canonical.num as number, it.answer.canonical.den as number);
    assert.ok(f.equals(Rational.from(p.value as number).mul(new Rational(p.factorNum as number, p.factorDen as number))));
    const names: Record<string, boolean> = {};
    for (const c of validate(it).checks as { name: string; ok: boolean }[]) names[c.name] = c.ok;
    for (const chk of [
      "scale-unit-wording-grammatical",
      "singular-plural-units-correct",
      "scale-answer-contract-matches-prompt",
      "measurement-unit-answer-not-bare-number",
      "no-cross-unit-conversion-in-v1",
    ]) {
      assert.equal(names[chk], true, `seed ${seed} ${chk}`);
    }
  }
});

test("CORRECTION #6: diagnostic predictions are distinct per item (collision deduped)", () => {
  for (let seed = 1; seed <= 4000; seed++) {
    const it = generate(seed);
    const p = it.params;
    const preds = RM.diagnosticsFor(p.task as string, p).map((d: { predictedResponse: string }) => d.predictedResponse);
    assert.equal(new Set(preds).size, preds.length, `seed ${seed} task ${p.task} duplicate predictions`);
  }
  // the share_three_part collision (seed 14) collapses to a single canonical diagnostic.
  const it14 = generate(14, { task: "share_three_part" });
  const ds = RM.diagnosticsFor("share_three_part", it14.params);
  const preds = ds.map((d: { predictedResponse: string }) => d.predictedResponse);
  assert.equal(new Set(preds).size, preds.length);
  assert.equal(ds[0].misconceptionId, "MISC.RATIO.WRONG_TOTAL_PARTS");
});

test("CORRECTION #6: every diagnostic's rationale + feedback match its registry source", () => {
  const byId: Record<string, { observableError: string; feedback: string }> = {};
  for (const m of RM.MISCONCEPTIONS) byId[m.misconceptionId as string] = m;
  for (let seed = 1; seed <= 1500; seed++) {
    const it = generate(seed);
    const p = it.params;
    for (const d of RM.diagnosticsFor(p.task as string, p)) {
      const reg = byId[d.misconceptionId as string] as { observableError: string; feedback: string };
      assert.equal(d.observableError, reg.observableError);
      assert.equal(d.feedback, reg.feedback);
      assert.ok(d.predictedResponse !== null && d.predictedResponse !== undefined);
    }
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
  assert.equal(d.approvalStatus, "approved");
});

test("serialize is stable and round-trips through JSON", () => {
  const item = generate(42, { interactionType: "free-response", task: "share_two_part" });
  const s = serialize(item);
  assert.equal(serialize(item), s);
  const parsed = JSON.parse(s);
  assert.equal(parsed.itemId, "ITEM-RATIO-share_two_part-42");
});

// --------------------------------------------------------------------------- //
// simple_scale subject-verb grammar + false-pass fix (owner REVISE v1.0.2)
// --------------------------------------------------------------------------- //
const _scaleNamed = ["scale-singular-represents", "scale-plural-represent", "scale-prompt-grammar-valid",
  "scale-a11y-grammar-valid", "scale-svg-desc-grammar-valid", "scale-unit-wording-grammatical-inspects-rendered-text",
  "singular-plural-units-correct-inspects-rendered-text", "scale-unit-wording-grammatical", "singular-plural-units-correct"];
const _names = (it: any) => Object.fromEntries(validate(it).checks.map((c: any) => [c.name, c.ok]));

test("simple_scale: subject-verb agreement + named checks pass for real items (singular + plural)", () => {
  let sing = false, plur = false;
  for (let s = 1; s <= 800; s++) {
    const it: any = generate(s, { task: "simple_scale" });
    const n = _names(it);
    for (const c of _scaleNamed) assert.ok(n[c], `seed ${s}: ${c}`);
    const instr = it.prompt.instruction as string;
    if (it.params.factorDen === 1) { sing = true; assert.ok(instr.includes(" unit represents ")); }
    else { plur = true; assert.ok(instr.includes(" units represent ")); }
  }
  assert.ok(sing && plur, "exercised both singular and plural subjects");
});

test("simple_scale: the validator FAILS the owner's exact bad wording (false-pass fix)", () => {
  // find a factorDen==1 item and tamper its rendered prompt to 'represent' -> must fail.
  let it: any = null;
  for (let s = 1; s <= 800; s++) { const g: any = generate(s, { task: "simple_scale" }); if (g.params.factorDen === 1) { it = g; break; } }
  assert.ok(it, "found a singular-subject scale item");
  it.prompt.instruction = (it.prompt.instruction as string).replace("represents", "represent");
  const n = _names(it);
  assert.equal(n["scale-prompt-grammar-valid"], false);
  assert.equal(n["scale-unit-wording-grammatical"], false);
  assert.equal(n["scale-singular-represents"], false);
});

test("simple_scale seed 4 regression is valid", () => {
  assert.ok(validate(generate(4, { task: "simple_scale" })).valid);
});
