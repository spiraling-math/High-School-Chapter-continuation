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
export const GENERATOR_VERSION = "1.0.0";

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
const ARC_R = 70, LBL_R = 120, TICK = 22;
const STYLE = ".gl{stroke:#111;stroke-width:3;fill:none}.ga{stroke:#111;stroke-width:2;fill:none}"
  + ".gt{stroke:#111;stroke-width:3}.gv{fill:#111}text{font-family:sans-serif;font-size:30px;fill:#111}"
  + ".gn{font-size:22px;fill:#444;letter-spacing:1px}";

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
  arcs: Array<[string, number, number]>;
  alabels: Array<[string, number, number, string]>;
  ticks: Array<[string, string, number]>;
  plabels: Array<[string, number, number, string, string]>;
}

function buildFigure(p: Params): Figure {
  const task = p.task;
  const points: Record<string, Pt> = {};
  const segs: Array<[string, string, string]> = [];
  const arcs: Array<[string, number, number]> = [];
  const alabels: Array<[string, number, number, string]> = [];
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
      arcs.push(["O", bounds[j]!, bounds[j + 1]!]);
      alabels.push(["O", bounds[j]!, bounds[j + 1]!, j === uidx ? "x" : `${regions[j]}°`]);
    }
  } else if (task === "triangle_missing_angle" || task === "isosceles_base_angle") {
    let A: number, B: number; let apex = 0;
    if (task === "triangle_missing_angle") { A = p["A"] as number; B = p["B"] as number; }
    else { apex = p["apex"] as number; A = B = (180 - apex) / 2; }
    const L: Pt = [0, 0], Rr: Pt = [RAW_BASE, 0];
    const P = apexPoint(L, Rr, A, B);
    points["L"] = L; points["R"] = Rr; points["P"] = P;
    segs.push(["L", "R", "gl"], ["L", "P", "gl"], ["R", "P", "gl"]);
    if (task === "triangle_missing_angle") {
      arcs.push(["L", 0, A], ["R", 180 - B, 180], ["P", (A + 180) % 360, (360 - B) % 360]);
      alabels.push(["L", 0, A, `${A}°`], ["R", 180 - B, 180, `${B}°`], ["P", (A + 180) % 360, (360 - B) % 360, "x"]);
      plabels.push(["L", -34, 30, "A", "end"], ["R", 34, 30, "B", "start"], ["P", 0, -18, "C", "middle"]);
    } else {
      arcs.push(["P", (A + 180) % 360, (360 - B) % 360], ["L", 0, A]);
      alabels.push(["P", (A + 180) % 360, (360 - B) % 360, `${apex}°`], ["L", 0, A, "x"]);
      ticks.push(["L", "P", A], ["R", "P", 180 - B]);
    }
  } else if (task === "vertically_opposite_angle") {
    const theta = p["theta"] as number;
    const O: Pt = [0, 0];
    points["O"] = O; points["E0"] = ray(O, 0, RAW_LEN); points["E180"] = ray(O, 180, RAW_LEN);
    points["Et"] = ray(O, theta, RAW_LEN); points["Et2"] = ray(O, theta + 180, RAW_LEN);
    segs.push(["E180", "E0", "gl"], ["Et2", "Et", "gl"]);
    arcs.push(["O", 0, theta], ["O", 180, (theta + 180) % 360]);
    alabels.push(["O", 0, theta, `${theta}°`], ["O", 180, (theta + 180) % 360, "x"]);
  } else {
    const regions = p["regions"] as number[], uidx = p["unknownIndex"] as number;
    const bounds = cum(regions);
    const O: Pt = [0, 0];
    points["O"] = O;
    const m = regions.length;
    for (let i = 0; i < m; i++) { points[`Rr${i}`] = ray(O, bounds[i]!, RAW_LEN); segs.push(["O", `Rr${i}`, "gl"]); }
    for (let j = 0; j < m; j++) {
      arcs.push(["O", bounds[j]!, bounds[j + 1]!]);
      alabels.push(["O", bounds[j]!, bounds[j + 1]!, j === uidx ? "x" : `${regions[j]}°`]);
    }
  }
  return { points, segs, arcs, alabels, ticks, plabels };
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

function arcPath(v: Pt, a1: number, a2: number): string {
  const e1: Pt = [v[0] + gridRound(dirAt(a1)[0] * ARC_R, R), v[1] - gridRound(dirAt(a1)[1] * ARC_R, R)];
  const e2: Pt = [v[0] + gridRound(dirAt(a2)[0] * ARC_R, R), v[1] - gridRound(dirAt(a2)[1] * ARC_R, R)];
  const cross = (e1[0] - v[0]) * (e2[1] - v[1]) - (e1[1] - v[1]) * (e2[0] - v[0]);
  const sweep = cross < 0 ? 1 : 0;
  return `M ${e1[0]} ${e1[1]} A ${ARC_R} ${ARC_R} 0 0 ${sweep} ${e2[0]} ${e2[1]}`;
}
function labelPos(v: Pt, a1: number, a2: number): Pt {
  const p1: Pt = [v[0] + gridRound(dirAt(a1)[0] * LBL_R, R), v[1] - gridRound(dirAt(a1)[1] * LBL_R, R)];
  const p2: Pt = [v[0] + gridRound(dirAt(a2)[0] * LBL_R, R), v[1] - gridRound(dirAt(a2)[1] * LBL_R, R)];
  return mid(p1, p2);
}

