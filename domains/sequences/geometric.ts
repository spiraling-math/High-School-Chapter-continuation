/**
 * Geometric sequences generator (production TypeScript).
 *
 * Generator id : gen.sequences.geometric   Version: 1.0.0
 * Spec         : docs/GENERATOR_SPEC_geometric_sequences_PROPOSAL.md (approved)
 *
 * Byte-for-byte counterpart of oracle/spi_oracle/geometric.py using the exact
 * Rational type. Tasks: nth_term, sum_n (MC or free-response), find_r,
 * find_n_for_value, sum_infinite (free-response). Asserted by golden/parity tests.
 */

import { Mulberry32 } from "../../core/seeded-random/mulberry32.ts";
import { canonicalStringify, type Json } from "../../core/serialization/canonical.ts";
import { Rational, rat } from "../../core/exact-math/rational.ts";
import { MISCONCEPTIONS, rulesFor } from "./geometric-misconceptions.ts";

export const GENERATOR_ID = "gen.sequences.geometric";
export const GENERATOR_VERSION = "1.0.0";

export type Task = "nth_term" | "sum_n" | "find_r" | "find_n_for_value" | "sum_infinite";
export const FORWARD_MC_TASKS: Task[] = ["nth_term", "sum_n"];
export const ALL_TASKS: Task[] = ["nth_term", "sum_n", "find_r", "find_n_for_value", "sum_infinite"];

const R_FINITE: [number, number][] = [[2, 1], [-2, 1], [3, 1], [-3, 1], [1, 2], [-1, 2], [1, 3], [-1, 3], [2, 3], [-2, 3], [3, 2], [-3, 2]];
const R_INFINITE: [number, number][] = [[1, 2], [-1, 2], [1, 3], [-1, 3], [2, 3], [-2, 3], [1, 4], [-1, 4], [3, 4], [-3, 4]];
const U1_CHOICES: number[] = [];
for (let u = -9; u <= 9; u++) if (u !== 0) U1_CHOICES.push(u);
const N_MIN = 2, N_MAX = 6;
const FIND_R_POSITIONS = [2, 4];
const MAX_NUM = 20000, MAX_DEN = 256, MAX_PARAM_ATTEMPTS = 256;
const CALCULATOR_POLICY = "calculator-not-required";

const OBJECTIVE_BY_TASK: Record<Task, string> = {
  nth_term: "SPI.IBDPAASL.SEQSER.GEO.NTH_TERM.01",
  sum_n: "SPI.IBDPAASL.SEQSER.GEO.SUM_N.01",
  find_r: "SPI.IBDPAASL.SEQSER.GEO.COMMON_RATIO.01",
  find_n_for_value: "SPI.IBDPAASL.SEQSER.GEO.TERM_INDEX.01",
  sum_infinite: "SPI.IBDPAASL.SEQSER.GEO.SUM_INFINITE.01",
};

export interface Params { task: Task; u1: number; r: { num: number; den: number }; n?: number; k?: number; }
export interface Config { task?: Task; answerType?: "integer" | "multiple-choice"; }
interface Cand { value: Rational; misconceptionId: string; rationale: string; }

// --------------------------------------------------------------------------- //
function rOf(p: Params): Rational { return new Rational(p.r.num, p.r.den); }
function disp(x: Rational | number): string { return typeof x === "number" ? String(x) : x.toString(); }
function withinCaps(x: Rational): boolean { return Math.abs(x.num) <= MAX_NUM && x.den <= MAX_DEN; }

function iroot(x: number, m: number): number {
  if (x === 0) return 0;
  const r = Math.round(x ** (1 / m));
  for (const cand of [r - 1, r, r + 1]) if (cand >= 0 && cand ** m === x) return cand;
  throw new Error(`no exact integer ${m}th root of ${x}`);
}
function rationalRoot(q: Rational, m: number): Rational {
  if (q.isZero()) return rat(0);
  const sign = q.num > 0 ? 1 : -1;
  return new Rational(sign * iroot(Math.abs(q.num), m), iroot(q.den, m));
}

function nth(u1: number, r: Rational, n: number): Rational { return rat(u1).mul(r.pow(n - 1)); }
function sumN(u1: number, r: Rational, n: number): Rational { return rat(u1).mul(r.pow(n).sub(rat(1))).div(r.sub(rat(1))); }

