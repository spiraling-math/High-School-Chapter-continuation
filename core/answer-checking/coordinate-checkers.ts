/**
 * Reusable answer-equivalence checkers for coordinate geometry (owner decision §15 / I.9).
 *
 * These are deliberately family-agnostic (no coordinate-lines imports) so the
 * Statistics & Data Handling family can reuse them:
 *   - `checkOrderedPair`   : exact, ORDER-SENSITIVE component-wise rational equality.
 *   - `checkLinearEquation`: accepts any input that normalises to the same (m, c) exact
 *                            rationals (y = mx + c, including reordered constant/x terms,
 *                            implicit ±1 coefficients, m = 0 as y = c, and c = 0).
 * Exact `Rational` comparison only — never floats. Vertical / non-`y=` input is rejected.
 */

import { Rational } from "../exact-math/rational.ts";

export interface RatJson { num: number; den: number }

function parseRational(s: string): Rational | null {
  const t = s.trim();
  if (/^-?\d+$/.test(t)) return new Rational(Number(t), 1);
  const m = /^(-?\d+)\/(\d+)$/.exec(t);
  if (m) { const d = Number(m[2]); if (d === 0) return null; return new Rational(Number(m[1]), d); }
  return null;
}

function eq(a: Rational, b: RatJson): boolean { return a.num === b.num && a.den === b.den; }

/** Parse "(x, y)" with integer or fractional components. */
export function parseOrderedPair(input: string): [Rational, Rational] | null {
  const m = /^\(\s*(-?\d+(?:\/\d+)?)\s*,\s*(-?\d+(?:\/\d+)?)\s*\)$/.exec(input.trim());
  if (!m) return null;
  const x = parseRational(m[1]!), y = parseRational(m[2]!);
  return x && y ? [x, y] : null;
}

/** Order-sensitive exact equality against a canonical {x:{num,den}, y:{num,den}}. */
export function checkOrderedPair(input: string, canonical: { x: RatJson; y: RatJson }): boolean {
  const p = parseOrderedPair(input);
  return p ? eq(p[0], canonical.x) && eq(p[1], canonical.y) : false;
}

/**
 * Parse a single linear-in-x expression "RHS" (no "y =") into (m, c) exact rationals.
 * Supports terms like  2x  -x  (3/2)x  3/2x  +4  -3/2 , in any order. Returns null if the
 * expression is not linear in a single variable x.
 */
function parseLinearRhs(rhs: string): { m: Rational; c: Rational } | null {
  let s = rhs.replace(/\s+/g, "").replace(/\(([^)]*)\)/g, "$1"); // drop spaces and ( ) grouping
  if (s === "") return null;
  if (!s.startsWith("+") && !s.startsWith("-")) s = "+" + s;
  let m = new Rational(0, 1), c = new Rational(0, 1);
  // split into signed terms
  const terms = s.match(/[+-][^+-]+/g);
  if (!terms) return null;
  for (const term of terms) {
    const sign = term[0] === "-" ? -1 : 1;
    let body = term.slice(1);
    if (body.includes("x")) {
      let coef = body.replace("x", "");
      if (coef === "" || coef === "*") coef = "1";
      const r = parseRational(coef);
      if (!r) return null;
      m = m.add(sign === -1 ? r.neg() : r);
    } else {
      const r = parseRational(body);
      if (!r) return null;
      c = c.add(sign === -1 ? r.neg() : r);
    }
  }
  return { m, c };
}

/** Accept any input that normalises to the same (m, c). Rejects vertical/non-`y=` forms. */
export function checkLinearEquation(input: string, canonical: { m: RatJson; c: RatJson }): boolean {
  const t = input.trim().replace(/\s+/g, "");
  const lower = t.toLowerCase();
  if (lower.startsWith("x=")) return false; // vertical line: not a y = mx + c answer
  if (!lower.startsWith("y=")) return false;
  const parsed = parseLinearRhs(lower.slice(2));
  if (!parsed) return false;
  return eq(parsed.m, canonical.m) && eq(parsed.c, canonical.c);
}
