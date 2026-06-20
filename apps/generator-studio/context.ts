/** Shared application context for the Studio panels. */

import type { Json } from "../../core/serialization/canonical.ts";
import type { BankStore, BankRecord, BankQuery, Mode } from "../../core/bank/types.ts";
import type { GenValidation } from "./generators.ts";

export type ValidationResult = GenValidation;

export interface Studio {
  store: BankStore;
  /** The item currently in the workspace (generated or loaded from the bank). */
  item: Record<string, Json> | null;
  validation: ValidationResult | null;
  /** The bank record backing the workspace item, if it has been saved/loaded. */
  record: BankRecord | null;
  mode: Mode;
  /** Currently selected generator module id. */
  generatorId: string;
  /** Exact config last passed to generate(), for faithful reproduction. */
  genConfig: { answerType: Mode; task?: string };
  /** Current bank list filter. */
  filter: BankQuery;
  /** Re-render all dynamic regions. Set by main(). */
  rerender: () => void;
}

export function setWorkspace(
  studio: Studio,
  item: Record<string, Json>,
  validation: ValidationResult,
  record: BankRecord | null,
): void {
  studio.item = item;
  studio.validation = validation;
  studio.record = record;
}
