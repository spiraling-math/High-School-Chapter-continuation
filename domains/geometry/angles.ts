/**
 * Geometry (angles) generator with mathematically generated SVG diagrams (production TS).
 *
 * Generator id : gen.geometry.angles-figures   Version: 1.0.0
 * Spec         : docs/GENERATOR_SPEC_geometry_svg_proposal.md (owner-approved core + revisions)
 *
 * Byte-for-byte counterpart of oracle/spi_oracle/geometry.py. Ray directions come
 * from the committed integer DIR table (no runtime trig); coordinates are integers
 * via a single round-half-up rule; the SVG is hand-serialized canonically so it is
 * byte-identical across languages. Figures are toScale:false with a NOT TO SCALE mark.
 */

import { Mulberry32 } from "../../core/seeded-random/mulberry32.ts";
import { canonicalStringify, type Json } from "../../core/serialization/canonical.ts";
import { Rational, rat } from "../../core/exact-math/rational.ts";
import { round3 } from "../../core/difficulty/band.ts";
import { resolveInteractionType } from "../../core/sdk/interaction.ts";
import { assembleMultipleChoice } from "../../core/sdk/multiple-choice.ts";
import { DIR, R } from "../../core/geometry/dir-table.ts";
import { MISCONCEPTIONS, rulesFor, type GeoCtx } from "./geometry-misconceptions.ts";

export const GENERATOR_ID = "gen.geometry.angles-figures";
export const GENERATOR_VERSION = "1.2.3"; // v1.2.1/v1.2.2: see DECISION_LOG; v1.2.3 = secondary non-crossing leaders

export type Task = "straight_line_missing_angle" | "triangle_missing_angle" | "isosceles_base_angle"
  | "vertically_opposite_angle" | "angles_at_point_missing";
export const TASKS: Task[] = ["straight_line_missing_angle", "triangle_missing_angle", "isosceles_base_angle",
  "vertically_opposite_angle", "angles_at_point_missing"];
export const MC_TASKS: Task[] = ["straight_line_missing_angle", "triangle_missing_angle", "isosceles_base_angle",
  "angles_at_point_missing"];

const OBJECTIVE_BY_TASK: Record<Task, string> = {
  straight_line_missing_angle: "SPI.MIDDLE.GEO.ANGLES_STRAIGHT_LINE.01",
  triangle_missing_angle: "SPI.MIDDLE.GEO.TRIANGLE_ANGLE_SUM.01",
  isosceles_base_angle: "SPI.MIDDLE.GEO.ISOSCELES_BASE_ANGLES.01",
  vertically_opposite_angle: "SPI.MIDDLE.GEO.VERTICALLY_OPPOSITE_ANGLES.01",
  angles_at_point_missing: "SPI.MIDDLE.GEO.ANGLES_AT_POINT.01",
};
const TASK_BANDS: Record<Task, [number, number]> = {
  straight_line_missing_angle: [1, 3], triangle_missing_angle: [2, 3], isosceles_base_angle: [2, 3],
  vertically_opposite_angle: [1, 2], angles_at_point_missing: [2, 4],
};
const CALCULATOR_POLICY = "calculator-not-required";
const MAX_PARAM_ATTEMPTS = 400;
const MIN_ANGLE = 10;
const VIEW_W = 1000, VIEW_H = 700, RAW_LEN = 1000, RAW_BASE = 1200;
const CX = 500, CY = 350, SPAN_X = 760, SPAN_Y = 520;
const ARC_R = 70, TICK = 22;
// Per-angle arc radii (v1.2.0): distinct radii so each angle's arc is identifiable.
const ARC_BASE = 44, ARC_STEP = 20;
const ARC_TRI_MAX = 56, ARC_TRI_NUM = 30, ARC_TRI_DEN = 100;
const ARC_DEFAULT = 62;
// Adaptive label placement (v1.2.1) + non-crossing radial leaders (v1.2.3).
const LBL_ASC = 22, LBL_DESC = 8, LBL_H = LBL_ASC + LBL_DESC;
const LBL_CLEAR = 8, CANVAS_M = 12, CAPTION_TOP = 666, LBL_R0_GAP = 36, LBL_STEP = 14, R_LABEL_MAX = 480;
const LEAD_IN = 10, LEAD_BACK = 14, LEADER_MIN = 26, ARC_SAMPLES = 8, NARROW_DEG = 30;
// Callout leaders (.gx) are visually SECONDARY: thinner than every geometry stroke, dashed,
// and round-capped, so they read as annotations, not rays/sides/arcs/ticks.
const STYLE = ".gl{stroke:#111;stroke-width:3;fill:none}.ga{stroke:#111;stroke-width:2;fill:none}"
  + ".gt{stroke:#111;stroke-width:3}.gx{stroke:#555;stroke-width:1.5;stroke-dasharray:5 4;stroke-linecap:round;fill:none}.gv{fill:#111}text{font-family:sans-serif;font-size:30px;fill:#111}"
  + ".gn{font-size:22px;fill:#444;letter-spacing:1px}";
const LEADER_STROKE_WIDTH = 1.5;
const GEOMETRY_STROKE_WIDTHS = [3, 2];

export interface Params { task: Task; [k: string]: Json; }
export interface Config { task?: Task; answerType?: "integer" | "multiple-choice"; interactionType?: "free-response" | "multiple-choice"; }
type Pt = [number, number];

function gridRound(num: number, den: number): number {
  const n = BigInt(num), d = BigInt(den);
  let q = n / d; let r = n % d;            // BigInt division truncates toward zero
  if (r < 0n) { q -= 1n; r += d; }         // make it floor with 0 <= r < d
  return Number(2n * r >= d ? q + 1n : q);
}
const dirAt = (theta: number): readonly [number, number] => DIR[((theta % 360) + 360) % 360]!;
function ray(o: Pt, theta: number, length: number): Pt {
  const [dx, dy] = dirAt(theta);
  return [o[0] + gridRound(dx * length, R), o[1] - gridRound(dy * length, R)];
}
const mid = (a: Pt, b: Pt): Pt => [gridRound(a[0] + b[0], 2), gridRound(a[1] + b[1], 2)];
function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function cum(values: number[]): number[] {
  const out = [0]; let s = 0;
  for (const v of values) { s += v; out.push(s); }
  return out;
}

interface Figure {
  points: Record<string, Pt>;
  segs: Array<[string, string, string]>;
  arcs: Array<[string, number, number]>;            // (vertex, startDir, measure) — CCW region
  alabels: Array<[string, number, number, string]>; // (vertex, startDir, measure, text)
  leaders: Array<[string, number, number, number]>; // (vertex, dir, r1, r2) — neutral target marker
  ticks: Array<[string, string, number]>;
  plabels: Array<[string, number, number, string, string]>;
}

