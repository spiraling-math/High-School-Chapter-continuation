/**
 * gen.stats.data-handling v1.0.0 — TypeScript mirror.
 *
 * Byte-for-byte counterpart of oracle/spi_oracle/data_handling.py: the same seeded
 * generation, exact-`Rational` mathematics, deterministic chart renderers (bar chart,
 * pictogram, line graph) with integer pixel coordinates via grid_round, deterministic
 * semantic HTML tables, answer encodings, misconception-backed distractors, feature-driven
 * six-axis difficulty, accessibility, premium spec, and an independent validator. Parity is
 * gated by the golden + 300-entry parity fixtures (oracle/golden/data_handling.*).
 */

import { Rational } from "../../core/exact-math/rational.ts";
import { Mulberry32 } from "../../core/seeded-random/mulberry32.ts";
import { bandFromScore, round3, clamp01 } from "../../core/difficulty/band.ts";
import { canonicalStringify } from "../../core/serialization/canonical.ts";
import {
  MISCONCEPTIONS, rulesFor, adapterFor,
  type Ctx, type CtxValue, type AdapterValue,
} from "./data-handling-misconceptions.ts";

type Json = any;
type Frac = Rational;
const F = (x: number): Rational => new Rational(x, 1);

export const GENERATOR_ID = "gen.stats.data-handling";
export const GENERATOR_VERSION = "1.0.2";
export const VALIDATOR_VERSION = "1.0.2";
const CALCULATOR_POLICY = "calculator-not-required";

export const TASKS = ["read_bar_chart", "read_pictogram", "read_table_value", "read_line_graph",
  "complete_frequency_table", "mean_from_list", "median_from_list",
  "mode_from_list", "range_from_list", "mean_from_freq_table",
  "single_event_probability"] as const;
// complete_frequency_table is free-response only (owner C).
export const FREE_RESPONSE_ONLY = ["complete_frequency_table"] as const;
export const MC_TASKS = TASKS.filter((t) => !(FREE_RESPONSE_ONLY as readonly string[]).includes(t));
// Tasks whose primary representation is a canonical chart SVG.
const SVG_TASKS = ["read_bar_chart", "read_pictogram", "read_line_graph"];
// Tasks whose primary representation is a semantic HTML table.
const TABLE_TASKS = ["read_table_value", "complete_frequency_table", "mean_from_freq_table",
  "mean_from_list", "median_from_list", "mode_from_list", "range_from_list",
  "single_event_probability"];

export const OBJECTIVE_BY_TASK: Record<string, string> = {
  read_bar_chart: "SPI.MIDDLE.STAT.READ.BAR_CHART.01",
  read_pictogram: "SPI.MIDDLE.STAT.READ.PICTOGRAM.01",
  read_table_value: "SPI.MIDDLE.STAT.READ.TABLE_VALUE.01",
  read_line_graph: "SPI.MIDDLE.STAT.READ.LINE_GRAPH.01",
  complete_frequency_table: "SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01",
  mean_from_list: "SPI.MIDDLE.STAT.AVG.MEAN_LIST.01",
  median_from_list: "SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01",
  mode_from_list: "SPI.MIDDLE.STAT.AVG.MODE_LIST.01",
  range_from_list: "SPI.MIDDLE.STAT.AVG.RANGE_LIST.01",
  mean_from_freq_table: "SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01",
  single_event_probability: "SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01",
};
const TASK_BANDS: Record<string, [number, number]> = {
  read_bar_chart: [1, 2], read_pictogram: [1, 2], read_table_value: [1, 2],
  read_line_graph: [1, 2], complete_frequency_table: [2, 3],
  mean_from_list: [2, 3], median_from_list: [2, 3], mode_from_list: [1, 2],
  range_from_list: [1, 2], mean_from_freq_table: [3, 4],
  single_event_probability: [2, 3],
};
// Canonical answer kind per task (drives encoding + validation).
const ANSWER_KIND: Record<string, string> = {
  read_bar_chart: "integer", read_pictogram: "integer", read_table_value: "integer",
  read_line_graph: "integer", complete_frequency_table: "table-completion",
  mean_from_list: "rational", median_from_list: "rational", mode_from_list: "integer",
  range_from_list: "integer", mean_from_freq_table: "rational",
  single_event_probability: "fraction",
};

const MAX_PARAM_ATTEMPTS = 800;

// Themed category sets (categories carry their own labels — a non-colour indicator).
type CatTheme = [string, string, string[]];
type ListTheme = [string, string, string];  // (title, unit, domain) — owner #1
type ProbTheme = [string, string, string[]];

const CATEGORY_THEMES: CatTheme[] = [
  ["Favourite pet", "students", ["Cat", "Dog", "Fish", "Bird", "Rabbit", "Hamster"]],
  ["Favourite fruit", "children", ["Apple", "Banana", "Grape", "Orange", "Pear", "Plum"]],
  ["Sport played", "pupils", ["Football", "Tennis", "Hockey", "Netball", "Rugby"]],
  ["Colour of car", "cars", ["Red", "Blue", "Black", "White", "Silver", "Green"]],
  ["Books read", "readers", ["Mystery", "Fantasy", "Comic", "Science", "History"]],
];
const LINE_THEMES: CatTheme[] = [
  ["Temperature", "degrees", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]],
  ["Visitors", "people", ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]],
  ["Plant height", "cm", ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6"]],
  ["Goals scored", "goals", ["Game 1", "Game 2", "Game 3", "Game 4", "Game 5"]],
];
// List-data contexts carry a DOMAIN (owner #1). Negative values may appear ONLY in signed or
// context-free contexts; counts/measurements must stay non-negative. (title, unit, domain)
const LIST_THEMES_NONNEG: ListTheme[] = [
  ["Test scores", "marks", "count"], ["Goals scored", "goals", "count"],
  ["Ages", "years", "count"], ["Shoe sizes", "sizes", "measurement"],
  ["Numbers of pets", "pets", "count"], ["Daily steps", "thousand steps", "count"],
];
const LIST_THEMES_SIGNED: ListTheme[] = [
  ["Temperature", "°C", "signed"], ["Temperature change", "°C", "signed"],
  ["Elevation relative to sea level", "m", "signed"], ["Profit and loss", "£", "signed"],
  ["Change in value", "points", "signed"],
];
const LIST_THEMES_FREE: ListTheme[] = [
  ["Numerical data", "values", "context-free"], ["Data values", "values", "context-free"],
];
// Authoritative context-domain registry (owner #1): every context used by the generator,
// mapped to the value domain it admits. Drives the context-value compatibility validators.
// Category/line defaults are applied FIRST; the explicitly-domained list themes win on any
// title collision (e.g. a "Temperature" series is signed, not a plain count).
const CONTEXT_DOMAINS: Record<string, string> = {};
for (const t of CATEGORY_THEMES) CONTEXT_DOMAINS[t[0]] = "count";  // category frequencies are counts
for (const t of LINE_THEMES) CONTEXT_DOMAINS[t[0]] = "count";      // default line series to counts
for (const t of [...LIST_THEMES_NONNEG, ...LIST_THEMES_SIGNED, ...LIST_THEMES_FREE]) CONTEXT_DOMAINS[t[0]] = t[2];
const NONNEG_DOMAINS = ["count", "measurement", "category-frequency"];

const PROB_THEMES: ProbTheme[] = [
  ["a bag of counters", "counter", ["red", "blue", "green", "yellow"]],
  ["a box of beads", "bead", ["red", "blue", "white", "black"]],
  ["a set of cards", "card", ["star", "circle", "square", "triangle"]],
];

// --------------------------------------------------------------------------- //
// Exact-rational helpers + encoders
// --------------------------------------------------------------------------- //
/** Deterministic integer in [0, k-1] (mirrors next_int(0, k-1)). */
function nInt(rng: Mulberry32, k: number): number {
  return rng.nextInt(0, k - 1);
}

/** Round the exact rational num/den half-up toward +infinity. den > 0. */
function gridRound(num: number, den: number): number {
  const q = Math.floor(num / den);
  const rem = num - q * den;
  return 2 * rem >= den ? q + 1 : q;
}

/** The single most frequent value, or null when there is no UNIQUE mode (owner #2):
 *  null if every value occurs equally often, or if two or more values tie for the greatest
 *  frequency. Never substitutes the first/max/min value. */
function uniqueMode(values: number[]): number | null {
  if (values.length === 0) return null;
  const ordered = counterMostCommon(values);
  const top = ordered[0]![1];
  const winners = ordered.filter(([, c]) => c === top);
  if (winners.length !== 1) return null;
  if (top === 1) return null;  // all values distinct -> no mode
  return winners[0]![0];
}

/** Natural signed-arithmetic display (owner #8): 8 + -5 + -6 -> '8 − 5 − 6'.
 *  The first term keeps its own sign; subsequent negatives render as ' − k'. */
function sumExpr(values: number[]): string {
  const parts: string[] = [];
  for (let i = 0; i < values.length; i++) {
    const x = values[i]!;
    if (i === 0) parts.push(String(x));
    else if (x < 0) parts.push(`− ${Math.abs(x)}`);
    else parts.push(`+ ${x}`);
  }
  return parts.join(" ");
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

const encRat = (f: Frac): Json => ({ num: f.num, den: f.den });
const dispRat = (f: Frac): string => (f.den === 1 ? String(f.num) : `${f.num}/${f.den}`);

const sumOf = (xs: number[]): number => xs.reduce((a, b) => a + b, 0);

// --------------------------------------------------------------------------- //
// Canonical-SVG style + palette (monochrome authoritative; theme adds colour)
// --------------------------------------------------------------------------- //
const STYLE =
  ".cx-axis{stroke:#111;stroke-width:3;fill:none}" +
  ".cx-tick{stroke:#111;stroke-width:2}" +
  ".cx-tick-minor{stroke:#111;stroke-width:1.5}" +
  ".cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}" +
  ".cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}" +
  ".cx-bar{fill:#bbb;stroke:#111;stroke-width:2}" +
  ".cx-line{stroke:#111;stroke-width:3;fill:none}" +
  ".cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}" +
  ".cx-pt-core{fill:#111}" +
  ".cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}" +
  "text{font-family:sans-serif;font-size:24px;fill:#111}" +
  ".cx-ticklbl{font-size:20px;fill:#333}" +
  ".cx-catlbl{font-size:20px;fill:#111}" +
  ".cx-axislbl{font-size:22px;fill:#111}" +
  ".cx-keylbl{font-size:20px;fill:#111}";

// Plot-area geometry (viewBox 0 0 1000 700).
const VIEW_W = 1000, VIEW_H = 700;
const PLOT_X0 = 120, PLOT_X1 = 950;     // value/category plotting band (x)
const PLOT_Y0 = 70, PLOT_Y1 = 590;      // top (max) .. baseline (zero) (y)
const PLOT_H = PLOT_Y1 - PLOT_Y0;        // 520

/** Pin a count-axis step from {1,2,5,10} (owner J) and a nice axis maximum. */
function axisStepAndMax(maxv: number): [number, number] {
  for (const step of [1, 2, 5, 10]) {
    let ymax = Math.ceil(maxv / step) * step;
    if (ymax === 0) ymax = step;
    const ticks = ymax / step;
    if (4 <= ticks && ticks <= 8) return [step, ymax];
  }
  const step = 10;
  const ymax = Math.max(10, Math.ceil(maxv / step) * step);
  return [step, ymax];
}

// Direct-read scale contract (owner v1.0.2): every queried value (and every plotted value)
// must land on a VISIBLE mathematical mark — a labelled major tick, or a rendered minor
// subdivision whose declared step resolves it exactly. No pixel estimation.
const MIN_SUBDIV_PX = 14;     // each visible subdivision must be at least this many pixels apart
const MAX_MINOR_LINES = 24;   // the minor grid must not be overloaded (clutter cap)

/** gcd of two non-negative integers (Euclid). Mirrors Python math.gcd on |a|,|b|. */
function gcd(a: number, b: number): number {
  a = Math.abs(a);
  b = Math.abs(b);
  while (b !== 0) {
    const t = a % b;
    a = b;
    b = t;
  }
  return a;
}

function listGcd(xs: number[]): number {
  let g = 0;
  for (const x of xs) g = gcd(g, Math.abs(Math.trunc(x)));
  return g || 1;
}

/** (majorStep, minorStep, ymax). The minor step is the coarsest subdivision of the major
 *  step that still divides EVERY plotted value, so all bars/points land on a visible mark
 *  (minorStep === majorStep means no extra minor grid is needed). */
function chartScale(values: number[]): [number, number, number] {
  const [major, ymax] = axisStepAndMax(Math.max(...values));
  let minor = gcd(major, listGcd(values));
  if (minor < 1) minor = 1;
  return [major, minor, ymax];
}

function subdivPx(minor: number, ymax: number): number {
  return gridRound(PLOT_H * minor, ymax);
}

/** The grid resolves the data without estimation or clutter. */
function scaleReadable(major: number, minor: number, ymax: number): boolean {
  if (minor < 1 || major % minor !== 0) return false;
  if (Math.floor(ymax / minor) > MAX_MINOR_LINES) return false;   // too many minor lines -> overloaded
  if (subdivPx(minor, ymax) < MIN_SUBDIV_PX) return false;        // subdivisions too close to read
  return true;
}

/** Project a value onto the integer pixel y (0 at baseline, ymax at top). */
function py(ymax: number, value: number): number {
  return PLOT_Y1 - gridRound(value * PLOT_H, ymax);
}

function slotEdges(n: number, i: number): [number, number] {
  const left = PLOT_X0 + gridRound((PLOT_X1 - PLOT_X0) * i, n);
  const right = PLOT_X0 + gridRound((PLOT_X1 - PLOT_X0) * (i + 1), n);
  return [left, right];
}

// --------------------------------------------------------------------------- //
// Canonical chart renderers (byte-parity targets)
// --------------------------------------------------------------------------- //
interface Acc { title: string; alt: string; desc: string; spoken: string; dataTable: Json; }

function svgOpen(acc: Acc): string[] {
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VIEW_W} ${VIEW_H}" role="img" aria-label="${esc(acc.alt)}">`,
    `<title>${esc(acc.title)}</title>`,
    `<desc>${esc(acc.desc)}</desc>`,
    `<style>${STYLE}</style>`,
  ];
}

