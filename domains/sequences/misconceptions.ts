/**
 * Canonical arithmetic-sequence misconception registry (production TypeScript).
 *
 * Byte-for-byte mirror of oracle/spi_oracle/misconceptions.py. This is the single
 * source of truth for distractor values and their rationale/feedback. The
 * `observableError` strings are serialized into items as the distractor
 * `rationale`, so they MUST match the oracle exactly for cross-language parity.
 */

export interface MisconceptionParams { a1: number; d: number; n: number; }

export interface Misconception {
  formula: (p: MisconceptionParams) => number;
  expression: string;
  title: string;
  description: string;
  observableError: string;
  feedback: string;
}

const uN = (p: MisconceptionParams) => p.a1 + (p.n - 1) * p.d;

export const MISCONCEPTIONS: Record<string, Misconception> = {
  "MISC.SEQ.OFFBYONE_TERMINDEX": {
    formula: (p) => p.a1 + p.n * p.d,
    expression: "u_1 + n*d",
    title: "Off-by-one in term index",
    description: "Uses n steps of the common difference instead of (n - 1).",
    observableError: "Answer is exactly one common difference too large.",
    feedback: "Reaching the nth term takes (n - 1) steps of the common difference, not n.",
  },
  "MISC.SEQ.SIGN_DIFFERENCE": {
    formula: (p) => p.a1 - (p.n - 1) * p.d,
    expression: "u_1 - (n-1)*d",
    title: "Sign error on the common difference",
    description: "Subtracts the common difference instead of adding it.",
    observableError: "Answer reflects the wrong direction of change.",
    feedback: "Add the common difference (which may be negative); check whether the sequence increases or decreases.",
  },
  "MISC.SEQ.FORGOT_MULTIPLY": {
    formula: (p) => p.a1 + (p.n - 1),
    expression: "u_1 + (n-1)",
    title: "Forgot to multiply by the common difference",
    description: "Adds the number of steps but omits multiplying by d.",
    observableError: "Answer adds (n - 1) rather than (n - 1)*d.",
    feedback: "Each step changes the term by d, so multiply the (n - 1) steps by the common difference.",
  },
  "MISC.SEQ.FORGOT_FIRST_TERM": {
    formula: (p) => (p.n - 1) * p.d,
    expression: "(n-1)*d",
    title: "Omitted the first term",
    description: "Computes (n - 1)*d but forgets to add the first term u_1.",
    observableError: "Answer is the change from u_1, not the term value itself.",
    feedback: "Add the first term u_1 to (n - 1)*d to get the nth term.",
  },
  "MISC.SERIES.FORGOT_HALF": {
    formula: (p) => p.n * (2 * p.a1 + (p.n - 1) * p.d),
    expression: "n*(2*u_1 + (n-1)*d)",
    title: "Omitted the one-half in the sum formula",
    description: "Uses n*(2u_1 + (n-1)d) without dividing by 2.",
    observableError: "Sum is exactly twice the correct value.",
    feedback: "The sum formula has a factor of one half: S_n = (n/2)(2u_1 + (n - 1)d).",
  },
  "MISC.SERIES.CONSTANT_LAST_TERM": {
    formula: (p) => p.n * uN(p),
    expression: "n*u_n  (= n*(u_1 + (n-1)*d))",
    title: "Treats every term as equal to the last term",
    description: "Multiplies the number of terms by the last (nth) term.",
    observableError: "Sum equals n multiplied by the nth term.",
    feedback: "The terms change by the common difference; do not multiply the number of terms by only the last term.",
  },
  "MISC.SERIES.CONSTANT_FIRST_TERM": {
    formula: (p) => p.n * p.a1,
    expression: "n*u_1",
    title: "Treats every term as equal to the first term",
    description: "Multiplies the number of terms by the first term.",
    observableError: "Sum equals n multiplied by the first term.",
    feedback: "The terms change by the common difference. Do not multiply the number of terms by only the first term.",
  },
};

export const NTH_TERM_RULES = [
  "MISC.SEQ.OFFBYONE_TERMINDEX",
  "MISC.SEQ.SIGN_DIFFERENCE",
  "MISC.SEQ.FORGOT_MULTIPLY",
  "MISC.SEQ.FORGOT_FIRST_TERM",
];
export const SUM_N_RULES = [
  "MISC.SERIES.FORGOT_HALF",
  "MISC.SERIES.CONSTANT_LAST_TERM",
  "MISC.SERIES.CONSTANT_FIRST_TERM",
];

export function rulesFor(task: string): string[] {
  if (task === "nth_term") return NTH_TERM_RULES;
  if (task === "sum_n") return SUM_N_RULES;
  return [];
}
