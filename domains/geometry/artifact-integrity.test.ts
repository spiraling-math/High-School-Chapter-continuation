/**
 * Blocking artifact-integrity test (TypeScript side).
 *
 * Confirms the generated geometry review pack + visual audit carry the CURRENT generator
 * version and a consistent build commit, contain no stale version text, and match the
 * SHA-256 hashes recorded in the generation manifest. Parses the actual serialized files.
 *
 * Run:  node --test domains/geometry/artifact-integrity.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { GENERATOR_VERSION } from "./angles.ts";
import { sha256CanonicalFile } from "../../core/integrity/canonical-hash.ts";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const rel = (p: string): string => ROOT + p;
const readText = (p: string): string => readFileSync(rel(p), "utf8");
const MANIFEST = "docs/review/geometry_manifest.json";
const AUDIT = "docs/review/geometry_visual_audit.html";
const PACK_MD = "docs/review/geometry_angles_review_pack.md";
const PACK_JSON = "docs/review/geometry_angles_review_pack.json";

const haveManifest = existsSync(rel(MANIFEST));

test("audit-version-matches-generator: pack/audit/manifest state the current version", { skip: !haveManifest }, () => {
  const man = JSON.parse(readText(MANIFEST)) as { generatorVersion: string; gitCommit: string; sha256: Record<string, string> };
  assert.equal(man.generatorVersion, GENERATOR_VERSION, "manifest version == generator version");
  const ver = /data-generator-version="([^"]+)"/.exec(readText(AUDIT))?.[1];
  assert.equal(ver, GENERATOR_VERSION, "audit version == generator version");
  assert.ok(readText(PACK_MD).includes(GENERATOR_VERSION), "review pack states the current version");
});

test("audit-commit-matches-build: audit commit equals the manifest build commit", { skip: !haveManifest }, () => {
  const man = JSON.parse(readText(MANIFEST)) as { gitCommit: string };
  const com = /data-git-commit="([^"]+)"/.exec(readText(AUDIT))?.[1];
  assert.equal(com, man.gitCommit, "audit commit == manifest commit");
  assert.match(String(com), /^[0-9a-f]{7,40}$/, "a real git commit hash");
});

test("no-stale-version-text: artifacts reference only the current version (+ v1.2.0 baseline)", { skip: !haveManifest }, () => {
  for (const p of [AUDIT, PACK_MD, PACK_JSON]) {
    const txt = readText(p);
    for (const stale of ["1.2.1", "1.2.2"]) assert.ok(!txt.includes(stale), `stale version ${stale} in ${p}`);
    assert.ok(txt.includes(GENERATOR_VERSION), `${p} states the current version`);
  }
});

test("manifest SHA-256 hashes match the serialized files", { skip: !haveManifest }, () => {
  const man = JSON.parse(readText(MANIFEST)) as { sha256: Record<string, string> };
  const files: Record<string, string> = {
    reviewPackMd: PACK_MD, reviewPackJson: PACK_JSON, visualAudit: AUDIT,
    goldenFixture: "oracle/golden/geometry_angles.golden.json",
    parityFixture: "oracle/golden/geometry_angles.parity.json",
  };
  for (const [key, p] of Object.entries(files)) {
    const digest = sha256CanonicalFile(rel(p)); // canonical (CRLF→LF): same on Windows working trees + LF git bytes
    assert.equal(digest, man.sha256[key], `manifest hash stale for ${p}`);
  }
});
