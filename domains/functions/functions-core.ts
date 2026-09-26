/**
 * Exact function-rule model for gen.functions.foundations (production TypeScript).
 *
 * A *rule* is a small record with a `kind` and exact `Rational` fields:
 *
 *   linear     {kind, a, b}       a·x + b                 (a ≠ 0)
 *   quadratic  {kind, a, b, c}    a·x² + b·x + c          (a ≠ 0)
 *   reciprocal {kind, k, h, v}    k/(x − h) + v           (k ≠ 0)
 *   sqrt       {kind, a, b, v}    √(a·x + b) + v          (a ≠ 0)
 *
 * Owns everything the generator and the misconception registry need: exact evaluation (null where the
 * value is not an exact rational), polynomial views, the LaTeX / plain-text renderings of a rule, and the
 * real-subset descriptor constructors. No floats anywhere.
 *
 * Byte-for-byte counterpart of oracle/spi_oracle/functions_core.py (every rendered string is part of the
 * cross-language contract).
 */

import { Rational, rat } from "../../core/exact-math/rational.ts";
import { Poly, polyDisplay, ratDisplay, ratFromJson, ratJson, type RatJson } from "../../core/exact-math/polynomial.ts";
import type { Interval, Variable } from "../../core/answer-checking/interval-checker.ts";

export type RuleKind = "linear" | "quadratic" | "reciprocal" | "sqrt";
export interface Rule { kind: RuleKind; a?: Rational; b?: Rational; c?: Rational; k?: Rational; h?: Rational; v?: Rational }
export type RuleJson = { kind: RuleKind } & Record<string, RatJson | RuleKind>;

const F = (x: Rational | number): Rational => Rational.from(x);
const lt = (a: Rational, b: Rational): boolean => a.num * b.den < b.num * a.den;
const gt = (a: Rational, b: Rational): boolean => a.num * b.den > b.num * a.den;
export const isNeg = (a: Rational): boolean => a.num < 0;
export const isPos = (a: Rational): boolean => a.num > 0;
export const cmp = (a: Rational, b: Rational): number => a.num * b.den - b.num * a.den;
export { lt, gt };

// --------------------------------------------------------------------------- //
// Exact helpers
// --------------------------------------------------------------------------- //

/** Integer square root when n is a perfect square (n ≥ 0), else null. */
export function isqrtExact(n: number): number | null {
  if (n < 0) return null;
  let r = 0;
  while ((r + 1) * (r + 1) <= n) r += 1;
  return r * r === n ? r : null;
}

/** Exact non-negative square root of a rational when numerator and denominator are perfect squares. */
export function sqrtExact(q: Rational): Rational | null {
  if (isNeg(q)) return null;
  const rn = isqrtExact(q.num), rd = isqrtExact(q.den);
  if (rn === null || rd === null) return null;
  return new Rational(rn, rd);
}

// --------------------------------------------------------------------------- //
// Rules
// --------------------------------------------------------------------------- //

export const linear = (a: Rational | number, b: Rational | number): Rule => ({ kind: "linear", a: F(a), b: F(b) });
export const quadratic = (a: Rational | number, b: Rational | number, c: Rational | number): Rule => ({ kind: "quadratic", a: F(a), b: F(b), c: F(c) });
export const reciprocal = (k: Rational | number, h: Rational | number, v: Rational | number): Rule => ({ kind: "reciprocal", k: F(k), h: F(h), v: F(v) });
export const sqrtRule = (a: Rational | number, b: Rational | number, v: Rational | number): Rule => ({ kind: "sqrt", a: F(a), b: F(b), v: F(v) });

const FIELDS: readonly (keyof Rule)[] = ["a", "b", "c", "k", "h", "v"];

export function ruleToJson(rule: Rule): RuleJson {
  const out: Record<string, RatJson | RuleKind> = { kind: rule.kind };
  for (const f of FIELDS) {
    const val = rule[f];
    if (val !== undefined && f !== "kind") out[f] = ratJson(val as Rational);
  }
  return out as RuleJson;
}

export function ruleFromJson(j: RuleJson): Rule {
  const out: Rule = { kind: j.kind };
  for (const f of FIELDS) {
    const val = j[f as string];
    if (val !== undefined && typeof val !== "string") (out as unknown as Record<string, unknown>)[f] = ratFromJson(val);
  }
  return out;
}

