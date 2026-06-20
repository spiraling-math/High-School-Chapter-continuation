/**
 * Arithmetic-sequences validator (production TypeScript).
 *
 * Byte-for-byte counterpart of the oracle's validate() (Principle 4). The core
 * correctness check uses an INDEPENDENT method — iterative term-by-term
 * construction — that differs from the generator's closed-form solve(), so a
 * bug in one is not hidden by reusing it in the other.
 *
 * This module deliberately does NOT import the generator's solve(): it
 * re-derives everything from the item's params, keeping verification independent
 * of generation.
 */

import type { Json } from "../../core/serialization/canonical.ts";

export interface CheckResult { name: string; result: "pass" | "fail"; detail: string; }
export interface ValidationResult { status: "pass" | "fail"; validatorVersion: string; checks: CheckResult[]; }

const A1_MIN = -20, A1_MAX = 20;
const D_ABS_MAX = 12;
const N_MIN = 3, N_MAX = 40;
const VALIDATOR_VERSION = "1.0.0";

type Task = "nth_term" | "sum_n" | "find_d" | "find_n_for_value";

function nthTerm(a1: number, d: number, n: number): number { return a1 + (n - 1) * d; }

/** Independent construction: build the sequence term by term. */
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

  // 1. params-in-domain
  add("params-in-domain",
    a1 >= A1_MIN && a1 <= A1_MAX && Math.abs(d) >= 1 && Math.abs(d) <= D_ABS_MAX && d !== 0 && n >= N_MIN && n <= N_MAX,
    `a1=${a1}, d=${d}, n=${n}`);

  // 2. INDEPENDENT verification by iterative construction
  if (task === "find_n_for_value") {
    const value = nthTerm(a1, d, n);
    const terms = iterativeTerms(a1, d, answer);
    const ok = terms.length === answer && terms[terms.length - 1] === value && !terms.slice(0, -1).includes(value);
    add("arith-iterative-agreement", ok, `index ${answer} is first with value ${value}`);
  } else if (task === "find_d") {
    const value = nthTerm(a1, d, n);
    const terms = iterativeTerms(a1, answer, n); // rebuild with the found d
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

  // 3. answer-solution-agree (final solution step contains the answer)
  const steps = (item["solution"] as { steps: Array<{ intermediateResult?: string }> }).steps;
  const lastStep = steps[steps.length - 1]?.intermediateResult ?? "";
  add("answer-solution-agree", lastStep.includes(String(answer)), `final step '${lastStep}'`);

  // 4. no-answer-leakage: every integer printed in the prompt is a declared given
  const blocks = (item["prompt"] as { blocks: Array<{ text?: string }> }).blocks;
  const promptText = blocks.map((b) => b.text ?? "").join(" ");
  const promptInts = (promptText.match(/-?\d+/g) ?? []).map(Number);
  const givens = givenIntegers(task, a1, d, n);
  add("no-answer-leakage", promptInts.every((i) => givens.has(i)),
    `prompt ints ${JSON.stringify(promptInts)} subset of givens ${JSON.stringify([...givens])}`);

  // 5. selected-response checks (only when options present)
  if (item["options"]) {
    const opts = item["options"] as Array<{ value: number; correct: boolean; misconceptionId?: string }>;
    const correctVals = opts.filter((o) => o.correct).map((o) => o.value);
    add("exactly-one-correct", correctVals.length === 1 && correctVals[0] === answer, `correct values ${JSON.stringify(correctVals)}`);
    const wrong = opts.filter((o) => !o.correct).map((o) => o.value);
    add("distractors-unique", new Set(wrong).size === wrong.length, JSON.stringify(wrong));
    add("distractor-not-answer", !wrong.includes(answer), `answer ${answer}, wrong ${JSON.stringify(wrong)}`);
    add("distractor-misconception", opts.filter((o) => !o.correct).every((o) => Boolean(o.misconceptionId)), "every distractor maps to a misconception");
    add("min-three-distractors", wrong.length >= 3, `${wrong.length} distractors`);
  }

  // 6. accessibility fields present
  const a11y = item["accessibility"] as { spokenMath?: string } | undefined;
  add("a11y-fields-present", Boolean(a11y?.spokenMath), "spokenMath present");

  const status = checks.every((c) => c.result === "pass") ? "pass" : "fail";
  return { status, validatorVersion: VALIDATOR_VERSION, checks };
}
