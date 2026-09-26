/**
 * gen.functions.foundations v1.0.0 — TypeScript mirror of oracle/spi_oracle/functions.py.
 *
 * IB Mathematics: Analysis and Approaches SL, Oxford chapter 2 (ToC 2.1, 2.2, 2.4, 2.5, 2.6). Eleven exact
 * tasks over linear, quadratic, reciprocal and square-root rules: identify_function (multiple-choice only),
 * evaluate_function, solve_for_input, domain_of_function, range_of_function, composite_value,
 * composite_expression, function_from_composite, inverse_value, inverse_expression, one_to_one_restriction.
 * Specification: docs/GENERATOR_SPEC_functions_PROPOSAL.md.
 *
 * Byte-for-byte parity with the Python oracle (the draw order there is NORMATIVE); gated by
 * oracle/golden/functions.golden.json + functions.parity.json through functions.parity.test.ts.
 * Registered PENDING-REVIEW: visible only in the Studio's review mode, never in production exports or
 * samples, until the owner approves the family.
 */

import { Rational, rat } from "../../core/exact-math/rational.ts";
import { Poly, ratDisplay, ratFromJson, ratJson, type RatJson, type PolyJson } from "../../core/exact-math/polynomial.ts";
import { Mulberry32 } from "../../core/seeded-random/mulberry32.ts";
import { round3, clamp01 } from "../../core/difficulty/band.ts";
import { canonicalStringify } from "../../core/serialization/canonical.ts";
import { assembleMultipleChoice } from "../../core/sdk/multiple-choice.ts";
import { checkExpression } from "../../core/answer-checking/expression-checker.ts";
import { checkInterval, intervalDisplay, intervalToJson, type Interval, type IntervalJson } from "../../core/answer-checking/interval-checker.ts";
import * as C from "./functions-core.ts";
import type { Rule, RuleJson } from "./functions-core.ts";
import * as FM from "./functions-misconceptions.ts";
import type { Ctx, ReciprocalOf, WrongValue } from "./functions-misconceptions.ts";
import {
  FUNCTIONS_TASKS, OBJECTIVE_BY_TASK, TASK_BANDS, MC_ONLY_TASKS, supportedInteractions,
} from "../../core/curriculum/functions-objective-ids.ts";

// Local Json alias (matches the convention in the other domain mirrors, e.g. mensuration.ts).
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = any;
type Params = Record<string, Json>;

export const GENERATOR_ID = "gen.functions.foundations";
export const GENERATOR_VERSION = "1.0.0";
export const VALIDATOR_VERSION = "1.0.0";
export const CALCULATOR_POLICY = "calculator-not-required";
export const SCHEMA_VERSION = "1.0.0";
const MAX_PARAM_ATTEMPTS = 256;

export const TASKS: readonly string[] = [...FUNCTIONS_TASKS];
export { OBJECTIVE_BY_TASK, TASK_BANDS, MC_ONLY_TASKS, supportedInteractions };

type Family = "choice" | "number" | "interval" | "expression";
export const ANSWER_FAMILY: Record<string, Family> = {
  identify_function: "choice", evaluate_function: "number", solve_for_input: "number",
  domain_of_function: "interval", range_of_function: "interval", composite_value: "number",
  composite_expression: "expression", function_from_composite: "expression", inverse_value: "number",
  inverse_expression: "expression", one_to_one_restriction: "number",
};

const NAMES: readonly string[] = ["f", "g", "h"];
const rangeInc = (lo: number, hi: number): number[] => Array.from({ length: hi - lo + 1 }, (_, i) => lo + i);
const NZ5 = rangeInc(-5, 5).filter((x) => x !== 0);
const NZ6 = rangeInc(-6, 6).filter((x) => x !== 0);
const SMALL = rangeInc(-3, 3).filter((x) => x !== 0);
const MAX_NUM = 10000, MAX_DEN = 144;
const LABELS = ["A", "B", "C", "D", "E"];

const F = (x: Rational | number): Rational => Rational.from(x);
const ZERO = rat(0), ONE = rat(1);
const eqn = (a: Rational, b: number): boolean => a.equals(rat(b));

export class InteractionNotSupported extends Error {}

function pyList(items: string[]): string {
  return "[" + items.map((s) => `'${s}'`).join(", ") + "]";
}

/** Forward key only. The legacy `answerType` selector is NOT consulted (ratio v1.0.2 precedent): a legacy
 *  sweep therefore exercises every task at its default interaction and never raises. */
function resolveInteraction(task: string, config: Json): string {
  const requested = config.interactionType;
  if (requested === undefined || requested === null) {
    return (MC_ONLY_TASKS as string[]).includes(task) ? "multiple-choice" : "free-response";
  }
  if (requested !== "free-response" && requested !== "multiple-choice") {
    throw new InteractionNotSupported(`unsupported interaction '${requested}' for '${task}'`);
  }
  if (!supportedInteractions(task).includes(requested)) {
    throw new InteractionNotSupported(`task '${task}' does not support '${requested}' (supported: ${pyList(supportedInteractions(task))})`);
  }
  return requested;
}

// --------------------------------------------------------------------------- //
// Draws (the normative RNG order — mirror of functions.py exactly)
// --------------------------------------------------------------------------- //

const pickName = (rng: Mulberry32): string => rng.choice(NAMES);

function distinct(rng: Mulberry32, n: number, lo: number, hi: number): number[] {
  const vals: number[] = [];
  while (vals.length < n) {
    const v = rng.nextInt(lo, hi);
    if (!vals.includes(v)) vals.push(v);
  }
  return vals;
}

function collinear(pairs: number[][]): boolean {
  const [x0, y0] = pairs[0] as [number, number];
  const [x1, y1] = pairs[1] as [number, number];
  for (const [x, y] of pairs.slice(2) as [number, number][]) {
    if ((x1 - x0) * (y - y0) !== (y1 - y0) * (x - x0)) return false;
  }
  return true;
}

function drawIdentify(rng: Mulberry32): Params {
  const neg = rng.nextInt(0, 1) === 1;
  const lo = neg ? -4 : 0, hi = 9;
  const out = (): number => rng.nextInt(-6, 9);

  // the non-function: three distinct inputs, one of them repeated with a different output
  const ins = distinct(rng, 3, lo, hi);
  const r = rng.nextInt(0, 2);
  const outs = [out(), out(), out()];
  let o4 = out();
  while (o4 === outs[r]) o4 = out();
  const adjacent = rng.nextInt(0, 1) === 1;
  const nonFunction: number[][] = [0, 1, 2].map((i) => [ins[i]!, outs[i]!]);
  if (adjacent) nonFunction.splice(r + 1, 0, [ins[r]!, o4]);
  else nonFunction.push([ins[r]!, o4]);
  const separated = !adjacent && r !== 2;

  // D1: many-to-one (a repeated output, not all equal)
  const i1 = distinct(rng, 4, lo, hi);
  const y = out();
  const o1 = [out(), out(), out(), out()];
  const j = rng.nextInt(1, 3);
  const i = rng.nextInt(0, j - 1);
  o1[i] = y;
  o1[j] = y;
  if (o1.every((v) => v === y)) {
    const kk = [0, 1, 2, 3].find((t) => t !== i && t !== j)!;
    o1[kk] = y + 1;
  }
  const manyToOne = [0, 1, 2, 3].map((t) => [i1[t]!, o1[t]!]);

  // D2: constant
  const i2 = distinct(rng, 4, lo, hi);
  const y2 = out();
  const constant = [0, 1, 2, 3].map((t) => [i2[t]!, y2]);

  // D3: pattern-free (unsorted inputs, distinct outputs, not collinear)
  const i3 = distinct(rng, 4, lo, hi);
  const sortedI3 = [...i3].sort((a, b) => a - b);
  if (i3.every((v, k) => v === sortedI3[k])) {
    const t = i3[0]!;
    i3[0] = i3[1]!;
    i3[1] = t;
  }
  const o3: number[] = [];
  while (o3.length < 4) {
    const v = out();
    if (!o3.includes(v)) o3.push(v);
  }
  let patternFree = [0, 1, 2, 3].map((t) => [i3[t]!, o3[t]!]);
  if (collinear(patternFree)) {
    o3[3] = o3[3]! + 1;
    while (o3.slice(0, 3).includes(o3[3]!)) o3[3] = o3[3]! + 1;
    patternFree = [0, 1, 2, 3].map((t) => [i3[t]!, o3[t]!]);
  }

  return {
    task: "identify_function", nonFunction,
    functions: [{ pairs: manyToOne, misconceptionId: "MISC.FUNC.MANY_TO_ONE_REJECTED" },
      { pairs: constant, misconceptionId: "MISC.FUNC.CONSTANT_REJECTED" },
      { pairs: patternFree, misconceptionId: "MISC.FUNC.PATTERN_REQUIRED" }],
    negativeInputs: neg, separatedRepeat: separated,
  };
}

function drawQuadratic(rng: Mulberry32, aPool: readonly number[] = [1, 1, 2, -1, -2, 3]): Rule {
  return C.quadratic(rng.choice(aPool), rng.nextInt(-6, 6), rng.nextInt(-9, 9));
}

function drawEvaluate(rng: Mulberry32): Params | null {
  const kind = rng.choice(["linear", "quadratic", "reciprocal", "sqrt"]);
  const name = pickName(rng);
  const p = F(rng.nextInt(-6, 6));
  let rule: Rule;
  if (kind === "linear") {
    rule = C.linear(rng.choice(NZ5), rng.nextInt(-9, 9));
  } else if (kind === "quadratic") {
    rule = drawQuadratic(rng);
  } else if (kind === "reciprocal") {
    rule = C.reciprocal(rng.choice(NZ6), rng.nextInt(-5, 5), rng.nextInt(-4, 4));
    if (p.equals(rule.h!)) return null;
  } else {
    const t = rng.nextInt(0, 6);
    const a = rng.choice(SMALL);
    const v = rng.nextInt(-4, 4);
    rule = C.sqrtRule(a, rat(t * t).sub(rat(a).mul(p)), v);
  }
  return { task: "evaluate_function", name, rule, p };
}

