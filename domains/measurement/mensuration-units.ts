/**
 * gen.measurement.mensuration v1.0.0 — dimensional-quantity answer contract (TS mirror of
 * oracle/spi_oracle/mensuration_units.py). Byte-for-byte parity with the Python oracle on the
 * serialized answer encoding (canonical {num,den} + structured measure + derived ASCII display).
 *
 * Quantity model (owner B): { dimension: "length"|"area", baseUnit: "mm"|"cm"|"m", exponent: 1|2,
 * value: Rational }. The checker treats unit meaning STRUCTURALLY (owner D) and never converts
 * between base units in v1.0.0.
 */

import { Rational } from "../../core/exact-math/rational.ts";

export type Dimension = "length" | "area";
export type BaseUnit = "mm" | "cm" | "m";

export const BASE_UNITS: BaseUnit[] = ["mm", "cm", "m"];
export const RESULT_CODES = [
  "correct", "incorrect-value", "missing-unit", "wrong-base-unit",
  "wrong-dimension", "wrong-exponent", "malformed-response",
] as const;
export type ResultCode = (typeof RESULT_CODES)[number];

export interface Quantity {
  dimension: Dimension;
  baseUnit: BaseUnit;
  exponent: 1 | 2;
  value: Rational;
}

export function makeLength(value: Rational | number, baseUnit: BaseUnit): Quantity {
  return { dimension: "length", baseUnit, exponent: 1, value: Rational.from(value) };
}
export function makeArea(value: Rational | number, baseUnit: BaseUnit): Quantity {
  return { dimension: "area", baseUnit, exponent: 2, value: Rational.from(value) };
}
export function quantity(dimension: Dimension, baseUnit: BaseUnit, exponent: 1 | 2, value: Rational | number): Quantity {
  return { dimension, baseUnit, exponent, value: Rational.from(value) };
}

// --- Formatter ---
export function formatValue(value: Rational): string {
  return value.den === 1 ? String(value.num) : `${value.num}/${value.den}`;
}
export function unitToken(baseUnit: BaseUnit, exponent: number): string {
  return exponent === 1 ? baseUnit : `${baseUnit}^2`;
}
export function formatQuantity(q: Quantity): string {
  return `${formatValue(q.value)} ${unitToken(q.baseUnit, q.exponent)}`;
}
export function formatQuantityDisplay(q: Quantity): string {
  return `${formatValue(q.value)} ${q.baseUnit}${q.exponent === 2 ? "²" : ""}`;
}

export function encodeQuantityAnswer(q: Quantity): Record<string, unknown> {
  return {
    type: "quantity",
    canonical: { num: q.value.num, den: q.value.den },
    measure: { dimension: q.dimension, baseUnit: q.baseUnit, exponent: q.exponent },
    display: formatQuantity(q),
  };
}

// --- Alias table (mirrors the Python _build_alias_table) ---
function buildAliasTable(): Map<string, [BaseUnit, 1 | 2]> {
  const table = new Map<string, [BaseUnit, 1 | 2]>();
  const names: Record<BaseUnit, string[]> = {
    mm: ["mm", "millimetre", "millimetres", "millimeter", "millimeters"],
    cm: ["cm", "centimetre", "centimetres", "centimeter", "centimeters"],
    m: ["m", "metre", "metres", "meter", "meters"],
  };
  (Object.keys(names) as BaseUnit[]).forEach((base) => {
    for (const f of names[base]) {
      table.set(f, [base, 1]);
      if (f === base) {
        table.set(`${f}^2`, [base, 2]);
        table.set(`${f}2`, [base, 2]);
      }
      table.set(`${f} squared`, [base, 2]);
      table.set(`square ${f}`, [base, 2]);
      table.set(`sq ${f}`, [base, 2]);
    }
  });
  return table;
}
const ALIAS = buildAliasTable();

const NUM_RE = /^([+-]?\d+\s*\/\s*\d+|[+-]?\d+\.\d+|[+-]?\d+)/;

function normalize(s: string): string {
  return s.replace(/−/g, "-").replace(/²/g, "^2").trim();
}