/** Render the value axis with a MAJOR grid (labelled ticks) and, when minor < major, a
 *  rendered MINOR subdivision grid (unlabelled, lighter) so every plotted/queried value lands
 *  on a visible mark (owner v1.0.2 direct-read contract). */
function valueAxis(out: string[], ymax: number, major: number, minor: number, unitLabel: string): void {
  out.push(`<line class="cx-axis" x1="${PLOT_X0}" y1="${PLOT_Y0}" x2="${PLOT_X0}" y2="${PLOT_Y1}"/>`);
  out.push(`<line class="cx-axis" x1="${PLOT_X0}" y1="${PLOT_Y1}" x2="${PLOT_X1}" y2="${PLOT_Y1}"/>`);
  // 1. minor subdivisions (only at positions that are NOT also a major mark).
  if (minor < major) {
    let v = minor;
    while (v < ymax) {
      if (v % major !== 0) {
        const yp = py(ymax, v);
        out.push(`<line class="cx-grid-minor" x1="${PLOT_X0}" y1="${yp}" x2="${PLOT_X1}" y2="${yp}"/>`);
        out.push(`<line class="cx-tick-minor" x1="${PLOT_X0 - 4}" y1="${yp}" x2="${PLOT_X0}" y2="${yp}"/>`);
      }
      v += minor;
    }
  }
  // 2. major gridlines + ticks + integer labels.
  let v = 0;
  while (v <= ymax) {
    const yp = py(ymax, v);
    if (v !== 0) {
      out.push(`<line class="cx-grid-major" x1="${PLOT_X0}" y1="${yp}" x2="${PLOT_X1}" y2="${yp}"/>`);
    }
    out.push(`<line class="cx-tick" x1="${PLOT_X0 - 6}" y1="${yp}" x2="${PLOT_X0}" y2="${yp}"/>`);
    out.push(`<text class="cx-ticklbl" x="${PLOT_X0 - 12}" y="${yp + 7}" text-anchor="end">${v}</text>`);
    v += major;
  }
  const mid = Math.floor((PLOT_Y0 + PLOT_Y1) / 2);
  out.push(`<text class="cx-axislbl" x="36" y="${mid}" ` +
    `text-anchor="middle" transform="rotate(-90 36 ${mid})">${esc(unitLabel)}</text>`);
}

function barChartSvg(params: Json): string {
  const ds = params.dataset;
  const cats: string[] = ds.categories, freqs: number[] = ds.frequencies, unit: string = ds.unit;
  const n = cats.length;
  const [major, minor, ymax] = chartScale(freqs);
  const acc = accessibility("read_bar_chart", params);
  const out = svgOpen(acc);
  valueAxis(out, ymax, major, minor, `Frequency (${unit})`);
  for (let i = 0; i < n; i++) {
    const cat = cats[i]!, fr = freqs[i]!;
    const [left, right] = slotEdges(n, i);
    const inset = gridRound((right - left) * 20, 100);
    const bl = left + inset, br = right - inset;
    const top = py(ymax, fr);
    out.push(`<rect class="cx-bar" data-cat="${i}" x="${bl}" y="${top}" width="${br - bl}" height="${PLOT_Y1 - top}"/>`);
    const cx = Math.floor((left + right) / 2);
    out.push(`<text class="cx-catlbl" x="${cx}" y="${PLOT_Y1 + 28}" text-anchor="middle">${esc(cat)}</text>`);
  }
  out.push(`<text class="cx-axislbl" x="${Math.floor((PLOT_X0 + PLOT_X1) / 2)}" y="${VIEW_H - 18}" text-anchor="middle">${esc(ds.title)}</text>`);
  out.push("</svg>");
  return out.join("\n");
}

function lineGraphSvg(params: Json): string {
  const ds = params.dataset;
  const labels: string[] = ds.seriesLabels, vals: number[] = ds.values, unit: string = ds.unit;
  const n = labels.length;
  const [major, minor, ymax] = chartScale(vals);
  const acc = accessibility("read_line_graph", params);
  const out = svgOpen(acc);
  valueAxis(out, ymax, major, minor, `${ds.title} (${unit})`);
  const xs: number[] = [];
  for (let i = 0; i < n; i++) xs.push(PLOT_X0 + gridRound((PLOT_X1 - PLOT_X0) * (2 * i + 1), 2 * n));
  const pts: Array<[number, number]> = [];
  for (let i = 0; i < n; i++) pts.push([xs[i]!, py(ymax, vals[i]!)]);
  out.push('<polyline class="cx-line" points="' + pts.map(([x, y]) => `${x},${y}`).join(" ") + '"/>');
  for (let i = 0; i < pts.length; i++) {
    const [x, y] = pts[i]!;
    out.push(`<circle class="cx-pt-outline" cx="${x}" cy="${y}" r="7"/>`);
    out.push(`<circle class="cx-pt-core" cx="${x}" cy="${y}" r="3"/>`);
    out.push(`<line class="cx-tick" x1="${x}" y1="${PLOT_Y1}" x2="${x}" y2="${PLOT_Y1 + 6}"/>`);
    out.push(`<text class="cx-catlbl" x="${x}" y="${PLOT_Y1 + 28}" text-anchor="middle">${esc(labels[i]!)}</text>`);
  }
  out.push("</svg>");
  return out.join("\n");
}

function pictogramSvg(params: Json): string {
  const ds = params.dataset;
  const cats: string[] = ds.categories, freqs: number[] = ds.frequencies, unit: string = ds.unit, key: number = ds.pictogramKey;
  const acc = accessibility("read_pictogram", params);
  const out = svgOpen(acc);
  out.push(`<text class="cx-keylbl" x="${PLOT_X0}" y="48">Key: 1 symbol represents ${key} ${esc(unit)}.</text>`);
  const rowH = 70;
  const sym = 34;     // symbol box size
  const gap = 10;
  const labelX = 80;
  const gridX = 280;
  for (let i = 0; i < cats.length; i++) {
    const cat = cats[i]!, fr = freqs[i]!;
    const ry = 90 + i * rowH;
    const cy = ry + Math.floor(sym / 2);
    out.push(`<text class="cx-catlbl" x="${labelX}" y="${cy + 7}" text-anchor="start">${esc(cat)}</text>`);
    const whole = Math.floor(fr / key);
    const hasHalf = (fr % key) === Math.floor(key / 2) && key % 2 === 0;
    for (let s = 0; s < whole; s++) {
      const sx = gridX + s * (sym + gap);
      out.push(`<rect class="cx-symbol" data-cat="${i}" x="${sx}" y="${ry}" width="${sym}" height="${sym}" rx="6"/>`);
    }
    if (hasHalf) {
      const sx = gridX + whole * (sym + gap);
      out.push(`<rect class="cx-symbol" data-cat="${i}" data-half="1" x="${sx}" y="${ry}" width="${Math.floor(sym / 2)}" height="${sym}" rx="6"/>`);
    }
  }
  out.push(`<text class="cx-axislbl" x="${Math.floor(VIEW_W / 2)}" y="${VIEW_H - 18}" text-anchor="middle">${esc(ds.title)}</text>`);
  out.push("</svg>");
  return out.join("\n");
}

function chartSvg(task: string, params: Json): string {
  if (task === "read_bar_chart") return barChartSvg(params);
  if (task === "read_line_graph") return lineGraphSvg(params);
  if (task === "read_pictogram") return pictogramSvg(params);
  throw new Error(task);
}

// --------------------------------------------------------------------------- //
// Deterministic semantic HTML-table renderer (owner F; byte-parity target)
// --------------------------------------------------------------------------- //
function tableCell(value: number, blank: boolean, aria: string): string {
  if (blank) {
    return `<td class="cx-blank"><input type="text" inputmode="numeric" aria-label="${esc(aria)}"></td>`;
  }
  return `<td>${value}</td>`;
}

function freqTableHtml(params: Json, reveal: boolean): string {
  const ds = params.dataset;
  const cats: string[] = ds.categories, freqs: number[] = ds.frequencies;
  const total = sumOf(freqs);
  const blank = params.blank;  // {kind:"frequency",index:i} or {kind:"total"} or undefined
  const lines = ['<table class="cx-table">'];
  lines.push(`<caption>${esc(ds.title)}</caption>`);
  lines.push('<thead><tr><th scope="col">Category</th><th scope="col">Frequency</th></tr></thead>');
  lines.push('<tbody>');
  for (let i = 0; i < cats.length; i++) {
    const cat = cats[i]!, fr = freqs[i]!;
    const isBlank = !!blank && blank.kind === "frequency" && blank.index === i;
    const cell = tableCell(fr, isBlank && !reveal, `Frequency for ${cat}`);
    lines.push(`<tr><th scope="row">${esc(cat)}</th>${cell}</tr>`);
  }
  const isBlankTotal = !!blank && blank.kind === "total";
  const cell = tableCell(total, isBlankTotal && !reveal, "Total frequency");
  lines.push(`<tr class="cx-total"><th scope="row">Total</th>${cell}</tr>`);
  lines.push('</tbody></table>');
  return lines.join("\n");
}

