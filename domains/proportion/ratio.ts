/**
 * gen.proportion.ratio v1.0.0 — generator, family-local ratio renderer (bar models / double number
 * lines / proportional best-buy table), and the independent validator.
 *
 * Byte-for-byte TypeScript mirror of oracle/spi_oracle/ratio.py.
 * EXACT: every value is an integer or an exact Rational — no floats, tolerance, or irrational anywhere.
 */

import { Mulberry32 } from "../../core/seeded-random/mulberry32.ts";
import { canonicalStringify } from "../../core/serialization/canonical.ts";
import { round3, clamp01 } from "../../core/difficulty/band.ts";
import { Rational } from "../../core/exact-math/rational.ts";
import * as RC from "./ratio-core.ts";
import * as RM from "./ratio-misconceptions.ts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = any;

export const GENERATOR_ID = "gen.proportion.ratio";
export const GENERATOR_VERSION = "1.0.0";
export const VALIDATOR_VERSION = "1.0.0";
const CALCULATOR_POLICY = "calculator-not-required";

// --------------------------------------------------------------------------- //
// Task -> objective mapping
// --------------------------------------------------------------------------- //
export const RATIO_TASKS: readonly string[] = [
  "simplify",
  "write_from_quantities",
  "ratio_to_fraction",
  "fraction_to_ratio",
  "share_two_part",
  "share_three_part",
  "missing_part",
  "direct_proportion",
  "inverse_proportion",
  "unit_rate",
  "best_buy",
  "simple_scale",
];

export const OBJECTIVE_BY_TASK: Record<string, string> = {
  simplify: "SPI.MIDDLE.RATIO.SIMPLIFY.01",
  write_from_quantities: "SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01",
  ratio_to_fraction: "SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01",
  fraction_to_ratio: "SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01",
  share_two_part: "SPI.MIDDLE.RATIO.SHARE_TWO_PART.01",
  share_three_part: "SPI.MIDDLE.RATIO.SHARE_THREE_PART.01",
  missing_part: "SPI.MIDDLE.RATIO.MISSING_PART.01",
  direct_proportion: "SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01",
  inverse_proportion: "SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01",
  unit_rate: "SPI.MIDDLE.RATIO.UNIT_RATE.01",
  best_buy: "SPI.MIDDLE.RATIO.BEST_BUY.01",
  simple_scale: "SPI.MIDDLE.RATIO.SIMPLE_SCALE.01",
};

// Interaction policy (owner C).
export const MC_ELIGIBLE_TASKS: readonly string[] = [
  "simplify",
  "ratio_to_fraction",
  "fraction_to_ratio",
  "direct_proportion",
  "inverse_proportion",
  "best_buy",
];
export const MC_ONLY_TASKS: readonly string[] = ["best_buy"];

// Answer kind per task (owner D).
const ANSWER_KIND: Record<string, string> = {
  simplify: "ratio",
  write_from_quantities: "ratio",
  ratio_to_fraction: "rational",
  fraction_to_ratio: "ratio",
  share_two_part: "table",
  share_three_part: "table",
  missing_part: "integer",
  direct_proportion: "rational",
  inverse_proportion: "integer",
  unit_rate: "rational",
  best_buy: "mc",
  simple_scale: "rational",
};

// Figure kind per task (owner J).
const FIGURE_KIND: Record<string, string | null> = {
  ratio_to_fraction: "bar",
  fraction_to_ratio: "bar",
  share_two_part: "bar",
  share_three_part: "bar",
  missing_part: "bar",
  direct_proportion: "numberline",
  unit_rate: "numberline",
  simple_scale: "numberline",
  best_buy: "table",
  simplify: null,
  write_from_quantities: null,
  inverse_proportion: null,
};

// Single source-of-truth difficulty bands.
const TASK_BANDS: Record<string, [number, number]> = {
  simplify: [1, 3],
  write_from_quantities: [1, 3],
  ratio_to_fraction: [2, 3],
  fraction_to_ratio: [2, 3],
  share_two_part: [2, 3],
  share_three_part: [3, 4],
  missing_part: [2, 3],
  direct_proportion: [2, 4],
  inverse_proportion: [3, 4],
  unit_rate: [2, 3],
  best_buy: [3, 4],
  simple_scale: [2, 4],
};

const MAX_PARAM_ATTEMPTS = 800;

export class InteractionNotSupported extends Error {}

function supportedInteractions(task: string): string[] {
  if (MC_ONLY_TASKS.includes(task)) {
    return ["multiple-choice"];
  }
  if (MC_ELIGIBLE_TASKS.includes(task)) {
    return ["free-response", "multiple-choice"];
  }
  return ["free-response"];
}

// --------------------------------------------------------------------------- //
// Themed contexts.
// --------------------------------------------------------------------------- //
const _QTY_THEMES: [string, string[], string][] = [
  ["Paint mixture", ["red paint", "white paint", "blue paint"], "litres"],
  ["Fruit basket", ["apples", "oranges", "pears"], "pieces"],
  ["Class survey", ["boys", "girls", "teachers"], "people"],
  ["Recipe", ["flour", "sugar", "butter"], "grams"],
  ["Garden", ["roses", "tulips", "daisies"], "plants"],
];
const _SHARE_THEMES: [string, string[], string][] = [
  ["Sharing money", ["Amir", "Beth", "Carl"], "pounds"],
  ["Sharing sweets", ["Dana", "Eli", "Faye"], "sweets"],
  ["Sharing marbles", ["Gus", "Hana", "Ivan"], "marbles"],
  ["Sharing stickers", ["Jo", "Kim", "Lee"], "stickers"],
];
const _RATE_THEMES: [string, string][] = [
  ["books", "shelves"],
  ["apples", "bags"],
  ["pages", "minutes"],
  ["litres", "tanks"],
  ["kilometres", "hours"],
  ["words", "lines"],
];
const _BUY_THEMES: [string, string, string][] = [
  ["rice", "grams", "pack"],
  ["juice", "millilitres", "bottle"],
  ["nails", "nails", "box"],
  ["paper", "sheets", "ream"],
  ["seeds", "seeds", "packet"],
];
const _INVERSE_THEMES: [string, string, string][] = [
  ["workers", "days", "to finish the job"],
  ["taps", "hours", "to fill the tank"],
  ["machines", "minutes", "to complete the batch"],
  ["painters", "days", "to paint the hall"],
];
const _SCALE_THEMES: [string, string, string, string][] = [
  ["map", "the real distance", "centimetres on the map", "kilometres on the ground"],
  ["model", "the real length", "centimetres on the model", "metres in real life"],
  ["plan", "the real width", "centimetres on the plan", "metres in the building"],
];

function _n(rng: Mulberry32, k: number): number {
  return rng.nextInt(0, k - 1);
}

function _pick<T>(rng: Mulberry32, items: T[]): T {
  return items[_n(rng, items.length)] as T;
}

function _dispRat(f: Rational): string {
  return f.den === 1 ? String(f.num) : `${f.num}/${f.den}`;
}

function _esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// --------------------------------------------------------------------------- //
// Parameter draws (seeded; exact integer/Rational only; deterministic redraw)
// --------------------------------------------------------------------------- //
function _drawSimplify(rng: Mulberry32): Json | null {
  const three = _n(rng, 3) === 0;
  const k = 2 + _n(rng, 7);
  let base: number[];
  if (three) {
    base = [1 + _n(rng, 6), 1 + _n(rng, 6), 1 + _n(rng, 6)];
  } else {
    base = [1 + _n(rng, 8), 1 + _n(rng, 8)];
  }
  if (RC.gcdList(base) !== 1) {
    return null;
  }
  const parts = base.map((p) => p * k);
  return { task: "simplify", parts };
}

function _drawWriteFromQuantities(rng: Mulberry32): Json | null {
  const [title, labels, unit] = _pick(rng, _QTY_THEMES);
  const three = _n(rng, 3) === 0;
  const nq = three ? 3 : 2;
  const k = 1 + _n(rng, 6);
  const base: number[] = [];
  for (let i = 0; i < nq; i++) {
    base.push(1 + _n(rng, 7));
  }
  if (RC.gcdList(base) !== 1) {
    return null;
  }
  const quantities = base.map((b) => b * k);
  return { task: "write_from_quantities", title, labels: labels.slice(0, nq), unit, quantities };
}

function _drawRatioToFraction(rng: Mulberry32): Json | null {
  const [title, labels, unit] = _pick(rng, _QTY_THEMES);
  const parts = [1 + _n(rng, 7), 1 + _n(rng, 7)];
  if (parts[0] === parts[1]) {
    return null;
  }
  const partIndex = _n(rng, 2);
  return { task: "ratio_to_fraction", title, labels: labels.slice(0, 2), unit, parts, partIndex };
}

function _drawFractionToRatio(rng: Mulberry32): Json | null {
  const den = 3 + _n(rng, 8);
  const num = 1 + _n(rng, den - 1);
  const rest = den - num;
  if (num === rest) {
    return null;
  }
  return { task: "fraction_to_ratio", num, den };
}

