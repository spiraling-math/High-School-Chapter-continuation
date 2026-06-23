/**
 * Coordinate-geometry misconception registry (TypeScript mirror).
 *
 * Byte-for-byte behavioural mirror of oracle/spi_oracle/coordinate_misconceptions.py.
 * Each misconception is one conceptual error with a TASK-SPECIFIC value adapter; a
 * semantic id may be reused across tasks when the underlying error is the same (owner
 * decision H). Adapters take a task context of exact `Rational` values and return the
 * wrong value in the task's natural shape, or `null` when the misconception does not
 * apply. `observableError` (distractor rationale) and `feedback` use only legitimate
 * domain vocabulary — gradient, intercept, x, y, m, c — never internal placeholders.
 */

import { Rational } from "../../core/exact-math/rational.ts";

export type Ctx = Record<string, Rational>;
export type AdapterValue = Rational | [Rational, Rational] | null;
// The context is dynamically keyed per task; each adapter reads the keys its task provides.
// Typed as a concrete record so reads are not flagged by noUncheckedIndexedAccess.
export type CtxFields = { x: Rational; y: Rational; x1: Rational; y1: Rational; x2: Rational; y2: Rational; m: Rational; c: Rational; mx: Rational; my: Rational };
export type Adapter = (c: CtxFields) => AdapterValue;

export interface Misconception {
  title: string;
  observableError: string;
  feedback: string;
  adapt: Record<string, Adapter>;
}

const ZERO = new Rational(0, 1);
const TWO = new Rational(2, 1);

