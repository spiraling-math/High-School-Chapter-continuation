/**
 * Arithmetic sequences generator (production TypeScript).
 *
 * Generator id : gen.sequences.arithmetic   Version: 1.0.1
 * Spec         : docs/GENERATOR_SPEC_arithmetic_sequences.md
 *
 * Byte-for-byte counterpart of oracle/spi_oracle/sequences.py, asserted by the
 * golden- and parity-vector tests (Principle 4: independent verification across
 * two implementations). All maths uses integers only.
 *
 * v1.0.1: distinct-misconception distractors from the canonical registry, with
 * deterministic parameter regeneration when a clean set of three is not
 * available; clarified "find term index" wording; explicit calculator policy.
 */

import { Mulberry32 } from "../../core/seeded-random/mulberry32.ts";
import { canonicalStringify, type Json } from "../../core/serialization/canonical.ts";
import { round3, bandFromScore } from "../../core/difficulty/band.ts";
import { resolveInteractionType } from "../../core/sdk/interaction.ts";
import { assembleMultipleChoice } from "../../core/sdk/multiple-choice.ts";
import { MISCONCEPTIONS, rulesFor } from "./misconceptions.ts";

export const GENERATOR_ID = "gen.sequences.arithmetic";
export const GENERATOR_VERSION = "1.1.0";

export type Task = "nth_term" | "sum_n" | "find_d" | "find_n_for_value";
export const FORWARD_TASKS: Task[] = ["nth_term", "sum_n"];
export const REVERSE_TASKS: Task[] = ["find_d", "find_n_for_value"];
export const ALL_TASKS: Task[] = ["nth_term", "sum_n", "find_d", "find_n_for_value"];

const A1_MIN = -20, A1_MAX = 20;
const D_ABS_MIN = 1, D_ABS_MAX = 12;
const N_MIN = 3, N_MAX = 40;
const MAX_PARAM_ATTEMPTS = 64;
const CALCULATOR_POLICY = "calculator-not-required";

// v1.1.0: dedicated micro-objectives for the reverse tasks (curriculum-approved).
const OBJECTIVE_BY_TASK: Record<Task, string> = {
  nth_term: "SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01",
  find_d: "SPI.IBDPAASL.SEQSER.ARITH.COMMON_DIFF.01",
  find_n_for_value: "SPI.IBDPAASL.SEQSER.ARITH.TERM_INDEX.01",
  sum_n: "SPI.IBDPAASL.SEQSER.ARITH.SUM_N.01",
};

export interface Params { task: Task; a1: number; d: number; n: number; }
export interface Config { task?: Task; answerType?: "integer" | "multiple-choice"; interactionType?: "free-response" | "multiple-choice"; }
interface Cand { value: number; misconceptionId: string; rationale: string; }

// --------------------------------------------------------------------------- //
// Canonical mathematics (closed form)
// --------------------------------------------------------------------------- //
function nthTerm(a1: number, d: number, n: number): number { return a1 + (n - 1) * d; }
function sumN(a1: number, d: number, n: number): number { return (n * (2 * a1 + (n - 1) * d)) / 2; }
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
// Distractors — distinct misconceptions from the canonical registry
// --------------------------------------------------------------------------- //
export function generateDistractors(p: Params): Cand[] | null {
  const ruleIds = rulesFor(p.task);
  if (ruleIds.length === 0) return [];
  const correct = solve(p);
  const chosen: Cand[] = [];
  const seen = new Set<number>([correct]);
  for (const mid of ruleIds) {
    const m = MISCONCEPTIONS[mid]!;
    const val = m.formula(p);
    if (seen.has(val)) continue;
    seen.add(val);
    chosen.push({ value: val, misconceptionId: mid, rationale: m.observableError });
    if (chosen.length === 3) break;
  }
  return chosen.length === 3 ? chosen : null;
}

// --------------------------------------------------------------------------- //
// Structured solution
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
// Prompt + accessibility + difficulty
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
      { kind: "text", text: `The nth term of the sequence is ${value}. Find the value of n.` },
    ],
    spoken: `An arithmetic sequence has first term ${a1} and common difference ${d}. The nth term of the sequence is ${value}. Find the value of n.`,
  };
}