function _drawShare(rng: Mulberry32, three: boolean): Json | null {
  const [title, labels, unit] = _pick(rng, _SHARE_THEMES);
  const nq = three ? 3 : 2;
  const parts: number[] = [];
  for (let i = 0; i < nq; i++) {
    parts.push(1 + _n(rng, 5));
  }
  if (RC.gcdList(parts) !== 1) {
    return null;
  }
  if (new Set(parts).size === 1) {
    return null;
  }
  const s = parts.reduce((acc, p) => acc + p, 0);
  const one = 2 + _n(rng, 9);
  const total = one * s;
  return {
    task: three ? "share_three_part" : "share_two_part",
    title,
    labels: labels.slice(0, nq),
    unit,
    parts,
    total,
  };
}

function _drawMissingPart(rng: Mulberry32): Json | null {
  const [title, labels, unit] = _pick(rng, _SHARE_THEMES);
  const parts = [1 + _n(rng, 6), 1 + _n(rng, 6)];
  if (RC.gcdList(parts) !== 1 || parts[0] === parts[1]) {
    return null;
  }
  const knownIndex = _n(rng, 2);
  const missingIndex = 1 - knownIndex;
  const one = 2 + _n(rng, 9);
  const knownValue = one * (parts[knownIndex] as number);
  return {
    task: "missing_part",
    title,
    labels: labels.slice(0, 2),
    unit,
    parts,
    knownIndex,
    missingIndex,
    knownValue,
  };
}

function _drawDirectProportion(rng: Mulberry32): Json | null {
  const [a, b] = _pick(rng, _RATE_THEMES);
  const quantity = 2 + _n(rng, 7);
  const oneUnitNum = 1 + _n(rng, 12);
  const wholeResult = _n(rng, 2) === 0;
  let total: number;
  if (wholeResult) {
    total = quantity * oneUnitNum;
  } else {
    total = oneUnitNum;
  }
  const target = 2 + _n(rng, 9);
  if (target === quantity) {
    return null;
  }
  return { task: "direct_proportion", givenLabel: a, perLabel: b, quantity, total, target };
}

function _drawInverseProportion(rng: Mulberry32): Json | null {
  const [agent, unit, tail] = _pick(rng, _INVERSE_THEMES);
  const q1 = 2 + _n(rng, 7);
  const v1 = 2 + _n(rng, 11);
  const prod = q1 * v1;
  const divisors: number[] = [];
  for (let d = 2; d <= prod; d++) {
    if (prod % d === 0 && d !== q1 && Math.trunc(prod / d) !== v1) {
      divisors.push(d);
    }
  }
  if (divisors.length === 0) {
    return null;
  }
  const q2 = divisors[_n(rng, divisors.length)] as number;
  return { task: "inverse_proportion", agent, unit, tail, q1, v1, q2 };
}

function _drawUnitRate(rng: Mulberry32): Json | null {
  const [a, b] = _pick(rng, _RATE_THEMES);
  const quantity = 2 + _n(rng, 7);
  const whole = _n(rng, 2) === 0;
  let total: number;
  if (whole) {
    total = quantity * (1 + _n(rng, 12));
  } else {
    total = 1 + _n(rng, 40);
  }
  if (total === 0) {
    return null;
  }
  return { task: "unit_rate", amountLabel: a, perLabel: b, total, quantity };
}

function _drawBestBuy(rng: Mulberry32): Json | null {
  const [product, unit, pack] = _pick(rng, _BUY_THEMES);
  const nOpts = 2 + _n(rng, 2);
  const options: Json[] = [];
  for (let i = 0; i < nOpts; i++) {
    const packSize = 2 + _n(rng, 9);
    const per = 1 + _n(rng, 12);
    const totalAmount = packSize * per;
    options.push({
      label: String.fromCharCode("A".charCodeAt(0) + i),
      packSize,
      totalAmount,
      unitRate: { num: totalAmount, den: packSize },
    });
  }
  // require a UNIQUE strict-minimum exact unit rate (redraw on a tie)
  const rates = options.map((o) => new Rational(o.totalAmount as number, o.packSize as number));
  const mn = _minRational(rates);
  const winners: number[] = [];
  rates.forEach((r, i) => {
    if (r.equals(mn)) winners.push(i);
  });
  if (winners.length !== 1) {
    return null;
  }
  const correct = options[winners[0] as number].label as string;
  return { task: "best_buy", product, unit, pack, options, correctLabel: correct };
}

function _drawSimpleScale(rng: Mulberry32): Json | null {
  const [kind, _what, srcUnit, dstUnit] = _pick(rng, _SCALE_THEMES);
  void _what;
  const fnum = 1 + _n(rng, 9);
  const fden = 1 + _n(rng, 9);
  if (fnum === fden) {
    return null;
  }
  const value = 2 + _n(rng, 19);
  const direction = "multiply";
  return {
    task: "simple_scale",
    scaleKind: kind,
    srcUnit,
    dstUnit,
    value,
    factorNum: fnum,
    factorDen: fden,
    direction,
  };
}

const _DRAW: Record<string, (r: Mulberry32) => Json | null> = {
  simplify: (r) => _drawSimplify(r),
  write_from_quantities: (r) => _drawWriteFromQuantities(r),
  ratio_to_fraction: (r) => _drawRatioToFraction(r),
  fraction_to_ratio: (r) => _drawFractionToRatio(r),
  share_two_part: (r) => _drawShare(r, false),
  share_three_part: (r) => _drawShare(r, true),
  missing_part: (r) => _drawMissingPart(r),
  direct_proportion: (r) => _drawDirectProportion(r),
  inverse_proportion: (r) => _drawInverseProportion(r),
  unit_rate: (r) => _drawUnitRate(r),
  best_buy: (r) => _drawBestBuy(r),
  simple_scale: (r) => _drawSimpleScale(r),
};

/** Signed exact comparison of two Rationals: -1 / 0 / 1 (cross-multiplication; dens are positive). */
function _cmpRational(a: Rational, b: Rational): number {
  const lhs = a.num * b.den;
  const rhs = b.num * a.den;
  return lhs < rhs ? -1 : lhs > rhs ? 1 : 0;
}

function _minRational(rs: Rational[]): Rational {
  let m = rs[0] as Rational;
  for (let i = 1; i < rs.length; i++) {
    if (_cmpRational(rs[i] as Rational, m) < 0) {
      m = rs[i] as Rational;
    }
  }
  return m;
}

// --------------------------------------------------------------------------- //
// Solvers (exact).
// --------------------------------------------------------------------------- //
function _solve(task: string, params: Json): Json {
  if (task === "simplify") {
    return RC.simplifyParts(params.parts as number[]);
  }
  if (task === "write_from_quantities") {
    return RC.simplifyParts(params.quantities as number[]);
  }
  if (task === "ratio_to_fraction") {
    const a = (params.parts as number[])[0] as number;
    const b = (params.parts as number[])[1] as number;
    const part = (params.parts as number[])[params.partIndex as number] as number;
    return new Rational(part, a + b);
  }
  if (task === "fraction_to_ratio") {
    const num = params.num as number;
    const den = params.den as number;
    return RC.simplifyParts([num, den - num]);
  }
  if (task === "share_two_part" || task === "share_three_part") {
    return RC.share(params.total as number, params.parts as number[]);
  }
  if (task === "missing_part") {
    return RC.missingPart(
      params.knownValue as number,
      params.knownIndex as number,
      params.missingIndex as number,
      params.parts as number[],
    );
  }
  if (task === "direct_proportion") {
    return RC.directProportion(params.total as number, params.quantity as number, params.target as number);
  }
  if (task === "inverse_proportion") {
    return RC.inverseProportion(params.q1 as number, params.v1 as number, params.q2 as number);
  }
  if (task === "unit_rate") {
    return RC.unitRate(params.total as number, params.quantity as number);
  }
  if (task === "best_buy") {
    return params.correctLabel as string;
  }
  if (task === "simple_scale") {
    return RC.scaleValue(params.value as number, new Rational(params.factorNum as number, params.factorDen as number));
  }
  throw new Error(task);
}

// --------------------------------------------------------------------------- //
// Exactness gate — deterministic-redraw acceptance test.
// --------------------------------------------------------------------------- //
function _acceptable(task: string, params: Json): boolean {
  const sol = _solve(task, params);
  if (task === "share_two_part" || task === "share_three_part") {
    return sol !== null;
  }
  if (task === "missing_part") {
    return sol !== null && (sol as number) > 0;
  }
  if (task === "inverse_proportion") {
    return sol !== null && (sol as number) > 0;
  }
  if (task === "best_buy") {
    const rates = (params.options as Json[]).map((o) => new Rational(o.totalAmount as number, o.packSize as number));
    const mn = _minRational(rates);
    return rates.filter((r) => r.equals(mn)).length === 1;
  }
  if (task === "ratio_to_fraction") {
    const f = sol as Rational;
    // 0 < sol < 1 (proper fraction)
    return f.num > 0 && f.num < f.den;
  }
  if (task === "direct_proportion" || task === "unit_rate" || task === "simple_scale") {
    return sol instanceof Rational && sol.num > 0;
  }
  return true;
}

