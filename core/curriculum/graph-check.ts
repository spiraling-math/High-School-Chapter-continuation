/**
 * Curriculum-graph integrity check.
 *
 * Validates the objective graph as the curriculum scales: no duplicate IDs, no
 * prerequisite cycles, and prerequisites resolve (unresolved ones are warnings,
 * since a prerequisite may legitimately be defined in another stage not yet
 * loaded). DOM-free; usable in tests and tooling.
 */

export interface ObjectiveLike {
  objectiveId: string;
  prerequisites?: string[];
}

export interface GraphReport {
  ok: boolean;
  objectiveCount: number;
  errors: string[];
  warnings: string[];
}

export function checkCurriculumGraph(objectives: ObjectiveLike[]): GraphReport {
  const errors: string[] = [];
  const warnings: string[] = [];
  const ids = objectives.map((o) => o.objectiveId);
  const idSet = new Set(ids);

  const seen = new Set<string>();
  for (const id of ids) {
    if (seen.has(id)) errors.push(`duplicate objective id: ${id}`);
    seen.add(id);
  }

  const adj = new Map<string, string[]>();
  for (const o of objectives) {
    const internal: string[] = [];
    for (const p of o.prerequisites ?? []) {
      if (idSet.has(p)) internal.push(p);
      else warnings.push(`unresolved prerequisite '${p}' for ${o.objectiveId} (may be defined in another stage)`);
    }
    adj.set(o.objectiveId, internal);
  }

  // Cycle detection over resolved prerequisite edges (DFS with colours).
  const WHITE = 0, GRAY = 1, BLACK = 2;
  const colour = new Map<string, number>(ids.map((i) => [i, WHITE]));
  const stack: string[] = [];
  const visit = (u: string): void => {
    colour.set(u, GRAY);
    stack.push(u);
    for (const v of adj.get(u) ?? []) {
      if (colour.get(v) === GRAY) errors.push(`prerequisite cycle: ${[...stack, v].join(" -> ")}`);
      else if (colour.get(v) === WHITE) visit(v);
    }
    stack.pop();
    colour.set(u, BLACK);
  };
  for (const id of ids) if (colour.get(id) === WHITE) visit(id);

  return { ok: errors.length === 0, objectiveCount: objectives.length, errors, warnings };
}

/** Confirm a set of expected objective IDs are all present in the graph. */
export function requireObjectives(objectives: ObjectiveLike[], expected: string[]): string[] {
  const present = new Set(objectives.map((o) => o.objectiveId));
  return expected.filter((id) => !present.has(id));
}
