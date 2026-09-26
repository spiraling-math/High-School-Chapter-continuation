/**
 * Real-subset ("interval") answer checker — the `interval` answer type used for domains and ranges.
 *
 * Canonical descriptor (answer.canonical):
 *   {kind: "reals"}
 *   {kind: "ray", variable, endpoint: {num,den}, inclusive, direction: "ge" | "le"}
 *   {kind: "bounded", variable, lo, hi, loInclusive, hiInclusive}
 *   {kind: "reals-except", variable, points: [{num,den}, ...]}          // sorted, distinct
 * with variable in {"x", "y"} (x for a domain, y for a range).
 *
 * Accepted learner forms (ASCII-anchored, unicode conveniences normalised): inequalities (`x >= 2`,
 * `2 <= x`, `-1 < x <= 4`, `x >= -1 and x <= 4`), interval notation (`[2, inf)`, `(-inf, 2]`,
 * `[-1, 4]`), exclusions (`x != 3`, `x =/= 3`, `x != 3, 5`, `all real numbers except 3`, `R \ {3}`),
 * the whole line (`all real numbers`, `R`, `(-inf, inf)`, `x in R`) and set-builder wrappers
 * (`{x | x >= 2}`, `{x : x != 3}`). The variable may be `x`, `y` or `f(x)`/`g(x)`/`h(x)` (read as
 * `y`). Plain-text display: `x >= 2`, `y != 1`, `-1 <= y <= 4`, `all real numbers`.
 *
 * Byte-for-byte counterpart of oracle/spi_oracle/interval_checker.py.
 */

import { Rational } from "../exact-math/rational.ts";
import { ratDisplay, ratFromJson, ratJson, type RatJson } from "../exact-math/polynomial.ts";

export type IntervalCode =
  | "correct" | "unparseable" | "wrong-variable" | "wrong-kind" | "wrong-endpoint" | "wrong-inclusivity" | "wrong-direction" | "misconception";
export const INTERVAL_CODES: readonly IntervalCode[] = [
  "correct", "unparseable", "wrong-variable", "wrong-kind", "wrong-endpoint", "wrong-inclusivity", "wrong-direction", "misconception",
];

export type Variable = "x" | "y";
export type IntervalJson =
  | { kind: "reals" }
  | { kind: "ray"; variable: Variable; endpoint: RatJson; inclusive: boolean; direction: "ge" | "le" }
  | { kind: "bounded"; variable: Variable; lo: RatJson; hi: RatJson; loInclusive: boolean; hiInclusive: boolean }
  | { kind: "reals-except"; variable: Variable; points: RatJson[] };

/** Parsed descriptor (exact rationals; variable null when the notation carried none). */
export type Interval =
  | { kind: "reals"; variable: Variable | null }
  | { kind: "ray"; variable: Variable | null; endpoint: Rational; inclusive: boolean; direction: "ge" | "le" }
  | { kind: "bounded"; variable: Variable | null; lo: Rational; hi: Rational; loInclusive: boolean; hiInclusive: boolean }
  | { kind: "reals-except"; variable: Variable | null; points: Rational[] };

export interface IntervalResult { code: IntervalCode; misconceptionId?: string }
export interface IntervalDiagnostic { misconceptionId: string; canonical: IntervalJson }

const MAX_INPUT_LENGTH = 200;
const UNICODE: ReadonlyArray<[string, string]> = [
  ["≥", ">="], ["⩾", ">="], ["≤", "<="], ["⩽", "<="], ["≠", "!="],
  ["∞", "inf"], ["ℝ", "R"], ["∈", " in "], ["−", "-"], ["–", "-"],
  ["—", "-"], ["∖", "\\"],
];
const NUM = "-?\\d+(?:\\.\\d+)?(?:/\\d+)?";
const VAR = "(?:x|y|[a-z]\\(x\\))";
const RE_INTERVAL = /^([[(])(-inf|-?[\d./]+),(inf|-?[\d./]+)([\])])$/;
const RE_RAY = new RegExp(`^(${VAR})(>=|<=|>|<)(${NUM})$`);
const RE_RAY_REV = new RegExp(`^(${NUM})(>=|<=|>|<)(${VAR})$`);
const RE_BOUNDED = new RegExp(`^(${NUM})(<=|<)(${VAR})(<=|<)(${NUM})$`);
const RE_BOUNDED_REV = new RegExp(`^(${NUM})(>=|>)(${VAR})(>=|>)(${NUM})$`);
const RE_EXCEPT = new RegExp(`^(${VAR})!=(${NUM}(?:,${NUM})*)$`);
const RE_SETBUILDER = new RegExp(`^\\{(${VAR})(?:inr)?[|:](.*)\\}$`);
const RE_WORDS_EXCEPT = new RegExp(`^(?:allrealnumbers|allreals|realnumbers|reals|r)except(${NUM}(?:(?:,|and)${NUM})*)$`);
const RE_SETMINUS = new RegExp(`^r\\\\\\{(${NUM}(?:,${NUM})*)\\}$`);
const RE_VAR_IN_R = new RegExp(`^${VAR}inr$`);
const REALS_WORDS = new Set(["allrealnumbers", "allreals", "realnumbers", "reals", "r", "(-inf,inf)"]);
/** The whitespace class stripped before parsing — spelled out so Python and TypeScript agree exactly. */
const WHITESPACE = new RegExp("[ \\t\\n\\r\\f\\v\\u00a0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000\\ufeff]+", "g");