function buildFigure(p: Params): Figure {
  const task = p.task;
  const points: Record<string, Pt> = {};
  const segs: Array<[string, string, string]> = [];
  const arcs: Array<[string, number, number]> = [];
  const alabels: Array<[string, number, number, string]> = [];
  const leaders: Array<[string, number, number, number]> = [];
  const ticks: Array<[string, string, number]> = [];
  const plabels: Array<[string, number, number, string, string]> = [];

  if (task === "straight_line_missing_angle") {
    const regions = p["regions"] as number[], uidx = p["unknownIndex"] as number;
    const bounds = cum(regions);
    const O: Pt = [0, 0];
    points["O"] = O;
    const names: string[] = [];
    bounds.forEach((ang, i) => { const n = `B${i}`; points[n] = ray(O, ang, RAW_LEN); names.push(n); });
    segs.push([names[0]!, names[names.length - 1]!, "gl"]);
    for (let i = 1; i < bounds.length - 1; i++) segs.push(["O", names[i]!, "gl"]);
    for (let j = 0; j < regions.length; j++) {
      arcs.push(["O", bounds[j]!, regions[j]!]);
      alabels.push(["O", bounds[j]!, regions[j]!, j === uidx ? "x" : `${regions[j]}°`]);
    }
  } else if (task === "triangle_missing_angle" || task === "isosceles_base_angle") {
    let A: number, B: number; let apex = 0;
    if (task === "triangle_missing_angle") { A = p["A"] as number; B = p["B"] as number; }
    else { apex = p["apex"] as number; A = B = (180 - apex) / 2; }
    const L: Pt = [0, 0], Rr: Pt = [RAW_BASE, 0];
    const P = apexPoint(L, Rr, A, B);
    points["L"] = L; points["R"] = Rr; points["P"] = P;
    segs.push(["L", "R", "gl"], ["L", "P", "gl"], ["R", "P", "gl"]);
    // interior angle at each vertex = (startDir, measure) sweeping CCW through the interior.
    if (task === "triangle_missing_angle") {
      arcs.push(["L", 0, A], ["R", 180 - B, B], ["P", (A + 180) % 360, 180 - A - B]);
      alabels.push(["L", 0, A, `${A}°`], ["R", 180 - B, B, `${B}°`], ["P", (A + 180) % 360, 180 - A - B, "x"]);
      plabels.push(["L", -34, 30, "A", "end"], ["R", 34, 30, "B", "start"], ["P", 0, -18, "C", "middle"]);
    } else {
      arcs.push(["P", (A + 180) % 360, 180 - A - B], ["L", 0, A]);
      alabels.push(["P", (A + 180) % 360, 180 - A - B, `${apex}°`], ["L", 0, A, "x"]);
      ticks.push(["L", "P", A], ["R", "P", 180 - B]);
    }
  } else if (task === "vertically_opposite_angle") {
    const theta = p["theta"] as number;
    const O: Pt = [0, 0];
    points["O"] = O; points["E0"] = ray(O, 0, RAW_LEN); points["E180"] = ray(O, 180, RAW_LEN);
    points["Et"] = ray(O, theta, RAW_LEN); points["Et2"] = ray(O, theta + 180, RAW_LEN);
    segs.push(["E180", "E0", "gl"], ["Et2", "Et", "gl"]);
    // ONLY the given angle gets an arc; the target (x) is a label in the directly-opposite
    // region (the placer adds a neutral leader if that sector is too narrow for the label).
    arcs.push(["O", 0, theta]);
    alabels.push(["O", 0, theta, `${theta}°`], ["O", 180, theta, "x"]);
  } else {
    const regions = p["regions"] as number[], uidx = p["unknownIndex"] as number;
    const bounds = cum(regions);
    const O: Pt = [0, 0];
    points["O"] = O;
    const m = regions.length;
    for (let i = 0; i < m; i++) { points[`Rr${i}`] = ray(O, bounds[i]!, RAW_LEN); segs.push(["O", `Rr${i}`, "gl"]); }
    for (let j = 0; j < m; j++) {
      arcs.push(["O", bounds[j]!, regions[j]!]);
      alabels.push(["O", bounds[j]!, regions[j]!, j === uidx ? "x" : `${regions[j]}°`]);
    }
  }
  return { points, segs, arcs, alabels, leaders, ticks, plabels };
}

function apexPoint(L: Pt, Rr: Pt, A: number, B: number): Pt {
  const dLx = dirAt(A)[0], dLy = -dirAt(A)[1];
  const dRx = dirAt(180 - B)[0], dRy = -dirAt(180 - B)[1];
  const W = Rr[0] - L[0];
  const det = dLx * dRy - dLy * dRx;
  const s = new Rational(W * dRy, det);
  const ax = rat(L[0]).add(s.mul(rat(dLx)));
  const ay = rat(L[1]).add(s.mul(rat(dLy)));
  return [gridRound(ax.num, ax.den), gridRound(ay.num, ay.den)];
}

function layout(points: Record<string, Pt>): Record<string, Pt> {
  const xs = Object.values(points).map((p) => p[0]);
  const ys = Object.values(points).map((p) => p[1]);
  const minx = Math.min(...xs), maxx = Math.max(...xs), miny = Math.min(...ys), maxy = Math.max(...ys);
  const bw = Math.max(maxx - minx, 1), bh = Math.max(maxy - miny, 1);
  const sx = new Rational(SPAN_X, bw), sy = new Rational(SPAN_Y, bh);
  const s = sx.num * sy.den <= sy.num * sx.den ? sx : sy;   // min(sx, sy)
  const out: Record<string, Pt> = {};
  for (const [name, [x, y]] of Object.entries(points)) {
    const nx = rat(CX).sub(rat(bw).mul(s).div(rat(2))).add(rat(x - minx).mul(s));
    const ny = rat(CY).sub(rat(bh).mul(s).div(rat(2))).add(rat(y - miny).mul(s));
    out[name] = [gridRound(nx.num, nx.den), gridRound(ny.num, ny.den)];
  }
  return out;
}

function rayAt(v: Pt, theta: number, radius: number): Pt {
  return [v[0] + gridRound(dirAt(theta)[0] * radius, R), v[1] - gridRound(dirAt(theta)[1] * radius, R)];
}
function isqrt(n: number): number {        // exact integer floor sqrt (no float / no trig)
  if (n < 2) return n;
  let x = n, y = Math.floor((n + 1) / 2);
  while (y < x) { x = y; y = Math.floor((x + Math.floor(n / x)) / 2); }
  return x;
}
const edgeLen = (p: Pt, q: Pt): number => isqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2);

// One radius per arc: graduated at a shared vertex (angles on a line / around a point);
// scaled to the shortest incident edge for triangle/isosceles vertices; default for VO.
function arcRadii(fig: Figure, P: Record<string, Pt>): number[] {
  const sameVertex = new Set(fig.arcs.map((a) => a[0])).size === 1 && fig.arcs.length >= 2;
  return fig.arcs.map(([vn], j) => {
    if (sameVertex) return ARC_BASE + j * ARC_STEP;
    const inc = fig.segs.filter(([a, b]) => a === vn || b === vn).map(([a, b]) => edgeLen(P[a]!, P[b]!));
    return inc.length ? Math.min(ARC_TRI_MAX, Math.floor((Math.min(...inc) * ARC_TRI_NUM) / ARC_TRI_DEN)) : ARC_DEFAULT;
  });
}
// Arc of the CCW sector [start, start+measure]. Reflex-correct: large-arc-flag = 1 iff
// measure > 180 (exactly 180 -> 0); sweep-flag is always 0 (the intended interior sector).
function arcPath(v: Pt, start: number, measure: number, radius: number): string {
  const e1 = rayAt(v, start, radius), e2 = rayAt(v, start + measure, radius);
  const large = measure > 180 ? 1 : 0;
  return `M ${e1[0]} ${e1[1]} A ${radius} ${radius} 0 ${large} 0 ${e2[0]} ${e2[1]}`;
}