export function solve(p: Params): Rational | number {
  const r = rOf(p);
  if (p.task === "nth_term") return nth(p.u1, r, p.n!);
  if (p.task === "sum_n") return sumN(p.u1, r, p.n!);
  if (p.task === "sum_infinite") return rat(p.u1).div(rat(1).sub(r));
  if (p.task === "find_r") {
    const value = nth(p.u1, r, p.k!);
    return rationalRoot(value.div(rat(p.u1)), p.k! - 1);
  }
  // find_n_for_value
  const value = nth(p.u1, r, p.n!);
  let t = rat(p.u1);
  for (let k = 1; k <= 64; k++) { if (t.equals(value)) return k; t = t.mul(r); }
  throw new Error("term index not found");
}

function givenValue(p: Params): Rational {
  const pos = p.task === "find_r" ? p.k! : p.n!;
  return nth(p.u1, rOf(p), pos);
}

// --------------------------------------------------------------------------- //
export function generateDistractors(p: Params): Cand[] | null {
  const ruleIds = rulesFor(p.task);
  if (ruleIds.length === 0) return [];
  const r = rOf(p);
  const correct = solve(p) as Rational;
  const chosen: Cand[] = [];
  const seen = new Set<string>([`${correct.num}/${correct.den}`]);
  for (const mid of ruleIds) {
    const m = MISCONCEPTIONS[mid]!;
    const val = m.formula(p.u1, r, p.n!);
    const key = `${val.num}/${val.den}`;
    if (!withinCaps(val) || seen.has(key)) continue;
    seen.add(key);
    chosen.push({ value: val, misconceptionId: mid, rationale: m.observableError });
    if (chosen.length === 3) break;
  }
  return chosen.length === 3 ? chosen : null;
}

function ordinal(n: number): string {
  let s: string;
  if (n % 100 >= 10 && n % 100 <= 20) s = "th";
  else s = ({ 1: "st", 2: "nd", 3: "rd" } as Record<number, string>)[n % 10] ?? "th";
  return `${n}${s}`;
}

export function generateSolution(p: Params): Json {
  const u1 = p.u1, r = rOf(p), rd = r.toString();
  const ans = solve(p);
  const ad = disp(ans);
  if (p.task === "nth_term") {
    const n = p.n!;
    return { steps: [
      { number: 1, transformation: "State the formula", ruleOrTheorem: "u_n = u_1 r^{n-1}" },
      { number: 2, transformation: "Substitute", intermediateResult: `u_{${n}} = ${u1}\\times(${rd})^{${n}-1}`, dependsOn: [1] },
      { number: 3, transformation: "Evaluate", intermediateResult: `u_{${n}} = ${ad}`, dependsOn: [2], marks: 1 },
    ] };
  }
  if (p.task === "sum_n") {
    const n = p.n!;
    return { steps: [
      { number: 1, transformation: "State the formula", ruleOrTheorem: "S_n = u_1 (r^n - 1)/(r - 1)" },
      { number: 2, transformation: "Substitute", intermediateResult: `S_{${n}} = ${u1}\\times\\frac{(${rd})^{${n}} - 1}{(${rd}) - 1}`, dependsOn: [1] },
      { number: 3, transformation: "Evaluate", intermediateResult: `S_{${n}} = ${ad}`, dependsOn: [2], marks: 1 },
    ] };
  }
  if (p.task === "sum_infinite") {
    return { steps: [
      { number: 1, transformation: "Check convergence", ruleOrTheorem: "|r| < 1 so the series converges" },
      { number: 2, transformation: "State the formula", ruleOrTheorem: "S_\\infty = u_1/(1 - r)" },
      { number: 3, transformation: "Substitute and evaluate", intermediateResult: `S_\\infty = \\frac{${u1}}{1 - (${rd})} = ${ad}`, dependsOn: [2], marks: 1 },
    ] };
  }
  if (p.task === "find_r") {
    const k = p.k!, value = disp(givenValue(p));
    return { steps: [
      { number: 1, transformation: "State the formula", ruleOrTheorem: "u_k = u_1 r^{k-1}" },
      { number: 2, transformation: "Rearrange for r", intermediateResult: `r^{${k}-1} = \\frac{u_k}{u_1} = \\frac{${value}}{${u1}}`, dependsOn: [1] },
      { number: 3, transformation: "Take the root", intermediateResult: `r = ${ad}`, dependsOn: [2], marks: 1 },
    ] };
  }
  const value = disp(givenValue(p));
  return { steps: [
    { number: 1, transformation: "State the formula", ruleOrTheorem: "u_n = u_1 r^{n-1}" },
    { number: 2, transformation: "Set up the equation", intermediateResult: `${u1}\\times(${rd})^{n-1} = ${value}`, dependsOn: [1] },
    { number: 3, transformation: "Solve for n", intermediateResult: `n = ${ad}`, dependsOn: [2], marks: 1 },
  ] };
}

