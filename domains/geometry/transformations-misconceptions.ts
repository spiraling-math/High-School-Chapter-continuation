/**
 * gen.geometry.transformations — MISC.TRANS.* registry and per-item diagnostics (owner K).
 *
 * Byte-for-byte TypeScript mirror of oracle/spi_oracle/transformations_misconceptions.py.
 */

import {
  type Point,
  QUARTER_DEGREES,
  applyTransform,
  formatDisplay,
  reflectionVertical,
  reflectionHorizontal,
  rotationDesc,
  translationDesc,
  rotateQuarter,
  reflectXEqA,
  reflectYEqB,
  reflectYEqX,
  reflectYEqNegX,
  deepEqual,
} from "./transformations-core.ts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = any;

export const DOMAIN = "geometry";

function m(mid: string, title: string, obs: string, feedback: string, hint: string, objs: string[]): Json {
  return {
    misconceptionId: mid,
    domain: DOMAIN,
    title,
    description: obs,
    observableError: obs,
    feedback,
    remediationHint: hint,
    objectiveRelationships: [...objs],
    reviewStatus: "proposed",
    version: "1.0.0",
  };
}

const _TR = ["SPI.MIDDLE.GEO.TRANS.TRANSLATE_POINT.01", "SPI.MIDDLE.GEO.TRANS.TRANSLATE_SHAPE.01"];
const _RF = ["SPI.MIDDLE.GEO.TRANS.REFLECT_POINT.01", "SPI.MIDDLE.GEO.TRANS.REFLECT_SHAPE.01"];
const _RO = ["SPI.MIDDLE.GEO.TRANS.ROTATE_POINT.01", "SPI.MIDDLE.GEO.TRANS.ROTATE_SHAPE.01"];
const _DT = ["SPI.MIDDLE.GEO.TRANS.DESCRIBE_TRANSLATION.01"];
const _DR = ["SPI.MIDDLE.GEO.TRANS.DESCRIBE_REFLECTION.01"];
const _DO = ["SPI.MIDDLE.GEO.TRANS.DESCRIBE_ROTATION.01"];

