/**
 * gen.geometry.transformations v1.0.0 — generator, family-local Cartesian renderer, and validator.
 *
 * Byte-for-byte TypeScript mirror of oracle/spi_oracle/transformations.py.
 * EXACT (owner F): integer coordinates only; no trig/float/tolerance/irrational.
 */

import { Mulberry32 } from "../../core/seeded-random/mulberry32.ts";
import { canonicalStringify } from "../../core/serialization/canonical.ts";
import * as TC from "./transformations-core.ts";
import * as TS from "./transformations-shapes.ts";
import type { Point } from "./transformations-core.ts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = any;

export const GENERATOR_ID = "gen.geometry.transformations";
export const GENERATOR_VERSION = "1.0.0";
export const VALIDATOR_VERSION = "1.0.0";

export const OBJECTIVE_BY_TASK: Record<string, string> = {
  translate_point: "SPI.MIDDLE.GEO.TRANS.TRANSLATE_POINT.01",
  translate_shape: "SPI.MIDDLE.GEO.TRANS.TRANSLATE_SHAPE.01",
  reflect_point: "SPI.MIDDLE.GEO.TRANS.REFLECT_POINT.01",
  reflect_shape: "SPI.MIDDLE.GEO.TRANS.REFLECT_SHAPE.01",
  rotate_point: "SPI.MIDDLE.GEO.TRANS.ROTATE_POINT.01",
  rotate_shape: "SPI.MIDDLE.GEO.TRANS.ROTATE_SHAPE.01",
  describe_translation: "SPI.MIDDLE.GEO.TRANS.DESCRIBE_TRANSLATION.01",
  describe_reflection: "SPI.MIDDLE.GEO.TRANS.DESCRIBE_REFLECTION.01",
  describe_rotation: "SPI.MIDDLE.GEO.TRANS.DESCRIBE_ROTATION.01",
};
const SUPPORTED_INTERACTIONS = ["free-response"];
const FAMILY_KIND: Record<string, string> = {
  translate_point: "translation",
  translate_shape: "translation",
  describe_translation: "translation",
  reflect_point: "reflection",
  reflect_shape: "reflection",
  describe_reflection: "reflection",
  rotate_point: "rotation",
  rotate_shape: "rotation",
  describe_rotation: "rotation",
};

export class InteractionNotSupported extends Error {}

// --------------------------------------------------------------------------- //
// Family-local projection (owner L — mirrored, NOT imported)
// --------------------------------------------------------------------------- //
const VIEW_W = 1000;
const VIEW_H = 700;
const PAD = 70;
const U_MIN = 34;
const MARGIN = 1;
const CX = Math.floor(VIEW_W / 2);
const CY = Math.floor(VIEW_H / 2);

export function txGridRound(num: number, den: number): number {
  const q = Math.floor(num / den);
  const r = num - q * den;
  return 2 * r >= den ? q + 1 : q;
}

function viewport(pts: Point[]): Json | null {
  const xs = pts.map((p) => p[0]).concat([0]);
  const ys = pts.map((p) => p[1]).concat([0]);
  const wx0 = Math.min(...xs) - MARGIN;
  const wx1 = Math.max(...xs) + MARGIN;
  const wy0 = Math.min(...ys) - MARGIN;
  const wy1 = Math.max(...ys) + MARGIN;
  const Wx = wx1 - wx0;
  const Wy = wy1 - wy0;
  const U = Math.min(Math.floor((VIEW_W - 2 * PAD) / Wx), Math.floor((VIEW_H - 2 * PAD) / Wy));
  if (U < U_MIN) {
    return null;
  }
  return { wx0, wx1, wy0, wy1, Wx, Wy, U };
}

function projX(lay: Json, x: number): number {
  const num = CX * 2 - lay.U * lay.Wx + 2 * (x - lay.wx0) * lay.U;
  return txGridRound(num, 2);
}

function projY(lay: Json, y: number): number {
  const num = CY * 2 + lay.U * lay.Wy - 2 * (y - lay.wy0) * lay.U;
  return txGridRound(num, 2);
}

function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

const STYLE =
  ".tx-grid{stroke:#bbb;stroke-width:0.75;fill:none}" +
  ".tx-axis{stroke:#111;stroke-width:2.5;fill:none}" +
  ".tx-src-edge{stroke:#111;stroke-width:3;fill:none}" +
  ".tx-src-core{fill:#111}" +
  ".tx-img-edge{stroke:#111;stroke-width:3;fill:none;stroke-dasharray:8 5}" +
  ".tx-img-open{fill:#fff;stroke:#111;stroke-width:3}" +
  ".tx-mirror{stroke:#111;stroke-width:2;stroke-dasharray:2 6;fill:none}" +
  ".tx-vec{stroke:#111;stroke-width:3;fill:none;marker-end:url(#tx-arrow)}" +
  ".tx-centre{fill:#111;stroke:#fff;stroke-width:2}" +
  "text{font-family:sans-serif;font-size:26px;fill:#111}" +
  ".tx-ticklbl{font-size:18px;fill:#333}" +
  ".tx-lbl{font-size:26px;fill:#111}";