const DIFFICULTY_WEIGHTS = { numericalComplexity: 0.3, reasoningSteps: 0.45, abstraction: 0.25 };

function difficulty(p: Params): Json {
  const { task, a1, d, n } = p;
  const magnitude = (Math.abs(a1) / A1_MAX + Math.abs(d) / D_ABS_MAX + n / N_MAX) / 3;
  const numerical = Math.min(1, magnitude + (d < 0 ? 0.1 : 0));
  const steps = { nth_term: 0.2, sum_n: 0.5, find_d: 0.7, find_n_for_value: 0.7 }[task];
  const abstraction = REVERSE_TASKS.includes(task) ? 0.6 : 0.1;
  const axes = { numericalComplexity: round3(numerical), reasoningSteps: steps, abstraction };
  const band = bandFromScore(
    DIFFICULTY_WEIGHTS.numericalComplexity * axes.numericalComplexity +
    DIFFICULTY_WEIGHTS.reasoningSteps * axes.reasoningSteps +
    DIFFICULTY_WEIGHTS.abstraction * axes.abstraction);
  return { overallBand: band, axes };
}

// --------------------------------------------------------------------------- //
// generate()
// --------------------------------------------------------------------------- //
function drawParams(rng: Mulberry32, explicitTask: Task | undefined, answerType: string): Params {
  let task: Task;
  if (explicitTask != null) {
    task = explicitTask;
  } else {
    const pool = answerType === "multiple-choice" ? FORWARD_TASKS : ALL_TASKS;
    task = rng.choice(pool);
  }
  const a1 = rng.nextInt(A1_MIN, A1_MAX);
  const dMag = rng.nextInt(D_ABS_MIN, D_ABS_MAX);
  const d = rng.nextFloat() < 0.5 ? dMag : -dMag;
  const n = rng.nextInt(N_MIN, N_MAX);
  return { task, a1, d, n };
}

export function generate(seed: number, config: Config = {}): Record<string, Json> {
  // Accept the forward `interactionType` key and the legacy `answerType` (TD-1).
  const answerType = resolveInteractionType(config) === "multiple-choice" ? "multiple-choice" : "integer";
  const explicitTask = config.task;
  if (explicitTask != null && !ALL_TASKS.includes(explicitTask)) throw new Error(`unknown task: ${explicitTask}`);
  if (answerType === "multiple-choice" && explicitTask != null && REVERSE_TASKS.includes(explicitTask)) {
    throw new Error("multiple-choice is only offered for forward tasks");
  }

  const rng = new Mulberry32(seed);
  let params!: Params;
  let distractors: Cand[] | null = null;
  let ok = false;
  for (let attempt = 0; attempt < MAX_PARAM_ATTEMPTS; attempt++) {
    params = drawParams(rng, explicitTask, answerType);
    if (answerType === "multiple-choice") {
      distractors = generateDistractors(params);
      if (distractors === null) continue; // regenerate parameters
    }
    ok = true;
    break;
  }
  if (!ok) throw new Error("could not find parameters yielding three distinct distractors");

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
    calculatorPolicy: CALCULATOR_POLICY,
    accessibility: { spokenMath: pr.spoken, nonColorIndicators: true },
    provenance: {
      origin: "generated",
      rightsStatus: "academy-owned",
      originalityNote: "Original parameterized item; structure abstracted from curriculum.",
    },
    lifecycle: { state: "generated" },
  };

  if (answerType === "multiple-choice") {
    const ds = distractors ?? [];
    (item["answer"] as Record<string, Json>)["type"] = "multiple-choice";
    const mc = assembleMultipleChoice(rng, answerValue, ds, (v) => ({ value: v, display: String(v) }));
    item["distractors"] = mc.distractors;
    item["options"] = mc.options;
  }
  return item;
}

export function serialize(item: Record<string, Json>): string {
  return canonicalStringify(item);
}