function promptBlocks(p: Params): { instruction: string; blocks: Json[]; spoken: string } {
  const u1 = p.u1, rd = rOf(p).toString();
  if (p.task === "nth_term") {
    const n = p.n!;
    return { instruction: "Find", blocks: [
      { kind: "text", text: `A geometric sequence has first term ${u1} and common ratio ${rd}.` },
      { kind: "text", text: `Find the ${ordinal(n)} term of the sequence.` }],
      spoken: `A geometric sequence has first term ${u1} and common ratio ${rd}. Find the ${ordinal(n)} term.` };
  }
  if (p.task === "sum_n") {
    const n = p.n!;
    return { instruction: "Find", blocks: [
      { kind: "text", text: `A geometric sequence has first term ${u1} and common ratio ${rd}.` },
      { kind: "text", text: `Find the sum of the first ${n} terms of the sequence.` }],
      spoken: `A geometric sequence has first term ${u1} and common ratio ${rd}. Find the sum of the first ${n} terms.` };
  }
  if (p.task === "sum_infinite") {
    return { instruction: "Find", blocks: [
      { kind: "text", text: `A geometric sequence has first term ${u1} and common ratio ${rd}, with |r| < 1.` },
      { kind: "text", text: "Find the sum to infinity of the sequence." }],
      spoken: `A geometric sequence has first term ${u1} and common ratio ${rd}, with absolute value of r less than 1. Find the sum to infinity.` };
  }
  if (p.task === "find_r") {
    const k = p.k!, value = disp(givenValue(p));
    return { instruction: "Find", blocks: [
      { kind: "text", text: `A geometric sequence has first term ${u1}, and its ${ordinal(k)} term is ${value}.` },
      { kind: "text", text: "Find the common ratio of the sequence." }],
      spoken: `A geometric sequence has first term ${u1}, and its ${ordinal(k)} term is ${value}. Find the common ratio.` };
  }
  const value = disp(givenValue(p));
  return { instruction: "Find", blocks: [
    { kind: "text", text: `A geometric sequence has first term ${u1} and common ratio ${rd}.` },
    { kind: "text", text: `The nth term of the sequence is ${value}. Find the value of n.` }],
    spoken: `A geometric sequence has first term ${u1} and common ratio ${rd}. The nth term of the sequence is ${value}. Find the value of n.` };
}

function givenInts(p: Params): Set<number> {
  const text = promptBlocks(p).blocks.map((b) => (b as { text?: string }).text ?? "").join(" ");
  return new Set((text.match(/-?\d+/g) ?? []).map(Number));
}

const W = { numericalComplexity: 0.25, reasoningSteps: 0.4, abstraction: 0.2, exactVsApproximate: 0.15 };
function round3(x: number): number { const v = Math.floor(x * 1000 + 0.5) / 1000; return v; }

function difficulty(p: Params): Json {
  const u1 = p.u1, r = rOf(p);
  const fracRatio = r.den !== 1;
  const nOrK = p.n ?? p.k ?? 3;
  const mag = (Math.abs(u1) / 9 + (Math.abs(r.num) + r.den) / 7 + nOrK / N_MAX) / 3.0;
  const numerical = Math.min(1.0, mag);
  const steps = { nth_term: 0.25, sum_n: 0.5, find_r: 0.7, find_n_for_value: 0.7, sum_infinite: 0.6 }[p.task];
  const abstraction = p.task === "sum_infinite" ? 0.7 : (p.task === "find_r" || p.task === "find_n_for_value" ? 0.5 : 0.15);
  const exact = fracRatio ? 0.7 : 0.1;
  const axes = { numericalComplexity: round3(numerical), reasoningSteps: steps, abstraction, exactVsApproximate: exact };
  const score = Math.max(0, Math.min(1, W.numericalComplexity * axes.numericalComplexity + W.reasoningSteps * axes.reasoningSteps + W.abstraction * axes.abstraction + W.exactVsApproximate * axes.exactVsApproximate));
  const band = Math.min(5, 1 + Math.floor(score * 5));
  return { overallBand: band, axes };
}

function drawParams(rng: Mulberry32, explicitTask: Task | undefined, answerType: string): Params {
  let task: Task;
  if (explicitTask != null) task = explicitTask;
  else task = rng.choice(answerType === "multiple-choice" ? FORWARD_MC_TASKS : ALL_TASKS);
  const u1 = rng.choice(U1_CHOICES);
  const rspec = rng.choice(task === "sum_infinite" ? R_INFINITE : R_FINITE);
  const params: Params = { task, u1, r: { num: rspec[0], den: rspec[1] } };
  if (task === "find_r") params.k = rng.choice(FIND_R_POSITIONS);
  else if (task !== "sum_infinite") params.n = rng.nextInt(N_MIN, N_MAX);
  return params;
}

