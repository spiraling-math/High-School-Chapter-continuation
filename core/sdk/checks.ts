/**
 * Universal validation predicates (SDK).
 *
 * Domain-INDEPENDENT check logic shared by every generator's validator. These
 * return booleans only; each validator keeps its own check IDs, ordering, and
 * detail messages (so existing validator output is preserved byte-for-byte) and
 * composes only the predicates that apply to it. Domain-specific checks
 * (iterative agreement, ratio/term-index uniqueness, convergence, parameter-domain
 * maths) stay inside the relevant generator. This is intentionally NOT one large
 * universal validator.
 */

import type { Json } from "../serialization/canonical.ts";

/** The final solution step states the canonical answer. */
export function answerSolutionAgrees(lastStepText: string, answerDisplay: string): boolean {
  return lastStepText.includes(answerDisplay);
}

/** Every integer printed in the prompt is a declared given (no answer leakage). */
export function promptIntsAreGivens(promptInts: readonly number[], givens: ReadonlySet<number>): boolean {
  return promptInts.every((i) => givens.has(i));
}

/** Exactly one option is flagged correct and it matches the canonical answer. */
export function exactlyOneCorrectByDisplay(
  options: ReadonlyArray<{ display: string; correct: boolean }>,
  answerDisplay: string,
): boolean {
  const correct = options.filter((o) => o.correct);
  return correct.length === 1 && correct[0]!.display === answerDisplay;
}

/** All incorrect options are distinct. */
export function wrongOptionsUniqueByDisplay(options: ReadonlyArray<{ display: string; correct: boolean }>): boolean {
  const wrong = options.filter((o) => !o.correct).map((o) => o.display);
  return new Set(wrong).size === wrong.length;
}

/** Required accessibility field (spoken-math rendering) is present. */
export function spokenMathPresent(item: Record<string, Json>): boolean {
  return Boolean((item["accessibility"] as { spokenMath?: string } | undefined)?.spokenMath);
}

/** interactionType is one of the allowed values. */
export function interactionTypeValid(value: unknown): boolean {
  return value === "free-response" || value === "multiple-choice";
}

/** The answer's mathematical type agrees with its canonical value. */
export function answerTypeConsistent(type: string, canonical: unknown): boolean {
  const isObj = canonical !== null && typeof canonical === "object" && "den" in (canonical as object);
  if (type === "integer") return !isObj || (canonical as { den: number }).den === 1;
  if (type === "exact-rational") return isObj && (canonical as { den: number }).den >= 1;
  return true; // other answer types are not constrained by this check
}

/** Provenance carries origin and rights status. */
export function provenanceComplete(item: Record<string, Json>): boolean {
  const p = item["provenance"] as { origin?: string; rightsStatus?: string } | undefined;
  return Boolean(p && p.origin && p.rightsStatus);
}

/** Generator id + version are present (traceability). */
export function versionFieldsPresent(item: Record<string, Json>): boolean {
  return Boolean(item["generatorId"]) && Boolean(item["generatorVersion"]);
}
