/**
 * Exact rational arithmetic.
 *
 * Mirrors Python's fractions.Fraction semantics for the operations the geometric
 * generator needs: always reduced to lowest terms with a positive denominator,
 * so `{num, den}` and the display string are identical to the oracle's output
 * for any value. Values are bounded by the generator's parameter caps, so plain
 * JS integers are exact here (no bigint required).
 */

function gcd(a: number, b: number): number {
  a = Math.abs(a);
  b = Math.abs(b);
  while (b) { [a, b] = [b, a % b]; }
  return a;
}

export class Rational {
  readonly num: number;
  readonly den: number;

  constructor(num: number, den = 1) {
    if (den === 0) throw new Error("Rational: zero denominator");
    if (!Number.isInteger(num) || !Number.isInteger(den)) throw new Error("Rational: non-integer components");
    if (den < 0) { num = -num; den = -den; }
    const g = gcd(num, den) || 1;
    this.num = num / g;
    this.den = den / g;
  }

  static from(value: number | Rational): Rational {
    return value instanceof Rational ? value : new Rational(value, 1);
  }

  add(o: Rational): Rational { return new Rational(this.num * o.den + o.num * this.den, this.den * o.den); }
  sub(o: Rational): Rational { return new Rational(this.num * o.den - o.num * this.den, this.den * o.den); }
  mul(o: Rational): Rational { return new Rational(this.num * o.num, this.den * o.den); }
  div(o: Rational): Rational {
    if (o.num === 0) throw new Error("Rational: division by zero");
    return new Rational(this.num * o.den, this.den * o.num);
  }
  neg(): Rational { return new Rational(-this.num, this.den); }
  abs(): Rational { return new Rational(Math.abs(this.num), this.den); }

  /** Integer power (exponent >= 0). */
  pow(k: number): Rational {
    if (!Number.isInteger(k) || k < 0) throw new Error("Rational.pow: exponent must be a non-negative integer");
    return new Rational(this.num ** k, this.den ** k);
  }

  equals(o: Rational): boolean { return this.num === o.num && this.den === o.den; }
  isInteger(): boolean { return this.den === 1; }
  isZero(): boolean { return this.num === 0; }
  /** Sign of (|this| - |other|) as -1/0/1, using cross-multiplication (exact). */
  cmpAbs(o: Rational): number {
    const a = Math.abs(this.num) * o.den;
    const b = Math.abs(o.num) * this.den;
    return a < b ? -1 : a > b ? 1 : 0;
  }

  toJSON(): { num: number; den: number } { return { num: this.num, den: this.den }; }
  toString(): string { return this.den === 1 ? String(this.num) : `${this.num}/${this.den}`; }
}

export function rat(num: number, den = 1): Rational { return new Rational(num, den); }