// --- Adaptive label placement (v1.2.1) -------------------------------------- //
type TextLabel = [number, number, string, string]; // x, y, anchor, text
type Box = [number, number, number, number];
type Leader = readonly [Pt, Pt];
const LBL_CHARW: Record<string, number> = { x: 16, "°": 11 };
const textW = (t: string): number => [...t].reduce((a, c) => a + (LBL_CHARW[c] ?? 17), 0);
const boxMake = (x: number, y: number, w: number): Box => [x - Math.floor(w / 2), y - LBL_ASC, x + (w - Math.floor(w / 2)), y + LBL_DESC];
const boxInCanvas = (b: Box): boolean => b[0] >= CANVAS_M && b[2] <= VIEW_W - CANVAS_M && b[1] >= CANVAS_M && b[3] <= CAPTION_TOP;
const boxesClear = (a: Box, b: Box, c: number): boolean => a[2] + c <= b[0] || b[2] + c <= a[0] || a[3] + c <= b[1] || b[3] + c <= a[1];
const ptBoxD2 = (px: number, py: number, b: Box): number => { const dx = Math.max(b[0] - px, 0, px - b[2]), dy = Math.max(b[1] - py, 0, py - b[3]); return dx * dx + dy * dy; };
const orient = (ax: number, ay: number, bx: number, by: number, cx: number, cy: number): number => (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);
const onSeg = (ax: number, ay: number, bx: number, by: number, cx: number, cy: number): boolean =>
  Math.min(ax, bx) <= cx && cx <= Math.max(ax, bx) && Math.min(ay, by) <= cy && cy <= Math.max(ay, by);
function segIntersect(ax: number, ay: number, bx: number, by: number, cx: number, cy: number, dx: number, dy: number): boolean {
  const d1 = orient(cx, cy, dx, dy, ax, ay), d2 = orient(cx, cy, dx, dy, bx, by), d3 = orient(ax, ay, bx, by, cx, cy), d4 = orient(ax, ay, bx, by, dx, dy);
  if ((d1 > 0) !== (d2 > 0) && (d3 > 0) !== (d4 > 0)) return true;
  if (d1 === 0 && onSeg(cx, cy, dx, dy, ax, ay)) return true;
  if (d2 === 0 && onSeg(cx, cy, dx, dy, bx, by)) return true;
  if (d3 === 0 && onSeg(ax, ay, bx, by, cx, cy)) return true;
  if (d4 === 0 && onSeg(ax, ay, bx, by, dx, dy)) return true;
  return false;
}
function segClearBox(ax: number, ay: number, bx: number, by: number, box: Box, c: number): boolean {
  const L: Box = [box[0] - c, box[1] - c, box[2] + c, box[3] + c];
  if (L[0] <= ax && ax <= L[2] && L[1] <= ay && ay <= L[3]) return false;
  if (L[0] <= bx && bx <= L[2] && L[1] <= by && by <= L[3]) return false;
  const cor: Pt[] = [[L[0], L[1]], [L[2], L[1]], [L[2], L[3]], [L[0], L[3]]];
  for (let i = 0; i < 4; i++) { const a = cor[i]!, e = cor[(i + 1) % 4]!; if (segIntersect(ax, ay, bx, by, a[0], a[1], e[0], e[1])) return false; }
  return true;
}
function arcClearBox(box: Box, v: Pt, ar: number, start: number, measure: number, c: number): boolean {
  const cc = c * c;
  for (let i = 0; i <= ARC_SAMPLES; i++) { const ang = start + Math.floor((measure * i) / ARC_SAMPLES); const pt = rayAt(v, ang, ar); if (ptBoxD2(pt[0], pt[1], box) < cc) return false; }
  return true;
}
function pointAlong(ax: number, ay: number, bx: number, by: number, back: number): Pt {
  const len = isqrt((bx - ax) ** 2 + (by - ay) ** 2);
  if (len <= back) return [ax, ay];
  const t = len - back;
  return [ax + Math.floor((bx - ax) * t / len), ay + Math.floor((by - ay) * t / len)];
}
function boxInsideWedge(box: Box, v: Pt, start: number, measure: number): boolean {
  for (const cx of [box[0], box[2]]) for (const cy of [box[1], box[3]]) if (!inCcwWedge(start, measure, v, [cx, cy])) return false;
  return true;
}
// Is point P at least c px from segment AB? Exact integer (squared) comparison.
function ptSegClear(px: number, py: number, ax: number, ay: number, bx: number, by: number, c: number): boolean {
  const dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy, cc = c * c;
  if (l2 === 0) return (px - ax) ** 2 + (py - ay) ** 2 >= cc;
  const t = (px - ax) * dx + (py - ay) * dy;
  if (t <= 0) return (px - ax) ** 2 + (py - ay) ** 2 >= cc;
  if (t >= l2) return (px - bx) ** 2 + (py - by) ** 2 >= cc;
  const pa2 = (px - ax) ** 2 + (py - ay) ** 2;
  return l2 * pa2 - t * t >= cc * l2;
}
function segSegClear(ax: number, ay: number, bx: number, by: number, cx: number, cy: number, dx: number, dy: number, c: number): boolean {
  if (segIntersect(ax, ay, bx, by, cx, cy, dx, dy)) return false;
  return ptSegClear(ax, ay, cx, cy, dx, dy, c) && ptSegClear(bx, by, cx, cy, dx, dy, c)
    && ptSegClear(cx, cy, ax, ay, bx, by, c) && ptSegClear(dx, dy, ax, ay, bx, by, c);
}
function arcClearSeg(seg: Leader, v: Pt, ar: number, start: number, measure: number, c: number): boolean {
  for (let i = 0; i <= ARC_SAMPLES; i++) { const ang = start + Math.floor((measure * i) / ARC_SAMPLES); const pt = rayAt(v, ang, ar); if (!ptSegClear(pt[0], pt[1], seg[0][0], seg[0][1], seg[1][0], seg[1][1], c)) return false; }
  return true;
}
const segLen2 = (s: Leader): number => (s[1][0] - s[0][0]) ** 2 + (s[1][1] - s[0][1]) ** 2;
function leaderClearsGeometry(seg: Leader, segLines: [Pt, Pt][], arcsObs: [Pt, number, number, number][], vertices: Pt[], c: number): boolean {
  const [ix, iy] = seg[0], [ox, oy] = seg[1];
  for (const [A, B] of segLines) if (!segSegClear(ix, iy, ox, oy, A[0], A[1], B[0], B[1], c)) return false;
  for (const [av, r, s, m] of arcsObs) if (!arcClearSeg(seg, av, r, s, m, c)) return false;
  for (const vtx of vertices) if (!ptSegClear(vtx[0], vtx[1], ix, iy, ox, oy, c)) return false;
  return true;
}

