/**
 * gen.geometry.transformations — labelled object model, exact congruence + orientation checks
 * (owner G), the INDEPENDENT validator (owner H), describe-task family-specific uniqueness (owner D),
 * and the fixed-point policy (owner E).
 *
 * Byte-for-byte TypeScript mirror of oracle/spi_oracle/transformations_shapes.py.
 * All arithmetic is exact integer — no trig, float, or tolerance.
 */

import {
  type Point,
  reflectionVertical,
  reflectionHorizontal,
  reflectionDiagonal,
  rotationDesc,
  translationDesc,
  deepEqual,
} from "./transformations-core.ts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = any;

export const OBJECT_VERTEX_COUNT: Record<string, number> = {
  point: 1,
  segment: 2,
  triangle: 3,
  quadrilateral: 4,
};
export const SOURCE_LABELS: Record<string, string[]> = {
  point: ["P"],
  segment: ["A", "B"],
  triangle: ["A", "B", "C"],
  quadrilateral: ["A", "B", "C", "D"],
};
export const PRIME = "′"; // U+2032 PRIME — canonical image-label suffix (owner B)

export function imageLabels(objType: string): string[] {
  return (SOURCE_LABELS[objType] as string[]).map((lab) => lab + PRIME);
}

// --------------------------------------------------------------------------- //
// Exact metric primitives (owner G)
// --------------------------------------------------------------------------- //
export function sqDist(p: Point, q: Point): number {
  return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2;
}

function pairwiseSqDists(verts: Point[]): number[] {
  const n = verts.length;
  const out: number[] = [];
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      out.push(sqDist(verts[i] as Point, verts[j] as Point));
    }
  }
  return out;
}

export function signedArea2(verts: Point[]): number {
  const n = verts.length;
  let s = 0;
  for (let i = 0; i < n; i++) {
    const [x1, y1] = verts[i] as Point;
    const [x2, y2] = verts[(i + 1) % n] as Point;
    s += x1 * y2 - x2 * y1;
  }
  return s;
}

export function orientationSign(verts: Point[]): number {
  const a = signedArea2(verts);
  return (a > 0 ? 1 : 0) - (a < 0 ? 1 : 0);
}

export function isCollinear(verts: Point[]): boolean {
  return signedArea2(verts) === 0;
}

function segmentsCross(a: Point, b: Point, c: Point, d: Point): boolean {
  const o = (p: Point, q: Point, r: Point): number =>
    (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]);
  const d1 = o(c, d, a);
  const d2 = o(c, d, b);
  const d3 = o(a, b, c);
  const d4 = o(a, b, d);
  if (
    d1 > 0 !== d2 > 0 &&
    d3 > 0 !== d4 > 0 &&
    d1 !== 0 &&
    d2 !== 0 &&
    d3 !== 0 &&
    d4 !== 0
  ) {
    return true;
  }
  return false;
}

export function isSimpleQuad(verts: Point[]): boolean {
  const [a, b, c, d] = verts as [Point, Point, Point, Point];
  return !(segmentsCross(a, b, c, d) || segmentsCross(b, c, d, a));
}

export function congruentInCorrespondence(source: Point[], image: Point[], objType: string): boolean {
  if (objType === "point") {
    return true;
  }
  if (!deepEqual(pairwiseSqDists(source), pairwiseSqDists(image))) {
    return false;
  }
  if (objType === "triangle") {
    return !isCollinear(source) && !isCollinear(image);
  }
  if (objType === "quadrilateral") {
    return isSimpleQuad(source) && isSimpleQuad(image);
  }
  return true;
}

export function isUnchanged(source: Point[], image: Point[]): boolean {
  return deepEqual(source, image);
}

// --------------------------------------------------------------------------- //
// Independent per-transform image verification (owner H) — NOT via applyTransform.
// --------------------------------------------------------------------------- //
export function verifyTranslation(source: Point[], image: Point[], dx: number, dy: number): boolean {
  if (dx === 0 && dy === 0) {
    return false;
  }
  for (let i = 0; i < source.length; i++) {
    const s = source[i] as Point;
    const t = image[i] as Point;
    if (t[0] - s[0] !== dx || t[1] - s[1] !== dy) {
      return false;
    }
  }
  return true;
}

export function verifyReflection(source: Point[], image: Point[], axis: Json): boolean {
  for (let i = 0; i < source.length; i++) {
    const s = source[i] as Point;
    const t = image[i] as Point;
    if (axis.kind === "vertical") {
      if (!(s[1] === t[1] && s[0] + t[0] === 2 * axis.value)) {
        return false;
      }
    } else if (axis.kind === "horizontal") {
      if (!(s[0] === t[0] && s[1] + t[1] === 2 * axis.value)) {
        return false;
      }
    } else if (axis.kind === "diagonal") {
      if (axis.equation === "y=x") {
        if (!(s[0] === t[1] && s[1] === t[0])) {
          return false;
        }
      } else {
        if (!(s[0] === -t[1] && s[1] === -t[0])) {
          return false;
        }
      }
    }
  }
  return true;
}

