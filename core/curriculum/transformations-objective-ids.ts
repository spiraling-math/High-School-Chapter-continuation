/**
 * Single source of truth for the gen.geometry.transformations task -> objective mapping (owner A).
 * Every specification section, objective record, descriptor, validator, fixture, review-pack record,
 * and registry entry MUST use exactly these nine IDs and the nine canonical task slugs — no alternative
 * spellings. The Python oracle mirrors this map verbatim
 * (oracle/spi_oracle/transformations.py: OBJECTIVE_BY_TASK) and a parity test asserts the two agree and
 * that all nine IDs exist in curriculum/objectives/SPI.MIDDLE.GEO.TRANS.json.
 *
 * Domain segment is GEO.TRANS; the misconception prefix is MISC.TRANS.* (owner A). All nine tasks are
 * FREE-RESPONSE only in v1.0.0 (owner A); an explicit multiple-choice request must raise an
 * interaction-not-supported error (never a silent free-response substitution).
 */

export const TRANSFORMATIONS_TASKS = [
  "translate_point",
  "translate_shape",
  "reflect_point",
  "reflect_shape",
  "rotate_point",
  "rotate_shape",
  "describe_translation",
  "describe_reflection",
  "describe_rotation",
] as const;

export type TransformationTask = (typeof TRANSFORMATIONS_TASKS)[number];

export const OBJECTIVE_BY_TASK: Record<TransformationTask, string> = {
  translate_point: "SPI.MIDDLE.GEO.TRANS.TRANSLATE_POINT.01",
  translate_shape: "SPI.MIDDLE.GEO.TRANS.TRANSLATE_SHAPE.01",
  reflect_point: "SPI.MIDDLE.GEO.TRANS.REFLECT_POINT.01",
  reflect_shape: "SPI.MIDDLE.GEO.TRANS.REFLECT_SHAPE.01",
  rotate_point: "SPI.MIDDLE.GEO.TRANS.ROTATE_POINT.01",
  rotate_shape: "SPI.MIDDLE.GEO.TRANS.ROTATE_SHAPE.01",
  describe_translation: "SPI.MIDDLE.GEO.TRANS.DESCRIBE_TRANSLATION.01",
  describe_reflection: "SPI.MIDDLE.GEO.TRANS.DESCRIBE_REFLECTION.01",
  describe_rotation: "SPI.MIDDLE.GEO.TRANS.DESCRIBE_ROTATION.01",
};

/** The nine approved objective IDs, in task order. */
export const TRANS_OBJECTIVE_IDS: string[] = TRANSFORMATIONS_TASKS.map((t) => OBJECTIVE_BY_TASK[t]);

/** v1.0.0 interaction policy (owner A): every task is free-response only. */
export const SUPPORTED_INTERACTIONS: readonly string[] = ["free-response"] as const;

/** Point-image tasks answer with a single coordinate (owner B). */
export const POINT_TASKS: TransformationTask[] = ["translate_point", "reflect_point", "rotate_point"];
/** Shape-image tasks answer with a table-completion, one cell per labelled image vertex (owner B). */
export const SHAPE_TASKS: TransformationTask[] = ["translate_shape", "reflect_shape", "rotate_shape"];
/** Describe tasks answer with the structured transformation descriptor (owner B/C). */
export const DESCRIBE_TASKS: TransformationTask[] = ["describe_translation", "describe_reflection", "describe_rotation"];

/** The mathematical answer.type per task (owner B). */
export const ANSWER_TYPE_BY_TASK: Record<TransformationTask, "coordinate" | "table-completion" | "transformation"> = {
  translate_point: "coordinate", reflect_point: "coordinate", rotate_point: "coordinate",
  translate_shape: "table-completion", reflect_shape: "table-completion", rotate_shape: "table-completion",
  describe_translation: "transformation", describe_reflection: "transformation", describe_rotation: "transformation",
};