interface Placed { placements: TextLabel[]; leaders: (Leader | null)[]; }
function placeLabels(P: Record<string, Pt>, fig: Figure): Placed | null {
  const ar = arcRadii(fig, P);
  const rmap = new Map(fig.arcs.map(([vn, s, m], i) => [`${vn}|${s}|${m}`, ar[i]!]));
  const segLines = fig.segs.map(([a, b]) => [P[a]!, P[b]!] as [Pt, Pt]);
  const arcsObs = fig.arcs.map(([vn, s, m], i) => [P[vn]!, ar[i]!, s, m] as [Pt, number, number, number]);
  const vertices = Object.values(fig.points);
  const placed: Box[] = [];
  for (const [name, ox, oy, text, anchor] of fig.plabels) {
    const w = textW(text), p = P[name]!;
    const left = p[0] + ox - (anchor === "middle" ? Math.floor(w / 2) : anchor === "end" ? w : 0);
    placed.push([left, p[1] + oy - LBL_ASC, left + w, p[1] + oy + LBL_DESC]);
  }
  const boxOk = (box: Box): boolean => {
    if (!boxInCanvas(box)) return false;
    for (const [A, B] of segLines) if (!segClearBox(A[0], A[1], B[0], B[1], box, LBL_CLEAR)) return false;
    for (const [av, r, s, m] of arcsObs) if (!arcClearBox(box, av, r, s, m, LBL_CLEAR)) return false;
    for (const vtx of vertices) if (ptBoxD2(vtx[0], vtx[1], box) < LBL_CLEAR * LBL_CLEAR) return false;
    for (const pb of placed) if (!boxesClear(box, pb, LBL_CLEAR)) return false;
    return true;
  };
  const placements: TextLabel[] = [], leaders: (Leader | null)[] = [];
  for (const [vn, start, measure, text] of fig.alabels) {
    const v = P[vn]!, w = textW(text), bis = (((start + Math.floor(measure / 2)) % 360) + 360) % 360;
    const arad = rmap.get(`${vn}|${start}|${measure}`) ?? ARC_DEFAULT;
    const s = dirAt(Math.floor(measure / 2))[1];
    const rFit = s > 0 ? Math.floor(((Math.floor(w / 2) + LBL_CLEAR) * R + s - 1) / s) : R_LABEL_MAX;
    const rLo = Math.max(arad + LBL_R0_GAP, rFit);
    let pos: Pt | null = null;
    for (let r = rLo; r <= R_LABEL_MAX; r += LBL_STEP) {
      const cand = rayAt(v, bis, r), box = boxMake(cand[0], cand[1], w);
      if (!boxInCanvas(box)) break;
      if (boxInsideWedge(box, v, start, measure) && boxOk(box)) { pos = cand; break; }
    }
    if (pos === null) return null;
    const box = boxMake(pos[0], pos[1], w);
    let leaderSeg: Leader | null = null;
    if (measure < NARROW_DEG) {
      const rIn = Math.max(arad + LEAD_IN, Math.floor((LBL_CLEAR * R + s - 1) / s) + 2);
      const inner = rayAt(v, bis, rIn);
      const back = Math.floor(isqrt(w * w + LBL_H * LBL_H) / 2) + LEAD_BACK;
      const outer = pointAlong(inner[0], inner[1], pos[0], pos[1], back);
      const seg: Leader = [inner, outer];
      if (!(inner[0] === outer[0] && inner[1] === outer[1]) && segLen2(seg) >= LEADER_MIN * LEADER_MIN
        && inCcwWedge(start, measure, v, inner) && leaderClearsGeometry(seg, segLines, arcsObs, vertices, LBL_CLEAR)
        && segClearBox(inner[0], inner[1], outer[0], outer[1], box, 0)) {
        leaderSeg = seg;
      }
    }
    placements.push([pos[0], pos[1], "middle", text]);
    leaders.push(leaderSeg);
    placed.push(box);
  }
  const nPl = fig.plabels.length;
  for (let k = 0; k < leaders.length; k++) {
    const seg = leaders[k]; if (!seg) continue;
    for (let idx = 0; idx < placed.length; idx++) {
      if (idx === nPl + k) continue;
      if (!segClearBox(seg[0][0], seg[0][1], seg[1][0], seg[1][1], placed[idx]!, LBL_CLEAR)) return null;
    }
    for (let j = 0; j < leaders.length; j++) {
      const o = leaders[j];
      if (j !== k && o && !segSegClear(seg[0][0], seg[0][1], seg[1][0], seg[1][1], o[0][0], o[0][1], o[1][0], o[1][1], LBL_CLEAR)) return null;
    }
  }
  return { placements, leaders };
}

function textElements(P: Record<string, Pt>, fig: Figure): { texts: TextLabel[]; leaders: (Leader | null)[] } | null {
  const placed = placeLabels(P, fig);
  if (!placed) return null;
  const texts: TextLabel[] = [];
  for (const [name, ox, oy, text, anchor] of fig.plabels) { const p = P[name]!; texts.push([p[0] + ox, p[1] + oy, anchor, text]); }
  texts.push(...placed.placements);
  return { texts, leaders: placed.leaders };
}

function labelsOk(p: Params): boolean { const fig = buildFigure(p); return placeLabels(layout(fig.points), fig) !== null; }

function canonicalSvg(fig: Figure, alt: string, title: string, desc: string): string {
  const P = layout(fig.points);
  const out: string[] = [];
  out.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VIEW_W} ${VIEW_H}" role="img" aria-label="${esc(alt)}">`);
  out.push(`<title>${esc(title)}</title>`);
  out.push(`<desc>${esc(desc)}</desc>`);
  out.push(`<style>${STYLE}</style>`);
  for (const [a, b, cls] of fig.segs) out.push(`<line class="${cls}" x1="${P[a]![0]}" y1="${P[a]![1]}" x2="${P[b]![0]}" y2="${P[b]![1]}"/>`);
  const arcR = arcRadii(fig, P);
  fig.arcs.forEach(([vn, start, measure], k) => out.push(`<path class="ga" d="${arcPath(P[vn]!, start, measure, arcR[k]!)}"/>`));
  for (const [a, b, ang] of fig.ticks) {
    const m = mid(P[a]!, P[b]!);
    const d: Pt = [gridRound(dirAt(ang + 90)[0] * TICK, R), -gridRound(dirAt(ang + 90)[1] * TICK, R)];
    out.push(`<line class="gt" x1="${m[0] - d[0]}" y1="${m[1] - d[1]}" x2="${m[0] + d[0]}" y2="${m[1] + d[1]}"/>`);
  }
  const te = textElements(P, fig)!;
  for (const seg of te.leaders) if (seg) out.push(`<line class="gx" x1="${seg[0][0]}" y1="${seg[0][1]}" x2="${seg[1][0]}" y2="${seg[1][1]}"/>`);
  for (const [x, y, anchor, text] of te.texts) out.push(`<text x="${x}" y="${y}" text-anchor="${anchor}">${esc(text)}</text>`);
  out.push('<text class="gn" x="500" y="685" text-anchor="middle">NOT TO SCALE</text>');
  out.push("</svg>");
  return out.join("\n");
}

function ctx(p: Params): GeoCtx {
  const task = p.task;
  if (task === "straight_line_missing_angle" || task === "angles_at_point_missing") {
    const regions = p["regions"] as number[], uidx = p["unknownIndex"] as number;
    return { givens: regions.filter((_, i) => i !== uidx) };
  }
  if (task === "triangle_missing_angle") return { givens: [p["A"] as number, p["B"] as number] };
  if (task === "isosceles_base_angle") return { apex: p["apex"] as number, givens: [p["apex"] as number] };
  return { theta: p["theta"] as number, givens: [p["theta"] as number] };
}
const sum = (xs: number[]): number => xs.reduce((a, b) => a + b, 0);

export function solve(p: Params): number {
  const g = ctx(p);
  switch (p.task) {
    case "straight_line_missing_angle": return 180 - sum(g.givens);
    case "triangle_missing_angle": return 180 - (p["A"] as number) - (p["B"] as number);
    case "isosceles_base_angle": return (180 - (p["apex"] as number)) / 2;
    case "vertically_opposite_angle": return p["theta"] as number;
    case "angles_at_point_missing": return 360 - sum(g.givens);
  }
}

