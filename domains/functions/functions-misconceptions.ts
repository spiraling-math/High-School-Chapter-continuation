/**
 * MISC.FUNC.* misconception registry for gen.functions.foundations (production TypeScript).
 *
 * Byte-for-byte mirror of oracle/spi_oracle/functions_misconceptions.py. Every rule is an INDEPENDENTLY
 * recomputable wrong value over the item's rule record(s): a Rational (numeric tasks), a Poly or a
 * `{kind: "reciprocal-of", poly}` marker (expression tasks), or a real-subset descriptor (domain / range
 * tasks) — or `null` when it does not apply. `observableError` (the serialized distractor rationale) and the
 * item-specific `feedback(ctx)` (student-facing) contain NO internal placeholder symbols. `feedback(ctx)` is
 * defined only where `wrong(ctx)` is not null.
 *
 * The three identify_function records describe the structure of a wrongly chosen relation; their wrong
 * values are built by the generator's relation draw (`wrong` returns null).
 */

import { Rational, rat } from "../../core/exact-math/rational.ts";
import { Poly, ratDisplay } from "../../core/exact-math/polynomial.ts";
import type { Interval } from "../../core/answer-checking/interval-checker.ts";
import * as C from "./functions-core.ts";
import type { Rule } from "./functions-core.ts";

export interface ReciprocalOf { kind: "reciprocal-of"; poly: Poly }
export type WrongValue = Rational | Poly | ReciprocalOf | Interval;

/** The misconception context (mirrors the Python `ctx` dict; absent fields are undefined). */
export interface Ctx {
  task: string;
  name?: string;
  rule?: Rule;
  p?: Rational;
  target?: Rational;
  x0?: Rational | null;
  restricted?: { p: Rational; q: Rational } | null;
  outer?: Rule;
  inner?: Rule;
  outer_name?: string;
  inner_name?: string;
  A?: Rational; B?: Rational; m?: Rational; c?: Rational;
  comp_p?: Rational; comp_q?: Rational;
  a?: Rational; b?: Rational;
  form?: string;
  k?: Rational;
  side?: string;
}

export interface Misconception {
  wrong: (ctx: Ctx) => WrongValue | null;
  feedback: (ctx: Ctx) => string;
  title: string;
  description: string;
  observableError: string;
  expression: string;
}

const n = ratDisplay;
const one = rat(1), zero = rat(0), two = rat(2);
const R = (ctx: Ctx): Rule => ctx.rule!;
const eq = (a: Rational, b: Rational | number): boolean => a.equals(Rational.from(b));
const nz = (a: Rational): boolean => !a.isZero();
const sq = (ctx: Ctx): Rational | null => C.sqrtExact(C.radicand(R(ctx), ctx.p!));
const rec = (poly: Poly): ReciprocalOf => ({ kind: "reciprocal-of", poly });
const fname = (ctx: Ctx): string => ctx.name ?? "f";

/** Dispatch a feedback builder on the rule kind; builders are thunks so only the matching one runs. */
function fbEval(ctx: Ctx, byKind: Record<string, () => string>): string {
  const make = byKind[R(ctx).kind] ?? byKind["*"];
  return make ? make() : "";
}

// --- evaluate_function --------------------------------------------------------------------- //
const evalForgotMultiply = (ctx: Ctx): WrongValue | null => (R(ctx).kind === "linear" ? R(ctx).a!.add(ctx.p!).add(R(ctx).b!) : null);
const evalDropConstant = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), p = ctx.p!;
  if (r.kind === "linear") return nz(r.b!) ? r.a!.mul(p) : null;
  if (r.kind === "quadratic") return nz(r.c!) ? r.a!.mul(p).mul(p).add(r.b!.mul(p)) : null;
  if (r.kind === "reciprocal") return nz(r.v!) && !p.equals(r.h!) ? r.k!.div(p.sub(r.h!)) : null;
  const t = sq(ctx);
  return t !== null && nz(r.v!) ? t : null;
};
const evalSignOfInput = (ctx: Ctx): WrongValue | null => (C.isNeg(ctx.p!) ? C.evalRule(R(ctx), ctx.p!.neg()) : null);
const evalConstantSignFlipped = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), p = ctx.p!;
  if (r.kind === "linear") return nz(r.b!) ? r.a!.mul(p).sub(r.b!) : null;
  if (r.kind === "quadratic") return nz(r.c!) ? r.a!.mul(p).mul(p).add(r.b!.mul(p)).sub(r.c!) : null;
  return null;
};
const evalSquareNegative = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), p = ctx.p!;
  if (r.kind !== "quadratic" || !C.isNeg(p)) return null;
  return r.a!.neg().mul(p).mul(p).add(r.b!.mul(p)).add(r.c!);
};
const evalSquareCoefficient = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), p = ctx.p!;
  if (r.kind !== "quadratic" || eq(r.a!, 1)) return null;
  const ap = r.a!.mul(p);
  return ap.mul(ap).add(r.b!.mul(p)).add(r.c!);
};
const evalSquareAsDouble = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), p = ctx.p!;
  if (r.kind !== "quadratic") return null;
  return two.mul(r.a!).mul(p).add(r.b!.mul(p)).add(r.c!);
};
const evalDenominatorNotGrouped = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), p = ctx.p!;
  if (r.kind !== "reciprocal" || p.isZero()) return null;
  return r.k!.div(p).sub(r.h!).add(r.v!);
};
const evalReciprocalInverted = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), p = ctx.p!;
  if (r.kind !== "reciprocal") return null;
  return p.sub(r.h!).div(r.k!).add(r.v!);
};
const evalRootIgnored = (ctx: Ctx): WrongValue | null => (R(ctx).kind === "sqrt" ? C.radicand(R(ctx), ctx.p!).add(R(ctx).v!) : null);
const evalHalveInsteadOfRoot = (ctx: Ctx): WrongValue | null => (R(ctx).kind === "sqrt" ? C.radicand(R(ctx), ctx.p!).div(two).add(R(ctx).v!) : null);
const evalNegativeRoot = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind !== "sqrt") return null;
  const t = sq(ctx);
  return t !== null && C.isPos(t) ? t.neg().add(r.v!) : null;
};

