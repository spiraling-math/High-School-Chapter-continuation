/**
 * Unified objective registry / index (Phase 1, read-only).
 *
 * A derived READ LAYER over the `curriculum/objectives/*.json` source-of-truth files
 * (the eleven frozen approved files plus any proposed pending-review family files). It loads every objective into one in-memory index keyed by `objectiveId` and
 * exposes a small, stable, read-only query surface (§5 of the Objective Registry &
 * Standards proposal). It NEVER writes any objective file: the per-family JSON files
 * remain the single source of truth for definitions; this registry only indexes them.
 *
 * It also parses the variable-depth ID grammar `SPI.<STAGE>.<DOMAIN>[.<SUB>].<MICRO>.<NN>`
 * (§3) so the graph/coverage layers and the integrity gate can reason about ID structure
 * without re-implementing the parser.
 *
 * DOM-free; usable in tests and offline tooling.
 *
 * Run a smoke check:  node --test core/curriculum/objective-registry.test.ts
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

/**
 * The ONLY hand-maintained lists of objective files. Identity is the `objectiveId`,
 * never the filename (§2.1), but the loader still needs to know which files to read.
 *
 * APPROVED_OBJECTIVE_FILES is the frozen Phase-1 set (eleven files, 70 curriculum-approved
 * objectives). PROPOSED_OBJECTIVE_FILES holds families whose objectives are `reviewStatus:
 * proposed` (indexed so the graph, coverage and integrity gates see them, but NOT part of
 * the approved baseline; promotion to the approved list is an owner governance action).
 */
export const APPROVED_OBJECTIVE_FILES = [
  "SPI.IBDPAASL.SEQSER.ARITH.json",
  "SPI.IBDPAASL.SEQSER.GEO.json",
  "SPI.MIDDLE.ALG.FOUNDATIONS.json",
  "SPI.MIDDLE.ALG.LINEQ.json",
  "SPI.MIDDLE.GEO.json",
  "SPI.MIDDLE.GEO.COORD.json",
  "SPI.MIDDLE.GEO.TRANS.json",
  "SPI.MIDDLE.MEAS.json",
  "SPI.MIDDLE.NUM.json",
  "SPI.MIDDLE.RATIO.json",
  "SPI.MIDDLE.STAT.json",
] as const;

/** Proposed (pending-review) objective files — gen.functions.foundations (DECISION_LOG.md #65). */
export const PROPOSED_OBJECTIVE_FILES = [
  "SPI.IBDPAASL.FUNC.json",
] as const;

/** Every indexed objective file: the approved baseline followed by the proposed families. */
export const OBJECTIVE_FILES: readonly string[] = [...APPROVED_OBJECTIVE_FILES, ...PROPOSED_OBJECTIVE_FILES];

/** The objective lifecycle states (the schema `reviewStatus` enum, §6). */
export type ReviewStatus =
  | "draft"
  | "proposed"
  | "curriculum-reviewed"
  | "approved"
  | "approved-for-implementation"
  | "published"
  | "revised"
  | "retired";

/** An inline external-alignment record (the existing, frozen `{framework, code, label?}` hook). */
export interface InlineAlignment {
  framework: string;
  code: string;
  label?: string;
}

/**
 * An objective record as it appears in the source JSON. Authoritative fields only;
 * mirrored verbatim from the file (no reformatting, no derived state injected here).
 */
export interface ObjectiveRecord {
  objectiveId: string;
  stage: string;
  domain: string;
  strand?: string;
  topic?: string;
  subtopic?: string;
  microSkill?: string;
  objectiveWording: string;
  answerTypes: string[];
  difficultyRange?: { min: number; max: number };
  prerequisites?: string[];
  relatedObjectives?: string[];
  crossDomainRelationships?: string[];
  externalAlignments?: InlineAlignment[];
  reviewStatus: ReviewStatus;
  version: string;
  /** Provenance: which file this record was read from (traceability only). */
  sourceFile: string;
  /** Any other authoritative fields present in the source, preserved untouched. */
  [extra: string]: unknown;
}

/** The parsed pieces of a variable-depth objective ID (§3). */
export interface IdParts {
  stage: string;
  domain: string;
  sub: string[];
  micro: string;
  nn: string;
}