export const isPolynomialRule = (rule: Rule): boolean => rule.kind === "linear" || rule.kind === "quadratic";

/** The polynomial view of a linear / quadratic rule. */
export function rulePoly(rule: Rule): Poly {
  if (rule.kind === "linear") return Poly.linear(rule.a!, rule.b!);
  if (rule.kind === "quadratic") return Poly.quadratic(rule.a!, rule.b!, rule.c!);
  throw new Error("not a polynomial rule");
}

export const radicand = (rule: Rule, x: Rational | number): Rational => rule.a!.mul(F(x)).add(rule.b!);

/** Exact value f(x), or null when undefined (pole) or irrational (non-square radicand). */
export function evalRule(rule: Rule, x: Rational | number): Rational | null {
  const xf = F(x);
  if (rule.kind === "linear") return rule.a!.mul(xf).add(rule.b!);
  if (rule.kind === "quadratic") return rule.a!.mul(xf).mul(xf).add(rule.b!.mul(xf)).add(rule.c!);
  if (rule.kind === "reciprocal") {
    if (xf.equals(rule.h!)) return null;
    return rule.k!.div(xf.sub(rule.h!)).add(rule.v!);
  }
  const root = sqrtExact(radicand(rule, xf));
  return root === null ? null : root.add(rule.v!);
}

// --------------------------------------------------------------------------- //
// Rendering of rules: LaTeX (prompt math blocks), plain text (displays/spoken)
// --------------------------------------------------------------------------- //

/** LaTeX for a rational: 3, -3, \frac{3}{4}, -\frac{3}{4}. */
export function latexRat(q: Rational): string {
  if (q.den === 1) return String(q.num);
  const s = `\\frac{${Math.abs(q.num)}}{${q.den}}`;
  return isNeg(q) ? "-" + s : s;
}

function latexCoefVar(a: Rational, v: string): string {
  if (a.equals(rat(1))) return v;
  if (a.equals(rat(-1))) return "-" + v;
  return latexRat(a) + v;
}

/** LaTeX for a polynomial, descending degree, e.g. x^{2} - 4x + 1, -\frac{1}{2}x + 3, 0. */
export function latexPoly(p: Poly): string {
  let out = "";
  for (let d = p.c.length - 1; d >= 0; d--) {
    const c = p.c[d]!;
    if (c.isZero()) continue;
    const v = d === 0 ? "" : d === 1 ? "x" : `x^{${d}}`;
    if (out === "") {
      out = d === 0 ? latexRat(c) : latexCoefVar(c, v);
    } else {
      const mag = c.abs();
      const body = d === 0 ? latexRat(mag) : latexCoefVar(mag, v);
      out += (isNeg(c) ? " - " : " + ") + body;
    }
  }
  return out || "0";
}

export function shiftLatex(v: Rational): string {
  if (v.isZero()) return "";
  return isNeg(v) ? " - " + latexRat(v.abs()) : " + " + latexRat(v);
}

export function shiftText(v: Rational): string {
  if (v.isZero()) return "";
  return isNeg(v) ? " - " + ratDisplay(v.abs()) : " + " + ratDisplay(v);
}

export function denominatorLatex(h: Rational): string {
  if (h.isZero()) return "x";
  return isPos(h) ? `x - ${latexRat(h)}` : `x + ${latexRat(h.abs())}`;
}

export function denominatorText(h: Rational): string {
  if (h.isZero()) return "x";
  return isPos(h) ? `x - ${ratDisplay(h)}` : `x + ${ratDisplay(h.abs())}`;
}

const radicandPoly = (rule: Rule): Poly => Poly.linear(rule.a!, rule.b!);

/** ax + b for a > 0; b − |a|x for a < 0 (reads naturally: \sqrt{5 - 2x}). */
export function radicandLatex(rule: Rule): string {
  const a = rule.a!, b = rule.b!;
  if (isPos(a) || b.isZero()) return latexPoly(radicandPoly(rule));
  return `${latexRat(b)} - ${latexCoefVar(a.abs(), "x")}`;
}

export function radicandText(rule: Rule): string {
  const a = rule.a!, b = rule.b!;
  if (isPos(a) || b.isZero()) return polyDisplay(radicandPoly(rule).c);
  const mag = a.abs();
  const coef = mag.equals(rat(1)) ? "x" : mag.den === 1 ? `${mag.num}x` : `(${ratDisplay(mag)})x`;
  return `${ratDisplay(b)} - ${coef}`;
}