// --- solve_for_input ------------------------------------------------------------------------ //
const solveEvaluatesInstead = (ctx: Ctx): WrongValue | null => (R(ctx).kind === "sqrt" ? null : C.evalRule(R(ctx), ctx.target!));
const solveWrongInverse = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), k = ctx.target!;
  if (r.kind === "linear") return nz(r.b!) ? k.add(r.b!).div(r.a!) : null;
  if (r.kind === "sqrt") { const t = k.sub(r.v!); return nz(r.b!) ? t.mul(t).add(r.b!).div(r.a!) : null; }
  return null;
};
const solveStopsBeforeDividing = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), k = ctx.target!;
  if (r.kind !== "linear" || eq(r.a!.abs(), 1)) return null;
  return k.sub(r.b!);
};
const solveDivideByConstant = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), k = ctx.target!;
  if (r.kind !== "linear" || r.b!.isZero() || r.b!.equals(r.a!)) return null;
  return k.sub(r.b!).div(r.b!);
};
const solveReciprocalNotInverted = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), k = ctx.target!;
  if (r.kind !== "reciprocal") return null;
  return r.h!.add(k.sub(r.v!).div(r.k!));
};
const solvePoleSign = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), k = ctx.target!;
  if (r.kind !== "reciprocal" || r.h!.isZero()) return null;
  return r.k!.div(k.sub(r.v!)).sub(r.h!);
};
const solveIgnoresShift = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), k = ctx.target!;
  if (r.kind !== "reciprocal" || r.v!.isZero() || k.isZero()) return null;
  return r.h!.add(r.k!.div(k));
};
const solveForgotToSquare = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), k = ctx.target!;
  if (r.kind !== "sqrt") return null;
  return k.sub(r.v!).sub(r.b!).div(r.a!);
};
const solveSquareBeforeIsolating = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx), k = ctx.target!;
  if (r.kind !== "sqrt" || r.v!.isZero()) return null;
  return k.mul(k).sub(r.v!).sub(r.b!).div(r.a!);
};

// --- domain_of_function --------------------------------------------------------------------- //
const domainAllReals = (ctx: Ctx): WrongValue | null => (!C.isPolynomialRule(R(ctx)) ? C.reals() : null);
const domainDirectionFlipped = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind !== "sqrt") return null;
  const d = C.domainOf(r) as Extract<Interval, { kind: "ray" }>;
  return C.ray("x", d.endpoint, true, d.direction === "ge" ? "le" : "ge");
};
const domainStrictEndpoint = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind !== "sqrt") return null;
  const d = C.domainOf(r) as Extract<Interval, { kind: "ray" }>;
  return C.ray("x", d.endpoint, false, d.direction);
};
const domainEndpointSign = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind !== "sqrt" || r.b!.isZero()) return null;
  const d = C.domainOf(r) as Extract<Interval, { kind: "ray" }>;
  return C.ray("x", r.b!.div(r.a!), true, d.direction);
};
const domainAsExcludedPoint = (ctx: Ctx): WrongValue | null => (R(ctx).kind === "sqrt" ? C.realsExcept("x", [R(ctx).b!.neg().div(R(ctx).a!)]) : null);
const domainPoleSign = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind !== "reciprocal" || r.h!.isZero()) return null;
  return C.realsExcept("x", [r.h!.neg()]);
};
const domainExcludesZero = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind === "reciprocal") return nz(r.h!) ? C.realsExcept("x", [zero]) : null;
  if (C.isPolynomialRule(r)) return C.realsExcept("x", [zero]);
  return null;
};
const domainPoleAsInequality = (ctx: Ctx): WrongValue | null => (R(ctx).kind === "reciprocal" ? C.ray("x", R(ctx).h!, false, "ge") : null);
const domainNonnegativeOnly = (ctx: Ctx): WrongValue | null => (C.isPolynomialRule(R(ctx)) ? C.ray("x", zero, true, "ge") : null);
const domainExcludesConstant = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (!C.isPolynomialRule(r)) return null;
  const c = r.kind === "linear" ? r.b! : r.c!;
  return nz(c) ? C.realsExcept("x", [c]) : null;
};

// --- range_of_function ---------------------------------------------------------------------- //
const trueRange = (ctx: Ctx): Interval => C.rangeOf(R(ctx), ctx.restricted ?? null);
type Ray = Extract<Interval, { kind: "ray" }>;
type Bounded = Extract<Interval, { kind: "bounded" }>;
const rangeAllReals = (_ctx: Ctx): WrongValue | null => C.reals();
const rangeDirectionFlipped = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind !== "quadratic" && r.kind !== "sqrt") return null;
  const t = trueRange(ctx) as Ray;
  return C.ray("y", t.endpoint, true, t.direction === "ge" ? "le" : "ge");
};
const rangeUsesVertexX = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind !== "quadratic") return null;
  const hx = C.vertexX(r);
  const t = trueRange(ctx) as Ray;
  return hx.equals(t.endpoint) ? null : C.ray("y", hx, true, t.direction);
};
const rangeStrictAtBound = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind !== "quadratic" && r.kind !== "sqrt") return null;
  const t = trueRange(ctx) as Ray;
  return C.ray("y", t.endpoint, false, t.direction);
};
const rangeUsesConstantTerm = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind !== "quadratic") return null;
  const t = trueRange(ctx) as Ray;
  return r.c!.equals(t.endpoint) ? null : C.ray("y", r.c!, true, t.direction);
};
const rangeIgnoresShift = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind === "sqrt") return nz(r.v!) ? C.ray("y", zero, true, "ge") : null;
  if (r.kind === "reciprocal") return nz(r.v!) ? C.realsExcept("y", [zero]) : null;
  return null;
};
const domainRangeConfused = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind === "sqrt") { const d = C.domainOf(r) as Ray; return C.ray("y", d.endpoint, true, d.direction); }
  if (r.kind === "reciprocal") return r.h!.equals(r.v!) ? null : C.realsExcept("y", [r.h!]);
  if (r.kind === "linear" && ctx.restricted) {
    const { p, q } = ctx.restricted;
    const t = trueRange(ctx) as Bounded;
    return p.equals(t.lo) && q.equals(t.hi) ? null : C.bounded("y", p, q, true, true);
  }
  return null;
};
const rangePoleAsInequality = (ctx: Ctx): WrongValue | null => (R(ctx).kind === "reciprocal" ? C.ray("y", R(ctx).v!, false, "ge") : null);
const rangeOnlyLowerBound = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind !== "linear" || !ctx.restricted) return null;
  const t = trueRange(ctx) as Bounded;
  return C.ray("y", t.lo, true, "ge");
};
const rangeStrictEndpoints = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.kind !== "linear" || !ctx.restricted) return null;
  const t = trueRange(ctx) as Bounded;
  return C.bounded("y", t.lo, t.hi, false, false);
};