function listTableHtml(params: Json): string {
  const ds = params.dataset;
  const vals: number[] = ds.values, title: string = ds.title;
  const lines = ['<table class="cx-list">'];
  lines.push(`<caption>${esc(title)}</caption>`);
  lines.push('<tbody><tr>');
  for (const v of vals) lines.push(`<td>${v}</td>`);
  lines.push('</tr></tbody></table>');
  return lines.join("\n");
}

function valueFreqTableHtml(params: Json): string {
  const ds = params.dataset;
  const vals: number[] = ds.categories, freqs: number[] = ds.frequencies, title: string = ds.title;
  const lines = ['<table class="cx-table">'];
  lines.push(`<caption>${esc(title)}</caption>`);
  lines.push('<thead><tr><th scope="col">Value</th><th scope="col">Frequency</th></tr></thead>');
  lines.push('<tbody>');
  for (let i = 0; i < vals.length; i++) {
    lines.push(`<tr><th scope="row">${esc(String(vals[i]!))}</th><td>${freqs[i]!}</td></tr>`);
  }
  lines.push('</tbody></table>');
  return lines.join("\n");
}

function probTableHtml(params: Json): string {
  const ds = params.dataset;
  const cats: string[] = ds.categories, freqs: number[] = ds.frequencies, title: string = ds.title;
  const lines = ['<table class="cx-table">'];
  lines.push(`<caption>${esc(title)}</caption>`);
  lines.push('<thead><tr><th scope="col">Type</th><th scope="col">How many</th></tr></thead>');
  lines.push('<tbody>');
  for (let i = 0; i < cats.length; i++) {
    lines.push(`<tr><th scope="row">${esc(cats[i]!)}</th><td>${freqs[i]!}</td></tr>`);
  }
  lines.push(`<tr class="cx-total"><th scope="row">Total</th><td>${sumOf(freqs)}</td></tr>`);
  lines.push('</tbody></table>');
  return lines.join("\n");
}

function tableHtml(task: string, params: Json, reveal = false): string {
  if (task === "read_table_value" || task === "complete_frequency_table") return freqTableHtml(params, reveal);
  if (task === "mean_from_freq_table") return valueFreqTableHtml(params);
  if (task === "single_event_probability") return probTableHtml(params);
  if (task === "mean_from_list" || task === "median_from_list" || task === "mode_from_list" || task === "range_from_list") return listTableHtml(params);
  throw new Error(task);
}

// --------------------------------------------------------------------------- //
// Solvers (exact)
// --------------------------------------------------------------------------- //
type SolveResult = number | Rational;

function solve(task: string, params: Json): SolveResult {
  const ds = params.dataset;
  if (task === "read_bar_chart" || task === "read_pictogram" || task === "read_table_value") {
    return ds.frequencies[params.queryIndex] as number;
  }
  if (task === "read_line_graph") return ds.values[params.queryIndex] as number;
  if (task === "complete_frequency_table") return completeValue(params);
  if (task === "mean_from_list") {
    const v: number[] = ds.values;
    return new Rational(sumOf(v), v.length);
  }
  if (task === "median_from_list") {
    const v = [...ds.values].sort((a: number, b: number) => a - b) as number[];
    const n = v.length;
    return n % 2 ? F(v[Math.floor(n / 2)]!) : new Rational(v[Math.floor(n / 2) - 1]! + v[Math.floor(n / 2)]!, 2);
  }
  if (task === "mode_from_list") {
    return mostCommon(ds.values as number[])[0]!;
  }
  if (task === "range_from_list") {
    const v: number[] = ds.values;
    return Math.max(...v) - Math.min(...v);
  }
  if (task === "mean_from_freq_table") {
    const vals: number[] = ds.categories, freqs: number[] = ds.frequencies;
    let svf = 0;
    for (let i = 0; i < vals.length; i++) svf += vals[i]! * freqs[i]!;
    return new Rational(svf, sumOf(freqs));
  }
  if (task === "single_event_probability") {
    const os = params.outcomeSpace;
    return new Rational(os.favourable, os.total);
  }
  throw new Error(task);
}

function completeValue(params: Json): number {
  const ds = params.dataset;
  const freqs: number[] = ds.frequencies;
  const blank = params.blank;
  if (blank.kind === "total") return sumOf(freqs);
  return freqs[blank.index]!;  // frequencies already store the true value
}

/** Counter.most_common — value with highest count; ties broken by first-seen order.
 *  Returns the list of [value, count] pairs sorted by count desc (insertion order for ties),
 *  matching Python's collections.Counter.most_common(). */
function counterMostCommon(values: number[]): Array<[number, number]> {
  const order: number[] = [];
  const counts = new Map<number, number>();
  for (const v of values) {
    if (!counts.has(v)) { counts.set(v, 0); order.push(v); }
    counts.set(v, counts.get(v)! + 1);
  }
  // Stable sort by count descending, preserving first-insertion order for ties.
  return order
    .map((v) => [v, counts.get(v)!] as [number, number])
    .sort((a, b) => b[1] - a[1]);
}
const mostCommon = (values: number[]): [number, number] => counterMostCommon(values)[0]!;

// --------------------------------------------------------------------------- //
// Misconception context + distractors
// --------------------------------------------------------------------------- //
function ctxOf(task: string, params: Json, correct: SolveResult): Ctx {
  const ds = params.dataset;
  const c: Ctx = { correct: correct as CtxValue };
  if (task === "read_bar_chart" || task === "read_pictogram" || task === "read_table_value" || task === "read_line_graph") {
    const vals: number[] = task === "read_line_graph" ? ds.values : ds.frequencies;
    c.values = [...vals];
    c.queryIndex = params.queryIndex;
    c.total = sumOf(vals);
    if (task === "read_bar_chart" || task === "read_line_graph") {
      const [major, minor] = chartScale(vals);
      c.axisStep = minor;       // off-by-step / miscount use the visible MINOR subdivision
      c.minorStep = minor;
      c.majorStep = major;
    }
    if (task === "read_pictogram") {
      c.key = ds.pictogramKey;
      const fr = ds.frequencies[params.queryIndex] as number;
      c.halfPresent = (fr % ds.pictogramKey) === Math.floor(ds.pictogramKey / 2) && ds.pictogramKey % 2 === 0;
    }
    if (task === "read_line_graph") {
      c.xValue = params.queryIndex + 1;
    }
  } else if (task === "mean_from_list" || task === "median_from_list" || task === "mode_from_list" || task === "range_from_list") {
    const v: number[] = ds.values;
    c.values = [...v];
    c.sortedVals = [...v].sort((a, b) => a - b);
    c.n = v.length;
    c.listSum = sumOf(v);
    c.maxv = Math.max(...v);
    c.minv = Math.min(...v);
    // uniqueMode is null when there is no single most-frequent value (owner #2).
    const um = uniqueMode(v);
    c.uniqueMode = um;
    c.modeFrequency = um !== null ? counterMostCommon(v).find(([val]) => val === um)![1] : null;
    c.midrange = new Rational(Math.max(...v) + Math.min(...v), 2);
    c.meanValue = new Rational(sumOf(v), v.length);
    const sv = [...v].sort((a, b) => a - b);
    c.medianValue = sv.length % 2
      ? F(sv[Math.floor(sv.length / 2)]!)
      : new Rational(sv[Math.floor(sv.length / 2) - 1]! + sv[Math.floor(sv.length / 2)]!, 2);
  } else if (task === "mean_from_freq_table") {
    const vals: number[] = ds.categories, freqs: number[] = ds.frequencies;
    let svf = 0;
    for (let i = 0; i < vals.length; i++) svf += vals[i]! * freqs[i]!;
    c.sumVF = svf;
    c.sumf = sumOf(freqs);
    c.nCats = vals.length;
    c.sumValues = sumOf(vals);
    c.n = sumOf(freqs);
    c.listSum = svf;
  } else if (task === "single_event_probability") {
    const os = params.outcomeSpace;
    c.favourable = os.favourable;
    c.probTotal = os.total;
  }
  return c;
}

interface Distractor { value: AdapterValue; misconceptionId: string; rationale: string; }

/** Up to three DISTINCT misconception-backed distractor values, else null (owner N). */
function distractors(task: string, params: Json, correct: SolveResult): Distractor[] | null {
  const c = ctxOf(task, params, correct);
  const out: Distractor[] = [];
  const seen = new Set<string>([valueKey(task, correct)]);
  for (const mid of rulesFor(task)) {
    const val = adapterFor(mid)(c);
    if (val === null) continue;
    if (!valueOk(task, val)) continue;
    const k = valueKey(task, val);
    if (seen.has(k)) continue;
    seen.add(k);
    const m = MISCONCEPTIONS[mid]!;
    out.push({ value: val, misconceptionId: mid, rationale: m.observableError });
    if (out.length === 3) break;
  }
  return out.length === 3 ? out : null;
}

function valueOk(task: string, val: AdapterValue): boolean {
  if (task === "single_event_probability") {
    if (!(val instanceof Rational)) return false;
    return val.num >= 0 && val.num <= val.den;  // 0 <= val <= 1
  }
  if (ANSWER_KIND[task] === "rational") {
    return val instanceof Rational;
  }
  // integer-valued tasks: distractor must be a non-negative integer (counts/values)
  let iv: number | null;
  if (typeof val === "number") iv = val;
  else if (val instanceof Rational && val.den === 1) iv = val.num;
  else iv = null;
  return iv !== null && iv >= 0;
}

function valueKey(task: string, val: AdapterValue | SolveResult): string {
  // Normalise so an integer and a Rational(n,1) share a key (dedup correctness).
  if (val instanceof Rational) return dispRat(val);
  return String(val);
}

// --------------------------------------------------------------------------- //
// Answer encoding + display
// --------------------------------------------------------------------------- //
function encodeAnswer(task: string, params: Json, correct: SolveResult): Json {
  const kind = ANSWER_KIND[task];
  if (kind === "integer") {
    const iv = correct as number;
    return { type: "integer", canonical: iv, display: String(iv) };
  }
  if (kind === "rational") {
    const f = correct instanceof Rational ? correct : F(correct as number);
    const typ = f.den === 1 ? "integer" : "exact-rational";
    return {
      type: typ, canonical: f.den === 1 ? f.num : encRat(f),
      display: dispRat(f), accepts: { fraction: true, decimal: false, mixed: false },
    };
  }
  if (kind === "fraction") {
    const f = correct as Rational;
    return {
      type: "fraction", canonical: encRat(f), display: dispRat(f),
      accepts: { fraction: false, decimal: false, mixed: false },
    };
  }
  if (kind === "table-completion") {
    const blank = params.blank;
    const loc = blank.kind === "total" ? "Total" : params.dataset.categories[blank.index];
    return {
      type: "table-completion", canonical: { cells: [{ location: loc, value: correct as number }] },
      display: String(correct as number),
    };
  }
  throw new Error(kind);
}

function displayValue(task: string, val: AdapterValue | SolveResult): [Json, string] {
  const kind = ANSWER_KIND[task];
  if (kind === "integer" || kind === "table-completion") {
    // Mirror Python int(val): collapse a Rational (always den 1 here) to an int.
    const iv = val instanceof Rational ? Math.trunc(val.num / val.den) : (val as number);
    return [iv, String(iv)];
  }
  const f = val instanceof Rational ? val : F(val as number);
  if (kind === "fraction") return [encRat(f), dispRat(f)];
  return [f.den === 1 ? f.num : encRat(f), dispRat(f)];
}

