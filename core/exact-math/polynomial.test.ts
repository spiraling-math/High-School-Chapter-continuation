/**
 * Exact polynomial tests. Run:  node --test core/exact-math/polynomial.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { Poly, polyDisplay } from "./polynomial.ts";
import { Rational, rat } from "./rational.ts";

test("canonical form: trailing zeros stripped, zero polynomial is [0], degree reported", () => {
  const p = new Poly([1, 2, 0, 0]);
  assert.deepEqual(p.toJson(), { variable: "x", coefficients: [{ num: 1, den: 1 }, { num: 2, den: 1 }] });
  assert.equal(p.degree(), 1);
  assert.equal(new Poly([0, 0, 0]).degree(), 0);
  assert.ok(new Poly([]).isZero());
  assert.ok(Poly.const(3).isConstant());
});

test("arithmetic: add/sub/mul/scale/pow are exact and agree with hand expansion", () => {
  const f = Poly.linear(2, -3);          // 2x - 3
  const g = Poly.quadratic(1, 0, 1);     // x^2 + 1
  assert.equal(f.mul(f).display(), "4x^2 - 12x + 9");
  assert.equal(f.pow(2).display(), "4x^2 - 12x + 9");
  assert.equal(f.add(g).display(), "x^2 + 2x - 2");
  assert.equal(g.sub(f).display(), "x^2 - 2x + 4");
  assert.equal(f.scale(new Rational(1, 2)).display(), "x - 3/2");
  assert.equal(f.neg().display(), "-2x + 3");
});

test("compose: (g∘f)(x) = (2x-3)^2 + 1 = 4x^2 - 12x + 10 and (f∘g)(x) = 2x^2 - 1; eval by Horner", () => {
  const f = Poly.linear(2, -3), g = Poly.quadratic(1, 0, 1);
  const gf = g.compose(f), fg = f.compose(g);
  assert.equal(gf.display(), "4x^2 - 12x + 10");
  assert.equal(fg.display(), "2x^2 - 1");
  assert.equal(gf.eval(4).toString(), "26");
  assert.equal(fg.eval(new Rational(1, 2)).toString(), "-1/2");
  assert.ok(Poly.x().compose(f).equals(f), "x∘f = f");
  assert.ok(f.compose(Poly.x()).equals(f), "f∘x = f");
});

test("display contract (cross-language): signs, ±1 coefficients, bracketed fractions, zero", () => {
  assert.equal(Poly.linear(new Rational(1, 2), 9).display(), "(1/2)x + 9");
  assert.equal(Poly.linear(new Rational(-1, 2), 9).display(), "(-1/2)x + 9");
  assert.equal(Poly.linear(-1, 5).display(), "-x + 5");
  assert.equal(Poly.linear(1, -5).display(), "x - 5");
  assert.equal(Poly.quadratic(1, 0, -4).display(), "x^2 - 4");
  assert.equal(Poly.quadratic(-2, 3, 0).display(), "-2x^2 + 3x");
  assert.equal(Poly.quadratic(1, new Rational(-1, 3), new Rational(2, 3)).display(), "x^2 - (1/3)x + 2/3");
  assert.equal(new Poly([0]).display(), "0");
  assert.equal(polyDisplay([rat(7)]), "7");
  assert.equal(Poly.const(new Rational(-3, 4)).display(), "-3/4");
});

test("JSON round trip preserves the canonical vector", () => {
  const p = Poly.quadratic(new Rational(1, 3), -2, 5);
  assert.ok(Poly.fromJson(p.toJson()).equals(p));
});
