/**
 * Linear equations (one variable) generator (production TypeScript).
 *
 * Generator id : gen.algebra.linear-equations   Version: 1.0.0
 * Spec         : docs/GENERATOR_SPEC_linear_equations_proposal.md (APPROVED w/ revisions)
 * Stage        : SPI-Math Middle School -> Algebra -> Linear equations in one variable
 *
 * Byte-for-byte counterpart of oracle/spi_oracle/linear_equations.py. Equations are
 * constructed BACKWARD from a chosen exact solution over the minimal LinExpr algebra
 * (no CAS); the validator re-derives everything independently.
 */

import { Mulberry32 } from "../../core/seeded-random/mulberry32.ts";
import { type Json } from "../../core/serialization/canonical.ts";
import { Rational, rat } from "../../core/exact-math/rational.ts";
import { LinExpr, normalize } from "../../core/exact-math/linexpr.ts";
import { round3 } from "../../core/difficulty/band.ts";
import { resolveInteractionType } from "../../core/sdk/interaction.ts";
import { assembleMultipleChoice } from "../../core/sdk/multiple-choice.ts";
import { canonicalStringify } from "../../core/serialization/canonical.ts";
import {
  answerSolutionAgrees, exactlyOneCorrectByDisplay, wrongOptionsUniqueByDisplay,
  spokenMathPresent, interactionTypeValid, answerTypeConsistent, provenanceComplete, versionFieldsPresent,
} from "../../core/sdk/checks.ts";
import { MISCONCEPTIONS, rulesFor, type Red } from "./linear-misconceptions.ts";

export const GENERATOR_ID = "gen.algebra.linear-equations";
export const GENERATOR_VERSION = "1.0.1";

export type Task = "one_step_add" | "one_step_mul" | "two_step" | "both_sides" | "brackets";
export const TASKS: Task[] = ["one_step_add", "one_step_mul", "two_step", "both_sides", "brackets"];

const NZ: number[] = [];
for (let x = -9; x <= 9; x++) if (x !== 0) NZ.push(x);
const A_MUL: number[] = [];
for (let x = -9; x <= 9; x++) if (x !== -1 && x !== 0 && x !== 1) A_MUL.push(x);
const K_POOL: number[] = [];
for (let x = -6; x <= 6; x++) if (x !== -1 && x !== 0 && x !== 1) K_POOL.push(x);

const MAX_NUM = 10000, MAX_DEN = 144, MAX_COEF = 400, MAX_PARAM_ATTEMPTS = 256;
const CALCULATOR_POLICY = "calculator-not-required";

const OBJECTIVE_BY_TASK: Record<Task, string> = {
  one_step_add: "SPI.MIDDLE.ALG.LINEQ.ONESTEP_ADD.01",
  one_step_mul: "SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01",
  two_step: "SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01",
  both_sides: "SPI.MIDDLE.ALG.LINEQ.BOTHSIDES.01",
  brackets: "SPI.MIDDLE.ALG.LINEQ.BRACKETS.01",
};
const TASK_BANDS: Record<Task, [number, number]> = {
  one_step_add: [1, 2], one_step_mul: [1, 2], two_step: [2, 3], both_sides: [3, 4], brackets: [3, 5],
};

type RJ = { num: number; den: number };
export interface Params { task: Task; [k: string]: Json; }
export interface Config { task?: Task; answerType?: "integer" | "multiple-choice"; interactionType?: "free-response" | "multiple-choice"; }
interface Cand { value: Rational; misconceptionId: string; rationale: string; }

const F = (d: RJ): Rational => new Rational(d.num, d.den);
const J = (v: number | Rational): RJ => Rational.from(v).toJSON();
const dispR = (x: Rational): string => x.toString();

function terminates(den: number): boolean {
  let d = den;
  while (d % 2 === 0) d /= 2;
  while (d % 5 === 0) d /= 5;
  return d === 1;
}

