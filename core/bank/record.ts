/**
 * Helpers for constructing and transforming BankRecords.
 *
 * These keep the protected mathematical data (`item`) immutable: wording edits
 * and lifecycle changes never touch params/answer/solution.
 */

import type { Json } from "../serialization/canonical.ts";
import type { BankRecord, LifecycleState, Mode, WordingOverlay } from "./types.ts";

function nowIso(): string {
  return new Date().toISOString();
}

/** Build a BankRecord from a freshly generated, validated item. */
export function makeRecord(
  item: Record<string, Json>,
  validationStatus: "pass" | "fail" | "warn" | "not-run",
  opts: { tags?: string[]; mode: Mode; genConfig?: { answerType: Mode; task?: string }; now?: string } = { mode: "integer" },
): BankRecord {
  const params = item["params"] as { task: string };
  const diff = item["difficulty"] as { overallBand: number };
  const now = opts.now ?? nowIso();
  // Items begin at machine-validated when validation passes; otherwise generated.
  const lifecycleState: LifecycleState = validationStatus === "pass" ? "machine-validated" : "generated";
  return {
    itemId: String(item["itemId"]),
    item,
    wording: {},
    lifecycleState,
    validationStatus,
    tags: opts.tags ?? [],
    archived: false,
    createdAt: now,
    modifiedAt: now,
    generatorId: String(item["generatorId"]),
    generatorVersion: String(item["generatorVersion"]),
    objectiveId: (item["objectiveIds"] as string[])[0] ?? "",
    task: params.task,
    band: diff.overallBand,
    seed: Number(item["seed"]),
    mode: opts.mode,
    interactionType: opts.mode === "multiple-choice" ? "multiple-choice" : "free-response",
    genConfig: opts.genConfig ?? { answerType: opts.mode },
    schemaRev: 3,
  };
}

/**
 * Ensure a record carries the canonical `interactionType` field (TD-1).
 *
 * Idempotent: a record that already has a valid interactionType (and schemaRev 3)
 * is returned unchanged in content. Used by the IndexedDB v3 migration and by JSON
 * import so legacy and imported records are normalized identically.
 */
export function ensureInteractionType(rec: BankRecord): BankRecord {
  const valid = rec.interactionType === "free-response" || rec.interactionType === "multiple-choice";
  const interactionType = valid ? rec.interactionType : (rec.mode === "multiple-choice" ? "multiple-choice" : "free-response");
  return { ...rec, interactionType, schemaRev: 3 };
}

/** Apply an editable wording overlay. Returns a new record; `item` is untouched. */
export function withWording(rec: BankRecord, wording: WordingOverlay, now = nowIso()): BankRecord {
  return { ...rec, wording: { ...wording }, modifiedAt: now };
}

/** Change lifecycle state. Returns a new record; `item` is untouched. */
export function withLifecycle(rec: BankRecord, lifecycleState: LifecycleState, now = nowIso()): BankRecord {
  return { ...rec, lifecycleState, modifiedAt: now };
}

/** Duplicate a record as an independent editable copy with a new id. */
export function duplicateRecord(rec: BankRecord, newItemId: string, now = nowIso()): BankRecord {
  return {
    ...rec,
    itemId: newItemId,
    item: { ...rec.item, itemId: newItemId },
    wording: { ...rec.wording },
    tags: [...rec.tags],
    lifecycleState: "draft",
    archived: false,
    createdAt: now,
    modifiedAt: now,
  };
}
