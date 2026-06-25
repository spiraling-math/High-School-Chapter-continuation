/**
 * gen.measurement.mensuration v1.0.0 — TypeScript mirror of oracle/spi_oracle/mensuration.py.
 * Byte-for-byte parity with the Python oracle (canonical item + canonical dimensioned-figure SVG).
 * See the Python module for the full design notes (owner E/F/G/H/I/J). All eight tasks are
 * FREE-RESPONSE only (owner C); the answer is a structured dimensional Quantity (owner B/D).
 */

import { Rational } from "../../core/exact-math/rational.ts";
import { Mulberry32 } from "../../core/seeded-random/mulberry32.ts";
import { bandFromScore, round3, clamp01 } from "../../core/difficulty/band.ts";
import { canonicalStringify } from "../../core/serialization/canonical.ts";

// Local Json alias (matches the convention in the other domain mirrors, e.g. data-handling.ts).
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = any;
import {
  type Quantity, type BaseUnit, makeLength, makeArea, quantity,
  formatValue, formatQuantity, encodeQuantityAnswer, parseQuantity,
} from "./mensuration-units.ts";

export const GENERATOR_ID = "gen.measurement.mensuration";
export const GENERATOR_VERSION = "1.0.0";
export const VALIDATOR_VERSION = "1.0.0";
export const CALCULATOR_POLICY = "calculator-not-required";
export const SCHEMA_VERSION = "1.0.0";

export const TASKS = [
  "perimeter_rectangle", "perimeter_composite", "area_rectangle", "area_triangle",
  "area_composite", "missing_length_perimeter", "missing_dimension_area", "missing_triangle_base_height",
] as const;
export type Task = (typeof TASKS)[number];

export const OBJECTIVE_BY_TASK: Record<string, string> = {
  perimeter_rectangle: "SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01",
  perimeter_composite: "SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01",
  area_rectangle: "SPI.MIDDLE.MEAS.AREA.RECTANGLE.01",
  area_triangle: "SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01",
  area_composite: "SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01",
  missing_length_perimeter: "SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01",
  missing_dimension_area: "SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01",
  missing_triangle_base_height: "SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01",
};
export const HIDDEN_DIMENSION_TASKS = ["missing_length_perimeter", "missing_dimension_area", "missing_triangle_base_height"];
export const TRIANGLE_TASKS = ["area_triangle", "missing_triangle_base_height"];
export const COMPOSITE_TASKS = ["perimeter_composite", "area_composite"];
export const RATIONAL_ANSWER_TASKS = ["area_triangle", "missing_triangle_base_height"];

export const TASK_BANDS: Record<string, [number, number]> = {
  perimeter_rectangle: [1, 2], perimeter_composite: [2, 3], area_rectangle: [1, 2], area_triangle: [2, 3],
  area_composite: [3, 4], missing_length_perimeter: [2, 3], missing_dimension_area: [2, 3],
  missing_triangle_base_height: [3, 4],
};

const BASE_UNIT_POOL: BaseUnit[] = ["mm", "cm", "m"];
const MAX_PARAM_ATTEMPTS = 600;

export class UnsupportedInteractionError extends Error {}

function nInt(rng: Mulberry32, k: number): number { return rng.nextInt(0, k - 1); }

