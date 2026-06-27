/**
 * Registry manifest integrity + output-neutrality tests (§11 G8/G12).
 *
 * Asserts: every Phase-1 registry artifact's sha256 in objective_registry_manifest.json
 * matches the file on disk (0 drift); AND the manifest's frozen record of the 11 objective
 * files equals the on-disk sha256 of those files (the output-neutrality guard — proves the
 * approved objective definitions are byte-for-byte unchanged).
 *
 * Run:  node --test core/curriculum/registry-manifest.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const rel = (p: string): string => join(ROOT, p);
const sha256 = (p: string): string => createHash("sha256").update(readFileSync(rel(p))).digest("hex");

const MANIFEST = "docs/review/objective_registry_manifest.json";

interface ArtifactEntry { path: string; sha256: string; present?: boolean }
interface Manifest {
  approvalStatus: string;
  objectiveCount: number;
  gitCommit: string;
  versionTags: { currentImplementationTag: string; approvedTag?: string };
  artifacts: Record<string, ArtifactEntry>;
  frozenObjectiveFiles: Record<string, ArtifactEntry>;
}

const have = existsSync(rel(MANIFEST));
const manifest: Manifest | null = have ? (JSON.parse(readFileSync(rel(MANIFEST), "utf8")) as Manifest) : null;

test("manifest exists and is curriculum-approved (DECISION_LOG #63)", { skip: !have }, () => {
  assert.ok(manifest);
  assert.equal(manifest.approvalStatus, "approved");
  assert.equal(manifest.versionTags.approvedTag, "approved-objective-registry-phase1-v1.0.0");
  assert.equal(manifest.versionTags.currentImplementationTag, "objective-registry-phase1-v1.0.0");
  assert.equal(manifest.objectiveCount, 70);
  assert.match(manifest.gitCommit, /^[0-9a-f]{7,40}$|^unknown$/);
});

test("every registry artifact sha256 matches disk (0 drift)", { skip: !have }, () => {
  for (const [key, entry] of Object.entries(manifest!.artifacts)) {
    assert.ok(existsSync(rel(entry.path)), `${key}: ${entry.path} must exist`);
    assert.equal(sha256(entry.path), entry.sha256, `${key}: ${entry.path} hash drift`);
  }
});

test("OUTPUT-NEUTRALITY: the 11 objective files' sha256 equal the manifest's frozen record", { skip: !have }, () => {
  const frozen = manifest!.frozenObjectiveFiles;
  assert.equal(Object.keys(frozen).length, 11, "exactly 11 objective files must be frozen");
  for (const [name, entry] of Object.entries(frozen)) {
    assert.equal(entry.path, `curriculum/objectives/${name}`);
    assert.equal(sha256(entry.path), entry.sha256, `objective file ${name} has DRIFTED from the frozen record`);
  }
});

test("the alignment schema, pilot, baseline, and reports are all manifested", { skip: !have }, () => {
  const paths = new Set(Object.values(manifest!.artifacts).map((a) => a.path));
  for (const required of [
    "core/curriculum/objective-registry.ts",
    "core/curriculum/registry-graph.ts",
    "core/curriculum/generator-capability.ts",
    "curriculum/registry/known-baseline-referenced-undefined.json",
    "docs/review/objective_registry_gap_report.json",
    "docs/review/objective_coverage_report.json",
    "schemas/standard-alignment.schema.json",
    "curriculum/alignments/pilot.json",
  ]) {
    assert.ok(paths.has(required), `manifest must include ${required}`);
  }
});
