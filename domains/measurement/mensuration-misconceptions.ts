/**
 * MISC.MENS.* — mensuration misconception & diagnostic registry (TS mirror of
 * oracle/spi_oracle/mensuration_misconceptions.py). All eight tasks are FREE-RESPONSE in v1.0.0,
 * so these are deterministic free-response diagnostics, not four-option distractors (owner C/K).
 * Three groups: mathematical (wrong value, correct unit), unit (right number, wrong unit), and a
 * single non-numeric pedagogical rule (USES_SLOPING_SIDE — diagnostic-only, no irrational distractor).
 */

import { Rational } from "../../core/exact-math/rational.ts";
import {
  type Quantity, type BaseUnit, makeLength, makeArea, quantity,
  formatValue, formatQuantity, parseQuantity, checkResponse,
} from "./mensuration-units.ts";

export const GROUP_MATH = "mathematical";
export const GROUP_UNIT = "unit";
export const GROUP_PEDAGOGICAL = "pedagogical";

type Json = Record<string, unknown>;
type Adapter = (task: string, p: Json, ans: Quantity) => string | null;

function otherBase(base: BaseUnit): BaseUnit {
  return ({ mm: "cm", cm: "m", m: "cm" } as Record<BaseUnit, BaseUnit>)[base];
}
function valQuantity(answer: Quantity, value: Rational | number): Quantity {
  return quantity(answer.dimension, answer.baseUnit, answer.exponent, value);
}
function valueResponse(answer: Quantity, wrong: Rational | number): string | null {
  const w = Rational.from(wrong);
  if (w.equals(answer.value) || w.num <= 0) return null;
  return formatQuantity(valQuantity(answer, w));
}
const num = (p: Json, k: string) => p[k] as number;

const adaptAddsTwoSides: Adapter = (t, p, a) => t !== "perimeter_rectangle" ? null : valueResponse(a, num(p, "width") + num(p, "height"));
const adaptAreaForPerimeter: Adapter = (t, p, a) => {
  if (t === "perimeter_rectangle") return valueResponse(a, num(p, "width") * num(p, "height"));
  if (t === "perimeter_composite") return valueResponse(a, num(p, "W") * num(p, "H") - num(p, "a") * num(p, "b"));
  return null;
};
const adaptPerimeterForArea: Adapter = (t, p, a) => {
  if (t === "area_rectangle") return valueResponse(a, 2 * (num(p, "width") + num(p, "height")));
  if (t === "area_composite") return valueResponse(a, 2 * (num(p, "W") + num(p, "H")));
  return null;
};
const adaptAddsDimsForArea: Adapter = (t, p, a) => {
  if (t === "area_rectangle") return valueResponse(a, num(p, "width") + num(p, "height"));
  if (t === "area_composite") return valueResponse(a, num(p, "W") + num(p, "H"));
  return null;
};
const adaptForgetsToHalve: Adapter = (t, p, a) => {
  if (t === "area_triangle") return valueResponse(a, num(p, "base") * num(p, "height"));
  if (t === "missing_triangle_base_height") {
    const known = p.hidden === "height" ? num(p, "base") : num(p, "height");
    return valueResponse(a, new Rational(num(p, "area2"), 2 * known));
  }
  return null;
};
const adaptOmitsIndentedEdge: Adapter = (t, p, a) => t !== "perimeter_composite" ? null : valueResponse(a, 2 * (num(p, "W") + num(p, "H")) - num(p, "a"));
const adaptCountsInternalEdge: Adapter = (t, p, a) => t !== "perimeter_composite" ? null : valueResponse(a, 2 * (num(p, "W") + num(p, "H")) + (num(p, "W") - num(p, "a")));
const adaptSubtractsWrongRectangle: Adapter = (t, p, a) => t !== "area_composite" ? null : valueResponse(a, num(p, "W") * num(p, "H") - (num(p, "W") - num(p, "a")) * num(p, "b"));
const adaptRightNumberNoUnit: Adapter = (_t, _p, a) => formatValue(a.value);
const adaptLinearForArea: Adapter = (_t, _p, a) => a.dimension !== "area" ? null : formatQuantity(makeLength(a.value, a.baseUnit));
const adaptSquareForPerimeter: Adapter = (_t, _p, a) => a.dimension !== "length" ? null : formatQuantity(makeArea(a.value, a.baseUnit));
const adaptWrongBaseUnit: Adapter = (_t, _p, a) => formatQuantity(quantity(a.dimension, otherBase(a.baseUnit), a.exponent, a.value));
const adaptSlopingSide: Adapter = () => null;

export interface Rule {
  id: string; group: string; title: string; observableError: string; feedback: string;
  expectedCode: string | null; adapter: Adapter;
}