export function gridRound(num: number, den: number): number {
  const q = Math.floor(num / den);
  const r = num - q * den;
  return 2 * r >= den ? q + 1 : q;
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

// Canonical figure geometry (viewBox 0 0 1000 700).
const VIEW_W = 1000, VIEW_H = 700;
const SHAPE_X0 = 320, SHAPE_X1 = 700, SHAPE_Y0 = 200, SHAPE_Y1 = 520;
const SHAPE_W = SHAPE_X1 - SHAPE_X0, SHAPE_H = SHAPE_Y1 - SHAPE_Y0;
const DIM_OFF = 40, ARROW = 7;

const STYLE =
  ".cx-figure{font-family:'Segoe UI',system-ui,sans-serif}" +
  ".cx-shape{fill:var(--cx-fill,#eef2f7);stroke:var(--cx-edge,#1b2733);stroke-width:3;stroke-linejoin:round}" +
  ".cx-dimline{stroke:var(--cx-dim,#244);stroke-width:1.5}" +
  ".cx-ext{stroke:var(--cx-dim,#244);stroke-width:1}" +
  ".cx-arrow{fill:var(--cx-dim,#244)}" +
  ".cx-rightangle{fill:none;stroke:var(--cx-edge,#1b2733);stroke-width:1.5}" +
  ".cx-altitude{stroke:var(--cx-edge,#1b2733);stroke-width:1.5;stroke-dasharray:5 4}" +
  ".cx-dimlbl{fill:var(--cx-dim,#244);font-size:19px}" +
  ".cx-unknown{fill:var(--cx-unknown,#b91c1c);font-size:21px;font-weight:600}" +
  ".cx-nts{fill:var(--cx-nts,#92400e);font-size:17px;font-weight:600;letter-spacing:1px}" +
  ".cx-cut{stroke:var(--cx-cut,#2563eb);stroke-width:2;stroke-dasharray:6 4}" +
  ".cx-result{fill:var(--cx-result,#166534);font-size:21px;font-weight:600}" +
  ".cx-keylbl{fill:var(--cx-result,#166534);font-size:19px;font-weight:600}";

function R(n: number): Rational { return new Rational(n, 1); }
function ratMin(a: Rational, b: Rational): Rational { return a.num * b.den <= b.num * a.den ? a : b; }

// --- Shape model (discriminated union) ---
function rectVertices(w: number, h: number): any[] {
  return [[R(0), R(0)], [R(w), R(0)], [R(w), R(h)], [R(0), R(h)]];
}
function lshapeVertices(W: number, H: number, a: number, b: number, corner: string): any[] {
  let pts: any[];
  if (corner === "TR") pts = [[0, 0], [W, 0], [W, H - b], [W - a, H - b], [W - a, H], [0, H]];
  else if (corner === "TL") pts = [[0, 0], [W, 0], [W, H], [a, H], [a, H - b], [0, H - b]];
  else if (corner === "BR") pts = [[0, 0], [W - a, 0], [W - a, b], [W, b], [W, H], [0, H]];
  else pts = [[a, 0], [W, 0], [W, H], [0, H], [0, b], [a, b]];
  return pts.map(([x, y]) => [R(x), R(y)] as any);
}
interface DRect { x0: number; y0: number; w: number; h: number; sign: number; }
function lshapeDecomposition(W: number, H: number, a: number, b: number, corner: string, mode: string): any[] {
  if (mode === "subtractive") {
    const notch: Record<string, [number, number]> = { TR: [W - a, H - b], TL: [0, H - b], BR: [W - a, 0], BL: [0, 0] };
    const [nx, ny] = notch[corner] as number[];
    return [{ x0: 0, y0: 0, w: W, h: H, sign: 1 }, { x0: nx, y0: ny, w: a, h: b, sign: -1 }];
  }
  if (corner === "TR") return [{ x0: 0, y0: 0, w: W, h: H - b, sign: 1 }, { x0: 0, y0: H - b, w: W - a, h: b, sign: 1 }];
  if (corner === "TL") return [{ x0: 0, y0: 0, w: W, h: H - b, sign: 1 }, { x0: a, y0: H - b, w: W - a, h: b, sign: 1 }];
  if (corner === "BR") return [{ x0: 0, y0: b, w: W, h: H - b, sign: 1 }, { x0: 0, y0: 0, w: W - a, h: b, sign: 1 }];
  return [{ x0: 0, y0: b, w: W, h: H - b, sign: 1 }, { x0: a, y0: 0, w: W - a, h: b, sign: 1 }];
}

interface Shape {
  kind: string; baseUnit: BaseUnit; vertices: any[]; bbox: [number, number];
  width?: number; height?: number; W?: number; H?: number; a?: number; b?: number;
  corner?: string; decompMode?: string; base?: number; apexOffset?: number; decomposition?: any[];
}
function buildShape(task: string, p: Json): Shape {
  const bu = p.baseUnit as BaseUnit;
  if (p.kind === "rectangle") {
    const w = p.width as number, h = p.height as number;
    return { kind: "rectangle", baseUnit: bu, width: w, height: h, vertices: rectVertices(w, h), bbox: [w, h] };
  }
  if (p.kind === "rectilinear_composite") {
    const W = p.W as number, H = p.H as number, a = p.a as number, b = p.b as number, corner = p.corner as string;
    return {
      kind: "rectilinear_composite", baseUnit: bu, W, H, a, b, corner, decompMode: p.decompMode as string,
      vertices: lshapeVertices(W, H, a, b, corner), decomposition: lshapeDecomposition(W, H, a, b, corner, p.decompMode as string),
      bbox: [W, H],
    };
  }
  const base = p.base as number, height = p.height as number, apex = p.apexOffset as number;
  return {
    kind: "triangle_base_height", baseUnit: bu, base, height, apexOffset: apex,
    vertices: [[R(0), R(0)], [R(base), R(0)], [R(apex), R(height)]], bbox: [base, height],
  };
}

// --- Geometry math (independent routes) ---
function polygonAreaShoelace(verts: any[]): Rational {
  let s = new Rational(0, 1);
  for (let i = 0; i < verts.length; i++) {
    const [x1, y1] = verts[i], [x2, y2] = verts[(i + 1) % verts.length];
    s = s.add(x1.mul(y2)).sub(x2.mul(y1));
  }
  return s.abs().div(R(2));
}
function polygonPerimeter(verts: any[]): Rational {
  let per = new Rational(0, 1);
  for (let i = 0; i < verts.length; i++) {
    const [x1, y1] = verts[i], [x2, y2] = verts[(i + 1) % verts.length];
    per = per.add(x2.sub(x1).abs()).add(y2.sub(y1).abs());
  }
  return per;
}
function isClosedOrthogonalSimple(verts: any[]): [boolean, string] {
  const n = verts.length;
  if (n < 4) return [false, "too few vertices"];
  const edges: any[] = [];
  for (let i = 0; i < n; i++) {
    const a = verts[i], b = verts[(i + 1) % n];
    if (a[0].equals(b[0]) && a[1].equals(b[1])) return [false, "zero-length edge / duplicate vertex"];
    if (!a[0].equals(b[0]) && !a[1].equals(b[1])) return [false, "non-orthogonal edge"];
    edges.push([a, b]);
  }
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      if (j === i || (i === 0 && j === n - 1) || j === i + 1) continue;
      if (segmentsTouch(edges[i], edges[j])) return [false, "self-intersection"];
    }
  }
  return [true, ""];
}
function rnum(r: Rational): number { return r.num / r.den; }
function segmentsTouch(e1: [any, any], e2: [any, any]): boolean {
  const [[ax1, ay1], [ax2, ay2]] = e1, [[bx1, by1], [bx2, by2]] = e2;
  const axlo = Math.min(rnum(ax1), rnum(ax2)), axhi = Math.max(rnum(ax1), rnum(ax2));
  const aylo = Math.min(rnum(ay1), rnum(ay2)), ayhi = Math.max(rnum(ay1), rnum(ay2));
  const bxlo = Math.min(rnum(bx1), rnum(bx2)), bxhi = Math.max(rnum(bx1), rnum(bx2));
  const bylo = Math.min(rnum(by1), rnum(by2)), byhi = Math.max(rnum(by1), rnum(by2));
  const ixlo = Math.max(axlo, bxlo), ixhi = Math.min(axhi, bxhi);
  const iylo = Math.max(aylo, bylo), iyhi = Math.min(ayhi, byhi);
  return ixlo <= ixhi && iylo <= iyhi;
}
function rectsOverlap(r1: DRect, r2: DRect): boolean {
  const ax1 = r1.x0 + r1.w, ay1 = r1.y0 + r1.h, bx1 = r2.x0 + r2.w, by1 = r2.y0 + r2.h;
  return Math.min(ax1, bx1) > Math.max(r1.x0, r2.x0) && Math.min(ay1, by1) > Math.max(r1.y0, r2.y0);
}
function decompositionArea(decomp: any[]): Rational {
  let s = new Rational(0, 1);
  for (const r of decomp) s = s.add(new Rational(r.w * r.h * r.sign, 1));
  return s;
}

// --- Backward construction ---
const GOOD_RATIO = new Rational(7, 2);
function ratioOk(w: number, h: number): boolean {
  const lo = Math.min(w, h), hi = Math.max(w, h);
  return lo > 0 && new Rational(hi, lo).num * GOOD_RATIO.den <= GOOD_RATIO.num * new Rational(hi, lo).den;
}
function pickUnit(rng: Mulberry32): BaseUnit { return BASE_UNIT_POOL[nInt(rng, 3)] as BaseUnit; }