function answerObj(value: Rational): Record<string, Json> {
  return {
    type: value.den === 1 ? "integer" : "exact-rational",
    canonical: value.toJSON(),
    display: value.toString(),
    accepts: { fraction: true, decimal: terminates(value.den), mixed: false },
  };
}

function reduced(p: Params): Red {
  const task = p.task;
  if (task === "one_step_add") return { P: rat(1), Q: F(p["b"] as RJ), R: rat(0), T: F(p["c"] as RJ), kMul: null, innerP: null, innerQ: null };
  if (task === "one_step_mul") return { P: F(p["a"] as RJ), Q: rat(0), R: rat(0), T: F(p["c"] as RJ), kMul: null, innerP: null, innerQ: null };
  if (task === "two_step") return { P: F(p["a"] as RJ), Q: F(p["b"] as RJ), R: rat(0), T: F(p["c"] as RJ), kMul: null, innerP: null, innerQ: null };
  if (task === "both_sides") return { P: F(p["a"] as RJ), Q: F(p["b"] as RJ), R: F(p["c"] as RJ), T: F(p["d"] as RJ), kMul: null, innerP: null, innerQ: null };
  const k = F(p["k"] as RJ), pp = F(p["p"] as RJ), q = F(p["q"] as RJ);
  return { P: k.mul(pp), Q: k.mul(q), R: F(p["c"] as RJ), T: F(p["d"] as RJ), kMul: k, innerP: pp, innerQ: q };
}

export function solve(p: Params): Rational {
  const red = reduced(p);
  if (red.P.equals(red.R)) throw new Error("equation does not have a unique solution (P == R)");
  return red.T.sub(red.Q).div(red.P.sub(red.R));
}

function buildSides(p: Params): [LinExpr, LinExpr] {
  const task = p.task;
  if (task === "one_step_add") return [LinExpr.coef(1, F(p["b"] as RJ)), LinExpr.coef(0, F(p["c"] as RJ))];
  if (task === "one_step_mul") return [LinExpr.coef(F(p["a"] as RJ), 0), LinExpr.coef(0, F(p["c"] as RJ))];
  if (task === "two_step") return [LinExpr.coef(F(p["a"] as RJ), F(p["b"] as RJ)), LinExpr.coef(0, F(p["c"] as RJ))];
  if (task === "both_sides") return [LinExpr.coef(F(p["a"] as RJ), F(p["b"] as RJ)), LinExpr.coef(F(p["c"] as RJ), F(p["d"] as RJ))];
  const lhs = LinExpr.coef(F(p["p"] as RJ), F(p["q"] as RJ)).scale(F(p["k"] as RJ));
  return [lhs, LinExpr.coef(F(p["c"] as RJ), F(p["d"] as RJ))];
}

const withinCaps = (x: Rational): boolean => Math.abs(x.num) <= MAX_NUM && x.den <= MAX_DEN;

function coeffsWithinCaps(p: Params): boolean {
  const red = reduced(p);
  const vals = [red.P, red.Q, red.R, red.T];
  for (const key of ["a", "b", "c", "d", "k", "p", "q"]) if (key in p) vals.push(F(p[key] as RJ));
  return vals.every((v) => Math.abs(v.num) <= MAX_COEF && v.den <= MAX_DEN);
}

export function generateDistractors(p: Params): Cand[] | null {
  const red = reduced(p);
  const correct = solve(p);
  const chosen: Cand[] = [];
  const key = (v: Rational): string => `${v.num}/${v.den}`;
  const seen = new Set<string>([key(correct)]);
  for (const mid of rulesFor(p.task)) {
    const w = MISCONCEPTIONS[mid]!.wrong(red);
    if (w === null || !withinCaps(w) || seen.has(key(w))) continue;
    seen.add(key(w));
    chosen.push({ value: w, misconceptionId: mid, rationale: MISCONCEPTIONS[mid]!.observableError });
    if (chosen.length === 3) break;
  }
  return chosen.length === 3 ? chosen : null;
}