export const MISCONCEPTIONS: Record<string, Misconception> = {
  "MISC.COORD.AXIS_SWAP": {
    title: "Swaps the coordinate order",
    observableError: "Wrote the coordinates in the wrong order (y before x).",
    feedback: "Write the x-coordinate first, then the y-coordinate: (x, y).",
    adapt: {
      read_point: (c) => [c.y, c.x],
      midpoint: (c) => [c.my, c.mx],
    },
  },
  "MISC.COORD.COORD_SIGN_FLIP": {
    title: "Sign error on a coordinate",
    observableError: "Reversed the sign of a coordinate.",
    feedback: "Check the sign of each coordinate against its axis direction; left and down are negative.",
    adapt: {},
  },
  "MISC.COORD.POINT_REFLECT_X": {
    title: "Reflects across the x-axis",
    observableError: "Read the y-coordinate with the wrong sign (reflected across the x-axis).",
    feedback: "Read the y-coordinate by its height above or below the x-axis; below the axis is negative.",
    adapt: { read_point: (c) => [c.x, c.y.neg()] },
  },
  "MISC.COORD.POINT_REFLECT_Y": {
    title: "Reflects across the y-axis",
    observableError: "Read the x-coordinate with the wrong sign (reflected across the y-axis).",
    feedback: "Read the x-coordinate by its distance left or right of the y-axis; left of the axis is negative.",
    adapt: { read_point: (c) => [c.x.neg(), c.y] },
  },
  "MISC.COORD.GRADIENT_INVERTED": {
    title: "Inverts the gradient (run over rise)",
    observableError: "Divided the change in x by the change in y instead of the other way round.",
    feedback: "Gradient is rise over run: divide the change in y by the change in x.",
    adapt: {
      gradient_two_points: (c) => (c.y2.equals(c.y1) ? null : c.x2.sub(c.x1).div(c.y2.sub(c.y1))),
      equation_from_graph: (c) => (c.y2.equals(c.y1) ? null : [c.x2.sub(c.x1).div(c.y2.sub(c.y1)), c.c]),
      equation_from_two_points: (c) => (c.y2.equals(c.y1) ? null : [c.x2.sub(c.x1).div(c.y2.sub(c.y1)), c.c]),
    },
  },
  "MISC.COORD.GRADIENT_SIGN": {
    title: "Sign error in the gradient",
    observableError: "Subtracted the coordinates in inconsistent orders, flipping the sign of the gradient.",
    feedback: "Subtract the x-coordinates and the y-coordinates in the SAME order; keep the signs consistent.",
    adapt: {
      gradient_two_points: (c) => c.m.neg(),
      equation_from_two_points: (c) => [c.m.neg(), c.c],
    },
  },
  "MISC.COORD.GRADIENT_SUM_BOTH": {
    title: "Adds instead of subtracting",
    observableError: "Added the coordinates instead of subtracting them.",
    feedback: "Gradient uses the DIFFERENCES: (y2 - y1) divided by (x2 - x1), not the sums.",
    adapt: {
      gradient_two_points: (c) => (c.x2.add(c.x1).equals(ZERO) ? null : c.y2.add(c.y1).div(c.x2.add(c.x1))),
    },
  },
  "MISC.COORD.MIDPOINT_DIFFERENCE": {
    title: "Uses the difference, not the average",
    observableError: "Halved the difference of the coordinates instead of their average.",
    feedback: "Midpoint averages the coordinates: add them and divide by 2, do not subtract.",
    adapt: { midpoint: (c) => [c.x2.sub(c.x1).div(TWO), c.y2.sub(c.y1).div(TWO)] },
  },
  "MISC.COORD.MIDPOINT_SUM_NO_HALF": {
    title: "Adds without halving",
    observableError: "Added the coordinates but did not divide by 2.",
    feedback: "After adding each pair of coordinates, divide by 2 to find the midpoint.",
    adapt: { midpoint: (c) => [c.x1.add(c.x2), c.y1.add(c.y2)] },
  },
  "MISC.COORD.MC_SWAPPED": {
    title: "Swaps gradient and intercept",
    observableError: "Read the gradient as the intercept and the intercept as the gradient.",
    feedback: "In y = mx + c the gradient m multiplies x; the intercept c is the constant term.",
    adapt: {
      interpret_mx_c: (c) => [c.c, c.m],
      equation_from_graph: (c) => [c.c, c.m],
      equation_from_two_points: (c) => [c.c, c.m],
    },
  },
  "MISC.COORD.INTERCEPT_SIGN": {
    title: "Sign error on the intercept",
    observableError: "Gave the y-intercept with the wrong sign.",
    feedback: "Read the y-intercept where the line crosses the y-axis, keeping its sign (below the origin is negative).",
    adapt: {
      interpret_mx_c: (c) => [c.m, c.c.neg()],
      equation_from_graph: (c) => [c.m, c.c.neg()],
      equation_from_two_points: (c) => [c.m, c.c.neg()],
    },
  },
  "MISC.COORD.READS_X_INTERCEPT": {
    title: "Reads the x-intercept as c",
    observableError: "Used the x-intercept instead of the y-intercept.",
    feedback: "The y-intercept c is where the line meets the y-axis (x = 0), not where it meets the x-axis.",
    adapt: {
      interpret_mx_c: (c) => (c.m.equals(ZERO) ? null : [c.m, c.c.neg().div(c.m)]),
      equation_from_graph: (c) => (c.m.equals(ZERO) ? null : [c.m, c.c.neg().div(c.m)]),
    },
  },
};

const ELIGIBILITY: Record<string, string[]> = {
  read_point: ["MISC.COORD.AXIS_SWAP", "MISC.COORD.POINT_REFLECT_X", "MISC.COORD.POINT_REFLECT_Y"],
  plot_point: [],
  gradient_two_points: ["MISC.COORD.GRADIENT_INVERTED", "MISC.COORD.GRADIENT_SIGN", "MISC.COORD.GRADIENT_SUM_BOTH"],
  midpoint: ["MISC.COORD.MIDPOINT_DIFFERENCE", "MISC.COORD.MIDPOINT_SUM_NO_HALF", "MISC.COORD.AXIS_SWAP"],
  interpret_mx_c: ["MISC.COORD.MC_SWAPPED", "MISC.COORD.INTERCEPT_SIGN", "MISC.COORD.READS_X_INTERCEPT"],
  equation_from_graph: ["MISC.COORD.GRADIENT_INVERTED", "MISC.COORD.INTERCEPT_SIGN", "MISC.COORD.READS_X_INTERCEPT"],
  equation_from_two_points: ["MISC.COORD.GRADIENT_INVERTED", "MISC.COORD.GRADIENT_SIGN", "MISC.COORD.INTERCEPT_SIGN"],
};

export function rulesFor(task: string): string[] {
  return [...(ELIGIBILITY[task] ?? [])];
}

export function adapterFor(mid: string, task: string): Adapter | undefined {
  return MISCONCEPTIONS[mid]?.adapt[task];
}