// --------------------------------------------------------------------------- //
// Answer encoding (owner D).
// --------------------------------------------------------------------------- //
function _shareLabelsCells(params: Json): [string, number][] {
  const shares = RC.share(params.total as number, params.parts as number[]) as number[];
  return (params.labels as string[]).map((lab, i) => [lab, shares[i] as number] as [string, number]);
}

function _encodeAnswer(task: string, params: Json): Json {
  const kind = ANSWER_KIND[task];
  const sol = _solve(task, params);
  if (kind === "ratio") {
    return RC.ratioAnswer(sol as number[]);
  }
  if (kind === "rational") {
    return RC.rationalAnswer(sol as Rational);
  }
  if (kind === "integer") {
    return RC.integerAnswer(sol as number);
  }
  if (kind === "table") {
    return RC.tableAnswer(_shareLabelsCells(params));
  }
  if (kind === "mc") {
    return RC.mcAnswer(sol as string);
  }
  throw new Error(kind);
}

// =========================================================================== //
// RENDERER (owner J) — family-local; tx-style class names prefixed `rt-`.
// =========================================================================== //
const BAR_W = 1000;
const BAR_H = 300;
const NL_W = 1000;
const NL_H = 260;
const TBL_W = 1000;
const TBL_H = 300;

const STYLE =
  ".rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}" +
  ".rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}" +
  ".rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}" +
  ".rt-divider{stroke:#111;stroke-width:1.5}" +
  ".rt-axis{stroke:#111;stroke-width:2.5;fill:none}" +
  ".rt-tick{stroke:#111;stroke-width:2}" +
  ".rt-given-pt{fill:#111;stroke:#111;stroke-width:2}" +
  ".rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}" +
  ".rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}" +
  ".rt-table-line{stroke:#111;stroke-width:2;fill:none}" +
  ".rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}" +
  "text{font-family:sans-serif;font-size:26px;fill:#111}" +
  ".rt-ticklbl{font-size:20px;fill:#333}" +
  ".rt-lbl{font-size:26px;fill:#111}" +
  ".rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}";

function _svgHeader(viewW: number, viewH: number, acc: Json): string[] {
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${viewW} ${viewH}" role="img" aria-label="${_esc(acc.alt)}">`,
    `<title>${_esc(acc.title)}</title><desc>${_esc(acc.desc)}</desc>`,
    `<style>${STYLE}</style>`,
  ];
}

// --- bar models ------------------------------------------------------------- //
function _barSegments(task: string, params: Json): [number[], boolean[], string[]] {
  if (task === "ratio_to_fraction") {
    const a = (params.parts as number[])[0] as number;
    const b = (params.parts as number[])[1] as number;
    const weights = [a, b];
    const labels = [
      `${(params.labels as string[])[0]} (${a})`,
      `${(params.labels as string[])[1]} (${b})`,
    ];
    const given = [true, true];
    return [weights, given, labels];
  }
  if (task === "fraction_to_ratio") {
    const num = params.num as number;
    const den = params.den as number;
    const weights = [num, den - num];
    const labels = [`named part (${num})`, `rest (${den - num})`];
    return [weights, [true, true], labels];
  }
  if (task === "share_two_part" || task === "share_three_part") {
    const parts = params.parts as number[];
    const labels = (params.labels as string[]).map((lab, i) => `${lab} (${parts[i]} parts)`);
    return [parts.slice(), parts.map(() => false), labels];
  }
  if (task === "missing_part") {
    const parts = params.parts as number[];
    const ki = params.knownIndex as number;
    const mi = params.missingIndex as number;
    const given = [false, false];
    given[ki] = true;
    const labels = ["", ""];
    labels[ki] = `${(params.labels as string[])[ki]} = ${params.knownValue}`;
    labels[mi] = `${(params.labels as string[])[mi]} = ?`;
    return [parts.slice(), given, labels];
  }
  throw new Error(task);
}

function _renderBar(task: string, params: Json, answerKey: boolean, acc: Json): string {
  const [weights, given, labels] = _barSegments(task, params);
  const totalW = weights.reduce((s, w) => s + w, 0);
  const x0 = 80;
  const x1 = 920;
  const band = x1 - x0;
  const y0 = 110;
  const h = 90;
  const out = _svgHeader(BAR_W, BAR_H, acc);
  let accW = 0;
  const edges = [x0];
  for (const w of weights) {
    accW += w;
    edges.push(x0 + Math.floor((band * accW) / totalW));
  }
  out.push('<g class="rt-base">');
  out.push(
    `<text class="rt-lbl" x="${Math.floor(BAR_W / 2)}" y="56" text-anchor="middle">${_esc(_barCaption(task, params))}</text>`,
  );
  for (let i = 0; i < weights.length; i++) {
    const lx = edges[i] as number;
    const rx = edges[i + 1] as number;
    const cls = given[i] ? "rt-bar-given" : "rt-bar-unknown";
    out.push(`<rect class="${cls}" data-cell="${i}" x="${lx}" y="${y0}" width="${rx - lx}" height="${h}"/>`);
    const cx = Math.floor((lx + rx) / 2);
    if (labels[i]) {
      out.push(`<text class="rt-lbl" x="${cx}" y="${y0 + h + 36}" text-anchor="middle">${_esc(labels[i] as string)}</text>`);
    }
  }
  out.push(`<rect class="rt-bar-frame" x="${x0}" y="${y0}" width="${band}" height="${h}"/>`);
  out.push("</g>");
  const unknownCells: [number, number][] = [];
  for (let i = 0; i < weights.length; i++) {
    if (!given[i]) {
      unknownCells.push([i, Math.floor(((edges[i] as number) + (edges[i + 1] as number)) / 2)]);
    }
  }
  const answerOnly = task === "ratio_to_fraction" || task === "fraction_to_ratio";
  const ay = y0 + h + 78;
  if (answerKey) {
    out.push('<g class="rt-overlay">');
    for (const [i, cx] of unknownCells) {
      const val = _barCellValue(task, params, i);
      if (val !== null) {
        out.push(`<text class="rt-unknown-lbl" x="${cx}" y="${y0 + h - 28}" text-anchor="middle">${val}</text>`);
      }
    }
    if (answerOnly) {
      const sol = _solve(task, params);
      const disp = sol instanceof Rational ? _dispRat(sol) : RC.formatRatio(sol as number[]);
      out.push(
        `<text class="rt-unknown-lbl" x="${Math.floor(BAR_W / 2)}" y="${ay}" text-anchor="middle">Answer: ${_esc(disp)}</text>`,
      );
    }
    out.push("</g>");
  } else {
    out.push('<g class="rt-student">');
    for (const [i, cx] of unknownCells) {
      void i;
      out.push(`<text class="rt-unknown-lbl" x="${cx}" y="${y0 + h - 28}" text-anchor="middle">?</text>`);
    }
    if (answerOnly) {
      out.push(`<text class="rt-unknown-lbl" x="${Math.floor(BAR_W / 2)}" y="${ay}" text-anchor="middle">Answer: ?</text>`);
    }
    out.push("</g>");
  }
  out.push("</svg>");
  return out.join("\n");
}

function _barCellValue(task: string, params: Json, i: number): number | null {
  if (task === "share_two_part" || task === "share_three_part") {
    const shares = RC.share(params.total as number, params.parts as number[]) as number[];
    return shares[i] as number;
  }
  if (task === "missing_part") {
    if (i === (params.missingIndex as number)) {
      return _solve(task, params) as number;
    }
    return null;
  }
  return null;
}

function _barCaption(task: string, params: Json): string {
  if (task === "ratio_to_fraction") {
    return `Bar model: the whole split as ${RC.formatRatio(params.parts as number[])}`;
  }
  if (task === "fraction_to_ratio") {
    return `Bar model: ${params.num} of ${params.den} equal parts shaded`;
  }
  if (task === "share_two_part" || task === "share_three_part") {
    return `Bar model: ${params.total} ${params.unit} shared in ${RC.formatRatio(params.parts as number[])}`;
  }
  if (task === "missing_part") {
    return `Bar model: parts in the ratio ${RC.formatRatio(params.parts as number[])}`;
  }
  return "Bar model";
}

// --- double number lines ---------------------------------------------------- //
type Rung = [Json, Json, boolean];

function _nlPairs(task: string, params: Json): [string, string, Rung[]] {
  if (task === "direct_proportion") {
    const q = params.quantity as number;
    const total = params.total as number;
    const target = params.target as number;
    const one = new Rational(total, q);
    return [
      params.perLabel as string,
      params.givenLabel as string,
      [
        [q, total, false],
        [target, one.mul(Rational.from(target)), true],
      ],
    ];
  }
  if (task === "unit_rate") {
    const q = params.quantity as number;
    const total = params.total as number;
    const one = new Rational(total, q);
    return [
      params.perLabel as string,
      params.amountLabel as string,
      [
        [q, total, false],
        [1, one, true],
      ],
    ];
  }
  if (task === "simple_scale") {
    const v = params.value as number;
    const fnum = params.factorNum as number;
    const fden = params.factorDen as number;
    const scaled = Rational.from(v).mul(new Rational(fnum, fden));
    return [
      params.srcUnit as string,
      params.dstUnit as string,
      [
        [fden, fnum, false],
        [v, scaled, true],
      ],
    ];
  }
  throw new Error(task);
}