// --- rendering ----------------------------------------------------------- //
function coefTerm(a: Rational): string {
  if (a.equals(rat(1))) return "x";
  if (a.equals(rat(-1))) return "-x";
  if (a.den === 1) return `${a.num}x`;
  return `\\frac{${a.num}}{${a.den}}x`;
}
function signedConst(b: Rational): string {
  if (b.isZero()) return "";
  return b.num > 0 ? ` + ${b.toString()}` : ` - ${b.neg().toString()}`;
}
function side(a: Rational, b: Rational): string {
  return a.isZero() ? b.toString() : coefTerm(a) + signedConst(b);
}
function eq(aL: Rational, bL: Rational, aR: Rational, bR: Rational): string {
  return `${side(aL, bL)} = ${side(aR, bR)}`;
}
function rgt(a: Rational, b: Rational): boolean { return a.num * b.den > b.num * a.den; } // a > b (dens > 0)
function equationLatex(p: Params): string {
  if (p.task === "brackets") {
    const k = F(p["k"] as RJ), pp = F(p["p"] as RJ), q = F(p["q"] as RJ), c = F(p["c"] as RJ), d = F(p["d"] as RJ);
    return `${k.toString()}(${side(pp, q)}) = ${side(c, d)}`;
  }
  const red = reduced(p);
  return eq(red.P, red.Q, red.R, red.T);
}
function promptBlocks(p: Params): { instruction: string; blocks: Json[]; spoken: string } {
  const e = equationLatex(p);
  return {
    instruction: "Solve",
    blocks: [{ kind: "text", text: "Solve the equation for x." }, { kind: "math", latex: e }],
    spoken: `Solve the equation ${e} for x.`,
  };
}

export function generateSolution(p: Params): Json {
  const red = reduced(p);
  const s = solve(p);
  const sd = dispR(s);
  const steps: Record<string, Json>[] = [];
  let n = 0;
  let prev: number | null = null;
  const add = (transformation: string, opts: { intermediate?: string; rule?: string; explanation?: string; marks?: number; depends?: number[] }): number => {
    n += 1;
    const st: Record<string, Json> = { number: n, transformation };
    if (opts.rule !== undefined) st["ruleOrTheorem"] = opts.rule;
    if (opts.intermediate !== undefined) st["intermediateResult"] = opts.intermediate;
    if (opts.explanation !== undefined) st["explanation"] = opts.explanation;
    if (opts.depends !== undefined) st["dependsOn"] = opts.depends;
    if (opts.marks !== undefined) st["marks"] = opts.marks;
    steps.push(st);
    return n;
  };
  const dep = (): number[] | undefined => (prev !== null ? [prev] : undefined);

  const subTerm = (coef: Rational): string =>
    coef.num > 0 ? `Subtract ${coefTerm(coef)} from both sides` : `Add ${coefTerm(coef.neg())} to both sides`;
  const moveConst = (c: Rational): string =>
    c.num > 0 ? `Subtract ${c.toString()} from both sides` : `Add ${c.neg().toString()} to both sides`;

  let aL = red.P, bL = red.Q, aR = red.R, bR = red.T;
  if (p.task === "brackets") {
    prev = add("Expand the brackets", { intermediate: eq(red.P, red.Q, red.R, red.T), rule: `Multiply every term inside the bracket by ${dispR(red.kMul as Rational)}.` });
  }
  // Collect variable terms keeping a POSITIVE coefficient: subtract the smaller term.
  let varLeft = true;
  if (!aR.isZero()) {
    if (rgt(aL, aR)) {
      const newAL = aL.sub(aR);
      prev = add(subTerm(aR), { intermediate: eq(newAL, bL, rat(0), bR), explanation: "Collect the variable terms on one side (keeping a positive coefficient).", depends: dep() });
      aL = newAL; aR = rat(0);
    } else {
      const newAR = aR.sub(aL);
      prev = add(subTerm(aL), { intermediate: eq(rat(0), bL, newAR, bR), explanation: "Collect the variable terms on one side (keeping a positive coefficient).", depends: dep() });
      aL = rat(0); aR = newAR; varLeft = false;
    }
  }
  let coef: Rational;
  if (varLeft) {
    coef = aL;
    if (!bL.isZero()) {
      const newBR = bR.sub(bL);
      prev = add(moveConst(bL), { intermediate: eq(aL, rat(0), rat(0), newBR), explanation: "Collect the constants on the other side.", depends: dep() });
      bL = rat(0); bR = newBR;
    }
  } else {
    coef = aR;
    if (!bR.isZero()) {
      const newBL = bL.sub(bR);
      prev = add(moveConst(bR), { intermediate: eq(rat(0), newBL, aR, rat(0)), explanation: "Collect the constants on the other side.", depends: dep() });
      bL = newBL; bR = rat(0);
    }
  }
  if (!coef.equals(rat(1))) {
    prev = add(`Divide both sides by ${dispR(coef)}`, { intermediate: `x = ${sd}`, explanation: "Divide by the coefficient of x.", depends: dep() });
  }
  prev = add("State the exact solution", { intermediate: `x = ${sd}`, marks: 1, depends: dep() });
  const [lhs] = buildSides(p);
  const lv = lhs.eval(s);
  add("Verify by substitution", { intermediate: `Substitute x = ${sd}: \\text{LHS} = ${dispR(lv)} = \\text{RHS}, so x = ${sd}.`, explanation: "Both sides are equal, confirming the solution.", depends: [prev] });
  return { steps };
}