function parseNumber(numRaw: string): Rational | null {
  const num = numRaw.replace(/\s+/g, "");
  try {
    if (num.includes("/")) {
      const parts = num.split("/");
      const n = parts[0] ?? "", d = parts[1] ?? "";
      if (parseInt(d, 10) === 0) return null;
      return new Rational(parseInt(n, 10), parseInt(d, 10));
    }
    if (num.includes(".")) {
      const parts = num.split(".");
      const whole = parts[0] ?? "", frac = parts[1] ?? "";
      if (!/^\d+$/.test(frac)) return null;
      const sign = whole.startsWith("-") ? -1 : 1;
      const wd = whole.replace(/^[+-]/, "");
      const scale = 10 ** frac.length;
      const mag = new Rational(parseInt(wd || "0", 10) * scale + parseInt(frac, 10), scale);
      return sign === -1 ? mag.neg() : mag;
    }
    return new Rational(parseInt(num, 10), 1);
  } catch {
    return null;
  }
}

export function parseQuantity(text: string | null): { q: Quantity | null; code: ResultCode | null } {
  if (text === null || text === undefined) return { q: null, code: "malformed-response" };
  const norm = normalize(text);
  if (norm === "") return { q: null, code: "malformed-response" };
  const m = NUM_RE.exec(norm);
  if (!m) return { q: null, code: "malformed-response" };
  const value = parseNumber(m[0]);
  if (value === null) return { q: null, code: "malformed-response" };
  const rest = norm.slice(m[0].length).trim();
  if (rest === "") return { q: null, code: "missing-unit" };
  const key = rest.toLowerCase().replace(/\s+/g, " ").trim();
  const hit = ALIAS.get(key);
  if (!hit) return { q: null, code: "malformed-response" };
  const [base, exponent] = hit;
  return { q: { dimension: exponent === 1 ? "length" : "area", baseUnit: base, exponent, value }, code: null };
}

// --- Equivalence checker ---
function basePhrase(base: BaseUnit): string {
  return { mm: "millimetres (mm)", cm: "centimetres (cm)", m: "metres (m)" }[base];
}
function expectedPhrase(q: Quantity): string {
  return q.dimension === "length"
    ? `a length in ${basePhrase(q.baseUnit)}`
    : `an area in square ${q.baseUnit} (${unitToken(q.baseUnit, 2)})`;
}

export interface CheckResult { code: ResultCode; correct: boolean; feedback: string; expected: string; parsed?: string; }

export function checkResponse(text: string, expected: Quantity): CheckResult {
  const { q: parsed, code } = parseQuantity(text);
  if (code === "missing-unit") {
    return result("missing-unit", expected, `You gave a number but no unit. This answer needs ${expectedPhrase(expected)}.`);
  }
  if (code === "malformed-response") {
    return result("malformed-response", expected,
      "I could not read your answer. Write a number and a unit, for example 12 cm or 24 cm^2.");
  }
  const p = parsed as Quantity;
  const baseMatch = p.baseUnit === expected.baseUnit;
  const expMatch = p.exponent === expected.exponent;
  if (baseMatch && expMatch) {
    if (p.value.equals(expected.value)) return result("correct", expected, "Correct.", p);
    return result("incorrect-value", expected,
      `The unit is right, but the number is not. Re-check your working — the answer is ${formatQuantity(expected)}.`, p);
  }
  if (baseMatch && !expMatch) {
    const msg = expected.exponent === 2
      ? `An area is measured in SQUARE units (${unitToken(expected.baseUnit, 2)}); you used linear units (${unitToken(p.baseUnit, 1)}).`
      : `A length is measured in LINEAR units (${unitToken(expected.baseUnit, 1)}); you used square units (${unitToken(p.baseUnit, 2)}).`;
    return result("wrong-exponent", expected, msg, p);
  }
  if (!baseMatch && expMatch) {
    return result("wrong-base-unit", expected,
      `This answer must be given in ${basePhrase(expected.baseUnit)}, using the unit shown on the figure — do not convert from ${basePhrase(p.baseUnit)}.`, p);
  }
  return result("wrong-dimension", expected,
    `This answer should be ${expectedPhrase(expected)}; ${formatQuantity(p)} is a different kind of measurement.`, p);
}

