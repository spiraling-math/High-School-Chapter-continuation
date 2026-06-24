/**
 * gen.geometry.coordinate-lines v1.0.0 — TypeScript mirror.
 *
 * Byte-for-byte counterpart of oracle/spi_oracle/coordinate_lines.py: the same seeded
 * generation, exact-`Rational` mathematics, deterministic Cartesian renderer (equal x/y
 * unit scale, integer coordinates via a single gridRound projection of record, exact
 * line clipping), answer encodings, distractors, four-axis difficulty, accessibility,
 * premium spec, and independent validator. Parity is gated by the golden + 300-entry
 * parity fixtures (oracle/golden/coordinate_lines.*).
 */

import { Rational } from "../../core/exact-math/rational.ts";
import { Mulberry32 } from "../../core/seeded-random/mulberry32.ts";
import { bandFromScore, round3 } from "../../core/difficulty/band.ts";
import { canonicalStringify } from "../../core/serialization/canonical.ts";
import { MISCONCEPTIONS, rulesFor, adapterFor, type Ctx, type AdapterValue } from "./coordinate-misconceptions.ts";

type Json = any;
type Frac = Rational;
const F = (x: number): Rational => new Rational(x, 1);

export const GENERATOR_ID = "gen.geometry.coordinate-lines";
export const GENERATOR_VERSION = "1.0.2";
export const VALIDATOR_VERSION = "1.0.2";
const CALCULATOR_POLICY = "calculator-not-required";

export const TASKS = ["read_point", "plot_point", "gradient_two_points", "midpoint",
  "interpret_mx_c", "equation_from_graph", "equation_from_two_points"] as const;
const MC_TASKS = ["read_point", "gradient_two_points", "midpoint", "interpret_mx_c",
  "equation_from_graph", "equation_from_two_points"];
const FIGURE_TASKS = ["read_point", "plot_point", "gradient_two_points", "midpoint",
  "equation_from_graph", "equation_from_two_points"];

const OBJECTIVE_BY_TASK: Record<string, string> = {
  read_point: "SPI.MIDDLE.GEO.COORD.READ_POINT.01",
  plot_point: "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01",
  gradient_two_points: "SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01",
  midpoint: "SPI.MIDDLE.GEO.COORD.MIDPOINT.01",
  interpret_mx_c: "SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01",
  equation_from_graph: "SPI.MIDDLE.GEO.COORD.EQUATION_FROM_GRAPH.01",
  equation_from_two_points: "SPI.MIDDLE.GEO.COORD.EQUATION_FROM_2PTS.01",
};
const TASK_BANDS: Record<string, [number, number]> = {
  read_point: [1, 2], plot_point: [1, 2], gradient_two_points: [2, 4], midpoint: [2, 3],
  interpret_mx_c: [2, 3], equation_from_graph: [3, 4], equation_from_two_points: [3, 5],
};

const COORD_MAX_X = 10, COORD_MAX_Y = 10;
const GRAD_DENS = [1, 2, 3, 4];
const MAX_PARAM_ATTEMPTS = 800;
const VIEW_W = 1000, VIEW_H = 700, CX = 500, CY = 350;
const PAD = 40, U_MIN = 24, DATA_MARGIN_UNITS = 1, MAX_LABELS_PER_AXIS = 11, MINOR_GRID_MIN_U = 32;

const STYLE =
  ".cx-axis{stroke:#111;stroke-width:3;fill:none}" +
  ".cx-tick{stroke:#111;stroke-width:2}" +
  ".cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}" +
  ".cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}" +
  ".cx-line{stroke:#111;stroke-width:3;fill:none}" +
  ".cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}" +
  ".cx-pt-core{fill:#111}" +
  ".cx-guide{stroke:#555;stroke-width:1.5;stroke-dasharray:5 4;stroke-linecap:round;fill:none}" +
  "text{font-family:sans-serif;font-size:28px;fill:#111}" +
  ".cx-ticklbl{font-size:20px;fill:#333}" +
  ".cx-lbl{font-size:28px;fill:#111}";
const GREYS = new Set(["#111", "#333", "#444", "#555", "#888", "#bbb", "#fff"]);

const ANSWER_KIND: Record<string, string> = {
  read_point: "coordinate", plot_point: "coordinate", midpoint: "ordered-pair",
  gradient_two_points: "gradient", interpret_mx_c: "equation",
  equation_from_graph: "equation", equation_from_two_points: "equation",
};

// --------------------------------------------------------------------------- //
function intgcd(a: number, b: number): number { a = Math.abs(a); b = Math.abs(b); while (b) { [a, b] = [b, a % b]; } return a; }