export const MISCONCEPTIONS: Json[] = [
  // --- translation (6) ---
  m("MISC.TRANS.REVERSES_VECTOR", "Subtracts the translation vector",
    "Subtracts the vector instead of adding it (moves the opposite way).",
    "A translation by (dx, dy) adds dx to x and dy to y. Move with the vector, not against it.",
    "Add each component of the vector to the matching coordinate.", _TR),
  m("MISC.TRANS.SWAPS_DX_DY", "Swaps the vector components",
    "Adds dy to x and dx to y, swapping the two components.",
    "The first component changes x; the second changes y. Keep them in order.",
    "Match dx to x and dy to y.", _TR),
  m("MISC.TRANS.CHANGES_ONLY_X", "Translates horizontally only",
    "Applies the x-component but leaves y unchanged.",
    "A translation moves the point in both directions at once.",
    "Add dy to y as well as dx to x.", _TR),
  m("MISC.TRANS.CHANGES_ONLY_Y", "Translates vertically only",
    "Applies the y-component but leaves x unchanged.",
    "A translation moves the point in both directions at once.",
    "Add dx to x as well as dy to y.", _TR),
  m("MISC.TRANS.WRONG_SIGN_ONE_COMPONENT", "Wrong sign on one component",
    "Negates one component of the vector (e.g. moves left instead of right).",
    "Check the sign of each component of the vector before adding.",
    "Keep the signs exactly as the column vector shows.", _TR),
  m("MISC.TRANS.TRANSLATES_FROM_ORIGIN", "Reads the vector as the image point",
    "Writes the vector itself as the image, ignoring the start point.",
    "Add the vector to the point's coordinates; the vector is not the answer on its own.",
    "Image = start point + vector.", _TR),
  // --- reflection (7) ---
  m("MISC.TRANS.REFLECTS_X_FOR_Y_AXIS", "Reflects in the wrong orthogonal line",
    "Reflects in a horizontal line when the mirror is vertical (or vice versa).",
    "A vertical mirror x = a changes x; a horizontal mirror y = b changes y.",
    "Decide which coordinate the mirror line fixes.", _RF),
  m("MISC.TRANS.REFLECTS_Y_FOR_X_AXIS", "Confuses the x-axis and y-axis mirror",
    "Reflects in the x-axis when the mirror is the y-axis (or vice versa).",
    "The x-axis is y = 0 and changes y; the y-axis is x = 0 and changes x.",
    "Name the axis as an equation before reflecting.", _RF),
  m("MISC.TRANS.NEGATES_WRONG_COORDINATE", "Negates the coordinate the mirror fixes",
    "Changes the coordinate that should stay the same.",
    "Reflection in x = a leaves y unchanged; reflection in y = b leaves x unchanged.",
    "Only the coordinate across the mirror moves.", _RF),
  m("MISC.TRANS.YX_CHANGES_BOTH_SIGNS", "Confuses y = x with y = -x",
    "Uses (-y, -x) for a reflection in y = x.",
    "Reflection in y = x swaps the coordinates: (x, y) -> (y, x), with no sign change.",
    "Swap x and y for y = x; negate and swap for y = -x.", _RF),
  m("MISC.TRANS.YNEGX_ONLY_SWAPS", "Confuses y = -x with y = x",
    "Uses (y, x) for a reflection in y = -x, missing the sign change.",
    "Reflection in y = -x gives (x, y) -> (-y, -x).",
    "For y = -x, swap AND negate both coordinates.", _RF),
  m("MISC.TRANS.REFLECTS_X0_FOR_XA", "Uses the y-axis instead of x = a",
    "Reflects in x = 0 instead of the given vertical line x = a.",
    "Use the actual mirror line x = a, not the y-axis.",
    "Reflection in x = a gives (2a - x, y).", _RF),
  m("MISC.TRANS.REFLECTS_Y0_FOR_YB", "Uses the x-axis instead of y = b",
    "Reflects in y = 0 instead of the given horizontal line y = b.",
    "Use the actual mirror line y = b, not the x-axis.",
    "Reflection in y = b gives (x, 2b - y).", _RF),
  // --- rotation (6) ---
  m("MISC.TRANS.ROTATES_WRONG_DIRECTION", "Rotates the wrong way",
    "Turns clockwise when the rotation is anticlockwise (or vice versa).",
    "Check the direction; 90 deg clockwise and 90 deg anticlockwise give different images.",
    "Use the stated direction relative to the centre.", _RO),
  m("MISC.TRANS.ROTATES_ABOUT_ORIGIN", "Rotates about the origin",
    "Rotates about (0, 0) instead of the given centre.",
    "Rotate about the marked centre, not the origin.",
    "Measure each point's position relative to the centre first.", _RO),
  m("MISC.TRANS.USES_180_RULE_FOR_90", "Applies the half-turn rule for a quarter turn",
    "Uses the 180 deg rule (negate both) for a 90 or 270 deg rotation.",
    "A quarter turn swaps the coordinates relative to the centre; a half turn negates them.",
    "Apply the correct quarter-turn rule.", _RO),
  m("MISC.TRANS.SWAPS_WITHOUT_SIGN", "Swaps without the sign change",
    "Swaps the centre-relative coordinates but omits the required sign change.",
    "A quarter turn swaps AND changes a sign relative to the centre.",
    "For 90 deg anticlockwise, (X, Y) -> (-Y, X).", _RO),
  m("MISC.TRANS.ROTATES_THE_CENTRE", "Shifts by the centre as well",
    "Adds the centre a second time, shifting the whole image.",
    "Translate to the centre, turn, then translate back exactly once.",
    "The centre is used once, to measure relative position.", _RO),
  m("MISC.TRANS.APPLIES_TO_ONE_VERTEX", "Rotates only one vertex",
    "Turns a single vertex and leaves the rest of the shape unchanged.",
    "Every vertex of the shape must be rotated about the same centre.",
    "Apply the rotation to all labelled vertices.", _RO),
  // --- descriptor diagnostics (5; owner K exact IDs) ---
  m("MISC.TRANS.RIGHT_TYPE_WRONG_VECTOR", "Right type, wrong translation vector",
    "Names a translation but gives the reversed or mis-signed vector.",
    "Read the vector from a corresponding pair: image - source.",
    "Check the vector against every labelled vertex.", _DT),
  m("MISC.TRANS.RIGHT_REFLECTION_WRONG_AXIS", "Right type, wrong mirror line",
    "Names a reflection but gives the wrong mirror line.",
    "The mirror line is the perpendicular bisector of each pair of corresponding points.",
    "Find the line equidistant from a point and its image.", _DR),
  m("MISC.TRANS.RIGHT_ANGLE_MISSING_CENTRE", "Angle without a centre",
    "States the angle and direction but omits the centre of rotation.",
    "A rotation is only fully described with its centre, angle, and direction.",
    "Give the centre of rotation as well as the angle and direction.", _DO),
  m("MISC.TRANS.RIGHT_CENTRE_WRONG_DIRECTION", "Right centre, wrong direction",
    "Gives the correct centre but the wrong direction (e.g. clockwise for anticlockwise).",
    "Check the turn direction; it determines the image for a quarter turn.",
    "Confirm the direction against a single corresponding pair.", _DO),
  m("MISC.TRANS.NAMES_REFLECTION_FOR_ROTATION", "Names a reflection for a rotation",
    "Describes a reflection when the mapping is a rotation.",
    "Reflections reverse orientation; rotations preserve it. Check the orientation first.",
    "Compare the sense (orientation) of the source and image.", _DO),
];

