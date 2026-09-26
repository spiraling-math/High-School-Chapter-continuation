/**
 * Contract tests for canonical artifact hashing (core/integrity/canonical-hash.ts).
 *
 * Pins: CRLF and LF encodings of one text hash identically (and equal the plain SHA-256 of the LF
 * bytes git stores); a lone CR is preserved; binary is never rewritten; the file variant agrees with
 * the bytes variant. The Python mirror (oracle/build_meta.py) is held to the same vectors by
 * oracle/tests/test_build_meta.py.
 *
 * Run:  node --test core/integrity/canonical-hash.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { canonicalTextBytes, sha256CanonicalBytes, sha256CanonicalFile } from "./canonical-hash.ts";

const plainSha256 = (b: Uint8Array): string => createHash("sha256").update(b).digest("hex");
const bytes = (s: string): Uint8Array => Buffer.from(s, "utf8");

test("CRLF and LF encodings of the same text hash identically, to the plain sha256 of the LF bytes", () => {
  const lf = bytes('{\n  "a": 1,\n  "b": "x"\n}\n');
  const crlf = bytes('{\r\n  "a": 1,\r\n  "b": "x"\r\n}\r\n');
  assert.equal(sha256CanonicalBytes(crlf), sha256CanonicalBytes(lf));
  assert.equal(sha256CanonicalBytes(lf), plainSha256(lf));
  assert.notEqual(plainSha256(crlf), plainSha256(lf), "the raw digests differ — that is the defect being neutralised");
});

test("no trailing newline: the final line's CR is dropped too", () => {
  assert.equal(sha256CanonicalBytes(bytes("a\r\nb")), sha256CanonicalBytes(bytes("a\nb")));
});

test("a lone CR is preserved (exactly as git leaves it)", () => {
  const loneCr = bytes("a\rb\n");
  assert.deepEqual(Buffer.from(canonicalTextBytes(loneCr)), Buffer.from(loneCr));
  assert.equal(sha256CanonicalBytes(loneCr), plainSha256(loneCr));
  assert.notEqual(sha256CanonicalBytes(loneCr), sha256CanonicalBytes(bytes("a\nb\n")));
});

test("binary (NUL in the first 8000 bytes) is never rewritten, even when it contains CRLF", () => {
  const bin = Buffer.concat([Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00]), bytes("x\r\ny")]);
  assert.deepEqual(Buffer.from(canonicalTextBytes(bin)), bin);
  assert.equal(sha256CanonicalBytes(bin), plainSha256(bin));
});

test("already-canonical input is returned as-is (fast path) and mixed endings normalise fully", () => {
  const lf = bytes("one\ntwo\n");
  assert.equal(canonicalTextBytes(lf), lf, "same reference when nothing to do");
  assert.equal(sha256CanonicalBytes(bytes("one\r\ntwo\nthree\r\n")), sha256CanonicalBytes(bytes("one\ntwo\nthree\n")));
});

test("sha256CanonicalFile agrees with sha256CanonicalBytes across a CRLF file on disk", () => {
  const dir = mkdtempSync(join(tmpdir(), "spi-canonical-hash-"));
  try {
    const p = join(dir, "artifact.json");
    writeFileSync(p, '{\r\n  "k": 1\r\n}\r\n');
    assert.equal(sha256CanonicalFile(p), sha256CanonicalBytes(bytes('{\n  "k": 1\n}\n')));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