interface Cand { value: number; misconceptionId: string; rationale: string; }
export function generateDistractors(p: Params): Cand[] | null {
  const g = ctx(p);
  const correct = solve(p);
  const chosen: Cand[] = [];
  const seen = new Set<number>([correct]);
  for (const mid of rulesFor(p.task)) {
    const w = MISCONCEPTIONS[mid]!.wrong(g);
    if (w === null || !(w >= 1 && w <= 359) || seen.has(w)) continue;
    seen.add(w);
    chosen.push({ value: w, misconceptionId: mid, rationale: MISCONCEPTIONS[mid]!.observableError });
    if (chosen.length === 3) break;
  }
  return chosen.length === 3 ? chosen : null;
}

function accessibility(p: Params): { title: string; alt: string; desc: string; dataTable: Json } {
  const g = ctx(p);
  const gv = g.givens.map((v) => `${v} degrees`).join(", ");
  // Information-EQUIVALENT to the diagram: same givens/configuration, never the
  // theorem, calculation, or answer being assessed (see a11yEquivalentOk).
  let title: string, alt: string, desc: string;
  if (p.task === "straight_line_missing_angle") {
    title = "Angles on a straight line";
    alt = "Diagram: angles adjacent on one side of a straight line, with an unknown angle x.";
    desc = `Angles of ${gv} and an unknown angle x are adjacent, in order, along one side of a straight line.`;
  } else if (p.task === "triangle_missing_angle") {
    title = "Triangle ABC";
    alt = "Diagram: a triangle with two known angles and an unknown angle x.";
    desc = `Triangle ABC has an interior angle of ${p["A"]} degrees at A, an interior angle of ${p["B"]} degrees at B, and an unknown interior angle x at C.`;
  } else if (p.task === "isosceles_base_angle") {
    title = "Isosceles triangle";
    alt = "Diagram: a triangle with two sides marked equal, an apex angle, and an unknown base angle x.";
    desc = `Triangle ABC has its two slanted sides marked equal with single tick marks. The angle at the apex is ${p["apex"]} degrees, and the unknown base angle is marked x.`;
  } else if (p.task === "vertically_opposite_angle") {
    title = "Two intersecting straight lines";
    alt = "Diagram: two straight lines crossing at a point, with a given angle and the angle x in the opposite region.";
    desc = `Two straight lines cross at a point, forming four angles. One angle measures ${p["theta"]} degrees, and the unknown angle x is in the region directly opposite it.`;
  } else {
    title = "Angles around a point";
    alt = "Diagram: angles meeting consecutively around a point, with an unknown angle x.";
    desc = `Angles of ${gv} and an unknown angle x are arranged consecutively, with no gaps, around a single point.`;
  }
  const rows: Json[] = g.givens.map((v, i) => [`angle ${i + 1}`, `${v} degrees`]);
  rows.push(["x", "unknown"]);
  return { title, alt, desc, dataTable: { columns: ["angle", "value"], rows } };
}

// Theorem/answer phrasings the accessible text must never contain (it must be
// information-EQUIVALENT, not easier). Bare numbers like "180" are not banned.
const A11Y_BANNED = ["sum", "add up", "full turn", "straight angle", "are equal", "is equal",
  "equal to", "base angles", "make a straight", "make a full", "add to"];
const A11Y_REQUIRED: Record<Task, string[]> = {
  straight_line_missing_angle: ["straight line", "adjacent"],
  triangle_missing_angle: ["triangle abc"],
  isosceles_base_angle: ["marked equal", "apex"],
  vertically_opposite_angle: ["opposite", "cross"],
  angles_at_point_missing: ["around", "consecutively"],
};
function a11yEquivalentOk(p: Params, acc: { alt: string; desc: string }): boolean {
  const g = ctx(p);
  const blob = (acc.desc + " " + acc.alt).toLowerCase();
  if (A11Y_BANNED.some((b) => blob.includes(b))) return false;
  if (!A11Y_REQUIRED[p.task].every((r) => blob.includes(r))) return false;
  if (!acc.desc.toLowerCase().includes("unknown")) return false;
  return g.givens.every((v) => acc.desc.includes(`${v} degrees`));
}

// Is pt inside the CCW sector [start, start+measure] at vertex v? Integer math-frame test.
function inCcwWedge(start: number, measure: number, v: Pt, pt: Pt): boolean {
  const us = dirAt(start), ue = dirAt(start + measure);
  const pm: Pt = [pt[0] - v[0], -(pt[1] - v[1])];
  const cs = us[0] * pm[1] - us[1] * pm[0];   // > 0 if pm CCW of the start ray
  const ce = pm[0] * ue[1] - pm[1] * ue[0];   // > 0 if pm CW of the end ray
  if (measure < 180) return cs > 0 && ce > 0;
  if (measure > 180) return !(cs < 0 && ce < 0);
  return cs > 0;
}

export function generateSolution(p: Params): Json {
  const g = ctx(p);
  const ans = solve(p);
  if (p.task === "straight_line_missing_angle") {
    const s = g.givens.join(" + ");
    return { steps: [
      { number: 1, transformation: "State the angle fact", ruleOrTheorem: "Angles on a straight line sum to 180 degrees" },
      { number: 2, transformation: "Form the equation", intermediateResult: `x = 180 - (${s})`, dependsOn: [1] },
      { number: 3, transformation: "Evaluate", intermediateResult: `x = ${ans}°`, dependsOn: [2], marks: 1 }] };
  }
  if (p.task === "triangle_missing_angle") {
    return { steps: [
      { number: 1, transformation: "State the angle fact", ruleOrTheorem: "The interior angles of a triangle sum to 180 degrees" },
      { number: 2, transformation: "Form the equation", intermediateResult: `x = 180 - (${p["A"]} + ${p["B"]})`, dependsOn: [1] },
      { number: 3, transformation: "Evaluate", intermediateResult: `x = ${ans}°`, dependsOn: [2], marks: 1 }] };
  }
  if (p.task === "isosceles_base_angle") {
    return { steps: [
      { number: 1, transformation: "State the angle fact", ruleOrTheorem: "Base angles of an isosceles triangle are equal; the three angles sum to 180 degrees" },
      { number: 2, transformation: "Form the equation", intermediateResult: `x = (180 - ${p["apex"]}) / 2`, dependsOn: [1] },
      { number: 3, transformation: "Evaluate", intermediateResult: `x = ${ans}°`, dependsOn: [2], marks: 1 }] };
  }
  if (p.task === "vertically_opposite_angle") {
    return { steps: [
      { number: 1, transformation: "State the angle fact", ruleOrTheorem: "Vertically opposite angles are equal" },
      { number: 2, transformation: "Apply", intermediateResult: `x = ${p["theta"]}°`, dependsOn: [1], marks: 1 }] };
  }
  const s = g.givens.join(" + ");
  return { steps: [
    { number: 1, transformation: "State the angle fact", ruleOrTheorem: "Angles around a point sum to 360 degrees" },
    { number: 2, transformation: "Form the equation", intermediateResult: `x = 360 - (${s})`, dependsOn: [1] },
    { number: 3, transformation: "Evaluate", intermediateResult: `x = ${ans}°`, dependsOn: [2], marks: 1 }] };
}

function difficulty(p: Params): Json {
  const g = ctx(p);
  const givenCount = g.givens.length;
  const nonMult5 = g.givens.some((v) => v % 5 !== 0) || solve(p) % 5 !== 0;
  const obtuse = g.givens.some((v) => v > 90);
  const factors = (givenCount >= 3 ? 1 : 0) + (nonMult5 ? 1 : 0) + (obtuse ? 1 : 0);
  const [lo, hi] = TASK_BANDS[p.task];
  return {
    overallBand: lo + Math.min(factors, hi - lo),
    axes: {
      numericalComplexity: round3(Math.min(1.0, givenCount / 4.0)),
      reasoningSteps: p.task !== "vertically_opposite_angle" ? 0.5 : 0.25,
      representation: 0.6,
      abstraction: round3(0.3 + (nonMult5 ? 0.2 : 0.0)),
    },
  };
}

