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
    genConfig: opts.genConfig ?? { answerType: opts.mode },
    schemaRev: 2,
  };
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