function _renderNumberline(task: string, params: Json, answerKey: boolean, acc: Json): string {
  const [topLbl, botLbl, rungs] = _nlPairs(task, params);
  const x0 = 120;
  const x1 = 880;
  const yTop = 110;
  const yBot = 200;
  const out = _svgHeader(NL_W, NL_H, acc);
  out.push('<g class="rt-base">');
  out.push(`<text class="rt-lbl" x="${Math.floor(NL_W / 2)}" y="52" text-anchor="middle">${_esc("Double number line")}</text>`);
  out.push(`<line class="rt-axis" x1="${x0}" y1="${yTop}" x2="${x1}" y2="${yTop}"/>`);
  out.push(`<line class="rt-axis" x1="${x0}" y1="${yBot}" x2="${x1}" y2="${yBot}"/>`);
  out.push(`<text class="rt-lbl" x="${x0 - 16}" y="${yTop + 8}" text-anchor="end">${_esc(topLbl)}</text>`);
  out.push(`<text class="rt-lbl" x="${x0 - 16}" y="${yBot + 8}" text-anchor="end">${_esc(botLbl)}</text>`);
  const n = rungs.length;
  const xs: number[] = [];
  for (let i = 0; i < n; i++) {
    xs.push(x0 + Math.floor(((x1 - x0) * (i + 1)) / (n + 1)));
  }
  for (let i = 0; i < rungs.length; i++) {
    const [tv, bv, unknown] = rungs[i] as Rung;
    const px = xs[i] as number;
    out.push(`<line class="rt-rung" x1="${px}" y1="${yTop}" x2="${px}" y2="${yBot}"/>`);
    out.push(`<circle class="rt-given-pt" cx="${px}" cy="${yTop}" r="6"/>`);
    out.push(`<text class="rt-ticklbl" x="${px}" y="${yTop - 14}" text-anchor="middle">${_esc(_fmtVal(tv))}</text>`);
    if (unknown) {
      out.push(`<circle class="rt-unknown-pt" cx="${px}" cy="${yBot}" r="7"/>`);
    } else {
      out.push(`<circle class="rt-given-pt" cx="${px}" cy="${yBot}" r="6"/>`);
      out.push(`<text class="rt-ticklbl" x="${px}" y="${yBot + 36}" text-anchor="middle">${_esc(_fmtVal(bv))}</text>`);
    }
  }
  out.push("</g>");
  if (answerKey) {
    out.push('<g class="rt-overlay">');
    for (let i = 0; i < rungs.length; i++) {
      const [, bv, unknown] = rungs[i] as Rung;
      if (unknown) {
        out.push(`<text class="rt-unknown-lbl" x="${xs[i]}" y="${yBot + 36}" text-anchor="middle">${_esc(_fmtVal(bv))}</text>`);
      }
    }
    out.push("</g>");
  } else {
    out.push('<g class="rt-student">');
    for (let i = 0; i < rungs.length; i++) {
      const [, , unknown] = rungs[i] as Rung;
      if (unknown) {
        out.push(`<text class="rt-unknown-lbl" x="${xs[i]}" y="${yBot + 36}" text-anchor="middle">?</text>`);
      }
    }
    out.push("</g>");
  }
  out.push("</svg>");
  return out.join("\n");
}

function _fmtVal(v: Json): string {
  if (v instanceof Rational) {
    return _dispRat(v);
  }
  return String(v);
}

// --- proportional best-buy table -------------------------------------------- //
function _capitalize(s: string): string {
  // Python str.capitalize(): first char upper, rest lower.
  if (s.length === 0) return s;
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
}

function _renderTable(task: string, params: Json, answerKey: boolean, acc: Json): string {
  void task;
  const options = params.options as Json[];
  const n = options.length;
  const out = _svgHeader(TBL_W, TBL_H, acc);
  const x0 = 80;
  const x1 = 920;
  const colW = Math.floor((x1 - x0) / (n + 1));
  const y0 = 80;
  const rowH = 56;
  const rows = [
    "Option",
    `Total ${params.unit}`,
    `${_capitalize(params.pack as string)} size`,
    `Unit rate (${params.unit} per item)`,
  ];
  const nRows = rows.length;
  out.push('<g class="rt-base">');
  out.push(`<text class="rt-lbl" x="${Math.floor(TBL_W / 2)}" y="48" text-anchor="middle">${_esc("Compare the options by unit rate")}</text>`);
  for (let r = 0; r < nRows + 1; r++) {
    const y = y0 + r * rowH;
    out.push(`<line class="rt-table-line" x1="${x0}" y1="${y}" x2="${x0 + colW * (n + 1)}" y2="${y}"/>`);
  }
  for (let c = 0; c < n + 2; c++) {
    const x = x0 + c * colW;
    out.push(`<line class="rt-table-line" x1="${x}" y1="${y0}" x2="${x}" y2="${y0 + rowH * nRows}"/>`);
  }
  for (let r = 0; r < rows.length; r++) {
    const ty = y0 + r * rowH + 36;
    out.push(`<text class="rt-ticklbl" x="${x0 + 12}" y="${ty}" text-anchor="start">${_esc(rows[r] as string)}</text>`);
  }
  for (let i = 0; i < options.length; i++) {
    const o = options[i];
    const cx = x0 + colW * (i + 1) + Math.floor(colW / 2);
    out.push(`<text class="rt-lbl" x="${cx}" y="${y0 + 36}" text-anchor="middle">${_esc(o.label as string)}</text>`);
    out.push(`<text class="rt-lbl" x="${cx}" y="${y0 + rowH + 36}" text-anchor="middle">${o.totalAmount}</text>`);
    out.push(`<text class="rt-lbl" x="${cx}" y="${y0 + 2 * rowH + 36}" text-anchor="middle">${o.packSize}</text>`);
  }
  out.push("</g>");
  const ry = y0 + 3 * rowH + 36;
  if (answerKey) {
    out.push('<g class="rt-overlay">');
    for (let i = 0; i < options.length; i++) {
      const o = options[i];
      const cx = x0 + colW * (i + 1) + Math.floor(colW / 2);
      const rate = new Rational(o.totalAmount as number, o.packSize as number);
      const mark = o.label === (params.correctLabel as string) ? " ✓" : "";
      out.push(`<text class="rt-unknown-lbl" x="${cx}" y="${ry}" text-anchor="middle">${_esc(_dispRat(rate) + mark)}</text>`);
    }
    out.push("</g>");
  } else {
    out.push('<g class="rt-student">');
    for (let i = 0; i < options.length; i++) {
      const o = options[i];
      const cx = x0 + colW * (i + 1) + Math.floor(colW / 2);
      out.push(`<text class="rt-unknown-lbl" x="${cx}" y="${ry}" text-anchor="middle">?</text>`);
    }
    out.push("</g>");
  }
  out.push("</svg>");
  return out.join("\n");
}

function render(task: string, params: Json, answerKey: boolean, acc: Json): string | null {
  const fig = FIGURE_KIND[task];
  if (fig === null || fig === undefined) {
    return null;
  }
  if (fig === "bar") {
    return _renderBar(task, params, answerKey, acc);
  }
  if (fig === "numberline") {
    return _renderNumberline(task, params, answerKey, acc);
  }
  if (fig === "table") {
    return _renderTable(task, params, answerKey, acc);
  }
  throw new Error(fig);
}

// --------------------------------------------------------------------------- //
// Difficulty.
// --------------------------------------------------------------------------- //
function _isHighComplexity(task: string, params: Json): boolean {
  if (task === "simplify" || task === "write_from_quantities") {
    const parts = (params.parts as number[]) || (params.quantities as number[]);
    return parts.length === 3;
  }
  if (task === "ratio_to_fraction" || task === "fraction_to_ratio") {
    if (task === "ratio_to_fraction") {
      return ((params.parts as number[])[0] as number) + ((params.parts as number[])[1] as number) >= 9;
    }
    return RC.gcdList([params.num as number, (params.den as number) - (params.num as number)]) > 1;
  }
  if (task === "share_two_part" || task === "share_three_part") {
    return (params.total as number) >= 40;
  }
  if (task === "missing_part") {
    return (params.knownValue as number) >= 30;
  }
  if (task === "direct_proportion") {
    return (_solve(task, params) as Rational).den > 1;
  }
  if (task === "inverse_proportion") {
    return (params.q1 as number) * (params.v1 as number) >= 60;
  }
  if (task === "unit_rate") {
    return (_solve(task, params) as Rational).den > 1;
  }
  if (task === "best_buy") {
    return (params.options as Json[]).length === 3;
  }
  if (task === "simple_scale") {
    return (_solve(task, params) as Rational).den > 1;
  }
  return false;
}