function acceptable(p: Params, answerType: string): Cand[] | null {
  let ans: Rational | number;
  try { ans = solve(p); } catch { return null; }
  const af = typeof ans === "number" ? rat(ans) : ans;
  if (!withinCaps(af)) return null;
  if (p.task === "find_r" || p.task === "find_n_for_value") { if (!withinCaps(givenValue(p))) return null; }
  if (answerType === "multiple-choice") return generateDistractors(p);
  return [];
}

export function generate(seed: number, config: Config = {}): Record<string, Json> {
  const answerType = config.answerType ?? "integer";
  const explicitTask = config.task;
  if (explicitTask != null && !ALL_TASKS.includes(explicitTask)) throw new Error(`unknown task: ${explicitTask}`);
  if (answerType === "multiple-choice" && explicitTask != null && !FORWARD_MC_TASKS.includes(explicitTask)) {
    throw new Error("multiple-choice is only offered for nth_term and sum_n");
  }
  const rng = new Mulberry32(seed);
  let params!: Params;
  let distractors: Cand[] | null = null;
  let ok = false;
  for (let i = 0; i < MAX_PARAM_ATTEMPTS; i++) {
    params = drawParams(rng, explicitTask, answerType);
    const result = acceptable(params, answerType);
    if (result === null) continue;
    distractors = result;
    ok = true;
    break;
  }
  if (!ok) throw new Error("could not find acceptable geometric parameters");

  const task = params.task;
  const ans = solve(params);
  const pr = promptBlocks(params);

  let answerObj: Record<string, Json>;
  if (task === "find_n_for_value") answerObj = { type: "integer", canonical: ans as number, display: String(ans) };
  else { const af = ans as Rational; answerObj = { type: "fraction", canonical: af.toJSON(), display: af.toString() }; }

  const paramsJson: Record<string, Json> = { task: params.task, u1: params.u1, r: { num: params.r.num, den: params.r.den } };
  if (params.n !== undefined) paramsJson["n"] = params.n;
  if (params.k !== undefined) paramsJson["k"] = params.k;

  const item: Record<string, Json> = {
    itemId: `ITEM-${GENERATOR_ID.replace(/\./g, "-")}-${seed}-${task}`,
    schemaVersion: "1.0.0",
    objectiveIds: [OBJECTIVE_BY_TASK[task]],
    generatorId: GENERATOR_ID,
    generatorVersion: GENERATOR_VERSION,
    seed,
    params: paramsJson,
    prompt: { instruction: pr.instruction, blocks: pr.blocks },
    answer: answerObj,
    solution: generateSolution(params),
    difficulty: difficulty(params),
    calculatorPolicy: CALCULATOR_POLICY,
    accessibility: { spokenMath: pr.spoken, nonColorIndicators: true },
    provenance: { origin: "generated", rightsStatus: "academy-owned", originalityNote: "Original parameterized item; structure abstracted from curriculum." },
    lifecycle: { state: "generated" },
  };

  if (answerType === "multiple-choice") {
    const ds = distractors ?? [];
    (item["answer"] as Record<string, Json>)["type"] = "multiple-choice";
    item["distractors"] = ds.map((dd, i) => ({
      id: `d${i + 1}`, value: dd.value.toJSON(), display: dd.value.toString(),
      misconceptionId: dd.misconceptionId, rationale: dd.rationale,
    }));
    interface Opt { value: Rational; correct: boolean; misconceptionId: string | null; }
    const correctR = ans as Rational;
    const pool: Opt[] = [{ value: correctR, correct: true, misconceptionId: null }];
    for (const dd of ds) pool.push({ value: dd.value, correct: false, misconceptionId: dd.misconceptionId });
    const shuffled = rng.shuffle(pool);
    const labels = ["A", "B", "C", "D", "E"];
    item["options"] = shuffled.map((o, i) => {
      const opt: Record<string, Json> = { label: labels[i] as string, value: o.value.toJSON(), display: o.value.toString(), correct: o.correct };
      if (o.misconceptionId) opt["misconceptionId"] = o.misconceptionId;
      return opt;
    });
  }
  return item;
}

