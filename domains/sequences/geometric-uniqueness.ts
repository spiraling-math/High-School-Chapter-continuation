/**
 * Independent uniqueness validators for geometric reverse tasks.
 *
 * These compute the COMPLETE real solution set so the validator can confirm a
 * generated item has exactly the response the prompt and canonical answer claim.
 * Mirrors oracle/spi_oracle/geometric_uniqueness.py.
 */

import { Rational, rat } from "../../core/exact-math/rational.ts";

/**
 * Number of real solutions r of  r^m = q  (m = k-1 >= 1).
 *   m odd  -> exactly one real root (any sign of q);
 *   m even -> 0 if q<0, 1 if q=0, 2 if q>0.
 */
export function realRatioSolutionCount(q: Rational, m: number): number {
  if (m % 2 === 1) return 1;
  if (q.num < 0) return 0;
  if (q.num === 0) return 1;
  return 2;
}

/** Exact integer m-th root of a non-negative integer, or null if not perfect. */
function iroot(x: number, m: number): number | null {
  if (x === 0) return 0;
  const r = Math.round(x ** (1 / m));
  for (const c of [r - 1, r, r + 1]) if (c >= 0 && c ** m === x) return c;
  return null;
}

/**
 * The rational principal real root of r^m = q, or null if irrational.
 * For odd m the sign of q is preserved; for even m the non-negative root.
 */
export function rationalRoot(q: Rational, m: number): Rational | null {
  if (q.num === 0) return rat(0);
  const sign = q.num > 0 ? 1 : -1;
  const ra = iroot(Math.abs(q.num), m);
  const rb = iroot(q.den, m);
  if (ra === null || rb === null) return null;
  if (m % 2 === 0 && sign < 0) return null; // no real root
  return new Rational((m % 2 === 1 ? sign : 1) * ra, rb);
}

/** All real solutions r of u1*r^(k-1) = value as exact rationals (best-effort). */
export function realRatioSolutions(u1: number, value: Rational, k: number): Rational[] {
  const m = k - 1;
  const q = value.div(rat(u1)); // r^m = q
  const principal = rationalRoot(q, m);
  if (principal === null) return [];
  if (m % 2 === 1) return [principal];
  // even m, q>0 -> ± ; q=0 -> {0}
  if (principal.isZero()) return [rat(0)];
  return [principal, principal.neg()];
}

/**
 * All indices n in [1, maxN] with u1*r^(n-1) = value. For a well-posed term-index
 * question this is exactly [n]; degenerate ratios (r in {0,1,-1}) can yield none,
 * many, or repeated indices.
 */
export function termIndexSolutions(u1: number, r: Rational, value: Rational, maxN = 40): number[] {
  const out: number[] = [];
  let t = rat(u1);
  for (let n = 1; n <= maxN; n++) {
    if (t.equals(value)) out.push(n);
    t = t.mul(r);
  }
  return out;
}