const LABEL_W_PER_CHAR = 16;
const LABEL_H = 24;
const CAND_OFFSETS: [number, number, string][] = [
  [14, -14, "start"],
  [-14, -14, "end"],
  [14, 18, "start"],
  [-14, 18, "end"],
  [0, -18, "middle"],
  [0, 26, "middle"],
];

// --------------------------------------------------------------------------- //
// Deterministic label placement with complete bounding-box clearance (owner M)
// --------------------------------------------------------------------------- //
function bbox(cx: number, cy: number, w: number, h: number): [number, number, number, number] {
  return [cx - Math.floor(w / 2), cy - h, cx + Math.floor(w / 2), cy];
}

function overlap(a: [number, number, number, number], b: [number, number, number, number]): boolean {
  return !(a[2] <= b[0] || b[2] <= a[0] || a[3] <= b[1] || b[3] <= a[1]);
}

function viehHGuard(): number {
  return VIEW_H - 4;
}

function placeLabels(items: [string, number, number][]): Json[] {
  const placed: Json[] = [];
  const markerBoxes = items.map(([, px, py]) => bbox(px, py + 9, 22, 22));
  for (const [text, px, py] of items) {
    const w = LABEL_W_PER_CHAR * text.length + 6;
    let chosen: Json | null = null;
    for (const [dx, dy, anchor] of CAND_OFFSETS) {
      const lx = px + dx;
      const ly = py + dy;
      const cx = lx + (anchor === "start" ? Math.floor(w / 2) : anchor === "end" ? -Math.floor(w / 2) : 0);
      const box = bbox(cx, ly + LABEL_H, w, LABEL_H);
      if (box[0] < 4 || box[1] < 4 || box[2] > VIEW_W - 4 || box[3] > viehHGuard()) {
        continue;
      }
      if (placed.some((pb) => overlap(box, pb.box))) {
        continue;
      }
      if (markerBoxes.some((mb) => overlap(box, mb))) {
        continue;
      }
      chosen = { text, x: lx, y: ly, anchor, box };
      break;
    }
    if (chosen === null) {
      const [dx, dy, anchor] = CAND_OFFSETS[0] as [number, number, string];
      const lx = px + dx;
      const ly = py + dy;
      const cx = lx + Math.floor(w / 2);
      chosen = { text, x: lx, y: ly, anchor, box: bbox(cx, ly + LABEL_H, w, LABEL_H), clearanceFailed: true };
    }
    placed.push(chosen);
  }
  return placed;
}

// --------------------------------------------------------------------------- //
// SVG building blocks
// --------------------------------------------------------------------------- //
function gridAxes(lay: Json): string[] {
  const out: string[] = [];
  const { wx0, wx1, wy0, wy1 } = lay;
  for (let gx = wx0; gx <= wx1; gx++) {
    if (gx === 0) continue;
    const sx = projX(lay, gx);
    out.push(`<line class="tx-grid" x1="${sx}" y1="${projY(lay, wy1)}" x2="${sx}" y2="${projY(lay, wy0)}"/>`);
  }
  for (let gy = wy0; gy <= wy1; gy++) {
    if (gy === 0) continue;
    const sy = projY(lay, gy);
    out.push(`<line class="tx-grid" x1="${projX(lay, wx0)}" y1="${sy}" x2="${projX(lay, wx1)}" y2="${sy}"/>`);
  }
  const axY = projY(lay, 0);
  const ayX = projX(lay, 0);
  out.push(`<line class="tx-axis" x1="${projX(lay, wx0)}" y1="${axY}" x2="${projX(lay, wx1)}" y2="${axY}"/>`);
  out.push(`<line class="tx-axis" x1="${ayX}" y1="${projY(lay, wy0)}" x2="${ayX}" y2="${projY(lay, wy1)}"/>`);
  for (let gx = wx0; gx <= wx1; gx++) {
    if (gx === 0) continue;
    const sx = projX(lay, gx);
    out.push(`<text class="tx-ticklbl" x="${sx}" y="${axY + 22}" text-anchor="middle">${gx}</text>`);
  }
  for (let gy = wy0; gy <= wy1; gy++) {
    if (gy === 0) continue;
    const sy = projY(lay, gy);
    out.push(`<text class="tx-ticklbl" x="${ayX - 10}" y="${sy + 6}" text-anchor="end">${gy}</text>`);
  }
  out.push(`<text class="tx-ticklbl" x="${ayX - 10}" y="${axY + 22}" text-anchor="end">0</text>`);
  return out;
}