/**
 * The normative structural ID pattern — adopted unchanged from
 * `schemas/curriculum-objective.schema.json` (§3.5). Structure only, not vocabulary.
 */
export const OBJECTIVE_ID_PATTERN = /^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$/;

/**
 * Parse a variable-depth objective ID. Returns null if the structure is invalid.
 * Grammar: SPI . STAGE . DOMAIN . {SUB} . MICRO . NN  (5 or 6+ segments).
 */
export function parseObjectiveId(id: string): IdParts | null {
  if (!OBJECTIVE_ID_PATTERN.test(id)) return null;
  const segs = id.split(".");
  // segs[0] === "SPI"; last segment is NN; segs[1] is stage; segs[2] is domain.
  // Interior (segs[3 .. n-2]) are sub-segments; segs[n-1] is the micro-skill.
  if (segs.length < 5) return null;
  const nn = segs[segs.length - 1]!;
  const micro = segs[segs.length - 2]!;
  const stage = segs[1]!;
  const domain = segs[2]!;
  const sub = segs.slice(3, segs.length - 2);
  return { stage, domain, sub, micro, nn };
}

/** The immutable, read-only registry surface. */
export interface ObjectiveRegistry {
  /** Every objective, in load order. */
  all(): ObjectiveRecord[];
  /** Lookup by id; undefined if absent. */
  byId(id: string): ObjectiveRecord | undefined;
  /** True if the id resolves to a loaded objective. */
  has(id: string): boolean;
  /** All objectives at a stage field value (e.g. "middle-school"). */
  byStage(stage: string): ObjectiveRecord[];
  /** All objectives in a domain field value (e.g. "proportion"). */
  byDomain(domain: string): ObjectiveRecord[];
  /** All objectives in a strand field value (e.g. "ratio-and-proportion"). */
  byStrand(strand: string): ObjectiveRecord[];
  /** Total count. */
  readonly count: number;
}

function readObjectiveFiles(objDir: string): ObjectiveRecord[] {
  const out: ObjectiveRecord[] = [];
  for (const name of OBJECTIVE_FILES) {
    const raw = readFileSync(join(objDir, name), "utf8");
    const records = JSON.parse(raw) as Record<string, unknown>[];
    if (!Array.isArray(records)) {
      throw new Error(`objective file ${name} is not a JSON array`);
    }
    for (const r of records) {
      out.push({ ...(r as ObjectiveRecord), sourceFile: name });
    }
  }
  return out;
}

/** Default objectives directory, resolved relative to this module. */
export function defaultObjectivesDir(): string {
  return join(dirname(fileURLToPath(import.meta.url)), "../../curriculum/objectives");
}

/**
 * Build a registry from an explicit list of records (no disk I/O). Used by the
 * loader and by tests that need to exercise the query surface on synthetic data.
 */
export function buildRegistry(records: ObjectiveRecord[]): ObjectiveRegistry {
  const index = new Map<string, ObjectiveRecord>();
  for (const r of records) {
    // First-wins on duplicate ids at the index level; duplicate detection is the
    // graph layer's job (it reports duplicates as errors, §11 G2).
    if (!index.has(r.objectiveId)) index.set(r.objectiveId, r);
  }
  return {
    all: () => records.slice(),
    byId: (id) => index.get(id),
    has: (id) => index.has(id),
    byStage: (stage) => records.filter((r) => r.stage === stage),
    byDomain: (domain) => records.filter((r) => r.domain === domain),
    byStrand: (strand) => records.filter((r) => r.strand === strand),
    count: records.length,
  };
}

/**
 * Load the registry from disk (every indexed source file). Pure read: no file is written
 * and no record is reformatted. Returns an immutable, queryable registry.
 */
export function loadRegistry(objectivesDir?: string): ObjectiveRegistry {
  const dir = objectivesDir ?? defaultObjectivesDir();
  return buildRegistry(readObjectiveFiles(dir));
}

/** Convenience: load just the flat array of objective records from disk. */
export function loadObjectives(objectivesDir?: string): ObjectiveRecord[] {
  return readObjectiveFiles(objectivesDir ?? defaultObjectivesDir());
}
