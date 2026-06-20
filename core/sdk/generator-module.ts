/**
 * The formal Generator SDK contract.
 *
 * The platform (Studio, exporters, bank, harness, tests) depends on this
 * interface, never on a specific generator family. Both curriculum-approved
 * generators (arithmetic v1.1.0, geometric v1.1.0) satisfy `GeneratorModule`;
 * this is asserted by the harness test.
 */

import type { Json } from "../serialization/canonical.ts";

export type Item = Record<string, Json>;

export type InteractionType = "free-response" | "multiple-choice";

/** Forward canonical answer model (geometric v1.1.0 onward). */
export type AnswerType = "integer" | "exact-rational";
export interface CanonicalRational { num: number; den: number; }

export interface GenValidationCheck { name: string; result: "pass" | "fail"; detail: string; }
export interface GenValidationResult { status: "pass" | "fail"; validatorVersion: string; checks: GenValidationCheck[]; }

export interface GeneratorTaskInfo {
  value: string;
  label: string;
  /** Whether this task supports a multiple-choice interaction. */
  mc: boolean;
}

/** Configuration accepted by generate(). `answerType` is the legacy selector
 *  (see TD-1); `interactionType` is the forward key. */
export interface GenConfig {
  task?: string;
  answerType?: string;
  interactionType?: string;
}

/**
 * The minimal runtime-facing generator surface. The richer contract
 * (describe/solve/generateDistractors/generateSolution/render) is documented in
 * GENERATOR_STANDARD.md and GENERATOR_SDK_DESIGN.md; these three are what the
 * Studio, exporters, and stability harness require.
 */
export interface GeneratorModule {
  readonly id: string;
  readonly version: string;
  readonly label: string;
  readonly tasks: GeneratorTaskInfo[];
  generate(seed: number, config: GenConfig): Item;
  validate(item: Item): GenValidationResult;
  serialize(item: Item): string;
}

/** The interaction modes a generator can be swept in, derived from its tasks. */
export function interactionModesFor(gen: GeneratorModule): InteractionType[] {
  return gen.tasks.some((t) => t.mc) ? ["free-response", "multiple-choice"] : ["free-response"];
}