function objectEls(verts: Point[], lay: Json, image: boolean): string[] {
  const out: string[] = [];
  const pts = verts.map((v) => [projX(lay, v[0]), projY(lay, v[1])] as [number, number]);
  if (pts.length >= 2) {
    const edge = image ? "tx-img-edge" : "tx-src-edge";
    let d = "M " + pts.map(([x, y]) => `${x} ${y}`).join(" L ");
    if (pts.length >= 3) {
      d += " Z";
    }
    out.push(`<path class="${edge}" d="${d}"/>`);
  }
  for (const [x, y] of pts) {
    if (image) {
      out.push(`<rect class="tx-img-open" x="${x - 7}" y="${y - 7}" width="14" height="14"/>`);
    } else {
      out.push(`<circle class="tx-src-core" cx="${x}" cy="${y}" r="6"/>`);
    }
  }
  return out;
}

function labelEls(placed: Json[]): string[] {
  return placed.map(
    (p) => `<text class="tx-lbl" x="${p.x}" y="${p.y}" text-anchor="${p.anchor}">${esc(p.text)}</text>`,
  );
}

function overlayEls(_task: string, desc: Json, src: Point[], img: Point[], lay: Json): string[] {
  const out: string[] = ['<g class="tx-overlay">'];
  const kind = desc.kind;
  if (kind === "translation") {
    const sx = projX(lay, (src[0] as Point)[0]);
    const sy = projY(lay, (src[0] as Point)[1]);
    const ix = projX(lay, (img[0] as Point)[0]);
    const iy = projY(lay, (img[0] as Point)[1]);
    out.push(`<line class="tx-vec" x1="${sx}" y1="${sy}" x2="${ix}" y2="${iy}"/>`);
  } else if (kind === "reflection") {
    const ax = desc.axis;
    const { wx0, wx1, wy0, wy1 } = lay;
    if (ax.kind === "vertical") {
      const x = projX(lay, ax.value);
      out.push(`<line class="tx-mirror" x1="${x}" y1="${projY(lay, wy0)}" x2="${x}" y2="${projY(lay, wy1)}"/>`);
    } else if (ax.kind === "horizontal") {
      const y = projY(lay, ax.value);
      out.push(`<line class="tx-mirror" x1="${projX(lay, wx0)}" y1="${y}" x2="${projX(lay, wx1)}" y2="${y}"/>`);
    } else {
      if (ax.equation === "y=x") {
        const a = Math.max(wx0, wy0);
        const b = Math.min(wx1, wy1);
        out.push(
          `<line class="tx-mirror" x1="${projX(lay, a)}" y1="${projY(lay, a)}" x2="${projX(lay, b)}" y2="${projY(lay, b)}"/>`,
        );
      } else {
        const a = Math.max(wx0, -wy1);
        const b = Math.min(wx1, -wy0);
        out.push(
          `<line class="tx-mirror" x1="${projX(lay, a)}" y1="${projY(lay, -a)}" x2="${projX(lay, b)}" y2="${projY(lay, -b)}"/>`,
        );
      }
    }
  } else if (kind === "rotation") {
    const c = desc.centre;
    const cx = projX(lay, c.x);
    const cy = projY(lay, c.y);
    out.push(`<circle class="tx-centre" cx="${cx}" cy="${cy}" r="6"/>`);
  }
  out.push("</g>");
  return out;
}

function arrowDefs(): string {
  return (
    '<defs><marker id="tx-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" ' +
    'orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#111"/></marker></defs>'
  );
}

function render(task: string, params: Json, answerKey: boolean): string {
  const src = params.source;
  const img = params.image;
  const desc = params.descriptor;
  const obj = params.objectType;
  const perform = !task.startsWith("describe");
  const lay = params.layout;
  const acc = accessibility(task, params);

  const out: string[] = [
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VIEW_W} ${VIEW_H}" role="img" aria-label="${esc(acc.alt)}">`,
  ];
  out.push(`<title>${esc(acc.title)}</title><desc>${esc(acc.desc)}</desc>`);
  out.push(`<style>${STYLE}</style>${arrowDefs()}`);
  out.push(...gridAxes(lay));

  // base geometry + student annotations (identical in both channels)
  out.push(...objectEls(src, lay, false));
  let labelItems: [string, number, number][] = zipLabels(TS.SOURCE_LABELS[obj] as string[], src, lay);
  const showImageInStudent = !perform;
  if (showImageInStudent) {
    out.push(...objectEls(img, lay, true));
    labelItems = labelItems.concat(zipLabels(TS.imageLabels(obj), img, lay));
  }
  const placed = placeLabels(labelItems);
  params._labelPlacements = placed;
  out.push(...labelEls(placed));

  if (answerKey) {
    if (perform) {
      out.push(...objectEls(img, lay, true));
      const imgLabels = placeLabels(zipLabels(TS.imageLabels(obj), img, lay));
      out.push(...labelEls(imgLabels));
    }
    out.push(...overlayEls(task, desc, src, img, lay));
  }

  out.push("</svg>");
  return out.join("\n");
}

function zipLabels(labels: string[], verts: Point[], lay: Json): [string, number, number][] {
  const out: [string, number, number][] = [];
  const n = Math.min(labels.length, verts.length);
  for (let i = 0; i < n; i++) {
    const v = verts[i] as Point;
    out.push([labels[i] as string, projX(lay, v[0]), projY(lay, v[1])]);
  }
  return out;
}

