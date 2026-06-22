/**
 * Question-bank JSON export/import with round-trip validation.
 *
 * Export produces a canonical (stable-key-order) JSON document. Import re-parses
 * it, re-validates each item's mathematics, and performs an INTEGRITY check by
 * regenerating each item from its stored seed + exact generation config and
 * confirming byte-for-byte canonical equality (ignoring only the itemId, which a
 * duplicate intentionally renames). Re-exporting imported records yields an
 * identical document.
 */

import { canonicalStringify, type Json } from "../../core/serialization/canonical.ts";
import { GENERATORS } from "../../core/sdk/sequence-registry.ts";
import { ensureInteractionType } from "../../core/bank/record.ts";
import { assertValidItem, validateItem, formatErrors } from "../../core/schema/runtime-validate.ts";
import type { BankRecord, Mode } from "../../core/bank/types.ts";

const FORMAT = "spi-math-bank";
const FORMAT_VERSION = "1.0.0";

export function exportBankJson(records: BankRecord[]): string {
  for (const r of records) assertValidItem(r.item, `bank export ${r.itemId}`);
  const doc = { format: FORMAT, version: FORMAT_VERSION, records };
  return canonicalStringify(doc as unknown as Json);
}

export interface ImportResult {
  records: BankRecord[];
  errors: string[];
  integrityOk: boolean;
}

export function importBankJson(text: string): ImportResult {
  const errors: string[] = [];
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch (e) {
    return { records: [], errors: [`Invalid JSON: ${(e as Error).message}`], integrityOk: false };
  }
  const doc = parsed as { format?: string; records?: unknown };
  if (doc.format !== FORMAT || !Array.isArray(doc.records)) {
    return { records: [], errors: ["Not an SPI-Math bank file"], integrityOk: false };
  }

  // Normalize legacy/imported records to the canonical interactionType (TD-1). Idempotent.
  const records = (doc.records as BankRecord[]).map(ensureInteractionType);
  let integrityOk = true;

  records.forEach((r, i) => {
    if (!r.itemId || !r.item || typeof r.seed !== "number") {
      errors.push(`record ${i}: missing required fields`);
      integrityOk = false;
      return;
    }
    const schemaErrs = validateItem(r.item);
    if (schemaErrs.length > 0) {
      errors.push(`record ${i} (${r.itemId}): schema ${formatErrors(schemaErrs)}`);
      integrityOk = false;
    }
    // Resolve the generator by its stored id so every family (sequences, algebra,
    // geometry) re-validates and regenerates with its own oracle-mirrored code.
    const gen = GENERATORS.find((g) => g.id === r.item["generatorId"]);
    if (!gen) {
      errors.push(`record ${i} (${r.itemId}): unknown generator ${String(r.item["generatorId"])}`);
      integrityOk = false;
      return;
    }
    const v = gen.validate(r.item);
    if (v.status !== "pass") {
      errors.push(`record ${i} (${r.itemId}): item validation ${v.status}`);
      integrityOk = false;
    }
    try {
      const cfg = (r.genConfig ?? { answerType: r.mode }) as { answerType: Mode; task?: string };
      const regen = gen.generate(r.seed, cfg);
      const fixed = { ...regen, itemId: r.item["itemId"] as Json };
      if (gen.serialize(fixed) !== gen.serialize(r.item)) {
        errors.push(`record ${i} (${r.itemId}): does not reproduce from seed + config`);
        integrityOk = false;
      }
    } catch (e) {
      errors.push(`record ${i} (${r.itemId}): regenerate failed: ${(e as Error).message}`);
      integrityOk = false;
    }
  });

  return { records, errors, integrityOk };
}