export const ALL_IDS: readonly string[] = MISCONCEPTIONS.map((mm) => mm.misconceptionId as string);

export function registry(): Json[] {
  return MISCONCEPTIONS.map((mm) => ({ ...mm }));
}

// --------------------------------------------------------------------------- //
// Per-item diagnostics (owner K).
// --------------------------------------------------------------------------- //
function diag(
  mid: string,
  kind: string,
  predicted: Json,
  expectedCode: string,
  studentText: string | null = null,
  diagnosticOnly = true,
): Json {
  const rec = MISCONCEPTIONS.find((mm) => mm.misconceptionId === mid) as Json;
  const out: Json = {
    misconceptionId: mid,
    kind,
    predicted,
    observableError: rec.observableError,
    feedback: rec.feedback,
    expectedResultCode: expectedCode,
    diagnosticOnly,
  };
  if (studentText !== null) {
    out.studentResponseText = studentText;
  }
  return out;
}

function valueDiagsTranslation(src: Point[], desc: Json): [string, Point[]][] {
  const v = desc.vector;
  const dx = v.dx;
  const dy = v.dy;
  const out: [string, Point[]][] = [];
  out.push(["MISC.TRANS.REVERSES_VECTOR", src.map((p) => [p[0] - dx, p[1] - dy] as Point)]);
  if (dx !== dy) {
    out.push(["MISC.TRANS.SWAPS_DX_DY", src.map((p) => [p[0] + dy, p[1] + dx] as Point)]);
  }
  if (dy !== 0) {
    out.push(["MISC.TRANS.CHANGES_ONLY_X", src.map((p) => [p[0] + dx, p[1]] as Point)]);
  }
  if (dx !== 0) {
    out.push(["MISC.TRANS.CHANGES_ONLY_Y", src.map((p) => [p[0], p[1] + dy] as Point)]);
  }
  if (dx !== 0) {
    out.push(["MISC.TRANS.WRONG_SIGN_ONE_COMPONENT", src.map((p) => [p[0] - dx, p[1] + dy] as Point)]);
  }
  out.push(["MISC.TRANS.TRANSLATES_FROM_ORIGIN", src.map(() => [dx, dy] as Point)]);
  return out;
}

function valueDiagsReflection(src: Point[], desc: Json): [string, Point[]][] {
  const ax = desc.axis;
  const out: [string, Point[]][] = [];
  if (ax.kind === "vertical") {
    const a = ax.value;
    out.push(["MISC.TRANS.REFLECTS_X_FOR_Y_AXIS", src.map((p) => reflectYEqB(p, a))]);
    out.push(["MISC.TRANS.NEGATES_WRONG_COORDINATE", src.map((p) => [p[0], -p[1]] as Point)]);
    if (a !== 0) {
      out.push(["MISC.TRANS.REFLECTS_X0_FOR_XA", src.map((p) => reflectXEqA(p, 0))]);
    }
  } else if (ax.kind === "horizontal") {
    const b = ax.value;
    out.push(["MISC.TRANS.REFLECTS_X_FOR_Y_AXIS", src.map((p) => reflectXEqA(p, b))]);
    out.push(["MISC.TRANS.NEGATES_WRONG_COORDINATE", src.map((p) => [-p[0], p[1]] as Point)]);
    if (b !== 0) {
      out.push(["MISC.TRANS.REFLECTS_Y0_FOR_YB", src.map((p) => reflectYEqB(p, 0))]);
    }
    out.push(["MISC.TRANS.REFLECTS_Y_FOR_X_AXIS", src.map((p) => reflectXEqA(p, b))]);
  } else if (ax.kind === "diagonal") {
    if (ax.equation === "y=x") {
      out.push(["MISC.TRANS.YX_CHANGES_BOTH_SIGNS", src.map((p) => reflectYEqNegX(p))]);
    } else {
      out.push(["MISC.TRANS.YNEGX_ONLY_SWAPS", src.map((p) => reflectYEqX(p))]);
    }
  }
  return out;
}