// --- difficulty ---------------------------------------------------------- //
const STEP_COUNT: Record<Task, number> = { one_step_add: 1, one_step_mul: 1, two_step: 2, both_sides: 3, brackets: 4 };

function difficulty(p: Params): Json {
  const red = reduced(p);
  const s = solve(p);
  const disp: Rational[] = [];
  for (const key of ["a", "b", "c", "d", "k", "p", "q"]) if (key in p) disp.push(F(p[key] as RJ));
  const mag = Math.max(...disp.map((v) => Math.abs(v.num) + (v.den - 1)), Math.abs(s.num) + (s.den - 1));
  const numerical = Math.min(1.0, mag / 12.0);
  const reasoning = STEP_COUNT[p.task] / 4.0;
  const fracCoef = disp.some((v) => v.den !== 1);
  const both = !red.R.isZero();
  const negatives = disp.some((v) => v.num < 0);
  const rationy = s.den !== 1 || fracCoef;
  const baseAlg = { one_step_add: 0.1, one_step_mul: 0.2, two_step: 0.4, both_sides: 0.65, brackets: 0.85 }[p.task];
  const algebraic = Math.min(1.0, baseAlg + (fracCoef ? 0.1 : 0.0) + (both ? 0.1 : 0.0));
  const representation = Math.min(1.0, (negatives ? 0.5 : 0.15) + (rationy ? 0.25 : 0.0));
  const axes = {
    numericalComplexity: round3(numerical), reasoningSteps: round3(reasoning),
    algebraicComplexity: round3(algebraic), representation: round3(representation),
  };
  const factors = (negatives ? 1 : 0) + (rationy ? 1 : 0) + (mag > 9 ? 1 : 0);
  const [lo, hi] = TASK_BANDS[p.task];
  const band = lo + Math.min(factors, hi - lo);
  return { overallBand: band, axes };
}

