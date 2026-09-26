/**
 * gen.functions.foundations v1.0.0 — TypeScript behaviour tests (mirror the Python oracle gates in
 * oracle/tests/test_functions.py). Byte parity itself is gated by functions.parity.test.ts.
 *
 * Run:  node --test domains/functions/functions.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  generate, validate, describe, serialize, TASKS, MC_ONLY_TASKS, TASK_BANDS, InteractionNotSupported,
} from "./functions.ts";
import * as FM from "./functions-misconceptions.ts";
import { ANSWER_TYPES_BY_TASK, FUNCTIONS_OBJECTIVE_IDS } from "../../core/curriculum/functions-objective-ids.ts";

const root = fileURLToPath(new URL("../../", import.meta.url));

function isFunctionRelation(pairs: number[][]): boolean {
  const seen = new Map<number, number>();
  for (const [x, y] of pairs as [number, number][]) {
    if (seen.has(x) && seen.get(x) !== y) return false;
    if (!seen.has(x)) seen.set(x, y);
  }
  return true;
}

test("interaction policy: identify_function is MC-only; unsupported requests raise; unknown task raises", () => {
  assert.throws(() => generate(1, { task: "identify_function", interactionType: "free-response" }), InteractionNotSupported);
  assert.throws(() => generate(1, { task: "evaluate_function", interactionType: "matching" }), InteractionNotSupported);
  assert.throws(() => generate(1, { task: "nope" }), /unknown task/);
  assert.equal(generate(3, { task: "identify_function" }).interactionType, "multiple-choice");
  assert.equal(generate(3, { task: "evaluate_function" }).interactionType, "free-response");
  // the legacy answerType selector is NOT consulted (ratio v1.0.2 precedent): default interaction per task
  assert.equal(generate(3, { task: "evaluate_function", answerType: "multiple-choice" }).interactionType, "free-response");
  assert.equal(generate(3, { task: "identify_function", answerType: "integer" }).interactionType, "multiple-choice");
  assert.equal(serialize(generate(5, { answerType: "integer" })), serialize(generate(5, {})));
});

test("no-task request never raises and respects the requested pool", () => {
  for (let seed = 1; seed < 200; seed++) {
    const fr = generate(seed, { interactionType: "free-response" });
    assert.equal(fr.interactionType, "free-response");
    assert.ok(!(MC_ONLY_TASKS as string[]).includes(fr.params.task));
    const mc = generate(seed, { interactionType: "multiple-choice" });
    assert.equal(mc.interactionType, "multiple-choice");
    assert.ok(Array.isArray(mc.options) && mc.options.length === 4);
    const dflt = generate(seed, {});
    assert.equal(dflt.interactionType, dflt.params.task === "identify_function" ? "multiple-choice" : "free-response");
  }
});

test("validity sweep: 600 seeds x both interaction pools, zero invalid; serialization reproducible", () => {
  const failing: string[] = [];
  for (let seed = 1; seed <= 600; seed++) {
    for (const inter of ["free-response", "multiple-choice"]) {
      const item = generate(seed, { interactionType: inter });
      const v = validate(item);
      if (v.status !== "pass") failing.push(`${seed}/${inter}/${item.params.task}: ${v.checks.filter((c: { result: string }) => c.result === "fail").map((c: { name: string }) => c.name).join(",")}`);
      if (seed <= 100) assert.equal(serialize(generate(seed, { interactionType: inter })), serialize(item));
    }
  }
  assert.deepEqual(failing, []);
});

test("answer types per task follow the curriculum contract (free-response)", () => {
  for (const task of TASKS) {
    for (let seed = 1; seed <= 15; seed++) {
      const item = generate(seed, { task });
      assert.ok(ANSWER_TYPES_BY_TASK[task as keyof typeof ANSWER_TYPES_BY_TASK].includes(item.answer.type), `${task}: ${item.answer.type}`);
      assert.deepEqual(item.objectiveIds, [FUNCTIONS_OBJECTIVE_IDS[TASKS.indexOf(task)]]);
    }
  }
});

test("every declared difficulty band is reachable per task", () => {
  for (const task of TASKS) {
    const [lo, hi] = TASK_BANDS[task as keyof typeof TASK_BANDS];
    const seen = new Set<number>();
    for (let seed = 1; seed <= 1500 && seen.size < hi - lo + 1; seed++) {
      const b = generate(seed, { task }).difficulty.overallBand as number;
      assert.ok(b >= lo && b <= hi, `${task}: band ${b} outside [${lo}, ${hi}]`);
      seen.add(b);
    }
    for (let b = lo; b <= hi; b++) assert.ok(seen.has(b), `${task}: band ${b} never reached`);
  }
});

test("every eligible misconception rule is exercised as a distractor with clean feedback", () => {
  const placeholder = /(?<![A-Za-z])[bcmpqtv](?![A-Za-z])/;
  for (const task of TASKS) {
    if ((MC_ONLY_TASKS as string[]).includes(task)) continue;
    const eligible = new Set(FM.rulesFor(task));
    const seen = new Set<string>();
    for (let seed = 1; seed <= 3000 && seen.size < eligible.size; seed++) {
      const item = generate(seed, { task, interactionType: "multiple-choice" });
      for (const d of item.distractors as { misconceptionId: string }[]) seen.add(d.misconceptionId);
    }
    assert.deepEqual([...seen].sort(), [...eligible].sort(), `${task}: never exercised ${[...eligible].filter((m) => !seen.has(m)).join(",")}`);
  }
  // feedback strings never leak internal coefficient names (the formula -b/(2a) is allowed)
  for (const [mid, m] of Object.entries(FM.MISCONCEPTIONS)) {
    assert.ok(m.title && m.description && m.observableError && m.expression, mid);
    assert.ok(!placeholder.test(m.observableError.split("-b/(2a)").join(" ")), `${mid}: observableError leaks a placeholder`);
  }
});

test("identify_function: four options, the three structural distractors, exactly one non-function", () => {
  for (let seed = 1; seed < 200; seed++) {
    const item = generate(seed, { task: "identify_function" });
    const opts = item.options as { correct: boolean; misconceptionId?: string; value: number[][] }[];
    assert.equal(opts.length, 4);
    const wrongIds = opts.filter((o) => !o.correct).map((o) => o.misconceptionId).sort();
    assert.deepEqual(wrongIds, [...FM.STRUCTURAL_ONLY].sort());
    assert.equal(opts.filter((o) => !isFunctionRelation(o.value)).length, 1);
    assert.equal(validate(item).status, "pass");
  }
});

test("core/misconceptions/functions.json is in sync with the TypeScript registry", () => {
  const recs = JSON.parse(readFileSync(root + "core/misconceptions/functions.json", "utf8")) as Array<Record<string, unknown>>;
  assert.deepEqual(recs.map((r) => r.misconceptionId).sort(), Object.keys(FM.MISCONCEPTIONS).sort());
  assert.equal(recs.length, 68);
  for (const r of recs) {
    const m = FM.MISCONCEPTIONS[r.misconceptionId as string]!;
    assert.equal(r.title, m.title);
    assert.equal(r.description, m.description);
    assert.equal(r.observableError, m.observableError);
    assert.equal((r.distractorRule as { expression: string }).expression, m.expression);
    assert.deepEqual((r.validRange as { levels: string[] }).levels, ["ibdp-aasl"]);
    assert.equal(r.reviewStatus, "proposed");
  }
});

test("describe(): pending-review, eleven objectives, the two new canonical answer types declared", () => {
  const d = describe();
  assert.equal(d.generatorId, "gen.functions.foundations");
  assert.equal(d.version, "1.0.0");
  assert.equal(d.approvalStatus, "pending-review");
  assert.deepEqual(d.objectiveIds, FUNCTIONS_OBJECTIVE_IDS);
  assert.deepEqual(d.tasks, [...TASKS]);
  for (const t of ["algebraic-expression", "interval", "integer", "exact-rational", "multiple-choice"]) assert.ok(d.answerTypes.includes(t));
  assert.equal(Object.keys(d.difficultyRanges).length, 11);
});