function drawSolve(rng: Mulberry32): Params | null {
  const kind = rng.choice(["linear", "linear", "reciprocal", "sqrt"]);
  const name = pickName(rng);
  let rule: Rule, target: Rational, x0: Rational;
  if (kind === "linear") {
    const frac = rng.nextInt(0, 3) === 0;
    let a: Rational;
    if (frac) {
      const d = rng.choice([2, 3]);
      const n = rng.choice(rangeInc(-9, 9).filter((x) => x % d !== 0));
      x0 = new Rational(n, d);
      a = F(d * rng.choice([1, -1, 2, -2]));
    } else {
      x0 = F(rng.nextInt(-8, 8));
      a = F(rng.choice(NZ5));
    }
    const b = F(rng.nextInt(-9, 9));
    rule = C.linear(a, b);
    target = a.mul(x0).add(b);
  } else if (kind === "reciprocal") {
    const k0 = rng.choice(NZ6);
    const h = rng.nextInt(-5, 5);
    const v = rng.nextInt(-4, 4);
    const divs = rangeInc(-6, 6).filter((d) => d !== 0 && k0 % d === 0);
    const d = rng.choice(divs);
    x0 = F(h + d);
    rule = C.reciprocal(k0, h, v);
    target = new Rational(k0, d).add(rat(v));
  } else {
    const t = rng.nextInt(0, 6);
    x0 = F(rng.nextInt(-6, 6));
    const a = rng.choice(SMALL);
    const v = rng.nextInt(-4, 4);
    rule = C.sqrtRule(a, rat(t * t).sub(rat(a).mul(x0)), v);
    target = F(t + v);
  }
  return { task: "solve_for_input", name, rule, target, x0 };
}

function drawDomain(rng: Mulberry32): Params | null {
  const kind = rng.choice(["sqrt", "sqrt", "reciprocal", "reciprocal", "linear", "quadratic"]);
  const name = pickName(rng);
  let rule: Rule;
  if (kind === "sqrt") rule = C.sqrtRule(rng.choice(NZ5), rng.nextInt(-6, 6), rng.nextInt(-3, 3));
  else if (kind === "reciprocal") rule = C.reciprocal(rng.choice(NZ6), rng.nextInt(-6, 6), rng.nextInt(-4, 4));
  else if (kind === "linear") rule = C.linear(rng.choice(NZ5), rng.choice(NZ6));
  else rule = C.quadratic(rng.choice([1, -1, 2]), rng.nextInt(-6, 6), rng.choice(NZ6));
  return { task: "domain_of_function", name, rule };
}

function drawRange(rng: Mulberry32): Params | null {
  const kind = rng.choice(["quadratic", "quadratic", "sqrt", "reciprocal", "linear_restricted"]);
  const name = pickName(rng);
  if (kind === "quadratic") {
    const rule = C.quadratic(rng.choice([1, 1, 2, -1, -2, 3, -3]), rng.nextInt(-6, 6), rng.nextInt(-6, 6));
    return { task: "range_of_function", name, rule };
  }
  if (kind === "sqrt") {
    const rule = C.sqrtRule(rng.choice(NZ5), rng.nextInt(-6, 6), rng.nextInt(-6, 6));
    return { task: "range_of_function", name, rule };
  }
  if (kind === "reciprocal") {
    const rule = C.reciprocal(rng.choice(NZ6), rng.nextInt(-6, 6), rng.nextInt(-6, 6));
    return { task: "range_of_function", name, rule };
  }
  const rule = C.linear(rng.choice(NZ5), rng.nextInt(-6, 6));
  const p = rng.nextInt(-5, 4);
  const q = rng.nextInt(p + 1, 5);
  return { task: "range_of_function", name, rule, restricted: { p: F(p), q: F(q) } };
}

function drawPolyRule(rng: Mulberry32, kind: string): Rule {
  if (kind === "linear") return C.linear(rng.choice(NZ5), rng.nextInt(-6, 6));
  return C.quadratic(rng.choice([1, 1, -1, 2]), rng.nextInt(-3, 3), rng.nextInt(-6, 6));
}

function drawCompositeValue(rng: Mulberry32): Params | null {
  const fk = rng.choice(["linear", "quadratic"]);
  const gk = rng.choice(["linear", "quadratic"]);
  const f = drawPolyRule(rng, fk);
  const g = drawPolyRule(rng, gk);
  const order = rng.choice(["fg", "gf"]);
  const p = F(rng.nextInt(-5, 5));
  return { task: "composite_value", f, g, order, p };
}

function drawCompositeExpression(rng: Mulberry32): Params | null {
  const quadSlot = rng.choice(["none", "outer", "inner"]);
  const order = rng.choice(["fg", "gf"]);
  const outerKind = quadSlot === "outer" ? "quadratic" : "linear";
  const innerKind = quadSlot === "inner" ? "quadratic" : "linear";
  const [fk, gk] = order === "fg" ? [outerKind, innerKind] : [innerKind, outerKind];
  const f = drawPolyRule(rng, fk);
  const g = drawPolyRule(rng, gk);
  return { task: "composite_expression", f, g, order };
}

function drawFunctionFromComposite(rng: Mulberry32): Params | null {
  const A = F(rng.choice(NZ5));
  const B = F(rng.nextInt(-6, 6));
  const m = F(rng.choice([1, 1, 2, -1]));
  const c = F(rng.choice(NZ6));
  return { task: "function_from_composite", A, B, m, c };
}

function drawInverseValue(rng: Mulberry32): Params | null {
  const form = rng.choice(["inverse_at", "solve_inverse_equation"]);
  const name = pickName(rng);
  const a = F(rng.choice(NZ5));
  const b = F(rng.nextInt(-6, 6));
  const x0 = F(rng.nextInt(-6, 6));
  if (form === "inverse_at") {
    const mode = rng.nextInt(0, 2);
    const k = mode === 0 ? F(rng.nextInt(-9, 9)) : a.mul(x0).add(b);
    return { task: "inverse_value", name, a, b, form, k };
  }
  return { task: "inverse_value", name, a, b, form, x0 };
}

function drawInverseExpression(rng: Mulberry32): Params | null {
  const name = pickName(rng);
  const frac = rng.nextInt(0, 3) === 0;
  const a = frac ? rng.choice([new Rational(1, 2), new Rational(-1, 2), new Rational(1, 3)]) : F(rng.choice(NZ5));
  const b = F(rng.nextInt(-6, 6));
  return { task: "inverse_expression", name, a, b };
}

function drawOneToOne(rng: Mulberry32): Params | null {
  const name = pickName(rng);
  const rule = C.quadratic(rng.choice([1, 1, -1, 2, -2, 3]), rng.choice(NZ6), rng.nextInt(-6, 6));
  const side = rng.choice(["ge", "le"]);
  return { task: "one_to_one_restriction", name, rule, side };
}

const DRAW: Record<string, (rng: Mulberry32) => Params | null> = {
  identify_function: drawIdentify, evaluate_function: drawEvaluate, solve_for_input: drawSolve,
  domain_of_function: drawDomain, range_of_function: drawRange, composite_value: drawCompositeValue,
  composite_expression: drawCompositeExpression, function_from_composite: drawFunctionFromComposite,
  inverse_value: drawInverseValue, inverse_expression: drawInverseExpression,
  one_to_one_restriction: drawOneToOne,
};

// --------------------------------------------------------------------------- //
// Params encoding (public JSON <-> internal exact)
// --------------------------------------------------------------------------- //

const RAT_KEYS = ["p", "target", "x0", "A", "B", "m", "c", "a", "b", "k"];

function publicParams(params: Params): Json {
  const out: Json = {};
  for (const [key, val] of Object.entries(params)) {
    if (key === "rule" || key === "f" || key === "g") out[key] = C.ruleToJson(val as Rule);
    else if (key === "restricted") out[key] = { p: ratJson(val.p), q: ratJson(val.q) };
    else if (RAT_KEYS.includes(key)) out[key] = ratJson(val as Rational);
    else out[key] = val;
  }
  return out;
}

function internalParams(pub: Json): Params {
  const out: Params = {};
  for (const [key, val] of Object.entries(pub as Record<string, Json>)) {
    if (key === "rule" || key === "f" || key === "g") out[key] = C.ruleFromJson(val as RuleJson);
    else if (key === "restricted") out[key] = { p: ratFromJson(val.p), q: ratFromJson(val.q) };
    else if (RAT_KEYS.includes(key)) out[key] = ratFromJson(val as RatJson);
    else out[key] = val;
  }
  return out;
}

function outerInner(params: Params): [Rule, Rule, string, string] {
  if (params.order === "fg") return [params.f as Rule, params.g as Rule, "f", "g"];
  return [params.g as Rule, params.f as Rule, "g", "f"];
}

// --------------------------------------------------------------------------- //
// Guards
// --------------------------------------------------------------------------- //

const withinCaps = (x: Rational): boolean => Math.abs(x.num) <= MAX_NUM && x.den <= MAX_DEN;

const pairsDisplay = (pairs: number[][]): string => "{" + pairs.map(([x, y]) => `(${x}, ${y})`).join(", ") + "}";

function acceptable(task: string, params: Params): boolean {
  if (task === "identify_function") {
    const displays = [pairsDisplay(params.nonFunction), ...(params.functions as Json[]).map((f) => pairsDisplay(f.pairs))];
    return new Set(displays).size === 4;
  }
  if (task === "evaluate_function") {
    const v = C.evalRule(params.rule as Rule, params.p as Rational);
    return v !== null && withinCaps(v);
  }
  if (task === "solve_for_input") {
    const rule = params.rule as Rule;
    return withinCaps(params.target) && withinCaps(params.x0) && (rule.v === undefined || !(params.target as Rational).equals(rule.v));
  }
  if (task === "composite_value") {
    const [outer, inner] = outerInner(params);
    return withinCaps(C.rulePoly(outer).eval(C.rulePoly(inner).eval(params.p as Rational)));
  }
  if (task === "composite_expression") {
    const [outer, inner] = outerInner(params);
    return C.rulePoly(outer).compose(C.rulePoly(inner)).degree() <= 2;
  }
  return true;
}