export function parseNumber(s: string): Rational | null {
  const m = /^(-?)(\d+)(?:\.(\d+))?(?:\/(\d+))?$/.exec(s);
  if (!m) return null;
  const sign = m[1], ip = m[2]!, fp = m[3] ?? "", dp = m[4];
  if (ip.length + fp.length > 12 || (dp !== undefined && dp.length > 12)) return null;
  const den = 10 ** fp.length * (dp !== undefined ? Number(dp) : 1);
  if (den === 0) return null;
  const value = new Rational(Number(ip + fp), den);
  return sign === "-" ? value.neg() : value;
}

export function normalizeInterval(raw: string): string | null {
  let s = raw.trim();
  if (s.length > MAX_INPUT_LENGTH) return null;
  for (const [a, b] of UNICODE) s = s.split(a).join(b);
  s = s.toLowerCase().replace(WHITESPACE, "");
  s = s.split("=/=").join("!=").split("=<").join("<=").split("=>").join(">=");
  s = s.replace(/(?<![a-z])(?:infinity|oo)(?![a-z])/g, "inf");
  s = s.split("thesetof").join("").split("theset").join("").split("suchthat").join("|");
  return s;
}

const variableOf = (tok: string): Variable => (tok === "x" ? "x" : "y"); // y, f(x), g(x), h(x) -> the output variable

function ray(variable: Variable | null, op: string, n: Rational): Interval {
  return { kind: "ray", variable, endpoint: n, inclusive: op === ">=" || op === "<=", direction: op === ">=" || op === ">" ? "ge" : "le" };
}

function bounded(variable: Variable | null, lo: Rational, loInc: boolean, hi: Rational, hiInc: boolean): Interval | null {
  if (!(lo.num * hi.den < hi.num * lo.den)) return null;
  return { kind: "bounded", variable, lo, hi, loInclusive: loInc, hiInclusive: hiInc };
}

const cmp = (a: Rational, b: Rational): number => a.num * b.den - b.num * a.den;
function sortedDistinct(vals: Rational[]): Rational[] {
  const out: Rational[] = [];
  for (const v of [...vals].sort(cmp)) if (!out.some((o) => o.equals(v))) out.push(v);
  return out;
}

function points(text: string): Rational[] | null {
  const vals: Rational[] = [];
  for (const part of text.split(/,|and/)) {
    const n = parseNumber(part);
    if (n === null) return null;
    vals.push(n);
  }
  return sortedDistinct(vals);
}