type TextLabel = [number, number, string, string]; // x, y, anchor, text
function textLabelPositions(P: Record<string, Pt>, fig: Figure): TextLabel[] {
  // Single source for canonicalSvg's <text> AND the overlap guard, so the boxes
  // always match the rendered label positions. NOT TO SCALE is structural (excluded).
  const out: TextLabel[] = [];
  for (const [name, ox, oy, text, anchor] of fig.plabels) { const p = P[name]!; out.push([p[0] + ox, p[1] + oy, anchor, text]); }
  for (const [vn, a1, a2, text] of fig.alabels) { const lp = labelPos(P[vn]!, a1, a2); out.push([lp[0], lp[1], "middle", text]); }
  return out;
}

const LBL_CHARW: Record<string, number> = { x: 16, "°": 11 };
const LBL_ASC = 22, LBL_DESC = 8;
function labelBox(x: number, y: number, anchor: string, text: string): [number, number, number, number] {
  const w = [...text].reduce((a, c) => a + (LBL_CHARW[c] ?? 17), 0);
  const left = anchor === "middle" ? x - Math.floor(w / 2) : anchor === "end" ? x - w : x;
  return [left, y - LBL_ASC, left + w, y + LBL_DESC];
}
function labelsOk(p: Params): boolean {
  const fig = buildFigure(p);
  const P = layout(fig.points);
  const boxes = textLabelPositions(P, fig).map(([x, y, anc, t]) => labelBox(x, y, anc, t));
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i]!, b = boxes[j]!;
    if (!(a[2] <= b[0] || b[2] <= a[0] || a[3] <= b[1] || b[3] <= a[1])) return false;
  }
  return true;
}

function canonicalSvg(fig: Figure, alt: string, title: string, desc: string): string {
  const P = layout(fig.points);
  const out: string[] = [];
  out.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${VIEW_W} ${VIEW_H}" role="img" aria-label="${esc(alt)}">`);
  out.push(`<title>${esc(title)}</title>`);
  out.push(`<desc>${esc(desc)}</desc>`);
  out.push(`<style>${STYLE}</style>`);
  for (const [a, b, cls] of fig.segs) out.push(`<line class="${cls}" x1="${P[a]![0]}" y1="${P[a]![1]}" x2="${P[b]![0]}" y2="${P[b]![1]}"/>`);
  for (const [vn, a1, a2] of fig.arcs) out.push(`<path class="ga" d="${arcPath(P[vn]!, a1, a2)}"/>`);
  for (const [a, b, ang] of fig.ticks) {
    const m = mid(P[a]!, P[b]!);
    const d: Pt = [gridRound(dirAt(ang + 90)[0] * TICK, R), -gridRound(dirAt(ang + 90)[1] * TICK, R)];
    out.push(`<line class="gt" x1="${m[0] - d[0]}" y1="${m[1] - d[1]}" x2="${m[0] + d[0]}" y2="${m[1] + d[1]}"/>`);
  }
  for (const [x, y, anchor, text] of textLabelPositions(P, fig)) {
    out.push(`<text x="${x}" y="${y}" text-anchor="${anchor}">${esc(text)}</text>`);
  }
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
  let title: string, alt: string, desc: string;
  if (p.task === "straight_line_missing_angle") {
    title = "Angles on a straight line";
    alt = "Diagram: angles meeting on a straight line, with an unknown angle x.";
    desc = `Angles of ${gv} and an unknown angle x lie along one side of a straight line and together make a straight angle of 180 degrees.`;
  } else if (p.task === "triangle_missing_angle") {
    title = "Triangle ABC";
    alt = "Diagram: a triangle with two known angles and an unknown angle x.";
    desc = `Triangle ABC has interior angles of ${p["A"]} degrees at A and ${p["B"]} degrees at B, and an unknown interior angle x at C.`;
  } else if (p.task === "isosceles_base_angle") {
    title = "Isosceles triangle";
    alt = "Diagram: an isosceles triangle with the apex angle given and an unknown base angle x.";
    desc = `An isosceles triangle has an apex angle of ${p["apex"]} degrees and two equal sides marked with single tick marks; each base angle is equal, and one is the unknown x.`;
  } else if (p.task === "vertically_opposite_angle") {
    title = "Two intersecting straight lines";
    alt = "Diagram: two straight lines crossing at a point, with a given angle and the angle x opposite it.";
    desc = `Two straight lines cross at a point. One angle is ${p["theta"]} degrees and the unknown angle x is the angle vertically opposite it.`;
  } else {
    title = "Angles around a point";
    alt = "Diagram: several angles meeting around a point, with an unknown angle x.";
    desc = `Angles of ${gv} and an unknown angle x meet around a single point and together make a full turn of 360 degrees.`;
  }
  const rows: Json[] = g.givens.map((v, i) => [`angle ${i + 1}`, `${v} degrees`]);
  rows.push(["x", "unknown"]);
  return { title, alt, desc, dataTable: { columns: ["angle", "value"], rows } };
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
    throw new Error("vertically_opposite_angle is free-response only in v1.0.0");
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
  return { status, validatorVersion: "1.0.0", checks };
}

export function serialize(item: Record<string, Json>): string { return canonicalStringify(item); }