function result(code: ResultCode, expected: Quantity, feedback: string, parsed?: Quantity): CheckResult {
  const out: CheckResult = { code, correct: code === "correct", feedback, expected: formatQuantity(expected) };
  if (parsed) out.parsed = formatQuantity(parsed);
  return out;
}

/** Exact terminating-decimal string for `value`, or null if it does not terminate. */
export function formatDecimal(value: Rational): string | null {
  let t = value.den, twos = 0, fives = 0;
  while (t % 2 === 0) { t /= 2; twos++; }
  while (t % 5 === 0) { t /= 5; fives++; }
  if (t !== 1) return null;
  const k = Math.max(twos, fives);
  if (k === 0) return String(value.num);
  const scaled = value.num * (10 ** k / value.den);
  let s = String(Math.abs(scaled)).padStart(k + 1, "0");
  s = s.slice(0, -k) + "." + s.slice(-k);
  return (scaled < 0 ? "-" : "") + s;
}

export interface Evidence { scenario: string; response: string; expectedCode: ResultCode; genuinelyDifferent: boolean; }

/** The shared quantity-checker evidence matrix (owner D/C3): genuinely-different accepted forms, every
 * reject code, and every malformed-response category. Mirror of mensuration_units.checker_evidence. */
export function checkerEvidence(ans: Quantity): Evidence[] {
  const val = formatValue(ans.value);
  const tok = unitToken(ans.baseUnit, ans.exponent);
  const other = ({ mm: "cm", cm: "m", m: "cm" } as Record<BaseUnit, BaseUnit>)[ans.baseUnit];
  const ev: Evidence[] = [];
  const add = (scenario: string, response: string, expectedCode: ResultCode, genuinelyDifferent = false) =>
    ev.push({ scenario, response, expectedCode, genuinelyDifferent });

  add("canonical form", formatQuantity(ans), "correct", false);
  add("no-space unit form", `${val}${tok}`, "correct", true);
  add("extra-space form", `${val}  ${tok}`, "correct", true);
  if (ans.value.den !== 1) {
    add("unreduced fraction form", `${ans.value.num * 2}/${ans.value.den * 2} ${tok}`, "correct", true);
    const dec = formatDecimal(ans.value);
    if (dec !== null) add("terminating decimal form", `${dec} ${tok}`, "correct", true);
  }
  if (ans.exponent === 2) add("Unicode superscript form", `${val} ${ans.baseUnit}²`, "correct", true);

  add("bare number (no unit)", val, "missing-unit");
  add("wrong base unit (no conversion)", formatQuantity(quantity(ans.dimension, other, ans.exponent, ans.value)), "wrong-base-unit");
  add("incorrect value, correct unit", formatQuantity(quantity(ans.dimension, ans.baseUnit, ans.exponent, ans.value.add(new Rational(1, 1)))), "incorrect-value");
  if (ans.dimension === "area") {
    add("linear units for an area", formatQuantity(makeLength(ans.value, ans.baseUnit)), "wrong-exponent");
    add("different dimensional quantity", formatQuantity(makeLength(ans.value, other)), "wrong-dimension");
  } else {
    add("square units for a length", formatQuantity(makeArea(ans.value, ans.baseUnit)), "wrong-exponent");
    add("different dimensional quantity", formatQuantity(makeArea(ans.value, other)), "wrong-dimension");
  }

  add("scientific notation", `${val}e2 ${tok}`, "malformed-response");
  add("trailing unparsed text", `${formatQuantity(ans)} long`, "malformed-response");
  add("conflicting unit tokens", `${val} ${ans.baseUnit} ${other}`, "malformed-response");
  add("malformed fraction", `${ans.value.num}/ ${tok}`, "malformed-response");
  add("malformed exponent", `${val} ${ans.baseUnit}^3`, "malformed-response");
  add("unsupported compound unit", `${val} ${ans.baseUnit}/s`, "malformed-response");
  add("empty response", "", "malformed-response");
  add("multiple numerical expressions", `${val} ${tok} ${val} ${tok}`, "malformed-response");
  return ev;
}