// --- composite ------------------------------------------------------------------------------ //
const po = (ctx: Ctx): [Poly, Poly] => [C.rulePoly(ctx.outer!), C.rulePoly(ctx.inner!)];
const compOrderReversed = (ctx: Ctx): WrongValue | null => {
  const [outer, inner] = po(ctx);
  if (ctx.task === "composite_value") return inner.eval(outer.eval(ctx.p!));
  const rev = inner.compose(outer);
  return rev.equals(outer.compose(inner)) ? null : rev;
};
const compAsProduct = (ctx: Ctx): WrongValue | null => {
  const [outer, inner] = po(ctx);
  return ctx.task === "composite_value" ? outer.eval(ctx.p!).mul(inner.eval(ctx.p!)) : outer.mul(inner);
};
const compAsSum = (ctx: Ctx): WrongValue | null => {
  const [outer, inner] = po(ctx);
  return ctx.task === "composite_value" ? outer.eval(ctx.p!).add(inner.eval(ctx.p!)) : outer.add(inner);
};
const compInnerOnly = (ctx: Ctx): WrongValue | null => (ctx.task === "composite_value" ? po(ctx)[1].eval(ctx.p!) : null);
const compOuterAtInput = (ctx: Ctx): WrongValue | null => (ctx.task === "composite_value" ? po(ctx)[0].eval(ctx.p!) : null);
const compSquareNoCrossTerm = (ctx: Ctx): WrongValue | null => {
  if (ctx.task !== "composite_expression") return null;
  const o = ctx.outer!, i = ctx.inner!;
  if (o.kind !== "quadratic" || i.kind !== "linear") return null;
  const m = i.a!, nn = i.b!;
  if (m.isZero() || nn.isZero()) return null;
  const sqp = Poly.quadratic(m.mul(m), zero, nn.mul(nn));
  return sqp.scale(o.a!).add(Poly.linear(m, nn).scale(o.b!)).add(Poly.const(o.c!));
};

// --- function_from_composite ---------------------------------------------------------------- //
const ffcIgnoresInner = (ctx: Ctx): WrongValue | null => Poly.linear(ctx.comp_p!, ctx.comp_q!);
const ffcShiftNotInverted = (ctx: Ctx): WrongValue | null => {
  const p = ctx.comp_p!, q = ctx.comp_q!, m = ctx.m!, c = ctx.c!;
  return Poly.linear(p.div(m), p.mul(c).div(m).add(q));
};
const ffcScaleNotInverted = (ctx: Ctx): WrongValue | null => {
  const p = ctx.comp_p!, q = ctx.comp_q!, m = ctx.m!, c = ctx.c!;
  if (eq(m, 1)) return null;
  return Poly.linear(p.mul(m), p.mul(m).mul(c).neg().add(q));
};
const ffcComposesInstead = (ctx: Ctx): WrongValue | null => {
  const p = ctx.comp_p!, q = ctx.comp_q!, m = ctx.m!, c = ctx.c!;
  return Poly.linear(p.mul(m), p.mul(c).add(q));
};

// --- inverse -------------------------------------------------------------------------------- //
const invAsReciprocal = (ctx: Ctx): WrongValue | null => (ctx.task === "inverse_expression" ? rec(Poly.linear(ctx.a!, ctx.b!)) : null);
const invUndoOrder = (ctx: Ctx): WrongValue | null => {
  const a = ctx.a!, b = ctx.b!;
  if (b.isZero() || eq(a, 1)) return null;
  if (ctx.task === "inverse_expression") return Poly.linear(one.div(a), b.neg());
  if (ctx.form === "inverse_at") return ctx.k!.div(a).sub(b);
  return null;
};
const invSignError = (ctx: Ctx): WrongValue | null => {
  const a = ctx.a!, b = ctx.b!;
  if (b.isZero()) return null;
  if (ctx.task === "inverse_expression") return Poly.linear(one.div(a), b.div(a));
  if (ctx.form === "inverse_at") return ctx.k!.add(b).div(a);
  return a.mul(ctx.x0!).sub(b);
};
const invNegatesOnly = (ctx: Ctx): WrongValue | null => (ctx.task !== "inverse_expression" || ctx.b!.isZero() ? null : Poly.linear(ctx.a!, ctx.b!.neg()));
const invSwapsRoles = (ctx: Ctx): WrongValue | null => (ctx.task !== "inverse_expression" || ctx.b!.isZero() ? null : Poly.linear(one.div(ctx.b!), ctx.a!.neg().div(ctx.b!)));
const invvalForward = (ctx: Ctx): WrongValue | null => (ctx.form !== "inverse_at" ? null : ctx.a!.mul(ctx.k!).add(ctx.b!));
const invvalReciprocal = (ctx: Ctx): WrongValue | null => {
  const x = ctx.form === "inverse_at" ? ctx.k! : ctx.x0!;
  const fx = ctx.a!.mul(x).add(ctx.b!);
  return fx.isZero() ? null : one.div(fx);
};
const invvalAppliesInverseAgain = (ctx: Ctx): WrongValue | null => (ctx.form !== "solve_inverse_equation" ? null : ctx.x0!.sub(ctx.b!).div(ctx.a!));
const invvalIdentity = (ctx: Ctx): WrongValue | null => (ctx.form !== "solve_inverse_equation" ? null : ctx.x0!);

// --- one_to_one_restriction ----------------------------------------------------------------- //
const vertexXMissingHalf = (ctx: Ctx): WrongValue | null => R(ctx).b!.neg().div(R(ctx).a!);
const vertexXSign = (ctx: Ctx): WrongValue | null => R(ctx).b!.div(two.mul(R(ctx).a!));
const vertexYForX = (ctx: Ctx): WrongValue | null => {
  const hy = C.vertexY(R(ctx));
  return hy.equals(C.vertexX(R(ctx))) ? null : hy;
};
const restrictionZero = (_ctx: Ctx): WrongValue | null => zero;
const vertexXUsesC = (ctx: Ctx): WrongValue | null => {
  const r = R(ctx);
  if (r.c!.isZero() || r.c!.equals(r.b!)) return null;
  return r.c!.neg().div(two.mul(r.a!));
};

function entry(wrong: (ctx: Ctx) => WrongValue | null, feedback: (ctx: Ctx) => string, title: string, description: string,
               observableError: string, expression: string): Misconception {
  return { wrong, feedback, title, description, observableError, expression };
}

