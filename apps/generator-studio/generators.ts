/**
 * Studio generator registry — now a thin re-export of the core SDK registry
 * (core/sdk). The app depends on the SDK contract, not on a duplicate list.
 */

export type { GeneratorModule, StudioMode, ApprovalStatus } from "../../core/sdk/generator-module.ts";
export type { GenValidationResult as GenValidation } from "../../core/sdk/generator-module.ts";
export { approvalStatusOf } from "../../core/sdk/generator-module.ts";
export { GENERATORS, getGenerator, taskIsMc, generatorsForMode, approvedGenerators } from "../../core/sdk/sequence-registry.ts";

/** The Studio's current visibility mode. Normal users see only curriculum-approved
 *  generators; review/developer mode (URL ?review) also sees machine-validated,
 *  pending-approval generators (labelled as such). */
export function studioMode(): import("../../core/sdk/generator-module.ts").StudioMode {
  try {
    const g = globalThis as { location?: { search?: string } };
    return g.location && new URLSearchParams(g.location.search).has("review") ? "review" : "normal";
  } catch {
    return "normal";
  }
}