function drawPerimeterRectangle(rng: Mulberry32): Json | null {
  const w = rng.nextInt(3, 19), h = rng.nextInt(2, 14);
  if (w === h || !ratioOk(w, h)) return null;
  return { task: "perimeter_rectangle", kind: "rectangle", baseUnit: pickUnit(rng), width: w, height: h };
}
function drawAreaRectangle(rng: Mulberry32): Json | null {
  const w = rng.nextInt(3, 18), h = rng.nextInt(2, 13);
  if (!ratioOk(w, h)) return null;
  return { task: "area_rectangle", kind: "rectangle", baseUnit: pickUnit(rng), width: w, height: h };
}
function drawAreaTriangle(rng: Mulberry32): Json | null {
  const base = rng.nextInt(3, 18), height = rng.nextInt(2, 13), apex = rng.nextInt(0, base);
  if (!ratioOk(base, height)) return null;
  return { task: "area_triangle", kind: "triangle_base_height", baseUnit: pickUnit(rng), base, height, apexOffset: apex };
}
function drawLshape(rng: Mulberry32, task: string): Json | null {
  const W = rng.nextInt(8, 18), H = rng.nextInt(6, 14), a = rng.nextInt(2, W - 3), b = rng.nextInt(2, H - 3);
  const corner = ["TR", "TL", "BR", "BL"][nInt(rng, 4)];
  const mode = nInt(rng, 2) === 0 ? "subtractive" : "additive";
  if (a >= W || b >= H || W - a < 2 || H - b < 2 || !ratioOk(W, H)) return null;
  return { task, kind: "rectilinear_composite", baseUnit: pickUnit(rng), W, H, a, b, corner, decompMode: mode };
}
function drawMissingLengthPerimeter(rng: Mulberry32): Json | null {
  const w = rng.nextInt(3, 18), h = rng.nextInt(2, 14);
  if (w === h) return null;
  const hidden = nInt(rng, 2) === 0 ? "height" : "width";
  return { task: "missing_length_perimeter", kind: "rectangle", baseUnit: pickUnit(rng), width: w, height: h, given: "perimeter", hidden, perimeter: 2 * (w + h) };
}
function drawMissingDimensionArea(rng: Mulberry32): Json | null {
  const w = rng.nextInt(3, 18), h = rng.nextInt(2, 13);
  if (w === h) return null;
  const hidden = nInt(rng, 2) === 0 ? "height" : "width";
  return { task: "missing_dimension_area", kind: "rectangle", baseUnit: pickUnit(rng), width: w, height: h, given: "area", hidden, area: w * h };
}
function drawMissingTriangle(rng: Mulberry32): Json | null {
  const base = rng.nextInt(3, 18), height = rng.nextInt(2, 13), apex = rng.nextInt(0, base);
  if (base === height) return null;
  const hidden = nInt(rng, 2) === 0 ? "height" : "base";
  return { task: "missing_triangle_base_height", kind: "triangle_base_height", baseUnit: pickUnit(rng), base, height, apexOffset: apex, given: "area", hidden, area2: base * height };
}
const DRAW: Record<string, (rng: Mulberry32) => Json | null> = {
  perimeter_rectangle: drawPerimeterRectangle,
  area_rectangle: drawAreaRectangle,
  area_triangle: drawAreaTriangle,
  perimeter_composite: (r) => drawLshape(r, "perimeter_composite"),
  area_composite: (r) => drawLshape(r, "area_composite"),
  missing_length_perimeter: drawMissingLengthPerimeter,
  missing_dimension_area: drawMissingDimensionArea,
  missing_triangle_base_height: drawMissingTriangle,
};

// --- Solver ---
export function solve(task: string, p: Json): Quantity {
  const bu = p.baseUnit as BaseUnit;
  switch (task) {
    case "perimeter_rectangle": return makeLength(2 * ((p.width as number) + (p.height as number)), bu);
    case "area_rectangle": return makeArea((p.width as number) * (p.height as number), bu);
    case "area_triangle": return makeArea(new Rational((p.base as number) * (p.height as number), 2), bu);
    case "perimeter_composite": return makeLength(2 * ((p.W as number) + (p.H as number)), bu);
    case "area_composite": return makeArea((p.W as number) * (p.H as number) - (p.a as number) * (p.b as number), bu);
    case "missing_length_perimeter": {
      const known = p.hidden === "height" ? (p.width as number) : (p.height as number);
      return makeLength(new Rational(p.perimeter as number, 2).sub(R(known)), bu);
    }
    case "missing_dimension_area": {
      const known = p.hidden === "height" ? (p.width as number) : (p.height as number);
      return makeLength(new Rational(p.area as number, known), bu);
    }
    case "missing_triangle_base_height": {
      const known = p.hidden === "height" ? (p.base as number) : (p.height as number);
      return makeLength(new Rational(p.area2 as number, known), bu);
    }
  }
  throw new Error(task);
}
function isExactAcceptable(task: string, _p: Json, q: Quantity): boolean {
  if (q.value.num <= 0) return false;
  if (RATIONAL_ANSWER_TASKS.includes(task)) return true;
  return q.value.den === 1;
}

// --- Layout ---
function layout(shape: Shape, toScale: boolean): any[] {
  const verts = shape.vertices, [bw, bh] = shape.bbox;
  if (toScale) {
    const sx = new Rational(SHAPE_W, 1).div(R(bw)), sy = new Rational(SHAPE_H, 1).div(R(bh));
    const s = ratMin(sx, sy);
    const pw = R(bw).mul(s), ph = R(bh).mul(s);
    const usedw = gridRound(pw.num, pw.den), usedh = gridRound(ph.num, ph.den);
    const x0 = SHAPE_X0 + Math.floor((SHAPE_W - usedw) / 2);
    const ybot = SHAPE_Y1 - Math.floor((SHAPE_H - usedh) / 2);
    return verts.map(([x, y]) => {
      const xs = x.mul(s), ys = y.mul(s);
      return [x0 + gridRound(xs.num, xs.den), ybot - gridRound(ys.num, ys.den)] as [number, number];
    });
  }
  const fixedW = 360, fixedH = 250;
  const x0 = SHAPE_X0 + Math.floor((SHAPE_W - fixedW) / 2);
  const ybot = SHAPE_Y1 - Math.floor((SHAPE_H - fixedH) / 2);
  let tmpl: any[];
  if (shape.kind === "rectangle") tmpl = [[R(0), R(0)], [R(1), R(0)], [R(1), R(1)], [R(0), R(1)]];
  else if (shape.kind === "triangle_base_height") tmpl = [[R(0), R(0)], [R(1), R(0)], [new Rational(2, 5), R(1)]];
  else tmpl = verts.map(([x, y]) => [x.div(R(bw)), y.div(R(bh))] as any);
  return tmpl.map(([fx, fy]) => {
    const xs = fx.mul(R(fixedW)), ys = fy.mul(R(fixedH));
    return [x0 + gridRound(xs.num, xs.den), ybot - gridRound(ys.num, ys.den)] as [number, number];
  });
}

