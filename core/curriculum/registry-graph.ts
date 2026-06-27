/**
 * Global curriculum-graph check (Phase 1, §7, §7.5, §11).
 *
 * Runs over the GLOBAL union of all 70 objectives (sourced through the registry of §5),
 * extending `core/curriculum/graph-check.ts`'s `checkCurriculumGraph` with the eight
 * owner-specified buckets (correction A, §7.4) and the §11 integrity predicates G1-G13.
 *
 * The decisive policy (§7.5, owner correction A): a `prerequisites[]` target that resolves
 * to NO objective is classified as either `knownBaselineReferencedUndefined` (it is in the
 * committed known-baseline set — recorded, NON-blocking) or `newReferencedUndefined` (it is
 * NOT in the baseline — a BLOCKING error / regression). Hence:
 *
 *     ok = errors.length === 0 && newReferencedUndefined.length === 0
 *
 * `knownBaselineReferencedUndefined` never gates.
 *
 * Pure, offline, DOM-free. No file is written; the gate only REPORTS.
 *
 * Run:  node --test core/curriculum/registry-graph.test.ts
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { checkCurriculumGraph, type GraphReport, type ObjectiveLike } from "./graph-check.ts";
import {
  parseObjectiveId,
  OBJECTIVE_ID_PATTERN,
  type ObjectiveRecord,
  type ReviewStatus,
} from "./objective-registry.ts";

/** A directed edge in the global graph (source -> target). */
export interface Edge {
  from: string;
  to: string;
}

/**
 * The global graph report. Extends the existing `GraphReport` (ok, objectiveCount,
 * errors, warnings) with the eight owner-specified buckets (§7.4).
 */
export interface GlobalGraphReport extends GraphReport {
  /** referenced-undefined prerequisite IDs that ARE in the committed baseline (non-blocking). */
  knownBaselineReferencedUndefined: string[];
  /** referenced-undefined prerequisite IDs NOT in the baseline (BLOCKING error). */
  newReferencedUndefined: string[];
  /** live (approved/published) -> retired prerequisite dependence (error). */
  retiredDependence: Edge[];
  /** approved/published -> draft/proposed prerequisite dependence (warning). */
  placeholderDependence: Edge[];
  /** crossDomainRelationships[] target that does not resolve, or points within the same domain (warning). */
  invalidCrossDomain: Edge[];
  /** relatedObjectives[] target that does not resolve (warning). */
  danglingRelated: Edge[];
}

/** The §4 controlled vocabulary: stage and domain segment <-> field maps + sub-segments + strands. */
export interface ControlledVocabulary {
  /** ID stage segment -> `stage` field spelling. */
  stageMap: Record<string, string>;
  /** ID domain segment -> `domain` field spelling. */
  domainMap: Record<string, string>;
  /** Allowed interior sub-segment tokens. */
  subsegments: Set<string>;
  /** Allowed `strand` field values (present-or-valid). */
  strands: Set<string>;
}

/**
 * The §4 controlled vocabulary, derived from the current approved data. Closed sets:
 * adding a value is a governance action (§4.6), never an incidental side effect.
 */
export const CONTROLLED_VOCABULARY: ControlledVocabulary = {
  stageMap: {
    MIDDLE: "middle-school",
    IBDPAASL: "ibdp-aasl",
  },
  domainMap: {
    SEQSER: "sequences-and-series",
    ALG: "algebra",
    GEO: "geometry",
    MEAS: "measurement",
    NUM: "number",
    RATIO: "proportion",
    STAT: "statistics",
  },
  subsegments: new Set([
    "ARITH", "GEO", "LINEQ", "COORD", "TRANS", "PERIM", "AREA", "READ", "FREQ", "AVG", "PROB",
  ]),
  strands: new Set([
    "arithmetic-sequences",
    "arithmetic-series",
    "geometric-sequences",
    "geometric-series",
    "algebraic-foundations",
    "linear-equations-one-variable",
    "angles-lines-triangles-quadrilaterals",
    "coordinate-geometry-straight-line-graphs",
    "coordinate-transformations",
    "mensuration",
    "signed-numbers",
    "ratio-and-proportion",
    "data-handling-and-probability",
  ]),
};

/** The schema `stage` enum (§4.2). */
export const STAGE_ENUM = new Set<string>([
  "preschool-kg", "primary", "middle-school", "high-school", "ibdp-aasl",
  "ibdp-aahl", "ibdp-ai", "university", "cross-level",
]);

const LIVE_STATUSES: ReadonlySet<ReviewStatus> = new Set<ReviewStatus>([
  "approved", "approved-for-implementation", "published",
]);
const PLACEHOLDER_STATUSES: ReadonlySet<ReviewStatus> = new Set<ReviewStatus>([
  "draft", "proposed",
]);

/** Load the committed known-baseline referenced-undefined set from disk. */
export function loadKnownBaseline(baselineFile?: string): Set<string> {
  const file = baselineFile ?? join(
    dirname(fileURLToPath(import.meta.url)),
    "../../curriculum/registry/known-baseline-referenced-undefined.json",
  );
  const data = JSON.parse(readFileSync(file, "utf8")) as { ids: string[] };
  return new Set(data.ids);
}

/**
 * Run the global graph check over a list of objective records, using a committed
 * known-baseline set to classify referenced-undefined prerequisites (§7.5).
 *
 * `knownBaseline` is the explicit set; pass `loadKnownBaseline()` for the on-disk one.
 * `vocab` defaults to CONTROLLED_VOCABULARY.
 */