// --- sampling ------------------------------------------------------------ //
function drawParams(rng: Mulberry32, explicitTask: Task | undefined): Params {
  const task = explicitTask ?? rng.choice(TASKS);
  if (task === "one_step_add") {
    const b = rng.choice(NZ), m = rng.nextInt(-12, 12);
    return { task, b: J(b), c: J(m + b) };
  }
  if (task === "one_step_mul") {
    const a = rng.choice(A_MUL), m = rng.nextInt(-9, 9);
    return { task, a: J(a), c: J(m) };
  }
  if (task === "two_step") {
    const a = rng.nextInt(0, 4) === 0 ? rat(1, rng.choice([2, 3, 4])) : rat(rng.choice(A_MUL));
    const m = rng.nextInt(-9, 9), b = rng.choice(NZ);
    return { task, a: J(a), b: J(b), c: J(m + b) };
  }
  if (task === "both_sides") {
    const a = rng.choice(NZ);
    let c = rng.choice(NZ);
    while (c === a) c = rng.choice(NZ);
    const m = rng.nextInt(-9, 9), b = rng.choice(NZ);
    return { task, a: J(a), b: J(b), c: J(c), d: J(m + b) };
  }
  // brackets: two-way draw spreads complexity across bands 3-5.
  let k: number, pp: number, q: number, c: number, m: number;
  if (rng.nextInt(0, 1) === 0) {
    k = rng.choice([2, 3, -2, -3]);
    pp = 1;
    q = rng.choice([1, 2, 3, -1, -2, -3]);
    c = rng.choice([0, 1, -1, 2, -2]);
    while (k * pp === c) c = rng.choice([0, 1, -1, 2, -2]);
    const j = rng.nextInt(-4, 4);
    m = (k * pp - c) * j; // integer solution j
  } else {
    k = rng.choice(K_POOL);
    pp = rng.choice(NZ);
    q = rng.choice(NZ);
    c = rng.nextInt(-9, 9);
    while (k * pp === c) c = rng.nextInt(-9, 9);
    m = rng.nextInt(-9, 9);
  }
  return { task, k: J(k), p: J(pp), q: J(q), c: J(c), d: J(m + k * q) };
}

function guardsOk(p: Params, red: Red): boolean {
  if (red.P.equals(red.R)) return false;
  const task = p.task;
  if (task === "one_step_add") return !red.Q.isZero();
  if (task === "one_step_mul") return !red.P.isZero() && !red.P.equals(rat(1));
  if (task === "two_step") return !red.P.isZero() && !red.P.equals(rat(1)) && !red.Q.isZero();
  if (task === "both_sides") {
    const a = F(p["a"] as RJ), c = F(p["c"] as RJ);
    return !a.isZero() && !c.isZero() && !a.equals(c);
  }
  const k = F(p["k"] as RJ), pp = F(p["p"] as RJ), q = F(p["q"] as RJ);
  return !k.isZero() && !k.equals(rat(1)) && !pp.isZero() && !q.isZero() && !k.mul(pp).equals(F(p["c"] as RJ));
}

function acceptable(p: Params, answerType: string): Cand[] | null {
  const red = reduced(p);
  if (!guardsOk(p, red)) return null;
  let s: Rational;
  try { s = solve(p); } catch { return null; }
  if (!withinCaps(s) || !coeffsWithinCaps(p)) return null;
  if (answerType === "multiple-choice") return generateDistractors(p);
  return [];
}

