/**
 * Canonical registry of the approved sequence generators as GeneratorModules.
 *
 * The single source of truth for "which generators exist", used by the Studio,
 * exporters, and the stability harness. Adding a family is one entry here. The
 * underlying generate/validate/serialize functions are the approved, immutable
 * implementations — this registry only adapts them to the GeneratorModule shape
 * (output-neutral).
 */

import type { GeneratorModule, StudioMode } from "./generator-module.ts";
import { approvalStatusOf } from "./generator-module.ts";
import * as arithmetic from "../../domains/sequences/arithmetic.ts";
import { validate as arithmeticValidate } from "../../domains/sequences/validate.ts";
import * as geometric from "../../domains/sequences/geometric.ts";
import * as linear from "../../domains/algebra/linear-equations.ts";
import * as geometryAngles from "../../domains/geometry/angles.ts";
import * as coordinateLines from "../../domains/geometry/coordinate-lines.ts";
import * as dataHandling from "../../domains/statistics/data-handling.ts";
import * as mensuration from "../../domains/measurement/mensuration.ts";
import * as transformations from "../../domains/geometry/transformations.ts";
import * as ratio from "../../domains/proportion/ratio.ts";

export const GENERATORS: GeneratorModule[] = [
  {
    id: arithmetic.GENERATOR_ID,
    version: arithmetic.GENERATOR_VERSION,
    label: "Arithmetic sequences",
    tasks: [
      { value: "nth_term", label: "nth term", mc: true },
      { value: "sum_n", label: "Sum of first n terms", mc: true },
      { value: "find_d", label: "Find common difference", mc: false },
      { value: "find_n_for_value", label: "Find term index", mc: false },
    ],
    generate: (s, c) => arithmetic.generate(s, c as arithmetic.Config),
    validate: arithmeticValidate,
    serialize: arithmetic.serialize,
  },
  {
    id: geometric.GENERATOR_ID,
    version: geometric.GENERATOR_VERSION,
    label: "Geometric sequences",
    tasks: [
      { value: "nth_term", label: "nth term", mc: true },
      { value: "sum_n", label: "Sum of first n terms", mc: true },
      { value: "find_r", label: "Find common ratio", mc: false },
      { value: "find_n_for_value", label: "Find term index", mc: false },
      { value: "sum_infinite", label: "Sum to infinity", mc: false },
    ],
    generate: (s, c) => geometric.generate(s, c as geometric.Config),
    validate: geometric.validate,
    serialize: geometric.serialize,
  },
  {
    id: linear.GENERATOR_ID,
    version: linear.GENERATOR_VERSION,
    label: "Linear equations (one variable)",
    tasks: [
      { value: "one_step_add", label: "One-step (+/−)", mc: true },
      { value: "one_step_mul", label: "One-step (×)", mc: true },
      { value: "two_step", label: "Two-step (ax+b=c)", mc: true },
      { value: "both_sides", label: "Variables on both sides", mc: true },
      { value: "brackets", label: "One set of brackets", mc: true },
    ],
    generate: (s, c) => linear.generate(s, c as linear.Config),
    validate: linear.validate,
    serialize: linear.serialize,
  },
  {
    id: geometryAngles.GENERATOR_ID,
    version: geometryAngles.GENERATOR_VERSION,
    label: "Geometry — angles (SVG)",
    // Curriculum-approved at v1.2.3 (DECISION_LOG.md #40, 2026-06-23). Selectable in normal
    // Studio use and included in production exports/samples. v1.2.0/1.2.1/1.2.2 are preserved
    // in history (unapproved) and are not registered/selectable. Newly generated items still
    // begin at machine-validated; approval does not auto-approve future items.
    approvalStatus: "approved",
    tasks: [
      { value: "straight_line_missing_angle", label: "Angles on a straight line", mc: true },
      { value: "triangle_missing_angle", label: "Triangle angle sum", mc: true },
      { value: "isosceles_base_angle", label: "Isosceles base angle", mc: true },
      { value: "vertically_opposite_angle", label: "Vertically opposite", mc: false },
      { value: "angles_at_point_missing", label: "Angles around a point", mc: true },
    ],
    generate: (s, c) => geometryAngles.generate(s, c as geometryAngles.Config),
    validate: geometryAngles.validate,
    serialize: geometryAngles.serialize,
  },
  {
    id: coordinateLines.GENERATOR_ID,
    version: coordinateLines.GENERATOR_VERSION,
    label: "Coordinate geometry & straight-line graphs (SVG)",
    // Curriculum-APPROVED at v1.0.2 (DECISION_LOG.md #44, 2026-06-24): selectable in normal
    // Studio use and included in production exports/samples. History: implemented #41,
    // curriculum REVISE #42 -> v1.0.1, visual/export REJECT #43 -> v1.0.2 (per-root CSS-var
    // render-mode isolation + materialized export via core/visual-style/cartesian-theme).
    // Only v1.0.2 is registered; v1.0.0/v1.0.1 preserved (tags), unapproved, not selectable.
    // Newly generated items begin at machine-validated; approval does not auto-approve future items.
    approvalStatus: "approved",
    tasks: [
      { value: "read_point", label: "Read a point", mc: true },
      { value: "plot_point", label: "Plot a point", mc: false },
      { value: "gradient_two_points", label: "Gradient between two points", mc: true },
      { value: "midpoint", label: "Midpoint", mc: true },
      { value: "interpret_mx_c", label: "Read m and c from y = mx + c", mc: true },
      { value: "equation_from_graph", label: "Equation from a graph", mc: true },
      { value: "equation_from_two_points", label: "Equation through two points", mc: true },
    ],
    generate: (s, c) => coordinateLines.generate(s, c as coordinateLines.Config),
    validate: coordinateLines.validate,
    serialize: coordinateLines.serialize,
  },
  {
    id: dataHandling.GENERATOR_ID,
    version: dataHandling.GENERATOR_VERSION,
    label: "Statistics & data handling (charts + tables)",
    // Curriculum-APPROVED at v1.0.2 (DECISION_LOG.md #49). The TS mirror is byte-parity with the
    // Python oracle (gated by oracle/golden/data_handling.*). Selectable in normal Studio use and
    // included in production exports/samples; only v1.0.2 registered (v1.0.0/v1.0.1 preserved as
    // historical, unapproved). Newly generated items begin at machine-validated.
    approvalStatus: "approved",
    tasks: [
      { value: "read_bar_chart", label: "Read a bar chart", mc: true },
      { value: "read_pictogram", label: "Read a pictogram", mc: true },
      { value: "read_table_value", label: "Read a table value", mc: true },
      { value: "read_line_graph", label: "Read a line graph", mc: true },
      { value: "complete_frequency_table", label: "Complete a frequency table", mc: false },
      { value: "mean_from_list", label: "Mean of a list", mc: true },
      { value: "median_from_list", label: "Median of a list", mc: true },
      { value: "mode_from_list", label: "Mode of a list", mc: true },
      { value: "range_from_list", label: "Range of a list", mc: true },
      { value: "mean_from_freq_table", label: "Mean from a frequency table", mc: true },
      { value: "single_event_probability", label: "Single-event probability", mc: true },
    ],
    generate: (s, c) => dataHandling.generate(s, c as dataHandling.Config),
    validate: dataHandling.validate,
    serialize: dataHandling.serialize,
  },
  {
    id: mensuration.GENERATOR_ID,
    version: mensuration.GENERATOR_VERSION,
    label: "Mensuration — perimeter, area & composite shapes",
    // Curriculum-APPROVED at v1.0.1 (DECISION_LOG.md #53; tag approved-mensuration-v1.0.1). The TS
    // mirror is byte-parity with the Python oracle (gated by oracle/golden/mensuration.*). Selectable
    // in normal Studio use and included in production exports/samples; only v1.0.1 registered
    // (v1.0.0 preserved as historical, unapproved). The eight SPI.MIDDLE.MEAS.* objectives are
    // curriculum-approved; the dimensional-quantity answer.type "quantity" + answer.measure contract
    // is approved (length/area, mm/cm/m; NO cross-unit conversion). All eight tasks are FREE-RESPONSE
    // only. Newly generated items begin at machine-validated.
    approvalStatus: "approved",
    tasks: [
      { value: "perimeter_rectangle", label: "Perimeter of a rectangle", mc: false },
      { value: "perimeter_composite", label: "Perimeter of a composite (L-shape)", mc: false },
      { value: "area_rectangle", label: "Area of a rectangle", mc: false },
      { value: "area_triangle", label: "Area of a triangle (base × height)", mc: false },
      { value: "area_composite", label: "Area of a composite by decomposition", mc: false },
      { value: "missing_length_perimeter", label: "Missing length from a perimeter", mc: false },
      { value: "missing_dimension_area", label: "Missing dimension from an area", mc: false },
      { value: "missing_triangle_base_height", label: "Missing triangle base/height from an area", mc: false },
    ],
    generate: (s, c) => mensuration.generate(s, c as Parameters<typeof mensuration.generate>[1]),
    validate: mensuration.validate,
    serialize: mensuration.serialize,
  },
  {
    id: transformations.GENERATOR_ID,
    version: transformations.GENERATOR_VERSION,
    label: "Coordinate transformations — translate, reflect & rotate",
    // Curriculum-APPROVED at v1.0.2 (DECISION_LOG.md #57; tag approved-transformations-v1.0.2). The TS
    // mirror is byte-parity with the Python oracle (gated by oracle/golden/transformations.*). Selectable
    // in normal Studio use and included in production exports/samples; only v1.0.2 registered (v1.0.0/
    // v1.0.1 preserved as historical, unapproved). The nine SPI.MIDDLE.GEO.TRANS.* objectives are
    // curriculum-approved; the shared transformation-descriptor contract (answer.type "transformation"
    // canonical-first + the translation/reflection/rotation descriptor union + parser/canonicalizer/
    // formatter/equivalence checker + the 14 result codes) is approved — this does NOT authorize
    // enlargements, compositions, arbitrary-angle rotations, arbitrary reflection lines, fractional
    // vectors/centres, matrices, transformations of functions, tessellations, or 3D. All nine tasks are
    // FREE-RESPONSE only; an explicit MC request is rejected with interaction-not-supported. Newly
    // generated items begin at machine-validated.
    approvalStatus: "approved",
    tasks: [
      { value: "translate_point", label: "Translate a point", mc: false },
      { value: "translate_shape", label: "Translate a shape", mc: false },
      { value: "reflect_point", label: "Reflect a point", mc: false },
      { value: "reflect_shape", label: "Reflect a shape", mc: false },
      { value: "rotate_point", label: "Rotate a point", mc: false },
      { value: "rotate_shape", label: "Rotate a shape", mc: false },
      { value: "describe_translation", label: "Describe a translation", mc: false },
      { value: "describe_reflection", label: "Describe a reflection", mc: false },
      { value: "describe_rotation", label: "Describe a rotation", mc: false },
    ],
    generate: (s, c) => transformations.generate(s, c as Parameters<typeof transformations.generate>[1]),
    validate: transformations.validate,
    serialize: transformations.serialize,
  },
  {
    id: ratio.GENERATOR_ID,
    version: ratio.GENERATOR_VERSION,
    label: "Ratio & proportion — simplify, share, direct/inverse, best buy",
    // Curriculum-APPROVED at v1.0.2 (DECISION_LOG.md #61, 2026-06-26); selectable in normal Studio +
    // production; only v1.0.2 registered (v1.0.0/v1.0.1 preserved historical/unapproved). The TS mirror is
    // byte-parity with the Python oracle (gated by oracle/golden/ratio.*). The twelve SPI.MIDDLE.RATIO.*
    // objectives are curriculum-approved; the canonical-first answer.type "ratio" schema extension is
    // approved. Per the owner interaction matrix: best_buy is MULTIPLE-CHOICE only; simplify /
    // ratio_to_fraction / fraction_to_ratio / direct_proportion / inverse_proportion support both FR and MC;
    // the remaining six tasks are FREE-RESPONSE only (an explicit MC request is rejected with
    // interaction-not-supported). Scope excludes percentages, currency, geometric similarity,
    // gradient-as-ratio, probability/odds, and any irrational/decimal ratio. Newly generated items begin at
    // machine-validated; approval does not auto-approve future items.
    approvalStatus: "approved",
    tasks: [
      { value: "simplify", label: "Simplify a ratio", mc: true },
      { value: "write_from_quantities", label: "Write a ratio from quantities", mc: false },
      { value: "ratio_to_fraction", label: "Ratio to fraction of the whole", mc: true },
      { value: "fraction_to_ratio", label: "Fraction to ratio", mc: true },
      { value: "share_two_part", label: "Share in a two-part ratio", mc: false },
      { value: "share_three_part", label: "Share in a three-part ratio", mc: false },
      { value: "missing_part", label: "Find a missing part", mc: false },
      { value: "direct_proportion", label: "Direct proportion (unitary)", mc: true },
      { value: "inverse_proportion", label: "Inverse proportion", mc: true },
      { value: "unit_rate", label: "Unit rate", mc: false },
      { value: "best_buy", label: "Best buy (multiple choice)", mc: true },
      { value: "simple_scale", label: "Simple scale", mc: false },
    ],
    generate: (s, c) => ratio.generate(s, c as Parameters<typeof ratio.generate>[1]),
    validate: ratio.validate,
    serialize: ratio.serialize,
  },
];

export function getGenerator(id: string): GeneratorModule {
  return GENERATORS.find((g) => g.id === id) ?? GENERATORS[0]!;
}

/** Generators selectable in a given Studio mode. Normal users see only "approved"
 *  generators; review/developer mode additionally sees "pending-review" ones; "rejected"
 *  versions are never returned. */
export function generatorsForMode(mode: StudioMode): GeneratorModule[] {
  return GENERATORS.filter((g) => {
    const s = approvalStatusOf(g);
    if (s === "rejected") return false;
    if (s === "pending-review") return mode === "review";
    return true;
  });
}

/** Curriculum-approved generators only (used by production exports/samples). */
export function approvedGenerators(): GeneratorModule[] {
  return GENERATORS.filter((g) => approvalStatusOf(g) === "approved");
}

export function taskIsMc(gen: GeneratorModule, task: string | undefined): boolean {
  if (!task) return true; // "auto" resolves to an MC-capable task in MC mode
  return gen.tasks.find((t) => t.value === task)?.mc ?? false;
}