// --------------------------------------------------------------------------- //
// Parameter draw
// --------------------------------------------------------------------------- //
const GRID = 6;

function randPoint(rng: Mulberry32, lo = -GRID, hi = GRID): Point {
  return [rng.nextInt(lo, hi), rng.nextInt(lo, hi)];
}

function randTriangle(rng: Mulberry32): Point[] {
  for (let i = 0; i < 60; i++) {
    const v = [randPoint(rng, -4, 4), randPoint(rng, -4, 4), randPoint(rng, -4, 4)];
    if (!TS.isCollinear(v) && uniqueCount(v) === 3) {
      return v;
    }
  }
  return [
    [0, 0],
    [3, 0],
    [0, 2],
  ];
}

function randQuad(rng: Mulberry32): Point[] {
  for (let i = 0; i < 80; i++) {
    const cx = rng.nextInt(-2, 2);
    const cy = rng.nextInt(-2, 2);
    const offs: [number, number][] = [
      [1, 1],
      [-1, 1],
      [-1, -1],
      [1, -1],
    ];
    const v: Point[] = offs.map(([ox, oy]) => [cx + ox * rng.nextInt(1, 3), cy + oy * rng.nextInt(1, 3)] as Point);
    if (uniqueCount(v) === 4 && TS.isSimpleQuad(v) && TS.signedArea2(v) !== 0) {
      return v;
    }
  }
  return [
    [1, 1],
    [-1, 1],
    [-1, -1],
    [1, -1],
  ];
}

function randSegment(rng: Mulberry32): Point[] {
  for (let i = 0; i < 40; i++) {
    const a = randPoint(rng, -4, 4);
    const b = randPoint(rng, -4, 4);
    if (!(a[0] === b[0] && a[1] === b[1])) {
      return [a, b];
    }
  }
  return [
    [-2, -1],
    [3, 2],
  ];
}

/** Number of distinct points (mirror of Python len(set(...)) on tuples). */
function uniqueCount(pts: Point[]): number {
  const seen = new Set<string>();
  for (const p of pts) {
    seen.add(`${p[0]},${p[1]}`);
  }
  return seen.size;
}

function drawObject(rng: Mulberry32, obj: string): Point[] {
  if (obj === "point") return [randPoint(rng)];
  if (obj === "segment") return randSegment(rng);
  if (obj === "triangle") return randTriangle(rng);
  return randQuad(rng);
}

function drawDescriptor(rng: Mulberry32, kind: string): Json {
  if (kind === "translation") {
    for (;;) {
      const dx = rng.nextInt(-5, 5);
      const dy = rng.nextInt(-5, 5);
      if (!(dx === 0 && dy === 0)) {
        return TC.translationDesc(dx, dy);
      }
    }
  }
  if (kind === "reflection") {
    const choice = rng.nextInt(0, 3);
    if (choice === 0) {
      return TC.reflectionVertical(rng.nextInt(-3, 3));
    }
    if (choice === 1) {
      return TC.reflectionHorizontal(rng.nextInt(-3, 3));
    }
    if (choice === 2) {
      return TC.reflectionDiagonal("y=x");
    }
    return TC.reflectionDiagonal("y=-x");
  }
  // rotation
  return TC.rotationDesc(rng.nextInt(-3, 3), rng.nextInt(-3, 3), rng.nextInt(1, 3));
}

function objectForTask(task: string, rng: Mulberry32): string {
  if (task.endsWith("_point")) {
    return "point";
  }
  if (task.startsWith("describe")) {
    return rng.nextInt(0, 1) === 0 ? "triangle" : "quadrilateral";
  }
  return (["segment", "triangle", "quadrilateral"][rng.nextInt(0, 2)]) as string;
}

function inGrid(verts: Point[], bound = GRID + 2): boolean {
  return verts.every((v) => -bound <= v[0] && v[0] <= bound && -bound <= v[1] && v[1] <= bound);
}

function paramsFor(seed: number, task: string): Json {
  const rng = new Mulberry32(seed);
  const kind = FAMILY_KIND[task] as string;
  for (let i = 0; i < 200; i++) {
    const obj = objectForTask(task, rng);
    const src = drawObject(rng, obj);
    const desc = drawDescriptor(rng, kind);
    const img: Point[] = src.map((p) => TC.applyTransform(desc, p));
    if (!inGrid(src) || !inGrid(img)) {
      continue;
    }
    if (TS.isUnchanged(src, img)) {
      continue;
    }
    const lay = viewport(src.concat(img));
    if (lay === null) {
      continue;
    }
    if (task.startsWith("describe")) {
      const uniq = TS.uniqueDescriptor(kind, src, img);
      if (uniq === null || !TC.descriptorsEqual(uniq, desc)) {
        continue;
      }
    }
    return { task, objectType: obj, source: src, image: img, descriptor: desc, kind, layout: lay };
  }
  throw new Error(`could not draw a valid item for ${task} seed=${seed}`);
}