// --- Dimension primitives ---
function arrow(out: string[], x: number, y: number, dx: number, dy: number): void {
  if (dx !== 0) {
    const back = x - dx * ARROW;
    out.push(`<polygon class="cx-arrow" points="${x},${y} ${back},${y - 4} ${back},${y + 4}"/>`);
  } else {
    const back = y - dy * ARROW;
    out.push(`<polygon class="cx-arrow" points="${x},${y} ${x - 4},${back} ${x + 4},${back}"/>`);
  }
}
function dimH(out: string[], x1: number, x2: number, yedge: number, off: number, label: string, cls = "cx-dimlbl"): void {
  const yd = yedge + off;
  out.push(`<line class="cx-ext" x1="${x1}" y1="${yedge}" x2="${x1}" y2="${yd + (off > 0 ? 4 : -4)}"/>`);
  out.push(`<line class="cx-ext" x2="${x2}" y1="${yedge}" x1="${x2}" y2="${yd + (off > 0 ? 4 : -4)}"/>`);
  out.push(`<line class="cx-dimline" x1="${x1}" y1="${yd}" x2="${x2}" y2="${yd}"/>`);
  arrow(out, x1, yd, 1, 0); arrow(out, x2, yd, -1, 0);
  const ty = off > 0 ? yd - 8 : yd + 20;
  out.push(`<text class="${cls}" x="${Math.floor((x1 + x2) / 2)}" y="${ty}" text-anchor="middle">${esc(label)}</text>`);
}
function dimV(out: string[], y1: number, y2: number, xedge: number, off: number, label: string, cls = "cx-dimlbl"): void {
  const xd = xedge + off;
  out.push(`<line class="cx-ext" x1="${xedge}" y1="${y1}" x2="${xd + (off > 0 ? 4 : -4)}" y2="${y1}"/>`);
  out.push(`<line class="cx-ext" x1="${xedge}" y2="${y2}" x2="${xd + (off > 0 ? 4 : -4)}" y1="${y2}"/>`);
  out.push(`<line class="cx-dimline" x1="${xd}" y1="${y1}" x2="${xd}" y2="${y2}"/>`);
  arrow(out, xd, y1, 0, 1); arrow(out, xd, y2, 0, -1);
  const anchor = off > 0 ? "start" : "end";
  const tx = off > 0 ? xd + 8 : xd - 8;
  out.push(`<text class="${cls}" x="${tx}" y="${Math.floor((y1 + y2) / 2) + 6}" text-anchor="${anchor}">${esc(label)}</text>`);
}
function rightAngle(out: string[], cx: number, cy: number, sx: number, sy: number, size = 14): void {
  out.push(`<polyline class="cx-rightangle" points="${cx + sx * size},${cy} ${cx + sx * size},${cy + sy * size} ${cx},${cy + sy * size}"/>`);
}
function labelValue(value: number | string, unit: string): string { return `${value} ${unit}`; }