function gridRound(num: number, den: number): number {
  const q = Math.floor(num / den);
  const r = num - q * den;
  return 2 * r >= den ? q + 1 : q;
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

const encRat = (f: Frac): Json => ({ num: f.num, den: f.den });
const dispRat = (f: Frac): string => (f.den === 1 ? String(f.num) : `${f.num}/${f.den}`);
const encPt = (x: Frac, y: Frac): Json => ({ x: encRat(x), y: encRat(y) });
const dispPt = (x: Frac, y: Frac): string => `(${dispRat(x)}, ${dispRat(y)})`;
const encLine = (m: Frac, c: Frac): Json => ({ m: encRat(m), c: encRat(c) });

function mTerm(m: Frac): string {
  if (m.num === 1 && m.den === 1) return "x";
  if (m.num === -1 && m.den === 1) return "-x";
  if (m.den === 1) return `${m.num}x`;
  return `(${dispRat(m)})x`;
}
function dispLine(m: Frac, c: Frac): string {
  if (m.num === 0) return `y = ${dispRat(c)}`;
  let s = "y = " + mTerm(m);
  if (c.num > 0) s += ` + ${dispRat(c)}`;
  else if (c.num < 0) s += ` - ${dispRat(c.neg())}`;
  return s;
}
const dispMxC = (m: Frac, c: Frac): string => `m = ${dispRat(m)}, c = ${dispRat(c)}`;

// --------------------------------------------------------------------------- //
interface Lay { wx0: number; wx1: number; wy0: number; wy1: number; Wx: number; Wy: number; U: number; }

function viewport(req: Array<[number, number]>): Lay | null {
  const pts = [...req, [0, 0] as [number, number]];
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
  const wx0 = Math.min(...xs) - DATA_MARGIN_UNITS, wx1 = Math.max(...xs) + DATA_MARGIN_UNITS;
  const wy0 = Math.min(...ys) - DATA_MARGIN_UNITS, wy1 = Math.max(...ys) + DATA_MARGIN_UNITS;
  const Wx = wx1 - wx0, Wy = wy1 - wy0;
  const aw = VIEW_W - 2 * PAD, ah = VIEW_H - 2 * PAD;
  const U = Math.min(Math.floor(aw / Wx), Math.floor(ah / Wy));
  if (U < U_MIN) return null;
  return { wx0, wx1, wy0, wy1, Wx, Wy, U };
}

function projX(lay: Lay, x: Frac): number {
  const nx = F(CX).sub(new Rational(lay.U * lay.Wx, 2)).add(x.sub(F(lay.wx0)).mul(F(lay.U)));
  return gridRound(nx.num, nx.den);
}
function projY(lay: Lay, y: Frac): number {
  const ny = F(CY).add(new Rational(lay.U * lay.Wy, 2)).sub(y.sub(F(lay.wy0)).mul(F(lay.U)));
  return gridRound(ny.num, ny.den);
}

const sgn = (a: Frac): number => (a.num > 0 ? 1 : a.num < 0 ? -1 : 0);
const le = (a: Frac, b: Frac): boolean => sgn(a.sub(b)) <= 0;

function clipLine(m: Frac, c: Frac, lay: Lay): Array<[Frac, Frac]> {
  const wx0 = F(lay.wx0), wx1 = F(lay.wx1), wy0 = F(lay.wy0), wy1 = F(lay.wy1);
  const cand: Array<[Frac, Frac]> = [];
  const addP = (x: Frac, y: Frac): void => {
    if (le(wx0, x) && le(x, wx1) && le(wy0, y) && le(y, wy1)) {
      if (!cand.some((p) => p[0].equals(x) && p[1].equals(y))) cand.push([x, y]);
    }
  };
  addP(wx0, m.mul(wx0).add(c));
  addP(wx1, m.mul(wx1).add(c));
  if (m.num !== 0) {
    addP(wy0.sub(c).div(m), wy0);
    addP(wy1.sub(c).div(m), wy1);
  }
  cand.sort((p, q) => sgn(p[0].sub(q[0])) || sgn(p[1].sub(q[1])));
  if (cand.length < 2) return [];
  return [cand[0]!, cand[cand.length - 1]!];
}

function latticePointsOnLine(m: Frac, c: Frac, lay: Lay): Array<[number, number]> {
  const q = m.den;
  const out: Array<[number, number]> = [];
  for (let x = lay.wx0; x <= lay.wx1; x++) {
    if (((x % q) + q) % q === 0) {
      const y = m.mul(F(x)).add(c);
      if (y.den === 1 && lay.wy0 <= y.num && y.num <= lay.wy1) out.push([x, y.num]);
    }
  }
  return out;
}

function tickStride(lo: number, hi: number): number {
  const n = hi - lo + 1;
  let stride = 1;
  while (Math.floor((n + stride - 1) / stride) > MAX_LABELS_PER_AXIS) stride += 1;
  return stride;
}

// --------------------------------------------------------------------------- //
const lineEl = (cls: string, x1: number, y1: number, x2: number, y2: number): string =>
  `<line class="${cls}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`;
const pointEls = (px: number, py: number): string[] => [
  `<circle class="cx-pt-outline" cx="${px}" cy="${py}" r="9"/>`,
  `<circle class="cx-pt-core" cx="${px}" cy="${py}" r="5"/>`,
];

function labelPos(lay: Lay, gx: number, px: number): [number, string] {
  const right = gx <= (lay.wx0 + lay.wx1) / 2;
  return [right ? px + 14 : px - 14, right ? "start" : "end"];
}

function figure(task: string, params: Json, lay: Lay, scaffold: boolean): string {
  const out: string[] = [];
  const acc = accessibility(task, params);
  out.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VIEW_W} ${VIEW_H}" role="img" aria-label="${esc(acc.alt)}">`);
  out.push(`<title>${esc(acc.title)}</title>`);
  out.push(`<desc>${esc(acc.desc)}</desc>`);
  out.push(`<style>${STYLE}</style>`);
  const { wx0, wx1, wy0, wy1, U } = lay;
  const xAxisY = projY(lay, F(0)), yAxisX = projX(lay, F(0));

  if (U >= MINOR_GRID_MIN_U) {
    for (let gx2 = wx0 * 2 + 1; gx2 < wx1 * 2; gx2 += 2) {
      const sx = projX(lay, new Rational(gx2, 2));
      out.push(lineEl("cx-grid-minor", sx, projY(lay, F(wy1)), sx, projY(lay, F(wy0))));
    }
    for (let gy2 = wy0 * 2 + 1; gy2 < wy1 * 2; gy2 += 2) {
      const sy = projY(lay, new Rational(gy2, 2));
      out.push(lineEl("cx-grid-minor", projX(lay, F(wx0)), sy, projX(lay, F(wx1)), sy));
    }
  }
  for (let gx = wx0; gx <= wx1; gx++) {
    if (gx === 0) continue;
    const sx = projX(lay, F(gx));
    out.push(lineEl("cx-grid-major", sx, projY(lay, F(wy1)), sx, projY(lay, F(wy0))));
  }
  for (let gy = wy0; gy <= wy1; gy++) {
    if (gy === 0) continue;
    const sy = projY(lay, F(gy));
    out.push(lineEl("cx-grid-major", projX(lay, F(wx0)), sy, projX(lay, F(wx1)), sy));
  }

  const axL = projX(lay, F(wx0)), axR = projX(lay, F(wx1));
  const ayB = projY(lay, F(wy0)), ayT = projY(lay, F(wy1));
  out.push(lineEl("cx-axis", axL, xAxisY, axR, xAxisY));
  out.push(lineEl("cx-axis", yAxisX, ayB, yAxisX, ayT));
  out.push(`<path class="cx-axis" d="M ${axR - 12} ${xAxisY - 7} L ${axR} ${xAxisY} L ${axR - 12} ${xAxisY + 7}"/>`);
  out.push(`<path class="cx-axis" d="M ${yAxisX - 7} ${ayT + 12} L ${yAxisX} ${ayT} L ${yAxisX + 7} ${ayT + 12}"/>`);
  out.push(`<text class="cx-lbl" x="${axR - 4}" y="${xAxisY + 30}" text-anchor="end">x</text>`);
  out.push(`<text class="cx-lbl" x="${yAxisX + 12}" y="${ayT + 6}" text-anchor="start">y</text>`);

  const sxStride = tickStride(wx0, wx1);
  for (let gx = wx0; gx <= wx1; gx++) {
    if (gx === 0 || gx % sxStride !== 0) continue;
    const sx = projX(lay, F(gx));
    out.push(lineEl("cx-tick", sx, xAxisY - 6, sx, xAxisY + 6));
    out.push(`<text class="cx-ticklbl" x="${sx}" y="${xAxisY + 26}" text-anchor="middle">${gx}</text>`);
  }
  const syStride = tickStride(wy0, wy1);
  for (let gy = wy0; gy <= wy1; gy++) {
    if (gy === 0 || gy % syStride !== 0) continue;
    const sy = projY(lay, F(gy));
    out.push(lineEl("cx-tick", yAxisX - 6, sy, yAxisX + 6, sy));
    out.push(`<text class="cx-ticklbl" x="${yAxisX - 12}" y="${sy + 7}" text-anchor="end">${gy}</text>`);
  }
  out.push(`<text class="cx-ticklbl" x="${yAxisX - 12}" y="${xAxisY + 26}" text-anchor="end">0</text>`);

  out.push(...taskGeometry(task, params, lay, scaffold));
  out.push("</svg>");
  return out.join("\n");
}