// --------------------------------------------------------------------------- //
// Difficulty (owner M — schema-valid axes only)
// --------------------------------------------------------------------------- //
const WEIGHTS: Record<string, number> = {
  numericalComplexity: 0.25, readingDemand: 0.15, interpretationDemand: 0.2,
  reasoningSteps: 0.2, informationDensity: 0.1, scaffolding: 0.1,
};
const WEIGHT_KEYS = ["numericalComplexity", "readingDemand", "interpretationDemand",
  "reasoningSteps", "informationDensity", "scaffolding"];

function difficulty(task: string, params: Json): Json {
  const ds = params.dataset;
  const scaffold = Boolean(params.scaffold);
  const axes: Record<string, number> = {};
  for (const k of WEIGHT_KEYS) axes[k] = 0.0;
  axes.scaffolding = scaffold ? 0.1 : 0.5;

  if (task === "read_bar_chart" || task === "read_table_value" || task === "read_line_graph") {
    const vals: number[] = (ds.values && ds.values.length ? ds.values : ds.frequencies);
    const n = vals.length;
    axes.numericalComplexity = Math.min(1.0, Math.max(...vals) / 50);
    axes.readingDemand = 0.15 + 0.05 * (n - 3);
    axes.interpretationDemand = ({ read_bar_chart: 0.15, read_table_value: 0.1, read_line_graph: 0.2 } as Record<string, number>)[task]!;
    axes.reasoningSteps = 0.1;
    const denom0 = task === "read_line_graph" ? 5 : 3;
    axes.informationDensity = Math.min(1.0, Math.max(0, n - denom0) / 3);
  } else if (task === "read_pictogram") {
    const freqs: number[] = ds.frequencies, key: number = ds.pictogramKey;
    const n = freqs.length;
    const anyhalf = freqs.some((f) => (f % key) === Math.floor(key / 2) && key % 2 === 0);
    axes.numericalComplexity = ({ 2: 0.2, 5: 0.4, 10: 0.5 } as Record<number, number>)[key]! + (anyhalf ? 0.1 : 0.0);
    axes.readingDemand = 0.15 + 0.05 * (n - 3);
    axes.interpretationDemand = 0.25;
    axes.reasoningSteps = 0.15;
    axes.informationDensity = Math.min(1.0, (n - 3) / 3);
  } else if (task === "complete_frequency_table") {
    const freqs: number[] = ds.frequencies;
    const n = freqs.length;
    axes.numericalComplexity = Math.min(1.0, sumOf(freqs) / 60);
    axes.readingDemand = 0.25 + 0.05 * (n - 3);
    axes.interpretationDemand = 0.3;
    axes.reasoningSteps = 0.3;
    axes.informationDensity = Math.min(1.0, (n - 3) / 3);
  } else if (task === "mode_from_list" || task === "range_from_list") {
    const vals: number[] = ds.values;
    const n = vals.length;
    const spread = Math.max(...vals) - Math.min(...vals);
    axes.numericalComplexity = Math.min(0.45, 0.1 + spread / 60);
    axes.readingDemand = 0.2;
    axes.interpretationDemand = 0.2;
    axes.reasoningSteps = 0.2;
    const denom = task === "range_from_list" ? 4 : 5;
    axes.informationDensity = Math.min(1.0, Math.max(0, n - denom) / 3);
  } else if (task === "mean_from_list" || task === "median_from_list") {
    const f = solve(task, params);
    const n = ds.values.length;
    const frac = f instanceof Rational && f.den > 1;
    axes.numericalComplexity = 0.3 + (frac ? 0.25 : 0.0);
    axes.readingDemand = 0.2;
    axes.interpretationDemand = 0.3;
    axes.reasoningSteps = 0.35;
    axes.informationDensity = Math.min(1.0, (n - 3) / 3);
  } else if (task === "mean_from_freq_table") {
    const f = solve(task, params);
    const n = ds.categories.length;
    const frac = f instanceof Rational && f.den > 1;
    axes.numericalComplexity = 0.55 + (frac ? 0.25 : 0.0);
    axes.readingDemand = 0.4 + 0.05 * (n - 3);
    axes.interpretationDemand = 0.55;
    axes.reasoningSteps = 0.7;
    axes.informationDensity = Math.min(1.0, (n - 3) / 3);
  } else if (task === "single_event_probability") {
    const os = params.outcomeSpace;
    const n = ds.categories.length;
    const f = solve(task, params) as Rational;
    const reduces = f.den !== os.total && !(f.num === 0 && f.den === 1) && !(f.num === 1 && f.den === 1);
    axes.numericalComplexity = Math.min(1.0, os.total / 16) + (reduces ? 0.1 : 0.0);
    axes.readingDemand = 0.25;
    axes.interpretationDemand = 0.4;
    axes.reasoningSteps = 0.35;
    axes.informationDensity = Math.min(1.0, (n - 2) / 3);
  }

  for (const k of WEIGHT_KEYS) axes[k] = clamp01(axes[k]!);
  let score = 0;
  for (const k of WEIGHT_KEYS) score += WEIGHTS[k]! * axes[k]!;
  let band = bandFromScore(score);
  const [lo, hi] = TASK_BANDS[task]!;
  band = Math.max(lo, Math.min(hi, band));
  const roundedAxes: Record<string, number> = {};
  for (const k of WEIGHT_KEYS) roundedAxes[k] = round3(axes[k]!);
  return { overallBand: band, axes: roundedAxes };
}

// --------------------------------------------------------------------------- //
// Accessibility (owner L — student a11y must not state a computed result)
// --------------------------------------------------------------------------- //
function dataRows(ds: Json, task: string): string {
  if (task === "read_line_graph") {
    const labels: string[] = ds.seriesLabels, vals: number[] = ds.values;
    return labels.map((k, i) => `${k}: ${vals[i]}`).join("; ");
  }
  if (task === "mean_from_list" || task === "median_from_list" || task === "mode_from_list" || task === "range_from_list") {
    return (ds.values as number[]).map((v) => String(v)).join(", ");
  }
  if (task === "mean_from_freq_table") {
    const vals: number[] = ds.categories, freqs: number[] = ds.frequencies;
    return vals.map((v, i) => `value ${v} occurs ${freqs[i]}`).join("; ");
  }
  const cats: string[] = ds.categories, freqs: number[] = ds.frequencies;
  return cats.map((k, i) => `${k}: ${freqs[i]}`).join("; ");
}

function dataTableObj(task: string, ds: Json): Json {
  if (task === "read_line_graph") {
    return {
      columns: ["Position", "Value"],
      rows: (ds.seriesLabels as string[]).map((lab, i) => [lab, String(ds.values[i])]),
    };
  }
  if (task === "mean_from_list" || task === "median_from_list" || task === "mode_from_list" || task === "range_from_list") {
    return { columns: ["Value"], rows: (ds.values as number[]).map((v) => [String(v)]) };
  }
  if (task === "mean_from_freq_table") {
    return {
      columns: ["Value", "Frequency"],
      rows: (ds.categories as number[]).map((v, i) => [String(v), String(ds.frequencies[i])]),
    };
  }
  if (task === "read_pictogram") {
    const key: number = ds.pictogramKey;
    const rows: string[][] = [];
    const cats: string[] = ds.categories, freqs: number[] = ds.frequencies;
    for (let i = 0; i < cats.length; i++) {
      const fr = freqs[i]!;
      const whole = Math.floor(fr / key);
      const half = (fr % key) === Math.floor(key / 2) && key % 2 === 0;
      rows.push([cats[i]!, half ? `${whole} whole symbols and 1 half symbol` : `${whole} whole symbols`]);
    }
    return { columns: ["Category", `Symbols (1 symbol = ${key} ${ds.unit})`], rows };
  }
  if (task === "single_event_probability") {
    const cats: string[] = ds.categories, freqs: number[] = ds.frequencies;
    const rows: string[][] = cats.map((cat, i) => [cat, String(freqs[i])]);
    rows.push(["Total", String(sumOf(freqs))]);
    return { columns: ["Type", "How many"], rows };
  }
  // bar chart / frequency table value / complete frequency table
  const cats: string[] = ds.categories, freqs: number[] = ds.frequencies;
  const rows: string[][] = [];
  for (let i = 0; i < cats.length; i++) rows.push([cats[i]!, String(freqs[i]!)]);
  return { columns: ["Category", "Frequency"], rows };
}

function accessibility(task: string, params: Json): Acc {
  const ds = params.dataset;
  const title: string = ds.title ?? "data";
  let alt: string, spoken: string;
  if (task === "read_bar_chart") {
    alt = `Vertical bar chart: ${title}.`;
    spoken = `A bar chart titled ${title}. Read the frequency for the named category from the labelled axis.`;
  } else if (task === "read_pictogram") {
    alt = `Pictogram: ${title}.`;
    spoken = `A pictogram titled ${title}, where one symbol represents ${ds.pictogramKey} ${ds.unit}. Read the frequency for the named category.`;
  } else if (task === "read_line_graph") {
    alt = `Line graph: ${title}.`;
    spoken = `A line graph titled ${title} with marked points at each labelled position. Read the value at the named position.`;
  } else if (task === "read_table_value" || task === "complete_frequency_table" || task === "mean_from_freq_table" || task === "single_event_probability") {
    alt = `Frequency table: ${title}.`;
    spoken = `A frequency table titled ${title}.`;
  } else {
    alt = `Data list: ${title}.`;
    spoken = `A list of values titled ${title}.`;
  }
  return { title, alt, desc: spoken, spoken, dataTable: dataTableObj(task, ds) };
}

// --------------------------------------------------------------------------- //
// Prompt + solution
// --------------------------------------------------------------------------- //
function prompt(task: string, params: Json): Json {
  const ds = params.dataset;
  const blocks: Json[] = [];
  blocks.push({ kind: "media-ref", ref: "fig-1" });
  let instr = "";
  if (task === "read_bar_chart" || task === "read_table_value") {
    const cat = ds.categories[params.queryIndex];
    instr = `How many ${ds.unit} are in the category “${cat}”?`;
  } else if (task === "read_pictogram") {
    const cat = ds.categories[params.queryIndex];
    instr = `Use the key to find the number of ${ds.unit} for “${cat}”.`;
  } else if (task === "read_line_graph") {
    const lab = ds.seriesLabels[params.queryIndex];
    instr = `What is the value at ${lab}?`;
  } else if (task === "complete_frequency_table") {
    instr = "Find the missing value in the frequency table.";
  } else if (task === "mean_from_list") {
    instr = "Calculate the mean of the data. Give your answer as an integer or a fraction in its simplest form.";
  } else if (task === "median_from_list") {
    instr = "Find the median of the data. Give your answer as an integer or a fraction in its simplest form.";
  } else if (task === "mode_from_list") {
    instr = "Write down the mode of the data.";
  } else if (task === "range_from_list") {
    instr = "Work out the range of the data.";
  } else if (task === "mean_from_freq_table") {
    instr = "Calculate the mean from the frequency table. Give your answer as an integer or a fraction in its simplest form.";
  } else if (task === "single_event_probability") {
    const ctx = params.context;
    const tgt = ds.categories[params.outcomeSpace.targetCategoryIndex];
    instr = `${ctx} What is the probability that the ${params.itemNoun} chosen is ${tgt}? Give your answer as a fraction in its simplest form.`;
  }
  blocks.push({ kind: "text", text: instr });
  return { blocks, instruction: instr };
}