export function generate(seed: number, config: Config = {}): Record<string, Json> {
  const answerType = resolveInteractionType(config) === "multiple-choice" ? "multiple-choice" : "integer";
  const explicitTask = config.task;
  if (explicitTask != null && !TASKS.includes(explicitTask)) throw new Error(`unknown task: ${explicitTask}`);

  const rng = new Mulberry32(seed);
  let params!: Params;
  let distractors: Cand[] | null = null;
  let ok = false;
  for (let i = 0; i < MAX_PARAM_ATTEMPTS; i++) {
    params = drawParams(rng, explicitTask);
    const result = acceptable(params, answerType);
    if (result === null) continue;
    distractors = result;
    ok = true;
    break;
  }
  if (!ok) throw new Error("could not find acceptable linear-equation parameters");

  const task = params.task;
  const ans = solve(params);
  const pr = promptBlocks(params);
  const interaction = answerType === "multiple-choice" ? "multiple-choice" : "free-response";

  const item: Record<string, Json> = {
    itemId: `ITEM-${GENERATOR_ID.replace(/\./g, "-")}-${seed}-${task}`,
    schemaVersion: "1.0.0",
    objectiveIds: [OBJECTIVE_BY_TASK[task]],
    generatorId: GENERATOR_ID,
    generatorVersion: GENERATOR_VERSION,
    seed,
    params: params as unknown as Json,
    interactionType: interaction,
    prompt: { instruction: pr.instruction, blocks: pr.blocks },
    answer: answerObj(ans),
    solution: generateSolution(params),
    difficulty: difficulty(params),
    calculatorPolicy: CALCULATOR_POLICY,
    accessibility: { spokenMath: pr.spoken, nonColorIndicators: true },
    provenance: { origin: "generated", rightsStatus: "academy-owned", originalityNote: "Original parameterized item; structure abstracted from curriculum." },
    lifecycle: { state: "generated" },
  };

  if (answerType === "multiple-choice") {
    const mc = assembleMultipleChoice(rng, ans, distractors ?? [], (v) => ({ value: v.toJSON(), display: v.toString() }));
    item["distractors"] = mc.distractors;
    item["options"] = mc.options;
  }
  return item;
}

// --- validation (independent) -------------------------------------------- //
export interface CheckResult { name: string; result: "pass" | "fail"; detail: string; }
export interface ValidationResult { status: "pass" | "fail"; validatorVersion: string; checks: CheckResult[]; }

function stepsPreserve(red: Red, ans: Rational): boolean {
  let aL = red.P, bL = red.Q, aR = red.R, bR = red.T;
  const root = (a1: Rational, b1: Rational, a2: Rational, b2: Rational): Rational | null =>
    a1.sub(a2).isZero() ? null : b2.sub(b1).div(a1.sub(a2));
  const stages: Array<[Rational, Rational, Rational, Rational]> = [[aL, bL, aR, bR]];
  let varLeft = true;
  if (!aR.isZero()) {
    if (rgt(aL, aR)) { const aL2 = aL.sub(aR); stages.push([aL2, bL, rat(0), bR]); aL = aL2; aR = rat(0); }
    else { const aR2 = aR.sub(aL); stages.push([rat(0), bL, aR2, bR]); aL = rat(0); aR = aR2; varLeft = false; }
  }
  let coef: Rational;
  if (varLeft) { coef = aL; if (!bL.isZero()) { const nb = bR.sub(bL); stages.push([aL, rat(0), rat(0), nb]); } }
  else { coef = aR; if (!bR.isZero()) { const nb = bL.sub(bR); stages.push([rat(0), nb, aR, rat(0)]); } }
  if (coef.isZero()) return false;
  for (const [a1, b1, a2, b2] of stages) {
    const r = root(a1, b1, a2, b2);
    if (r === null || !r.equals(ans)) return false;
  }
  return true;
}

/** True if student-facing text contains a bare internal symbol (p, q, r, t, k). */
function hasPlaceholder(text: string): boolean {
  return /(?<![A-Za-z])[pqrtk](?![A-Za-z])/.test(text);
}

function explicitReveal(item: Record<string, Json>): boolean {
  const disp = (item["answer"] as { display: string }).display.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const blocks = (item["prompt"] as { blocks: Array<{ text?: string; latex?: string }> }).blocks;
  let text = blocks.map((b) => `${b.text ?? ""} ${b.latex ?? ""}`).join(" ");
  text += " " + ((item["accessibility"] as { spokenMath?: string }).spokenMath ?? "");
  return new RegExp(`(?<![A-Za-z0-9])x\\s*=\\s*${disp}(?![\\d/])`).test(text);
}