function taskGeometry(task: string, params: Json, lay: Lay, scaffold: boolean): string[] {
  const out: string[] = [];
  if (task === "read_point") {
    const x = params.x, y = params.y;
    const px = projX(lay, F(x)), py = projY(lay, F(y));
    if (scaffold) {
      out.push(lineEl("cx-guide", px, py, px, projY(lay, F(0))));
      out.push(lineEl("cx-guide", px, py, projX(lay, F(0)), py));
    }
    out.push(...pointEls(px, py));
    const [lx, anchor] = labelPos(lay, x, px);
    out.push(`<text class="cx-lbl" x="${lx}" y="${py - 12}" text-anchor="${anchor}">P</text>`);
  } else if (task === "plot_point") {
    /* blank labelled grid; the target point is never drawn */
  } else if (task === "gradient_two_points" || task === "midpoint" || task === "equation_from_two_points") {
    const a: [number, number] = [params.x1, params.y1];
    const b: [number, number] = [params.x2, params.y2];
    if (task === "equation_from_two_points") {
      const [m, c] = solveLine2pts(params);
      const seg = clipLine(m, c, lay);
      if (seg.length) {
        const [s0, s1] = [seg[0]!, seg[1]!];
        out.push(lineEl("cx-line", projX(lay, s0[0]), projY(lay, s0[1]), projX(lay, s1[0]), projY(lay, s1[1])));
      }
    }
    if (task === "gradient_two_points" && scaffold) {
      const cxn = b[0], cyn = a[1];
      out.push(lineEl("cx-guide", projX(lay, F(a[0])), projY(lay, F(a[1])), projX(lay, F(cxn)), projY(lay, F(cyn))));
      out.push(lineEl("cx-guide", projX(lay, F(cxn)), projY(lay, F(cyn)), projX(lay, F(b[0])), projY(lay, F(b[1]))));
    }
    for (const [pt, letter] of [[a, "A"], [b, "B"]] as Array<[[number, number], string]>) {
      const px = projX(lay, F(pt[0])), py = projY(lay, F(pt[1]));
      out.push(...pointEls(px, py));
      const [lx, anchor] = labelPos(lay, pt[0], px);
      out.push(`<text class="cx-lbl" x="${lx}" y="${py - 12}" text-anchor="${anchor}">${letter}</text>`);
    }
  } else if (task === "equation_from_graph") {
    const [m, c] = paramsToLine(params);
    const seg = clipLine(m, c, lay);
    if (seg.length) {
      const [s0, s1] = [seg[0]!, seg[1]!];
      out.push(lineEl("cx-line", projX(lay, s0[0]), projY(lay, s0[1]), projX(lay, s1[0]), projY(lay, s1[1])));
      const lx = projX(lay, s1[0]);
      out.push(`<text class="cx-lbl" x="${lx - 10}" y="${projY(lay, s1[1]) - 10}" text-anchor="end">l</text>`);
    }
  }
  return out;
}

// --------------------------------------------------------------------------- //
const solveGradient = (p: Json): Frac => new Rational(p.y2 - p.y1, p.x2 - p.x1);
const solveMidpoint = (p: Json): [Frac, Frac] => [new Rational(p.x1 + p.x2, 2), new Rational(p.y1 + p.y2, 2)];
function solveLine2pts(p: Json): [Frac, Frac] {
  const m = solveGradient(p);
  return [m, F(p.y1).sub(m.mul(F(p.x1)))];
}
const paramsToLine = (p: Json): [Frac, Frac] => [new Rational(p.m_num, p.m_den), new Rational(p.c_num, p.c_den)];

function ctxFor(task: string, p: Json): Ctx {
  if (task === "read_point") return { x: F(p.x), y: F(p.y) };
  if (task === "midpoint") {
    const [mx, my] = solveMidpoint(p);
    return { x1: F(p.x1), y1: F(p.y1), x2: F(p.x2), y2: F(p.y2), mx, my };
  }
  if (task === "gradient_two_points") return { x1: F(p.x1), y1: F(p.y1), x2: F(p.x2), y2: F(p.y2), m: solveGradient(p) };
  if (task === "equation_from_two_points") {
    const [m, c] = solveLine2pts(p);
    return { x1: F(p.x1), y1: F(p.y1), x2: F(p.x2), y2: F(p.y2), m, c };
  }
  const [m, c] = paramsToLine(p);
  const extra: Ctx = "x1" in p ? { x1: F(p.x1), y1: F(p.y1), x2: F(p.x2), y2: F(p.y2) } : {};
  return { m, c, ...extra };
}

type AnswerValue = [Frac, Frac] | Frac;
function answerValue(task: string, p: Json): AnswerValue {
  if (task === "read_point" || task === "plot_point") return [F(p.x), F(p.y)];
  if (task === "midpoint") return solveMidpoint(p);
  if (task === "gradient_two_points") return solveGradient(p);
  if (task === "equation_from_two_points") return solveLine2pts(p);
  return paramsToLine(p);
}

// --------------------------------------------------------------------------- //
const reasonableRat = (f: Frac): boolean => Math.abs(f.num) <= 99 && f.den <= 12;

function valueOk(task: string, val: AdapterValue): boolean {
  const kind = ANSWER_KIND[task];
  if (kind === "coordinate" || kind === "ordered-pair") {
    const [x, y] = val as [Frac, Frac];
    return reasonableRat(x) && reasonableRat(y) && Math.abs(x.num / x.den) <= 20 && Math.abs(y.num / y.den) <= 20;
  }
  if (kind === "gradient") return reasonableRat(val as Frac);
  const [m, c] = val as [Frac, Frac];
  return reasonableRat(m) && reasonableRat(c);
}

function sameValue(task: string, a: AnswerValue | AdapterValue, b: AnswerValue | AdapterValue): boolean {
  const kind = ANSWER_KIND[task];
  if (kind === "gradient") return (a as Frac).equals(b as Frac);
  const [ax, ay] = a as [Frac, Frac], [bx, by] = b as [Frac, Frac];
  return ax.equals(bx) && ay.equals(by);
}