// --------------------------------------------------------------------------- //
// Answers
// --------------------------------------------------------------------------- //

type Value = Rational | Poly | Interval | ReciprocalOf;

/** The canonical answer value (Rational | Poly | descriptor); identify_function is resolved at assembly. */
function solve(task: string, params: Params): Value {
  if (task === "evaluate_function") return C.evalRule(params.rule as Rule, params.p as Rational)!;
  if (task === "solve_for_input") {
    const r = params.rule as Rule, k = params.target as Rational;
    if (r.kind === "linear") return k.sub(r.b!).div(r.a!);
    if (r.kind === "reciprocal") return r.h!.add(r.k!.div(k.sub(r.v!)));
    const t = k.sub(r.v!);
    return t.mul(t).sub(r.b!).div(r.a!);
  }
  if (task === "domain_of_function") return C.domainOf(params.rule as Rule);
  if (task === "range_of_function") return C.rangeOf(params.rule as Rule, params.restricted ?? null);
  if (task === "composite_value") {
    const [outer, inner] = outerInner(params);
    return C.evalRule(outer, C.evalRule(inner, params.p as Rational)!)!;
  }
  if (task === "composite_expression") {
    const [outer, inner] = outerInner(params);
    return C.rulePoly(outer).compose(C.rulePoly(inner));
  }
  if (task === "function_from_composite") return Poly.linear(params.A as Rational, params.B as Rational);
  if (task === "inverse_value") {
    const a = params.a as Rational, b = params.b as Rational;
    if (params.form === "inverse_at") return (params.k as Rational).sub(b).div(a);
    return a.mul(params.x0 as Rational).add(b);
  }
  if (task === "inverse_expression") {
    const a = params.a as Rational, b = params.b as Rational;
    return Poly.linear(ONE.div(a), b.neg().div(a));
  }
  if (task === "one_to_one_restriction") return C.vertexX(params.rule as Rule);
  throw new Error(task);
}

function terminates(den: number): boolean {
  while (den % 2 === 0) den /= 2;
  while (den % 5 === 0) den /= 5;
  return den === 1;
}

const isReciprocalOf = (v: Value): v is ReciprocalOf => !(v instanceof Rational) && !(v instanceof Poly) && (v as ReciprocalOf).kind === "reciprocal-of";

function valueDisplay(v: Value): string {
  if (v instanceof Rational) return ratDisplay(v);
  if (v instanceof Poly) return v.display();
  if (isReciprocalOf(v)) return `1/(${v.poly.display()})`;
  return intervalDisplay(intervalToJson(v as Interval));
}

function valueJson(v: Value): Json {
  if (v instanceof Rational) return ratJson(v);
  if (v instanceof Poly) return v.toJson();
  if (isReciprocalOf(v)) return { kind: "reciprocal-of", coefficients: v.poly.toJson().coefficients };
  return intervalToJson(v as Interval);
}

function encodeAnswer(task: string, value: Value): Json {
  const fam = ANSWER_FAMILY[task]!;
  if (fam === "number") {
    const q = value as Rational;
    return { type: q.den === 1 ? "integer" : "exact-rational", canonical: ratJson(q), display: ratDisplay(q),
      accepts: { fraction: true, decimal: terminates(q.den), mixed: false } };
  }
  if (fam === "expression") {
    const p = value as Poly;
    return { type: "algebraic-expression", canonical: p.toJson(), display: p.display() };
  }
  const j = intervalToJson(value as Interval);
  return { type: "interval", canonical: j, display: intervalDisplay(j) };
}

// --------------------------------------------------------------------------- //
// Misconception context + MC distractors
// --------------------------------------------------------------------------- //

function ctxFor(task: string, params: Params): Ctx {
  const ctx: Record<string, unknown> = { task };
  for (const [k, v] of Object.entries(params)) if (k !== "task") ctx[k] = v;
  if (task === "composite_value" || task === "composite_expression") {
    const [outer, inner, on, inn] = outerInner(params);
    Object.assign(ctx, { outer, inner, outer_name: on, inner_name: inn, p: params.p });
  }
  if (task === "function_from_composite") {
    ctx.comp_p = (params.A as Rational).mul(params.m as Rational);
    ctx.comp_q = (params.A as Rational).mul(params.c as Rational).add(params.B as Rational);
  }
  if (task === "inverse_value" && !("x0" in ctx)) ctx.x0 = null;
  return ctx as unknown as Ctx;
}

interface Distractor { value: Value; misconceptionId: string; rationale: string }

/** Three distinct misconception-backed distractors. The eligibility list is rotated by ONE seeded draw so
 *  that every eligible pathway is exercised across items and distractor sets vary between items. */
function mcDistractors(task: string, params: Params, rng: Mulberry32): Distractor[] | null {
  const answerKey = valueDisplay(solve(task, params));
  const ctx = ctxFor(task, params);
  const seen = new Set<string>([answerKey]);
  const chosen: Distractor[] = [];
  let rules = FM.rulesFor(task);
  const offset = rng.nextInt(0, rules.length - 1);
  rules = [...rules.slice(offset), ...rules.slice(0, offset)];
  for (const mid of rules) {
    const w: WrongValue | null = FM.MISCONCEPTIONS[mid]!.wrong(ctx);
    if (w === null) continue;
    if (w instanceof Rational && !withinCaps(w)) continue;
    const key = valueDisplay(w);
    if (seen.has(key)) continue;
    seen.add(key);
    chosen.push({ value: w, misconceptionId: mid, rationale: FM.MISCONCEPTIONS[mid]!.observableError });
    if (chosen.length === 3) break;
  }
  return chosen.length === 3 ? chosen : null;
}

// --------------------------------------------------------------------------- //
// Prompts + spoken text
// --------------------------------------------------------------------------- //

function definedBy(name: string, rule: Rule, suffix = ""): Json[] {
  return [{ kind: "text", text: `The function ${name} is defined by` },
    { kind: "math", latex: `${name}(x) = ${C.ruleLatex(rule)}${suffix}` }];
}

function twoFunctions(f: Rule, g: Rule): Json[] {
  return [{ kind: "text", text: "The functions f and g are defined by" },
    { kind: "math", latex: `f(x) = ${C.ruleLatex(f)}, \\qquad g(x) = ${C.ruleLatex(g)}` }];
}

function compositeOfParams(params: Params): Poly {
  return Poly.linear((params.A as Rational).mul(params.m as Rational), (params.A as Rational).mul(params.c as Rational).add(params.B as Rational));
}

function prompt(task: string, params: Params): Json {
  const n = (params.name as string | undefined) ?? "f";
  if (task === "identify_function") {
    return { instruction: "Identify",
      blocks: [{ kind: "text", text: "Exactly one of the following relations is not a function. Which one?" }] };
  }
  if (task === "evaluate_function") {
    return { instruction: "Evaluate", blocks: [...definedBy(n, params.rule),
      { kind: "text", text: `Find the value of ${n}(${ratDisplay(params.p)}).` }] };
  }
  if (task === "solve_for_input") {
    return { instruction: "Solve", blocks: [...definedBy(n, params.rule),
      { kind: "text", text: `Find the value of x for which ${n}(x) = ${ratDisplay(params.target)}.` }] };
  }
  if (task === "domain_of_function") {
    return { instruction: "State the domain", blocks: [...definedBy(n, params.rule),
      { kind: "text", text: `State the largest possible domain of ${n}.` }] };
  }
  if (task === "range_of_function") {
    let suffix = "";
    if ("restricted" in params) {
      suffix = `, \\quad ${C.latexRat(params.restricted.p)} \\leq x \\leq ${C.latexRat(params.restricted.q)}`;
    }
    return { instruction: "State the range", blocks: [...definedBy(n, params.rule, suffix),
      { kind: "text", text: `State the range of ${n}.` }] };
  }
  if (task === "composite_value") {
    const [, , on, inn] = outerInner(params);
    return { instruction: "Evaluate", blocks: [...twoFunctions(params.f, params.g),
      { kind: "text", text: "Find the value of" },
      { kind: "math", latex: `(${on} \\circ ${inn})(${C.latexRat(params.p)})` }] };
  }
  if (task === "composite_expression") {
    const [, , on, inn] = outerInner(params);
    return { instruction: "Find the composite", blocks: [...twoFunctions(params.f, params.g),
      { kind: "text", text: "Find an expression for" },
      { kind: "math", latex: `(${on} \\circ ${inn})(x)` },
      { kind: "text", text: "Expand and simplify your answer." }] };
  }
  if (task === "function_from_composite") {
    const g = C.linear(params.m, params.c);
    const comp = compositeOfParams(params);
    return { instruction: "Find the outer function",
      blocks: [{ kind: "text", text: "The functions f and g are defined by" },
        { kind: "math", latex: `g(x) = ${C.ruleLatex(g)}, \\qquad (f \\circ g)(x) = ${C.latexPoly(comp)}` },
        { kind: "text", text: "Find an expression for f(x)." }] };
  }
  if (task === "inverse_value") {
    const rule = C.linear(params.a, params.b);
    if (params.form === "inverse_at") {
      return { instruction: "Evaluate the inverse", blocks: [...definedBy(n, rule),
        { kind: "text", text: "Find the value of" },
        { kind: "math", latex: `${n}^{-1}(${C.latexRat(params.k)})` }] };
    }
    return { instruction: "Solve", blocks: [...definedBy(n, rule),
      { kind: "text", text: "Find the value of k for which" },
      { kind: "math", latex: `${n}^{-1}(k) = ${C.latexRat(params.x0)}` }] };
  }
  if (task === "inverse_expression") {
    const rule = C.linear(params.a, params.b);
    return { instruction: "Find the inverse", blocks: [...definedBy(n, rule),
      { kind: "text", text: "Find an expression for" },
      { kind: "math", latex: `${n}^{-1}(x)` }] };
  }
  const side = params.side as string;
  const word = side === "ge" ? "least" : "greatest";
  const cmpLatex = side === "ge" ? "\\geq" : "\\leq";
  return { instruction: "Find the restriction",
    blocks: [...definedBy(n, params.rule, `, \\quad x ${cmpLatex} k`),
      { kind: "text", text: `The domain of ${n} is restricted so that the inverse function ${n}^-1 exists. `
        + `Find the ${word} possible value of k.` }] };
}