export const MISCONCEPTIONS: Rule[] = [
  { id: "MISC.MENS.ADDS_TWO_SIDES_RECT", group: GROUP_MATH, title: "Adds only two sides of a rectangle", observableError: "Adds one length and one width instead of all four sides.", feedback: "A rectangle has four sides. Add all four (or use 2 × (length + width)).", expectedCode: "incorrect-value", adapter: adaptAddsTwoSides },
  { id: "MISC.MENS.USES_AREA_FOR_PERIMETER", group: GROUP_MATH, title: "Uses area when perimeter is required", observableError: "Multiplies the sides (area) when the question asks for the distance around.", feedback: "Perimeter is the distance around the outside — add the side lengths, do not multiply.", expectedCode: "incorrect-value", adapter: adaptAreaForPerimeter },
  { id: "MISC.MENS.USES_PERIMETER_FOR_AREA", group: GROUP_MATH, title: "Uses perimeter when area is required", observableError: "Adds the sides (perimeter) when the question asks for the space inside.", feedback: "Area is the space inside — multiply, do not add the sides.", expectedCode: "incorrect-value", adapter: adaptPerimeterForArea },
  { id: "MISC.MENS.ADDS_DIMS_FOR_AREA", group: GROUP_MATH, title: "Adds dimensions instead of multiplying for area", observableError: "Adds length and width instead of multiplying them.", feedback: "Area of a rectangle is length × width, not length + width.", expectedCode: "incorrect-value", adapter: adaptAddsDimsForArea },
  { id: "MISC.MENS.FORGETS_TO_HALVE", group: GROUP_MATH, title: "Forgets to halve base × height for a triangle", observableError: "Computes base × height without halving.", feedback: "A triangle is half of the surrounding rectangle — remember the ½ (÷ 2).", expectedCode: "incorrect-value", adapter: adaptForgetsToHalve },
  { id: "MISC.MENS.OMITS_INDENTED_EDGE", group: GROUP_MATH, title: "Omits an indented edge from a composite perimeter", observableError: "Misses one of the step edges when tracing the outside.", feedback: "Trace the whole outside boundary — include every step edge of the indent.", expectedCode: "incorrect-value", adapter: adaptOmitsIndentedEdge },
  { id: "MISC.MENS.COUNTS_INTERNAL_EDGE", group: GROUP_MATH, title: "Counts an internal decomposition edge in a perimeter", observableError: "Includes a cutting line used to split the shape as if it were an outer edge.", feedback: "Only the outside edges count for perimeter — a line you draw to split the shape is not part of it.", expectedCode: "incorrect-value", adapter: adaptCountsInternalEdge },
  { id: "MISC.MENS.SUBTRACTS_WRONG_RECTANGLE", group: GROUP_MATH, title: "Subtracts the wrong rectangle in a composite area", observableError: "Subtracts a rectangle that is not the missing corner.", feedback: "Subtract exactly the missing corner rectangle (its width × its height).", expectedCode: "incorrect-value", adapter: adaptSubtractsWrongRectangle },
  { id: "MISC.MENS.RIGHT_NUMBER_NO_UNIT", group: GROUP_UNIT, title: "Right number, no unit", observableError: "Gives the correct number but omits the unit.", feedback: "Always state the unit. A measurement is not complete without it.", expectedCode: "missing-unit", adapter: adaptRightNumberNoUnit },
  { id: "MISC.MENS.LINEAR_UNITS_FOR_AREA", group: GROUP_UNIT, title: "Linear units given for an area", observableError: "Labels an area with a length unit (e.g. cm instead of cm^2).", feedback: "Area is measured in SQUARE units — write cm^2, not cm.", expectedCode: "wrong-exponent", adapter: adaptLinearForArea },
  { id: "MISC.MENS.SQUARE_UNITS_FOR_PERIMETER", group: GROUP_UNIT, title: "Square units given for a perimeter / length", observableError: "Labels a length with a square unit (e.g. cm^2 instead of cm).", feedback: "A perimeter or length is measured in LINEAR units — write cm, not cm^2.", expectedCode: "wrong-exponent", adapter: adaptSquareForPerimeter },
  { id: "MISC.MENS.WRONG_BASE_UNIT", group: GROUP_UNIT, title: "Right number, wrong base unit", observableError: "Gives the correct number with a different base unit from the figure.", feedback: "Use the unit shown on the figure. Do not change between mm, cm and m here.", expectedCode: "wrong-base-unit", adapter: adaptWrongBaseUnit },
  { id: "MISC.MENS.USES_SLOPING_SIDE", group: GROUP_PEDAGOGICAL, title: "Uses a sloping side instead of the perpendicular height", observableError: "Reads a slanted side of the triangle as the height.", feedback: "Use the perpendicular height (the line marked with a right angle), not a sloping side.", expectedCode: null, adapter: adaptSlopingSide },
];

const BY_ID: Record<string, Rule> = Object.fromEntries(MISCONCEPTIONS.map((m) => [m.id, m]));

