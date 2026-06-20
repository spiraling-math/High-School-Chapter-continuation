/**
 * Studio generator registry — now a thin re-export of the core SDK registry
 * (core/sdk). The app depends on the SDK contract, not on a duplicate list.
 */

export type { GeneratorModule } from "../../core/sdk/generator-module.ts";
export type { GenValidationResult as GenValidation } from "../../core/sdk/generator-module.ts";
export { GENERATORS, getGenerator, taskIsMc } from "../../core/sdk/sequence-registry.ts";