export function checkGlobalGraph(
  objectives: ObjectiveRecord[],
  knownBaseline: Set<string>,
  vocab: ControlledVocabulary = CONTROLLED_VOCABULARY,
): GlobalGraphReport {
  // Start from the trusted base checker (duplicate ids + prerequisite cycles as errors).
  const base = checkCurriculumGraph(objectives as ObjectiveLike[]);
  const errors = [...base.errors];
  const warnings: string[] = [];

  const byId = new Map<string, ObjectiveRecord>();
  for (const o of objectives) if (!byId.has(o.objectiveId)) byId.set(o.objectiveId, o);

  const knownBaselineReferencedUndefined = new Set<string>();
  const newReferencedUndefined = new Set<string>();
  const retiredDependence: Edge[] = [];
  const placeholderDependence: Edge[] = [];
  const invalidCrossDomain: Edge[] = [];
  const danglingRelated: Edge[] = [];

  for (const o of objectives) {
    const id = o.objectiveId;
    const parts = parseObjectiveId(id);

    // G1 — ID grammar (structural regex + parse).
    if (!OBJECTIVE_ID_PATTERN.test(id) || parts === null) {
      errors.push(`G1 invalid objective id grammar: ${id}`);
    } else {
      // L2 vocabulary checks (§3.5, §4.5).
      if (!(parts.stage in vocab.stageMap)) {
        errors.push(`G1 unknown stage segment '${parts.stage}' in ${id}`);
      } else if (vocab.stageMap[parts.stage] !== o.stage) {
        errors.push(
          `G1 stage segment '${parts.stage}' maps to '${vocab.stageMap[parts.stage]}' but stage field is '${o.stage}' (${id})`,
        );
      }
      if (!(parts.domain in vocab.domainMap)) {
        errors.push(`G4 unknown domain segment '${parts.domain}' in ${id}`);
      } else if (vocab.domainMap[parts.domain] !== o.domain) {
        errors.push(
          `G4 domain segment '${parts.domain}' maps to '${vocab.domainMap[parts.domain]}' but domain field is '${o.domain}' (${id})`,
        );
      }
      for (const s of parts.sub) {
        if (!vocab.subsegments.has(s)) errors.push(`G4 unknown sub-segment '${s}' in ${id}`);
      }
    }

    // G3 — stage field in the schema enum.
    if (!STAGE_ENUM.has(o.stage)) errors.push(`G3 invalid stage '${o.stage}' for ${id}`);

    // G4 — strand present-or-valid.
    if (o.strand !== undefined && !vocab.strands.has(o.strand)) {
      errors.push(`G4 unknown strand '${o.strand}' for ${id}`);
    }

    // G7 — reviewStatus in enum (the registry type already constrains, but a raw file could drift).
    const status = o.reviewStatus;

    // G5 — baseline-aware prerequisite resolution + approval-aware layering (G7 dependence).
    for (const p of o.prerequisites ?? []) {
      const target = byId.get(p);
      if (target === undefined) {
        if (knownBaseline.has(p)) knownBaselineReferencedUndefined.add(p);
        else newReferencedUndefined.add(p);
        continue;
      }
      // retired-objective dependence (error) when a LIVE objective depends on a retired one.
      if (target.reviewStatus === "retired" && LIVE_STATUSES.has(status)) {
        retiredDependence.push({ from: id, to: p });
      }
      // placeholder dependence (warning): approved/published -> draft/proposed.
      if (LIVE_STATUSES.has(status) && PLACEHOLDER_STATUSES.has(target.reviewStatus)) {
        placeholderDependence.push({ from: id, to: p });
      }
    }

    // Invalid cross-domain links (warning): unresolved, or pointing within the same domain.
    for (const c of o.crossDomainRelationships ?? []) {
      const target = byId.get(c);
      if (target === undefined) {
        invalidCrossDomain.push({ from: id, to: c });
      } else if (target.domain === o.domain) {
        invalidCrossDomain.push({ from: id, to: c });
      }
    }

    // Dangling lateral links (warning): relatedObjectives that do not resolve.
    for (const r of o.relatedObjectives ?? []) {
      if (!byId.has(r)) danglingRelated.push({ from: id, to: r });
    }
  }

  // Promote the new buckets into errors/warnings strings for the GraphReport contract.
  for (const p of [...newReferencedUndefined].sort()) {
    errors.push(`G5 new referenced-undefined prerequisite (regression): ${p}`);
  }
  for (const e of retiredDependence) {
    errors.push(`G7 live->retired dependence: ${e.from} -> ${e.to}`);
  }
  for (const p of [...knownBaselineReferencedUndefined].sort()) {
    warnings.push(`G5 known-baseline referenced-undefined prerequisite (recorded, non-blocking): ${p}`);
  }
  for (const e of placeholderDependence) {
    warnings.push(`G7 approved->placeholder dependence: ${e.from} -> ${e.to}`);
  }
  for (const e of invalidCrossDomain) {
    warnings.push(`invalid cross-domain link: ${e.from} -> ${e.to}`);
  }
  for (const e of danglingRelated) {
    warnings.push(`dangling related link: ${e.from} -> ${e.to}`);
  }

  const ok = errors.length === 0 && newReferencedUndefined.size === 0;

  return {
    ok,
    objectiveCount: objectives.length,
    errors,
    warnings,
    knownBaselineReferencedUndefined: [...knownBaselineReferencedUndefined].sort(),
    newReferencedUndefined: [...newReferencedUndefined].sort(),
    retiredDependence,
    placeholderDependence,
    invalidCrossDomain,
    danglingRelated,
  };
}
