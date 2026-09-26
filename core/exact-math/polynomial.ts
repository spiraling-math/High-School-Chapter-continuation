/**
 * Exact univariate polynomial over rationals.
 *
 * Dense coefficient vector, ASCENDING degree, exact `Rational` entries, always canonical (trailing
 * zero coefficients stripped; the zero polynomial is `[0]`). Intentionally NOT a CAS: only the
 * operations the functions family needs — add / sub / neg / scale / mul / pow / compose / eval /
 * degree / equality / JSON encoding / plain-text display. No factoring, no rational functions, no
 * radicals.
 *
 * Byte-for-byte counterpart of oracle/spi_oracle/polynomial.py (the display strings are part of the
 * cross-language contract: `4x^2 - 12x + 10`, `(1/2)x + 9`, `-x + 5`, `0`).
 */

import { Rational, rat } from "./rational.ts";

export interface RatJson { num: number; den: number }
export interface PolyJson { variable: string; coefficients: RatJson[] }

/** Plain-text rational: `3`, `-3`, `3/4`, `-3/4` (sign on the numerator). */
export function ratDisplay(value: Rational | number): string {
  return Rational.from(value).toString();
}

export function ratJson(value: Rational | number): RatJson {
  return Rational.from(value).toJSON();
}

export function ratFromJson(d: RatJson): Rational {
  return new Rational(d.num, d.den);
}

export class Poly {
  /** Coefficients, ascending degree, canonical. */
  readonly c: readonly Rational[];

  constructor(coeffs: ReadonlyArray<Rational | number>) {
    const c = coeffs.map((v) => Rational.from(v));
    while (c.length > 1 && c[c.length - 1]!.isZero()) c.pop();
    if (c.length === 0) c.push(rat(0));
    this.c = c;
  }

  // --- constructors -------------------------------------------------------- //
  static const(v: Rational | number): Poly { return new Poly([v]); }
  static x(): Poly { return new Poly([0, 1]); }
  /** a·x + b */
  static linear(a: Rational | number, b: Rational | number): Poly { return new Poly([b, a]); }
  /** a·x² + b·x + c */
  static quadratic(a: Rational | number, b: Rational | number, c: Rational | number): Poly { return new Poly([c, b, a]); }
  static fromJson(d: PolyJson): Poly { return new Poly(d.coefficients.map(ratFromJson)); }

  // --- queries ------------------------------------------------------------- //
  /** Degree; the zero polynomial reports 0. */
  degree(): number { return this.c.length - 1; }
  isZero(): boolean { return this.c.length === 1 && this.c[0]!.isZero(); }
  isConstant(): boolean { return this.c.length === 1; }
  coef(k: number): Rational { return k < this.c.length ? this.c[k]! : rat(0); }
  equals(o: Poly): boolean {
    return this.c.length === o.c.length && this.c.every((v, i) => v.equals(o.c[i]!));
  }

  // --- arithmetic ---------------------------------------------------------- //
  add(o: Poly): Poly {
    const n = Math.max(this.c.length, o.c.length);
    const out: Rational[] = [];
    for (let i = 0; i < n; i++) out.push(this.coef(i).add(o.coef(i)));
    return new Poly(out);
  }
  neg(): Poly { return new Poly(this.c.map((v) => v.neg())); }
  sub(o: Poly): Poly { return this.add(o.neg()); }
  scale(k: Rational | number): Poly {
    const kf = Rational.from(k);
    return new Poly(this.c.map((v) => v.mul(kf)));
  }
  mul(o: Poly): Poly {
    const out: Rational[] = new Array<Rational>(this.c.length + o.c.length - 1).fill(rat(0));
    for (let i = 0; i < this.c.length; i++) {
      for (let j = 0; j < o.c.length; j++) out[i + j] = out[i + j]!.add(this.c[i]!.mul(o.c[j]!));
    }
    return new Poly(out);
  }
  pow(n: number): Poly {
    if (!Number.isInteger(n) || n < 0) throw new Error("Poly.pow: exponent must be a non-negative integer");
    let r = Poly.const(1);
    for (let i = 0; i < n; i++) r = r.mul(this);
    return r;
  }
  /** this(inner(x)) by Horner's scheme over polynomials. */
  compose(inner: Poly): Poly {
    let r = Poly.const(0);
    for (let i = this.c.length - 1; i >= 0; i--) r = r.mul(inner).add(Poly.const(this.c[i]!));
    return r;
  }
  /** Horner evaluation at an exact rational. */
  eval(x: Rational | number): Rational {
    const xf = Rational.from(x);
    let r = rat(0);
    for (let i = this.c.length - 1; i >= 0; i--) r = r.mul(xf).add(this.c[i]!);
    return r;
  }

  // --- encoding ------------------------------------------------------------ //
  toJson(variable = "x"): PolyJson {
    return { variable, coefficients: this.c.map((v) => v.toJSON()) };
  }
  display(variable = "x"): string { return polyDisplay(this.c, variable); }
}

function varPower(variable: string, d: number): string {
  return d === 1 ? variable : `${variable}^${d}`;
}

/**
 * Plain-text display, descending degree, zero terms omitted, ±1 coefficients implicit on variable
 * terms, fractional coefficients bracketed: `4x^2 - 12x + 10`, `(1/2)x + 9`, `(-1/2)x + 9`,
 * `-x + 5`, `x^2 - 4`, `0`.
 */
export function polyDisplay(coeffs: readonly Rational[], variable = "x"): string {
  const terms: string[] = [];
  for (let d = coeffs.length - 1; d >= 0; d--) {
    const c = coeffs[d]!;
    if (c.isZero()) continue;
    const leading = terms.length === 0;
    let body: string;
    if (d === 0) {
      body = leading ? ratDisplay(c) : ratDisplay(c.abs());
    } else {
      const a = leading ? c : c.abs();
      const v = varPower(variable, d);
      if (a.equals(rat(1))) body = v;
      else if (a.equals(rat(-1))) body = "-" + v;
      else if (a.den === 1) body = `${a.num}${v}`;
      else body = `(${ratDisplay(a)})${v}`;
    }
    terms.push(leading ? body : (c.num < 0 ? " - " : " + ") + body);
  }
  return terms.length ? terms.join("") : "0";
}