function _difficulty(task: string, params: Json): Json {
  const [lo, hi] = TASK_BANDS[task] as [number, number];
  const high = _isHighComplexity(task, params);
  const band = high ? hi : lo;

  const sol = _solve(task, params);
  const frac = sol instanceof Rational && sol.den > 1;
  const stepsByTask: Record<string, number> = {
    simplify: 0.3,
    write_from_quantities: 0.35,
    ratio_to_fraction: 0.45,
    fraction_to_ratio: 0.45,
    share_two_part: 0.5,
    share_three_part: 0.6,
    missing_part: 0.5,
    direct_proportion: 0.55,
    inverse_proportion: 0.7,
    unit_rate: 0.45,
    best_buy: 0.7,
    simple_scale: 0.5,
  };
  const abstractionByTask: Record<string, number> = {
    simplify: 0.25,
    write_from_quantities: 0.3,
    ratio_to_fraction: 0.5,
    fraction_to_ratio: 0.5,
    share_two_part: 0.4,
    share_three_part: 0.5,
    missing_part: 0.45,
    direct_proportion: 0.5,
    inverse_proportion: 0.65,
    unit_rate: 0.4,
    best_buy: 0.6,
    simple_scale: 0.5,
  };
  const rs = (stepsByTask[task] as number) + (high ? 0.1 : 0.0);
  const ab = (abstractionByTask[task] as number) + (high ? 0.1 : 0.0);
  const nc = 0.3 + (frac ? 0.25 : 0.0) + (high ? 0.1 : 0.0);
  const axes = {
    numericalComplexity: round3(clamp01(nc)),
    // ratio is ALWAYS exact; mirror ratio.py: route through round3 so it serializes as int 0.
    exactVsApproximate: round3(clamp01(0.0)),
    reasoningSteps: round3(clamp01(rs)),
    abstraction: round3(clamp01(ab)),
  };
  return { overallBand: band, axes };
}

// --------------------------------------------------------------------------- //
// Accessibility.
// --------------------------------------------------------------------------- //
function _dataTable(task: string, params: Json, answerKey: boolean): Json {
  if (task === "share_two_part" || task === "share_three_part") {
    let rows: string[][] = (params.labels as string[]).map((lab, i) => [lab, `${(params.parts as number[])[i]} parts`]);
    if (answerKey) {
      const shares = RC.share(params.total as number, params.parts as number[]) as number[];
      rows = (params.labels as string[]).map((lab, i) => [
        lab,
        `${(params.parts as number[])[i]} parts -> ${shares[i]} ${params.unit}`,
      ]);
    }
    return { columns: ["Share", "Ratio part"], rows };
  }
  if (task === "missing_part") {
    const ki = params.knownIndex as number;
    const mi = params.missingIndex as number;
    const rows: string[][] = [
      ["", ""],
      ["", ""],
    ];
    rows[ki] = [(params.labels as string[])[ki] as string, `${(params.parts as number[])[ki]} parts = ${params.knownValue}`];
    rows[mi] = [
      (params.labels as string[])[mi] as string,
      `${(params.parts as number[])[mi]} parts = ` + (answerKey ? String(_solve(task, params)) : "?"),
    ];
    return { columns: ["Part", "Value"], rows };
  }
  if (task === "best_buy") {
    const cols = ["Option", `Total ${params.unit}`, "Pack size"];
    let rows: string[][] = (params.options as Json[]).map((o) => [
      o.label as string,
      String(o.totalAmount),
      String(o.packSize),
    ]);
    if (answerKey) {
      cols.push("Unit rate");
      rows = (params.options as Json[]).map((o) => [
        o.label as string,
        String(o.totalAmount),
        String(o.packSize),
        _dispRat(new Rational(o.totalAmount as number, o.packSize as number)) +
          (o.label === (params.correctLabel as string) ? " (best)" : ""),
      ]);
    }
    return { columns: cols, rows };
  }
  if (task === "direct_proportion" || task === "unit_rate" || task === "simple_scale") {
    const [topLbl, botLbl, rungs] = _nlPairs(task, params);
    const rows: string[][] = [];
    for (const [tv, bv, unknown] of rungs) {
      const b = unknown && !answerKey ? "?" : _fmtVal(bv);
      rows.push([_fmtVal(tv), b]);
    }
    return { columns: [topLbl, botLbl], rows };
  }
  if (task === "ratio_to_fraction" || task === "fraction_to_ratio") {
    const [weights, , labels] = _barSegments(task, params);
    return { columns: ["Part", "Size"], rows: labels.map((lab, i) => [lab, String(weights[i])]) };
  }
  return { columns: ["Quantity", "Value"], rows: [] };
}

function _accessibility(task: string, params: Json, answerKey: boolean): Json {
  const fig = FIGURE_KIND[task];
  const instr = _instruction(task, params);
  let base: string;
  let title: string;
  if (fig === "bar") {
    base =
      task === "ratio_to_fraction" ||
      task === "share_two_part" ||
      task === "share_three_part" ||
      task === "missing_part"
        ? `A bar model for the ratio ${RC.formatRatio((params.parts as number[]) ?? [1, 1])}.`
        : `A bar model split into ${params.den ?? 0} equal parts.`;
    title = "Bar model";
  } else if (fig === "numberline") {
    base = "A double number line aligning the two proportional quantities.";
    title = "Double number line";
  } else if (fig === "table") {
    base = "A comparison table of the options' total amount and pack size.";
    title = "Best-buy comparison table";
  } else {
    base = "No figure; the data is given in the prompt.";
    title = "Ratio question";
  }
  let alt: string;
  let desc: string;
  if (answerKey) {
    alt = `Answer key. ${base} The solved quantities are shown.`;
    desc = `${base} The solution overlay reveals the answer to: ${instr}`;
  } else {
    alt = `${base} ${instr}`;
    desc = `${base} Unknown quantities are marked with a question mark. ${instr}`;
  }
  return {
    title,
    alt,
    desc,
    spokenMath: alt,
    longDescription: `${title}. ${desc}`,
  };
}

// --------------------------------------------------------------------------- //
// Prompt + solution
// --------------------------------------------------------------------------- //
function _instruction(task: string, params: Json): string {
  if (task === "simplify") {
    return `Write the ratio ${RC.formatRatio(params.parts as number[])} in its simplest form.`;
  }
  if (task === "write_from_quantities") {
    const qs = (params.quantities as number[])
      .map((v, i) => `${v} ${(params.labels as string[])[i]}`)
      .join(", ");
    return (
      `In a ${(params.title as string).toLowerCase()} there are ${qs}. ` +
      `Write the ratio of ${(params.labels as string[]).join(" to ")} in its simplest form.`
    );
  }
  if (task === "ratio_to_fraction") {
    const a = (params.parts as number[])[0] as number;
    const b = (params.parts as number[])[1] as number;
    const named = (params.labels as string[])[params.partIndex as number];
    return (
      `The ${(params.title as string).toLowerCase()} mixes ${(params.labels as string[])[0]} and ${(params.labels as string[])[1]} ` +
      `in the ratio ${a}:${b}. What fraction of the whole is ${named}? ` +
      `Give your answer as a fraction in its simplest form.`
    );
  }
  if (task === "fraction_to_ratio") {
    return (
      `In a group, ${params.num}/${params.den} are one type and the rest are another. ` +
      `Write the ratio of the first type to the rest in its simplest form.`
    );
  }
  if (task === "share_two_part" || task === "share_three_part") {
    return (
      `Share ${params.total} ${params.unit} between ${(params.labels as string[]).join(", ")} ` +
      `in the ratio ${RC.formatRatio(params.parts as number[])}. Give each share.`
    );
  }
  if (task === "missing_part") {
    const ki = params.knownIndex as number;
    const mi = params.missingIndex as number;
    return (
      `${(params.labels as string[])[ki]} and ${(params.labels as string[])[mi]} share an amount in the ratio ` +
      `${RC.formatRatio(params.parts as number[])}. ${(params.labels as string[])[ki]} gets ${params.knownValue} ` +
      `${params.unit}. How many ${params.unit} does ${(params.labels as string[])[mi]} get?`
    );
  }
  if (task === "direct_proportion") {
    return (
      `${params.quantity} ${params.perLabel} hold ${params.total} ${params.givenLabel}. ` +
      `How many ${params.givenLabel} are in ${params.target} ${params.perLabel}? ` +
      `Give an exact value.`
    );
  }
  if (task === "inverse_proportion") {
    return (
      `${params.q1} ${params.agent} take ${params.v1} ${params.unit} ${params.tail}. ` +
      `How many ${params.unit} would ${params.q2} ${params.agent} take ${params.tail}?`
    );
  }
  if (task === "unit_rate") {
    const perLabel = params.perLabel as string;
    const singular = perLabel.endsWith("s") ? perLabel.slice(0, -1) : perLabel;
    return (
      `${params.quantity} ${params.perLabel} hold ${params.total} ${params.amountLabel}. ` +
      `How many ${params.amountLabel} per ${singular}? ` +
      `Give an exact value.`
    );
  }
  if (task === "best_buy") {
    const opts = (params.options as Json[])
      .map(
        (o) =>
          `option ${o.label} has ${o.totalAmount} ${params.unit} in a ${params.pack} of ${o.packSize}`,
      )
      .join("; ");
    return (
      `You can buy ${params.product}: ${opts}. Which option is the best value ` +
      `(the lowest amount per item)? Choose the best option.`
    );
  }
  if (task === "simple_scale") {
    return (
      `On a ${params.scaleKind}, ${params.factorDen} ${params.srcUnit} represent ` +
      `${params.factorNum} ${params.dstUnit}. What do ${params.value} ${params.srcUnit} ` +
      `represent? Give an exact value.`
    );
  }
  throw new Error(task);
}

