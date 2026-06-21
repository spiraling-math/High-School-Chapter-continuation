/**
 * Linear-equation misconception registry (production TypeScript).
 *
 * Byte-for-byte mirror of oracle/spi_oracle/linear_misconceptions.py. Each rule is
 * an independently recomputable wrong-answer over the reduced form
 * `P·x + Q = R·x + T` (true `s = (T − Q)/(P − R)`); a rule returns its wrong value
 * or `null` when it does not apply. `observableError` is serialized into items as
 * the distractor rationale, so it MUST match the oracle exactly.
 */

import { Rational, rat } from "../../core/exact-math/rational.ts";

export interface Red {
  P: Rational; Q: Rational; R: Rational; T: Rational;
  kMul: Rational | null; innerP: Rational | null; innerQ: Rational | null;
}

export interface LinMisconception {
  wrong: (red: Red) => Rational | null;
  title: string;
  description: string;
  observableError: string;
  feedback: string;
  expression: string;
}

const one = rat(1);

export const MISCONCEPTIONS: Record<string, LinMisconception> = {
  "MISC.LINEQ.STOPS_BEFORE_DIVIDING": {
    wrong: (r) => (r.P.sub(r.R).abs().equals(one) ? null : r.T.sub(r.Q)),
    title: "Stops before dividing by the coefficient",
    description: "Isolates the variable term but reports it as the variable, without dividing by the coefficient.",
    observableError: "Isolated the variable term but did not divide by its coefficient.",
    feedback: "You have isolated the variable term, but not the variable. Divide both sides by the coefficient of x.",
    expression: "t - q",
  },
  "MISC.LINEQ.WRONG_INVERSE": {
    wrong: (r) => (r.Q.isZero() ? null : r.T.add(r.Q).div(r.P.sub(r.R))),
    title: "Wrong inverse operation on the constant",
    description: "Adds the constant instead of subtracting it (or vice versa) when moving it across the equals sign.",
    observableError: "Used the wrong inverse operation on the constant term.",
    feedback: "Use the inverse operation on the constant term and apply it to both sides.",
    expression: "(t + q)/(p - r)",
  },
  "MISC.LINEQ.VAR_SIGN": {
    wrong: (r) => (r.R.isZero() || r.P.add(r.R).isZero() ? null : r.T.sub(r.Q).div(r.P.add(r.R))),
    title: "Wrong sign moving a variable term",
    description: "Moves the variable term to the other side without flipping its sign.",
    observableError: "Moved the variable term with the wrong sign (used p + r instead of p - r).",
    feedback: "Subtract rx from both sides. The new variable coefficient is p - r, not p + r.",
    expression: "(t - q)/(p + r)",
  },
  "MISC.LINEQ.CONST_SIGN": {
    wrong: (r) => (r.Q.isZero() ? null : r.Q.sub(r.T).div(r.P.sub(r.R))),
    title: "Wrong sign moving a constant",
    description: "Changes the sign of a constant without applying the operation to both sides.",
    observableError: "Changed the sign of a constant without applying the operation to both sides.",
    feedback: "Apply the same subtraction to both sides and check the order of the constants.",
    expression: "(q - t)/(p - r)",
  },
  "MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT": {
    wrong: (r) => {
      const denom = r.P.add(r.Q).sub(r.R);
      return r.Q.isZero() || denom.isZero() ? null : r.T.div(denom);
    },
    title: "Combines unlike terms",
    description: "Adds an x-term and a constant into a single coefficient of x.",
    observableError: "Combined an x-term and a constant into a single coefficient.",
    feedback: "An x-term and a constant are unlike terms. Their coefficients cannot be combined.",
    expression: "t/(p + q - r)",
  },
  "MISC.LINEQ.DIVIDE_ONE_TERM": {
    wrong: (r) => (r.Q.isZero() ? null : r.T.div(r.P.sub(r.R)).sub(r.Q)),
    title: "Divides only one term",
    description: "Divides one term on the side by the coefficient but not every term.",
    observableError: "Divided only one term on the side, not every term.",
    feedback: "When dividing an equation, divide every term on the relevant side by the coefficient.",
    expression: "t/(p - r) - q",
  },
  "MISC.LINEQ.DIVIDE_BY_CONSTANT": {
    wrong: (r) => (r.Q.isZero() || r.Q.equals(r.P.sub(r.R)) ? null : r.T.sub(r.Q).div(r.Q)),
    title: "Divides by the constant",
    description: "Divides by the constant term instead of by the coefficient of x.",
    observableError: "Divided by the constant term instead of the coefficient of x.",
    feedback: "Divide by the coefficient of x, not by the constant term.",
    expression: "(t - q)/q",
  },
  "MISC.LINEQ.IGNORE_CONSTANT": {
    wrong: (r) => (r.Q.isZero() ? null : r.T),
    title: "Ignores the constant",
    description: "Reads off the right-hand value as the answer, ignoring the added or subtracted constant.",
    observableError: "Ignored the added or subtracted constant.",
    feedback: "Apply the inverse of the constant to both sides; do not ignore it.",
    expression: "t",
  },
  "MISC.LINEQ.MULTIPLY_INSTEAD_OF_DIVIDE": {
    wrong: (r) => (r.T.isZero() || r.P.equals(one) || r.P.equals(rat(-1)) ? null : r.P.mul(r.T)),
    title: "Multiplies instead of dividing",
    description: "Multiplies both sides by the coefficient instead of dividing by it.",
    observableError: "Multiplied by the coefficient instead of dividing by it.",
    feedback: "To undo multiplication by p, divide both sides by p.",
    expression: "p * t",
  },
  "MISC.LINEQ.REVERSES_DIVISION": {
    wrong: (r) => (r.T.isZero() ? null : r.P.div(r.T)),
    title: "Reverses the division",
    description: "Divides the coefficient by the constant instead of the constant by the coefficient.",
    observableError: "Inverted the division: used p/t instead of t/p.",
    feedback: "The equation gives x = t/p, not p/t.",
    expression: "p / t",
  },
  "MISC.LINEQ.DISTRIBUTE_PARTIAL": {
    wrong: (r) => (r.kMul === null || r.kMul.equals(one) || (r.innerQ as Rational).isZero()
      ? null
      : r.T.sub(r.innerQ as Rational).div(r.P.sub(r.R))),
    title: "Partial distribution over brackets",
    description: "Multiplies the factor outside the bracket by the variable term only, not the constant term.",
    observableError: "Multiplied only the first term inside the brackets by the factor.",
    feedback: "Multiply every term inside the brackets by the factor outside.",
    expression: "k(px + q) -> kp*x + q",
  },
  // Diagnostic-only category — NEVER used for MC distractor generation.
  "MISC.LINEQ.SIGNED_ARITH_SLIP": {
    wrong: () => null,
    title: "Signed-number arithmetic slip",
    description: "A generic signed-number arithmetic error; not a deterministic distractor rule.",
    observableError: "Made a signed-number arithmetic error.",
    feedback: "Re-check the signed arithmetic at each step.",
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
