/**
 * Generator capability + coverage join (Phase 1, §8, §10).
 *
 * Joins the SDK generator registry (`core/sdk/sequence-registry.ts` GENERATORS:
 * id/version/tasks/approvalStatus) with the objective registry (§5) through the
 * 1:1 task -> objective maps, producing the coverage report (§8.4 / §10.3) that
 * partitions the 70 objectives against the generator fleet.
 *
 * Source of the task -> objective resolution:
 *   - the four EXPORTED `core/curriculum/*-objective-ids.ts` OBJECTIVE_BY_TASK maps
 *     (ratio, mensuration, stats, transformations); plus
 *   - five thin join maps below for the families whose OBJECTIVE_BY_TASK is internal
 *     to the domain module (arithmetic, geometric, linear, angles, coordinate-lines).
 * Every value is cross-checked at load against the registry; none is a new source of
 * truth (the registry/objective files remain authoritative). This is the §8.1 join.
 *
 * READ-ONLY: writes nothing back. Coverage is a projection over existing data.
 *
 * Run:  node --test core/curriculum/coverage.test.ts
 */

import { GENERATORS } from "../sdk/sequence-registry.ts";
import { approvalStatusOf, type GeneratorModule } from "../sdk/generator-module.ts";
import { type ObjectiveRegistry, type ObjectiveRecord } from "./objective-registry.ts";
import { loadKnownBaseline } from "./registry-graph.ts";
import { OBJECTIVE_BY_TASK as RATIO_BY_TASK } from "./ratio-objective-ids.ts";
import { OBJECTIVE_BY_TASK as MENS_BY_TASK } from "./mensuration-objective-ids.ts";
import { OBJECTIVE_BY_TASK as STAT_BY_TASK } from "./stats-objective-ids.ts";
import { OBJECTIVE_BY_TASK as TRANS_BY_TASK } from "./transformations-objective-ids.ts";

/** Generator coverage tier per existing objective (the single coverage vocabulary, §5.3). */
export type CoverageTier = "G2_approved" | "G1_pendingOnly" | "G0_noGenerator";

/**
 * task -> objectiveId maps for the five families whose internal OBJECTIVE_BY_TASK
 * is not exported. Verified against the domain modules and the objective files; the
 * coverage builder asserts every value resolves in the registry at load (so drift is
 * caught, never silently absorbed).
 */
const ARITHMETIC_BY_TASK: Record<string, string> = {
  nth_term: "SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01",
  sum_n: "SPI.IBDPAASL.SEQSER.ARITH.SUM_N.01",
  find_d: "SPI.IBDPAASL.SEQSER.ARITH.COMMON_DIFF.01",
  find_n_for_value: "SPI.IBDPAASL.SEQSER.ARITH.TERM_INDEX.01",
};

const GEOMETRIC_BY_TASK: Record<string, string> = {
  nth_term: "SPI.IBDPAASL.SEQSER.GEO.NTH_TERM.01",
  sum_n: "SPI.IBDPAASL.SEQSER.GEO.SUM_N.01",
  find_r: "SPI.IBDPAASL.SEQSER.GEO.COMMON_RATIO.01",
  find_n_for_value: "SPI.IBDPAASL.SEQSER.GEO.TERM_INDEX.01",
  sum_infinite: "SPI.IBDPAASL.SEQSER.GEO.SUM_INFINITE.01",
};

const LINEAR_BY_TASK: Record<string, string> = {
  one_step_add: "SPI.MIDDLE.ALG.LINEQ.ONESTEP_ADD.01",
  one_step_mul: "SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01",
  two_step: "SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01",
  both_sides: "SPI.MIDDLE.ALG.LINEQ.BOTHSIDES.01",
  brackets: "SPI.MIDDLE.ALG.LINEQ.BRACKETS.01",
};

const ANGLES_BY_TASK: Record<string, string> = {
  straight_line_missing_angle: "SPI.MIDDLE.GEO.ANGLES_STRAIGHT_LINE.01",
  triangle_missing_angle: "SPI.MIDDLE.GEO.TRIANGLE_ANGLE_SUM.01",
  isosceles_base_angle: "SPI.MIDDLE.GEO.ISOSCELES_BASE_ANGLES.01",
  vertically_opposite_angle: "SPI.MIDDLE.GEO.VERTICALLY_OPPOSITE_ANGLES.01",
  angles_at_point_missing: "SPI.MIDDLE.GEO.ANGLES_AT_POINT.01",
};

const COORDINATE_BY_TASK: Record<string, string> = {
  read_point: "SPI.MIDDLE.GEO.COORD.READ_POINT.01",
  plot_point: "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01",
  gradient_two_points: "SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01",
  midpoint: "SPI.MIDDLE.GEO.COORD.MIDPOINT.01",
  interpret_mx_c: "SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01",
  equation_from_graph: "SPI.MIDDLE.GEO.COORD.EQUATION_FROM_GRAPH.01",
  equation_from_two_points: "SPI.MIDDLE.GEO.COORD.EQUATION_FROM_2PTS.01",
};