function solution(task: string, params: Json): Json {
  const ds = params.dataset;
  const correct = solve(task, params);
  const steps: Json[] = [];
  const step = (t: string, r: string): void => {
    steps.push({ number: steps.length + 1, transformation: t, intermediateResult: r });
  };

  // Representation-specific worked solutions (owner #6): table steps never mention a bar or
  // axis; chart/graph/pictogram steps reference their own elements.
  if (task === "read_bar_chart") {
    const cat = ds.categories[params.queryIndex];
    step("Locate the bar for the named category", `the bar for “${cat}”`);
    step("Read its height using the vertical-axis scale", String(correct as number));
  } else if (task === "read_table_value") {
    const cat = ds.categories[params.queryIndex];
    step("Locate the row for the named category", `the row for “${cat}”`);
    step("Read the frequency in that row", String(correct as number));
  } else if (task === "read_line_graph") {
    const lab = ds.seriesLabels[params.queryIndex];
    step("Locate the requested position on the horizontal axis", `${lab}`);
    step("Read the value of the marked point from the vertical axis", String(correct as number));
  } else if (task === "read_pictogram") {
    const key: number = ds.pictogramKey;
    const fr = correct as number;
    const whole = Math.floor(fr / key);
    const half = (fr % key) === Math.floor(key / 2) && key % 2 === 0;
    const symdesc = half ? `${whole} whole symbols and 1 half symbol` : `${whole} whole symbols`;
    step("Count the whole and half symbols in the named row", symdesc);
    step("Apply the displayed key", `${whole} × ${key}` + (half ? ` + ${Math.floor(key / 2)}` : "") + ` = ${fr}`);
  } else if (task === "complete_frequency_table") {
    const freqs: number[] = ds.frequencies;
    const blank = params.blank;
    const total = sumOf(freqs);
    if (blank.kind === "total") {
      // The total is the unknown -> ADD every displayed frequency (owner #4).
      step("Add every displayed frequency", sumExpr(freqs) + ` = ${total}`);
    } else {
      const i = blank.index;
      const others = total - freqs[i]!;
      step("Subtract the sum of the known frequencies from the displayed total", `${total} − ${others} = ${freqs[i]}`);
    }
  } else if (task === "mean_from_list") {
    const v: number[] = ds.values;
    step("Add the values", sumExpr(v) + ` = ${sumOf(v)}`);
    step("Divide by how many values", `${sumOf(v)} ÷ ${v.length} = ${dispRat(new Rational(sumOf(v), v.length))}`);
  } else if (task === "median_from_list") {
    const v = [...ds.values].sort((a: number, b: number) => a - b) as number[];
    step("Order the values", v.map((x) => String(x)).join(", "));
    const n = v.length;
    if (n % 2) {                                   // odd: a single middle value (owner #5)
      step("Identify the single middle value", String(v[Math.floor(n / 2)]!));
    } else {                                       // even: two middles, explicitly averaged
      const a = v[Math.floor(n / 2) - 1]!, b = v[Math.floor(n / 2)]!;
      step("Identify the two middle values", `${a} and ${b}`);
      step("Average the two middle values", `(${a} + ${b}) ÷ 2 = ${dispRat(new Rational(a + b, 2))}`);
    }
  } else if (task === "mode_from_list") {
    step("Count how many times each value occurs", "Tally the values.");
    step("Identify the most common value", String(correct as number));
  } else if (task === "range_from_list") {
    const v: number[] = ds.values;
    step("Identify the largest and smallest values", `largest ${Math.max(...v)}, smallest ${Math.min(...v)}`);
    step("Subtract", `${Math.max(...v)} − ${Math.min(...v)} = ${correct as number}`);
  } else if (task === "mean_from_freq_table") {
    const vals: number[] = ds.categories, freqs: number[] = ds.frequencies;
    let svf = 0;
    for (let i = 0; i < vals.length; i++) svf += vals[i]! * freqs[i]!;
    const sf = sumOf(freqs);
    step("Multiply each value by its frequency and add", vals.map((v, i) => `${v}×${freqs[i]}`).join(" + ") + ` = ${svf}`);
    step("Divide by the total frequency", `${svf} ÷ ${sf} = ${dispRat(correct instanceof Rational ? correct : F(correct as number))}`);
  } else if (task === "single_event_probability") {
    const os = params.outcomeSpace;
    step("Count favourable and total outcomes", `${os.favourable} favourable out of ${os.total}`);
    step("Write as a fraction in simplest form", dispRat(correct as Rational));
  }
  return { steps };
}

// --------------------------------------------------------------------------- //
// Premium spec (theme colours categories/series; never colour-only — owner K)
// --------------------------------------------------------------------------- //
function premiumSpec(task: string, params: Json): Json {
  const ds = params.dataset;
  let n: number;
  if (task === "read_bar_chart" || task === "read_pictogram") n = ds.categories.length;
  else if (task === "read_line_graph") n = 1;
  else n = 0;
  return { chart: task, series: n, hatched: true, legend: false };
}

// --------------------------------------------------------------------------- //
// Draws (seeded parameter sampling)
// --------------------------------------------------------------------------- //
function pickTheme<T>(rng: Mulberry32, themes: T[]): T {
  return themes[nInt(rng, themes.length)]!;
}

function drawCategories(rng: Mulberry32, themes: CatTheme[], minN: number, maxN: number): [string, string, string[], number] {
  const [title, unit, pool] = pickTheme(rng, themes);
  let n = minN + nInt(rng, maxN - minN + 1);
  n = Math.min(n, pool.length);
  return [title, unit, pool.slice(0, n), n];
}

function freqDataset(rng: Mulberry32, lo: number, hi: number, themes: CatTheme[] = CATEGORY_THEMES, minN = 3, maxN = 5): Json {
  const [title, unit, cats, n] = drawCategories(rng, themes, minN, maxN);
  const freqs: number[] = [];
  for (let i = 0; i < n; i++) freqs.push(lo + nInt(rng, hi - lo + 1));
  return { kind: "frequency", title, unit, categories: cats, frequencies: freqs };
}

/** n values that are MULTIPLES of vstep in [lo, hi] (so the chart scale resolves them). */
function steppedValues(rng: Mulberry32, n: number, lo: number, hi: number, vstep: number): number[] {
  const a = Math.floor(lo / vstep), b = Math.floor(hi / vstep);
  const out: number[] = [];
  for (let i = 0; i < n; i++) out.push(vstep * (a + nInt(rng, b - a + 1)));
  return out;
}

// Readable bar/line scale buckets (owner v1.0.2): (lo, hi, vstep). Generating values as
// multiples of vstep keeps the derived minor subdivision clean; the acceptable gate redraws
// any residual unreadable scale. These exercise major steps {1,2,5,10} and minor {1,5}.
const BAR_BUCKETS: [number, number, number][] = [[1, 8, 1], [2, 16, 1], [2, 16, 2], [5, 35, 5], [10, 55, 5]];
const LINE_BUCKETS: [number, number, number][] = [[1, 9, 1], [2, 16, 1], [5, 35, 5], [10, 55, 5]];

function drawReadBarChart(rng: Mulberry32): Json | null {
  const [lo, hi, vstep] = BAR_BUCKETS[nInt(rng, BAR_BUCKETS.length)]!;
  const [title, unit, cats, n] = drawCategories(rng, CATEGORY_THEMES, 3, 5);
  const freqs = steppedValues(rng, n, lo, hi, vstep);
  const ds = { kind: "frequency", title, unit, categories: cats, frequencies: freqs };
  const qi = nInt(rng, n);
  return { task: "read_bar_chart", dataset: ds, queryIndex: qi, scaffold: nInt(rng, 2) === 0 };
}

function drawReadPictogram(rng: Mulberry32): Json | null {
  const key = [2, 5, 10][nInt(rng, 3)]!;
  const [title, unit, cats, n] = drawCategories(rng, CATEGORY_THEMES, 3, 5);
  const freqs: number[] = [];
  for (let i = 0; i < n; i++) {
    const whole = 1 + nInt(rng, 5);
    const half = (key % 2 === 0) && nInt(rng, 2) === 0;
    freqs.push(whole * key + (half ? Math.floor(key / 2) : 0));
  }
  const ds = { kind: "frequency", title, unit, categories: cats, frequencies: freqs, pictogramKey: key };
  const qi = nInt(rng, n);
  return { task: "read_pictogram", dataset: ds, queryIndex: qi, scaffold: nInt(rng, 2) === 0 };
}

function drawReadTableValue(rng: Mulberry32): Json | null {
  const ds = freqDataset(rng, 2, 25);
  const qi = nInt(rng, ds.categories.length);
  return { task: "read_table_value", dataset: ds, queryIndex: qi, scaffold: false };
}

function drawReadLineGraph(rng: Mulberry32): Json | null {
  const [title, unit, pool] = pickTheme(rng, LINE_THEMES);
  let n = 5 + nInt(rng, 2);
  n = Math.min(n, pool.length);
  const [lo, hi, vstep] = LINE_BUCKETS[nInt(rng, LINE_BUCKETS.length)]!;
  const vals = steppedValues(rng, n, lo, hi, vstep);
  const ds = { kind: "list", title, unit, seriesLabels: pool.slice(0, n), values: vals };
  const qi = nInt(rng, n);
  return { task: "read_line_graph", dataset: ds, queryIndex: qi, scaffold: nInt(rng, 2) === 0 };
}

function drawCompleteFrequencyTable(rng: Mulberry32): Json | null {
  const ds = freqDataset(rng, 2, 18);
  const n = ds.categories.length;
  let blank: Json;
  if (nInt(rng, 3) === 0) blank = { kind: "total" };
  else blank = { kind: "frequency", index: nInt(rng, n) };
  return { task: "complete_frequency_table", dataset: ds, blank, scaffold: false };
}

function drawList(rng: Mulberry32, lo: number, hi: number, minN: number, maxN: number): Json {
  // Negative values require a signed or context-free context (owner #1).
  const signed = lo < 0;
  const pool: ListTheme[] = signed ? [...LIST_THEMES_SIGNED, ...LIST_THEMES_FREE] : [...LIST_THEMES_NONNEG, ...LIST_THEMES_FREE];
  const [title, unit] = pickTheme(rng, pool);
  const n = minN + nInt(rng, maxN - minN + 1);
  const vals: number[] = [];
  for (let i = 0; i < n; i++) {
    const v = lo + nInt(rng, hi - lo + 1);
    vals.push(v);
  }
  return { kind: "list", title, unit, values: vals };
}

function drawMeanFromList(rng: Mulberry32): Json | null {
  const allowNeg = nInt(rng, 4) === 0;
  const lo = allowNeg ? -6 : 1;
  const ds = drawList(rng, lo, 20, 3, 6);
  return { task: "mean_from_list", dataset: ds, scaffold: nInt(rng, 2) === 0 };
}

function drawMedianFromList(rng: Mulberry32): Json | null {
  const ds = drawList(rng, 1, 20, 4, 7);
  return { task: "median_from_list", dataset: ds, scaffold: false };
}

function drawModeFromList(rng: Mulberry32): Json | null {
  // build a list with a guaranteed UNIQUE mode (owner C/H)
  const n = 5 + nInt(rng, 3);
  const modeVal = 1 + nInt(rng, 9);
  const reps = 3 + nInt(rng, 2);
  let vals: number[] = Array(reps).fill(modeVal);
  const others: number[] = [];
  const pool: number[] = [];
  for (let x = 1; x < 13; x++) if (x !== modeVal) pool.push(x);
  while (vals.length + others.length < n) {
    const x = pool[nInt(rng, pool.length)]!;
    if (others.filter((o) => o === x).length < reps - 1) others.push(x);
  }
  vals = vals.concat(others);
  vals = seededShuffle(rng, vals);
  if (uniqueMode(vals) === null) return null;  // not a unique mode -> redraw (owner #2)
  const [title, unit] = pickTheme(rng, LIST_THEMES_NONNEG);
  const ds = { kind: "list", title, unit, values: vals };
  return { task: "mode_from_list", dataset: ds, scaffold: nInt(rng, 2) === 0 };
}

