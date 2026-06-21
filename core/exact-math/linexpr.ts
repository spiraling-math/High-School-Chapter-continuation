/**
 * Minimal linear-expression algebra over exact rationals.
 *
 * Represents `a·x + b` (degree ≤ 1 in a single variable) using the exact
 * `Rational` type. This is intentionally NOT a computer algebra system: only the
 * operations needed for verified linear-polynomial work are provided —
 * add / sub / scale (bracket expansion) / eval / normalize / solve. A higher
 * degree is not representable, so "is this genuinely linear?" is guaranteed by
 * construction.
 *
 * Byte-for-byte counterpart of oracle/spi_oracle/linexpr.py.
 */

import { Rational, rat } from "./rational.ts";

export class LinExpr {
  readonly a: Rational; // coefficient of x
  readonly b: Rational; // constant term

  constructor(a: Rational, b: Rational) {
    this.a = a;
    this.b = b;
  }

  /** Build from integers/rationals: coef(a, b) = a·x + b. */
  static coef(a: number | Rational, b: number | Rational): LinExpr {
    return new LinExpr(Rational.from(a), Rational.from(b));
  }

  add(o: LinExpr): LinExpr { return new LinExpr(this.a.add(o.a), this.b.add(o.b)); }
  sub(o: LinExpr): LinExpr { return new LinExpr(this.a.sub(o.a), this.b.sub(o.b)); }
  /** Multiply the whole expression by a scalar (used to expand k·(p·x + q)). */
  scale(k: Rational): LinExpr { return new LinExpr(this.a.mul(k), this.b.mul(k)); }
  /** Substitute a value for x. */
  eval(x: Rational): Rational { return this.a.mul(x).add(this.b); }
  isConstant(): boolean { return this.a.isZero(); }
}

/** Reduce `lhs = rhs` to `A·x + B = 0`. */
export function normalize(lhs: LinExpr, rhs: LinExpr): { A: Rational; B: Rational } {
  return { A: lhs.a.sub(rhs.a), B: lhs.b.sub(rhs.b) };
}

/**
 * Solve `lhs = rhs` for x. Requires a unique solution: throws if the reduced
 * coefficient A = 0 (no-solution or infinitely-many — both out of scope).
 */
export function solveLinear(lhs: LinExpr, rhs: LinExpr): Rational {
  const { A, B } = normalize(lhs, rhs);
  if (A.isZero()) throw new Error("not a unique-solution linear equation (A = 0)");
  return B.neg().div(A);
}

export function lin(a: number | Rational, b: number | Rational): LinExpr {
  return LinExpr.coef(a, b);
}

export { rat };