function _prompt(task: string, params: Json): Json {
  const blocks: Json[] = [];
  if (FIGURE_KIND[task] !== null && FIGURE_KIND[task] !== undefined) {
    blocks.push({ kind: "media-ref", ref: "fig-1" });
  }
  blocks.push({ kind: "text", text: _instruction(task, params) });
  return { blocks, instruction: _instruction(task, params) };
}

function _solution(task: string, params: Json): Json {
  const steps: Json[] = [];
  const step = (t: string, r: string): void => {
    steps.push({ number: steps.length + 1, transformation: t, intermediateResult: r });
  };

  const sol = _solve(task, params);
  if (task === "simplify" || task === "write_from_quantities") {
    const src = (params.parts as number[]) || (params.quantities as number[]);
    const g = RC.gcdList(src);
    step("Find the greatest common divisor of the parts", `gcd = ${g}`);
    step("Divide every part by the gcd, keeping the order", RC.formatRatio(sol as number[]));
  } else if (task === "ratio_to_fraction") {
    const a = (params.parts as number[])[0] as number;
    const b = (params.parts as number[])[1] as number;
    const part = (params.parts as number[])[params.partIndex as number] as number;
    step("Add the parts to find the total number of parts", `${a} + ${b} = ${a + b}`);
    step("Write the named part over the total", `${part}/${a + b} = ${_dispRat(sol as Rational)}`);
  } else if (task === "fraction_to_ratio") {
    const num = params.num as number;
    const den = params.den as number;
    step("Find the remaining part of the whole", `${den} - ${num} = ${den - num}`);
    step("Write the part-to-rest ratio and simplify", RC.formatRatio(sol as number[]));
  } else if (task === "share_two_part" || task === "share_three_part") {
    const parts = params.parts as number[];
    const s = parts.reduce((acc, p) => acc + p, 0);
    const one = Math.floor((params.total as number) / s);
    step("Add the parts to find the total number of parts", `${parts.map((p) => String(p)).join(" + ")} = ${s}`);
    step("Find the value of one part", `${params.total} ÷ ${s} = ${one}`);
    step(
      "Multiply to give each share",
      _shareLabelsCells(params)
        .map(([lab, v]) => `${lab}=${v}`)
        .join(", "),
    );
  } else if (task === "missing_part") {
    const ki = params.knownIndex as number;
    const mi = params.missingIndex as number;
    const one = Math.floor((params.knownValue as number) / ((params.parts as number[])[ki] as number));
    step(
      "Find the value of one part from the known share",
      `${params.knownValue} ÷ ${(params.parts as number[])[ki]} = ${one}`,
    );
    step("Multiply by the missing part's ratio value", `${one} × ${(params.parts as number[])[mi]} = ${sol}`);
  } else if (task === "direct_proportion") {
    const q = params.quantity as number;
    const total = params.total as number;
    const target = params.target as number;
    const one = new Rational(total, q);
    step("Find the value of one unit", `${total} ÷ ${q} = ${_dispRat(one)}`);
    step("Multiply by the required quantity", `${_dispRat(one)} × ${target} = ${_dispRat(sol as Rational)}`);
  } else if (task === "inverse_proportion") {
    const q1 = params.q1 as number;
    const v1 = params.v1 as number;
    const q2 = params.q2 as number;
    step("Use the product invariant (more means less)", `${q1} × ${v1} = ${q1 * v1}`);
    step("Divide the product by the new quantity", `${q1 * v1} ÷ ${q2} = ${sol}`);
  } else if (task === "unit_rate") {
    step("Divide the total by the number of units", `${params.total} ÷ ${params.quantity} = ${_dispRat(sol as Rational)}`);
  } else if (task === "best_buy") {
    for (const o of params.options as Json[]) {
      const rate = new Rational(o.totalAmount as number, o.packSize as number);
      step(
        `Unit rate of option ${o.label}`,
        `${o.totalAmount} ÷ ${o.packSize} = ${_dispRat(rate)} ${params.unit} per item`,
      );
    }
    const rates: Record<string, Rational> = {};
    for (const o of params.options as Json[]) {
      rates[o.label as string] = new Rational(o.totalAmount as number, o.packSize as number);
    }
    step(
      "Compare the unit rates and choose the strict minimum",
      `lowest is ${_dispRat(rates[params.correctLabel as string] as Rational)} -> option ${params.correctLabel}`,
    );
  } else if (task === "simple_scale") {
    const v = params.value as number;
    const fnum = params.factorNum as number;
    const fden = params.factorDen as number;
    step("Find the scale factor", `${fnum}/${fden}`);
    step("Multiply the value by the scale factor", `${v} × ${fnum}/${fden} = ${_dispRat(sol as Rational)}`);
  }
  return { steps };
}

// --------------------------------------------------------------------------- //
// MC option assembly (owner C).
// --------------------------------------------------------------------------- //
function _answerDisplayValue(task: string, value: Json): [Json, string] {
  const kind = ANSWER_KIND[task];
  if (kind === "ratio") {
    return [{ parts: [...(value as number[])] }, RC.formatRatio(value as number[])];
  }
  if (kind === "rational" || kind === "integer") {
    const f = value instanceof Rational ? value : Rational.from(value as number);
    if (f.den === 1) {
      return [f.num, String(f.num)];
    }
    return [{ num: f.num, den: f.den }, _dispRat(f)];
  }
  if (kind === "mc") {
    return [value, value];
  }
  throw new Error(kind);
}

function _mcDistractors(task: string, params: Json): Json[] | null {
  const correct = _solve(task, params);
  let correctKey: string;
  if (task === "best_buy") {
    correctKey = correct as string;
  } else {
    const [ce] = _answerDisplayValue(task, correct);
    correctKey = canonicalStringify(ce);
  }
  const out: Json[] = [];
  const seen = new Set<string>([correctKey]);
  for (const d of RM.diagnosticsFor(task, params)) {
    let enc: Json;
    let disp: string;
    let key: string;
    if (task === "best_buy") {
      const val = d.predictedResponse as string;
      key = val;
      enc = val;
      disp = val;
    } else {
      const pc = d.predictedCanonical;
      if ("parts" in pc) {
        enc = { parts: pc.parts };
        disp = RC.formatRatio(pc.parts as number[]);
      } else {
        const f = new Rational(pc.num as number, pc.den as number);
        [enc, disp] = _answerDisplayValue(task, f);
      }
      key = canonicalStringify(enc);
    }
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    out.push({
      value: enc,
      display: disp,
      misconceptionId: d.misconceptionId,
      rationale: d.observableError,
    });
    if (out.length === 3) {
      break;
    }
  }
  return out.length === 3 ? out : null;
}

// --------------------------------------------------------------------------- //
// Public generate()
// --------------------------------------------------------------------------- //
function _resolveInteraction(task: string, config: Json): string {
  const requested = config.interactionType;
  if (requested === undefined || requested === null) {
    return MC_ONLY_TASKS.includes(task) ? "multiple-choice" : "free-response";
  }
  if (requested !== "free-response" && requested !== "multiple-choice") {
    throw new InteractionNotSupported(`unsupported interaction ${JSON.stringify(requested)} for ${JSON.stringify(task)}`);
  }
  if (!supportedInteractions(task).includes(requested)) {
    throw new InteractionNotSupported(
      `task ${JSON.stringify(task)} does not support ${JSON.stringify(requested)} (supported: ${pyTuple(supportedInteractions(task))})`,
    );
  }
  return requested;
}

function pyTuple(items: string[]): string {
  // Mirror Python tuple repr for the error message: ('a', 'b') or ('a',).
  const inner = items.map((s) => `'${s}'`).join(", ");
  return items.length === 1 ? `(${inner},)` : `(${inner})`;
}