// --- SVG channels ---
function baseGroup(_task: string, _p: Json, shape: Shape, px: any[]): string[] {
  const out: string[] = ['<g class="cx-base">'];
  out.push(`<polygon class="cx-shape" points="${px.map(([x, y]) => `${x},${y}`).join(" ")}"/>`);
  if (shape.kind === "triangle_base_height") {
    const v0 = px[0], v1 = px[1], v2 = px[2];
    const footx = v2[0], footy = v0[1];
    out.push(`<line class="cx-altitude" x1="${footx}" y1="${footy}" x2="${v2[0]}" y2="${v2[1]}"/>`);
    const sx = v2[0] <= Math.floor((v0[0] + v1[0]) / 2) ? 1 : -1;
    rightAngle(out, footx, footy, sx, -1, 13);
  } else if (shape.kind === "rectangle") {
    const x0 = Math.min(...px.map((q) => q[0])), y1 = Math.max(...px.map((q) => q[1]));
    rightAngle(out, x0, y1, 1, -1, 13);
  }
  out.push("</g>");
  return out;
}
function annotGroup(task: string, p: Json, shape: Shape, px: any[]): string[] {
  const out: string[] = ['<g class="cx-annot">'];
  const unit = p.baseUnit as string;
  const kind = shape.kind;
  if (kind === "rectangle") {
    const [bx0, by0] = px[0], [bx1, by1] = px[1], [, ty1] = px[2];
    const w = p.width as number, h = p.height as number, hide = p.hidden;
    if (hide !== "width") dimH(out, bx0, bx1, by0, DIM_OFF, labelValue(w, unit));
    else dimH(out, bx0, bx1, by0, DIM_OFF, "?", "cx-unknown");
    if (hide !== "height") dimV(out, ty1, by1, bx1, DIM_OFF, labelValue(h, unit));
    else dimV(out, ty1, by1, bx1, DIM_OFF, "?", "cx-unknown");
  } else if (kind === "triangle_base_height") {
    const v0 = px[0], v1 = px[1], v2 = px[2];
    const base = p.base as number, height = p.height as number, hide = p.hidden;
    if (hide !== "base") dimH(out, v0[0], v1[0], v0[1], DIM_OFF, labelValue(base, unit));
    else dimH(out, v0[0], v1[0], v0[1], DIM_OFF, "?", "cx-unknown");
    const footx = v2[0];
    if (hide !== "height") out.push(`<text class="cx-dimlbl" x="${footx + 10}" y="${Math.floor((v0[1] + v2[1]) / 2)}" text-anchor="start">${esc(labelValue(height, unit))}</text>`);
    else out.push(`<text class="cx-unknown" x="${footx + 10}" y="${Math.floor((v0[1] + v2[1]) / 2)}" text-anchor="start">?</text>`);
  } else {
    annotComposite(out, p, shape, px, unit);
  }
  if (HIDDEN_DIMENSION_TASKS.includes(task)) {
    out.push(`<text class="cx-nts" x="${Math.floor(VIEW_W / 2)}" y="170" text-anchor="middle">NOT TO SCALE</text>`);
  }
  out.push("</g>");
  return out;
}
function annotComposite(out: string[], p: Json, shape: Shape, px: any[], unit: string): void {
  const W = p.W as number, H = p.H as number, a = p.a as number, b = p.b as number, corner = p.corner as string;
  const xs = px.map((q) => q[0]), ys = px.map((q) => q[1]);
  const xLeft = Math.min(...xs), xRight = Math.max(...xs), yTop = Math.min(...ys), yBot = Math.max(...ys);
  dimH(out, xLeft, xRight, yBot, DIM_OFF, labelValue(W, unit));
  const fullLeft = corner === "TR" || corner === "BR";
  if (fullLeft) dimV(out, yTop, yBot, xLeft, -DIM_OFF, labelValue(H, unit));
  else dimV(out, yTop, yBot, xRight, DIM_OFF, labelValue(H, unit));
  labelNotch(out, px, shape.vertices, a, b, unit);
}
function labelNotch(out: string[], px: any[], verts: any[], a: number, b: number, unit: string): void {
  const xs = verts.map((v) => rnum(v[0])), ys = verts.map((v) => rnum(v[1]));
  const xmin = Math.min(...xs), xmax = Math.max(...xs), ymin = Math.min(...ys), ymax = Math.max(...ys);
  let r = -1;
  for (let i = 0; i < verts.length; i++) {
    const x = rnum(verts[i][0]), y = rnum(verts[i][1]);
    if (x > xmin && x < xmax && y > ymin && y < ymax) { r = i; break; }
  }
  if (r < 0) return;
  const n = px.length;
  for (const j of [r - 1, r]) {
    const [x1, y1] = px[((j % n) + n) % n], [x2, y2] = px[(j + 1) % n];
    const midx = Math.floor((x1 + x2) / 2), midy = Math.floor((y1 + y2) / 2);
    if (y1 === y2) out.push(`<text class="cx-dimlbl" x="${midx}" y="${midy - 8}" text-anchor="middle">${esc(labelValue(a, unit))}</text>`);
    else out.push(`<text class="cx-dimlbl" x="${midx + 8}" y="${midy}" text-anchor="start">${esc(labelValue(b, unit))}</text>`);
  }
}
function overlayGroup(task: string, p: Json, shape: Shape, px: any[], answer: Quantity): string[] {
  const out: string[] = ['<g class="cx-overlay">'];
  const unit = p.baseUnit as string, kind = shape.kind;
  if (HIDDEN_DIMENSION_TASKS.includes(task)) {
    const val = formatValue(answer.value);
    if (kind === "rectangle") {
      const [bx0, by0] = px[0], [bx1, by1] = px[1], [, ty1] = px[2];
      if (p.hidden === "width") out.push(`<text class="cx-keylbl" x="${Math.floor((bx0 + bx1) / 2)}" y="${by0 + DIM_OFF - 8}" text-anchor="middle">${esc(labelValue(val, unit))}</text>`);
      else out.push(`<text class="cx-keylbl" x="${bx1 + DIM_OFF + 8}" y="${Math.floor((ty1 + by1) / 2) + 6}" text-anchor="start">${esc(labelValue(val, unit))}</text>`);
    } else if (kind === "triangle_base_height") {
      const v0 = px[0], v1 = px[1], v2 = px[2];
      if (p.hidden === "base") out.push(`<text class="cx-keylbl" x="${Math.floor((v0[0] + v1[0]) / 2)}" y="${v0[1] + DIM_OFF - 8}" text-anchor="middle">${esc(labelValue(val, unit))}</text>`);
      else out.push(`<text class="cx-keylbl" x="${v2[0] + 10}" y="${Math.floor((v0[1] + v2[1]) / 2)}" text-anchor="start">${esc(labelValue(val, unit))}</text>`);
    }
  }
  if (task === "area_composite") overlayCut(out, p, shape, px);
  out.push(`<text class="cx-result" x="${Math.floor(VIEW_W / 2)}" y="${VIEW_H - 40}" text-anchor="middle">${esc(formatQuantity(answer))}</text>`);
  out.push("</g>");
  return out;
}
function overlayCut(out: string[], p: Json, shape: Shape, px: any[]): void {
  const decomp = lshapeDecomposition(p.W as number, p.H as number, p.a as number, p.b as number, p.corner as string, "additive");
  const r0 = decomp[0];
  const [, bh] = shape.bbox;
  const xs = px.map((q) => q[0]), ys = px.map((q) => q[1]);
  const xLeft = Math.min(...xs), xRight = Math.max(...xs), yBot = Math.max(...ys), yTop = Math.min(...ys);
  const cutFrac = new Rational(r0.h, bh);
  const prod = cutFrac.mul(R(yBot - yTop));
  const cy = yBot - gridRound(prod.num, prod.den);
  out.push(`<line class="cx-cut" x1="${xLeft}" y1="${cy}" x2="${xRight}" y2="${cy}"/>`);
}
function renderSvg(task: string, p: Json, shape: Shape, answer: Quantity, channel: string, acc: Acc): string {
  const toScale = !HIDDEN_DIMENSION_TASKS.includes(task);
  const px = layout(shape, toScale);
  const out: string[] = [
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VIEW_W} ${VIEW_H}" role="img" class="cx-figure" aria-label="${esc(acc.alt)}">`,
    `<title>${esc(acc.title)}</title>`,
    `<desc>${esc(acc.desc)}</desc>`,
    `<style>${STYLE}</style>`,
  ];
  out.push(...baseGroup(task, p, shape, px));
  out.push(...annotGroup(task, p, shape, px));
  if (channel === "answer-key") out.push(...overlayGroup(task, p, shape, px, answer));
  out.push("</svg>");
  return out.join("");
}

