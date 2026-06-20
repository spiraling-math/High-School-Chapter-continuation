/**
 * Canonical JSON serialization.
 *
 * Produces the byte-for-byte counterpart of the Python oracle's
 * `json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))`:
 *   - object keys sorted lexicographically (ASCII keys => identical to Python),
 *   - no insignificant whitespace,
 *   - UTF-8 text, non-ASCII left literal.
 *
 * This is the form hashed for `contentHash` and compared in cross-language
 * reproducibility tests, so it MUST match the oracle exactly.
 */

export type Json =
  | null
  | boolean
  | number
  | string
  | Json[]
  | { [key: string]: Json };

export function canonicalStringify(value: Json): string {
  if (value === null) return "null";
  const t = typeof value;
  if (t === "number") {
    if (!Number.isFinite(value as number)) {
      throw new Error("canonicalStringify: non-finite number");
    }
    return JSON.stringify(value);
  }
  if (t === "boolean" || t === "string") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return "[" + value.map(canonicalStringify).join(",") + "]";
  }
  if (t === "object") {
    const obj = value as { [key: string]: Json };
    const keys = Object.keys(obj).sort();
    const parts = keys.map(
      (k) => JSON.stringify(k) + ":" + canonicalStringify(obj[k] as Json),
    );
    return "{" + parts.join(",") + "}";
  }
  throw new Error(`canonicalStringify: unsupported value of type ${t}`);
}