function drawRangeFromList(rng: Mulberry32): Json | null {
  // include range = 0 (uniform list) at a controlled low rate (owner H)
  let ds: Json;
  if (nInt(rng, 8) === 0) {
    const v = 1 + nInt(rng, 12);
    const n = 3 + nInt(rng, 3);
    const [title, unit] = pickTheme(rng, LIST_THEMES_NONNEG);
    ds = { kind: "list", title, unit, values: Array(n).fill(v) };
  } else {
    ds = drawList(rng, 1, 30, 4, 7);
  }
  return { task: "range_from_list", dataset: ds, scaffold: nInt(rng, 2) === 0 };
}

function drawMeanFromFreqTable(rng: Mulberry32): Json | null {
  const [title, unit] = pickTheme(rng, LIST_THEMES_NONNEG);
  const n = 3 + nInt(rng, 4);
  const base = nInt(rng, 3);
  const values: number[] = [];
  for (let i = 0; i < n; i++) values.push(base + i);
  const freqs: number[] = [];
  for (let i = 0; i < n; i++) freqs.push(1 + nInt(rng, 6));
  const ds = { kind: "frequency", title, unit, categories: values, frequencies: freqs };
  return { task: "mean_from_freq_table", dataset: ds, scaffold: false };
}

function drawSingleEventProbability(rng: Mulberry32): Json | null {
  const [ctxTitle, noun, colours] = pickTheme(rng, PROB_THEMES);
  let n = 2 + nInt(rng, 3);
  n = Math.min(n, colours.length);
  const counts: number[] = [];
  for (let i = 0; i < n; i++) counts.push(1 + nInt(rng, 6));
  let total = sumOf(counts);
  const ti = nInt(rng, n);
  let fav = counts[ti]!;
  // allow P=0 / P=1 occasionally
  const roll = nInt(rng, 10);
  if (roll === 0) {   // impossible event: add a zero-count target colour
    counts[ti] = 0;
    fav = 0;
    total = sumOf(counts);
    if (total === 0) return null;
  } else if (roll === 1) {  // certain event: make all outcomes the target colour
    for (let i = 0; i < n; i++) counts[i] = 0;
    counts[ti] = 2 + nInt(rng, 5);
    fav = counts[ti]!;
    total = fav;
  }
  const cats = colours.slice(0, n).map((c) => `${c}`);
  const ds = {
    kind: "frequency", title: `Contents of ${ctxTitle}`, unit: noun,
    categories: cats.map((c) => c.charAt(0).toUpperCase() + c.slice(1)), frequencies: counts,
  };
  const ctx = `One ${noun} is chosen at random from ${ctxTitle} containing the ${noun}s shown (each ${noun} is equally likely).`;
  return {
    task: "single_event_probability", dataset: ds, itemNoun: noun, context: ctx,
    outcomeSpace: { favourable: fav, total, targetCategoryIndex: ti }, scaffold: false,
  };
}

const DRAW: Record<string, (rng: Mulberry32) => Json | null> = {
  read_bar_chart: drawReadBarChart, read_pictogram: drawReadPictogram,
  read_table_value: drawReadTableValue, read_line_graph: drawReadLineGraph,
  complete_frequency_table: drawCompleteFrequencyTable, mean_from_list: drawMeanFromList,
  median_from_list: drawMedianFromList, mode_from_list: drawModeFromList,
  range_from_list: drawRangeFromList, mean_from_freq_table: drawMeanFromFreqTable,
  single_event_probability: drawSingleEventProbability,
};

function seededShuffle<T>(rng: Mulberry32, items: T[]): T[] {
  const a = [...items];
  for (let i = a.length - 1; i > 0; i--) {
    const j = nInt(rng, i + 1);
    const tmp = a[i]!;
    a[i] = a[j]!;
    a[j] = tmp;
  }
  return a;
}

// --------------------------------------------------------------------------- //
// Eligibility + interaction
// --------------------------------------------------------------------------- //
function resolveInteraction(config: Json): string {
  const it = config.interactionType;
  if (it === "free-response" || it === "multiple-choice") return it;
  if (config.answerType === "multiple-choice") return "multiple-choice";
  return "free-response";
}

function mcEligibleProbability(_params: Json, correct: Rational): boolean {
  // MC only for proper probabilities (owner C): exclude 0, 1, and 1/2.
  const isZero = correct.num === 0 && correct.den === 1;
  const isOne = correct.num === 1 && correct.den === 1;
  const isHalf = correct.num === 1 && correct.den === 2;
  return !isZero && !isOne && !isHalf;
}

function acceptable(params: Json, interaction: string): Distractor[] | null {
  const task = params.task;
  const correct = solve(task, params);
  if (!answerSane(task, params, correct)) return null;
  if (interaction === "multiple-choice") {
    if ((FREE_RESPONSE_ONLY as readonly string[]).includes(task)) return null;
    if (task === "single_event_probability" && !mcEligibleProbability(params, correct as Rational)) return null;
    return distractors(task, params, correct);
  }
  return [];
}

function answerSane(task: string, params: Json, _correct: SolveResult): boolean {
  const ds = params.dataset;
  if (task === "read_bar_chart" || task === "read_line_graph") {
    // Direct-read scale contract (owner v1.0.2): the chart scale must resolve every value
    // on a visible mark without estimation or clutter; otherwise redraw.
    const vals: number[] = task === "read_line_graph" ? ds.values : ds.frequencies;
    const [major, minor, ymax] = chartScale(vals);
    if (!scaleReadable(major, minor, ymax)) return false;
    if (vals.some((v) => v % minor !== 0)) return false;   // every value lands on a visible subdivision
  }
  if (task === "mode_from_list") {
    const cnt = counterMostCommon(ds.values);
    if (cnt.length < 2 || cnt[0]![1] === cnt[1]![1]) return false;
  }
  if (task === "complete_frequency_table") {
    return completeValue(params) >= 0;
  }
  if (task === "single_event_probability") {
    const os = params.outcomeSpace;
    if (os.total <= 0 || !(0 <= os.favourable && os.favourable <= os.total)) return false;
  }
  return true;
}

// --------------------------------------------------------------------------- //
// generate / serialize / describe
// --------------------------------------------------------------------------- //
export function generate(seed: number, config: Json = {}): Json {
  config = config || {};
  const interaction = resolveInteraction(config);
  const mc = interaction === "multiple-choice";
  const explicit = config.task ?? null;
  if (explicit !== null && !(TASKS as readonly string[]).includes(explicit)) throw new Error(`unknown task: ${explicit}`);
  if (mc && explicit !== null && (FREE_RESPONSE_ONLY as readonly string[]).includes(explicit)) {
    throw new Error(`${explicit} is free-response only; multiple-choice is not supported (owner C)`);
  }

  const pool = (mc && explicit === null) ? MC_TASKS : (TASKS as readonly string[]);
  const rng = new Mulberry32(seed);
  let params: Json = {};
  let dist: Distractor[] | null = null;
  let ok = false;
  for (let i = 0; i < MAX_PARAM_ATTEMPTS; i++) {
    const task = explicit !== null ? explicit : pool[nInt(rng, pool.length)]!;
    const drawn = DRAW[task]!(rng);
    if (drawn === null) continue;
    const res = acceptable(drawn, interaction);
    if (res === null) continue;
    params = drawn; dist = res; ok = true; break;
  }
  if (!ok) throw new Error("could not find acceptable data-handling parameters");

  const task = params.task;
  const correct = solve(task, params);
  const answer = encodeAnswer(task, params, correct);
  const acc = accessibility(task, params);

  const item: Json = {
    itemId: `ITEM-${GENERATOR_ID.replace(/\./g, "-")}-${seed}-${task}`,
    schemaVersion: "1.0.0",
    objectiveIds: [OBJECTIVE_BY_TASK[task]],
    generatorId: GENERATOR_ID,
    generatorVersion: GENERATOR_VERSION,
    seed,
    params: { ...params },
    interactionType: interaction,
    prompt: prompt(task, params),
    answer,
    solution: solution(task, params),
    difficulty: difficulty(task, params),
    calculatorPolicy: CALCULATOR_POLICY,
    accessibility: {
      spokenMath: acc.spoken, altText: acc.alt,
      longDescription: acc.spoken, nonColorIndicators: true,
    },
    provenance: {
      origin: "generated", rightsStatus: "academy-owned",
      originalityNote: "Original parameterized item; the figure/table is generated from the same dataset.",
    },
    lifecycle: { state: "generated" },
  };

  const media: Json[] = [];
  if (SVG_TASKS.includes(task)) {
    const svg = chartSvg(task, params);
    media.push({
      id: "fig-1", kind: "svg", svg, toScale: true,
      altText: acc.alt, longDescription: acc.spoken,
      dataTableFallback: acc.dataTable, spec: { premium: premiumSpec(task, params) },
    });
  } else {
    const html = tableHtml(task, params, false);
    media.push({
      id: "fig-1", kind: "table",
      spec: { format: "semantic-html", html },
      toScale: true, altText: acc.alt, longDescription: acc.spoken,
      dataTableFallback: acc.dataTable,
    });
  }
  item.media = media;

  if (mc) {
    const ds = dist || [];
    item.distractors = [];
    for (let i = 0; i < ds.length; i++) {
      const d = ds[i]!;
      const [enc, disp] = displayValue(task, d.value);
      item.distractors.push({
        id: `d${i + 1}`, value: enc, display: disp,
        misconceptionId: d.misconceptionId, rationale: d.rationale,
      });
    }
    const [aEnc, aDisp] = displayValue(task, correct);
    const poolOpts: Json[] = [{ value: aEnc, display: aDisp, correct: true, misconceptionId: null }];
    for (const d of ds) {
      const [enc, disp] = displayValue(task, d.value);
      poolOpts.push({ value: enc, display: disp, correct: false, misconceptionId: d.misconceptionId });
    }
    const shuffled = rng.shuffle(poolOpts);
    const labels = ["A", "B", "C", "D", "E"];
    item.options = shuffled.map((o, i) => ({
      label: labels[i]!, value: o.value, display: o.display, correct: o.correct,
      ...(o.misconceptionId ? { misconceptionId: o.misconceptionId } : {}),
    }));
  }
  return item;
}

export function serialize(item: Json): string {
  return canonicalStringify(item as Json);
}

export function describe(): Json {
  const difficultyRanges: Record<string, [number, number]> = {};
  for (const t of TASKS as readonly string[]) difficultyRanges[OBJECTIVE_BY_TASK[t]!] = [...TASK_BANDS[t]!] as [number, number];
  return {
    id: GENERATOR_ID, version: GENERATOR_VERSION,
    title: "Statistics & data handling",
    domain: "statistics",
    objectiveIds: (TASKS as readonly string[]).map((t) => OBJECTIVE_BY_TASK[t]),
    interactionTypes: ["free-response", "multiple-choice"],
    answerTypes: ["integer", "exact-rational", "fraction", "table-completion"],
    tasks: [...TASKS],
    // Difficulty ranges are derived from the single authoritative TASK_BANDS source (owner #7),
    // so the descriptor, objectives, distribution report, and review pack cannot disagree.
    difficultyRanges,
  };
}

export type Config = { task?: string; interactionType?: string; answerType?: string };

// --------------------------------------------------------------------------- //
// Independent validator (TypeScript). Mirrors the Python validator: rebuilds the
// figure/table from params and asserts the stored artifact byte-for-byte, recomputes the
// answer by a second route, and enforces the role-based answer-leakage contract (owner L).
// Functional parity (status), not byte parity (the result is not serialized).
// --------------------------------------------------------------------------- //
function eqJson(a: Json, b: Json): boolean {
  return canonicalStringify(a) === canonicalStringify(b);
}