function spoken(task: string, params: Params, options: Json[] | null = null): string {
  const n = (params.name as string | undefined) ?? "f";
  if (task === "identify_function") {
    const parts: string[] = [];
    for (const o of options ?? []) {
      const pairs = (o.value as number[][]).map(([x, y]) => `(${x}, ${y})`).join("; ");
      parts.push(`Option ${o.label}: the ordered pairs ${pairs}.`);
    }
    return "Exactly one of the following relations is not a function. Which one? " + parts.join(" ");
  }
  if (["evaluate_function", "solve_for_input", "domain_of_function", "range_of_function", "one_to_one_restriction"].includes(task)) {
    const r = params.rule as Rule;
    let head = `The function ${n} is defined by ${n}(x) = ${C.ruleText(r)}`;
    if (task === "evaluate_function") return `${head}. Find the value of ${n}(${ratDisplay(params.p)}).`;
    if (task === "solve_for_input") return `${head}. Find the value of x for which ${n}(x) = ${ratDisplay(params.target)}.`;
    if (task === "domain_of_function") return `${head}. State the largest possible domain of ${n}.`;
    if (task === "range_of_function") {
      if ("restricted" in params) head += `, for ${ratDisplay(params.restricted.p)} <= x <= ${ratDisplay(params.restricted.q)}`;
      return `${head}. State the range of ${n}.`;
    }
    const word = params.side === "ge" ? "least" : "greatest";
    const cmp = params.side === "ge" ? ">=" : "<=";
    return `${head}, for x ${cmp} k. The domain of ${n} is restricted so that the inverse function ${n}^-1 exists. `
      + `Find the ${word} possible value of k.`;
  }
  if (task === "composite_value" || task === "composite_expression") {
    const [, , on, inn] = outerInner(params);
    const head = `The functions f and g are defined by f(x) = ${C.ruleText(params.f)} and g(x) = ${C.ruleText(params.g)}.`;
    if (task === "composite_value") {
      return `${head} Find the value of (${on} o ${inn})(${ratDisplay(params.p)}), that is ${on} of ${inn} of ${ratDisplay(params.p)}.`;
    }
    return `${head} Find an expression for (${on} o ${inn})(x), that is ${on} of ${inn} of x. Expand and simplify your answer.`;
  }
  if (task === "function_from_composite") {
    const g = C.linear(params.m, params.c);
    const comp = compositeOfParams(params);
    return `The functions f and g are defined by g(x) = ${C.ruleText(g)} and (f o g)(x) = ${comp.display()}. `
      + "Find an expression for f(x).";
  }
  const rule = C.linear(params.a, params.b);
  const head = `The function ${n} is defined by ${n}(x) = ${C.ruleText(rule)}.`;
  if (task === "inverse_value") {
    if (params.form === "inverse_at") return `${head} Find the value of ${n} inverse of ${ratDisplay(params.k)}.`;
    return `${head} Find the value of k for which ${n} inverse of k equals ${ratDisplay(params.x0)}.`;
  }
  return `${head} Find an expression for ${n} inverse of x.`;
}

// --------------------------------------------------------------------------- //
// Worked solutions
// --------------------------------------------------------------------------- //

function sumText(terms: Rational[]): string {
  let out = "";
  terms.forEach((t, i) => {
    if (i === 0) out = ratDisplay(t);
    else out += (C.isNeg(t) ? " - " : " + ") + ratDisplay(t.abs());
  });
  return out;
}

const bracket = (x: Rational): string => (C.isNeg(x) ? `(${ratDisplay(x)})` : ratDisplay(x));

/** a·operand with ±1 implicit and the operand bracketed after a coefficient: 5, -5, 2(5), 2(-3), (1/2)(5). */
function coefTimes(a: Rational, operand: string): string {
  if (eqn(a, 1)) return operand;
  if (eqn(a, -1)) return "-" + operand;
  const wrapped = operand.startsWith("(") ? operand : `(${operand})`;
  return (a.den !== 1 ? `(${ratDisplay(a)})` : ratDisplay(a)) + wrapped;
}

function substituted(rule: Rule, p: Rational): string {
  const bp = bracket(p);
  if (rule.kind === "linear") return coefTimes(rule.a!, bp) + C.shiftText(rule.b!);
  if (rule.kind === "quadratic") {
    let s = coefTimes(rule.a!, `${bp}^2`);
    if (!rule.b!.isZero()) s += (C.isNeg(rule.b!) ? " - " : " + ") + coefTimes(rule.b!.abs(), bp);
    return s + C.shiftText(rule.c!);
  }
  if (rule.kind === "reciprocal") {
    const h = rule.h!;
    const den = C.isPos(h) ? `(${bp} - ${ratDisplay(h)})` : C.isNeg(h) ? `(${bp} + ${ratDisplay(h.neg())})` : bp;
    return `${ratDisplay(rule.k!)}/${den}` + C.shiftText(rule.v!);
  }
  return "sqrt(" + coefTimes(rule.a!, bp) + C.shiftText(rule.b!) + ")" + C.shiftText(rule.v!);
}

function substitutedExpr(outer: Rule, inner: Rule): string {
  const innerTxt = C.ruleText(inner);
  if (outer.kind === "linear") {
    const a = outer.a!;
    const head = eqn(a, 1) ? `(${innerTxt})` : eqn(a, -1) ? `-(${innerTxt})` : `${ratDisplay(a)}(${innerTxt})`;
    return head + C.shiftText(outer.b!);
  }
  const a = outer.a!, b = outer.b!, c = outer.c!;
  let head = eqn(a, 1) ? `(${innerTxt})^2` : eqn(a, -1) ? `-(${innerTxt})^2` : `${ratDisplay(a)}(${innerTxt})^2`;
  if (!b.isZero()) {
    const mag = b.abs();
    head += (C.isNeg(b) ? " - " : " + ") + (eqn(mag, 1) ? `(${innerTxt})` : `${ratDisplay(mag)}(${innerTxt})`);
  }
  return head + C.shiftText(c);
}

interface StepOpts { intermediate?: string; rule?: string; explanation?: string | null; marks?: number; depends?: boolean }

class Steps {
  steps: Json[] = [];
  prev: number | null = null;

  add(transformation: string, o: StepOpts = {}): void {
    const n = this.steps.length + 1;
    const st: Json = { number: n, transformation };
    if (o.rule !== undefined && o.rule !== null) st.ruleOrTheorem = o.rule;
    if (o.intermediate !== undefined && o.intermediate !== null) st.intermediateResult = o.intermediate;
    if (o.explanation !== undefined && o.explanation !== null) st.explanation = o.explanation;
    if ((o.depends ?? true) && this.prev !== null) st.dependsOn = [this.prev];
    if (o.marks !== undefined && o.marks !== null) st.marks = o.marks;
    this.steps.push(st);
    this.prev = n;
  }
}

const addSub = (v: Rational): string => (C.isPos(v) ? "Subtract" : "Add");
const fromTo = (v: Rational): string => (C.isPos(v) ? "from" : "to");