function valueDiagsRotation(src: Point[], desc: Json): [string, Point[]][] {
  const c = desc.centre;
  const h = c.x;
  const k = c.y;
  const q = desc.quarterTurnsCCW;
  const out: [string, Point[]][] = [];
  if (q !== 2) {
    out.push(["MISC.TRANS.ROTATES_WRONG_DIRECTION", src.map((p) => rotateQuarter(p, h, k, 4 - q))]);
    out.push(["MISC.TRANS.USES_180_RULE_FOR_90", src.map((p) => rotateQuarter(p, h, k, 2))]);
  }
  if (!(h === 0 && k === 0)) {
    out.push(["MISC.TRANS.ROTATES_ABOUT_ORIGIN", src.map((p) => rotateQuarter(p, 0, 0, q))]);
  }
  const swapped: Point[] = src.map((p) => [p[1] - k + h, p[0] - h + k] as Point);
  out.push(["MISC.TRANS.SWAPS_WITHOUT_SIGN", swapped]);
  out.push([
    "MISC.TRANS.ROTATES_THE_CENTRE",
    src.map((p) => {
      const rp = rotateQuarter(p, h, k, q);
      return [rp[0] + h, rp[1] + k] as Point;
    }),
  ]);
  if (src.length > 1) {
    const moved: Point[] = [rotateQuarter(src[0] as Point, h, k, q), ...src.slice(1)];
    out.push(["MISC.TRANS.APPLIES_TO_ONE_VERTEX", moved]);
  }
  return out;
}

export function diagnosticsFor(task: string, src: Point[], descriptor: Json): Json[] {
  const correct: Point[] = src.map((p) => applyTransform(descriptor, p));
  const out: Json[] = [];

  let valueDiags: [string, Point[]][];
  if (task === "translate_point" || task === "translate_shape") {
    valueDiags = valueDiagsTranslation(src, descriptor);
  } else if (task === "reflect_point" || task === "reflect_shape") {
    valueDiags = valueDiagsReflection(src, descriptor);
  } else if (task === "rotate_point" || task === "rotate_shape") {
    valueDiags = valueDiagsRotation(src, descriptor);
  } else {
    valueDiags = [];
  }

  if (valueDiags.length) {
    const isPoint = task.endsWith("_point");
    for (const [mid, wrong] of valueDiags) {
      if (deepEqual(wrong, correct)) {
        continue;
      }
      const predicted = isPoint
        ? { x: (wrong[0] as Point)[0], y: (wrong[0] as Point)[1] }
        : wrong.map((p) => ({ x: p[0], y: p[1] }));
      out.push(diag(mid, "value", predicted, "incorrect-coordinate"));
    }
    return out;
  }

  // --- describe tasks ---
  const kind = descriptor.kind;
  if (kind === "translation") {
    const v = descriptor.vector;
    const reversedDiffersFromOriginal = !(v.dx === -v.dx && v.dy === -v.dy);
    const wrong = reversedDiffersFromOriginal ? translationDesc(-v.dx, -v.dy) : translationDesc(v.dy, v.dx);
    out.push(
      diag("MISC.TRANS.RIGHT_TYPE_WRONG_VECTOR", "descriptor", { canonical: wrong, display: formatDisplay(wrong) }, "wrong-translation-vector"),
    );
  } else if (kind === "reflection") {
    const ax = descriptor.axis;
    let wrong: Json;
    if (ax.kind === "vertical") {
      wrong = reflectionVertical(ax.value !== 0 ? 0 : 1);
    } else if (ax.kind === "horizontal") {
      wrong = reflectionHorizontal(ax.value !== 0 ? 0 : 1);
    } else {
      wrong = reflectionVertical(0);
    }
    out.push(
      diag("MISC.TRANS.RIGHT_REFLECTION_WRONG_AXIS", "descriptor", { canonical: wrong, display: formatDisplay(wrong) }, "wrong-reflection-axis"),
    );
  } else if (kind === "rotation") {
    const c = descriptor.centre;
    const h = c.x;
    const k = c.y;
    const q = descriptor.quarterTurnsCCW;
    const deg = QUARTER_DEGREES[q];
    const direction = q === 2 ? "" : " anticlockwise";
    out.push(
      diag("MISC.TRANS.RIGHT_ANGLE_MISSING_CENTRE", "parser", null, "missing-rotation-centre", `rotation ${deg} deg${direction}`.trim()),
    );
    if (q !== 2) {
      const wrong = rotationDesc(h, k, 4 - q);
      out.push(
        diag("MISC.TRANS.RIGHT_CENTRE_WRONG_DIRECTION", "descriptor", { canonical: wrong, display: formatDisplay(wrong) }, "wrong-rotation-amount"),
      );
    }
    const refl = reflectionVertical(h);
    out.push(
      diag("MISC.TRANS.NAMES_REFLECTION_FOR_ROTATION", "descriptor", { canonical: refl, display: formatDisplay(refl) }, "wrong-transformation-type"),
    );
  }
  return out;
}