export const MISCONCEPTIONS: Record<string, Misconception> = {
  // --- identify_function (structural; built by the relation draw) ---------------------------- //
  "MISC.FUNC.MANY_TO_ONE_REJECTED": entry(() => null,
    () => "Two different inputs may share the same output. A relation fails to be a function only when ONE input has two different outputs.",
    "Rejects a many-to-one relation", "Believes a relation with a repeated output cannot be a function.",
    "Chose a relation in which two inputs share an output.", "repeated output -> 'not a function'"),
  "MISC.FUNC.CONSTANT_REJECTED": entry(() => null,
    () => "A constant relation sends every input to the same output; each input still has exactly one output, so it is a function.",
    "Rejects a constant relation", "Believes a relation whose outputs are all equal cannot be a function.",
    "Chose a relation whose outputs are all equal.", "all outputs equal -> 'not a function'"),
  "MISC.FUNC.PATTERN_REQUIRED": entry(() => null,
    () => "A function does not need a formula or a visible pattern. Check only that no input appears twice with different outputs.",
    "Requires a pattern", "Believes a relation must follow a formula or an ordered pattern to be a function.",
    "Chose a relation with no visible pattern.", "no pattern -> 'not a function'"),

  // --- evaluate_function --------------------------------------------------------------------- //
  "MISC.FUNC.EVAL_FORGOT_MULTIPLY": entry(evalForgotMultiply,
    (ctx) => `${n(R(ctx).a!)}x means ${n(R(ctx).a!)} multiplied by x, so substitute x = ${n(ctx.p!)} and multiply: ${n(R(ctx).a!)} × (${n(ctx.p!)}).`,
    "Adds the coefficient instead of multiplying", "Reads ax as a + x when substituting.",
    "Added the coefficient to the input instead of multiplying.", "a + p + b"),
  "MISC.FUNC.EVAL_DROP_CONSTANT": entry(evalDropConstant,
    (ctx) => fbEval(ctx, { linear: () => `After multiplying, remember the constant term ${n(R(ctx).b!)}.`,
      quadratic: () => `After the x^2 and x terms, remember the constant term ${n(R(ctx).c!)}.`,
      reciprocal: () => `After the fraction, remember to add the constant ${n(R(ctx).v!)}.`,
      sqrt: () => `After the square root, remember to add the constant ${n(R(ctx).v!)}.` }),
    "Drops the constant term", "Evaluates the variable part of the rule and forgets the constant term.",
    "Left out the constant term of the rule.", "rule without its constant"),
  "MISC.FUNC.EVAL_SIGN_OF_INPUT": entry(evalSignOfInput,
    (ctx) => `The input is ${n(ctx.p!)}, not ${n(ctx.p!.neg())}. Substitute the negative value in brackets and keep its sign.`,
    "Drops the sign of a negative input", "Substitutes |x| instead of a negative input.",
    "Substituted the positive value instead of the negative input.", "f(|p|)"),
  "MISC.FUNC.EVAL_CONSTANT_SIGN_FLIPPED": entry(evalConstantSignFlipped,
    () => "Keep the sign of the constant term exactly as it appears in the rule.",
    "Flips the sign of the constant", "Subtracts the constant that should be added (or vice versa).",
    "Used the opposite sign on the constant term.", "a p - b  /  a p^2 + b p - c"),
  "MISC.FUNC.EVAL_SQUARE_NEGATIVE": entry(evalSquareNegative,
    (ctx) => `(${n(ctx.p!)})^2 = ${n(ctx.p!.mul(ctx.p!))}: squaring a negative number gives a positive result.`,
    "Squares a negative input to a negative", "Computes (-p)^2 as -p^2.",
    "Treated the square of a negative input as negative.", "-a p^2 + b p + c"),
  "MISC.FUNC.EVAL_SQUARE_COEFFICIENT": entry(evalSquareCoefficient,
    (ctx) => `${n(R(ctx).a!)}x^2 squares only x, not the coefficient: compute x^2 first, then multiply by ${n(R(ctx).a!)}.`,
    "Squares the coefficient as well", "Computes a x^2 as (a x)^2.",
    "Squared the coefficient together with the input.", "(a p)^2 + b p + c"),
  "MISC.FUNC.EVAL_SQUARE_AS_DOUBLE": entry(evalSquareAsDouble,
    (ctx) => `x^2 means x × x, not 2x: (${n(ctx.p!)})^2 = ${n(ctx.p!.mul(ctx.p!))}.`,
    "Treats x^2 as 2x", "Doubles the input instead of squaring it.",
    "Doubled the input instead of squaring it.", "2 a p + b p + c"),
  "MISC.FUNC.EVAL_DENOMINATOR_NOT_GROUPED": entry(evalDenominatorNotGrouped,
    (ctx) => `The whole expression ${C.denominatorText(R(ctx).h!)} is the denominator: evaluate it first, then divide.`,
    "Ungroups the denominator", "Divides by x alone and treats the rest of the denominator as a separate term.",
    "Divided by x alone instead of by the whole denominator.", "k/p - h + v"),
  "MISC.FUNC.EVAL_RECIPROCAL_INVERTED": entry(evalReciprocalInverted,
    (ctx) => `The numerator is ${n(R(ctx).k!)} and the denominator is ${C.denominatorText(R(ctx).h!)}; do not turn the fraction upside down.`,
    "Inverts the fraction", "Divides the denominator by the numerator.",
    "Inverted the fraction when evaluating.", "(p - h)/k + v"),
  "MISC.FUNC.EVAL_ROOT_IGNORED": entry(evalRootIgnored,
    (ctx) => `Evaluate the expression under the root, ${C.radicandText(R(ctx))}, and then take its square root.`,
    "Ignores the square root", "Evaluates the radicand and forgets to take the root.",
    "Did not take the square root.", "a p + b + v"),
  "MISC.FUNC.EVAL_HALVE_INSTEAD_OF_ROOT": entry(evalHalveInsteadOfRoot,
    () => "A square root is not the same as halving: find the number whose square is the radicand.",
    "Halves instead of rooting", "Divides the radicand by 2 instead of taking its square root.",
    "Halved the radicand instead of taking its square root.", "(a p + b)/2 + v"),
  "MISC.FUNC.EVAL_NEGATIVE_ROOT": entry(evalNegativeRoot,
    () => "The square-root symbol denotes the non-negative root, so take the positive value.",
    "Takes the negative root", "Uses the negative square root for the radical symbol.",
    "Used the negative square root.", "-sqrt(a p + b) + v"),

  // --- solve_for_input ----------------------------------------------------------------------- //
  "MISC.FUNC.SOLVE_EVALUATES_INSTEAD": entry(solveEvaluatesInstead,
    (ctx) => `${fname(ctx)}(x) = ${n(ctx.target!)} asks for the INPUT x whose output is ${n(ctx.target!)}; do not substitute ${n(ctx.target!)} into the rule.`,
    "Evaluates instead of solving", "Substitutes the given output as if it were the input.",
    "Substituted the output value into the rule instead of solving for the input.", "f(k)"),
  "MISC.FUNC.SOLVE_WRONG_INVERSE": entry(solveWrongInverse,
    () => "Undo the constant with the inverse operation: a constant that is added must be subtracted from both sides (and vice versa).",
    "Wrong inverse operation on the constant", "Adds the constant instead of subtracting it when isolating the variable term.",
    "Used the wrong inverse operation on the constant.", "(k + b)/a"),
  "MISC.FUNC.SOLVE_STOPS_BEFORE_DIVIDING": entry(solveStopsBeforeDividing,
    (ctx) => `After isolating the x term, divide both sides by the coefficient ${n(R(ctx).a!)}.`,
    "Stops before dividing by the coefficient", "Reports the isolated variable term as the variable.",
    "Isolated the variable term but did not divide by its coefficient.", "k - b"),
  "MISC.FUNC.SOLVE_DIVIDE_BY_CONSTANT": entry(solveDivideByConstant,
    (ctx) => `Divide by the coefficient of x, ${n(R(ctx).a!)}, not by the constant ${n(R(ctx).b!)}.`,
    "Divides by the constant", "Divides by the constant term instead of the coefficient of x.",
    "Divided by the constant term instead of by the coefficient of x.", "(k - b)/b"),
  "MISC.FUNC.SOLVE_RECIPROCAL_NOT_INVERTED": entry(solveReciprocalNotInverted,
    (ctx) => (!R(ctx).h!.isZero()
      ? `To undo the fraction, divide ${n(R(ctx).k!)} by the isolated value: x - ${n(R(ctx).h!)} = ${n(R(ctx).k!)} ÷ (value).`
      : `To undo the fraction, divide ${n(R(ctx).k!)} by the isolated value.`),
    "Does not invert the reciprocal", "Multiplies by the numerator instead of dividing the numerator by the isolated value.",
    "Treated the reciprocal like a linear coefficient.", "h + (k - v)/k0"),
  "MISC.FUNC.SOLVE_POLE_SIGN": entry(solvePoleSign,
    (ctx) => `The denominator is ${C.denominatorText(R(ctx).h!)}; after finding its value, solve for x with the correct sign of ${n(R(ctx).h!)}.`,
    "Sign error at the pole", "Subtracts the shift of the denominator instead of adding it back.",
    "Used the wrong sign when undoing the shift inside the denominator.", "k0/(k - v) - h"),
  "MISC.FUNC.SOLVE_IGNORES_SHIFT": entry(solveIgnoresShift,
    (ctx) => `First subtract the constant ${n(R(ctx).v!)} from both sides, then deal with the fraction.`,
    "Ignores the vertical shift", "Does not remove the added constant before inverting the fraction.",
    "Did not subtract the constant before undoing the fraction.", "h + k0/k"),
  "MISC.FUNC.SOLVE_FORGOT_TO_SQUARE": entry(solveForgotToSquare,
    () => "To undo a square root, square both sides once the root is isolated.",
    "Forgets to square", "Removes the root without squaring the other side.",
    "Did not square both sides to remove the root.", "(k - v - b)/a"),
  "MISC.FUNC.SOLVE_SQUARE_BEFORE_ISOLATING": entry(solveSquareBeforeIsolating,
    (ctx) => `Isolate the square root first (subtract ${n(R(ctx).v!)}), and only then square both sides.`,
    "Squares before isolating the root", "Squares the whole output before removing the added constant.",
    "Squared before isolating the square root.", "(k^2 - v - b)/a"),

  // --- domain_of_function -------------------------------------------------------------------- //
  "MISC.FUNC.DOMAIN_ALL_REALS": entry(domainAllReals,
    (ctx) => fbEval(ctx, { sqrt: () => "A square root is only defined when the expression under it is at least 0.",
      reciprocal: () => "A fraction is undefined when its denominator is 0; that input must be excluded." }),
    "Domain is always all reals", "Ignores the restriction imposed by a root or a denominator.",
    "Gave all real numbers although the rule has a restriction.", "R"),
  "MISC.FUNC.DOMAIN_DIRECTION_FLIPPED": entry(domainDirectionFlipped,
    () => "Solve the inequality carefully: dividing by a negative number reverses the inequality sign.",
    "Inequality direction flipped", "Reverses (or fails to reverse) the inequality when solving the radicand condition.",
    "Solved the radicand inequality in the wrong direction.", "opposite ray"),
  "MISC.FUNC.DOMAIN_STRICT_ENDPOINT": entry(domainStrictEndpoint,
    () => "The square root of 0 is defined (it equals 0), so the endpoint belongs to the domain.",
    "Excludes the endpoint", "Uses a strict inequality, excluding the input where the radicand is 0.",
    "Excluded the endpoint where the radicand is zero.", "strict ray"),
  "MISC.FUNC.DOMAIN_ENDPOINT_SIGN": entry(domainEndpointSign,
    (ctx) => `Solve ${C.radicandText(R(ctx))} >= 0 step by step; watch the sign when moving the constant across.`,
    "Sign error in the endpoint", "Solves the radicand inequality with a sign slip in the constant.",
    "Made a sign error solving for the boundary input.", "x >= b/a"),
  "MISC.FUNC.DOMAIN_AS_EXCLUDED_POINT": entry(domainAsExcludedPoint,
    () => "A square root needs the whole radicand to be non-negative, not merely non-zero: the answer is an inequality, not a single excluded value.",
    "Treats the root like a denominator", "Excludes the single input where the radicand is 0 instead of requiring it to be non-negative.",
    "Excluded one point instead of solving the inequality.", "x != -b/a"),
  "MISC.FUNC.DOMAIN_POLE_SIGN": entry(domainPoleSign,
    (ctx) => `The denominator ${C.denominatorText(R(ctx).h!)} is zero when x = ${n(R(ctx).h!)}.`,
    "Sign error at the pole", "Excludes the negative of the pole.",
    "Excluded the input with the wrong sign.", "x != -h"),
  "MISC.FUNC.DOMAIN_EXCLUDES_ZERO": entry(domainExcludesZero,
    (ctx) => fbEval(ctx, { reciprocal: () => `The input to exclude is the one that makes the denominator 0: ${C.denominatorText(R(ctx).h!)} = 0.`,
      "*": () => "A polynomial rule is defined for every real number, including 0." }),
    "Excludes zero by habit", "Excludes x = 0 rather than the input that actually breaks the rule.",
    "Excluded zero instead of the actual restriction.", "x != 0"),
  "MISC.FUNC.DOMAIN_POLE_AS_INEQUALITY": entry(domainPoleAsInequality,
    () => "A denominator only needs to be non-zero, so exclude one value; an inequality would remove too much.",
    "Turns the pole into an inequality", "Writes an inequality instead of excluding the single undefined input.",
    "Wrote an inequality instead of excluding one value.", "x > h"),
  "MISC.FUNC.DOMAIN_NONNEGATIVE_ONLY": entry(domainNonnegativeOnly,
    () => "Negative inputs are allowed: a polynomial can be evaluated at any real number.",
    "Non-negative inputs only", "Restricts a polynomial rule to x >= 0.",
    "Restricted the domain to non-negative inputs without reason.", "x >= 0"),
  "MISC.FUNC.DOMAIN_EXCLUDES_CONSTANT": entry(domainExcludesConstant,
    () => "The constant term of a polynomial does not restrict the inputs; every real number is allowed.",
    "Excludes the constant term", "Excludes the constant of the rule as if it were a pole.",
    "Excluded the value of the constant term.", "x != c"),

  // --- range_of_function --------------------------------------------------------------------- //
  "MISC.FUNC.RANGE_ALL_REALS": entry(rangeAllReals,
    (ctx) => fbEval(ctx, { quadratic: () => "A quadratic has a minimum or maximum value at its vertex, so its outputs are bounded on one side.",
      sqrt: () => "A square root is never negative, so the outputs are bounded below.",
      reciprocal: () => "A fraction with a constant numerator can never be 0, so one output value is missed.",
      linear: () => "On a restricted domain the outputs are bounded by the images of the endpoints." }),
    "Range is always all reals", "Ignores the bound imposed by the shape of the graph.",
    "Gave all real numbers although the outputs are bounded.", "R"),
  "MISC.FUNC.RANGE_DIRECTION_FLIPPED": entry(rangeDirectionFlipped,
    (ctx) => fbEval(ctx, { quadratic: () => `The coefficient of x^2 is ${n(R(ctx).a!)}: ${C.isPos(R(ctx).a!) ? "positive, so the vertex is a minimum" : "negative, so the vertex is a maximum"}.`,
      sqrt: () => "A square root gives values at least 0, so after the shift the outputs lie above the bound, not below it." }),
    "Bound on the wrong side", "Uses the wrong direction of inequality for the bounded range.",
    "Gave the inequality in the wrong direction.", "opposite ray"),
  "MISC.FUNC.RANGE_USES_VERTEX_X": entry(rangeUsesVertexX,
    (ctx) => `The range uses the y-coordinate of the vertex; x = ${n(C.vertexX(R(ctx)))} is where the vertex is, not its value.`,
    "Uses the vertex x-coordinate", "Reports the axis of symmetry as the bound of the range.",
    "Used the x-coordinate of the vertex as the bound.", "y >= -b/2a"),
  "MISC.FUNC.RANGE_STRICT_AT_BOUND": entry(rangeStrictAtBound,
    () => "The bound is attained (at the vertex, or where the radicand is 0), so the inequality is not strict.",
    "Excludes the attained bound", "Uses a strict inequality although the extreme value is attained.",
    "Excluded the attained extreme value.", "strict ray"),
  "MISC.FUNC.RANGE_USES_CONSTANT_TERM": entry(rangeUsesConstantTerm,
    (ctx) => `The constant term ${n(R(ctx).c!)} is the value at x = 0, not the extreme value; find the vertex first.`,
    "Uses the constant term as the bound", "Takes the y-intercept as the minimum or maximum.",
    "Used the y-intercept as the extreme value.", "y >= c"),
  "MISC.FUNC.RANGE_IGNORES_SHIFT": entry(rangeIgnoresShift,
    (ctx) => `The constant ${n(R(ctx).v!)} shifts every output; apply it to the base range.`,
    "Ignores the vertical shift", "States the range of the unshifted base function.",
    "Ignored the vertical shift.", "base range"),
  "MISC.FUNC.DOMAIN_RANGE_CONFUSED": entry(domainRangeConfused,
    () => "The range is the set of OUTPUT values (y), not the set of allowed inputs (x).",
    "Confuses domain and range", "Gives the domain (in y) instead of the range.",
    "Gave the domain instead of the range.", "domain restated in y"),
  "MISC.FUNC.RANGE_POLE_AS_INEQUALITY": entry(rangePoleAsInequality,
    () => "The fraction takes every value except one (positive and negative), so exclude a single value rather than writing an inequality.",
    "Turns the missing value into an inequality", "Writes y > v instead of y != v.",
    "Wrote an inequality instead of excluding one value.", "y > v"),
  "MISC.FUNC.RANGE_ONLY_LOWER_BOUND": entry(rangeOnlyLowerBound,
    () => "On a closed restricted domain the outputs are bounded on BOTH sides: evaluate the rule at both endpoints.",
    "States only one bound", "Reports only the lower bound of a bounded range.",
    "Gave only one of the two bounds.", "y >= min"),
  "MISC.FUNC.RANGE_STRICT_ENDPOINTS": entry(rangeStrictEndpoints,
    () => "The domain includes its endpoints, so their images are attained: use <= at both ends.",
    "Open interval for a closed domain", "Uses strict inequalities although the endpoint images are attained.",
    "Excluded the attained endpoint images.", "open interval"),

  // --- composite ------------------------------------------------------------------------------ //
  "MISC.FUNC.COMP_ORDER_REVERSED": entry(compOrderReversed,
    (ctx) => `(${ctx.outer_name} o ${ctx.inner_name})(x) means ${ctx.outer_name}(${ctx.inner_name}(x)): apply ${ctx.inner_name} first, then ${ctx.outer_name}.`,
    "Reverses the order of composition", "Applies the outer function first.",
    "Composed the functions in the wrong order.", "inner(outer(.))"),
  "MISC.FUNC.COMP_AS_PRODUCT": entry(compAsProduct,
    (ctx) => `(${ctx.outer_name} o ${ctx.inner_name}) is composition, not multiplication: substitute ${ctx.inner_name}(x) into ${ctx.outer_name}.`,
    "Composition as a product", "Multiplies the two functions.",
    "Multiplied the functions instead of composing them.", "f * g"),
  "MISC.FUNC.COMP_AS_SUM": entry(compAsSum,
    (ctx) => `(${ctx.outer_name} o ${ctx.inner_name}) is composition, not addition: substitute ${ctx.inner_name}(x) into ${ctx.outer_name}.`,
    "Composition as a sum", "Adds the two functions.",
    "Added the functions instead of composing them.", "f + g"),
  "MISC.FUNC.COMP_INNER_ONLY": entry(compInnerOnly,
    (ctx) => `After finding ${ctx.inner_name}(${n(ctx.p!)}), substitute that value into ${ctx.outer_name}.`,
    "Stops after the inner function", "Reports the inner value without applying the outer function.",
    "Applied only the inner function.", "inner(p)"),
  "MISC.FUNC.COMP_OUTER_AT_INPUT": entry(compOuterAtInput,
    (ctx) => `Apply ${ctx.inner_name} first: the input of ${ctx.outer_name} is ${ctx.inner_name}(${n(ctx.p!)}), not ${n(ctx.p!)}.`,
    "Applies only the outer function", "Evaluates the outer function directly at the input.",
    "Applied only the outer function at the input.", "outer(p)"),
  "MISC.FUNC.COMP_SQUARE_NO_CROSS_TERM": entry(compSquareNoCrossTerm,
    () => "When squaring a binomial, include the cross term: (u + w)^2 = u^2 + 2uw + w^2.",
    "Squares a binomial without the cross term", "Expands (mx + n)^2 as m^2 x^2 + n^2.",
    "Dropped the cross term when squaring the inner expression.", "a(m^2 x^2 + n^2) + b(mx + n) + c"),

  // --- function_from_composite ----------------------------------------------------------------- //
  "MISC.FUNC.FFC_IGNORES_INNER": entry(ffcIgnoresInner,
    () => "The given expression is f(g(x)), not f(x); undo g to recover f.",
    "Takes the composite as f", "Reports the composite itself as the outer function.",
    "Gave the composite instead of the outer function.", "p x + q"),
  "MISC.FUNC.FFC_SHIFT_NOT_INVERTED": entry(ffcShiftNotInverted,
    (ctx) => `Let u = g(x) = ${C.ruleText(C.linear(ctx.m!, ctx.c!))} and express x in terms of u: the shift ${n(ctx.c!)} must be undone, not repeated.`,
    "Does not invert the inner shift", "Substitutes x + c instead of x - c when changing variable.",
    "Undid the inner shift with the wrong sign.", "p(x + c)/m + q"),
  "MISC.FUNC.FFC_SCALE_NOT_INVERTED": entry(ffcScaleNotInverted,
    (ctx) => `The inner function multiplies by ${n(ctx.m!)}; to recover x, divide by ${n(ctx.m!)}, do not multiply again.`,
    "Does not invert the inner scale", "Multiplies by the inner coefficient instead of dividing.",
    "Undid the inner scale by multiplying instead of dividing.", "p m (x - c) + q"),
  "MISC.FUNC.FFC_COMPOSES_INSTEAD": entry(ffcComposesInstead,
    () => "You composed the given expression with g again; instead, work backwards from f(g(x)) to f.",
    "Composes instead of decomposing", "Substitutes g into the composite.",
    "Composed with the inner function instead of undoing it.", "p(mx + c) + q"),

  // --- inverse --------------------------------------------------------------------------------- //
  "MISC.FUNC.INV_AS_RECIPROCAL": entry(invAsReciprocal,
    (ctx) => `${fname(ctx)}^-1 is the inverse function, not the reciprocal 1/${fname(ctx)}(x): swap x and y and solve for y.`,
    "Inverse as reciprocal", "Confuses the inverse function with the reciprocal of the function.",
    "Gave the reciprocal instead of the inverse function.", "1/(ax + b)"),
  "MISC.FUNC.INV_UNDO_ORDER": entry(invUndoOrder,
    (ctx) => `Undo the operations in reverse order: first undo the constant ${n(ctx.b!)}, then divide by ${n(ctx.a!)}.`,
    "Undoes the operations in the wrong order", "Divides before undoing the constant.",
    "Undid the operations in the wrong order.", "x/a - b"),
  "MISC.FUNC.INV_SIGN_ERROR": entry(invSignError,
    (ctx) => `To undo ${C.isPos(ctx.b!) ? "+ " + n(ctx.b!) : "- " + n(ctx.b!.neg())}, apply the opposite operation.`,
    "Sign error undoing the constant", "Adds the constant that should be subtracted (or vice versa).",
    "Used the wrong sign when undoing the constant.", "(x + b)/a"),
  "MISC.FUNC.INV_NEGATES_ONLY": entry(invNegatesOnly,
    (ctx) => `Changing the sign of the constant does not undo the function; divide by ${n(ctx.a!)} as well.`,
    "Negates the constant only", "Keeps the multiplication and only flips the sign of the constant.",
    "Only changed the sign of the constant.", "ax - b"),
  "MISC.FUNC.INV_SWAPS_ROLES": entry(invSwapsRoles,
    (ctx) => `Divide by the coefficient of x (${n(ctx.a!)}), not by the constant (${n(ctx.b!)}).`,
    "Swaps the coefficient and the constant", "Divides by the constant and subtracts the coefficient.",
    "Swapped the roles of the coefficient and the constant.", "(x - a)/b"),
  "MISC.FUNC.INVVAL_FORWARD": entry(invvalForward,
    (ctx) => `${fname(ctx)}^-1(${n(ctx.k!)}) is the input x with ${fname(ctx)}(x) = ${n(ctx.k!)}; do not substitute ${n(ctx.k!)} into ${fname(ctx)}.`,
    "Evaluates f instead of f^-1", "Substitutes the value into f rather than solving f(x) = value.",
    "Evaluated the function instead of its inverse.", "f(k)"),
  "MISC.FUNC.INVVAL_RECIPROCAL": entry(invvalReciprocal,
    (ctx) => `${fname(ctx)}^-1 means the inverse function, not 1 divided by ${fname(ctx)}.`,
    "Inverse value as a reciprocal", "Computes 1/f(value).",
    "Took the reciprocal of the function value.", "1/f(.)"),
  "MISC.FUNC.INVVAL_APPLIES_INVERSE_AGAIN": entry(invvalAppliesInverseAgain,
    (ctx) => `${fname(ctx)}^-1(k) = ${n(ctx.x0!)} means ${fname(ctx)}(${n(ctx.x0!)}) = k, so evaluate ${fname(ctx)} at ${n(ctx.x0!)}.`,
    "Applies the inverse a second time", "Applies f^-1 to the given input instead of f.",
    "Applied the inverse to the given value instead of the function.", "(x0 - b)/a"),
  "MISC.FUNC.INVVAL_IDENTITY": entry(invvalIdentity,
    (ctx) => `k is not ${n(ctx.x0!)}: ${fname(ctx)}^-1(k) = ${n(ctx.x0!)} means k = ${fname(ctx)}(${n(ctx.x0!)}).`,
    "Reads the equation as the identity", "Reports the given input as the unknown.",
    "Reported the given value as the answer.", "x0"),

  // --- one_to_one_restriction ----------------------------------------------------------------- //
  "MISC.FUNC.VERTEX_X_MISSING_HALF": entry(vertexXMissingHalf,
    (ctx) => `The axis of symmetry is x = -b/(2a): divide by twice the coefficient of x^2, that is by ${n(two.mul(R(ctx).a!))}.`,
    "Axis of symmetry without the half", "Uses -b/a for the axis of symmetry.",
    "Omitted the factor 2 in the axis of symmetry.", "-b/a"),
  "MISC.FUNC.VERTEX_X_SIGN": entry(vertexXSign,
    () => "The axis of symmetry is x = -b/(2a); watch the sign of the x coefficient.",
    "Axis of symmetry with the wrong sign", "Uses b/(2a) for the axis of symmetry.",
    "Used the wrong sign in the axis of symmetry.", "b/2a"),
  "MISC.FUNC.VERTEX_Y_FOR_X": entry(vertexYForX,
    () => "The restriction is on the INPUT x at the vertex, not on the value of the function there.",
    "Uses the vertex value", "Reports the minimum/maximum value instead of where it occurs.",
    "Gave the vertex value instead of its x-coordinate.", "f(-b/2a)"),
  "MISC.FUNC.RESTRICTION_ZERO": entry(restrictionZero,
    () => "The symmetry of this parabola is not about x = 0; find the axis of symmetry from the coefficients.",
    "Assumes the restriction is x = 0", "Restricts at 0 regardless of the axis of symmetry.",
    "Assumed the axis of symmetry is x = 0.", "0"),
  "MISC.FUNC.VERTEX_X_USES_C": entry(vertexXUsesC,
    () => "The axis of symmetry depends on the x coefficient and the x^2 coefficient, not on the constant term.",
    "Uses the constant term in the axis", "Substitutes the constant term for the x coefficient in -b/(2a).",
    "Used the constant term in place of the x coefficient.", "-c/2a"),
};

