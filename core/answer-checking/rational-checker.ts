/**
 * Exact-rational answer checker.
 *
 * Accepts equivalent forms of a canonical reduced rational {num, den}:
 *   - any equivalent fraction (e.g. 30/8 for 15/4) — always, unless disabled;
 *   - the integer form for integral values;
 *   - the terminating decimal — only when the item permits it (accepts.decimal);
 *   - the mixed-number form — only when enabled (accepts.mixed).
 *
 * Comparison is exact (via the Rational type); no floating point is used for the
 * decision once parsed.
 */

import { Rational } from "../exact-math/rational.ts";

export interface AcceptedForms { fraction?: boolean; decimal?: boolean; mixed?: boolean; }

/** Parse a student input string into a Rational, honouring which forms are accepted. */
export function parseRationalInput(input: string, accepts: AcceptedForms = {}): Rational | null {
  const s = input.trim();
  let m: RegExpExecArray | null;

  // Mixed number: "w n/d" (sign carried by the whole part), e.g. "3 3/4", "-1 1/2".
  if ((m = /^(-?\d+)\s+(\d+)\/(\d+)$/.exec(s))) {
    if (!accepts.mixed) return null;
    const whole = Number(m[1]), n = Number(m[2]), d = Number(m[3]);
    if (d === 0) return null;
    const sign = whole < 0 ? -1 : 1;
    return new Rational(sign * (Math.abs(whole) * d + n), d);
  }
  // Fraction: "a/b".
  if ((m = /^(-?\d+)\/(-?\d+)$/.exec(s))) {
    if (accepts.fraction === false) return null;
    const n = Number(m[1]), d = Number(m[2]);
    if (d === 0) return null;
    return new Rational(n, d);
  }
  // Integer.
  if (/^-?\d+$/.test(s)) return new Rational(Number(s), 1);
  // Terminating decimal: "a.b".
  if ((m = /^(-?)(\d+)\.(\d+)$/.exec(s))) {
    if (!accepts.decimal) return null;
    const sign = m[1] === "-" ? -1 : 1;
    const intDigits = m[2] ?? "", fracDigits = m[3] ?? "";
    const den = 10 ** fracDigits.length;
    return new Rational(sign * Number(intDigits + fracDigits), den);
  }
  return null;
}

/** True if `input` is an accepted equivalent of the canonical reduced rational. */
export function checkExactRational(input: string, canonical: { num: number; den: number }, accepts: AcceptedForms = {}): boolean {
  const opts: AcceptedForms = { fraction: accepts.fraction !== false, decimal: Boolean(accepts.decimal), mixed: Boolean(accepts.mixed) };
  const r = parseRationalInput(input, opts);
  if (!r) return false;
  return r.num === canonical.num && r.den === canonical.den;
}

/** A reduced rational terminates as a decimal iff its denominator has only 2s and 5s. */
export function terminates(den: number): boolean {
  let d = den;
  while (d % 2 === 0) d /= 2;
  while (d % 5 === 0) d /= 5;
  return d === 1;
}