interface Distractor { misconceptionId: string; value: AdapterValue; rationale: string; }
function distractors(task: string, p: Json): Distractor[] | null {
  const ids = rulesFor(task);
  if (!ids.length) return null;
  const ctx = ctxFor(task, p);
  const answer = answerValue(task, p);
  const seen: Array<AnswerValue | AdapterValue> = [answer];
  const chosen: Distractor[] = [];
  for (const mid of ids) {
    const ad = adapterFor(mid, task);
    if (!ad) continue;
    const val = ad(ctx as never);
    if (val === null || !valueOk(task, val)) continue;
    if (seen.some((s) => sameValue(task, val, s))) continue;
    seen.push(val);
    chosen.push({ misconceptionId: mid, value: val, rationale: MISCONCEPTIONS[mid]!.observableError });
    if (chosen.length === 3) break;
  }
  return chosen.length === 3 ? chosen : null;
}

function displayValue(task: string, val: AnswerValue | AdapterValue): [Json, string] {
  const kind = ANSWER_KIND[task];
  if (kind === "coordinate" || kind === "ordered-pair") {
    const [x, y] = val as [Frac, Frac];
    return [encPt(x, y), dispPt(x, y)];
  }
  if (kind === "gradient") return [encRat(val as Frac), dispRat(val as Frac)];
  const [m, c] = val as [Frac, Frac];
  return [encLine(m, c), task === "interpret_mx_c" ? dispMxC(m, c) : dispLine(m, c)];
}

// --------------------------------------------------------------------------- //
const RS_BASE: Record<string, number> = { read_point: 0.10, plot_point: 0.10, gradient_two_points: 0.40, midpoint: 0.30, interpret_mx_c: 0.30, equation_from_graph: 0.55, equation_from_two_points: 0.80 };
const AB_BASE: Record<string, number> = { read_point: 0.10, plot_point: 0.15, gradient_two_points: 0.30, midpoint: 0.20, interpret_mx_c: 0.20, equation_from_graph: 0.45, equation_from_two_points: 0.75 };

function difficulty(task: string, p: Json): Json {
  const scaffold = Boolean(p.scaffold);
  const answer = answerValue(task, p);
  const kind = ANSWER_KIND[task];
  let nc: number, ev: number;
  if (kind === "coordinate" || kind === "ordered-pair") {
    const [x, y] = answer as [Frac, Frac];
    const fx = x.num / x.den, fy = y.num / y.den;
    nc = Math.min(1.0, (Math.abs(fx) + Math.abs(fy)) / (COORD_MAX_X + COORD_MAX_Y));
    ev = x.den > 1 || y.den > 1 ? 1.0 : 0.0;
  } else if (kind === "gradient") {
    const m = answer as Frac;
    nc = Math.min(1.0, (Math.abs(m.num) + m.den) / 10.0);
    ev = m.den > 1 ? 1.0 : 0.0;
  } else {
    const [m, c] = answer as [Frac, Frac];
    nc = Math.min(1.0, (Math.abs(m.num) + m.den + Math.abs(c.num)) / 16.0);
    ev = m.den > 1 || c.den > 1 ? 1.0 : 0.0;
  }
  const rs = Math.max(0.0, Math.min(1.0, RS_BASE[task]! + (scaffold ? -0.10 : 0.05)));
  const ab = AB_BASE[task]!;
  const axes = { numericalComplexity: round3(nc), exactVsApproximate: round3(ev), reasoningSteps: round3(rs), abstraction: round3(ab) };
  const score = 0.30 * nc + 0.20 * ev + 0.25 * rs + 0.25 * ab;
  let band = bandFromScore(score);
  const [lo, hi] = TASK_BANDS[task]!;
  band = Math.max(lo!, Math.min(hi!, band));
  return { overallBand: band, axes };
}

// --------------------------------------------------------------------------- //
const gridPhrase = (): string => "on a labelled Cartesian grid with equal x and y scales";

function accessibility(task: string, p: Json): { title: string; alt: string; desc: string; dataTable: Json } {
  let title: string, alt: string, desc: string, rows: string[][];
  if (task === "read_point") {
    title = "Reading coordinates";
    alt = `A single point P plotted ${gridPhrase()}.`;
    desc = `A point labelled P is plotted ${gridPhrase()}. Read its x-coordinate from the horizontal axis and its y-coordinate from the vertical axis.`;
    rows = [["point", "position"], ["P", `x = ${p.x}, y = ${p.y}`]];
  } else if (task === "plot_point") {
    title = "Plotting a point";
    alt = `A blank labelled Cartesian grid for plotting a point.`;
    desc = `A labelled Cartesian grid with numbered axes and equal x and y scales. No point is plotted yet; plot the point given in the question.`;
    rows = [["axis", "range"], ["x", `${-COORD_MAX_X} to ${COORD_MAX_X}`], ["y", `${-COORD_MAX_Y} to ${COORD_MAX_Y}`]];
  } else if (task === "gradient_two_points" || task === "equation_from_two_points") {
    const a = [p.x1, p.y1], b = [p.x2, p.y2];
    title = task === "gradient_two_points" ? "Two plotted points" : "A line through two points";
    const extra = task === "gradient_two_points" ? "" : " A straight line is drawn through them.";
    alt = `Two points A and B plotted ${gridPhrase()}.${extra}`;
    desc = `Point A is at (${a[0]}, ${a[1]}) and point B is at (${b[0]}, ${b[1]}), plotted ${gridPhrase()}.${extra}`;
    rows = [["point", "coordinates"], ["A", `(${a[0]}, ${a[1]})`], ["B", `(${b[0]}, ${b[1]})`]];
  } else if (task === "midpoint") {
    const a = [p.x1, p.y1], b = [p.x2, p.y2];
    title = "A line segment";
    alt = `Two endpoints A and B of a segment plotted ${gridPhrase()}.`;
    desc = `The endpoints of a line segment are A at (${a[0]}, ${a[1]}) and B at (${b[0]}, ${b[1]}), plotted ${gridPhrase()}. The midpoint is not marked.`;
    rows = [["endpoint", "coordinates"], ["A", `(${a[0]}, ${a[1]})`], ["B", `(${b[0]}, ${b[1]})`]];
  } else if (task === "equation_from_graph") {
    title = "A straight-line graph";
    alt = `A straight line drawn ${gridPhrase()}.`;
    desc = `A straight line is drawn ${gridPhrase()}. It passes through the lattice points (${p.x1}, ${p.y1}) and (${p.x2}, ${p.y2}). Determine its equation in the form y = mx + c.`;
    rows = [["the line passes through", "coordinates"], ["point 1", `(${p.x1}, ${p.y1})`], ["point 2", `(${p.x2}, ${p.y2})`]];
  } else {
    const [m, c] = paramsToLine(p);
    title = "A linear equation";
    alt = `The linear equation ${dispLine(m, c)}.`;
    desc = `The straight line ${dispLine(m, c)} is written in the form y = mx + c.`;
    rows = [["the equation", dispLine(m, c)]];
  }
  return { title, alt, desc, dataTable: { columns: rows[0]!, rows: rows.slice(1) } };
}