export const ELIGIBILITY: Record<string, string[]> = {
  identify_function: ["MISC.FUNC.MANY_TO_ONE_REJECTED", "MISC.FUNC.CONSTANT_REJECTED", "MISC.FUNC.PATTERN_REQUIRED"],
  evaluate_function: ["MISC.FUNC.EVAL_FORGOT_MULTIPLY", "MISC.FUNC.EVAL_DROP_CONSTANT", "MISC.FUNC.EVAL_SIGN_OF_INPUT",
    "MISC.FUNC.EVAL_CONSTANT_SIGN_FLIPPED", "MISC.FUNC.EVAL_SQUARE_NEGATIVE", "MISC.FUNC.EVAL_SQUARE_COEFFICIENT",
    "MISC.FUNC.EVAL_SQUARE_AS_DOUBLE", "MISC.FUNC.EVAL_DENOMINATOR_NOT_GROUPED", "MISC.FUNC.EVAL_RECIPROCAL_INVERTED",
    "MISC.FUNC.EVAL_ROOT_IGNORED", "MISC.FUNC.EVAL_HALVE_INSTEAD_OF_ROOT", "MISC.FUNC.EVAL_NEGATIVE_ROOT"],
  solve_for_input: ["MISC.FUNC.SOLVE_EVALUATES_INSTEAD", "MISC.FUNC.SOLVE_WRONG_INVERSE", "MISC.FUNC.SOLVE_STOPS_BEFORE_DIVIDING",
    "MISC.FUNC.SOLVE_DIVIDE_BY_CONSTANT", "MISC.FUNC.SOLVE_RECIPROCAL_NOT_INVERTED", "MISC.FUNC.SOLVE_POLE_SIGN",
    "MISC.FUNC.SOLVE_IGNORES_SHIFT", "MISC.FUNC.SOLVE_FORGOT_TO_SQUARE", "MISC.FUNC.SOLVE_SQUARE_BEFORE_ISOLATING"],
  domain_of_function: ["MISC.FUNC.DOMAIN_ALL_REALS", "MISC.FUNC.DOMAIN_DIRECTION_FLIPPED", "MISC.FUNC.DOMAIN_STRICT_ENDPOINT",
    "MISC.FUNC.DOMAIN_ENDPOINT_SIGN", "MISC.FUNC.DOMAIN_AS_EXCLUDED_POINT", "MISC.FUNC.DOMAIN_POLE_SIGN",
    "MISC.FUNC.DOMAIN_EXCLUDES_ZERO", "MISC.FUNC.DOMAIN_POLE_AS_INEQUALITY", "MISC.FUNC.DOMAIN_NONNEGATIVE_ONLY",
    "MISC.FUNC.DOMAIN_EXCLUDES_CONSTANT"],
  range_of_function: ["MISC.FUNC.RANGE_DIRECTION_FLIPPED", "MISC.FUNC.RANGE_USES_VERTEX_X", "MISC.FUNC.RANGE_STRICT_AT_BOUND",
    "MISC.FUNC.RANGE_USES_CONSTANT_TERM", "MISC.FUNC.RANGE_IGNORES_SHIFT", "MISC.FUNC.DOMAIN_RANGE_CONFUSED",
    "MISC.FUNC.RANGE_POLE_AS_INEQUALITY", "MISC.FUNC.RANGE_ONLY_LOWER_BOUND", "MISC.FUNC.RANGE_STRICT_ENDPOINTS",
    "MISC.FUNC.RANGE_ALL_REALS"],
  composite_value: ["MISC.FUNC.COMP_ORDER_REVERSED", "MISC.FUNC.COMP_AS_PRODUCT", "MISC.FUNC.COMP_AS_SUM",
    "MISC.FUNC.COMP_INNER_ONLY", "MISC.FUNC.COMP_OUTER_AT_INPUT"],
  composite_expression: ["MISC.FUNC.COMP_ORDER_REVERSED", "MISC.FUNC.COMP_SQUARE_NO_CROSS_TERM", "MISC.FUNC.COMP_AS_PRODUCT",
    "MISC.FUNC.COMP_AS_SUM"],
  function_from_composite: ["MISC.FUNC.FFC_IGNORES_INNER", "MISC.FUNC.FFC_SHIFT_NOT_INVERTED", "MISC.FUNC.FFC_SCALE_NOT_INVERTED",
    "MISC.FUNC.FFC_COMPOSES_INSTEAD"],
  inverse_value: ["MISC.FUNC.INVVAL_FORWARD", "MISC.FUNC.INVVAL_RECIPROCAL", "MISC.FUNC.INVVAL_APPLIES_INVERSE_AGAIN",
    "MISC.FUNC.INVVAL_IDENTITY", "MISC.FUNC.INV_UNDO_ORDER", "MISC.FUNC.INV_SIGN_ERROR"],
  inverse_expression: ["MISC.FUNC.INV_AS_RECIPROCAL", "MISC.FUNC.INV_UNDO_ORDER", "MISC.FUNC.INV_SIGN_ERROR",
    "MISC.FUNC.INV_NEGATES_ONLY", "MISC.FUNC.INV_SWAPS_ROLES"],
  one_to_one_restriction: ["MISC.FUNC.VERTEX_X_MISSING_HALF", "MISC.FUNC.VERTEX_X_SIGN", "MISC.FUNC.VERTEX_Y_FOR_X",
    "MISC.FUNC.RESTRICTION_ZERO", "MISC.FUNC.VERTEX_X_USES_C"],
};

export const STRUCTURAL_ONLY: readonly string[] = ["MISC.FUNC.MANY_TO_ONE_REJECTED", "MISC.FUNC.CONSTANT_REJECTED", "MISC.FUNC.PATTERN_REQUIRED"];

export function rulesFor(task: string): string[] {
  return ELIGIBILITY[task] ? [...ELIGIBILITY[task]!] : [];
}
