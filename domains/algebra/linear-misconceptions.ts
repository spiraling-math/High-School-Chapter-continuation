/**
 * Linear-equation misconception registry (production TypeScript).
 *
 * Byte-for-byte mirror of oracle/spi_oracle/linear_misconceptions.py. Each rule is
 * an independently recomputable wrong-answer over the reduced form
 * `P·x + Q = R·x + T` (true `s = (T − Q)/(P − R)`); a rule returns its wrong value
 * or `null`. `observableError` (serialized as the distractor rationale) and the
 * item-specific `feedback(red)` (student-facing) contain NO internal placeholder
 * symbols (p, q, r, t, k) — internal formulas live only in `expression`
 * (teacher/technical metadata).
 */

import { Rational, rat } from "../../core/exact-math/rational.ts";

export interface Red {
  P: Rational; Q: Rational; R: Rational; T: Rational;
  kMul: Rational | null; innerP: Rational | null; innerQ: Rational | null;
}

export interface LinMisconception {
  wrong: (red: Red) => Rational | null;
  feedback: (red: Red) => string;
  title: string;
  description: string;
  observableError: string;
  expression: string;
}

const one = rat(1);

function nTxt(r: Rational): string { return r.toString(); }
function termTxt(r: Rational): string {
  if (r.equals(one)) return "x";
  if (r.equals(rat(-1))) return "-x";
  return `${r.toString()}x`;
}

export const MISCONCEPTIONS: Record<string, LinMisconception> = {
  "MISC.LINEQ.STOPS_BEFORE_DIVIDING": {
    wrong: (r) => (r.P.sub(r.R).abs().equals(one) ? null : r.T.sub(r.Q)),
    feedback: (r) => { const c = r.P.sub(r.R); return `Divide both sides by ${nTxt(c)} to find x, not just ${termTxt(c)}.`; },
    title: "Stops before dividing by the coefficient",
    description: "Isolates the variable term but reports it as the variable, without dividing by the coefficient.",
    observableError: "Isolated the variable term but did not divide by its coefficient.",
    expression: "t - q",
  },
  "MISC.LINEQ.WRONG_INVERSE": {
    wrong: (r) => (r.Q.isZero() ? null : r.T.add(r.Q).div(r.P.sub(r.R))),
    feedback: (r) => (r.Q.num > 0
      ? `The constant ${nTxt(r.Q)} is added, so subtract ${nTxt(r.Q)} from both sides — do not add it.`
      : `The constant ${nTxt(r.Q)} is subtracted, so add ${nTxt(r.Q.neg())} to both sides — do not subtract it.`),
    title: "Wrong inverse operation on the constant",
    description: "Adds the constant instead of subtracting it (or vice versa) when moving it across the equals sign.",
    observableError: "Used the wrong inverse operation on the constant term.",
    expression: "(t + q)/(p - r)",
  },
  "MISC.LINEQ.VAR_SIGN": {
    wrong: (r) => (r.R.isZero() || r.P.add(r.R).isZero() ? null : r.T.sub(r.Q).div(r.P.add(r.R))),
    feedback: (r) => (r.R.num > 0
      ? `Subtract ${termTxt(r.R)} from both sides so the variable terms are collected on one side.`
      : `Add ${termTxt(r.R.neg())} to both sides so the variable terms are collected on one side.`),
    title: "Wrong sign moving a variable term",
    description: "Moves the variable term to the other side without flipping its sign.",
    observableError: "Moved the variable term to the other side without flipping its sign.",
    expression: "(t - q)/(p + r)",
  },
  "MISC.LINEQ.CONST_SIGN": {
    wrong: (r) => (r.Q.isZero() ? null : r.Q.sub(r.T).div(r.P.sub(r.R))),
    feedback: (r) => `Apply the inverse of ${nTxt(r.Q)} to both sides and keep the sign of the constant consistent.`,
    title: "Wrong sign moving a constant",
    description: "Changes the sign of a constant without applying the operation to both sides.",
    observableError: "Changed the sign of a constant without applying the operation to both sides.",
    expression: "(q - t)/(p - r)",
  },
  "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT": {
    wrong: (r) => {
      const denom = r.P.add(r.Q).sub(r.R);
      return r.Q.isZero() || denom.isZero() ? null : r.T.div(denom);
    },
    feedback: (r) => `${termTxt(r.P)} and ${nTxt(r.Q)} are unlike terms; an x-term and a constant cannot be combined.`,
    title: "Combines unlike terms",
    description: "Adds an x-term and a constant into a single coefficient of x.",
    observableError: "Combined an x-term and a constant into a single coefficient.",
    expression: "t/(p + q - r)",
  },
  "MISC.LINEQ.DIVIDE_ONE_TERM": {
    wrong: (r) => (r.Q.isZero() ? null : r.T.div(r.P.sub(r.R)).sub(r.Q)),
    feedback: (r) => `Divide every term on that side by ${nTxt(r.P.sub(r.R))}, not just one term.`,
    title: "Divides only one term",
    description: "Divides one term on the side by the coefficient but not every term.",
    observableError: "Divided only one term on the side, not every term.",
    expression: "t/(p - r) - q",
  },
  "MISC.LINEQ.DIVIDE_BY_CONSTANT": {
    wrong: (r) => (r.Q.isZero() || r.Q.equals(r.P.sub(r.R)) ? null : r.T.sub(r.Q).div(r.Q)),
    feedback: (r) => `Divide by the coefficient of x (${nTxt(r.P.sub(r.R))}), not by the constant ${nTxt(r.Q)}.`,
    title: "Divides by the constant",
    description: "Divides by the constant term instead of by the coefficient of x.",
    observableError: "Divided by the constant term instead of the coefficient of x.",
    expression: "(t - q)/q",
  },
  "MISC.LINEQ.IGNORE_CONSTANT": {
    wrong: (r) => (r.Q.isZero() ? null : r.T),
    feedback: (r) => `Do not ignore the ${nTxt(r.Q)}; apply its inverse to both sides.`,
    title: "Ignores the constant",
    description: "Reads off the right-hand value as the answer, ignoring the added or subtracted constant.",
    observableError: "Ignored the added or subtracted constant.",
    expression: "t",
  },
  "MISC.LINEQ.MULTIPLY_INSTEAD_OF_DIVIDE": {
    wrong: (r) => (r.T.isZero() || r.P.equals(one) || r.P.equals(rat(-1)) ? null : r.P.mul(r.T)),
    feedback: (r) => `To undo multiplication by ${nTxt(r.P)}, divide both sides by ${nTxt(r.P)}.`,
    title: "Multiplies instead of dividing",
    description: "Multiplies both sides by the coefficient instead of dividing by it.",
    observableError: "Multiplied by the coefficient instead of dividing by it.",
    expression: "p * t",
  },
  "MISC.LINEQ.REVERSES_DIVISION": {
    wrong: (r) => (r.T.isZero() ? null : r.P.div(r.T)),
    feedback: (r) => `Divide ${nTxt(r.T)} by ${nTxt(r.P)}. Do not reverse the numerator and denominator.`,
    title: "Reverses the division",
    description: "Divides the coefficient by the constant instead of the constant by the coefficient.",
    observableError: "Inverted the division: divided the coefficient by the value instead of the value by the coefficient.",
    expression: "p / t",
  },
  "MISC.LINEQ.DISTRIBUTE_PARTIAL": {
    wrong: (r) => (r.kMul === null || r.kMul.equals(one) || (r.innerQ as Rational).isZero()
      ? null
      : r.T.sub(r.innerQ as Rational).div(r.P.sub(r.R))),
    feedback: (r) => `Multiply every term inside the brackets by ${nTxt(r.kMul as Rational)}.`,
    title: "Partial distribution over brackets",
    description: "Multiplies the factor outside the bracket by the variable term only, not the constant term.",
    observableError: "Multiplied only the first term inside the brackets by the factor.",
    expression: "k(px + q) -> kp*x + q",
  },
  // Diagnostic-only category — NEVER used for MC distractor generation.
  "MISC.LINEQ.SIGNED_ARITH_SLIP": {
    wrong: () => null,
    feedback: () => "Re-check the signed arithmetic at each step.",
    title: "Signed-number arithmetic slip",
    description: "A generic signed-number arithmetic error; not a deterministic distractor rule.",
    observableError: "Made a signed-number arithmetic error.",
    expression: "(diagnostic only)",
  },
};

