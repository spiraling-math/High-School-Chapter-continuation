/**
 * Canonical artifact hashing — the ONE SHA-256 every frozen manifest and integrity test uses.
 *
 * The repository stores text files with LF line endings (`.gitattributes`: `* text=auto eol=lf`),
 * but a Windows working tree can hold CRLF copies of the very same files (editors and Python's
 * text-mode writers emit CRLF; git normalises them back to LF on commit, so `git status` stays
 * clean). Line endings are therefore a checkout artefact, not artefact content — and a frozen
 * manifest digest must be identical on both sides. So we hash the CANONICAL bytes:
 *
 *   - text: every CRLF pair becomes LF (a lone CR is preserved, exactly as git leaves it);
 *   - binary (a NUL byte in the first 8000 bytes — git's own text/binary heuristic): untouched.
 *
 * Python mirror: `oracle/build_meta.py` (`canonical_text_bytes` / `sha256_canonical`). Both must
 * agree byte-for-byte; `canonical-hash.test.ts` pins the contract.
 *
 * Run tests:  node --test core/integrity/canonical-hash.test.ts
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

const CR = 13;
const LF = 10;
const BINARY_PROBE_BYTES = 8000;

/** The canonical (repository) bytes of an artifact: CRLF → LF for text, untouched for binary. */
export function canonicalTextBytes(data: Uint8Array): Uint8Array {
  if (data.subarray(0, BINARY_PROBE_BYTES).includes(0)) return data; // binary: never rewritten
  if (!data.includes(CR)) return data; // fast path: already canonical
  const out = new Uint8Array(data.length);
  let n = 0;
  for (let i = 0; i < data.length; i++) {
    const b = data[i]!;
    if (b === CR && data[i + 1] === LF) continue; // drop the CR of a CRLF pair; keep a lone CR
    out[n++] = b;
  }
  return out.subarray(0, n);
}

/** SHA-256 (hex) of the canonical bytes of `data`. */
export function sha256CanonicalBytes(data: Uint8Array): string {
  return createHash("sha256").update(canonicalTextBytes(data)).digest("hex");
}

/** SHA-256 (hex) of the canonical bytes of the file at `path` (absolute, or relative to cwd). */
export function sha256CanonicalFile(path: string): string {
  return sha256CanonicalBytes(readFileSync(path));
}