/** generatorId -> (task -> objectiveId) join table. */
const OBJECTIVE_BY_TASK_BY_GENERATOR: Record<string, Record<string, string>> = {
  "gen.sequences.arithmetic": ARITHMETIC_BY_TASK,
  "gen.sequences.geometric": GEOMETRIC_BY_TASK,
  "gen.algebra.linear-equations": LINEAR_BY_TASK,
  "gen.geometry.angles-figures": ANGLES_BY_TASK,
  "gen.geometry.coordinate-lines": COORDINATE_BY_TASK,
  "gen.stats.data-handling": STAT_BY_TASK,
  "gen.measurement.mensuration": MENS_BY_TASK,
  "gen.geometry.transformations": TRANS_BY_TASK,
  "gen.proportion.ratio": RATIO_BY_TASK,
};

/** A generator task whose mapped objective is missing or retired (a parity failure). */
export interface OrphanedTask {
  generatorId: string;
  task: string;
  objectiveId: string;
}

/** The coverage report (§8.4 / §10.8). */
export interface CoverageReport {
  objectiveTotal: number;
  /** G2_approved — objective is reached by an approved generator task. */
  coveredApproved: string[];
  /** G1_pendingOnly — reached only by a pending-review generator. */
  coveredPending: string[];
  /** G0_noGenerator — objective EXISTS but no generator task maps to it. */
  definedUncovered: string[];
  /** referenced (as prereq) but no record, in the committed baseline (non-blocking). */
  knownBaselineReferencedUndefined: string[];
  /** referenced but no record and NOT baseline (a §7 blocking error). */
  newReferencedUndefined: string[];
  /** a generator task whose mapped objective is missing/retired (must never occur for approved). */
  orphanedTasks: OrphanedTask[];
  /** generatorId -> objectiveIds assessed. */
  byGenerator: Record<string, string[]>;
  /** count summary keyed by tier. */
  byGeneratorTier: { G2_approved: number; G1_pendingOnly: number; G0_noGenerator: number };
}

/** Resolve the task -> objectiveId map for a generator (empty if unknown). */
function mapFor(generatorId: string): Record<string, string> {
  return OBJECTIVE_BY_TASK_BY_GENERATOR[generatorId] ?? {};
}

/**
 * Build the coverage report by joining the SDK generator fleet to the objective
 * registry. `generators` defaults to the live SDK GENERATORS; `knownBaseline` to the
 * committed on-disk set.
 */
export function buildCoverageReport(
  registry: ObjectiveRegistry,
  generators: GeneratorModule[] = GENERATORS,
  knownBaseline: Set<string> = loadKnownBaseline(),
): CoverageReport {
  const objectives: ObjectiveRecord[] = registry.all();

  // Highest tier seen per objective: approved beats pending; an objective starts at "none".
  const tier = new Map<string, "approved" | "pending">();
  const byGenerator: Record<string, string[]> = {};
  const orphanedTasks: OrphanedTask[] = [];
  const referencedUndefinedByGenerator = new Set<string>();

  for (const gen of generators) {
    const status = approvalStatusOf(gen);
    if (status === "rejected") continue;
    const taskMap = mapFor(gen.id);
    const covered: string[] = [];
    for (const t of gen.tasks) {
      const oid = taskMap[t.value];
      if (oid === undefined) continue; // task with no objective mapping (none today)
      const target = registry.byId(oid);
      if (target === undefined || target.reviewStatus === "retired") {
        orphanedTasks.push({ generatorId: gen.id, task: t.value, objectiveId: oid });
        referencedUndefinedByGenerator.add(oid);
        continue;
      }
      covered.push(oid);
      const eff = status === "approved" ? "approved" : "pending";
      const prev = tier.get(oid);
      if (eff === "approved" || prev === undefined) tier.set(oid, eff);
    }
    byGenerator[gen.id] = [...new Set(covered)];
  }

  const coveredApproved: string[] = [];
  const coveredPending: string[] = [];
  const definedUncovered: string[] = [];
  for (const o of objectives) {
    const t = tier.get(o.objectiveId);
    if (t === "approved") coveredApproved.push(o.objectiveId);
    else if (t === "pending") coveredPending.push(o.objectiveId);
    else definedUncovered.push(o.objectiveId);
  }

  // Referenced-undefined (as prerequisites) classified against the baseline.
  const knownBaselineReferencedUndefined = new Set<string>();
  const newReferencedUndefined = new Set<string>();
  for (const o of objectives) {
    for (const p of o.prerequisites ?? []) {
      if (registry.has(p)) continue;
      if (knownBaseline.has(p)) knownBaselineReferencedUndefined.add(p);
      else newReferencedUndefined.add(p);
    }
  }

  return {
    objectiveTotal: objectives.length,
    coveredApproved: coveredApproved.sort(),
    coveredPending: coveredPending.sort(),
    definedUncovered: definedUncovered.sort(),
    knownBaselineReferencedUndefined: [...knownBaselineReferencedUndefined].sort(),
    newReferencedUndefined: [...newReferencedUndefined].sort(),
    orphanedTasks,
    byGenerator,
    byGeneratorTier: {
      G2_approved: coveredApproved.length,
      G1_pendingOnly: coveredPending.length,
      G0_noGenerator: definedUncovered.length,
    },
  };
}

/** The full set of generator->task->objective mappings (read-only export for tests). */
export { OBJECTIVE_BY_TASK_BY_GENERATOR };