const ELIGIBILITY: Record<string, string[]> = {
  one_step_add: ["MISC.LINEQ.IGNORE_CONSTANT", "MISC.LINEQ.WRONG_INVERSE",
    "MISC.LINEQ.CONST_SIGN", "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT"],
  one_step_mul: ["MISC.LINEQ.STOPS_BEFORE_DIVIDING", "MISC.LINEQ.MULTIPLY_INSTEAD_OF_DIVIDE",
    "MISC.LINEQ.REVERSES_DIVISION"],
  two_step: ["MISC.LINEQ.STOPS_BEFORE_DIVIDING", "MISC.LINEQ.WRONG_INVERSE",
    "MISC.LINEQ.DIVIDE_ONE_TERM", "MISC.LINEQ.DIVIDE_BY_CONSTANT",
    "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT"],
  both_sides: ["MISC.LINEQ.STOPS_BEFORE_DIVIDING", "MISC.LINEQ.WRONG_INVERSE",
    "MISC.LINEQ.VAR_SIGN", "MISC.LINEQ.CONST_SIGN",
    "MISC.LINEQ.DIVIDE_ONE_TERM", "MISC.LINEQ.DIVIDE_BY_CONSTANT",
    "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT"],
  brackets: ["MISC.LINEQ.DISTRIBUTE_PARTIAL", "MISC.LINEQ.STOPS_BEFORE_DIVIDING",
    "MISC.LINEQ.WRONG_INVERSE", "MISC.LINEQ.VAR_SIGN", "MISC.LINEQ.CONST_SIGN",
    "MISC.LINEQ.DIVIDE_ONE_TERM", "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT"],
};

export function rulesFor(task: string): string[] {
  return ELIGIBILITY[task] ? [...ELIGIBILITY[task]!] : [];
}