// --------------------------------------------------------------------------- //
// Answer encoding (owner B)
// --------------------------------------------------------------------------- //
function coord(p: Point): Json {
  return { x: p[0], y: p[1] };
}

function answer(task: string, params: Json): Json {
  if (task.endsWith("_point")) {
    const p = params.image[0] as Point;
    return { type: "coordinate", canonical: coord(p), display: `(${p[0]}, ${p[1]})` };
  }
  if (task.startsWith("describe")) {
    return TC.answerObject(params.descriptor);
  }
  const obj = params.objectType;
  const labels = TS.imageLabels(obj);
  const cells: Json[] = [];
  const img = params.image as Point[];
  for (let i = 0; i < img.length; i++) {
    cells.push({ location: labels[i], value: coord(img[i] as Point) });
  }
  const disp = cells.map((c) => `${c.location}=(${c.value.x}, ${c.value.y})`).join(", ");
  return { type: "table-completion", canonical: { cells }, display: disp };
}

// --------------------------------------------------------------------------- //
// Difficulty
// --------------------------------------------------------------------------- //
const TASK_BANDS: Record<string, [number, number]> = {
  translate_point: [1, 2],
  translate_shape: [2, 3],
  reflect_point: [2, 3],
  reflect_shape: [2, 3],
  rotate_point: [2, 3],
  rotate_shape: [3, 4],
  describe_translation: [2, 3],
  describe_reflection: [3, 4],
  describe_rotation: [3, 4],
};

/** Mirror of Python round(x, 3) with banker's rounding, returning int when whole. */
function round3(x: number): number {
  const r = roundHalfEven(x, 3);
  return r === Math.trunc(r) ? Math.trunc(r) : r;
}

/** Python 3 round() — round-half-to-even at the given decimal precision. */
function roundHalfEven(x: number, ndigits: number): number {
  const factor = 10 ** ndigits;
  const scaled = x * factor;
  const floor = Math.floor(scaled);
  const diff = scaled - floor;
  let rounded: number;
  const eps = 1e-9;
  if (diff > 0.5 + eps) {
    rounded = floor + 1;
  } else if (diff < 0.5 - eps) {
    rounded = floor;
  } else {
    // exactly halfway (within eps): round to even
    rounded = floor % 2 === 0 ? floor : floor + 1;
  }
  return rounded / factor;
}

function isHighComplexity(task: string, params: Json): boolean {
  const kind = params.kind;
  const obj = params.objectType;
  const desc = params.descriptor;
  if (kind === "translation" && task.endsWith("_point")) {
    const v = desc.vector;
    return Math.abs(v.dx) + Math.abs(v.dy) >= 5;
  }
  if (kind === "reflection") {
    return desc.axis.kind === "diagonal";
  }
  if (kind === "rotation") {
    return desc.quarterTurnsCCW !== 2;
  }
  return obj === "quadrilateral";
}

function difficulty(task: string, params: Json): Json {
  const kind = params.kind;
  const obj = params.objectType;
  const high = isHighComplexity(task, params);
  const [lo, hi] = TASK_BANDS[task] as [number, number];
  const band = high ? hi : lo;

  const pts = (params.source as Point[]).concat(params.image as Point[]);
  const mags = pts.map((v) => Math.abs(v[0]) + Math.abs(v[1]));
  const nc = Math.min(1.0, (mags.length ? Math.max(...mags) : 0) / 24.0);
  const ev = 0.0;
  let rs = ({ translation: 0.3, reflection: 0.5, rotation: 0.7 } as Record<string, number>)[kind] as number;
  if (task.startsWith("describe")) {
    rs = Math.min(1.0, rs + 0.2);
  } else if (!task.endsWith("_point")) {
    rs = Math.min(1.0, rs + 0.1);
  }
  let ab = ({ point: 0.2, segment: 0.35, triangle: 0.45, quadrilateral: 0.6 } as Record<string, number>)[obj] as number;
  if (task.startsWith("describe")) {
    ab = Math.min(1.0, ab + 0.2);
  }
  if (high) {
    ab = Math.min(1.0, ab + 0.1);
  }
  const axes = {
    numericalComplexity: round3(nc),
    exactVsApproximate: round3(ev),
    reasoningSteps: round3(rs),
    abstraction: round3(ab),
  };
  return { overallBand: band, axes };
}

// --------------------------------------------------------------------------- //
// Accessibility
// --------------------------------------------------------------------------- //
function objPhrase(obj: string): string {
  return ({ point: "point", segment: "line segment", triangle: "triangle", quadrilateral: "quadrilateral" } as Record<string, string>)[
    obj
  ] as string;
}

function srcLabelStr(obj: string): string {
  return (TS.SOURCE_LABELS[obj] as string[]).join("");
}

function capitalize(s: string): string {
  // Python str.capitalize(): first char upper, rest lower. All inputs here are single words / lowercase.
  if (s.length === 0) return s;
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
}

