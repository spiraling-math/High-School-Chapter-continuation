/**
 * Arithmetic sequences generator (production TypeScript).
 *
 * Generator id : gen.sequences.arithmetic   Version: 1.0.0
 * Spec         : docs/GENERATOR_SPEC_arithmetic_sequences.md
 *
 * This is the byte-for-byte counterpart of the Python oracle
 * (oracle/spi_oracle/sequences.py). For any seed the two produce identical
 * canonical serializations; this is asserted by the golden-parity test against
 * oracle/golden/arithmetic_sequences.golden.json (Principle 4: independent
 * verification across two implementations).
 *
 * All maths uses integers only (the first slice is exact by construction).
 */

import { Mulberry32 } from "../../core/seeded-random/mulberry32.ts";
import { canonicalStringify, type Json } from "../../core/serialization/canonical.ts";

export const GENERATOR_ID = "gen.sequences.arithmetic";
export const GENERATOR_VERSION = "1.0.0";

export type Task = "nth_term" | "sum_n" | "find_d" | "find_n_for_value";
export const FORWARD_TASKS: Task[] = ["nth_term", "sum_n"];
export const REVERSE_TASKS: Task[] = ["find_d", "find_n_for_value"];
export const ALL_TASKS: Task[] = ["nth_term", "sum_n", "find_d", "find_n_for_value"];

const A1_MIN = -20, A1_MAX = 20;
const D_ABS_MIN = 1, D_ABS_MAX = 12;
const N_MIN = 3, N_MAX = 40;

const OBJECTIVE_BY_TASK: Record<Task, string> = {
  nth_term: "SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01",
  find_d: "SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01",
  find_n_for_value: "SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01",
  sum_n: "SPI.IBDPAASL.SEQSER.ARITH.SUM_N.01",
};

export interface Params { task: Task; a1: number; d: number; n: number; }
export interface Config { task?: Task; answerType?: "integer" | "multiple-choice"; }

// --------------------------------------------------------------------------- //
// Canonical mathematics (closed form) — mirrors solve()
// --------------------------------------------------------------------------- //
function nthTerm(a1: number, d: number, n: number): number { return a1 + (n - 1) * d; }
function sumN(a1: number, d: number, n: number): number {
  return (n * (2 * a1 + (n - 1) * d)) / 2; // even numerator => exact integer
}
function givenValue(p: Params): number { return nthTerm(p.a1, p.d, p.n); }

export function solve(p: Params): number {
  switch (p.task) {
    case "nth_term": return nthTerm(p.a1, p.d, p.n);
    case "sum_n": return sumN(p.a1, p.d, p.n);
    case "find_d": return (givenValue(p) - p.a1) / (p.n - 1);
    case "find_n_for_value": return (givenValue(p) - p.a1) / p.d + 1;
  }
}

// --------------------------------------------------------------------------- //
// Parameter selection (identical RNG draw order to the oracle)
// --------------------------------------------------------------------------- //
function chooseParams(rng: Mulberry32, config: Config): { params: Params; answerType: string } {
  const answerType = config.answerType ?? "integer";
  let task: Task;
  if (config.task != null) {
    if (!ALL_TASKS.includes(config.task)) throw new Error(`unknown task: ${config.task}`);
    if (answerType === "multiple-choice" && REVERSE_TASKS.includes(config.task)) {
      throw new Error("multiple-choice is only offered for forward tasks");
    }
    task = config.task;
  } else {
    const pool = answerType === "multiple-choice" ? FORWARD_TASKS : ALL_TASKS;
    task = rng.choice(pool);
  }
  const a1 = rng.nextInt(A1_MIN, A1_MAX);
  const dMag = rng.nextInt(D_ABS_MIN, D_ABS_MAX);
  const d = rng.nextFloat() < 0.5 ? dMag : -dMag;
  const n = rng.nextInt(N_MIN, N_MAX);
  return { params: { task, a1, d, n }, answerType };
}

// --------------------------------------------------------------------------- //
// Distractors (forward tasks) — each maps to a misconception
// --------------------------------------------------------------------------- //
interface Cand { value: number; misconceptionId: string; }