function partition(rng: Mulberry32, total: number, m: number): { regions: number[]; unknownIndex: number } {
  const parts: number[] = [];
  let remaining = total;
  for (let i = 0; i < m - 1; i++) {
    const hi = remaining - MIN_ANGLE * (m - 1 - i);
    const part = rng.nextInt(MIN_ANGLE, hi);
    parts.push(part); remaining -= part;
  }
  parts.push(remaining);
  const unknownIndex = rng.nextInt(0, m - 1);
  return { regions: parts, unknownIndex };
}

function drawParams(rng: Mulberry32, explicitTask: Task | undefined): Params {
  const task = explicitTask ?? rng.choice(TASKS);
  if (task === "straight_line_missing_angle") return { task, ...partition(rng, 180, rng.choice([2, 3, 4])) } as Params;
  if (task === "triangle_missing_angle") {
    const a = rng.nextInt(MIN_ANGLE, 180 - 2 * MIN_ANGLE);
    const b = rng.nextInt(MIN_ANGLE, 180 - MIN_ANGLE - a);
    return { task, A: a, B: b };
  }
  if (task === "isosceles_base_angle") return { task, apex: 2 * rng.nextInt(MIN_ANGLE, 80) };
  if (task === "vertically_opposite_angle") return { task, theta: rng.nextInt(MIN_ANGLE, 170) };
  return { task, ...partition(rng, 360, rng.choice([3, 4])) } as Params;
}

function guardsOk(p: Params): boolean {
  const task = p.task;
  const ans = solve(p);
  const g = ctx(p);
  if (!g.givens.every((v) => v >= MIN_ANGLE)) return false;
  if (task === "straight_line_missing_angle" || task === "triangle_missing_angle" || task === "isosceles_base_angle") {
    if (!(ans >= MIN_ANGLE && ans <= 180 - MIN_ANGLE)) return false;
  }
  if (task === "vertically_opposite_angle" && !(ans >= MIN_ANGLE && ans <= 170)) return false;
  if (task === "angles_at_point_missing" && !(ans >= MIN_ANGLE && ans <= 360 - MIN_ANGLE)) return false;
  if (task === "isosceles_base_angle") {
    const apex = p["apex"] as number;
    if (apex % 2 !== 0 || !(apex >= 20 && apex <= 160)) return false;
  }
  if (task === "straight_line_missing_angle" || task === "angles_at_point_missing") {
    if (sum(p["regions"] as number[]) !== (task === "straight_line_missing_angle" ? 180 : 360)) return false;
  }
  if (!labelsOk(p)) return false; // realisability: angle/vertex labels must not collide
  return true;
}

function acceptable(p: Params, answerType: string): Cand[] | null {
  if (!guardsOk(p)) return null;
  if (answerType === "multiple-choice") {
    if (!MC_TASKS.includes(p.task)) return null;
    return generateDistractors(p);
  }
  return [];
}

export function generate(seed: number, config: Config = {}): Record<string, Json> {
  const answerType = resolveInteractionType(config) === "multiple-choice" ? "multiple-choice" : "integer";
  const explicitTask = config.task;
  if (explicitTask != null && !TASKS.includes(explicitTask)) throw new Error(`unknown task: ${explicitTask}`);
  if (answerType === "multiple-choice" && explicitTask != null && !MC_TASKS.includes(explicitTask)) {
    throw new Error("vertically_opposite_angle is free-response only in geometry v1.2.x (current approved scope)");
  }
  const rng = new Mulberry32(seed);
  let params!: Params;
  let distractors: Cand[] | null = null;
  let ok = false;
  for (let i = 0; i < MAX_PARAM_ATTEMPTS; i++) {
    params = drawParams(rng, explicitTask);
    const result = acceptable(params, answerType);
    if (result === null) continue;
    distractors = result;
    ok = true;
    break;
  }
  if (!ok) throw new Error("could not find acceptable geometry parameters");

  const task = params.task;
  const ans = solve(params);
  const fig = buildFigure(params);
  const acc = accessibility(params);
  const svg = canonicalSvg(fig, acc.alt, acc.title, acc.desc);
  const interaction = answerType === "multiple-choice" ? "multiple-choice" : "free-response";

  const item: Record<string, Json> = {
    itemId: `ITEM-${GENERATOR_ID.replace(/\./g, "-")}-${seed}-${task}`,
    schemaVersion: "1.0.0",
    objectiveIds: [OBJECTIVE_BY_TASK[task]],
    generatorId: GENERATOR_ID,
    generatorVersion: GENERATOR_VERSION,
    seed,
    params: params as unknown as Json,
    interactionType: interaction,
    prompt: { instruction: "Find", blocks: [
      { kind: "text", text: "Find the size of the unknown angle x, in degrees." },
      { kind: "media-ref", ref: "fig-1" }] },
    answer: { type: "integer", canonical: { num: ans, den: 1 }, display: `${ans}°`, units: "degrees" },
    solution: generateSolution(params),
    difficulty: difficulty(params),
    calculatorPolicy: CALCULATOR_POLICY,
    media: [{ id: "fig-1", kind: "svg", svg, toScale: false, altText: acc.alt, longDescription: acc.desc, dataTableFallback: acc.dataTable }],
    accessibility: { spokenMath: acc.desc, altText: acc.alt, longDescription: acc.desc, nonColorIndicators: true },
    provenance: { origin: "generated", rightsStatus: "academy-owned", originalityNote: "Original parameterized item; diagram generated from the same parameters." },
    lifecycle: { state: "generated" },
  };

  if (answerType === "multiple-choice") {
    const mc = assembleMultipleChoice(rng, ans, distractors ?? [], (v) => ({ value: v, display: `${v}°` }));
    item["distractors"] = mc.distractors;
    item["options"] = mc.options;
  }
  return item;
}

// --- validation ---------------------------------------------------------- //
export interface CheckResult { name: string; result: "pass" | "fail"; detail: string; }
export interface ValidationResult { status: "pass" | "fail"; validatorVersion: string; checks: CheckResult[]; }
function hasPlaceholder(text: string): boolean { return /(?<![A-Za-z])[pqrtk](?![A-Za-z])/.test(text); }