/** One constraint (no conjunction). */
function parseAtom(s: string): Interval | null {
  if (REALS_WORDS.has(s) || RE_VAR_IN_R.test(s)) {
    return { kind: "reals", variable: s.endsWith("inr") ? variableOf(s.slice(0, -3)) : null };
  }
  let m = RE_WORDS_EXCEPT.exec(s);
  if (m) { const pts = points(m[1]!); return pts === null ? null : { kind: "reals-except", variable: null, points: pts }; }
  m = RE_SETMINUS.exec(s);
  if (m) { const pts = points(m[1]!); return pts === null ? null : { kind: "reals-except", variable: null, points: pts }; }
  m = RE_INTERVAL.exec(s);
  if (m) {
    const lb = m[1]!, loS = m[2]!, hiS = m[3]!, rb = m[4]!;
    const loInf = loS === "-inf", hiInf = hiS === "inf";
    if (loInf && lb !== "(") return null;
    if (hiInf && rb !== ")") return null;
    if (loInf && hiInf) return { kind: "reals", variable: null };
    if (loInf) { const hi = parseNumber(hiS); return hi === null ? null : ray(null, rb === "]" ? "<=" : "<", hi); }
    if (hiInf) { const lo = parseNumber(loS); return lo === null ? null : ray(null, lb === "[" ? ">=" : ">", lo); }
    const lo = parseNumber(loS), hi = parseNumber(hiS);
    if (lo === null || hi === null) return null;
    return bounded(null, lo, lb === "[", hi, rb === "]");
  }
  m = RE_RAY.exec(s);
  if (m) { const n = parseNumber(m[3]!); return n === null ? null : ray(variableOf(m[1]!), m[2]!, n); }
  m = RE_RAY_REV.exec(s);
  if (m) {
    const n = parseNumber(m[1]!);
    const flipped: Record<string, string> = { ">=": "<=", "<=": ">=", ">": "<", "<": ">" };
    return n === null ? null : ray(variableOf(m[3]!), flipped[m[2]!]!, n);
  }
  m = RE_BOUNDED.exec(s);
  if (m) {
    const lo = parseNumber(m[1]!), hi = parseNumber(m[5]!);
    if (lo === null || hi === null) return null;
    return bounded(variableOf(m[3]!), lo, m[2] === "<=", hi, m[4] === "<=");
  }
  m = RE_BOUNDED_REV.exec(s);
  if (m) {
    const hi = parseNumber(m[1]!), lo = parseNumber(m[5]!);
    if (lo === null || hi === null) return null;
    return bounded(variableOf(m[3]!), lo, m[4] === ">=", hi, m[2] === ">=");
  }
  m = RE_EXCEPT.exec(s);
  if (m) { const pts = points(m[2]!); return pts === null ? null : { kind: "reals-except", variable: variableOf(m[1]!), points: pts }; }
  return null;
}

/** Intersect two atoms: reals ∧ X = X; two opposite rays = bounded; two exclusions = union of points. */
function merge(a: Interval, b: Interval): Interval | null {
  const va = a.variable, vb = b.variable;
  if (va !== null && vb !== null && va !== vb) return null;
  const variable = va !== null ? va : vb;
  if (a.kind === "reals") return { ...b, variable };
  if (b.kind === "reals") return { ...a, variable };
  if (a.kind === "ray" && b.kind === "ray" && a.direction !== b.direction) {
    const [loA, hiA] = a.direction === "ge" ? [a, b] : [b, a];
    return bounded(variable, loA.endpoint, loA.inclusive, hiA.endpoint, hiA.inclusive);
  }
  if (a.kind === "reals-except" && b.kind === "reals-except") {
    return { kind: "reals-except", variable, points: sortedDistinct([...a.points, ...b.points]) };
  }
  return null;
}