export function ruleLatex(rule: Rule): string {
  if (rule.kind === "linear" || rule.kind === "quadratic") return latexPoly(rulePoly(rule));
  if (rule.kind === "reciprocal") {
    const kk = rule.k!;
    const frac = `\\frac{${latexRat(kk.abs())}}{${denominatorLatex(rule.h!)}}`;
    return (isNeg(kk) ? "-" : "") + frac + shiftLatex(rule.v!);
  }
  return `\\sqrt{${radicandLatex(rule)}}` + shiftLatex(rule.v!);
}

/** Plain-text rule, e.g. 2x - 3, x^2 - 4x + 1, 3/(x - 2) + 1, -2/x, sqrt(5 - 2x) - 1. */
export function ruleText(rule: Rule): string {
  if (rule.kind === "linear" || rule.kind === "quadratic") return rulePoly(rule).display();
  if (rule.kind === "reciprocal") {
    const den = denominatorText(rule.h!);
    const denTxt = rule.h!.isZero() ? den : `(${den})`;
    return `${ratDisplay(rule.k!)}/${denTxt}` + shiftText(rule.v!);
  }
  return `sqrt(${radicandText(rule)})` + shiftText(rule.v!);
}

// --------------------------------------------------------------------------- //
// Real-subset descriptors (exact) used by domain / range tasks
// --------------------------------------------------------------------------- //

export const reals = (): Interval => ({ kind: "reals", variable: null });
export const ray = (variable: Variable, endpoint: Rational | number, inclusive: boolean, direction: "ge" | "le"): Interval =>
  ({ kind: "ray", variable, endpoint: F(endpoint), inclusive, direction });
export const bounded = (variable: Variable, lo: Rational | number, hi: Rational | number, loInc = true, hiInc = true): Interval =>
  ({ kind: "bounded", variable, lo: F(lo), hi: F(hi), loInclusive: loInc, hiInclusive: hiInc });
export function realsExcept(variable: Variable, points: ReadonlyArray<Rational | number>): Interval {
  const out: Rational[] = [];
  for (const p of points.map(F).sort(cmp)) if (!out.some((o) => o.equals(p))) out.push(p);
  return { kind: "reals-except", variable, points: out };
}

/** A variable-blind identity key for dedupe (the set, not the letter). */
export function descriptorKey(d: Interval): string {
  if (d.kind === "reals") return "reals";
  if (d.kind === "ray") return `ray:${d.endpoint.toString()}:${d.inclusive ? 1 : 0}:${d.direction}`;
  if (d.kind === "bounded") return `bounded:${d.lo.toString()}:${d.hi.toString()}:${d.loInclusive ? 1 : 0}:${d.hiInclusive ? 1 : 0}`;
  return "except:" + d.points.map((p) => p.toString()).join(",");
}

/** The largest possible domain of a rule, as an exact descriptor in x. */
export function domainOf(rule: Rule): Interval {
  if (isPolynomialRule(rule)) return reals();
  if (rule.kind === "reciprocal") return realsExcept("x", [rule.h!]);
  const a = rule.a!, b = rule.b!;
  return ray("x", b.neg().div(a), true, isPos(a) ? "ge" : "le");
}

export const vertexX = (rule: Rule): Rational => rule.b!.neg().div(rule.a!.mul(rat(2)));
export const vertexY = (rule: Rule): Rational => rule.c!.sub(rule.b!.mul(rule.b!).div(rule.a!.mul(rat(4))));

/** The range of a rule in y: quadratic (vertex), sqrt (y ≥ v), reciprocal (y ≠ v), or a linear rule on the
 *  closed restricted domain [p, q] (endpoint images, ordered). */
export function rangeOf(rule: Rule, restricted?: { p: Rational; q: Rational } | null): Interval {
  if (rule.kind === "quadratic") return ray("y", vertexY(rule), true, isPos(rule.a!) ? "ge" : "le");
  if (rule.kind === "sqrt") return ray("y", rule.v!, true, "ge");
  if (rule.kind === "reciprocal") return realsExcept("y", [rule.v!]);
  if (!restricted) throw new Error("a linear rule needs a restricted domain to have a bounded range");
  const fp = evalRule(rule, restricted.p)!, fq = evalRule(rule, restricted.q)!;
  return lt(fp, fq) ? bounded("y", fp, fq, true, true) : bounded("y", fq, fp, true, true);
}