// --- Prompt / solution / difficulty / accessibility ---
const TASK_PROMPT: Record<string, string> = {
  perimeter_rectangle: "Work out the perimeter of the rectangle shown. Give your answer in the correct units.",
  perimeter_composite: "Work out the perimeter of the shape shown by adding the lengths around its outside. Give your answer in the correct units.",
  area_rectangle: "Work out the area of the rectangle shown. Give your answer in the correct square units.",
  area_triangle: "Work out the area of the triangle using its base and the perpendicular height shown. Give your answer in the correct square units.",
  area_composite: "Work out the area of the shape shown by splitting it into rectangles. Give your answer in the correct square units.",
  missing_length_perimeter: "The perimeter of the rectangle is given. Work out the missing side length marked “?”. Give your answer in the correct units.",
  missing_dimension_area: "The area of the rectangle is given. Work out the missing side length marked “?”. Give your answer in the correct units.",
  missing_triangle_base_height: "The area of the triangle is given. Work out the missing measurement marked “?”. Give your answer in the correct units.",
};
function buildPrompt(task: string, p: Json): Json {
  const unit = p.baseUnit as string;
  const blocks: Json[] = [{ kind: "media-ref", ref: "fig-1" }];
  let pre = "";
  if (task === "missing_length_perimeter") pre = `The perimeter of this rectangle is ${2 * ((p.width as number) + (p.height as number))} ${unit}. `;
  else if (task === "missing_dimension_area") pre = `The area of this rectangle is ${p.area} ${unit}^2. `;
  else if (task === "missing_triangle_base_height") pre = `The area of this triangle is ${formatValue(new Rational(p.area2 as number, 2))} ${unit}^2. `;
  const instr = pre + TASK_PROMPT[task];
  blocks.push({ kind: "text", text: instr });
  return { blocks, instruction: instr };
}
function buildSolution(task: string, p: Json, answer: Quantity): Json {
  const unit = p.baseUnit as string;
  const steps: Json[] = [];
  const final = formatQuantity(answer);
  const step = (t: string, r: string) => steps.push({ number: steps.length + 1, transformation: t, intermediateResult: r });
  if (task === "perimeter_rectangle") {
    const w = p.width as number, h = p.height as number;
    step("Add the four side lengths", `${w} + ${h} + ${w} + ${h} ${unit}`);
    step("Or use 2 × (length + width)", `2 × (${w} + ${h}) = ${final}`);
  } else if (task === "area_rectangle") {
    const w = p.width as number, h = p.height as number;
    step("Multiply length by width", `${w} × ${h}`);
    step("State the area in square units", final);
  } else if (task === "area_triangle") {
    const b = p.base as number, h = p.height as number;
    step("Multiply base by perpendicular height", `${b} × ${h} = ${b * h}`);
    step("Halve the product (½ × base × height)", final);
  } else if (task === "perimeter_composite") {
    step("Find any unlabelled outer edge from the given lengths", "use width − part and height − part");
    step("Add every edge around the outside once (no inside lines)", final);
  } else if (task === "area_composite") {
    const W = p.W as number, H = p.H as number, a = p.a as number, b = p.b as number;
    if (p.decompMode === "subtractive") {
      step("Area of the surrounding rectangle", `${W} × ${H} = ${W * H}`);
      step("Subtract the missing corner rectangle", `${W * H} − ${a} × ${b} = ${final}`);
    } else {
      const d = lshapeDecomposition(W, H, a, b, p.corner as string, "additive");
      step("Split into two rectangles and find each area", `${d[0].w}×${d[0].h} and ${d[1].w}×${d[1].h}`);
      step("Add the rectangle areas", final);
    }
  } else if (task === "missing_length_perimeter") {
    const known = p.hidden === "height" ? (p.width as number) : (p.height as number);
    const P = p.perimeter as number;
    step("Halve the perimeter to get length + width", `${P} ÷ 2 = ${Math.floor(P / 2)}`);
    step("Subtract the known side", `${Math.floor(P / 2)} − ${known} = ${final}`);
  } else if (task === "missing_dimension_area") {
    const known = p.hidden === "height" ? (p.width as number) : (p.height as number);
    step("Divide the area by the known side", `${p.area} ÷ ${known} = ${final}`);
  } else if (task === "missing_triangle_base_height") {
    const known = p.hidden === "height" ? (p.base as number) : (p.height as number);
    step("Double the area (undo the ½)", `2 × ${formatValue(new Rational(p.area2 as number, 2))} = ${p.area2}`);
    step("Divide by the known measurement", `${p.area2} ÷ ${known} = ${final}`);
  }
  return { steps };
}

const AXIS_FLOORS: Record<string, { rs: number; id: number; dn: number }> = {
  perimeter_rectangle: { rs: 0.05, id: 0.10, dn: 0.10 },
  area_rectangle: { rs: 0.08, id: 0.12, dn: 0.10 },
  area_triangle: { rs: 0.45, id: 0.35, dn: 0.25 },
  perimeter_composite: { rs: 0.37, id: 0.40, dn: 0.35 },
  area_composite: { rs: 0.70, id: 0.55, dn: 0.60 },
  missing_length_perimeter: { rs: 0.40, id: 0.40, dn: 0.25 },
  missing_dimension_area: { rs: 0.40, id: 0.40, dn: 0.25 },
  missing_triangle_base_height: { rs: 0.70, id: 0.50, dn: 0.30 },
};
function taskNumbers(p: Json): number[] {
  return ["width", "height", "base", "W", "H", "a", "b"].filter((k) => k in p).map((k) => p[k] as number);
}
function buildDifficulty(task: string, p: Json): Json {
  const [lo, hi] = TASK_BANDS[task] as [number, number];
  const fl = AXIS_FLOORS[task]!;
  const nums = taskNumbers(p);
  const nmax = nums.length ? Math.max(...nums) : 1;
  const numeric = clamp01((nmax - 2) / 18.0);
  const axes: Json = {
    numericalComplexity: round3(numeric),
    reasoningSteps: round3(fl.rs),
    interpretationDemand: round3(fl.id),
    informationDensity: round3(fl.dn),
    representation: 0.5,
    scaffolding: round3(HIDDEN_DIMENSION_TASKS.includes(task) ? 0.4 : 0.25),
  };
  const score = 0.40 * fl.rs + 0.22 * fl.id + 0.20 * numeric + 0.18 * fl.dn;
  const band = Math.max(lo, Math.min(hi, bandFromScore(score)));
  return { overallBand: band, axes };
}