// --------------------------------------------------------------------------- //
function prompt(task: string, p: Json): Json {
  const media = FIGURE_TASKS.includes(task) ? [{ kind: "media-ref", ref: "fig-1" }] : [];
  if (task === "read_point") return { instruction: "Write", blocks: [{ kind: "text", text: "Write the coordinates of the point P shown on the grid, as an ordered pair." }, ...media] };
  if (task === "plot_point") return { instruction: "Plot", blocks: [{ kind: "text", text: `Plot the point ${dispPt(F(p.x), F(p.y))} on the grid.` }, ...media] };
  if (task === "gradient_two_points") return { instruction: "Find", blocks: [{ kind: "text", text: `Find the gradient of the line through A ${dispPt(F(p.x1), F(p.y1))} and B ${dispPt(F(p.x2), F(p.y2))}.` }, ...media] };
  if (task === "midpoint") return { instruction: "Find", blocks: [{ kind: "text", text: `Find the midpoint of the line segment joining A ${dispPt(F(p.x1), F(p.y1))} and B ${dispPt(F(p.x2), F(p.y2))}.` }, ...media] };
  if (task === "interpret_mx_c") { const [m, c] = paramsToLine(p); return { instruction: "Write", blocks: [{ kind: "text", text: `For the straight line ${dispLine(m, c)}, write down the gradient m and the y-intercept c.` }] }; }
  if (task === "equation_from_graph") return { instruction: "Find", blocks: [{ kind: "text", text: "Find the equation of the line l shown on the grid, in the form y = mx + c." }, ...media] };
  return { instruction: "Find", blocks: [{ kind: "text", text: `Find the equation of the line through A ${dispPt(F(p.x1), F(p.y1))} and B ${dispPt(F(p.x2), F(p.y2))}, in the form y = mx + c.` }, ...media] };
}

function solution(task: string, p: Json): Json {
  const steps: Json[] = [];
  const step = (n: number, t: string, r: string): void => { steps.push({ number: n, transformation: t, intermediateResult: r }); };
  if (task === "read_point") {
    if (p.scaffold) step(1, "Project the point vertically to the x-axis to read x, and horizontally to the y-axis to read y", dispPt(F(p.x), F(p.y)));
    else step(1, "Read the horizontal position for the x-coordinate, then the vertical position for the y-coordinate. Write the coordinates as (x, y)", dispPt(F(p.x), F(p.y)));
  }
  else if (task === "plot_point") step(1, "Count along the x-axis, then up or down the y-axis, and mark the point", dispPt(F(p.x), F(p.y)));
  else if (task === "gradient_two_points") {
    const rise = p.y2 - p.y1, run = p.x2 - p.x1, m = solveGradient(p);
    step(1, "Find the rise (change in y) and the run (change in x)", `rise = ${rise}, run = ${run}`);
    step(2, "Divide the rise by the run and simplify", `gradient = ${dispRat(m)}`);
  } else if (task === "midpoint") {
    const [mx, my] = solveMidpoint(p);
    step(1, "Average the x-coordinates", `(${p.x1} + ${p.x2}) / 2 = ${dispRat(mx)}`);
    step(2, "Average the y-coordinates", `(${p.y1} + ${p.y2}) / 2 = ${dispRat(my)}`);
    step(3, "Write the midpoint as an ordered pair", dispPt(mx, my));
  } else if (task === "interpret_mx_c") {
    const [m, c] = paramsToLine(p);
    step(1, "The gradient m is the coefficient of x", `m = ${dispRat(m)}`);
    step(2, "The y-intercept c is the constant term", `c = ${dispRat(c)}`);
  } else if (task === "equation_from_graph") {
    const [m, c] = paramsToLine(p);
    step(1, "Read the gradient as rise over run between two lattice points", `m = ${dispRat(m)}`);
    step(2, "Read where the line crosses the y-axis for the intercept", `c = ${dispRat(c)}`);
    step(3, "Write the equation in the form y = mx + c", dispLine(m, c));
  } else {
    const [m, c] = solveLine2pts(p);
    step(1, "Find the gradient from the two points", `m = ${dispRat(m)}`);
    step(2, "Substitute one point to find the y-intercept c", `c = ${dispRat(c)}`);
    step(3, "Write the equation in the form y = mx + c", dispLine(m, c));
  }
  return { steps };
}

export function pngExportTransform(): Json {
  const scale = Math.min(Math.floor(7680 / VIEW_W), Math.floor(4320 / VIEW_H));
  return { maxEnvelope: "7680x4320", scale, width: VIEW_W * scale, height: VIEW_H * scale, viewBox: `0 0 ${VIEW_W} ${VIEW_H}` };
}

function premiumSpec(task: string, _p: Json): Json {
  const hasLine = task === "equation_from_graph" || task === "equation_from_two_points";
  const hasPoints = ["read_point", "gradient_two_points", "midpoint", "equation_from_two_points"].includes(task);
  const series: Json[] = [];
  if (hasLine) series.push({ id: "line-l", role: "line", colorToken: "--cx-series-1", dash: "solid", marker: "none" });
  if (hasPoints) series.push({ id: "points", role: "points", colorToken: "--cx-series-2", dash: "none", marker: "disc" });
  return {
    styleContractVersion: "1.0.0", paletteId: "cx-premium-default", modes: ["premium", "accessible", "print"],
    defaultMode: "print", series, axisHierarchy: { axis: 1, gridMajor: 2, gridMinor: 3 },
    glow: { enabled: true, outsideStrokeOnly: true, maxBlurPx: 6 }, legend: { enabled: false }, pngExport: pngExportTransform(),
  };
}

// --------------------------------------------------------------------------- //
function drawGradPq(rng: Mulberry32): [number, number] {
  const q = rng.choice(GRAD_DENS);
  let ps: number[];
  if (q === 1) { ps = []; for (let i = -6; i <= 6; i++) ps.push(i); }
  else { ps = []; for (let i = -6; i <= 6; i++) if (i !== 0 && intgcd(Math.abs(i), q) === 1) ps.push(i); }
  const p = rng.choice(ps);
  return [p, q];
}