// --------------------------------------------------------------------------- //
export interface CheckResult { name: string; result: "pass" | "fail"; detail: string; }
export interface ValidationResult { status: "pass" | "fail"; validatorVersion: string; checks: CheckResult[]; }

export function validate(item: Record<string, Json>): ValidationResult {
  const checks: CheckResult[] = [];
  const add = (name: string, ok: boolean, detail = ""): void => { checks.push({ name, result: ok ? "pass" : "fail", detail }); };
  const params = item["params"] as unknown as Params;
  const u1 = params.u1, r = new Rational(params.r.num, params.r.den);
  const ansF = item["answer"] as { type: string; canonical: Json; display: string };

  add("params-in-domain", u1 !== 0 && u1 >= -9 && u1 <= 9 && !r.isZero() && !r.equals(rat(1)) && !r.equals(rat(-1)) && params.r.den >= 1, `u1=${u1}, r=${r.toString()}`);

  const canRat = (): Rational => new Rational((ansF.canonical as { num: number }).num, (ansF.canonical as { den: number }).den);
  if (params.task === "nth_term") {
    let t = rat(u1); for (let i = 0; i < params.n! - 1; i++) t = t.mul(r);
    add("geo-iterative-agreement", t.equals(canRat()), "");
  } else if (params.task === "sum_n") {
    let t = rat(u1), s = rat(0); for (let i = 0; i < params.n!; i++) { s = s.add(t); t = t.mul(r); }
    add("geo-iterative-agreement", s.equals(canRat()), "");
  } else if (params.task === "sum_infinite") {
    add("geo-iterative-agreement", r.cmpAbs(rat(1)) < 0 && canRat().mul(rat(1).sub(r)).equals(rat(u1)), "");
  } else if (params.task === "find_r") {
    const found = canRat(); const value = givenValue(params);
    let t = rat(u1); for (let i = 0; i < params.k! - 1; i++) t = t.mul(found);
    add("geo-iterative-agreement", t.equals(value), "");
  } else {
    const nAns = ansF.canonical as number; const value = givenValue(params);
    const terms: Rational[] = []; let t = rat(u1);
    for (let i = 0; i < nAns; i++) { terms.push(t); t = t.mul(r); }
    add("geo-iterative-agreement", terms.length === nAns && terms[terms.length - 1]!.equals(value) && !terms.slice(0, -1).some((x) => x.equals(value)), "");
  }

  const steps = (item["solution"] as { steps: Array<{ intermediateResult?: string }> }).steps;
  add("answer-solution-agree", (steps[steps.length - 1]?.intermediateResult ?? "").includes(ansF.display), "");

  const text = (item["prompt"] as { blocks: Array<{ text?: string }> }).blocks.map((b) => b.text ?? "").join(" ");
  const promptInts = (text.match(/-?\d+/g) ?? []).map(Number);
  const givens = givenInts(params);
  add("no-answer-leakage", promptInts.every((i) => givens.has(i)), "");

  const distractors = item["distractors"] as Array<{ value: { num: number; den: number }; misconceptionId: string; rationale?: string }> | undefined;
  if (distractors) {
    const mids = distractors.map((d) => d.misconceptionId);
    add("distractors-distinct-misconceptions", new Set(mids).size === mids.length, JSON.stringify(mids));
    add("min-three-distractors", distractors.length >= 3, `${distractors.length}`);
    for (const d of distractors) {
      const m = MISCONCEPTIONS[d.misconceptionId];
      add("distractor-misconception-known", Boolean(m), d.misconceptionId);
      if (m) {
        const expected = m.formula(u1, r, params.n!);
        add("distractor-value-matches-rule", expected.num === d.value.num && expected.den === d.value.den, d.misconceptionId);
        add("distractor-rationale-matches", d.rationale === m.observableError, d.misconceptionId);
        add("distractor-feedback-present", Boolean(m.feedback), d.misconceptionId);
      }
    }
  }
  const options = item["options"] as Array<{ display: string; correct: boolean }> | undefined;
  if (options) {
    const correct = options.filter((o) => o.correct);
    add("exactly-one-correct", correct.length === 1 && correct[0]!.display === ansF.display, "");
    const wrong = options.filter((o) => !o.correct).map((o) => o.display);
    add("distractors-unique", new Set(wrong).size === wrong.length, "");
  }

  add("a11y-fields-present", Boolean((item["accessibility"] as { spokenMath?: string } | undefined)?.spokenMath), "");

  const status = checks.every((c) => c.result === "pass") ? "pass" : "fail";
  return { status, validatorVersion: "1.0.0", checks };
}

export function serialize(item: Record<string, Json>): string { return canonicalStringify(item); }