function rotationRelation(s: Point, t: Point, h: number, k: number, q: number): boolean {
  const X = s[0] - h;
  const Y = s[1] - k;
  let rx: number;
  let ry: number;
  if (q === 1) {
    rx = -Y;
    ry = X;
  } else if (q === 2) {
    rx = -X;
    ry = -Y;
  } else {
    rx = Y;
    ry = -X;
  }
  return t[0] - h === rx && t[1] - k === ry;
}

export function verifyRotation(source: Point[], image: Point[], h: number, k: number, q: number): boolean {
  const inv: Record<number, number> = { 1: 3, 2: 2, 3: 1 };
  const invQ = inv[q] as number;
  for (let i = 0; i < source.length; i++) {
    const s = source[i] as Point;
    const t = image[i] as Point;
    if (sqDist(s, [h, k]) !== sqDist(t, [h, k])) {
      return false;
    }
    if (!rotationRelation(s, t, h, k, q)) {
      return false;
    }
    if (!rotationRelation(t, s, h, k, invQ)) {
      return false;
    }
  }
  return true;
}

// --------------------------------------------------------------------------- //
// Candidate reconstruction WITHIN one family (owner D, H) — for describe-task uniqueness.
// --------------------------------------------------------------------------- //
export function reconstructTranslations(source: Point[], image: Point[]): Json[] {
  const dx = (image[0] as Point)[0] - (source[0] as Point)[0];
  const dy = (image[0] as Point)[1] - (source[0] as Point)[1];
  if (dx === 0 && dy === 0) {
    return [];
  }
  return verifyTranslation(source, image, dx, dy) ? [translationDesc(dx, dy)] : [];
}

export function reconstructReflections(source: Point[], image: Point[]): Json[] {
  const out: Json[] = [];
  const moving: [Point, Point][] = [];
  for (let i = 0; i < source.length; i++) {
    const s = source[i] as Point;
    const t = image[i] as Point;
    if (!deepEqual(s, t)) {
      moving.push([s, t]);
    }
  }
  if (moving.length === 0) {
    return out;
  }
  const [s0, t0] = moving[0] as [Point, Point];
  // vertical x = a
  if (mod2(s0[0] + t0[0]) === 0) {
    const a = Math.floor((s0[0] + t0[0]) / 2);
    const cand = reflectionVertical(a);
    if (verifyReflection(source, image, cand.axis)) {
      out.push(cand);
    }
  }
  // horizontal y = b
  if (mod2(s0[1] + t0[1]) === 0) {
    const b = Math.floor((s0[1] + t0[1]) / 2);
    const cand = reflectionHorizontal(b);
    if (verifyReflection(source, image, cand.axis) && !containsDesc(out, cand)) {
      out.push(cand);
    }
  }
  for (const eq of ["y=x", "y=-x"]) {
    const cand = reflectionDiagonal(eq);
    if (verifyReflection(source, image, cand.axis) && !containsDesc(out, cand)) {
      out.push(cand);
    }
  }
  return out;
}

function containsDesc(arr: Json[], cand: Json): boolean {
  return arr.some((d) => deepEqual(d, cand));
}

/** Non-negative remainder mod 2, matching Python's `% 2` on possibly-negative integers. */
function mod2(n: number): number {
  return ((n % 2) + 2) % 2;
}

function solveCentre(s: Point, t: Point, q: number): Point | null {
  const sx = s[0];
  const sy = s[1];
  const tx = t[0];
  const ty = t[1];
  let hxNum: number;
  let kyNum: number;
  if (q === 2) {
    hxNum = sx + tx;
    kyNum = sy + ty;
  } else if (q === 1) {
    hxNum = tx - ty + sx + sy;
    kyNum = tx + ty - sx + sy;
  } else {
    hxNum = tx + ty - sy + sx;
    kyNum = sx + sy - tx + ty;
  }
  // Fraction(num, 2): integral iff num is even.
  if (mod2(hxNum) !== 0 || mod2(kyNum) !== 0) {
    return null;
  }
  return [hxNum / 2, kyNum / 2];
}

export function reconstructRotations(source: Point[], image: Point[]): Json[] {
  const out: Json[] = [];
  const moving: [Point, Point][] = [];
  for (let i = 0; i < source.length; i++) {
    const s = source[i] as Point;
    const t = image[i] as Point;
    if (!deepEqual(s, t)) {
      moving.push([s, t]);
    }
  }
  if (moving.length === 0) {
    return out;
  }
  const [s0, t0] = moving[0] as [Point, Point];
  for (const q of [1, 2, 3]) {
    const centre = solveCentre(s0, t0, q);
    if (centre === null) {
      continue;
    }
    if (verifyRotation(source, image, centre[0], centre[1], q)) {
      out.push(rotationDesc(centre[0], centre[1], q));
    }
  }
  return out;
}

const RECONSTRUCT: Record<string, (source: Point[], image: Point[]) => Json[]> = {
  translation: reconstructTranslations,
  reflection: reconstructReflections,
  rotation: reconstructRotations,
};

export function describeCandidates(kind: string, source: Point[], image: Point[]): Json[] {
  return (RECONSTRUCT[kind] as (s: Point[], i: Point[]) => Json[])(source, image);
}

export function uniqueDescriptor(kind: string, source: Point[], image: Point[]): Json | null {
  if (isUnchanged(source, image)) {
    return null;
  }
  const cands = describeCandidates(kind, source, image);
  return cands.length === 1 ? cands[0] : null;
}