function drawTwoPointsWithGradient(rng: Mulberry32): Json | null {
  const [p, q] = drawGradPq(rng);
  const k = rng.nextInt(1, 3);
  const dx = q * k, dy = p * k;
  if (dx > 2 * COORD_MAX_X || Math.abs(dy) > 2 * COORD_MAX_Y) return null;
  const x1lo = -COORD_MAX_X, x1hi = COORD_MAX_X - dx;
  if (x1lo > x1hi) return null;
  let x1 = rng.nextInt(x1lo, x1hi);
  const y1lo = Math.max(-COORD_MAX_Y, -COORD_MAX_Y - dy), y1hi = Math.min(COORD_MAX_Y, COORD_MAX_Y - dy);
  if (y1lo > y1hi) return null;
  let y1 = rng.nextInt(y1lo, y1hi);
  let x2 = x1 + dx, y2 = y1 + dy;
  if (rng.nextInt(0, 1) === 1) { [x1, y1, x2, y2] = [x2, y2, x1, y1]; }
  return { x1, y1, x2, y2 };
}

function drawReadPoint(rng: Mulberry32): Json {
  const x = rng.nextInt(-COORD_MAX_X, COORD_MAX_X), y = rng.nextInt(-COORD_MAX_Y, COORD_MAX_Y);
  const scaffold = rng.nextInt(0, 1) === 1;
  return { task: "read_point", x, y, scaffold };
}
function drawPlotPoint(rng: Mulberry32): Json {
  const x = rng.nextInt(-COORD_MAX_X, COORD_MAX_X), y = rng.nextInt(-COORD_MAX_Y, COORD_MAX_Y);
  return { task: "plot_point", x, y, scaffold: false };
}
function drawGradient(rng: Mulberry32): Json | null {
  const base = drawTwoPointsWithGradient(rng);
  const scaffold = rng.nextInt(0, 1) === 1;
  if (base === null) return null;
  return { task: "gradient_two_points", ...base, scaffold };
}
function drawMidpoint(rng: Mulberry32): Json | null {
  const x1 = rng.nextInt(-COORD_MAX_X, COORD_MAX_X), y1 = rng.nextInt(-COORD_MAX_Y, COORD_MAX_Y);
  const x2 = rng.nextInt(-COORD_MAX_X, COORD_MAX_X), y2 = rng.nextInt(-COORD_MAX_Y, COORD_MAX_Y);
  if (x1 === x2 && y1 === y2) return null;
  return { task: "midpoint", x1, y1, x2, y2, scaffold: false };
}
function drawInterpret(rng: Mulberry32): Json {
  const [p, q] = drawGradPq(rng);
  const c = rng.nextInt(-9, 9);
  return { task: "interpret_mx_c", m_num: p, m_den: q, c_num: c, c_den: 1, scaffold: false };
}
function drawEquationFromTwoPoints(rng: Mulberry32): Json | null {
  const base = drawTwoPointsWithGradient(rng);
  if (base === null) return null;
  const params = { task: "equation_from_two_points", ...base, scaffold: false };
  const [, c] = solveLine2pts(params);
  if (Math.abs(c.num / c.den) > 20 || c.den > 12) return null;
  return params;
}
function drawEquationFromGraph(rng: Mulberry32): Json | null {
  const [p, q] = drawGradPq(rng);
  const c = rng.nextInt(-7, 7);
  const m = new Rational(p, q);
  const xs: number[] = [];
  for (let x = -COORD_MAX_X; x <= COORD_MAX_X; x++) {
    if (((x % q) + q) % q !== 0) continue;
    const y = m.mul(F(x)).add(F(c));
    if (y.den === 1 && -COORD_MAX_Y <= y.num && y.num <= COORD_MAX_Y) xs.push(x);
  }
  if (xs.length < 2) return null;
  const x1 = xs[0]!, x2 = xs[xs.length - 1]!;
  const y1 = m.mul(F(x1)).add(F(c)).num, y2 = m.mul(F(x2)).add(F(c)).num;
  return { task: "equation_from_graph", m_num: p, m_den: q, c_num: c, c_den: 1, x1, y1, x2, y2, scaffold: false };
}

const DRAW: Record<string, (rng: Mulberry32) => Json | null> = {
  read_point: drawReadPoint, plot_point: drawPlotPoint, gradient_two_points: drawGradient,
  midpoint: drawMidpoint, interpret_mx_c: drawInterpret, equation_from_graph: drawEquationFromGraph,
  equation_from_two_points: drawEquationFromTwoPoints,
};

function reqPoints(task: string, p: Json): Array<[number, number]> {
  if (task === "read_point" || task === "plot_point") return [[p.x, p.y]];
  if (task === "interpret_mx_c") return [];
  return [[p.x1, p.y1], [p.x2, p.y2]];
}

function labelsFeasible(task: string, p: Json, lay: Lay): boolean {
  let pts: Array<[number, number]> = [];
  if (task === "read_point") pts = [[p.x, p.y]];
  else if (task === "gradient_two_points" || task === "midpoint" || task === "equation_from_two_points") pts = [[p.x1, p.y1], [p.x2, p.y2]];
  const proj = pts.map(([gx, gy]) => [projX(lay, F(gx)), projY(lay, F(gy))] as [number, number]);
  for (const [px, py] of proj) if (!(16 <= px && px <= VIEW_W - 16 && 30 <= py && py <= VIEW_H - 16)) return false;
  if (proj.length === 2) {
    const a = proj[0]!, b = proj[1]!;
    if ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 < 44 * 44) return false;
  }
  return true;
}

// --------------------------------------------------------------------------- //
function resolveInteraction(config: Json): string {
  const it = config.interactionType;
  if (it === "free-response" || it === "multiple-choice") return it;
  if (config.answerType === "multiple-choice") return "multiple-choice";
  return "free-response";
}

function acceptable(p: Json, interaction: string): Distractor[] | null {
  const task = p.task;
  if (FIGURE_TASKS.includes(task)) {
    const lay = viewport(reqPoints(task, p));
    if (lay === null || !labelsFeasible(task, p, lay)) return null;
    if (task === "equation_from_graph") {
      const [m, c] = paramsToLine(p);
      if (latticePointsOnLine(m, c, lay).length < 2) return null;
    }
  }
  if (interaction === "multiple-choice") {
    if (!MC_TASKS.includes(task)) return null;
    return distractors(task, p);
  }
  return [];
}

function encodeAnswer(task: string, p: Json): Json {
  const kind = ANSWER_KIND[task];
  const val = answerValue(task, p);
  if (kind === "coordinate" || kind === "ordered-pair") {
    const [x, y] = val as [Frac, Frac];
    return { type: kind, canonical: encPt(x, y), display: dispPt(x, y) };
  }
  if (kind === "gradient") {
    const m = val as Frac;
    return { type: m.den === 1 ? "integer" : "exact-rational", canonical: encRat(m), display: dispRat(m), accepts: { fraction: true, decimal: false, mixed: false } };
  }
  const [m, c] = val as [Frac, Frac];
  const out: Json = { type: "equation", canonical: encLine(m, c) };
  if (task === "interpret_mx_c") { out.display = dispMxC(m, c); out.equivalentForms = [{ display: dispLine(m, c) }]; }
  else out.display = dispLine(m, c);
  return out;
}

