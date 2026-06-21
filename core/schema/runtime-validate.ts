/**
 * Runtime schema validation at trust boundaries.
 *
 * Validates question items against the JSON Schema (the single source of truth)
 * using a build-time PRECOMPILED standalone validator — no runtime code
 * generation, no network. Errors are reported with the schema path, the failing
 * field, the expected form, the received form, and the item/generator id.
 *
 * This is a STRUCTURAL gate. It never repairs data: mathematically meaningful
 * invalid data is surfaced as an error, never silently corrected.
 */

import validateQuestionItem from "./compiled/question-item.validator.mjs";
import type { Json } from "../serialization/canonical.ts";

export interface SchemaError {
  schemaPath: string;
  field: string;
  message: string;
  expected: string;
  received: string;
  itemId: string;
  generatorId: string;
}

/** Resolve the value at an Ajv instancePath (RFC6901 JSON pointer). */
function valueAt(root: unknown, instancePath: string): unknown {
  if (!instancePath) return root;
  const parts = instancePath.split("/").slice(1).map((p) => p.replace(/~1/g, "/").replace(/~0/g, "~"));
  let cur: unknown = root;
  for (const p of parts) {
    if (cur == null || typeof cur !== "object") return undefined;
    cur = (cur as Record<string, unknown>)[p];
  }
  return cur;
}

function describeExpected(e: { keyword: string; params: Record<string, unknown> }): string {
  const p = e.params;
  switch (e.keyword) {
    case "required": return `property '${String(p["missingProperty"])}' to be present`;
    case "additionalProperties": return `no unknown property (got '${String(p["additionalProperty"])}')`;
    case "type": return `type ${String(p["type"])}`;
    case "enum": return `one of ${JSON.stringify(p["allowedValues"])}`;
    case "const": return `value ${JSON.stringify(p["allowedValue"])}`;
    case "minItems": return `at least ${String(p["limit"])} item(s)`;
    case "minimum": return `>= ${String(p["limit"])}`;
    case "maximum": return `<= ${String(p["limit"])}`;
    case "pattern": return `to match ${String(p["pattern"])}`;
    default: return `${e.keyword} ${JSON.stringify(p)}`;
  }
}

function describeReceived(value: unknown): string {
  if (value === undefined) return "(absent)";
  const s = JSON.stringify(value);
  return s.length > 120 ? s.slice(0, 117) + "..." : s;
}

/** Validate one item; returns [] when valid, else a list of rich errors. */
export function validateItem(item: Record<string, Json>): SchemaError[] {
  const ok = validateQuestionItem(item);
  if (ok) return [];
  const itemId = String(item["itemId"] ?? "(no itemId)");
  const generatorId = String(item["generatorId"] ?? "(no generatorId)");
  return (validateQuestionItem.errors ?? []).map((e) => ({
    schemaPath: e.schemaPath,
    field: e.instancePath || "(root)",
    message: e.message ?? "schema violation",
    expected: describeExpected(e),
    received: describeReceived(valueAt(item, e.instancePath)),
    itemId,
    generatorId,
  }));
}

export class SchemaValidationError extends Error {
  readonly errors: SchemaError[];
  constructor(errors: SchemaError[], context: string) {
    super(`Schema validation failed at ${context}: ${formatErrors(errors)}`);
    this.name = "SchemaValidationError";
    this.errors = errors;
  }
}

/** Throw a SchemaValidationError if the item is structurally invalid. */
export function assertValidItem(item: Record<string, Json>, context = "item"): void {
  const errors = validateItem(item);
  if (errors.length > 0) throw new SchemaValidationError(errors, context);
}

/** Human-readable one-line-per-error rendering. */
export function formatErrors(errors: SchemaError[]): string {
  return errors
    .map((e) => `[${e.itemId}] ${e.field} (${e.schemaPath}): expected ${e.expected}, received ${e.received}`)
    .join("; ");
}