function solution(task: string, params: Params, answerDisplay: string, options: Json[] | null = null): Json {
  const S = new Steps();
  const n = (params.name as string | undefined) ?? "f";
  if (task === "identify_function") {
    S.add("List the inputs of each relation", { explanation: "A relation is a function when no input is paired with two different outputs." });
    const pairs = params.nonFunction as number[][];
    const seen = new Map<number, number>();
    let rep: [number, number, number] | null = null;
    for (const [x, y] of pairs as [number, number][]) {
      if (seen.has(x) && seen.get(x) !== y) { rep = [x, seen.get(x)!, y]; break; }
      if (!seen.has(x)) seen.set(x, y);
    }
    const label = (options ?? []).find((o) => o.correct)!.label as string;
    S.add("Find the relation with a repeated input and two different outputs",
      { intermediate: `Relation ${label}: the input ${rep![0]} is paired with both ${rep![1]} and ${rep![2]}` });
    S.add("State the relation that is not a function", { intermediate: label, marks: 1 });
    return { steps: S.steps };
  }
  if (task === "evaluate_function") {
    const r = params.rule as Rule, p = params.p as Rational;
    S.add(`Substitute x = ${ratDisplay(p)} into the rule`, { intermediate: `${n}(${ratDisplay(p)}) = ${substituted(r, p)}`,
      explanation: "Replace every x by the input, keeping a negative input in brackets." });
    if (r.kind === "linear") {
      const terms = r.b!.isZero() ? [r.a!.mul(p)] : [r.a!.mul(p), r.b!];
      S.add("Multiply, then add the constant", { intermediate: `= ${sumText(terms)}` });
    } else if (r.kind === "quadratic") {
      S.add("Square first, then multiply and add", { intermediate: `= ${sumText([r.a!.mul(p).mul(p), r.b!.mul(p), r.c!])}` });
    } else if (r.kind === "reciprocal") {
      S.add("Evaluate the denominator, then divide", { intermediate: `= ${ratDisplay(r.k!)}/${bracket(p.sub(r.h!))}` + C.shiftText(r.v!) });
    } else {
      const rad = C.radicand(r, p);
      S.add("Evaluate the radicand, then take the square root", { intermediate: `= sqrt(${ratDisplay(rad)})` + C.shiftText(r.v!)
        + ` = ${ratDisplay(C.sqrtExact(rad)!)}` + C.shiftText(r.v!) });
    }
    S.add("State the value", { intermediate: `${n}(${ratDisplay(p)}) = ${answerDisplay}`, marks: 1 });
    return { steps: S.steps };
  }
  if (task === "solve_for_input") {
    const r = params.rule as Rule, k = params.target as Rational, x0 = params.x0 as Rational;
    S.add("Set up the equation", { intermediate: `${C.ruleText(r)} = ${ratDisplay(k)}`, explanation: `${n}(x) = ${ratDisplay(k)} means the rule equals ${ratDisplay(k)}.` });
    if (r.kind === "linear") {
      if (!r.b!.isZero()) {
        S.add(`${addSub(r.b!)} ${ratDisplay(r.b!.abs())} ${fromTo(r.b!)} both sides`,
          { intermediate: `${C.ruleText(C.linear(r.a!, 0))} = ${ratDisplay(k.sub(r.b!))}` });
      }
      if (!eqn(r.a!, 1)) S.add(`Divide both sides by ${ratDisplay(r.a!)}`, { intermediate: `x = ${ratDisplay(x0)}` });
    } else if (r.kind === "reciprocal") {
      const den = C.denominatorText(r.h!);
      if (!r.v!.isZero()) {
        S.add(`${addSub(r.v!)} ${ratDisplay(r.v!.abs())} ${fromTo(r.v!)} both sides`,
          { intermediate: `${ratDisplay(r.k!)}/(${den}) = ${ratDisplay(k.sub(r.v!))}` });
      }
      S.add("Multiply both sides by the denominator and divide by the value",
        { intermediate: `${den} = ${ratDisplay(r.k!.div(k.sub(r.v!)))}`, explanation: "The denominator equals the numerator divided by the value of the fraction." });
      if (!r.h!.isZero()) {
        S.add(`${C.isPos(r.h!) ? "Add" : "Subtract"} ${ratDisplay(r.h!.abs())} ${C.isPos(r.h!) ? "to" : "from"} both sides`, { intermediate: `x = ${ratDisplay(x0)}` });
      }
    } else {
      const t = k.sub(r.v!);
      if (!r.v!.isZero()) {
        S.add(`${addSub(r.v!)} ${ratDisplay(r.v!.abs())} ${fromTo(r.v!)} both sides to isolate the root`,
          { intermediate: `sqrt(${C.radicandText(r)}) = ${ratDisplay(t)}` });
      }
      S.add("Square both sides", { intermediate: `${C.radicandText(r)} = ${ratDisplay(t.mul(t))}`, explanation: "Squaring undoes the square root once it is isolated." });
      S.add("Solve the linear equation", { intermediate: `x = ${ratDisplay(x0)}` });
    }
    S.add("State the solution", { intermediate: `x = ${answerDisplay}`, marks: 1 });
    S.add("Verify by substitution", { intermediate: `${n}(${ratDisplay(x0)}) = ${ratDisplay(k)}`, explanation: "The rule returns the required output, confirming the solution." });
    return { steps: S.steps };
  }
  if (task === "domain_of_function") {
    const r = params.rule as Rule;
    if (r.kind === "sqrt") {
      S.add("Identify the restriction", { intermediate: `${C.radicandText(r)} >= 0`, rule: "A square root is defined only for a non-negative radicand." });
      const expl = C.isNeg(r.a!) ? "Dividing both sides by a negative number reverses the inequality." : null;
      S.add("Solve the inequality", { intermediate: answerDisplay, explanation: expl });
    } else if (r.kind === "reciprocal") {
      S.add("Identify the restriction", { intermediate: `${C.denominatorText(r.h!)} != 0`, rule: "A fraction is undefined when its denominator is zero." });
      S.add("Solve for the excluded input", { intermediate: answerDisplay });
    } else {
      S.add("Identify the restriction", { intermediate: "none", rule: "A polynomial can be evaluated at every real number." });
    }
    S.add("State the domain", { intermediate: answerDisplay, marks: 1 });
    return { steps: S.steps };
  }
  if (task === "range_of_function") {
    const r = params.rule as Rule;
    if (r.kind === "quadratic") {
      const hx = C.vertexX(r), hy = C.vertexY(r);
      S.add("Find the axis of symmetry", { intermediate: `x = -(${ratDisplay(r.b!)})/(2(${ratDisplay(r.a!)})) = ${ratDisplay(hx)}`, rule: "x = -b/(2a)" });
      S.add("Find the value at the vertex", { intermediate: `${n}(${ratDisplay(hx)}) = ${ratDisplay(hy)}` });
      S.add("Determine the direction of opening",
        { intermediate: `a = ${ratDisplay(r.a!)} ${C.isPos(r.a!) ? "> 0, so the vertex is a minimum" : "< 0, so the vertex is a maximum"}` });
    } else if (r.kind === "sqrt") {
      S.add("Start from the base range", { intermediate: `sqrt(${C.radicandText(r)}) >= 0`, rule: "A square root is never negative and equals 0 at the domain endpoint." });
      S.add("Apply the vertical shift", { intermediate: `${n}(x) >= ${ratDisplay(r.v!)}` });
    } else if (r.kind === "reciprocal") {
      S.add("Start from the base range", { intermediate: `${ratDisplay(r.k!)}/(${C.denominatorText(r.h!)}) != 0`,
        rule: "A fraction with a non-zero constant numerator is never zero but takes every other value." });
      S.add("Apply the vertical shift", { intermediate: `${n}(x) != ${ratDisplay(r.v!)}` });
    } else {
      const p = params.restricted.p as Rational, q = params.restricted.q as Rational;
      const fp = C.evalRule(r, p)!, fq = C.evalRule(r, q)!;
      S.add("Evaluate at the endpoints of the domain", { intermediate: `${n}(${ratDisplay(p)}) = ${ratDisplay(fp)}, ${n}(${ratDisplay(q)}) = ${ratDisplay(fq)}`,
        rule: "A linear function is monotonic, so its extreme values occur at the endpoints." });
      const lo = C.lt(fp, fq) ? fp : fq, hi = C.lt(fp, fq) ? fq : fp;
      S.add("Order the images", { intermediate: `${ratDisplay(lo)} <= y <= ${ratDisplay(hi)}` });
    }
    S.add("State the range", { intermediate: answerDisplay, marks: 1 });
    return { steps: S.steps };
  }
  if (task === "composite_value") {
    const [, inner, on, inn] = outerInner(params);
    const p = params.p as Rational;
    const gv = C.evalRule(inner, p)!;
    S.add(`Evaluate the inner function ${inn} at ${ratDisplay(p)}`, { intermediate: `${inn}(${ratDisplay(p)}) = ${ratDisplay(gv)}`,
      explanation: `(${on} o ${inn})(x) = ${on}(${inn}(x)): the inner function is applied first.` });
    S.add(`Evaluate the outer function ${on} at ${ratDisplay(gv)}`, { intermediate: `${on}(${ratDisplay(gv)}) = ${answerDisplay}` });
    S.add("State the value", { intermediate: `(${on} o ${inn})(${ratDisplay(p)}) = ${answerDisplay}`, marks: 1 });
    return { steps: S.steps };
  }
  if (task === "composite_expression") {
    const [outer, inner, on, inn] = outerInner(params);
    S.add(`Substitute ${inn}(x) into ${on}`, { intermediate: `${on}(${inn}(x)) = ${substitutedExpr(outer, inner)}`,
      explanation: `Replace every x in ${on}(x) by the whole expression ${inn}(x).` });
    S.add("Expand and collect like terms", { intermediate: `= ${answerDisplay}` });
    S.add("State the composite", { intermediate: `(${on} o ${inn})(x) = ${answerDisplay}`, marks: 1 });
    return { steps: S.steps };
  }
  if (task === "function_from_composite") {
    const m = params.m as Rational, c = params.c as Rational, A = params.A as Rational, B = params.B as Rational;
    const comp = compositeOfParams(params);
    const g = C.linear(m, c);
    S.add("Write f(g(x)) equal to the given composite", { intermediate: `f(${C.ruleText(g)}) = ${comp.display()}` });
    S.add("Let u = g(x) and express x in terms of u", { intermediate: `x = ${Poly.linear(ONE.div(m), c.neg().div(m)).display("u")}`,
      explanation: "Undo the inner function to change the variable." });
    S.add("Substitute and simplify", { intermediate: `f(u) = ${Poly.linear(A, B).display("u")}` });
    S.add("State the outer function", { intermediate: `f(x) = ${answerDisplay}`, marks: 1 });
    return { steps: S.steps };
  }
  if (task === "inverse_value") {
    const a = params.a as Rational, b = params.b as Rational;
    const rule = C.linear(a, b);
    if (params.form === "inverse_at") {
      const k = params.k as Rational;
      S.add(`Let ${n}^-1(${ratDisplay(k)}) = x, so ${n}(x) = ${ratDisplay(k)}`, { intermediate: `${C.ruleText(rule)} = ${ratDisplay(k)}`,
        explanation: "The inverse function reverses the input and output." });
      S.add("Solve for x", { intermediate: `x = ${answerDisplay}` });
      S.add("State the value", { intermediate: `${n}^-1(${ratDisplay(k)}) = ${answerDisplay}`, marks: 1 });
    } else {
      const x0 = params.x0 as Rational;
      S.add(`Rewrite ${n}^-1(k) = ${ratDisplay(x0)} as k = ${n}(${ratDisplay(x0)})`, { explanation: "The inverse function reverses the input and output." });
      S.add(`Evaluate ${n} at ${ratDisplay(x0)}`, { intermediate: `k = ${substituted(rule, x0)} = ${answerDisplay}` });
      S.add("State the value", { intermediate: `k = ${answerDisplay}`, marks: 1 });
    }
    return { steps: S.steps };
  }
  if (task === "inverse_expression") {
    const a = params.a as Rational, b = params.b as Rational;
    const rule = C.linear(a, b);
    S.add(`Write y = ${n}(x)`, { intermediate: `y = ${C.ruleText(rule)}` });
    S.add("Swap x and y", { intermediate: `x = ${Poly.linear(a, b).display("y")}`, explanation: "The inverse reverses the roles of input and output." });
    S.add("Solve for y", { intermediate: `y = ${answerDisplay}`, explanation: "Undo the operations in reverse order." });
    S.add("State the inverse function", { intermediate: `${n}^-1(x) = ${answerDisplay}`, marks: 1 });
    S.add("Verify", { intermediate: `${n}(${answerDisplay}) = x`, explanation: "Composing the function with its inverse returns the input." });
    return { steps: S.steps };
  }
  const r = params.rule as Rule;
  const hx = C.vertexX(r);
  S.add("Find the axis of symmetry", { intermediate: `x = -(${ratDisplay(r.b!)})/(2(${ratDisplay(r.a!)})) = ${ratDisplay(hx)}`, rule: "x = -b/(2a)" });
  S.add("Restrict the domain at the vertex",
    { explanation: `${n} takes each value twice on either side of the axis of symmetry, so it is one-to-one only on one side of x = ${ratDisplay(hx)}.` });
  S.add("State the value of k", { intermediate: `k = ${answerDisplay}`, marks: 1 });
  return { steps: S.steps };
}

