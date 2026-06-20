/** Shared application context for the Studio panels. */

import type { Json } from "../../core/serialization/canonical.ts";
import type { BankStore, BankRecord, BankQuery, Mode } from "../../core/bank/types.ts";
import { validate } from "../../domains/sequences/validate.ts";

export type ValidationResult = ReturnType<typeof validate>;

export interface Studio {
  store: BankStore;
  /** The item currently in the workspace (generated or loaded from the bank). */
  item: Record<string, Json> | null;
  validation: ValidationResult | null;
  /** The bank record backing the workspace item, if it has been saved/loaded. */
  record: BankRecord | null;
  mode: Mode;
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