export function generate(seed: number, config?: Json): Json {
  config = config || {};
  const explicit = config.task;
  if (explicit !== undefined && explicit !== null && !(explicit in OBJECTIVE_BY_TASK)) {
    throw new Error(`unknown task ${JSON.stringify(explicit)}`);
  }

  const rng = new Mulberry32(seed);
  let task: string;
  if (explicit === undefined || explicit === null) {
    const requested = config.interactionType;
    const pool = requested === "multiple-choice" ? [...MC_ELIGIBLE_TASKS] : [...RATIO_TASKS];
    task = pool[_n(rng, pool.length)] as string;
  } else {
    task = explicit as string;
  }

  const interaction = _resolveInteraction(task, config);
  const mc = interaction === "multiple-choice";

  let params: Json = {};
  let distractors: Json[] | null = null;
  let ok = false;
  for (let attempt = 0; attempt < MAX_PARAM_ATTEMPTS; attempt++) {
    const drawn = _DRAW[task]!(rng);
    if (drawn === null) {
      continue;
    }
    if (!_acceptable(task, drawn)) {
      continue;
    }
    if (mc && task !== "best_buy") {
      const ds = _mcDistractors(task, drawn);
      if (ds === null) {
        continue;
      }
      distractors = ds;
    }
    params = drawn;
    ok = true;
    break;
  }
  if (!ok) {
    throw new Error(`could not draw acceptable ratio params for ${task} seed=${seed}`);
  }

  const answer = _encodeAnswer(task, params);
  const acc = _accessibility(task, params, false);
  const accKey = _accessibility(task, params, true);
  const itemId = `ITEM-RATIO-${task}-${seed}`;

  const item: Json = {
    itemId,
    schemaVersion: "1.0.0",
    objectiveIds: [OBJECTIVE_BY_TASK[task]],
    generatorId: GENERATOR_ID,
    generatorVersion: GENERATOR_VERSION,
    seed,
    interactionType: interaction,
    prompt: _prompt(task, params),
    answer,
    solution: _solution(task, params),
    calculatorPolicy: CALCULATOR_POLICY,
    provenance: {
      origin: "generated",
      rightsStatus: "academy-owned",
      originalityNote: "Original parameterized item; the figure is generated from the same params.",
    },
    lifecycle: { state: "generated" },
    accessibility: {
      spokenMath: acc.spokenMath,
      altText: acc.alt,
      longDescription: acc.longDescription,
      nonColorIndicators: true,
    },
    difficulty: _difficulty(task, params),
    params: _publicParams(task, params),
  };

  const studentSvg = render(task, params, false, acc);
  if (studentSvg !== null) {
    const keySvg = render(task, params, true, accKey);
    item.media = [
      {
        id: "fig-1",
        kind: "svg",
        svg: studentSvg,
        spec: {
          answerKeySvg: keySvg,
          figureKind: FIGURE_KIND[task],
          answerKeyAltText: accKey.alt,
          answerKeyLongDescription: accKey.longDescription,
          answerKeyDataTableFallback: _dataTable(task, params, true),
        },
        toScale: true,
        altText: acc.alt,
        longDescription: acc.longDescription,
        dataTableFallback: _dataTable(task, params, false),
      },
    ];
  }

  if (mc && task === "best_buy") {
    const diags: Record<string, Json> = {};
    for (const d of RM.diagnosticsFor(task, params)) {
      diags[d.predictedResponse as string] = d;
    }
    item.options = [];
    for (const o of params.options as Json[]) {
      const correct = o.label === (params.correctLabel as string);
      const opt: Json = {
        label: o.label,
        value: o.label,
        display: `${o.totalAmount} ${params.unit} per ${params.pack} of ${o.packSize}`,
        correct,
      };
      if (!correct && o.label in diags) {
        opt.misconceptionId = diags[o.label as string].misconceptionId;
      }
      item.options.push(opt);
    }
  } else if (mc) {
    const ds = distractors || [];
    item.distractors = ds.map((d, i) => ({
      id: `d${i + 1}`,
      value: d.value,
      display: d.display,
      misconceptionId: d.misconceptionId,
      rationale: d.rationale,
    }));
    const [aEnc, aDisp] = _answerDisplayValue(task, _solve(task, params));
    const poolOpts: Json[] = [{ value: aEnc, display: aDisp, correct: true, misconceptionId: null }];
    for (const d of ds) {
      poolOpts.push({ value: d.value, display: d.display, correct: false, misconceptionId: d.misconceptionId });
    }
    const shuffled = rng.shuffle(poolOpts);
    const labels = ["A", "B", "C", "D"];
    item.options = shuffled.map((o, i) => {
      const base: Json = { label: labels[i], value: o.value, display: o.display, correct: o.correct };
      if (o.misconceptionId) {
        base.misconceptionId = o.misconceptionId;
      }
      return base;
    });
  }
  return item;
}

function _publicParams(task: string, params: Json): Json {
  const out: Json = { ...params };
  if (task === "best_buy") {
    out.options = (params.options as Json[]).map((o) => ({ ...o }));
  }
  return out;
}

// --------------------------------------------------------------------------- //
// Independent validator.
// --------------------------------------------------------------------------- //
export function validate(item: Json): Json {
  const checks: Json[] = [];
  const add = (name: string, ok: boolean, detail = ""): void => {
    // Carry BOTH the Python oracle shape ({name, ok}) and the SDK GenValidationResult shape
    // ({name, result}), so the stability harness and the byte-parity gate read the same record.
    checks.push({ name, ok: Boolean(ok), result: ok ? "pass" : "fail", detail });
  };

  const p = item.params;
  const task = p.task as string;
  const interaction = item.interactionType;
  const answer = item.answer;

  add(
    "objective-mapping",
    arraysEqual(item.objectiveIds, [OBJECTIVE_BY_TASK[task]]),
    String(item.objectiveIds),
  );

  const sup = supportedInteractions(task);
  add("interaction-supported", sup.includes(interaction), `${interaction} in ${pyList(sup)}`);
  if (MC_ONLY_TASKS.includes(task)) {
    add("best-buy-is-mc-only", interaction === "multiple-choice");
  }
  if (!MC_ELIGIBLE_TASKS.includes(task)) {
    add("fr-only-task-not-mc", interaction === "free-response");
  }

  const sol = _solve(task, p);
  const rebuilt = _encodeAnswer(task, p);
  add("answer-recomputes", canonicalStringify(rebuilt) === canonicalStringify(answer), "answer re-derived from params matches stored canonical");

  const kind = ANSWER_KIND[task];
  if (kind === "ratio") {
    const parts = answer.canonical.parts as number[];
    add("ratio-in-simplest-form", RC.gcdList(parts) === 1, RC.formatRatio(parts));
    add("ratio-order-preserved", arraysEqual(parts, RC.simplifyParts(sol as number[])), `${pyList(parts)}`);
    const scaled = parts.map((pp) => pp * 2);
    add("checker-accepts-self", RC.checkRatio(parts, RC.formatRatio(parts), true).code === "correct");
    add(
      "checker-flags-unsimplified",
      RC.checkRatio(parts, RC.formatRatio(scaled), true).code === "equivalent-not-simplified",
    );
  } else if (kind === "integer") {
    add("integer-exact", answer.canonical.den === 1 && typeof sol === "number" && (sol as number) > 0, String(sol));
    if (task === "inverse_proportion") {
      add(
        "inverse-product-invariant",
        (p.q1 as number) * (p.v1 as number) === (p.q2 as number) * (sol as number),
        `${p.q1}*${p.v1} == ${p.q2}*${sol}`,
      );
    }
    if (task === "missing_part") {
      const one = Math.floor((p.knownValue as number) / ((p.parts as number[])[p.knownIndex as number] as number));
      add("missing-part-divisible", (p.knownValue as number) % ((p.parts as number[])[p.knownIndex as number] as number) === 0);
      add("missing-part-cross-multiplies", one * ((p.parts as number[])[p.missingIndex as number] as number) === (sol as number));
    }
  } else if (kind === "rational") {
    const f = new Rational(answer.canonical.num as number, answer.canonical.den as number);
    const s = sol as Rational;
    add(
      "rational-exact-and-reduced",
      f.equals(s) && f.num === s.num && f.den === s.den,
      _dispRat(f),
    );
    if (task === "ratio_to_fraction") {
      const a = (p.parts as number[])[0] as number;
      const b = (p.parts as number[])[1] as number;
      add("fraction-proper", f.num > 0 && f.num < f.den, _dispRat(f));
      add("fraction-part-over-whole", f.equals(new Rational((p.parts as number[])[p.partIndex as number] as number, a + b)));
    }
    if (task === "unit_rate") {
      add("unit-rate-recomputes", f.equals(new Rational(p.total as number, p.quantity as number)));
    }
    if (task === "direct_proportion") {
      add("direct-cross-multiplies", f.equals(new Rational(p.total as number, p.quantity as number).mul(Rational.from(p.target as number))));
    }
    if (task === "simple_scale") {
      add("scale-recomputes", f.equals(Rational.from(p.value as number).mul(new Rational(p.factorNum as number, p.factorDen as number))));
    }
  } else if (kind === "table") {
    const cells = answer.canonical.cells as Json[];
    const byLabel: Record<string, number> = {};
    for (const c of cells) {
      byLabel[c.location as string] = c.value as number;
    }
    const shares = RC.share(p.total as number, p.parts as number[]) as number[];
    const want: Record<string, number> = {};
    (p.labels as string[]).forEach((lab, i) => {
      want[lab] = shares[i] as number;
    });
    add(
      "table-labels-match",
      setEqual(Object.keys(byLabel), Object.keys(want)) && cells.length === (p.parts as number[]).length,
    );
    add("table-cell-values-match", recordEqual(byLabel, want));
    add(
      "shares-sum-to-whole",
      Object.values(byLabel).reduce((s2, v) => s2 + v, 0) === (p.total as number),
      `sum == ${p.total}`,
    );
    add("total-divisible-by-parts", (p.total as number) % (p.parts as number[]).reduce((s2, v) => s2 + v, 0) === 0);
  } else if (kind === "mc") {
    const rates: Record<string, Rational> = {};
    for (const o of p.options as Json[]) {
      rates[o.label as string] = new Rational(o.totalAmount as number, o.packSize as number);
    }
    const mn = _minRational(Object.values(rates));
    const winners = Object.keys(rates).filter((lab) => (rates[lab] as Rational).equals(mn));
    add("best-buy-unique-strict-min", winners.length === 1, `winners=${pyList(winners)}`);
    add(
      "best-buy-correct-is-min",
      winners.length > 0 && winners[0] === answer.canonical && answer.canonical === p.correctLabel,
      `min option ${winners.length > 0 ? winners[0] : null}`,
    );
    const witOk = (p.options as Json[]).every((o) =>
      new Rational(o.unitRate.num as number, o.unitRate.den as number).equals(
        new Rational(o.totalAmount as number, o.packSize as number),
      ),
    );
    add("best-buy-unit-rate-witness-exact", witOk);
  }

  const media = item.media || [];
  if (FIGURE_KIND[task] !== null && FIGURE_KIND[task] !== undefined) {
    add("media-present", media.length === 1);
    if (media.length > 0) {
      const m = media[0];
      const student = m.svg as string;
      const key = m.spec.answerKeySvg as string;
      add("media-kind-svg", m.kind === "svg");
      const rs = render(task, p, false, _accessibility(task, p, false)) as string;
      const rk = render(task, p, true, _accessibility(task, p, true)) as string;
      add("student-svg-realises-params", rs === student, "student SVG recomputes byte-for-byte");
      add("answer-key-svg-realises-params", rk === key, "answer-key SVG recomputes byte-for-byte");
      add("student-figure-has-no-overlay", student.indexOf('<g class="rt-overlay">') === -1);
      add(
        "answer-key-overlay-additive",
        key.indexOf('<g class="rt-overlay">') !== -1 && key.indexOf('<g class="rt-student">') === -1 && student !== key,
      );
      add(
        "student-and-key-share-base",
        _rtBase(student) !== "" && _rtBase(student) === _rtBase(key),
        "shared base group byte-identical",
      );
      add("student-unknown-marked-not-valued", _unknownHiddenInStudent(task, p, student));
      add("answer-key-reveals-unknown", _unknownShownInKey(task, p, key));
      add("student-a11y-no-result", !_a11yLeaks(task, p, (m.altText || "") + " " + (m.longDescription || "")));
      add(
        "dataTableFallback-present",
        typeof m.dataTableFallback === "object" && m.dataTableFallback !== null && "rows" in m.dataTableFallback,
      );
    }
  } else {
    add("no-figure-for-narrow-task", media.length === 0, "simplify/write/inverse carry no figure");
  }

  const band = item.difficulty.overallBand as number;
  const [lo, hi] = TASK_BANDS[task] as [number, number];
  add("difficulty-in-band", lo <= band && band <= hi, `band ${band} in [${lo},${hi}]`);

  if (interaction === "multiple-choice") {
    const opts = (item.options || []) as Json[];
    const vals = opts.map((o) => canonicalStringify(o.value));
    add("mc-options-distinct", new Set(vals).size === vals.length);
    add("mc-one-correct", opts.filter((o) => o.correct).length === 1);
    if (task === "best_buy") {
      add(
        "mc-option-count-matches-options",
        opts.length === (p.options as Json[]).length && opts.length >= 2 && opts.length <= 3,
        `${opts.length} options`,
      );
      const correctOpt = opts.filter((o) => o.correct);
      add("mc-correct-is-strict-min-option", correctOpt.length === 1 && (correctOpt[0] as Json).value === p.correctLabel);
    } else {
      add("mc-option-count", opts.length === 4, `${opts.length} options`);
      add("mc-distractors-misconception-backed", _distractorsRecompute(task, p, item));
    }
  }

  const valid = checks.every((c) => c.ok);
  // `valid` is the Python oracle field (golden-parity); `status` is the SDK GenValidationResult field.
  return { valid, status: valid ? "pass" : "fail", validatorVersion: VALIDATOR_VERSION, checks };
}