/** Parse a learner real-subset; code "correct" on success (equivalence judged later). */
export function parseInterval(raw: string): { code: IntervalCode; interval: Interval | null } {
  let s = normalizeInterval(raw);
  if (s === null || s === "") return { code: "unparseable", interval: null };
  const m = RE_SETBUILDER.exec(s);
  let declared: Variable | null = null;
  if (m) {
    declared = variableOf(m[1]!);
    s = m[2]!;
    if (s === "" || s === "r" || s === "inr") return { code: "correct", interval: { kind: "reals", variable: declared } };
  }
  // A single atom first (interval notation contains commas of its own); then conjunctions.
  let acc: Interval | null = parseAtom(s);
  if (acc === null) {
    const parts = s.split(/and|,(?=[a-z(\[])/).filter((p) => p !== "");
    if (parts.length === 0) return { code: "unparseable", interval: null };
    for (const part of parts) {
      const atom = parseAtom(part);
      if (atom === null) return { code: "unparseable", interval: null };
      acc = acc === null ? atom : merge(acc, atom);
      if (acc === null) return { code: "unparseable", interval: null };
    }
  }
  if (declared !== null) {
    if (acc!.variable !== null && acc!.variable !== declared) return { code: "unparseable", interval: null };
    acc = { ...acc!, variable: declared } as Interval;
  }
  return { code: "correct", interval: acc };
}

// --- canonical JSON encoding ------------------------------------------------------------------- //
export function intervalToJson(d: Interval): IntervalJson {
  if (d.kind === "reals") return { kind: "reals" };
  const variable = (d.variable ?? "x") as Variable;
  if (d.kind === "ray") return { kind: "ray", variable, endpoint: ratJson(d.endpoint), inclusive: d.inclusive, direction: d.direction };
  if (d.kind === "bounded") return { kind: "bounded", variable, lo: ratJson(d.lo), hi: ratJson(d.hi), loInclusive: d.loInclusive, hiInclusive: d.hiInclusive };
  return { kind: "reals-except", variable, points: sortedDistinct(d.points).map(ratJson) };
}

export function intervalFromJson(j: IntervalJson): Interval {
  if (j.kind === "reals") return { kind: "reals", variable: null };
  if (j.kind === "ray") return { kind: "ray", variable: j.variable, endpoint: ratFromJson(j.endpoint), inclusive: Boolean(j.inclusive), direction: j.direction };
  if (j.kind === "bounded") return { kind: "bounded", variable: j.variable, lo: ratFromJson(j.lo), hi: ratFromJson(j.hi), loInclusive: Boolean(j.loInclusive), hiInclusive: Boolean(j.hiInclusive) };
  return { kind: "reals-except", variable: j.variable, points: j.points.map(ratFromJson) };
}

/** Plain text: `all real numbers`, `x >= 2`, `y < -1/2`, `-1 <= y <= 4`, `x != 3`, `x != 1, 3`. */
export function intervalDisplay(j: IntervalJson): string {
  const d = intervalFromJson(j);
  if (d.kind === "reals") return "all real numbers";
  const v = d.variable ?? "x";
  if (d.kind === "ray") {
    const op = d.direction === "ge" ? (d.inclusive ? ">=" : ">") : (d.inclusive ? "<=" : "<");
    return `${v} ${op} ${ratDisplay(d.endpoint)}`;
  }
  if (d.kind === "bounded") {
    return `${ratDisplay(d.lo)} ${d.loInclusive ? "<=" : "<"} ${v} ${d.hiInclusive ? "<=" : "<"} ${ratDisplay(d.hi)}`;
  }
  return `${v} != ` + d.points.map(ratDisplay).join(", ");
}

/** Set equality ignoring the variable letter. */
export function sameSet(a: Interval, b: Interval): boolean {
  if (a.kind !== b.kind) return false;
  if (a.kind === "reals") return true;
  if (a.kind === "ray" && b.kind === "ray") return a.endpoint.equals(b.endpoint) && a.inclusive === b.inclusive && a.direction === b.direction;
  if (a.kind === "bounded" && b.kind === "bounded") {
    return a.lo.equals(b.lo) && a.hi.equals(b.hi) && a.loInclusive === b.loInclusive && a.hiInclusive === b.hiInclusive;
  }
  if (a.kind === "reals-except" && b.kind === "reals-except") {
    const pa = sortedDistinct(a.points), pb = sortedDistinct(b.points);
    return pa.length === pb.length && pa.every((v, i) => v.equals(pb[i]!));
  }
  return false;
}

/** Grade a learner input against a canonical real-subset descriptor (JSON form). */
export function checkInterval(raw: string, canonical: IntervalJson, diagnostics: readonly IntervalDiagnostic[] = []): IntervalResult {
  const { code, interval: got } = parseInterval(raw);
  if (got === null) return { code };
  const want = intervalFromJson(canonical);
  const expectedVar = want.variable;
  if (expectedVar !== null && got.variable !== null && got.variable !== expectedVar) return { code: "wrong-variable" };
  if (sameSet(got, want)) return { code: "correct" };
  for (const d of diagnostics) {
    if (sameSet(got, intervalFromJson(d.canonical))) return { code: "misconception", misconceptionId: d.misconceptionId };
  }
  if (got.kind !== want.kind) return { code: "wrong-kind" };
  if (want.kind === "ray" && got.kind === "ray") {
    if (got.direction !== want.direction) return { code: "wrong-direction" };
    if (!got.endpoint.equals(want.endpoint)) return { code: "wrong-endpoint" };
    return { code: "wrong-inclusivity" };
  }
  if (want.kind === "bounded" && got.kind === "bounded") {
    if (!got.lo.equals(want.lo) || !got.hi.equals(want.hi)) return { code: "wrong-endpoint" };
    return { code: "wrong-inclusivity" };
  }
  return { code: "wrong-endpoint" }; // reals-except with different points
}