function accessibility(task: string, params: Json): Json {
  const obj = params.objectType;
  const src = params.source as Point[];
  const perform = !task.startsWith("describe");
  const srcLabels = TS.SOURCE_LABELS[obj] as string[];
  const srcDesc = src.map((v, i) => `${srcLabels[i]} at (${v[0]}, ${v[1]})`).join("; ");
  let alt: string;
  let title: string;
  let desc: string;
  let table: string[][];
  if (perform) {
    const instr = instruction(task, params);
    alt = `A coordinate grid showing ${objPhrase(obj)} ${srcLabelStr(obj)} with vertices ${srcDesc}. ${instr}`;
    title = `Coordinate grid with ${objPhrase(obj)} ${srcLabelStr(obj)}`;
    desc = `${capitalize(objPhrase(obj))} ${srcLabelStr(obj)}: ${srcDesc}. The image is not shown.`;
    table = [["Vertex", "Coordinates"]];
    for (let i = 0; i < src.length; i++) {
      table.push([srcLabels[i] as string, `(${(src[i] as Point)[0]}, ${(src[i] as Point)[1]})`]);
    }
  } else {
    const img = params.image as Point[];
    const imgLabels = TS.imageLabels(obj);
    const imgDesc = img.map((v, i) => `${imgLabels[i]} at (${v[0]}, ${v[1]})`).join("; ");
    alt =
      `A coordinate grid showing ${objPhrase(obj)} ${srcLabelStr(obj)} (${srcDesc}) and its image ` +
      `(${imgDesc}). Describe the single transformation that maps the object onto its image.`;
    title = `Coordinate grid with an object and its image`;
    desc = `Object ${srcLabelStr(obj)}: ${srcDesc}. Image: ${imgDesc}.`;
    table = [["Vertex", "Object", "Image"]];
    for (let i = 0; i < src.length; i++) {
      table.push([
        srcLabels[i] as string,
        `(${(src[i] as Point)[0]}, ${(src[i] as Point)[1]})`,
        `(${(img[i] as Point)[0]}, ${(img[i] as Point)[1]})`,
      ]);
    }
  }
  return {
    alt,
    title,
    desc,
    dataTable: table,
    spokenMath: alt,
    longDescription: `${title}. ${desc}`,
  };
}

// --------------------------------------------------------------------------- //
// Prompt + solution
// --------------------------------------------------------------------------- //
function vecPhrase(desc: Json): string {
  const v = desc.vector;
  return `(${v.dx}, ${v.dy})`;
}

function instruction(task: string, params: Json): string {
  const obj = params.objectType;
  const desc = params.descriptor;
  const lab = srcLabelStr(obj);
  if (task.startsWith("translate")) {
    return `Translate ${objPhrase(obj)} ${lab} by the vector ${vecPhrase(desc)}.`;
  }
  if (task.startsWith("reflect")) {
    return `Reflect ${objPhrase(obj)} ${lab} in ${TC.axisEquation(desc.axis)}.`;
  }
  if (task.startsWith("rotate")) {
    const c = desc.centre;
    const q = desc.quarterTurnsCCW;
    const deg = TC.QUARTER_DEGREES[q];
    const dirn = q === 2 ? "" : " anticlockwise";
    return `Rotate ${objPhrase(obj)} ${lab} ${deg}°${dirn} about (${c.x}, ${c.y}).`;
  }
  const imgLab = TS.imageLabels(obj).join("");
  const fam = ({ translation: "translation", reflection: "reflection", rotation: "rotation" } as Record<string, string>)[
    params.kind
  ] as string;
  return `Describe fully the ${fam} that maps ${lab} onto ${imgLab}.`;
}

function prompt(task: string, params: Json): Json {
  const obj = params.objectType;
  const perform = !task.startsWith("describe");
  const instr = instruction(task, params);
  let ask: string;
  if (perform && task.endsWith("_point")) {
    ask = "Give the coordinates of the image.";
  } else if (perform) {
    ask = `Give the coordinates of each image vertex (${TS.imageLabels(obj).join("")}).`;
  } else {
    ask = "Give the full description of the transformation.";
  }
  return { blocks: [{ kind: "text", text: `${instr} ${ask}` }] };
}

function solution(task: string, params: Json): Json {
  const desc = params.descriptor;
  const src = params.source as Point[];
  const img = params.image as Point[];
  const obj = params.objectType;
  const steps: Json[] = [];
  if (task.startsWith("describe")) {
    const ans = TC.answerObject(desc).display;
    const srcLabels = TS.SOURCE_LABELS[obj] as string[];
    const imgLabels = TS.imageLabels(obj);
    const corr = srcLabels.map((a, i) => `${a}->${imgLabels[i]}`).join("; ");
    steps.push({
      number: 1,
      transformation: "Compare corresponding labelled vertices to identify the transformation.",
      intermediateResult: corr,
    });
    steps.push({
      number: 2,
      transformation: "Determine the parameters from the correspondence.",
      intermediateResult: ans,
    });
    return { steps };
  }
  const kind = params.kind;
  let rule: string;
  if (kind === "translation") {
    rule = "Add the vector to each coordinate.";
  } else if (kind === "reflection") {
    rule = `Apply the reflection rule for ${TC.axisEquation(desc.axis)}.`;
  } else {
    rule = "Measure each vertex from the centre and apply the quarter-turn rule.";
  }
  const inter = src.map((s, i) => `(${s[0]}, ${s[1]})->(${(img[i] as Point)[0]}, ${(img[i] as Point)[1]})`).join("; ");
  steps.push({ number: 1, transformation: rule, intermediateResult: inter });
  return { steps };
}