// --------------------------------------------------------------------------- //
// Difficulty
// --------------------------------------------------------------------------- //

const KIND_TIER: Record<string, number> = { linear: 0, quadratic: 1, reciprocal: 2, sqrt: 2 };

function band(task: string, params: Params): number {
  const [, hi] = TASK_BANDS[task as keyof typeof TASK_BANDS]!;
  if (task === "identify_function") return params.negativeInputs || params.separatedRepeat ? 2 : 1;
  if (task === "evaluate_function") {
    const r = params.rule as Rule, p = params.p as Rational;
    const v = C.evalRule(r, p)!;
    const tier = KIND_TIER[r.kind]! + (C.isNeg(p) || v.den !== 1 ? 1 : 0);
    return Math.min(1 + Math.min(tier, 2), hi);
  }
  if (task === "solve_for_input") {
    const r = params.rule as Rule;
    return r.kind === "linear" && (params.x0 as Rational).den === 1 ? 2 : 3;
  }
  if (task === "domain_of_function") {
    const r = params.rule as Rule;
    if (C.isPolynomialRule(r)) return 2;
    if (r.kind === "reciprocal") return r.h!.isZero() ? 2 : 3;
    const endpoint = r.b!.neg().div(r.a!);
    return C.isPos(r.a!) && endpoint.den === 1 ? 3 : 4;
  }
  if (task === "range_of_function") {
    const r = params.rule as Rule;
    if (r.kind === "linear") return 3;
    if (r.kind === "sqrt") return r.v!.isZero() ? 3 : 4;
    if (r.kind === "reciprocal") return 4;
    return C.isPos(r.a!) && C.vertexY(r).den === 1 ? 4 : 5;
  }
  if (task === "composite_value") {
    const bothLinear = (params.f as Rule).kind === "linear" && (params.g as Rule).kind === "linear";
    return bothLinear && !C.isNeg(params.p as Rational) ? 2 : 3;
  }
  if (task === "composite_expression") {
    const [outer, inner] = outerInner(params);
    if (outer.kind === "linear" && inner.kind === "linear") return 3;
    const hard = outer.kind === "quadratic" && (C.isNeg(inner.a!) || !eqn(inner.a!.abs(), 1) || !eqn(outer.a!, 1));
    return hard ? 5 : 4;
  }
  if (task === "function_from_composite") return eqn(params.m as Rational, 1) ? 4 : 5;
  if (task === "inverse_value") {
    if (params.form === "inverse_at") return (solve(task, params) as Rational).den === 1 ? 2 : 3;
    return C.cmp((params.a as Rational).abs(), rat(2)) >= 0 && !(params.b as Rational).isZero() ? 4 : 3;
  }
  if (task === "inverse_expression") return eqn((params.a as Rational).abs(), 1) ? 3 : 4;
  const r = params.rule as Rule;
  return eqn(r.a!, 1) && r.b!.num % 2 === 0 ? 4 : 5;
}

const STEPS_AX: Record<string, number> = { identify_function: 0.25, evaluate_function: 0.3, solve_for_input: 0.5, domain_of_function: 0.45,
  range_of_function: 0.6, composite_value: 0.45, composite_expression: 0.65, function_from_composite: 0.8,
  inverse_value: 0.5, inverse_expression: 0.65, one_to_one_restriction: 0.7 };
const ALG_AX: Record<string, number> = { identify_function: 0.1, evaluate_function: 0.3, solve_for_input: 0.5, domain_of_function: 0.4,
  range_of_function: 0.55, composite_value: 0.4, composite_expression: 0.75, function_from_composite: 0.85,
  inverse_value: 0.5, inverse_expression: 0.7, one_to_one_restriction: 0.6 };
const ABS_AX: Record<string, number> = { identify_function: 0.5, evaluate_function: 0.25, solve_for_input: 0.35, domain_of_function: 0.6,
  range_of_function: 0.7, composite_value: 0.5, composite_expression: 0.65, function_from_composite: 0.85,
  inverse_value: 0.6, inverse_expression: 0.7, one_to_one_restriction: 0.85 };
const REP_AX: Record<string, number> = { identify_function: 0.4, evaluate_function: 0.2, solve_for_input: 0.25, domain_of_function: 0.55,
  range_of_function: 0.6, composite_value: 0.35, composite_expression: 0.45, function_from_composite: 0.5,
  inverse_value: 0.4, inverse_expression: 0.45, one_to_one_restriction: 0.55 };
const CONN_AX: Record<string, number> = { identify_function: 0.1, evaluate_function: 0.1, solve_for_input: 0.3, domain_of_function: 0.3,
  range_of_function: 0.5, composite_value: 0.4, composite_expression: 0.5, function_from_composite: 0.7,
  inverse_value: 0.5, inverse_expression: 0.55, one_to_one_restriction: 0.8 };

function difficulty(task: string, params: Params): Json {
  const b = band(task, params);
  const [lo, hi] = TASK_BANDS[task as keyof typeof TASK_BANDS]!;
  const span = Math.max(1, hi - lo);
  const bump = ((b - lo) / span) * 0.2;
  return {
    overallBand: b,
    axes: {
      numericalComplexity: round3(clamp01(0.25 + bump)),
      algebraicComplexity: round3(clamp01(ALG_AX[task]! + bump)),
      reasoningSteps: round3(clamp01(STEPS_AX[task]! + bump)),
      abstraction: round3(clamp01(ABS_AX[task]! + bump)),
      representation: round3(clamp01(REP_AX[task]! + bump)),
      requiredConnections: round3(clamp01(CONN_AX[task]! + bump)),
      exactVsApproximate: round3(clamp01(0)),
    },
  };
}

// --------------------------------------------------------------------------- //
// generate
// --------------------------------------------------------------------------- //

const encodeRelation = (v: number[][]): { value: Json; display: string } => ({ value: v, display: pairsDisplay(v) });
const encodeValue = (v: Value): { value: Json; display: string } => ({ value: valueJson(v), display: valueDisplay(v) });

export function generate(seed: number, config?: Json): Json {
  config = config || {};
  const explicit = config.task;
  if (explicit !== undefined && explicit !== null && !(explicit in OBJECTIVE_BY_TASK)) {
    throw new Error(`unknown task '${explicit}'`);
  }

  const rng = new Mulberry32(seed);
  let task: string;
  if (explicit === undefined || explicit === null) {
    const requested = config.interactionType;
    const pool = requested === "free-response" ? TASKS.filter((t) => !(MC_ONLY_TASKS as string[]).includes(t)) : [...TASKS];
    task = rng.choice(pool);
  } else {
    task = explicit as string;
  }

  const interaction = resolveInteraction(task, config);
  const mc = interaction === "multiple-choice";

  let params: Params = {};
  let distractors: Distractor[] | null = null;
  let ok = false;
  for (let attempt = 0; attempt < MAX_PARAM_ATTEMPTS; attempt++) {
    const drawn = DRAW[task]!(rng);
    if (drawn === null || !acceptable(task, drawn)) continue;
    if (mc && task !== "identify_function") {
      const ds = mcDistractors(task, drawn, rng);
      if (ds === null) continue;
      distractors = ds;
    }
    params = drawn;
    ok = true;
    break;
  }
  if (!ok) throw new Error(`could not draw acceptable functions params for ${task} seed=${seed}`);

  let options: Json[] | null = null;
  let records: Json[] | null = null;
  let answer: Json;
  if (task === "identify_function") {
    const ds = (params.functions as Json[]).map((f) => ({
      value: f.pairs as number[][], misconceptionId: f.misconceptionId as string,
      rationale: FM.MISCONCEPTIONS[f.misconceptionId as string]!.observableError,
    }));
    const mcOut = assembleMultipleChoice(rng, params.nonFunction as number[][], ds, encodeRelation);
    records = mcOut.distractors;
    options = mcOut.options;
    const label = options.find((o) => o.correct)!.label as string;
    answer = { type: "multiple-choice", canonical: label, display: label };
  } else {
    const value = solve(task, params);
    answer = encodeAnswer(task, value);
    if (mc) {
      const mcOut = assembleMultipleChoice(rng, value, distractors ?? [], encodeValue);
      records = mcOut.distractors;
      options = mcOut.options;
    }
  }

  const item: Json = {
    itemId: `ITEM-FUNC-${task}-${seed}`,
    schemaVersion: SCHEMA_VERSION,
    objectiveIds: [OBJECTIVE_BY_TASK[task as keyof typeof OBJECTIVE_BY_TASK]],
    generatorId: GENERATOR_ID,
    generatorVersion: GENERATOR_VERSION,
    seed,
    params: publicParams(params),
    interactionType: interaction,
    prompt: prompt(task, params),
    answer,
    solution: solution(task, params, answer.display as string, options),
    difficulty: difficulty(task, params),
    calculatorPolicy: CALCULATOR_POLICY,
    accessibility: { spokenMath: spoken(task, params, options), nonColorIndicators: true },
    provenance: { origin: "generated", rightsStatus: "academy-owned",
      originalityNote: "Original parameterized item; structure abstracted from the IB AA SL functions syllabus." },
    lifecycle: { state: "generated" },
  };
  if (options !== null) {
    item.distractors = records;
    item.options = options;
  }
  return item;
}