interface Acc { spoken: string; alt: string; desc: string; title: string; dataTable: Json; }
function buildAccessibility(task: string, p: Json, shape: Shape): Acc {
  const unit = p.baseUnit as string;
  const unitWord = ({ mm: "millimetres", cm: "centimetres", m: "metres" } as Record<string, string>)[unit] as string;
  const kind = shape.kind;
  const rows: { label: string; value: string }[] = [];
  const nts = HIDDEN_DIMENSION_TASKS.includes(task) ? " The figure is not drawn to scale." : "";
  let shapeWord: string;
  if (kind === "rectangle") {
    if (p.hidden !== "width") rows.push({ label: "width", value: `${p.width} ${unit}` });
    if (p.hidden !== "height") rows.push({ label: "height", value: `${p.height} ${unit}` });
    shapeWord = "rectangle";
  } else if (kind === "triangle_base_height") {
    if (p.hidden !== "base") rows.push({ label: "base", value: `${p.base} ${unit}` });
    if (p.hidden !== "height") rows.push({ label: "perpendicular height", value: `${p.height} ${unit}` });
    shapeWord = "triangle with a perpendicular height marked";
  } else {
    rows.push({ label: "overall width", value: `${p.W} ${unit}` });
    rows.push({ label: "overall height", value: `${p.H} ${unit}` });
    rows.push({ label: "notch width", value: `${p.a} ${unit}` });
    rows.push({ label: "notch height", value: `${p.b} ${unit}` });
    shapeWord = "L-shaped composite rectilinear shape";
  }
  if (task === "missing_length_perimeter") rows.push({ label: "perimeter (given)", value: `${p.perimeter} ${unit}` });
  else if (task === "missing_dimension_area") rows.push({ label: "area (given)", value: `${p.area} ${unit} squared` });
  else if (task === "missing_triangle_base_height") rows.push({ label: "area (given)", value: `${formatValue(new Rational(p.area2 as number, 2))} ${unit} squared` });
  const given = rows.map((r) => `${r.label} ${r.value}`).join("; ");
  const spoken = `A ${shapeWord} measured in ${unitWord}. Given measurements: ${given}.${nts}`;
  const alt = `A ${shapeWord} with labelled measurements.`;
  return {
    spoken, alt, desc: spoken, title: alt,
    dataTable: { caption: `Given measurements of the ${shapeWord}`, columns: ["measurement", "value"], rows: rows.map((r) => [r.label, r.value]) },
  };
}

// --- Generate ---
export function generate(seed: number, config: Json = {}): Json {
  const interaction = (config.interactionType as string) ?? "free-response";
  if (interaction !== "free-response") {
    throw new UnsupportedInteractionError(`gen.measurement.mensuration v1.0.0 supports only free-response; got '${interaction}'.`);
  }
  const task = config.task as string | undefined;
  const pool = task ? [task] : [...TASKS];
  const rng = new Mulberry32(seed);
  let chosen: Json | null = null;
  let answer: Quantity | null = null;
  for (let i = 0; i < MAX_PARAM_ATTEMPTS; i++) {
    const t = pool[nInt(rng, pool.length)] as string;
    const drawn = DRAW[t]!(rng);
    if (drawn === null) continue;
    const q = solve(t, drawn);
    if (!isExactAcceptable(t, drawn, q)) continue;
    chosen = drawn; answer = q; break;
  }
  if (chosen === null || answer === null) throw new Error("could not find acceptable mensuration parameters");

  const t = chosen.task as string;
  const shape = buildShape(t, chosen);
  const acc = buildAccessibility(t, chosen, shape);
  const studentSvg = renderSvg(t, chosen, shape, answer, "student", acc);
  const keySvg = renderSvg(t, chosen, shape, answer, "answer-key", acc);

  return {
    itemId: `ITEM-${GENERATOR_ID.replace(/\./g, "-")}-${seed}-${t}`,
    schemaVersion: SCHEMA_VERSION,
    objectiveIds: [OBJECTIVE_BY_TASK[t]],
    generatorId: GENERATOR_ID,
    generatorVersion: GENERATOR_VERSION,
    seed,
    params: { ...chosen },
    interactionType: "free-response",
    prompt: buildPrompt(t, chosen),
    answer: encodeQuantityAnswer(answer) as Json,
    solution: buildSolution(t, chosen, answer),
    difficulty: buildDifficulty(t, chosen),
    calculatorPolicy: CALCULATOR_POLICY,
    media: [{
      id: "fig-1", kind: "svg", svg: studentSvg,
      toScale: !HIDDEN_DIMENSION_TASKS.includes(t),
      altText: acc.alt, longDescription: acc.spoken,
      dataTableFallback: acc.dataTable,
      spec: { answerKeySvg: keySvg, notToScale: HIDDEN_DIMENSION_TASKS.includes(t) },
    }],
    accessibility: { spokenMath: acc.spoken, altText: acc.alt, longDescription: acc.spoken, nonColorIndicators: true },
    provenance: { origin: "generated", rightsStatus: "academy-owned", originalityNote: "Original parameterized item; the figure is generated from the same shape model." },
    lifecycle: { state: "generated" },
  };
}

export function serialize(item: Json): string {
  return canonicalStringify(item);
}

export function describe(): Json {
  return {
    id: GENERATOR_ID, version: GENERATOR_VERSION,
    title: "Mensuration — perimeter, area & composite shapes",
    domain: "measurement",
    objectiveIds: TASKS.map((t) => OBJECTIVE_BY_TASK[t]),
    interactionTypes: ["free-response"],
    answerTypes: ["quantity"],
    tasks: [...TASKS],
    difficultyRanges: Object.fromEntries(TASKS.map((t) => [OBJECTIVE_BY_TASK[t], [...(TASK_BANDS[t] as [number, number])]])),
  };
}