// --------------------------------------------------------------------------- //
// Public generate()
// --------------------------------------------------------------------------- //
const _TASKS = Object.keys(OBJECTIVE_BY_TASK);
export const TASKS = _TASKS;

export function generate(seed: number, config?: Json): Json {
  config = config || {};
  const interaction = config.interactionType ?? "free-response";
  if (!SUPPORTED_INTERACTIONS.includes(interaction)) {
    throw new InteractionNotSupported(
      `gen.geometry.transformations supports only free-response in v1.0.0 (requested ${pyRepr(interaction)})`,
    );
  }
  let task = config.task;
  if (task === undefined || task === null) {
    task = _TASKS[new Mulberry32(seed).nextInt(0, _TASKS.length - 1)];
  }
  if (!(task in OBJECTIVE_BY_TASK)) {
    throw new Error(`unknown task ${pyRepr(task)}`);
  }

  const params = paramsFor(seed, task);
  const studentSvg = render(task, params, false);
  const keySvg = render(task, params, true);
  const acc = accessibility(task, params);
  const diff = difficulty(task, params);
  const ans = answer(task, params);

  const item: Json = {
    itemId: `ITEM-TRANS-${task}-${seed}`,
    schemaVersion: "1.0.0",
    objectiveIds: [OBJECTIVE_BY_TASK[task]],
    generatorId: GENERATOR_ID,
    generatorVersion: GENERATOR_VERSION,
    seed,
    interactionType: "free-response",
    prompt: prompt(task, params),
    answer: ans,
    solution: solution(task, params),
    media: [
      {
        id: "fig-1",
        kind: "svg",
        svg: studentSvg,
        spec: { answerKeySvg: keySvg, labelPlacements: params._labelPlacements ?? [] },
        toScale: true,
        altText: acc.alt,
        longDescription: acc.longDescription,
        dataTableFallback: { columns: acc.dataTable[0], rows: acc.dataTable.slice(1) },
      },
    ],
    provenance: { origin: "generated", rightsStatus: "academy-owned" },
    lifecycle: { state: "generated" },
    accessibility: {
      spokenMath: acc.spokenMath,
      altText: acc.alt,
      longDescription: acc.longDescription,
      nonColorIndicators: true,
    },
    difficulty: diff,
    params: {
      task,
      objectType: params.objectType,
      transformationKind: params.kind,
      descriptor: TC.canonicalizeDescriptor(params.descriptor),
      source: (params.source as Point[]).map((p) => coord(p)),
      image: (params.image as Point[]).map((p) => coord(p)),
    },
  };
  return item;
}

function pyRepr(v: Json): string {
  // Mirrors Python's !r for strings: single-quoted.
  if (typeof v === "string") {
    return `'${v}'`;
  }
  return String(v);
}

// --------------------------------------------------------------------------- //
// Independent validator
// --------------------------------------------------------------------------- //
function pts(coords: Json[]): Point[] {
  return coords.map((c) => [c.x, c.y] as Point);
}