// --------------------------------------------------------------------------- //
// validate (independent — mirror of the Python validate)
// --------------------------------------------------------------------------- //

// Internal coefficient names must never leak into student-facing feedback as bare symbols. The English
// article "a", the change-of-variable letter "u" and the textbook formula "-b/(2a)" are not leaks.
const PLACEHOLDER = /(?<![A-Za-z])[bcmpqtv](?![A-Za-z])/;
const ALLOWED_FRAGMENTS = ["-b/(2a)"];

function hasPlaceholder(text: string): boolean {
  let t = text;
  for (const frag of ALLOWED_FRAGMENTS) t = t.split(frag).join(" ");
  return PLACEHOLDER.test(t);
}

function promptText(item: Json): string {
  const parts: string[] = (item.prompt.blocks as Json[]).map((b) => (b.text ?? "") + " " + (b.latex ?? ""));
  parts.push(item.accessibility?.spokenMath ?? "");
  return parts.join(" ");
}

/** The requested quantity must never be stated with its answer in the prompt or spoken text. */
function explicitReveal(task: string, item: Json, params: Params): boolean {
  const disp = item.answer.display as string;
  const n = (params.name as string | undefined) ?? "f";
  const txt = promptText(item);
  let tok: string;
  if (task === "identify_function") return false;
  if (task === "evaluate_function") tok = `${n}(${ratDisplay(params.p)}) =`;
  else if (task === "solve_for_input") tok = "x =";
  else if (task === "domain_of_function" || task === "range_of_function") return txt.includes(`= ${disp}`) || txt.includes(`is ${disp}`);
  else if (task === "composite_value") {
    const [, , on, inn] = outerInner(params);
    tok = `(${on} o ${inn})(${ratDisplay(params.p)}) =`;
  } else if (task === "composite_expression") {
    const [, , on, inn] = outerInner(params);
    tok = `(${on} o ${inn})(x) =`;
  } else if (task === "function_from_composite") tok = "f(x) =";
  else if (task === "inverse_value") tok = params.form === "inverse_at" ? `${n}^-1(${ratDisplay(params.k)}) =` : "k =";
  else if (task === "inverse_expression") tok = `${n}^-1(x) =`;
  else tok = "k =";
  return txt.includes(`${tok} ${disp}`);
}

function isFunctionRelation(pairs: number[][]): boolean {
  const seen = new Map<number, number>();
  for (const [x, y] of pairs as [number, number][]) {
    if (seen.has(x) && seen.get(x) !== y) return false;
    if (!seen.has(x)) seen.set(x, y);
  }
  return true;
}

function structureMatches(pairs: number[][], mid: string): boolean {
  const xs = pairs.map((p) => p[0]!);
  const ys = pairs.map((p) => p[1]!);
  if (new Set(xs).size !== xs.length) return false;
  const distinctY = new Set(ys).size;
  if (mid === "MISC.FUNC.MANY_TO_ONE_REJECTED") return distinctY < ys.length && distinctY > 1;
  if (mid === "MISC.FUNC.CONSTANT_REJECTED") return distinctY === 1;
  if (mid === "MISC.FUNC.PATTERN_REQUIRED") {
    const sortedXs = [...xs].sort((a, b) => a - b);
    const unsorted = xs.some((v, i) => v !== sortedXs[i]);
    return distinctY === ys.length && unsorted && !collinear(pairs);
  }
  return false;
}

function parseDisplayNumber(s: string): Rational | null {
  const m = /^(-?\d+)(?:\/(\d+))?$/.exec(s.trim());
  if (!m) return null;
  const den = m[2] !== undefined ? Number(m[2]) : 1;
  if (den === 0) return null;
  return new Rational(Number(m[1]), den);
}

function reparses(task: string, answer: Json): boolean {
  const fam = ANSWER_FAMILY[task]!;
  if (fam === "choice") return answer.canonical === answer.display;
  if (fam === "number") {
    const parsed = parseDisplayNumber(answer.display as string);
    return parsed !== null && parsed.equals(ratFromJson(answer.canonical as RatJson));
  }
  if (fam === "expression") return checkExpression(answer.display as string, answer.canonical as PolyJson).code === "correct";
  return checkInterval(answer.display as string, answer.canonical as IntervalJson).code === "correct";
}

function reducedJson(t: RatJson): boolean {
  if (!Number.isInteger(t.num) || !Number.isInteger(t.den) || t.den < 1) return false;
  const f = new Rational(t.num, t.den);
  return f.num === t.num && f.den === t.den;
}

function canonicalNormalized(task: string, answer: Json): boolean {
  const fam = ANSWER_FAMILY[task]!;
  if (fam === "number") return reducedJson(answer.canonical as RatJson);
  if (fam === "expression") {
    const c = answer.canonical as PolyJson;
    const coeffs = c.coefficients;
    if (c.variable !== "x" || !coeffs || coeffs.length === 0) return false;
    const last = coeffs[coeffs.length - 1]!;
    const stripped = coeffs.length === 1 || last.num !== 0;
    const reduced = coeffs.every(reducedJson);
    return stripped && reduced;
  }
  if (fam === "interval") {
    const c = answer.canonical as IntervalJson;
    if (c.kind === "bounded") return C.lt(ratFromJson(c.lo), ratFromJson(c.hi));
    if (c.kind === "reals-except") {
      const pts = c.points.map(ratFromJson);
      if (pts.length < 1) return false;
      for (let i = 1; i < pts.length; i++) if (C.cmp(pts[i - 1]!, pts[i]!) >= 0) return false;
      return true;
    }
    return true;
  }
  return true;
}