// --- Independent validator (mirror of the Python validate) ---
function extractGroup(svg: string, cls: string): string {
  const openTag = `<g class="${cls}">`;
  const i = svg.indexOf(openTag);
  if (i < 0) return "";
  let depth = 0, j = i;
  while (j < svg.length) {
    if (svg.startsWith("<g", j)) depth++;
    else if (svg.startsWith("</g>", j)) { depth--; if (depth === 0) return svg.slice(i, j + 4); }
    j++;
  }
  return "";
}
function hasQuantityToken(text: string, qstr: string): boolean {
  const esc2 = qstr.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(?<!\\d)${esc2}(?!\\s*squared)(?![\\d²])(?!\\^2)`).test(text);
}
function substitutionRestores(task: string, p: Json, answer: Quantity): boolean {
  const v = answer.value;
  if (task === "missing_length_perimeter") {
    const known = p.hidden === "height" ? (p.width as number) : (p.height as number);
    return v.add(R(known)).mul(R(2)).equals(R(p.perimeter as number));
  }
  if (task === "missing_dimension_area") {
    const known = p.hidden === "height" ? (p.width as number) : (p.height as number);
    return v.mul(R(known)).equals(R(p.area as number));
  }
  if (task === "missing_triangle_base_height") {
    const known = p.hidden === "height" ? (p.base as number) : (p.height as number);
    return v.mul(R(known)).equals(R(p.area2 as number));
  }
  return false;
}
function hiddenNotMeasurable(task: string, p: Json): boolean {
  const shape = buildShape(task, p);
  const pxA = layout(shape, false);
  const p2: Json = { ...p };
  if ((p2.hidden === "height" || p2.hidden === "width") && shape.kind === "rectangle") {
    p2.width = (p2.width as number) + 3; p2.height = (p2.height as number) + 5;
  } else if (shape.kind === "triangle_base_height") {
    p2.base = (p2.base as number) + 3; p2.height = (p2.height as number) + 5;
  }
  const pxB = layout(buildShape(task, p2), false);
  return JSON.stringify(pxA) === JSON.stringify(pxB);
}

export function validate(item: Json): Json {
  const checks: Json[] = [];
  const add = (name: string, ok: boolean, detail = "") => checks.push({ name, result: ok ? "pass" : "fail", detail });
  const p = item.params as Json;
  const task = p.task as string;
  add("objective-mapping", JSON.stringify(item.objectiveIds) === JSON.stringify([OBJECTIVE_BY_TASK[task]]));
  add("interaction-free-response-only", item.interactionType === "free-response");

  const shape = buildShape(task, p);
  const answer = solve(task, p);
  const ans = item.answer as Json;
  const enc = encodeQuantityAnswer(answer);
  add("answer-type-quantity", ans.type === "quantity");
  add("answer-canonical-matches", JSON.stringify(ans.canonical) === JSON.stringify(enc.canonical));
  add("answer-measure-matches", JSON.stringify(ans.measure) === JSON.stringify(enc.measure));
  add("answer-display-derived", ans.display === enc.display);
  add("answer-exactness-policy", isExactAcceptable(task, p, answer));
  add("answer-no-legacy-units", !("units" in ans));

  const verts = shape.vertices;
  if (shape.kind === "rectangle") {
    add("rectangle-positive", (p.width as number) > 0 && (p.height as number) > 0);
    add("rectangle-closed-rect", verts.length === 4);
  } else if (shape.kind === "rectilinear_composite") {
    const [okClosed, why] = isClosedOrthogonalSimple(verts);
    add("composite-closed-orthogonal-simple", okClosed, why);
    const per = polygonPerimeter(verts);
    add("composite-exterior-perimeter", per.equals(R(2 * ((p.W as number) + (p.H as number)))));
    const decomp = shape.decomposition as DRect[];
    const adds = decomp.filter((r) => r.sign > 0);
    let overlap = false;
    for (let i = 0; i < adds.length; i++) for (let j = i + 1; j < adds.length; j++) if (rectsOverlap(adds[i] as DRect, adds[j] as DRect)) overlap = true;
    add("composite-decomposition-non-overlapping", !overlap);
    const shoe = polygonAreaShoelace(verts), deco = decompositionArea(decomp);
    add("composite-shoelace-equals-decomposition", shoe.equals(deco) && shoe.equals(R((p.W as number) * (p.H as number) - (p.a as number) * (p.b as number))));
  } else {
    add("triangle-non-collinear", (p.height as number) > 0 && (p.base as number) > 0);
    add("triangle-foot-on-base", (p.apexOffset as number) >= 0 && (p.apexOffset as number) <= (p.base as number));
    const area = new Rational((p.base as number) * (p.height as number), 2);
    add("triangle-area-half-base-height", polygonAreaShoelace(verts).equals(area));
  }

  if (HIDDEN_DIMENSION_TASKS.includes(task)) {
    add("missing-one-unknown", ["width", "height", "base"].includes(p.hidden as string));
    add("missing-substitution-restores", substitutionRestores(task, p, answer));
  }

  const media = (item.media as Json[])[0];
  const studentSvg = media.svg as string;
  const keySvg = (media.spec as Json).answerKeySvg as string;
  const acc = buildAccessibility(task, p, shape);
  add("svg-realises-data-student", studentSvg === renderSvg(task, p, shape, answer, "student", acc));
  add("svg-realises-data-key", keySvg === renderSvg(task, p, shape, answer, "answer-key", acc));
  add("answer-key-base-geometry-identical", extractGroup(studentSvg, "cx-base") === extractGroup(keySvg, "cx-base") && extractGroup(studentSvg, "cx-base") !== "");
  add("answer-key-overlay-additive-only", extractGroup(studentSvg, "cx-annot") === extractGroup(keySvg, "cx-annot"));
  add("student-figure-has-no-overlay", !studentSvg.includes("cx-overlay"));
  add("answer-key-has-overlay", keySvg.includes("cx-overlay"));

  const ansStr = formatQuantity(answer);
  add("no-result-in-student-figure", !hasQuantityToken(studentSvg, ansStr));
  add("student-a11y-does-not-state-result", !hasQuantityToken((item.accessibility as Json).spokenMath as string, ansStr));

  const shouldScale = !HIDDEN_DIMENSION_TASKS.includes(task);
  add("to-scale-policy-matches-task", Boolean(media.toScale) === shouldScale);
  if (!shouldScale) {
    add("not-to-scale-banner-present", studentSvg.includes("NOT TO SCALE"));
    add("hidden-dimension-not-measurable-from-svg", hiddenNotMeasurable(task, p));
  }

  const status = checks.every((c) => (c as Json).result === "pass") ? "pass" : "fail";
  return { status, validatorVersion: VALIDATOR_VERSION, checks };
}
