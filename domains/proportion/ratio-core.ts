/**
 * gen.proportion.ratio — exact Ratio model, proportional reasoning, the anchored ratio parser /
 * canonicalizer / formatter / equivalence checker, the result-code vocabularies, and the answer
 * encoders.
 *
 * Byte-for-byte TypeScript mirror of oracle/spi_oracle/ratio_core.py.
 * EXACT: every value is an integer or an exact Rational (mirrors Python Fraction). NO floats, NO
 * tolerance, NO irrational anywhere. A ratio is an ORDERED tuple of POSITIVE integers; the canonical
 * (simplest) form divides every part by their gcd and PRESERVES order (2:3 != 3:2; 2:3 == 4:6).
 */

import { Rational } from "../../core/exact-math/rational.ts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = any;

// --------------------------------------------------------------------------- //
// The ONE ratio result-code vocabulary (owner F). Lower-kebab.
// --------------------------------------------------------------------------- //
export const RATIO_RESULT_CODES: readonly string[] = [
  "correct",
  "equivalent-not-simplified",
  "wrong-order",
  "wrong-ratio",
  "wrong-number-of-parts",
  "zero-or-negative-part",
  "unsupported-term",
  "unparsed-trailing-text",
  "malformed-response",
];
// The best-buy / choice vocabulary (owner F).
export const CHOICE_RESULT_CODES: readonly string[] = ["correct", "wrong-choice", "malformed-response"];

// --------------------------------------------------------------------------- //
// Exact ratio model + proportional reasoning (owner 6)
// --------------------------------------------------------------------------- //
function gcd2(a: number, b: number): number {
  a = Math.abs(a);
  b = Math.abs(b);
  while (b) {
    const t = a % b;
    a = b;
    b = t;
  }
  return a;
}

export function gcdList(parts: number[]): number {
  let g = 0;
  for (const p of parts) {
    g = gcd2(g, Math.abs(p));
  }
  return g || 1;
}

export function simplifyParts(parts: number[]): number[] {
  // Divide every part by the gcd, preserving order (owner 6). parts must be positive integers.
  const g = gcdList(parts);
  return parts.map((p) => Math.trunc(p / g));
}

export function isSimplest(parts: number[]): boolean {
  return gcdList(parts) === 1;
}

export function ratiosEqual(a: number[], b: number[]): boolean {
  // Order-sensitive equivalence: a ~ b iff same length and simplest forms are identical (owner 6).
  if (a.length !== b.length) return false;
  const sa = simplifyParts(a);
  const sb = simplifyParts(b);
  return sa.every((v, i) => v === sb[i]);
}

export function crossMultiplyEqual(a0: number, a1: number, b0: number, b1: number): boolean {
  return a0 * b1 === a1 * b0;
}

export function totalParts(parts: number[]): number {
  return parts.reduce((s, p) => s + p, 0);
}

export function share(total: number, parts: number[]): number[] | null {
  // Exact integer sharing by the total-parts method: requires total divisible by sum(parts).
  const s = parts.reduce((acc, p) => acc + p, 0);
  if (s === 0 || total % s !== 0) {
    return null;
  }
  const one = Math.trunc(total / s);
  return parts.map((p) => one * p);
}

export function missingPart(
  knownValue: number,
  knownIndex: number,
  missingIndex: number,
  parts: number[],
): number | null {
  // Integer missing-part (owner E): requires parts[known_index] divides known_value.
  const k = parts[knownIndex] as number;
  if (k === 0 || knownValue % k !== 0) {
    return null;
  }
  return Math.trunc(knownValue / k) * (parts[missingIndex] as number);
}

export function unitRate(total: number, quantity: number): Rational {
  return new Rational(total, quantity);
}

export function directProportion(total: number, quantity: number, target: number): Rational {
  return new Rational(total, quantity).mul(Rational.from(target));
}

export function inverseProportion(q1: number, v1: number, q2: number): number | null {
  // Product invariant q1*v1 = q2*v2 (owner 6); integer-only.
  const prod = q1 * v1;
  if (q2 === 0 || prod % q2 !== 0) {
    return null;
  }
  return Math.trunc(prod / q2);
}

export function scaleValue(value: number, factor: Rational): Rational {
  return Rational.from(value).mul(factor);
}

// --------------------------------------------------------------------------- //
// Anchored parser / canonicalizer / formatter (owner G)
// --------------------------------------------------------------------------- //
export function formatRatio(parts: number[]): string {
  return parts.map((p) => String(p)).join(":");
}

export function canonicalize(parts: number[]): number[] {
  return simplifyParts(parts);
}