function _rtBase(svg: string): string {
  const a = svg.indexOf('<g class="rt-base">');
  if (a < 0) {
    return "";
  }
  const b = svg.indexOf("</g>", a);
  return b >= 0 ? svg.slice(a, b) : "";
}

function _unknownHiddenInStudent(task: string, params: Json, student: string): boolean {
  if (student.indexOf('<g class="rt-overlay">') !== -1) {
    return false;
  }
  const figTasks = [
    "share_two_part",
    "share_three_part",
    "missing_part",
    "direct_proportion",
    "unit_rate",
    "simple_scale",
    "best_buy",
    "ratio_to_fraction",
    "fraction_to_ratio",
  ];
  if (figTasks.includes(task)) {
    if (student.indexOf('<g class="rt-student">') === -1) {
      return false;
    }
    const studentGrp = student.slice(student.indexOf('<g class="rt-student">'));
    if (studentGrp.indexOf("?") === -1) {
      return false;
    }
    const sol = _solve(task, params);
    if (task === "share_two_part" || task === "share_three_part") {
      const shares = RC.share(params.total as number, params.parts as number[]) as number[];
      return shares.every((v) => studentGrp.indexOf(`>${v}</text>`) === -1);
    }
    if (task === "missing_part") {
      return studentGrp.indexOf(`>${sol}</text>`) === -1;
    }
    return true;
  }
  return true;
}

function _unknownShownInKey(task: string, params: Json, key: string): boolean {
  if (key.indexOf('<g class="rt-overlay">') === -1) {
    return false;
  }
  const sol = _solve(task, params);
  if (task === "share_two_part" || task === "share_three_part") {
    const shares = RC.share(params.total as number, params.parts as number[]) as number[];
    return shares.every((v) => key.indexOf(`>${v}</text>`) !== -1);
  }
  if (task === "missing_part") {
    return key.indexOf(`>${sol}</text>`) !== -1;
  }
  if (task === "direct_proportion" || task === "unit_rate" || task === "simple_scale") {
    return key.indexOf(_esc(_fmtVal(sol))) !== -1;
  }
  if (task === "best_buy") {
    return key.indexOf("✓") !== -1;
  }
  return true;
}

function _a11yLeaks(task: string, params: Json, text: string): boolean {
  if (task === "best_buy") {
    return false;
  }
  const disp = (_encodeAnswer(task, params).display as string) || "";
  const t = text.toLowerCase();
  return t.indexOf(`answer is ${disp}`.toLowerCase()) !== -1 || t.indexOf(`= ${disp}`.toLowerCase()) !== -1;
}

function _distractorsRecompute(task: string, params: Json, item: Json): boolean {
  const expected = _mcDistractors(task, params);
  if (expected === null) {
    return false;
  }
  const expKeys = expected.map((d) => canonicalStringify(d.value)).sort();
  const gotKeys = ((item.distractors as Json[]) || []).map((d) => canonicalStringify(d.value)).sort();
  return arraysEqual(expKeys, gotKeys);
}

// helpers
function arraysEqual<T>(a: T[], b: T[]): boolean {
  return a.length === b.length && a.every((v, i) => v === b[i]);
}

function setEqual(a: string[], b: string[]): boolean {
  if (a.length !== b.length) return false;
  const sb = new Set(b);
  return a.every((k) => sb.has(k));
}

function recordEqual(a: Record<string, number>, b: Record<string, number>): boolean {
  const ka = Object.keys(a);
  const kb = Object.keys(b);
  if (ka.length !== kb.length) return false;
  return ka.every((k) => a[k] === b[k]);
}

function pyList(items: (string | number)[]): string {
  // Mirror Python list/str repr for detail strings: ['a', 'b'] for strings, [1, 2] for numbers.
  const inner = items
    .map((s) => (typeof s === "string" ? `'${s}'` : String(s)))
    .join(", ");
  return `[${inner}]`;
}

// --------------------------------------------------------------------------- //
// serialize / describe
// --------------------------------------------------------------------------- //
export function serialize(item: Json): string {
  return canonicalStringify(item);
}

export function describe(): Json {
  return {
    generatorId: GENERATOR_ID,
    version: GENERATOR_VERSION,
    title: "Ratio and proportion",
    domain: "proportion",
    strand: "ratio-and-proportion",
    objectiveIds: RATIO_TASKS.map((t) => OBJECTIVE_BY_TASK[t]),
    tasks: [...RATIO_TASKS],
    interactionTypes: ["free-response", "multiple-choice"],
    answerTypes: ["ratio", "exact-rational", "integer", "table-completion", "multiple-choice"],
    difficultyRanges: Object.fromEntries(RATIO_TASKS.map((t) => [OBJECTIVE_BY_TASK[t], [...(TASK_BANDS[t] as [number, number])]])),
    approvalStatus: "pending-review",
  };
}
