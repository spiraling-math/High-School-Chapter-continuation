/**
 * Arithmetic-sequences validator (production TypeScript).
 *
 * Counterpart of the oracle's validate(). The core correctness check uses an
 * INDEPENDENT method — iterative term-by-term construction — distinct from the
 * generator's closed-form solve(). v1.1.0 adds distractor SEMANTIC AGREEMENT:
 * every distractor is independently recomputed from its misconception formula,
 * and its value, rationale, misconception, and feedback must agree.
 */

import type { Json } from "../../core/serialization/canonical.ts";
import { MISCONCEPTIONS } from "./misconceptions.ts";

export interface CheckResult { name: string; result: "pass" | "fail"; detail: string; }
export interface ValidationResult { status: "pass" | "fail"; validatorVersion: string; checks: CheckResult[]; }

const A1_MIN = -20, A1_MAX = 20;
const D_ABS_MAX = 12;
const N_MIN = 3, N_MAX = 40;
const VALIDATOR_VERSION = "1.1.0";

type Task = "nth_term" | "sum_n" | "find_d" | "find_n_for_value";

function nthTerm(a1: number, d: number, n: number): number { return a1 + (n - 1) * d; }

function iterativeTerms(a1: number, d: number, count: number): number[] {
  const terms: number[] = [];
  let t = a1;
  for (let i = 0; i < count; i++) { terms.push(t); t += d; }
  return terms;
}

function givenIntegers(task: Task, a1: number, d: number, n: number): Set<number> {
  if (task === "nth_term" || task === "sum_n") return new Set([a1, d, n]);
  if (task === "find_d") return new Set([a1, n, nthTerm(a1, d, n)]);
  return new Set([a1, d, nthTerm(a1, d, n)]); // find_n_for_value
}

export function validate(item: Record<string, Json>): ValidationResult {
  const checks: CheckResult[] = [];
  const add = (name: string, ok: boolean, detail = ""): void => {
    checks.push({ name, result: ok ? "pass" : "fail", detail });
  };

  const params = item["params"] as { task: Task; a1: number; d: number; n: number };
  const { task, a1, d, n } = params;
  const answer = (item["answer"] as { canonical: number }).canonical;

  add("params-in-domain",
    a1 >= A1_MIN && a1 <= A1_MAX && Math.abs(d) >= 1 && Math.abs(d) <= D_ABS_MAX && d !== 0 && n >= N_MIN && n <= N_MAX,
    `a1=${a1}, d=${d}, n=${n}`);

  if (task === "find_n_for_value") {
    const value = nthTerm(a1, d, n);
    const terms = iterativeTerms(a1, d, answer);
    add("arith-iterative-agreement",
      terms.length === answer && terms[terms.length - 1] === value && !terms.slice(0, -1).includes(value),
      `index ${answer} is first with value ${value}`);
  } else if (task === "find_d") {
    const value = nthTerm(a1, d, n);
    const terms = iterativeTerms(a1, answer, n);
    add("arith-iterative-agreement", terms[terms.length - 1] === value, `rebuilt nth term ${terms[terms.length - 1]} vs ${value}`);
  } else {
    const terms = iterativeTerms(a1, d, n);
    if (task === "nth_term") {
      add("arith-iterative-agreement", terms[terms.length - 1] === answer, `iter ${terms[terms.length - 1]} vs answer ${answer}`);
    } else {
      const s = terms.reduce((acc, x) => acc + x, 0);
      add("arith-iterative-agreement", s === answer, `iter sum ${s} vs answer ${answer}`);
    }
  }

  const steps = (item["solution"] as { steps: Array<{ intermediateResult?: string }> }).steps;
  const lastStep = steps[steps.length - 1]?.intermediateResult ?? "";
  add("answer-solution-agree", lastStep.includes(String(answer)), `final step '${lastStep}'`);

  const blocks = (item["prompt"] as { blocks: Array<{ text?: string }> }).blocks;
  const promptText = blocks.map((b) => b.text ?? "").join(" ");
  const promptInts = (promptText.match(/-?\d+/g) ?? []).map(Number);
  const givens = givenIntegers(task, a1, d, n);
  add("no-answer-leakage", promptInts.every((i) => givens.has(i)),
    `prompt ints ${JSON.stringify(promptInts)} subset of givens ${JSON.stringify([...givens])}`);

  // Distractor semantic agreement.
  const distractors = item["distractors"] as Array<{ value: number; misconceptionId: string; rationale?: string }> | undefined;
  if (distractors) {
    const mids = distractors.map((x) => x.misconceptionId);
    add("distractors-distinct-misconceptions", new Set(mids).size === mids.length, JSON.stringify(mids));
    add("min-three-distractors", distractors.length >= 3, `${distractors.length}`);
    for (const dd of distractors) {
      const m = MISCONCEPTIONS[dd.misconceptionId];
      add("distractor-misconception-known", Boolean(m), dd.misconceptionId);
      if (m) {
        add("distractor-value-matches-rule", m.formula(params) === dd.value,
          `${dd.misconceptionId}: rule ${m.formula(params)} vs stored ${dd.value}`);
        add("distractor-rationale-matches", dd.rationale === m.observableError, dd.misconceptionId);
        add("distractor-feedback-present", Boolean(m.feedback), dd.misconceptionId);
      }
      add("distractor-not-answer", dd.value !== answer, `${dd.value} vs ${answer}`);
    }
  }

  const options = item["options"] as Array<{ value: number; correct: boolean }> | undefined;
  if (options) {
    const correctVals = options.filter((o) => o.correct).map((o) => o.value);
    add("exactly-one-correct", correctVals.length === 1 && correctVals[0] === answer, JSON.stringify(correctVals));
    const wrong = options.filter((o) => !o.correct).map((o) => o.value);
    add("distractors-unique", new Set(wrong).size === wrong.length, JSON.stringify(wrong));
  }

  const a11y = item["accessibility"] as { spokenMath?: string } | undefined;
  add("a11y-fields-present", Boolean(a11y?.spokenMath), "spokenMath present");

  const status = checks.every((c) => c.result === "pass") ? "pass" : "fail";
  return { status, validatorVersion: VALIDATOR_VERSION, checks };
}
