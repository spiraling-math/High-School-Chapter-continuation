/**
 * Geometry (angles) misconception registry (production TypeScript).
 *
 * Byte-for-byte mirror of oracle/spi_oracle/geometry_misconceptions.py. Every rule
 * is computed ONLY from the displayed givens, returns its wrong value or null, and
 * carries a placeholder-free student feedback string. `observableError` is serialized
 * as the distractor rationale, so it MUST match the oracle exactly.
 */

export interface GeoCtx { givens: number[]; apex?: number; theta?: number }

export interface GeoMisconception {
  wrong: (g: GeoCtx) => number | null;
  title: string;
  observableError: string;
  feedback: string;
  expression: string;
}

const sum = (g: GeoCtx): number => g.givens.reduce((a, b) => a + b, 0);

export const MISCONCEPTIONS: Record<string, GeoMisconception> = {
  "MISC.GEOM.LINE.USES_360": {
    wrong: (g) => 360 - sum(g),
    title: "Uses 360 on a straight line",
    observableError: "Subtracted from 360 instead of 180.",
    feedback: "Angles on a straight line sum to 180 degrees, not 360. Subtract the given angles from 180.",
    expression: "360 - sum(givens)",
  },
  "MISC.GEOM.LINE.RETURNS_SUM_GIVENS": {
    wrong: (g) => sum(g),
    title: "Returns the sum of the givens",
    observableError: "Gave the sum of the given angles.",
    feedback: "You added the given angles. Subtract their total from 180 to find the unknown.",
    expression: "sum(givens)",
  },
  "MISC.GEOM.LINE.FORGOT_ONE_GIVEN": {
    wrong: (g) => (g.givens.length >= 2 ? 180 - (sum(g) - g.givens[g.givens.length - 1]!) : null),
    title: "Forgot one given angle",
    observableError: "Left out one of the given angles.",
    feedback: "Include every given angle. Subtract the total of all of them from 180.",
    expression: "180 - sum(all but one given)",
  },
  "MISC.GEOM.TRI.USES_360": {
    wrong: (g) => 360 - sum(g),
    title: "Uses 360 for a triangle",
    observableError: "Used a 360-degree sum for a triangle.",
    feedback: "The interior angles of a triangle sum to 180 degrees, not 360.",
    expression: "360 - A - B",
  },
  "MISC.GEOM.TRI.RETURNS_SUM_GIVENS": {
    wrong: (g) => sum(g),
    title: "Returns the sum of the givens",
    observableError: "Gave the sum of the two known angles.",
    feedback: "You added the two known angles. Subtract their total from 180.",
    expression: "A + B",
  },
  "MISC.GEOM.TRI.SUBTRACTS_ONLY_ONE_GIVEN": {
    wrong: (g) => 180 - g.givens[0]!,
    title: "Subtracts only one given",
    observableError: "Subtracted only one known angle from 180.",
    feedback: "Subtract both known angles from 180, not just one.",
    expression: "180 - A",
  },
  "MISC.GEOM.ISO.FORGOT_TO_HALVE": {
    wrong: (g) => 180 - g.apex!,
    title: "Forgot to halve",
    observableError: "Did not halve after subtracting the apex.",
    feedback: "After subtracting the apex from 180, share the result equally between the two base angles (divide by 2).",
    expression: "180 - apex",
  },
  "MISC.GEOM.ISO.HALVES_180_ONLY": {
    wrong: (g) => (90 - g.apex! > 0 ? 90 - g.apex! : null),
    title: "Halved 180 instead of (180 - apex)",
    observableError: "Used 90 - apex instead of (180 - apex) divided by 2.",
    feedback: "Subtract the apex from 180 first, then divide by 2.",
    expression: "90 - apex",
  },
  "MISC.GEOM.ISO.APEX_EQUALS_BASE": {
    wrong: (g) => g.apex!,
    title: "Base equals apex",
    observableError: "Took the base angle to equal the apex.",
    feedback: "The base angles are not equal to the apex; use base = (180 - apex) divided by 2.",
    expression: "apex",
  },
  "MISC.GEOM.POINT.USES_180": {
    wrong: (g) => (180 - sum(g) > 0 ? 180 - sum(g) : null),
    title: "Uses 180 around a point",
    observableError: "Used a 180-degree sum instead of 360.",
    feedback: "Angles around a point sum to 360 degrees, not 180.",
    expression: "180 - sum(givens)",
  },
  "MISC.GEOM.POINT.RETURNS_SUM_GIVENS": {
    wrong: (g) => sum(g),
    title: "Returns the sum of the givens",
    observableError: "Gave the sum of the given angles.",
    feedback: "You added the given angles. Subtract their total from 360.",
    expression: "sum(givens)",
  },
  "MISC.GEOM.POINT.FORGOT_ONE_GIVEN": {
    wrong: (g) => (g.givens.length >= 2 ? 360 - (sum(g) - g.givens[g.givens.length - 1]!) : null),
    title: "Forgot one given angle",
    observableError: "Left out one of the given angles.",
    feedback: "Include every given angle; subtract their total from 360.",
    expression: "360 - sum(all but one given)",
  },
  "MISC.GEOM.VO.USES_SUPPLEMENTARY": {
    wrong: (g) => 180 - g.theta!,
    title: "Uses the supplementary angle",
    observableError: "Used the supplementary angle (180 - given) instead of the equal vertically opposite angle.",
    feedback: "Vertically opposite angles are equal, so the answer equals the given angle (do not use 180 minus the angle).",
    expression: "180 - theta",
  },
};

const ELIGIBILITY: Record<string, string[]> = {
  straight_line_missing_angle: ["MISC.GEOM.LINE.USES_360", "MISC.GEOM.LINE.RETURNS_SUM_GIVENS", "MISC.GEOM.LINE.FORGOT_ONE_GIVEN"],
  triangle_missing_angle: ["MISC.GEOM.TRI.USES_360", "MISC.GEOM.TRI.RETURNS_SUM_GIVENS", "MISC.GEOM.TRI.SUBTRACTS_ONLY_ONE_GIVEN"],
  isosceles_base_angle: ["MISC.GEOM.ISO.FORGOT_TO_HALVE", "MISC.GEOM.ISO.HALVES_180_ONLY", "MISC.GEOM.ISO.APEX_EQUALS_BASE"],
  vertically_opposite_angle: [],
  angles_at_point_missing: ["MISC.GEOM.POINT.USES_180", "MISC.GEOM.POINT.RETURNS_SUM_GIVENS", "MISC.GEOM.POINT.FORGOT_ONE_GIVEN"],
};

export function rulesFor(task: string): string[] {
  return ELIGIBILITY[task] ? [...ELIGIBILITY[task]!] : [];
}