export function generateDistractors(p: Params): Cand[] {
  const correct = solve(p);
  const { a1, d, n, task } = p;
  let candidates: Cand[] = [];
  if (task === "nth_term") {
    candidates = [
      { value: a1 + n * d, misconceptionId: "MISC.SEQ.OFFBYONE_TERMINDEX" },
      { value: a1 - (n - 1) * d, misconceptionId: "MISC.SEQ.SIGN_DIFFERENCE" },
      { value: a1 + (n - 1), misconceptionId: "MISC.SEQ.FORGOT_MULTIPLY" },
      { value: a1 + (n + 1) * d, misconceptionId: "MISC.SEQ.OFFBYONE_TERMINDEX" },
    ];
  } else if (task === "sum_n") {
    const uN = nthTerm(a1, d, n);
    candidates = [
      { value: n * (2 * a1 + (n - 1) * d), misconceptionId: "MISC.SERIES.FORGOT_HALF" },
      { value: n * uN, misconceptionId: "MISC.SERIES.CONSTANT_TERMS" },
      { value: n * a1, misconceptionId: "MISC.SERIES.CONSTANT_TERMS" },
      { value: (n * (2 * a1 + (n + 1) * d)) / 2, misconceptionId: "MISC.SEQ.OFFBYONE_TERMINDEX" },
      { value: correct + (a1 + n * d), misconceptionId: "MISC.SEQ.OFFBYONE_TERMINDEX" },
      { value: correct - uN, misconceptionId: "MISC.SEQ.OFFBYONE_TERMINDEX" },
    ];
  } else {
    return [];
  }
  const chosen: Cand[] = [];
  const seen = new Set<number>([correct]);
  for (const c of candidates) {
    if (seen.has(c.value)) continue;
    seen.add(c.value);
    chosen.push({ value: c.value, misconceptionId: c.misconceptionId });
    if (chosen.length === 3) break;
  }
  return chosen;
}

// --------------------------------------------------------------------------- //
// Structured solution — mirrors generate_solution()
// --------------------------------------------------------------------------- //
export function generateSolution(p: Params): Json {
  const { task, a1, d, n } = p;
  const answer = solve(p);
  let steps: Json[];
  if (task === "nth_term") {
    steps = [
      { number: 1, transformation: "State the formula", ruleOrTheorem: "u_n = u_1 + (n - 1)d" },
      { number: 2, transformation: "Substitute", intermediateResult: `u_{${n}} = ${a1} + (${n} - 1)\\times(${d})`, dependsOn: [1] },
      { number: 3, transformation: "Evaluate", intermediateResult: `u_{${n}} = ${answer}`, dependsOn: [2], marks: 1 },
    ];
  } else if (task === "sum_n") {
    steps = [
      { number: 1, transformation: "State the formula", ruleOrTheorem: "S_n = n/2 (2u_1 + (n - 1)d)" },
      { number: 2, transformation: "Substitute", intermediateResult: `S_{${n}} = \\frac{${n}}{2}(2\\times${a1} + (${n} - 1)\\times(${d}))`, dependsOn: [1] },
      { number: 3, transformation: "Evaluate", intermediateResult: `S_{${n}} = ${answer}`, dependsOn: [2], marks: 1 },
    ];
  } else if (task === "find_d") {
    const value = givenValue(p);
    steps = [
      { number: 1, transformation: "State the formula", ruleOrTheorem: "u_n = u_1 + (n - 1)d" },
      { number: 2, transformation: "Rearrange for d", intermediateResult: `d = \\frac{u_n - u_1}{n - 1} = \\frac{${value} - ${a1}}{${n} - 1}`, dependsOn: [1] },
      { number: 3, transformation: "Evaluate", intermediateResult: `d = ${answer}`, dependsOn: [2], marks: 1 },
    ];
  } else {
    const value = givenValue(p);
    steps = [
      { number: 1, transformation: "State the formula", ruleOrTheorem: "u_n = u_1 + (n - 1)d" },
      { number: 2, transformation: "Rearrange for n", intermediateResult: `n = \\frac{u_n - u_1}{d} + 1 = \\frac{${value} - ${a1}}{${d}} + 1`, dependsOn: [1] },
      { number: 3, transformation: "Evaluate", intermediateResult: `n = ${answer}`, dependsOn: [2], marks: 1 },
    ];
  }
  return { steps };
}

// --------------------------------------------------------------------------- //
// Prompt + accessibility + difficulty — mirror the oracle
// --------------------------------------------------------------------------- //
function ordinal(n: number): string {
  let suffix: string;
  if (n % 100 >= 10 && n % 100 <= 20) suffix = "th";
  else suffix = ({ 1: "st", 2: "nd", 3: "rd" } as Record<number, string>)[n % 10] ?? "th";
  return `${n}${suffix}`;
}

