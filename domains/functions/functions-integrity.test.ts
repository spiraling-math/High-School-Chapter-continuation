/**
 * Blocking artifact-integrity test (TypeScript side) for gen.functions.foundations v1.0.0 (PENDING-REVIEW).
 * Confirms the manifest states the current generator version and the pending-review posture (hidden from
 * normal Studio + production), that every manifested artifact matches its canonical (CRLF→LF) SHA-256, and
 * that the review pack + distribution carry the current version with full coverage and zero invalid items.
 * Run:  node --test domains/functions/functions-integrity.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { GENERATOR_VERSION, VALIDATOR_VERSION, GENERATOR_ID } from "./functions.ts";
import { sha256CanonicalFile } from "../../core/integrity/canonical-hash.ts";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const rel = (p: string): string => ROOT + p;
const readText = (p: string): string => readFileSync(rel(p), "utf8");
const MANIFEST = "docs/review/functions_manifest.json";
const PACK_MD = "docs/review/functions_review_pack.md";
const PACK_JSON = "docs/review/functions_review_pack.json";
const DIST = "docs/review/functions_distribution.json";
const have = existsSync(rel(MANIFEST));

interface Manifest {
  generatorId: string; generatorVersion: string; validatorVersion: string; approvalStatus: string;
  objectiveReviewStatus: string; hiddenFromNormalStudioAndProduction: boolean; gitCommit: string;
  versionTags: { currentImplementationTag: string; approvedTag: string | null };
  artifacts: Record<string, { path: string; sha256: string | null; present: boolean }>;
}

test("manifest states the current version and the pending-review posture", { skip: !have }, () => {
  const man = JSON.parse(readText(MANIFEST)) as Manifest;
  assert.equal(man.generatorId, GENERATOR_ID);
  assert.equal(man.generatorVersion, GENERATOR_VERSION);
  assert.equal(man.validatorVersion, VALIDATOR_VERSION);
  assert.equal(man.approvalStatus, "pending-review");
  assert.equal(man.objectiveReviewStatus, "proposed");
  assert.equal(man.hiddenFromNormalStudioAndProduction, true);
  assert.equal(man.versionTags.approvedTag, null, "no approved tag may exist before the owner approves");
  assert.equal(man.versionTags.currentImplementationTag, `functions-v${GENERATOR_VERSION}`);
  assert.match(man.gitCommit, /^[0-9a-f]{7,40}$/);
});

test("every manifested artifact is present and matches its canonical SHA-256 (0 drift)", { skip: !have }, () => {
  const man = JSON.parse(readText(MANIFEST)) as Manifest;
  for (const [key, entry] of Object.entries(man.artifacts)) {
    assert.ok(entry.present, `${key}: ${entry.path} must be present`);
    assert.ok(existsSync(rel(entry.path)), `${key}: ${entry.path} must exist`);
    // canonical (CRLF→LF) hash: identical on a Windows working tree and on the LF bytes git stores
    assert.equal(sha256CanonicalFile(rel(entry.path)), entry.sha256, `${key}: ${entry.path} hash drift`);
  }
  for (const required of ["oracleGenerator", "tsGenerator", "golden", "parity", "checkerCorpus", "objectives",
    "schema", "compiledValidator", "misconceptionsJson", "distribution", "reviewPackJson", "reviewPackMd", "specificationProposal"]) {
    assert.ok(required in man.artifacts, `manifest must include ${required}`);
  }
});

test("review pack + distribution carry the current version; full coverage; zero invalid; pending-review", { skip: !have }, () => {
  const md = readText(PACK_MD);
  assert.ok(md.includes(`v${GENERATOR_VERSION}`), "review pack must state the current version");
  assert.ok(md.includes("PENDING-REVIEW"), "review pack must be marked PENDING-REVIEW");
  const pack = JSON.parse(readText(PACK_JSON)) as Record<string, unknown>;
  assert.equal(pack.generatorVersion, GENERATOR_VERSION);
  assert.equal(pack.approvalStatus, "pending-review");
  assert.equal(pack.allCovered, true);
  assert.equal(pack.allValid, true);
  assert.equal(pack.allExemplarsComplete, true);
  const misc = pack.misconceptions as { total: number; exercised: number; unexercised: string[] };
  assert.equal(misc.total, 68);
  assert.equal(misc.exercised, 68);
  assert.deepEqual(misc.unexercised, []);
  const matrix = pack.answerContractMatrix as Record<string, { allOk: boolean; allCodesReached: boolean }>;
  assert.equal(matrix.expression!.allOk && matrix.expression!.allCodesReached, true);
  assert.equal(matrix.interval!.allOk && matrix.interval!.allCodesReached, true);
  const dist = JSON.parse(readText(DIST)) as { generatorVersion: string; invalidItems: number; sweepSeeds: number; unreachableDeclaredBands: Record<string, number[]> };
  assert.equal(dist.generatorVersion, GENERATOR_VERSION);
  assert.equal(dist.invalidItems, 0);
  assert.equal(dist.sweepSeeds, 10000);
  assert.deepEqual(dist.unreachableDeclaredBands, {});
});