export function generate(seed: number, config: Json = {}): Json {
  const interaction = resolveInteraction(config);
  const mc = interaction === "multiple-choice";
  const explicit = config.task;
  if (explicit != null && !(TASKS as readonly string[]).includes(explicit)) throw new Error(`unknown task: ${explicit}`);
  if (mc && explicit === "plot_point") throw new Error("plot_point is free-response only; multiple-choice is not supported (owner decision B.2)");
  if (mc && explicit != null && !MC_TASKS.includes(explicit)) throw new Error(`task ${explicit} does not support multiple-choice`);

  const pool = mc && explicit == null ? MC_TASKS : (TASKS as readonly string[]);
  const rng = new Mulberry32(seed);
  let params: Json = {}, dist: Distractor[] | null = null, ok = false;
  for (let i = 0; i < MAX_PARAM_ATTEMPTS; i++) {
    const task = explicit != null ? explicit : rng.choice(pool);
    const drawn = DRAW[task]!(rng);
    if (drawn === null) continue;
    const res = acceptable(drawn, interaction);
    if (res === null) continue;
    params = drawn; dist = res; ok = true; break;
  }
  if (!ok) throw new Error("could not find acceptable coordinate-lines parameters");

  const task = params.task;
  const answer = encodeAnswer(task, params);
  const acc = accessibility(task, params);
  const lay = FIGURE_TASKS.includes(task) ? viewport(reqPoints(task, params)) : null;
  const scaffold = Boolean(params.scaffold);

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
    accessibility: { spokenMath: acc.desc, altText: acc.alt, longDescription: acc.desc, nonColorIndicators: true },
    provenance: { origin: "generated", rightsStatus: "academy-owned", originalityNote: "Original parameterized item; the figure is generated from the same parameters." },
    lifecycle: { state: "generated" },
  };

  if (FIGURE_TASKS.includes(task)) {
    const svg = figure(task, params, lay as Lay, scaffold);
    item.media = [{ id: "fig-1", kind: "svg", svg, toScale: true, altText: acc.alt, longDescription: acc.desc, dataTableFallback: acc.dataTable, spec: { premium: premiumSpec(task, params) } }];
  } else {
    item.media = [];
  }

  if (mc) {
    const ds = dist || [];
    item.distractors = ds.map((d, i) => { const [enc, disp] = displayValue(task, d.value); return { id: `d${i + 1}`, value: enc, display: disp, misconceptionId: d.misconceptionId, rationale: d.rationale }; });
    const [aEnc, aDisp] = displayValue(task, answerValue(task, params));
    const poolOpts: Json[] = [{ value: aEnc, display: aDisp, correct: true, misconceptionId: null }];
    for (const d of ds) { const [enc, disp] = displayValue(task, d.value); poolOpts.push({ value: enc, display: disp, correct: false, misconceptionId: d.misconceptionId }); }
    const shuffled = rng.shuffle(poolOpts);
    const labels = ["A", "B", "C", "D", "E"];
    item.options = shuffled.map((o, i) => ({ label: labels[i]!, value: o.value, display: o.display, correct: o.correct, ...(o.misconceptionId ? { misconceptionId: o.misconceptionId } : {}) }));
  }
  return item;
}

export function serialize(item: Json): string { return canonicalStringify(item as Json); }

export function describe(): Json {
  return {
    id: GENERATOR_ID, version: GENERATOR_VERSION, title: "Coordinate geometry & straight-line graphs",
    domain: "geometry", objectiveIds: (TASKS as readonly string[]).map((t) => OBJECTIVE_BY_TASK[t]),
    interactionTypes: ["free-response", "multiple-choice"],
    answerTypes: ["coordinate", "ordered-pair", "integer", "exact-rational", "equation"], tasks: [...TASKS],
  };
}

export type Config = { task?: string; interactionType?: string; answerType?: string };

// --------------------------------------------------------------------------- //
// Independent validator (TypeScript). Mirrors the Python validator: rebuilds the
// figure from params and asserts the stored SVG byte-for-byte, recomputes the answer by
// a second route, and enforces the vertical-line, clipping, leakage, and premium-spec
// contracts. Functional parity (status), not byte parity (the result is not serialized).
// --------------------------------------------------------------------------- //
const FINITE_GRADIENT_TASKS = ["gradient_two_points", "equation_from_graph", "equation_from_two_points"];

function inCanvas(px: number, py: number): boolean {
  return PAD - 1 <= px && px <= VIEW_W - PAD + 1 && PAD - 1 <= py && py <= VIEW_H - PAD + 1;
}

function inb(v: number, b: number): boolean { return -b <= v && v <= b; }

function paramsInDomain(task: string, p: Json): boolean {
  if (task === "read_point" || task === "plot_point") return inb(p.x, COORD_MAX_X) && inb(p.y, COORD_MAX_Y);
  if (task === "interpret_mx_c") return GRAD_DENS.includes(p.m_den) && p.c_den === 1;
  let ok = ["x1", "y1", "x2", "y2"].every((k) => inb(p[k], k[0] === "x" ? COORD_MAX_X : COORD_MAX_Y));
  if (FINITE_GRADIENT_TASKS.includes(task)) ok = ok && p.x1 !== p.x2;
  return ok;
}

function closureOk(task: string, p: Json, answer: Json): boolean {
  const can = answer.canonical;
  const eq = (a: Json, b: Json): boolean => canonicalStringify(a) === canonicalStringify(b);
  if (task === "read_point" || task === "plot_point" || task === "midpoint") {
    const [x, y] = answerValue(task, p) as [Frac, Frac];
    return eq(can, encPt(x, y));
  }
  if (task === "gradient_two_points") return eq(can, encRat(new Rational(p.y2 - p.y1, p.x2 - p.x1)));
  if (task === "equation_from_two_points") { const [m, c] = solveLine2pts(p); return eq(can, encLine(m, c)); }
  const [m, c] = paramsToLine(p);
  return eq(can, encLine(m, c));
}

function axisHierarchyOk(svg: string): boolean {
  const w = (cls: string): number => {
    const m = new RegExp("\\." + cls + "\\{[^}]*stroke-width:([0-9.]+)").exec(svg);
    return m ? parseFloat(m[1]!) : 0;
  };
  return w("cx-axis") > w("cx-grid-major") && w("cx-grid-major") > w("cx-grid-minor") && w("cx-grid-minor") > 0;
}

function distractorValuesOk(task: string, p: Json, ds: Json[]): boolean {
  const ctx = ctxFor(task, p);
  for (const d of ds) {
    const ad = adapterFor(d.misconceptionId, task);
    if (!ad) return false;
    const val = ad(ctx as never);
    if (val === null) return false;
    const [enc] = displayValue(task, val);
    if (canonicalStringify(enc) !== canonicalStringify(d.value)) return false;
  }
  return true;
}