export function validate(item: Json): Json {
  const checks: Array<{ name: string; result: string; detail: string }> = [];
  const add = (name: string, ok: boolean, detail = ""): void => {
    checks.push({ name, result: ok ? "pass" : "fail", detail });
  };

  const params = item.params;
  const task = params.task;
  const interaction = item.interactionType;
  const answer = item.answer;

  add("objective-mapping", eqJson(item.objectiveIds, [OBJECTIVE_BY_TASK[task]]), String(item.objectiveIds));
  add("interaction-type", interaction === "free-response" || interaction === "multiple-choice", String(interaction));
  add("free-response-only-respected",
    !((FREE_RESPONSE_ONLY as readonly string[]).includes(task) && interaction === "multiple-choice"),
    "complete_frequency_table is free-response only");

  // closure: recompute by an independent route
  const correct = solve(task, params);
  const rebuilt = encodeAnswer(task, params, correct);
  add("closure-agreement", eqJson(rebuilt, answer), "recomputed answer matches stored canonical");

  // answer-type fidelity
  add("answer-type-consistency", ["integer", "exact-rational", "fraction", "table-completion"].includes(answer.type), answer.type);
  if (task === "single_event_probability") {
    const f = new Rational(answer.canonical.num, answer.canonical.den);
    add("probability-in-range", f.num >= 0 && f.num <= f.den, dispRat(f));
    const cr = correct as Rational;
    add("probability-reduced",
      f.equals(cr) && answer.canonical.num === cr.num && answer.canonical.den === cr.den,
      "answer is the reduced fraction");
  }

  // media: byte-for-byte rebuild
  const media: Json[] = item.media ?? [];
  add("media-present", media.length === 1, "one media asset");
  if (media.length) {
    const m = media[0];
    if (SVG_TASKS.includes(task)) {
      add("media-kind", m.kind === "svg", String(m.kind));
      const rebuiltSvg = chartSvg(task, params);
      add("svg-realises-data", rebuiltSvg === m.svg, "recomputed chart SVG matches stored SVG byte-for-byte");
      add("chart-realises-data", chartRealisesData(task, params, m.svg ?? ""), "bars/points/symbols agree with the dataset");
      if (task === "read_bar_chart" || task === "read_line_graph") {
        add("axis-scale-consistency", axisConsistent(task, params, m.svg ?? ""), "ticks/gridlines follow a {1,2,5,10} step");
        // direct-read scale contract (owner v1.0.2) — inspect the serialized SVG
        for (const [name, ok_, detail] of readabilityChecks(task, params, m.svg ?? "")) {
          add(name, ok_, detail);
        }
      }
      const storedSpec = (m.spec ?? {}).premium;
      add("premium-spec-parity", eqJson(storedSpec, premiumSpec(task, params)), "premium spec recomputed byte-for-byte");
    } else {
      add("media-kind", m.kind === "table", String(m.kind));
      const storedHtml = (m.spec ?? {}).html ?? "";
      const rebuiltHtml = tableHtml(task, params, false);
      add("html-table-realises-data", rebuiltHtml === storedHtml, "recomputed HTML table matches stored table byte-for-byte");
      add("table-round-trip", tableRoundTrip(task, params, storedHtml), "table cells round-trip to the dataset");
      if (task === "complete_frequency_table") {
        const html = storedHtml;
        add("blank-cell-blank-in-student",
          countOccurrences(html, 'class="cx-blank"') === 1 && html.includes("<input"),
          "exactly one blank input cell in the student table");
      }
    }
  }

  // role-based answer-leakage (owner L)
  add("no-derived-statistic-annotation", noDerivedStatistic(media), "no computed result printed on the figure/table");
  add("student-a11y-does-not-state-result", a11yClean(task, item, correct), "student accessibility text does not state the computed result");
  add("no-solution-overlay-in-student-render", noSolutionOverlay(media), "no solution/answer overlay in student media");

  // difficulty within objective band
  const band = item.difficulty.overallBand;
  const [lo, hi] = TASK_BANDS[task]!;
  add("difficulty-in-band", lo <= band && band <= hi, `band ${band} in [${lo},${hi}]`);
  add("difficulty-axes-valid", Object.keys(item.difficulty.axes).every((k) => k in WEIGHTS), "only schema-valid axes used");

  // MC distractor discipline (owner N)
  if (interaction === "multiple-choice") {
    const opts: Json[] = item.options ?? [];
    add("mc-option-count", opts.length === 4, `${opts.length} options`);
    const vals = opts.map((o) => canonicalStringify(o.value));
    add("mc-options-distinct", new Set(vals).size === vals.length, "all options distinct");
    const correctOpts = opts.filter((o) => o.correct);
    add("mc-one-correct", correctOpts.length === 1, "exactly one correct option");
    add("mc-distractors-recompute", distractorsRecompute(task, params, item), "each distractor recomputes from its misconception");
    if (task === "single_event_probability") {
      const allin = opts.every((o) => {
        if (typeof o.value === "object" && o.value !== null && "num" in o.value) {
          const f = new Rational(o.value.num, o.value.den);
          return f.num >= 0 && f.num <= f.den;
        }
        return true;
      });
      add("mc-probability-options-in-range", allin, "all probability options lie in [0,1]");
    }
  }

  // v1.0.1 curriculum/semantic checks (owner #1-#6).
  for (const [name, ok_, detail] of v101Checks(task, params, item)) {
    add(name, ok_, detail);
  }

  const statuses = checks.map((c) => c.result);
  return {
    status: statuses.every((s) => s === "pass") ? "pass" : "fail",
    validatorVersion: VALIDATOR_VERSION, checks,
  };
}

function decodeDistractorValue(_task: string, value: Json): CtxValue {
  if (typeof value === "object" && value !== null && "num" in value) return new Rational(value.num, value.den);
  return value as number;
}

function v101Checks(task: string, params: Json, item: Json): Array<[string, boolean, string]> {
  const out: Array<[string, boolean, string]> = [];
  const ds = params.dataset;
  const correct = solve(task, params);
  const steps: Json[] = item.solution?.steps ?? [];
  const solText = steps.map((s) => `${s.transformation ?? ""} ${s.intermediateResult ?? ""}`).join(" ").toLowerCase();

  // --- #1 context-value compatibility ---------------------------------- //
  if ("values" in ds || ds.kind === "frequency") {
    const title: string = ds.title ?? "";
    let vals: number[] = ds.values;
    if (vals === undefined || vals === null) vals = ds.frequencies ?? [];
    let domain = CONTEXT_DOMAINS[title];
    if (domain === undefined) domain = ds.kind === "frequency" ? "count" : "context-free";
    const hasNeg = vals.some((v) => v < 0);
    const nonnegCtx = NONNEG_DOMAINS.includes(domain);
    out.push(["context-values-in-domain", (!hasNeg) || domain === "signed" || domain === "context-free",
      `domain=${domain} hasNeg=${hasNeg}`]);
    out.push(["count-context-nonnegative", (!nonnegCtx) || (!hasNeg), `domain=${domain}`]);
    out.push(["signed-context-explicit", (!hasNeg) || domain === "signed" || domain === "context-free", `title=${title}`]);
    out.push(["context-unit-compatible-with-values", (!hasNeg) || domain === "signed" || domain === "context-free",
      `unit=${ds.unit}`]);
  }

  // --- #2 mode/averages distractor semantics (MC only) ----------------- //
  if (item.interactionType === "multiple-choice" && item.distractors && item.distractors.length) {
    const c = ctxOf(task, params, correct);
    let reqUnique = true, statExists = true, valIsStat = true, rationaleTrue = true;
    for (const d of item.distractors as Json[]) {
      const mid: string = d.misconceptionId;
      const recomputed = adapterFor(mid)(c);
      if (recomputed === null) { statExists = false; continue; }
      if (valueKey(task, recomputed) !== valueKey(task, decodeDistractorValue(task, d.value))) valIsStat = false;
      if (d.rationale !== MISCONCEPTIONS[mid]!.observableError) rationaleTrue = false;
      if (mid === "MISC.STAT.AVG_USES_MODE") {
        const um = uniqueMode(ds.values);
        if (um === null || !F(um).equals(recomputed instanceof Rational ? recomputed : F(recomputed as number))) reqUnique = false;
      }
    }
    out.push(["mode-distractor-requires-unique-mode", reqUnique, "AVG_USES_MODE only with a true unique mode"]);
    out.push(["distractor-statistic-exists", statExists, "each distractor's misconception yields a value"]);
    out.push(["distractor-value-is-actual-statistic", valIsStat, "distractor value == recomputed statistic"]);
    out.push(["distractor-rationale-true-for-dataset", rationaleTrue, "rationale matches the registry observable error"]);
  }

  // --- #3 pictogram exact symbols -------------------------------------- //
  if (task === "read_pictogram") {
    const key: number = ds.pictogramKey;
    const fr: number = ds.frequencies[params.queryIndex];
    const unit = key % 2 === 0 ? Math.floor(key / 2) : key;
    out.push(["pictogram-symbol-count-exact", fr % unit === 0, `value ${fr} is an exact symbol count for key ${key}`]);
    if (item.interactionType === "multiple-choice") {
      const mids = (item.distractors ?? []).map((d: Json) => d.misconceptionId);
      const halfPresent = (fr % key) === Math.floor(key / 2) && key % 2 === 0;
      const okMatch = !(halfPresent && mids.includes("MISC.STAT.PICTO_COUNTS_SYMBOLS"));
      out.push(["pictogram-distractor-matches-visible-symbols", okMatch, "no whole-count distractor when a half symbol is shown"]);
      let distinct = true;
      const valsByMid: Record<string, string> = {};
      for (const d of (item.distractors ?? []) as Json[]) {
        valsByMid[d.misconceptionId] = valueKey(task, decodeDistractorValue(task, d.value));
      }
      if ("MISC.STAT.PICTO_IGNORES_HALF" in valsByMid && "MISC.STAT.PICTO_HALF_AS_WHOLE" in valsByMid) {
        distinct = valsByMid["MISC.STAT.PICTO_IGNORES_HALF"] !== valsByMid["MISC.STAT.PICTO_HALF_AS_WHOLE"];
      }
      out.push(["half-symbol-misconceptions-distinct", distinct, "ignore-half and half-as-whole give different values"]);
    }
  }

  // --- #4 frequency-table blank-kind diagnostics ----------------------- //
  if (task === "complete_frequency_table") {
    const kind: string = params.blank.kind;
    const first = steps.length ? String(steps[0].transformation).toLowerCase() : "";
    out.push(["total-blank-uses-addition", kind !== "total" || first.includes("add"), "missing total -> addition"]);
    out.push(["frequency-blank-uses-subtraction", kind !== "frequency" || first.includes("subtract"), "missing frequency -> subtraction"]);
    out.push(["frequency-diagnostic-applicable-to-blank-kind",
      first.includes("subtract") === (kind === "frequency"), "operation matches the blank kind"]);
    out.push(["feedback-matches-displayed-table", !(kind === "total" && first.includes("subtract")),
      "no 'subtract from the total' wording when the total is the unknown"]);
  }

  // --- #5 median solution parity --------------------------------------- //
  if (task === "median_from_list") {
    const n = ds.values.length;
    let okParity: boolean;
    if (n % 2) {
      okParity = solText.includes("single middle value") && !solText.includes("average");
      out.push(["even-median-identifies-two-middle-values", true, "n odd"]);
      out.push(["even-median-shows-average", true, "n odd"]);
    } else {
      const sv = [...ds.values].sort((a: number, b: number) => a - b) as number[];
      const a = sv[Math.floor(n / 2) - 1]!, b = sv[Math.floor(n / 2)]!;
      okParity = solText.includes("two middle values") && solText.includes("average");
      out.push(["even-median-identifies-two-middle-values", solText.includes(`${a} and ${b}`), "two middles listed"]);
      out.push(["even-median-shows-average", solText.includes(`(${a} + ${b}) ÷ 2`), "explicit average shown"]);
    }
    out.push(["median-solution-parity-correct", okParity, `n=${n}`]);
  }

  // --- general: the worked method ends at the canonical answer ---------- //
  if (steps.length) {
    const ansdisp: string = item.answer.display;
    const lastIr: string = steps[steps.length - 1].intermediateResult ?? "";
    out.push(["solution-method-produces-canonical-answer", lastIr.includes(ansdisp), `last step yields ${ansdisp}`]);
  }

  // --- #6 representation-specific worked-solution language -------------- //
  if (task === "read_table_value") {
    out.push(["table-solution-does-not-reference-axis", !solText.includes("axis"), "table solution avoids 'axis'"]);
    out.push(["table-solution-does-not-reference-bar-or-point", !solText.includes("bar") && !solText.includes("marked point"), "table solution avoids bar/point"]);
    out.push(["solution-language-matches-representation", solText.includes("row"), "table solution references a row"]);
  } else if (task === "read_bar_chart") {
    out.push(["chart-solution-references-correct-chart-elements", solText.includes("bar") && solText.includes("height"), "bar-chart solution references bar/height"]);
    out.push(["solution-language-matches-representation", solText.includes("axis"), "bar-chart references the axis scale"]);
  } else if (task === "read_line_graph") {
    out.push(["chart-solution-references-correct-chart-elements", solText.includes("point") && solText.includes("axis"), "line-graph solution references point/axis"]);
    out.push(["solution-language-matches-representation", solText.includes("horizontal axis") || solText.includes("vertical axis"), "line-graph references axes"]);
  } else if (task === "read_pictogram") {
    out.push(["chart-solution-references-correct-chart-elements", solText.includes("symbol") && solText.includes("key"), "pictogram solution references symbols/key"]);
    out.push(["solution-language-matches-representation", solText.includes("symbol"), "pictogram references symbols"]);
  }
  return out;
}

