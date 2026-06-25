/**
 * Single source of truth for the gen.measurement.mensuration task -> objective mapping
 * (owner decision A). Every specification section, objective record, descriptor, validator,
 * fixture, review-pack record, and registry entry MUST use exactly these eight IDs and the
 * eight canonical task names — no alternative spellings. The Python oracle mirrors this map
 * verbatim (oracle/spi_oracle/mensuration.py: OBJECTIVE_BY_TASK) and a parity test asserts the
 * two agree and that all eight IDs exist in curriculum/objectives/SPI.MIDDLE.MEAS.json.
 *
 * Domain segment is MEAS (NOT MENS); the misconception prefix is MISC.MENS.* (owner A).
 * All eight tasks are FREE-RESPONSE ONLY in v1.0.0 (owner C); the dimensional-quantity answer
 * checker is the architecture-proving purpose, so the number and the unit are both genuinely
 * checked. An explicit multiple-choice request must raise an unsupported-interaction error.
 */

export const MENSURATION_TASKS = [
  "perimeter_rectangle",
  "perimeter_composite",
  "area_rectangle",
  "area_triangle",
  "area_composite",
  "missing_length_perimeter",
  "missing_dimension_area",
  "missing_triangle_base_height",
] as const;

export type MensurationTask = (typeof MENSURATION_TASKS)[number];

export const OBJECTIVE_BY_TASK: Record<MensurationTask, string> = {
  perimeter_rectangle: "SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01",
  perimeter_composite: "SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01",
  area_rectangle: "SPI.MIDDLE.MEAS.AREA.RECTANGLE.01",
  area_triangle: "SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01",
  area_composite: "SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01",
  missing_length_perimeter: "SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01",
  missing_dimension_area: "SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01",
  missing_triangle_base_height: "SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01",
};

/** The eight approved objective IDs, in task order. */
export const MENS_OBJECTIVE_IDS: string[] = MENSURATION_TASKS.map((t) => OBJECTIVE_BY_TASK[t]);

/**
 * v1.0.0 interaction policy (owner C): every task is free-response only. The generator must
 * reject an explicit multiple-choice request with an unsupported-interaction error rather than
 * silently substituting free response.
 */
export const SUPPORTED_INTERACTIONS: readonly string[] = ["free-response"] as const;

/**
 * Hidden-dimension (inverse) tasks render a NOT-TO-SCALE student diagram so the answer cannot be
 * recovered by measuring the SVG (owner G). Direct-calculation tasks may render to-scale.
 */
export const HIDDEN_DIMENSION_TASKS: MensurationTask[] = [
  "missing_length_perimeter",
  "missing_dimension_area",
  "missing_triangle_base_height",
];

/** Tasks whose answer may be an exact rational (others are integer-only) — owner F. */
export const RATIONAL_ANSWER_TASKS: MensurationTask[] = [
  "area_triangle",
  "missing_triangle_base_height",
];