export const TASK_DIAGNOSTICS: Record<string, string[]> = {
  perimeter_rectangle: ["MISC.MENS.ADDS_TWO_SIDES_RECT", "MISC.MENS.USES_AREA_FOR_PERIMETER", "MISC.MENS.SQUARE_UNITS_FOR_PERIMETER", "MISC.MENS.WRONG_BASE_UNIT", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
  perimeter_composite: ["MISC.MENS.OMITS_INDENTED_EDGE", "MISC.MENS.COUNTS_INTERNAL_EDGE", "MISC.MENS.USES_AREA_FOR_PERIMETER", "MISC.MENS.SQUARE_UNITS_FOR_PERIMETER", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
  area_rectangle: ["MISC.MENS.ADDS_DIMS_FOR_AREA", "MISC.MENS.USES_PERIMETER_FOR_AREA", "MISC.MENS.LINEAR_UNITS_FOR_AREA", "MISC.MENS.WRONG_BASE_UNIT", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
  area_triangle: ["MISC.MENS.FORGETS_TO_HALVE", "MISC.MENS.USES_SLOPING_SIDE", "MISC.MENS.LINEAR_UNITS_FOR_AREA", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
  area_composite: ["MISC.MENS.SUBTRACTS_WRONG_RECTANGLE", "MISC.MENS.ADDS_DIMS_FOR_AREA", "MISC.MENS.USES_PERIMETER_FOR_AREA", "MISC.MENS.LINEAR_UNITS_FOR_AREA", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
  // Owner C4: only rules with a genuine pathway per task (no inapplicable value rules with a null
  // prediction). USES_AREA_FOR_PERIMETER / USES_PERIMETER_FOR_AREA dropped from the inverse tasks.
  missing_length_perimeter: ["MISC.MENS.SQUARE_UNITS_FOR_PERIMETER", "MISC.MENS.WRONG_BASE_UNIT", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
  missing_dimension_area: ["MISC.MENS.SQUARE_UNITS_FOR_PERIMETER", "MISC.MENS.WRONG_BASE_UNIT", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
  missing_triangle_base_height: ["MISC.MENS.FORGETS_TO_HALVE", "MISC.MENS.USES_SLOPING_SIDE", "MISC.MENS.SQUARE_UNITS_FOR_PERIMETER", "MISC.MENS.RIGHT_NUMBER_NO_UNIT"],
};

const GROUP_KIND: Record<string, string> = { [GROUP_MATH]: "numeric", [GROUP_UNIT]: "unit", [GROUP_PEDAGOGICAL]: "pedagogical" };

export interface Diagnostic {
  id: string; title: string; group: string; kind: string; observableError: string; feedback: string;
  appliesTo: string; diagnosticOnly: boolean; predictedResponse: string | null; resultCode: string | null; distinctFromAnswer: boolean;
}

export function diagnosticsFor(task: string, params: Json, answer: Quantity): Diagnostic[] {
  // Owner C4: numeric/unit rules carry a non-null prediction; pedagogical rules are diagnosticOnly;
  // an inapplicable value/unit rule (null prediction) is OMITTED entirely.
  const out: Diagnostic[] = [];
  for (const mid of TASK_DIAGNOSTICS[task] ?? []) {
    const rule = BY_ID[mid] as Rule;
    const kind = GROUP_KIND[rule.group]!;
    const base = { id: mid, title: rule.title, group: rule.group, kind, observableError: rule.observableError, feedback: rule.feedback, appliesTo: task };
    if (rule.group === GROUP_PEDAGOGICAL) {
      out.push({ ...base, diagnosticOnly: true, predictedResponse: null, resultCode: null, distinctFromAnswer: true });
      continue;
    }
    const predicted = rule.adapter(task, params, answer);
    if (predicted === null) continue; // inapplicable — never emit a null-with-code record
    const res = checkResponse(predicted, answer);
    out.push({ ...base, diagnosticOnly: false, predictedResponse: predicted, resultCode: res.code, distinctFromAnswer: !res.correct });
  }
  return out;
}

export function diagnose(task: string, params: Json, answer: Quantity, response: string): { id: string | null; feedback: string; resultCode: string } | null {
  const res = checkResponse(response, answer);
  if (res.correct) return null;
  const norm = response.trim();
  for (const entry of diagnosticsFor(task, params, answer)) {
    const pred = entry.predictedResponse;
    if (pred !== null && checkResponse(norm, answer).code === res.code) {
      if (entry.group === "unit") {
        if (entry.resultCode === res.code) return { id: entry.id, feedback: entry.feedback, resultCode: res.code };
      } else {
        const pr = parseQuantity(pred).q, sr = parseQuantity(norm).q;
        if (pr && sr && pr.value.equals(sr.value) && pr.exponent === sr.exponent) {
          return { id: entry.id, feedback: entry.feedback, resultCode: res.code };
        }
      }
    }
  }
  const fallback = ({ "missing-unit": "MISC.MENS.RIGHT_NUMBER_NO_UNIT", "wrong-base-unit": "MISC.MENS.WRONG_BASE_UNIT" } as Record<string, string>)[res.code];
  if (fallback && BY_ID[fallback]) return { id: fallback, feedback: (BY_ID[fallback] as Rule).feedback, resultCode: res.code };
  return { id: null, feedback: res.feedback, resultCode: res.code };
}

export { BY_ID as _BY_ID };
