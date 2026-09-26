/**
 * Blocking artifact-integrity test (TypeScript side) for coordinate-lines v1.0.0.
 * Confirms the review pack + visual audit carry the current generator version and a
 * consistent build commit, reference no other generator version, and match the manifest
 * SHA-256 hashes. Run:  node --test domains/geometry/coordinate-lines-integrity.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { GENERATOR_VERSION } from "./coordinate-lines.ts";
import { sha256CanonicalFile } from "../../core/integrity/canonical-hash.ts";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const rel = (p: string): string => ROOT + p;
const readText = (p: string): string => readFileSync(rel(p), "utf8");
const MANIFEST = "docs/review/coordinate_lines_manifest.json";
const AUDIT = "docs/review/coordinate_lines_visual_audit.html";
const PACK_MD = "docs/review/coordinate_lines_review_pack.md";
const PACK_JSON = "docs/review/coordinate_lines_review_pack.json";
const have = existsSync(rel(MANIFEST));

test("audit + manifest state the current version", { skip: !have }, () => {
  const man = JSON.parse(readText(MANIFEST)) as { generatorVersion: string };
  assert.equal(man.generatorVersion, GENERATOR_VERSION);
  assert.equal(/data-generator-version="([^"]+)"/.exec(readText(AUDIT))?.[1], GENERATOR_VERSION);
  assert.ok(readText(PACK_MD).includes(GENERATOR_VERSION));
});

test("audit commit equals the manifest build commit", { skip: !have }, () => {
  const man = JSON.parse(readText(MANIFEST)) as { gitCommit: string };
  const com = /data-git-commit="([^"]+)"/.exec(readText(AUDIT))?.[1];
  assert.equal(com, man.gitCommit);
  assert.match(String(com), /^[0-9a-f]{7,40}$/);
});

test("artifacts state the current version and no other generator version", { skip: !have }, () => {
  for (const p of [AUDIT, PACK_MD]) {
    const txt = readText(p);
    assert.ok(txt.includes(GENERATOR_VERSION), `${p} must state the current version`);
    for (const stale of ["1.0.0", "1.0.1", "1.1.0", "1.2.0", "1.2.1", "1.2.2", "1.2.3"]) assert.ok(!txt.includes(stale), `${stale} in ${p}`);
  }
});

test("manifest SHA-256 hashes match the serialized files", { skip: !have }, () => {
  const man = JSON.parse(readText(MANIFEST)) as { sha256: Record<string, string> };
  const files: Record<string, string> = {
    reviewPackMd: PACK_MD, reviewPackJson: PACK_JSON, visualAudit: AUDIT,
    goldenFixture: "oracle/golden/coordinate_lines.golden.json",
    parityFixture: "oracle/golden/coordinate_lines.parity.json",
  };
  for (const [key, p] of Object.entries(files)) {
    // canonical (CRLF→LF) hash: identical on a Windows working tree and on the LF bytes git stores
    assert.equal(sha256CanonicalFile(rel(p)), man.sha256[key], `hash for ${p}`);
  }
});