export function validate(item: Json): Json {
  const checks: Json[] = [];
  const add = (name: string, ok: boolean, detail = ""): void => { checks.push({ name, result: ok ? "pass" : "fail", detail }); };

  const pub = item.params as Json;
  const task = pub.task as string;
  const params = internalParams(pub);
  const answer = item.answer as Json;
  const fam = ANSWER_FAMILY[task]!;
  const interaction = item.interactionType as string | undefined;

  add("params-in-domain", task in OBJECTIVE_BY_TASK && acceptable(task, params), `task=${task}`);
  add("interaction-type", interaction !== undefined && supportedInteractions(task).includes(interaction), String(interaction));
  add("objective-mapping", JSON.stringify(item.objectiveIds) === JSON.stringify([OBJECTIVE_BY_TASK[task as keyof typeof OBJECTIVE_BY_TASK]]), (item.objectiveIds as string[]).join(","));
  const expectedType: Record<Family, string[]> = { choice: ["multiple-choice"], number: ["integer", "exact-rational"], expression: ["algebraic-expression"], interval: ["interval"] };
  add("answer-type-consistency", expectedType[fam].includes(answer.type)
    && (fam !== "number" || (answer.type === "integer") === (answer.canonical.den === 1)), answer.type);
  add("canonical-form-normalized", canonicalNormalized(task, answer), JSON.stringify(answer.canonical).slice(0, 80));
  add("display-reparses-to-canonical", reparses(task, answer), answer.display);

  // --- independent mathematical confirmation per task ---------------------------------------- //
  if (task === "identify_function") {
    const opts: Json[] = item.options ?? [];
    const nonFn = opts.filter((o) => !isFunctionRelation(o.value as number[][]));
    add("exactly-one-non-function", nonFn.length === 1 && Boolean(nonFn[0]!.correct) && nonFn[0]!.label === answer.canonical,
      nonFn.map((o) => o.label).join(","));
    const structural = opts.filter((o) => !o.correct).every((o) => structureMatches(o.value as number[][], (o.misconceptionId as string | undefined) ?? ""));
    add("distractor-structure-matches-misconception", structural, "");
    const displays = new Set(opts.map((o) => o.display as string));
    add("options-distinct-displays", displays.size === opts.length && opts.length === 4, "");
  } else if (task === "evaluate_function") {
    const r = params.rule as Rule, p = params.p as Rational;
    const want = ratFromJson(answer.canonical as RatJson);
    let ok: boolean;
    if (C.isPolynomialRule(r)) {
      ok = C.rulePoly(r).eval(p).equals(want);
    } else if (r.kind === "reciprocal") {
      ok = !p.equals(r.h!) && r.k!.add(r.v!.mul(p.sub(r.h!))).equals(want.mul(p.sub(r.h!)));
    } else {
      const t = want.sub(r.v!);
      ok = !C.isNeg(t) && t.mul(t).equals(C.radicand(r, p));
    }
    add("value-recomputed-independently", ok, ratDisplay(want));
  } else if (task === "solve_for_input") {
    const x = ratFromJson(answer.canonical as RatJson);
    const got = C.evalRule(params.rule as Rule, x);
    add("solution-satisfies-equation", got !== null && got.equals(params.target as Rational), `x=${ratDisplay(x)}`);
  } else if (task === "domain_of_function") {
    const r = params.rule as Rule;
    const c = answer.canonical as Json;
    let ok: boolean;
    if (r.kind === "sqrt") {
      if (c.kind === "ray") {
        const e = ratFromJson(c.endpoint as RatJson);
        const step = rat(c.direction === "ge" ? 1 : -1);
        const inside = e.add(step), outside = e.sub(step);
        ok = c.variable === "x" && Boolean(c.inclusive) && C.radicand(r, e).isZero()
          && C.isPos(C.radicand(r, inside)) && C.isNeg(C.radicand(r, outside));
      } else {
        ok = false;
      }
    } else if (r.kind === "reciprocal") {
      const pts: Rational[] = ((c.points as RatJson[] | undefined) ?? []).map(ratFromJson);
      ok = c.kind === "reals-except" && c.variable === "x" && pts.length === 1 && pts[0]!.sub(r.h!).isZero()
        && C.evalRule(r, pts[0]!.add(ONE)) !== null && C.evalRule(r, pts[0]!.sub(ONE)) !== null;
    } else {
      ok = c.kind === "reals" && [-1, 0, 1].every((x) => C.evalRule(r, rat(x)) !== null);
    }
    add("domain-boundary-probe", ok, c.kind);
  } else if (task === "range_of_function") {
    const r = params.rule as Rule;
    const c = answer.canonical as Json;
    let ok: boolean;
    if (r.kind === "quadratic") {
      if (c.kind === "ray") {
        const k = ratFromJson(c.endpoint as RatJson);
        const hx = C.vertexX(r);
        const side = c.direction === "ge" ? 1 : -1;
        ok = c.variable === "y" && Boolean(c.inclusive) && C.evalRule(r, hx)!.equals(k)
          && [1, 2, -1, -2].every((t) => side * C.cmp(C.evalRule(r, hx.add(rat(t)))!.sub(k), ZERO) > 0);
      } else {
        ok = false;
      }
    } else if (r.kind === "sqrt") {
      const e = r.b!.neg().div(r.a!);
      ok = c.kind === "ray" && c.variable === "y" && Boolean(c.inclusive) && c.direction === "ge"
        && C.evalRule(r, e)!.equals(ratFromJson(c.endpoint as RatJson)) && C.isPos(C.radicand(r, e.add(rat(C.isPos(r.a!) ? 1 : -1))));
    } else if (r.kind === "reciprocal") {
      const pts: Rational[] = ((c.points as RatJson[] | undefined) ?? []).map(ratFromJson);
      if (c.kind === "reals-except" && c.variable === "y" && pts.length === 1) {
        const up = C.evalRule(r, r.h!.add(ONE))!, down = C.evalRule(r, r.h!.sub(ONE))!;
        ok = !up.equals(pts[0]!) && !down.equals(pts[0]!) && up.sub(pts[0]!).equals(down.sub(pts[0]!).neg());
      } else {
        ok = false;
      }
    } else {
      const p = params.restricted.p as Rational, q = params.restricted.q as Rational;
      const fp = C.evalRule(r, p)!, fq = C.evalRule(r, q)!;
      const imgs = C.lt(fp, fq) ? [fp, fq] : [fq, fp];
      ok = c.kind === "bounded" && c.variable === "y" && Boolean(c.loInclusive) && Boolean(c.hiInclusive)
        && ratFromJson(c.lo as RatJson).equals(imgs[0]!) && ratFromJson(c.hi as RatJson).equals(imgs[1]!) && C.lt(p, q);
    }
    add("range-attained-and-bounded", ok, c.kind);
  } else if (task === "composite_value") {
    const [outer, inner] = outerInner(params);
    const want = ratFromJson(answer.canonical as RatJson);
    const got = C.rulePoly(outer).eval(C.rulePoly(inner).eval(params.p as Rational));
    add("composite-recomputed-stepwise", got.equals(want), ratDisplay(got));
  } else if (task === "composite_expression") {
    const [outer, inner] = outerInner(params);
    const stored = Poly.fromJson(answer.canonical as PolyJson);
    const po = C.rulePoly(outer), pi = C.rulePoly(inner);
    const agree = [-2, -1, 0, 1, 2].every((x) => stored.eval(x).equals(po.eval(pi.eval(x))));
    add("composite-pointwise-agreement", agree, stored.display());
    add("degree-bound", stored.degree() <= 2, String(stored.degree()));
  } else if (task === "function_from_composite") {
    const stored = Poly.fromJson(answer.canonical as PolyJson);
    const g = Poly.linear(params.m as Rational, params.c as Rational);
    const given = compositeOfParams(params);
    add("recomposes-to-given", stored.compose(g).equals(given), stored.display());
  } else if (task === "inverse_value") {
    const a = params.a as Rational, b = params.b as Rational;
    const v = ratFromJson(answer.canonical as RatJson);
    if (params.form === "inverse_at") add("inverse-value-satisfies-forward", a.mul(v).add(b).equals(params.k as Rational), ratDisplay(v));
    else add("inverse-value-satisfies-forward", v.sub(b).div(a).equals(params.x0 as Rational), ratDisplay(v));
  } else if (task === "inverse_expression") {
    const stored = Poly.fromJson(answer.canonical as PolyJson);
    const f = Poly.linear(params.a as Rational, params.b as Rational);
    add("inverse-round-trip", f.compose(stored).equals(Poly.x()) && stored.compose(f).equals(Poly.x()), stored.display());
  } else {
    const r = params.rule as Rule;
    const h = ratFromJson(answer.canonical as RatJson);
    add("axis-of-symmetry-probe", [1, 2, 3].every((t) => C.evalRule(r, h.add(rat(t)))!.equals(C.evalRule(r, h.sub(rat(t)))!)), ratDisplay(h));
  }

  // --- solution, leakage, MC -------------------------------------------------------------- //
  const steps = item.solution.steps as Json[];
  const last = steps[steps.length - 1]!;
  add("answer-solution-agree", ((last.intermediateResult as string | undefined) ?? "").includes(answer.display as string), "");
  add("no-answer-leakage", !explicitReveal(task, item, params), "");

  if (task !== "identify_function" && item.distractors && (item.distractors as Json[]).length > 0) {
    const ds = item.distractors as Json[];
    const mids = ds.map((d) => d.misconceptionId as string);
    add("distractors-distinct-misconceptions", new Set(mids).size === mids.length, mids.join(","));
    add("min-three-distractors", ds.length >= 3, String(ds.length));
    const ctx = ctxFor(task, params);
    for (const d of ds) {
      const mid = d.misconceptionId as string;
      const m = FM.MISCONCEPTIONS[mid];
      add("distractor-misconception-known", m !== undefined && FM.rulesFor(task).includes(mid), mid);
      if (m === undefined) continue;
      const expected = m.wrong(ctx);
      add("distractor-value-matches-rule", expected !== null && valueDisplay(expected) === d.display
        && canonicalStringify(valueJson(expected)) === canonicalStringify(d.value), mid);
      add("distractor-rationale-matches", d.rationale === m.observableError, mid);
      const fb = m.feedback(ctx);
      add("distractor-feedback-present", Boolean(fb), mid);
      add("distractor-feedback-clean", !hasPlaceholder(fb), fb);
      add("distractor-not-answer", d.display !== answer.display, d.display);
    }
  }
  if (item.options && (item.options as Json[]).length > 0) {
    const opts = item.options as Json[];
    const correct = opts.filter((o) => o.correct);
    const expectedDisplay = task !== "identify_function" ? answer.display : pairsDisplay(params.nonFunction as number[][]);
    add("exactly-one-correct", correct.length === 1 && correct[0]!.display === expectedDisplay, "");
    const wrong = opts.filter((o) => !o.correct).map((o) => o.display as string);
    add("distractors-unique", new Set(wrong).size === wrong.length, "");
    add("options-labelled-in-order", JSON.stringify(opts.map((o) => o.label)) === JSON.stringify(LABELS.slice(0, opts.length)), "");
  }

  add("a11y-fields-present", Boolean(item.accessibility?.spokenMath), "");
  add("provenance-complete", Boolean(item.provenance?.origin) && Boolean(item.provenance?.rightsStatus), "");
  add("version-fields-present", Boolean(item.generatorId) && Boolean(item.generatorVersion), "");

  const status = checks.every((c) => c.result === "pass") ? "pass" : "fail";
  return { status, validatorVersion: VALIDATOR_VERSION, checks };
}

// --------------------------------------------------------------------------- //
// render / serialize / describe
// --------------------------------------------------------------------------- //

export function render(item: Json, mode: "full" | "question-only" | "answer-only" = "full"): string {
  const lines: string[] = [];
  for (const b of item.prompt.blocks as Json[]) lines.push(b.text || b.latex || "");
  for (const o of (item.options as Json[] | undefined) ?? []) lines.push(`  ${o.label}. ${o.display}`);
  if (mode === "answer-only") return `Answer: ${item.answer.display}`;
  const out = [...lines];
  if (mode === "full") {
    out.push("", "Solution:");
    for (const s of item.solution.steps as Json[]) {
      const bit = s.intermediateResult || s.ruleOrTheorem || s.explanation || "";
      out.push(`  ${s.number}. ${s.transformation ?? ""}: ${bit}`);
    }
  }
  out.push(`Answer: ${item.answer.display}`);
  return out.join("\n");
}

export function serialize(item: Json): string {
  return canonicalStringify(item);
}

export function describe(): Json {
  return {
    generatorId: GENERATOR_ID,
    version: GENERATOR_VERSION,
    title: "Introducing Functions (IB AA SL): notation, domain and range, composition, inverses",
    domain: "functions",
    strand: "introducing-functions",
    objectiveIds: TASKS.map((t) => OBJECTIVE_BY_TASK[t as keyof typeof OBJECTIVE_BY_TASK]),
    tasks: [...TASKS],
    interactionTypes: ["free-response", "multiple-choice"],
    answerTypes: ["integer", "exact-rational", "algebraic-expression", "interval", "multiple-choice"],
    difficultyRanges: Object.fromEntries(TASKS.map((t) => [OBJECTIVE_BY_TASK[t as keyof typeof OBJECTIVE_BY_TASK], [...TASK_BANDS[t as keyof typeof TASK_BANDS]!]])),
    misconceptionIds: Object.keys(FM.MISCONCEPTIONS).sort(),
    approvalStatus: "pending-review",
  };
}
