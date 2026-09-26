/**
 * Question-bank data types.
 *
 * A BankRecord wraps the immutable, generated question `item` (the protected
 * mathematical truth) together with bank metadata and an EDITABLE WORDING
 * overlay. Wording edits change only presentation text — never the params,
 * answer, distractors, or solution. This enforces the separation between
 * editable wording and protected mathematical parameters.
 */

import type { Json } from "../serialization/canonical.ts";

export type LifecycleState =
  | "draft"
  | "generated"
  | "machine-validated"
  | "mathematics-reviewed"
  | "curriculum-reviewed"
  | "approved"
  | "published"
  | "revised"
  | "retired";

/** Lifecycle states the Studio app is allowed to set. Approval/publication are
 *  reserved for the curriculum authority and are NOT settable from the app. */
export const APP_SETTABLE_STATES: LifecycleState[] = [
  "draft", "generated", "machine-validated", "revised", "retired",
];

export type Mode = "integer" | "multiple-choice";

/** Canonical interaction classification (TD-1). Stored on every record. */
export type InteractionType = "free-response" | "multiple-choice";

/** Editable wording overlay. Overrides display text only. */
export interface WordingOverlay {
  title?: string;
  /** Optional per-block replacement texts; same length/order as item.prompt.blocks. */
  blocks?: string[];
}

export interface BankRecord {
  itemId: string;
  /** Canonical generated item. Treated as immutable mathematical data. */
  item: Record<string, Json>;
  /** Editable wording overlay (never mutates `item`). */
  wording: WordingOverlay;
  lifecycleState: LifecycleState;
  validationStatus: "pass" | "fail" | "warn" | "not-run";
  tags: string[];
  archived: boolean;
  createdAt: string;
  modifiedAt: string;
  // Denormalized fields for indexing / search:
  generatorId: string;
  generatorVersion: string;
  objectiveId: string;
  task: string;
  band: number;
  seed: number;
  /** Legacy interaction mode (kept for back-compat and the genConfig reproduction). */
  mode: Mode;
  /** Canonical interaction field (TD-1). Derived from mode for legacy records. */
  interactionType: InteractionType;
  /** Exact config passed to generate(seed, config), so the item reproduces
   *  identically. Distinguishes auto-task (no `task`) from explicit-task runs.
   *  This is the preserved original (legacy) configuration used for reproduction. */
  genConfig: { answerType: Mode; interactionType?: InteractionType; task?: string };
  /** Internal schema revision of the record shape (set by migrations). */
  schemaRev?: number;
}

export interface BankQuery {
  text?: string;
  generatorId?: string;
  objectiveId?: string;
  task?: string;
  band?: number;
  lifecycleState?: LifecycleState;
  /** undefined = all; false = only active; true = only archived. */
  archived?: boolean;
  tag?: string;
}

export interface BankStore {
  put(rec: BankRecord): Promise<void>;
  get(id: string): Promise<BankRecord | undefined>;
  query(q?: BankQuery): Promise<BankRecord[]>;
  delete(id: string): Promise<void>;
  count(): Promise<number>;
  clear(): Promise<void>;
  close(): void;
}