function promptBlocks(p: Params): { instruction: string; blocks: Json[]; spoken: string } {
  const { task, a1, d, n } = p;
  if (task === "nth_term") {
    return {
      instruction: "Find",
      blocks: [
        { kind: "text", text: `An arithmetic sequence has first term ${a1} and common difference ${d}.` },
        { kind: "text", text: `Find the ${ordinal(n)} term of the sequence.` },
      ],
      spoken: `An arithmetic sequence has first term ${a1} and common difference ${d}. Find the ${ordinal(n)} term.`,
    };
  }
  if (task === "sum_n") {
    return {
      instruction: "Find",
      blocks: [
        { kind: "text", text: `An arithmetic sequence has first term ${a1} and common difference ${d}.` },
        { kind: "text", text: `Find the sum of the first ${n} terms of the sequence.` },
      ],
      spoken: `An arithmetic sequence has first term ${a1} and common difference ${d}. Find the sum of the first ${n} terms.`,
    };
  }
  if (task === "find_d") {
    const value = givenValue(p);
    return {
      instruction: "Find",
      blocks: [
        { kind: "text", text: `An arithmetic sequence has first term ${a1}, and its ${ordinal(n)} term is ${value}.` },
        { kind: "text", text: "Find the common difference of the sequence." },
      ],
      spoken: `An arithmetic sequence has first term ${a1}, and its ${ordinal(n)} term is ${value}. Find the common difference.`,
    };
  }
  const value = givenValue(p);
  return {
    instruction: "Find",
    blocks: [
      { kind: "text", text: `An arithmetic sequence has first term ${a1} and common difference ${d}.` },
      { kind: "text", text: `One term of the sequence is ${value}. Find which term this is.` },
    ],
    spoken: `An arithmetic sequence has first term ${a1} and common difference ${d}. One term is ${value}. Find which term it is.`,
  };
}

const DIFFICULTY_WEIGHTS = { numericalComplexity: 0.3, reasoningSteps: 0.45, abstraction: 0.25 };

function round3(x: number): number { return Math.floor(x * 1000 + 0.5) / 1000; }

function difficulty(p: Params): Json {
  const { task, a1, d, n } = p;
  const magnitude = (Math.abs(a1) / A1_MAX + Math.abs(d) / D_ABS_MAX + n / N_MAX) / 3;
  const numerical = Math.min(1, magnitude + (d < 0 ? 0.1 : 0));
  const steps = { nth_term: 0.2, sum_n: 0.5, find_d: 0.7, find_n_for_value: 0.7 }[task];
  const abstraction = REVERSE_TASKS.includes(task) ? 0.6 : 0.1;
  const axes = { numericalComplexity: round3(numerical), reasoningSteps: steps, abstraction };
  const score = Math.max(0, Math.min(1,
    DIFFICULTY_WEIGHTS.numericalComplexity * axes.numericalComplexity +
    DIFFICULTY_WEIGHTS.reasoningSteps * axes.reasoningSteps +
    DIFFICULTY_WEIGHTS.abstraction * axes.abstraction));
  const band = Math.min(5, 1 + Math.floor(score * 5));
  return { overallBand: band, axes };
}

// --------------------------------------------------------------------------- //
// generate()
// --------------------------------------------------------------------------- //
export function generate(seed: number, config: Config = {}): Record<string, Json> {
  const rng = new Mulberry32(seed);
  const { params, answerType } = chooseParams(rng, config);
  const { task } = params;
  const answerValue = solve(params);
  const pr = promptBlocks(params);

  const item: Record<string, Json> = {
    itemId: `ITEM-${GENERATOR_ID.replace(/\./g, "-")}-${seed}-${task}`,
    schemaVersion: "1.0.0",
    objectiveIds: [OBJECTIVE_BY_TASK[task]],
    generatorId: GENERATOR_ID,
    generatorVersion: GENERATOR_VERSION,
    seed,
    params: { task: params.task, a1: params.a1, d: params.d, n: params.n },
    prompt: { instruction: pr.instruction, blocks: pr.blocks },
    answer: { type: "integer", canonical: answerValue, display: String(answerValue) },
    solution: generateSolution(params),
    difficulty: difficulty(params),
    calculatorPolicy: "either",
    accessibility: { spokenMath: pr.spoken, nonColorIndicators: true },
    provenance: {
      origin: "generated",
      rightsStatus: "academy-owned",
      originalityNote: "Original parameterized item; structure abstracted from curriculum.",
    },
    lifecycle: { state: "generated" },
  };

  if (answerType === "multiple-choice") {
    (item["answer"] as Record<string, Json>)["type"] = "multiple-choice";
    const distractors = generateDistractors(params);
    item["distractors"] = distractors.map((dd, i) => ({
      id: `d${i + 1}`, value: dd.value, display: String(dd.value), misconceptionId: dd.misconceptionId,
    }));
    interface Opt { value: number; correct: boolean; misconceptionId: string | null; }
    const pool: Opt[] = [{ value: answerValue, correct: true, misconceptionId: null }];
    for (const dd of distractors) pool.push({ value: dd.value, correct: false, misconceptionId: dd.misconceptionId });
    const shuffled = rng.shuffle(pool);
    const labels = ["A", "B", "C", "D", "E"];
    item["options"] = shuffled.map((o, i) => {
      const opt: Record<string, Json> = { label: labels[i] as string, value: o.value, display: String(o.value), correct: o.correct };
      if (o.misconceptionId) opt["misconceptionId"] = o.misconceptionId;
      return opt;
    });
  }
  return item;
}

export function serialize(item: Record<string, Json>): string {
  return canonicalStringify(item);
}