export function validate(item: Json): Json {
  const checks: Array<{ name: string; result: string; detail: string }> = [];
  const add = (name: string, ok: boolean, detail = ""): void => { checks.push({ name, result: ok ? "pass" : "fail", detail }); };
  const p = item.params, task = p.task, interaction = item.interactionType, answer = item.answer;
  const aDisp: string = answer.display ?? "";

  add("params-in-domain", paramsInDomain(task, p), `task=${task}`);
  add("interaction-type", interaction === "free-response" || interaction === "multiple-choice", String(interaction));
  add("objective-mapping", canonicalStringify(item.objectiveIds) === canonicalStringify([OBJECTIVE_BY_TASK[task]!]), String(item.objectiveIds));
  const kind = ANSWER_KIND[task];
  if (kind === "gradient") add("answer-type-consistency", answer.type === (answer.canonical.den === 1 ? "integer" : "exact-rational"), answer.type);
  else if (kind === "coordinate" || kind === "ordered-pair") add("answer-type-consistency", answer.type === kind, answer.type);
  else add("answer-type-consistency", answer.type === "equation", answer.type);

  if (FINITE_GRADIENT_TASKS.includes(task)) add("vertical-line-excluded", p.x1 !== p.x2, `x1=${p.x1} x2=${p.x2}`);
  add("closure-agreement", closureOk(task, p, answer), "recomputed answer matches stored canonical");

  if (FIGURE_TASKS.includes(task)) {
    const media = item.media ?? [];
    add("media-present", media.length === 1 && media[0].kind === "svg", "one svg media asset");
    if (media.length) {
      const lay = viewport(reqPoints(task, p));
      const rebuilt = lay ? figure(task, p, lay, Boolean(p.scaffold)) : "";
      const stored: string = media[0].svg ?? "";
      add("svg-realises-data", rebuilt === stored, "recomputed SVG matches stored SVG byte-for-byte");
      add("media-to-scale", media[0].toScale === true, "coordinate figures are drawn to scale");
      add("equal-axis-scale", lay !== null, "one equal x/y unit scale U");
      add("premium-spec-parity", canonicalStringify((media[0].spec ?? {}).premium) === canonicalStringify(premiumSpec(task, p)), "premium spec recomputed");
      const ticks = [...stored.matchAll(/<text class="cx-ticklbl"[^>]*>(-?\d+)<\/text>/g)].map((m) => m[1]!);
      add("tick-labels-integer", ticks.length >= 1 && ticks.every((t) => /^-?\d+$/.test(t)), `${ticks.length} integer tick labels`);
      add("axes-stronger-than-grid", axisHierarchyOk(stored), "axis width > major grid > minor grid");
      const svgTexts = [...stored.matchAll(/<text[^>]*>([^<]*)<\/text>/g)].map((m) => m[1]!);
      add("no-answer-label-in-svg", !svgTexts.some((t) => [",", "/", "="].some((ch) => t.includes(ch))), "no figure text states a coordinate, fraction, or equation");
      if (task === "plot_point") add("plot-point-target-absent", !stored.includes("<circle"), "the student grid plots no point");
      if (task === "equation_from_graph" || task === "equation_from_two_points") {
        const [m, c] = task === "equation_from_graph" ? paramsToLine(p) : solveLine2pts(p);
        const seg = lay ? clipLine(m, c, lay) : [];
        const okClip = seg.length > 0 && seg.every((s) => inCanvas(projX(lay as Lay, s[0]), projY(lay as Lay, s[1])));
        add("line-clipped-within-viewport", okClip, "clipped line endpoints lie inside the viewport");
      }
      if (task === "equation_from_graph") {
        const [m, c] = paramsToLine(p);
        add("lattice-anchors-readable", lay !== null && latticePointsOnLine(m, c, lay).length >= 2, "the line crosses >= 2 readable lattice points");
      }
    }
  } else {
    add("media-absent-for-text-task", (item.media ?? []).length === 0, "interpret_mx_c has no figure");
  }

  const acc = item.accessibility ?? {};
  add("a11y-fields-present", ["spokenMath", "altText", "longDescription"].every((k) => k in acc), "a11y fields present");
  add("a11y-non-color", acc.nonColorIndicators === true, "no colour-only information");
  if (task !== "read_point" && task !== "interpret_mx_c" && ["(", "/", "="].some((ch) => aDisp.includes(ch))) {
    const a11yText = `${acc.altText ?? ""} ${acc.longDescription ?? ""}`;
    add("no-answer-in-accessibility-text", !a11yText.includes(aDisp), "the answer is not stated in the accessibility text");
  }
  if (FIGURE_TASKS.includes(task) && (item.media ?? []).length) {
    const cols = new Set([...(item.media[0].svg as string).matchAll(/(?:fill|stroke):(#[0-9a-fA-F]{3,6})/g)].map((m) => m[1]!));
    add("no-colour-only-information", [...cols].every((c) => GREYS.has(c)), `colours ${[...cols].sort().join(",")}`);
  }

  if (interaction === "multiple-choice") {
    const ds = item.distractors ?? [], opts = item.options ?? [];
    add("min-three-distractors", ds.length >= 3, `${ds.length} distractors`);
    const mids = ds.map((d: Json) => d.misconceptionId);
    add("distractors-distinct-misconceptions", new Set(mids).size === mids.length && mids.every((m: string) => m in MISCONCEPTIONS), String(mids));
    add("distractor-value-matches-rule", distractorValuesOk(task, p, ds), "each distractor equals its rule's recomputed value");
    add("distractor-not-answer", ds.every((d: Json) => d.display !== aDisp), "no distractor equals the answer");
    add("distractor-rationale-matches", ds.every((d: Json) => d.rationale === MISCONCEPTIONS[d.misconceptionId]?.observableError), "rationale matches the rule");
    add("distractor-feedback-present", ds.every((d: Json) => Boolean(MISCONCEPTIONS[d.misconceptionId]?.feedback)), "registry feedback present");
    const correct = opts.filter((o: Json) => o.correct);
    add("exactly-one-correct", correct.length === 1 && correct[0].display === aDisp, "one correct option matching the answer");
  }

  const prov = item.provenance ?? {};
  add("provenance-complete", prov.origin === "generated" && Boolean(prov.rightsStatus), "origin + rightsStatus present");
  add("version-fields-present", item.generatorId === GENERATOR_ID && item.generatorVersion === GENERATOR_VERSION, "generator id + version present");

  const status = checks.every((c) => c.result === "pass") ? "pass" : "fail";
  return { status, validatorVersion: VALIDATOR_VERSION, checks };
}