export function parseRatio(text: string | null | undefined): [number[] | null, string | null] {
  if (text === null || text === undefined || String(text).trim() === "") {
    return [null, "malformed-response"];
  }
  const s = String(text).trim();
  // unsupported unicode ratio colon (U+2236) or word form -> unsupported-term
  if (s.indexOf("∶") !== -1 || /\bto\b/i.test(s)) {
    return [null, "unsupported-term"];
  }
  if (s.indexOf(",") !== -1) {
    return [null, "unsupported-term"]; // comma-separated not supported
  }
  if (s.indexOf(":") === -1) {
    return [null, "malformed-response"];
  }
  const raw = s.split(":");
  if (raw.length < 2) {
    return [null, "malformed-response"];
  }
  if (raw.length > 3) {
    return [null, "wrong-number-of-parts"];
  }
  const parts: number[] = [];
  for (const tok of raw) {
    const t = tok.trim();
    if (t === "") {
      return [null, "malformed-response"]; // missing part
    }
    if (/^-?\d+\.\d+$/.test(t)) {
      return [null, "unsupported-term"]; // decimal term
    }
    const m = /^(-?\d+)$/.exec(t);
    if (m === null) {
      // trailing junk after a number, e.g. '2x' or '3 cats'
      if (/^-?\d+\S/.test(t) || /^-?\d+\s+\S/.test(t)) {
        return [null, "unparsed-trailing-text"];
      }
      return [null, "malformed-response"];
    }
    const v = parseInt(m[1] as string, 10);
    if (v <= 0) {
      return [null, "zero-or-negative-part"];
    }
    parts.push(v);
  }
  return [parts, null];
}

// --------------------------------------------------------------------------- //
// Equivalence checker (owner F) — order-sensitive; simplest-form policy per task.
// --------------------------------------------------------------------------- //
function arrayEq(a: number[], b: number[]): boolean {
  return a.length === b.length && a.every((v, i) => v === b[i]);
}

export function checkRatio(
  expectedParts: number[],
  studentText: string | null | undefined,
  requireSimplest = true,
): Json {
  const [parts, code] = parseRatio(studentText);
  if (code !== null) {
    return { code, partial: false };
  }
  const p = parts as number[];
  const exp = simplifyParts(expectedParts);
  if (p.length !== exp.length) {
    return { code: "wrong-number-of-parts", partial: false };
  }
  const sSimp = simplifyParts(p);
  if (arrayEq(sSimp, exp)) {
    if (arrayEq(p, exp)) {
      return { code: "correct", partial: false };
    }
    // equivalent but not in simplest form
    if (requireSimplest) {
      return { code: "equivalent-not-simplified", partial: true };
    }
    return { code: "correct", partial: false };
  }
  const sortedS = sSimp.slice().sort((x, y) => x - y);
  const sortedE = exp.slice().sort((x, y) => x - y);
  if (arrayEq(sortedS, sortedE)) {
    return { code: "wrong-order", partial: false };
  }
  return { code: "wrong-ratio", partial: false };
}

export function checkChoice(expectedId: string, studentText: string | null | undefined): string {
  if (studentText === null || studentText === undefined || String(studentText).trim() === "") {
    return "malformed-response";
  }
  const sel = String(studentText).trim().toUpperCase();
  if (!/^[A-Z]$/.test(sel)) {
    return "malformed-response";
  }
  return sel === expectedId.toUpperCase() ? "correct" : "wrong-choice";
}

// --------------------------------------------------------------------------- //
// Answer encoders (owner B, D) — canonical-first; display derived.
// --------------------------------------------------------------------------- //
export function ratioAnswer(parts: number[]): Json {
  const canon = simplifyParts(parts);
  return { type: "ratio", canonical: { parts: canon }, display: formatRatio(canon) };
}

export function rationalAnswer(value: Rational): Json {
  const t = value.den === 1 ? "integer" : "exact-rational";
  const disp = value.den === 1 ? String(value.num) : `${value.num}/${value.den}`;
  return { type: t, canonical: { num: value.num, den: value.den }, display: disp };
}

export function integerAnswer(n: number): Json {
  const i = Math.trunc(n);
  return { type: "integer", canonical: { num: i, den: 1 }, display: String(i) };
}

export function tableAnswer(cells: [string, number][]): Json {
  const enc = cells.map(([loc, val]) => ({ location: loc, value: Math.trunc(val) }));
  const disp = cells.map(([loc, val]) => `${loc}=${val}`).join(", ");
  return { type: "table-completion", canonical: { cells: enc }, display: disp };
}

export function mcAnswer(optionId: string): Json {
  return { type: "multiple-choice", canonical: optionId, display: optionId };
}