export function validate(item: Json): Json {
  const checks: Json[] = [];
  const add = (name: string, ok: boolean, detail = ""): void => {
    // Carry BOTH the Python oracle shape ({name, ok}) — the golden-parity contract — and the
    // SDK GenValidationResult shape ({name, result}), so the stability harness and the byte-parity
    // gate read the same record.
    checks.push({ name, ok: Boolean(ok), result: ok ? "pass" : "fail", detail });
  };

  const p = item.params;
  const task = p.task;
  const obj = p.objectType;
  const kind = p.transformationKind;
  const desc = p.descriptor;
  const src = pts(p.source);
  const img = pts(p.image);
  const perform = !task.startsWith("describe");

  add("object-not-unchanged", !TS.isUnchanged(src, img));

  if (kind === "translation") {
    const v = desc.vector;
    add(
      "inverse-transformation-restores-source",
      TS.verifyTranslation(src, img, v.dx, v.dy) && !(v.dx === 0 && v.dy === 0),
    );
  } else if (kind === "reflection") {
    add("reflection-axis-condition", TS.verifyReflection(src, img, desc.axis));
  } else {
    const c = desc.centre;
    add("rotation-quarter-turn-agreement", TS.verifyRotation(src, img, c.x, c.y, desc.quarterTurnsCCW));
  }

  add("congruence-squared-distances", TS.congruentInCorrespondence(src, img, obj));
  if (obj === "triangle" || obj === "quadrilateral") {
    const so = TS.orientationSign(src);
    const io = TS.orientationSign(img);
    if (kind === "reflection") {
      add("orientation-reversed", so === -io && so !== 0);
    } else {
      add("orientation-preserved", so === io && so !== 0);
    }
  }

  const ans = item.answer;
  if (perform && task.endsWith("_point")) {
    add(
      "answer-agrees-with-descriptor",
      ans.type === "coordinate" && TC.deepEqual(ans.canonical, { x: (img[0] as Point)[0], y: (img[0] as Point)[1] }),
    );
  } else if (perform) {
    const cells = ans.canonical.cells as Json[];
    const byLabel: Record<string, [number, number]> = {};
    for (const c of cells) {
      byLabel[c.location] = [c.value.x, c.value.y];
    }
    const want: Record<string, [number, number]> = {};
    const imgLabels = TS.imageLabels(obj);
    for (let i = 0; i < img.length; i++) {
      want[imgLabels[i] as string] = img[i] as Point;
    }
    add("answer-agrees-with-descriptor", ans.type === "table-completion" && recordsEqual(byLabel, want));
    add(
      "no-vertex-omitted-or-mislabelled",
      sameKeys(byLabel, want) && cells.length === img.length,
    );
  } else {
    add("answer-agrees-with-descriptor", ans.type === "transformation" && TC.descriptorsEqual(ans.canonical, desc));
    add(
      "descriptor-display-derived",
      ans.display === TC.formatDisplay(TC.canonicalizeDescriptor(ans.canonical)),
    );
    const uniq = TS.uniqueDescriptor(kind, src, img);
    add("descriptor-unique", uniq !== null && TC.descriptorsEqual(uniq, desc));
  }

  const media = item.media[0];
  const student = media.svg as string;
  const key = media.spec.answerKeySvg as string;
  const idx = student.lastIndexOf("</svg>");
  add("answer-key-base-geometry-identical", key.startsWith(student.slice(0, idx)));
  add("answer-key-overlay-additive-only", key.length >= student.length && student !== key);

  if (perform) {
    add("perform-student-image-hidden", !student.includes('<rect class="tx-img-open"'));
    const rows = media.dataTableFallback.rows as string[][];
    const srcStrs = src.map((v) => `(${v[0]}, ${v[1]})`).sort();
    add(
      "perform-student-table-source-only",
      rows.length === src.length && arraysEqual(rows.map((r) => r[1] as string).sort(), srcStrs),
    );
  } else {
    add("describe-student-shows-both-figures", student.includes('<rect class="tx-img-open"'));
    add("describe-student-no-descriptor-named", !student.includes(TC.formatDisplay(desc)));
  }

  const placements = (media.spec.labelPlacements ?? []) as Json[];
  add("label-inside-canvas", placements.every((pl) => !pl.clearanceFailed));
  add("label-bbox-clearance", labelsPairwiseClear(placements));

  const valid = checks.every((c) => c.ok);
  // `valid` is the Python oracle field (golden-parity); `status` is the SDK GenValidationResult field.
  return { valid, status: valid ? "pass" : "fail", validatorVersion: VALIDATOR_VERSION, checks };
}

function recordsEqual(a: Record<string, [number, number]>, b: Record<string, [number, number]>): boolean {
  const ka = Object.keys(a);
  const kb = Object.keys(b);
  if (ka.length !== kb.length) return false;
  for (const k of ka) {
    const av = a[k];
    const bv = b[k];
    if (!bv || !av || av[0] !== bv[0] || av[1] !== bv[1]) return false;
  }
  return true;
}

function sameKeys(a: Record<string, unknown>, b: Record<string, unknown>): boolean {
  const ka = Object.keys(a).sort();
  const kb = Object.keys(b).sort();
  return ka.length === kb.length && ka.every((k, i) => k === kb[i]);
}

function arraysEqual(a: string[], b: string[]): boolean {
  return a.length === b.length && a.every((v, i) => v === b[i]);
}

function labelsPairwiseClear(placements: Json[]): boolean {
  const boxes = placements.filter((pl) => "box" in pl).map((pl) => pl.box as [number, number, number, number]);
  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      if (overlap(boxes[i] as [number, number, number, number], boxes[j] as [number, number, number, number])) {
        return false;
      }
    }
  }
  return true;
}

export function serialize(item: Json): string {
  return canonicalStringify(item);
}

export function describe(): Json {
  return {
    generatorId: GENERATOR_ID,
    version: GENERATOR_VERSION,
    title: "Coordinate transformations",
    domain: "geometry",
    strand: "coordinate-transformations",
    objectiveIds: Object.values(OBJECTIVE_BY_TASK),
    tasks: [..._TASKS],
    interactionTypes: [...SUPPORTED_INTERACTIONS],
    answerTypes: ["coordinate", "table-completion", "transformation"],
    approvalStatus: "pending-review",
  };
}