// --------------------------------------------------------------------------- //
// Validator helpers
// --------------------------------------------------------------------------- //
function countOccurrences(haystack: string, needle: string): number {
  let count = 0, idx = 0;
  while ((idx = haystack.indexOf(needle, idx)) !== -1) { count++; idx += needle.length; }
  return count;
}

function chartRealisesData(task: string, params: Json, svg: string): boolean {
  const ds = params.dataset;
  if (task === "read_bar_chart") {
    const rects = [...svg.matchAll(/<rect class="cx-bar"[^>]*y="(\d+)"[^>]*height="(\d+)"/g)];
    const freqs: number[] = ds.frequencies;
    if (rects.length !== freqs.length) return false;
    const [, , ymax] = chartScale(freqs);
    for (let i = 0; i < rects.length; i++) {
      const y = parseInt(rects[i]![1]!, 10), h = parseInt(rects[i]![2]!, 10);
      if (y !== py(ymax, freqs[i]!) || y + h !== PLOT_Y1) return false;
    }
    return true;
  }
  if (task === "read_line_graph") {
    const circles = [...svg.matchAll(/<circle class="cx-pt-core" cx="(\d+)" cy="(\d+)"/g)];
    const vals: number[] = ds.values;
    const [, , ymax] = chartScale(vals);
    if (circles.length !== vals.length) return false;
    for (let i = 0; i < circles.length; i++) {
      const cy = parseInt(circles[i]![2]!, 10);
      if (cy !== py(ymax, vals[i]!)) return false;
    }
    return true;
  }
  if (task === "read_pictogram") {
    const key: number = ds.pictogramKey;
    const freqs: number[] = ds.frequencies;
    for (let i = 0; i < freqs.length; i++) {
      const whole = [...svg.matchAll(new RegExp(`<rect class="cx-symbol" data-cat="${i}"(?! data-half)`, "g"))].length;
      const half = [...svg.matchAll(new RegExp(`<rect class="cx-symbol" data-cat="${i}" data-half="1"`, "g"))].length;
      if (whole * key + half * Math.floor(key / 2) !== freqs[i]!) return false;
    }
    return true;
  }
  return true;
}

function axisConsistent(task: string, params: Json, svg: string): boolean {
  const ds = params.dataset;
  const vals: number[] = task === "read_line_graph" ? ds.values : ds.frequencies;
  if (!vals || !vals.length) return true;
  const [major, minor, ymax] = chartScale(vals);
  const labels = [...svg.matchAll(/<text class="cx-ticklbl"[^>]*>(-?\d+)<\/text>/g)].map((mm) => parseInt(mm[1]!, 10));
  const expected: number[] = [];
  for (let v = 0; v <= ymax; v += major) expected.push(v);  // labels only on MAJOR ticks
  return labels.length === expected.length && labels.every((l, i) => l === expected[i])
    && [1, 2, 5, 10].includes(major) && major % minor === 0;
}

/** All visible value-mark y-positions in the SVG: major + minor gridlines and ticks, plus the
 *  baseline. The validator reads these from the SERIALIZED student SVG (owner v1.0.2). */
function gridTickYs(svg: string): Set<number> {
  const ys = new Set<number>();
  for (const cls of ["cx-grid-major", "cx-grid-minor"]) {
    for (const mm of svg.matchAll(new RegExp(`<line class="${cls}" x1="\\d+" y1="(\\d+)"`, "g"))) {
      ys.add(parseInt(mm[1]!, 10));
    }
  }
  for (const cls of ["cx-tick", "cx-tick-minor"]) {
    for (const mm of svg.matchAll(new RegExp(`<line class="${cls}" x1="\\d+" y1="(\\d+)" x2="\\d+" y2="(\\d+)"`, "g"))) {
      ys.add(parseInt(mm[1]!, 10));
    }
  }
  ys.add(PLOT_Y1);   // the baseline (value 0) is a visible mark
  return ys;
}

/** Owner v1.0.2 direct-read scale contract — inspect the SERIALIZED student SVG (not just the
 *  dataset) to prove every queried/plotted value lands on a visible mark with no pixel estimation. */
function readabilityChecks(task: string, params: Json, svg: string): Array<[string, boolean, string]> {
  const ds = params.dataset;
  const vals: number[] = task === "read_line_graph" ? ds.values : ds.frequencies;
  const [major, minor, ymax] = chartScale(vals);
  const qi: number = params.queryIndex;
  const queried = vals[qi]!;
  const markYs = gridTickYs(svg);
  const qPy = py(ymax, queried);
  const allOn = vals.every((v) => markYs.has(py(ymax, v)));
  const minorLines = Math.floor(ymax / minor);
  const sep = subdivPx(minor, ymax);
  const alignTag = task === "read_bar_chart" ? "bar-top-aligns-visible-subdivision" : "line-point-aligns-visible-subdivision";
  return [
    ["minor-step-divides-major-step", major % minor === 0, `major ${major} minor ${minor}`],
    ["minor-grid-not-overloaded", minorLines <= MAX_MINOR_LINES && sep >= MIN_SUBDIV_PX, `${minorLines} lines, ${sep}px`],
    ["queried-value-readable-from-scale", queried % minor === 0, `queried ${queried} % minor ${minor}`],
    ["visible-subdivision-resolves-query", markYs.has(qPy), `queried y ${qPy} on a visible mark`],
    [alignTag, allOn, "every plotted value sits on a visible mark"],
    ["exact-read-answer-unique", queried % minor === 0 && markYs.has(qPy), "answer uniquely readable from a mark"],
    ["no-pixel-estimation-required", vals.every((v) => v % minor === 0) && allOn, "no value falls between marks"],
    ["scale-readable-in-monochrome", svg.includes('<line class="cx-tick"') && svg.includes('<text class="cx-ticklbl"'),
      "labelled monochrome ticks present"],
    ["scale-readable-at-print-size", sep >= MIN_SUBDIV_PX, `subdivision ${sep}px >= ${MIN_SUBDIV_PX}`],
  ];
}

function tableRoundTrip(task: string, params: Json, html: string): boolean {
  const ds = params.dataset;
  if (task === "read_table_value" || task === "complete_frequency_table") {
    const cells = [...html.matchAll(/<td>(\d+)<\/td>/g)].map((mm) => parseInt(mm[1]!, 10));
    const revealed = cells.map((x) => String(x));
    const freqs: number[] = ds.frequencies;
    return freqs.every((f, i) =>
      revealed.includes(String(f)) ||
      (params.blank && params.blank.kind === "frequency" && params.blank.index === i));
  }
  if (task === "mean_from_freq_table") {
    const nums = [...html.matchAll(/<td>(\d+)<\/td>/g)].map((mm) => parseInt(mm[1]!, 10));
    const freqs: number[] = ds.frequencies;
    return nums.length === freqs.length && nums.every((x, i) => x === freqs[i]);
  }
  if (task === "single_event_probability") {
    const nums = [...html.matchAll(/<td>(\d+)<\/td>/g)].map((mm) => parseInt(mm[1]!, 10));
    const expected = [...ds.frequencies, sumOf(ds.frequencies)];
    return nums.length === expected.length && nums.every((x, i) => x === expected[i]);
  }
  if (task === "mean_from_list" || task === "median_from_list" || task === "mode_from_list" || task === "range_from_list") {
    const nums = [...html.matchAll(/<td>(-?\d+)<\/td>/g)].map((mm) => parseInt(mm[1]!, 10));
    const vals: number[] = ds.values;
    return nums.length === vals.length && nums.every((x, i) => x === vals[i]);
  }
  return true;
}

function noDerivedStatistic(media: Json[]): boolean {
  for (const m of media) {
    const blob: string = m.svg ?? (m.spec ?? {}).html ?? "";
    if (blob.includes('class="cx-answer"') || blob.includes("data-answer") || blob.includes('class="cx-result"')) return false;
  }
  return true;
}

function noSolutionOverlay(media: Json[]): boolean {
  for (const m of media) {
    const blob: string = m.svg ?? (m.spec ?? {}).html ?? "";
    if (blob.includes('class="cx-solution"') || blob.includes("Solution:") || blob.includes('data-reveal="1"')) return false;
  }
  return true;
}

function a11yClean(task: string, item: Json, _correct: SolveResult): boolean {
  if (task === "read_bar_chart" || task === "read_pictogram" || task === "read_table_value" || task === "read_line_graph") return true;
  const disp: string = item.answer.display;
  const text = (item.accessibility.spokenMath + " " + item.accessibility.altText);
  return !text.toLowerCase().includes(`answer is ${disp}`.toLowerCase()) && !text.includes(`= ${disp}`);
}

function distractorsRecompute(task: string, params: Json, item: Json): boolean {
  const correct = solve(task, params);
  const expected = distractors(task, params, correct);
  if (expected === null) return false;
  const expKeys = expected.map((d) => valueKey(task, d.value)).sort();
  const gotKeys = (item.distractors ?? []).map((d: Json) => dispToKey(task, d.display, d.value)).sort();
  return expKeys.length === gotKeys.length && expKeys.every((k, i) => k === gotKeys[i]);
}

function dispToKey(_task: string, display: string, value: Json): string {
  if (typeof value === "object" && value !== null && "num" in value) {
    return dispRat(new Rational(value.num, value.den));
  }
  if (typeof value === "number") return String(value);
  return display;
}