export function validate(item: Record<string, Json>): ValidationResult {
  const checks: CheckResult[] = [];
  const add = (name: string, ok: boolean, detail = ""): void => { checks.push({ name, result: ok ? "pass" : "fail", detail }); };
  const params = item["params"] as unknown as Params;
  const task = params.task;
  const g = ctx(params);
  const ansF = item["answer"] as { type: string; canonical: { num: number; den: number }; display: string; units?: string };
  const ans = ansF.canonical.den === 1 ? ansF.canonical.num : NaN;

  add("params-in-domain", guardsOk(params), `task=${task}`);
  add("answer-type-consistency", ansF.type === "integer" && ansF.canonical.den === 1, `type=${ansF.type}`);
  add("units-degrees", ansF.units === "degrees", String(ansF.units));
  add("interaction-type", item["interactionType"] === "free-response" || item["interactionType"] === "multiple-choice", String(item["interactionType"]));

  let indep: number;
  if (task === "straight_line_missing_angle") indep = 180 - sum(g.givens);
  else if (task === "triangle_missing_angle") indep = 180 - (params["A"] as number) - (params["B"] as number);
  else if (task === "isosceles_base_angle") indep = (180 - (params["apex"] as number)) / 2;
  else if (task === "vertically_opposite_angle") indep = params["theta"] as number;
  else indep = 360 - sum(g.givens);
  add("closure-agreement", indep === ans, `${indep} vs ${ans}`);

  const fig = buildFigure(params);
  const acc = accessibility(params);
  const rebuilt = canonicalSvg(fig, acc.alt, acc.title, acc.desc);
  const media = item["media"] as Array<{ kind: string; svg: string; toScale?: boolean }> | undefined;
  const storedSvg = media && media[0] ? media[0].svg : "";
  add("svg-realises-data", rebuilt === storedSvg, "recomputed SVG matches stored SVG byte-for-byte");
  add("media-present", Boolean(media && media[0] && media[0].kind === "svg"), "one svg media asset");
  add("not-to-scale", Boolean(media && media[0] && media[0].toScale === false) && storedSvg.includes("NOT TO SCALE"), "toScale false + label");
  add("labels-non-overlapping", labelsOk(params), "angle/vertex label boxes do not collide");

  // --- Semantic arc checks: PARSE the SVG arc commands and verify they realise each
  // region's measure, sector direction, and major/minor nature (catches a reflex
  // region drawn with its minor arc).
  const P = layout(fig.points);
  const arcR = arcRadii(fig, P);
  const arcCmds = [...storedSvg.matchAll(/<path class="ga" d="M (-?\d+) (-?\d+) A (\d+) (\d+) 0 (\d) (\d) (-?\d+) (-?\d+)"\/>/g)]
    .map((m) => m.slice(1, 9).map(Number));
  let regionOk = arcCmds.length === fig.arcs.length;
  let largeOk = regionOk, sweepOk = regionOk;
  fig.arcs.forEach(([vn, start, measure], k) => {
    const a = arcCmds[k]; if (!a) return;
    const [x1, y1, rx, ry, large, sweep, x2, y2] = a as number[];
    const V = P[vn]!, rr = arcR[k]!, e1 = rayAt(V, start, rr), e2 = rayAt(V, start + measure, rr);
    regionOk = regionOk && x1 === e1[0] && y1 === e1[1] && x2 === e2[0] && y2 === e2[1] && rx === rr && ry === rr;
    largeOk = largeOk && large === (measure > 180 ? 1 : 0);
    sweepOk = sweepOk && sweep === 0;
  });
  add("arc-region-measure-agreement", regionOk, "arc endpoints realise each region's (start, measure, radius)");
  add("arc-large-flag-correct", largeOk, "large-arc-flag = 1 iff region exceeds 180 degrees");
  add("arc-sweep-correct", sweepOk, "sweep-flag = 0 (CCW interior sector)");

  if (task === "straight_line_missing_angle" || task === "angles_at_point_missing") {
    let chain = arcCmds.length === fig.arcs.length;
    for (let k = 0; k < fig.arcs.length - 1; k++) {
      chain = chain && (fig.arcs[k]![1] + fig.arcs[k]![2]) % 360 === fig.arcs[k + 1]![1] % 360;
    }
    add("arc-matches-cyclic-region", chain, "arcs tile the angle consecutively");
  }

  // --- Adaptive label-placement clearances. Recompute the placement (svg-realises-data
  // ties it to the stored SVG) and test the COMPLETE label bounding boxes against every
  // ray, arc, vertex, label, and leader, with a documented minimum clearance (LBL_CLEAR).
  const placed = placeLabels(P, fig);
  add("label-placement-feasible", placed !== null, `all labels placed with >= ${LBL_CLEAR}px clearance`);
  if (placed !== null) {
    const { placements, leaders } = placed;
    const plabelBoxes: Box[] = fig.plabels.map(([name, ox, oy, t, anchor]) => {
      const wl = textW(t), p = P[name]!;
      const left = p[0] + ox - (anchor === "middle" ? Math.floor(wl / 2) : anchor === "end" ? wl : 0);
      return [left, p[1] + oy - LBL_ASC, left + wl, p[1] + oy + LBL_DESC] as Box;
    });
    const alabelBoxes: Box[] = placements.map(([x, y, , t]) => boxMake(x, y, textW(t)));
    const allBoxes = [...plabelBoxes, ...alabelBoxes];
    const segLines = fig.segs.map(([a, b]) => [P[a]!, P[b]!] as [Pt, Pt]);
    const vertices = Object.values(fig.points);

    add("labels-within-canvas", alabelBoxes.every(boxInCanvas), `boxes inside [${CANVAS_M}, ${VIEW_W - CANVAS_M}] x [${CANVAS_M}, ${CAPTION_TOP}]`);
    let ll = true;
    for (let i = 0; i < allBoxes.length; i++) for (let j = i + 1; j < allBoxes.length; j++) if (!boxesClear(allBoxes[i]!, allBoxes[j]!, LBL_CLEAR)) ll = false;
    add("label-label-clearance", ll, `label boxes clear each other by >= ${LBL_CLEAR}px`);
    add("label-ray-clearance", alabelBoxes.every((b) => segLines.every(([A, B]) => segClearBox(A[0], A[1], B[0], B[1], b, LBL_CLEAR))), `labels clear every drawn line by >= ${LBL_CLEAR}px`);
    add("label-arc-clearance", alabelBoxes.every((b) => fig.arcs.every(([vn, s, m], i) => arcClearBox(b, P[vn]!, arcR[i]!, s, m, LBL_CLEAR))), `labels clear every arc by >= ${LBL_CLEAR}px`);
    add("label-vertex-clearance", alabelBoxes.every((b) => vertices.every((vtx) => ptBoxD2(vtx[0], vtx[1], b) >= LBL_CLEAR * LBL_CLEAR)), `labels clear every vertex by >= ${LBL_CLEAR}px`);
    // --- Leader contract, PARSED from the serialized SVG. Leaders are radial, inside the
    // wedge, visually SECONDARY, non-degenerate, and clear of all geometry/labels.
    const gxSegs: Leader[] = [...storedSvg.matchAll(/<line class="gx" x1="(-?\d+)" y1="(-?\d+)" x2="(-?\d+)" y2="(-?\d+)"\/>/g)]
      .map((m) => [[Number(m[1]), Number(m[2])], [Number(m[3]), Number(m[4])]] as Leader);
    const styleOk = STYLE.includes(".gx{") && STYLE.includes(`stroke-width:${LEADER_STROKE_WIDTH}`)
      && STYLE.includes("stroke-dasharray:") && STYLE.includes("stroke-linecap:round")
      && LEADER_STROKE_WIDTH < Math.min(...GEOMETRY_STROKE_WIDTHS);
    add("leader-style-distinct-from-geometry", styleOk, "thinner + dashed + round-capped (not a ray/side/arc/tick)");
    add("leader-non-degenerate", gxSegs.every((s) => segLen2(s) > 0), "no zero-length leader");
    add("leader-minimum-length", gxSegs.every((s) => segLen2(s) >= LEADER_MIN * LEADER_MIN), `every leader >= ${LEADER_MIN}px`);
    const lclr = (s: Leader, A: Pt, B: Pt): boolean => segSegClear(s[0][0], s[0][1], s[1][0], s[1][1], A[0], A[1], B[0], B[1], LBL_CLEAR);
    add("leader-ray-clearance", gxSegs.every((s) => segLines.every(([A, B]) => lclr(s, A, B))), "leaders clear every ray");
    add("leader-side-clearance", gxSegs.every((s) => segLines.every(([A, B]) => lclr(s, A, B))), "leaders clear every triangle side");
    add("leader-arc-clearance", gxSegs.every((s) => fig.arcs.every(([vn, st, m], i) => arcClearSeg(s, P[vn]!, arcR[i]!, st, m, LBL_CLEAR))), "leaders clear every arc");
    add("leader-vertex-clearance", gxSegs.every((s) => vertices.every((vtx) => ptSegClear(vtx[0], vtx[1], s[0][0], s[0][1], s[1][0], s[1][1], LBL_CLEAR))), "leaders clear every vertex");
    let leadOk = true;
    leaders.forEach((seg, k) => {
      if (!seg) return;
      const others = [...plabelBoxes, ...alabelBoxes.filter((_, j) => j !== k)];
      if (!others.every((b) => segClearBox(seg[0][0], seg[0][1], seg[1][0], seg[1][1], b, LBL_CLEAR))) leadOk = false;
    });
    add("leader-label-clearance", leadOk, "no leader crosses a label box");
    add("leader-does-not-cross-label", leadOk, "no leader crosses another label box");
    let llc = true;
    for (let i = 0; i < gxSegs.length; i++) for (let j = i + 1; j < gxSegs.length; j++) {
      const a = gxSegs[i]!, b = gxSegs[j]!;
      if (!segSegClear(a[0][0], a[0][1], a[1][0], a[1][1], b[0][0], b[0][1], b[1][0], b[1][1], LBL_CLEAR)) llc = false;
    }
    add("leader-leader-clearance", llc, "leaders do not cross each other");
    let routeOk = true;
    leaders.forEach((seg, k) => { if (seg) { const [vn, start, measure] = fig.alabels[k]!; if (!inCcwWedge(start, measure, P[vn]!, seg[0])) routeOk = false; } });
    add("leader-route-unambiguous", routeOk, "each leader starts inside its sector and points to its label");

    let attribOk = true, smallOk = true, reflexOk = true;
    fig.alabels.forEach(([vn, start, measure], k) => {
      const attributable = boxInsideWedge(alabelBoxes[k]!, P[vn]!, start, measure)
        || (leaders[k] !== null && inCcwWedge(start, measure, P[vn]!, leaders[k]![0]));
      attribOk = attribOk && attributable;
      if (measure < NARROW_DEG) smallOk = smallOk && attributable;
      if (measure > 180) reflexOk = reflexOk && attributable;
    });
    add("label-inside-intended-region", attribOk, "every label is inside its sector or led into it");
    add("small-sector-label-unambiguous", smallOk, `narrow (< ${NARROW_DEG} deg) labels are inside or led into their sector`);
    add("reflex-region-rendered-correctly", reflexOk && largeOk, "regions > 180 use the reflex arc with an attributable label");
  }

  if (task === "vertically_opposite_angle") {
    const ga = (storedSvg.match(/<path class="ga"/g) ?? []).length;
    const gt = (storedSvg.match(/class="gt"/g) ?? []).length;
    add("no-theorem-revealing-markers", ga === 1 && gt === 0, `ga=${ga} gt=${gt}`);
    let okTarget = placed !== null;
    if (placed !== null) {
      const theta = params["theta"] as number;
      const { placements, leaders } = placed;
      fig.alabels.forEach(([, start2, measure2, text], k) => {
        void start2; void measure2;
        if (text === "x") {
          const box = boxMake(placements[k]![0], placements[k]![1], textW("x"));
          const led = leaders[k] !== null && inCcwWedge(180, theta, P["O"]!, leaders[k]![0]);
          okTarget = boxInsideWedge(box, P["O"]!, 180, theta) || led;
        }
      });
    }
    add("target-region-unambiguous", okTarget, "the x label (or its leader) lies in the opposite region");
  }

  add("a11y-equivalent-information", a11yEquivalentOk(params, acc), "accessible text is equivalent, not easier (no theorem/answer)");
  // Harden against a tampered stored description: stored accessibility/media text must
  // equal the canonical (recomputed) text byte-for-byte.
  const aStore = (item["accessibility"] as { longDescription?: string; altText?: string; spokenMath?: string }) ?? {};
  const media0 = (media && media[0] ? media[0] : {}) as { longDescription?: string; altText?: string };
  add("a11y-text-canonical",
    aStore.longDescription === acc.desc && aStore.altText === acc.alt && aStore.spokenMath === acc.desc
    && media0.longDescription === acc.desc && media0.altText === acc.alt,
    "stored accessibility/media text matches the canonical description");

  const numeric = fig.alabels.filter(([, , , t]) => t.endsWith("°")).map(([, , , t]) => parseInt(t, 10)).sort((a, b) => a - b);
  const xCount = fig.alabels.filter(([, , , t]) => t === "x").length;
  add("no-answer-leakage", xCount === 1 && JSON.stringify(numeric) === JSON.stringify([...g.givens].sort((a, b) => a - b)),
    `x-labels=${xCount}`);

  const steps = (item["solution"] as { steps: Array<{ intermediateResult?: string }> }).steps;
  add("answer-solution-agree", (steps[steps.length - 1]?.intermediateResult ?? "").includes(ansF.display), "");

  const distractors = item["distractors"] as Array<{ value: number; misconceptionId: string; rationale?: string }> | undefined;
  if (distractors) {
    const mids = distractors.map((d) => d.misconceptionId);
    add("distractors-distinct-misconceptions", new Set(mids).size === mids.length, JSON.stringify(mids));
    add("min-three-distractors", distractors.length >= 3, `${distractors.length}`);
    for (const d of distractors) {
      const m = MISCONCEPTIONS[d.misconceptionId];
      add("distractor-misconception-known", Boolean(m), d.misconceptionId);
      if (m) {
        const expected = m.wrong(g);
        add("distractor-value-matches-rule", expected !== null && expected === d.value, d.misconceptionId);
        add("distractor-rationale-matches", d.rationale === m.observableError, d.misconceptionId);
        add("distractor-feedback-present", Boolean(m.feedback), d.misconceptionId);
        add("distractor-feedback-clean", !hasPlaceholder(m.feedback), m.feedback);
        add("distractor-not-answer", d.value !== ans, `${d.value} vs ${ans}`);
      }
    }
  }
  const options = item["options"] as Array<{ display: string; correct: boolean }> | undefined;
  if (options) {
    const correct = options.filter((o) => o.correct);
    add("exactly-one-correct", correct.length === 1 && correct[0]!.display === ansF.display, "");
    const wrong = options.filter((o) => !o.correct).map((o) => o.display);
    add("distractors-unique", new Set(wrong).size === wrong.length, "");
  }

  const a = item["accessibility"] as { spokenMath?: string; altText?: string; longDescription?: string };
  add("a11y-fields-present", Boolean(a.spokenMath && a.altText && a.longDescription), "");
  add("a11y-no-answer-in-text", (a.longDescription ?? "").includes("unknown") && !(a.longDescription ?? "").includes(ansF.display), "");
  const prov = item["provenance"] as { origin?: string; rightsStatus?: string };
  add("provenance-complete", Boolean(prov.origin && prov.rightsStatus), "");
  add("version-fields-present", Boolean(item["generatorId"]) && Boolean(item["generatorVersion"]), "");

  const status = checks.every((c) => c.result === "pass") ? "pass" : "fail";
  return { status, validatorVersion: "1.2.3", checks };
}

export function serialize(item: Record<string, Json>): string { return canonicalStringify(item); }