export function validate(item: Record<string, Json>): ValidationResult {
  const checks: CheckResult[] = [];
  const add = (name: string, ok: boolean, detail = ""): void => { checks.push({ name, result: ok ? "pass" : "fail", detail }); };
  const params = item["params"] as unknown as Params;
  const red = reduced(params);
  const ansF = item["answer"] as { type: string; canonical: RJ; display: string };
  const ans = F(ansF.canonical);

  add("params-in-domain", guardsOk(params, red), `task=${params.task}`);
  add("answer-type-consistency", answerTypeConsistent(ansF.type, ansF.canonical), `type=${ansF.type}, den=${ansF.canonical.den}`);
  add("interaction-type", interactionTypeValid(item["interactionType"]), String(item["interactionType"]));

  const [lhs, rhs] = buildSides(params);
  const { A, B } = normalize(lhs, rhs);
  add("equation-is-linear-unique", !A.isZero(), `A=${A.toString()}`);
  add("normalized-form-matches", A.equals(red.P.sub(red.R)) && B.equals(red.Q.sub(red.T)), `A=${A.toString()}, B=${B.toString()}`);
  if (!A.isZero()) {
    const s2 = B.neg().div(A);
    add("solution-satisfies-equation", s2.equals(ans) && lhs.eval(ans).equals(rhs.eval(ans)), `resolved ${s2.toString()} vs ${ans.toString()}`);
  } else {
    add("solution-satisfies-equation", false, "A == 0");
  }
  add("steps-preserve-solution", stepsPreserve(red, ans), "root invariant under each operation");

  const steps = (item["solution"] as { steps: Array<{ intermediateResult?: string }> }).steps;
  add("answer-solution-agree", answerSolutionAgrees(steps[steps.length - 1]?.intermediateResult ?? "", ansF.display), "");
  add("no-answer-leakage", !explicitReveal(item), "no explicit 'x = answer' reveal in prompt");

  const distractors = item["distractors"] as Array<{ value: RJ; misconceptionId: string; rationale?: string }> | undefined;
  if (distractors) {
    const mids = distractors.map((d) => d.misconceptionId);
    add("distractors-distinct-misconceptions", new Set(mids).size === mids.length, JSON.stringify(mids));
    add("min-three-distractors", distractors.length >= 3, `${distractors.length}`);
    for (const d of distractors) {
      const m = MISCONCEPTIONS[d.misconceptionId];
      add("distractor-misconception-known", Boolean(m), d.misconceptionId);
      if (m) {
        const expected = m.wrong(red);
        add("distractor-value-matches-rule", expected !== null && expected.equals(F(d.value)), `${d.misconceptionId}`);
        add("distractor-rationale-matches", d.rationale === m.observableError, d.misconceptionId);
        const fb = m.feedback(red);
        add("distractor-feedback-present", Boolean(fb), d.misconceptionId);
        add("distractor-feedback-clean", !hasPlaceholder(fb), fb);
        add("distractor-not-answer", !F(d.value).equals(ans), `${d.value.num}/${d.value.den}`);
      }
    }
  }
  const options = item["options"] as Array<{ display: string; correct: boolean }> | undefined;
  if (options) {
    add("exactly-one-correct", exactlyOneCorrectByDisplay(options, ansF.display), "");
    add("distractors-unique", wrongOptionsUniqueByDisplay(options), "");
  }

  add("a11y-fields-present", spokenMathPresent(item), "");
  add("provenance-complete", provenanceComplete(item), "");
  add("version-fields-present", versionFieldsPresent(item), "");

  const status = checks.every((c) => c.result === "pass") ? "pass" : "fail";
  return { status, validatorVersion: "1.0.1", checks };
}

export function serialize(item: Record<string, Json>): string { return canonicalStringify(item); }

/** Student-facing feedback strings for an item's MC distractors (for review packs/tests). */
export function distractorFeedback(item: Record<string, Json>): string[] {
  const red = reduced(item["params"] as unknown as Params);
  const ds = (item["distractors"] as Array<{ misconceptionId: string }> | undefined) ?? [];
  return ds.map((d) => MISCONCEPTIONS[d.misconceptionId]!.feedback(red));
}
