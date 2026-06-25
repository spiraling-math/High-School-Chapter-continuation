/**
 * gen.geometry.transformations — exact transformation engine, descriptor model, parser,
 * canonicalizer, formatter, and the single result-code vocabulary (owner F, I, J).
 *
 * Byte-for-byte TypeScript mirror of oracle/spi_oracle/transformations_core.py.
 *
 * EXACTNESS (owner F): every coordinate is an integer; the engine uses only integer add / negate /
 * swap. There is NO runtime trigonometry, floating point, tolerance, or irrational coordinate anywhere.
 */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = any;

export type Point = [number, number];

// --------------------------------------------------------------------------- //
// The ONE result-code vocabulary (owner J). Python + TypeScript share this exact list.
// --------------------------------------------------------------------------- //
export const RESULT_CODES: readonly string[] = [
  "correct",
  "wrong-transformation-type",
  "wrong-translation-vector",
  "wrong-reflection-axis",
  "wrong-rotation-centre",
  "wrong-rotation-amount",
  "ambiguous-description",
  "missing-rotation-centre",
  "missing-translation-vector",
  "unsupported-reflection-line",
  "unsupported-angle",
  "contradictory-description",
  "unparsed-trailing-text",
  "malformed-response",
];

export const QUARTER_DEGREES: Record<number, number> = { 1: 90, 2: 180, 3: 270 };

// --------------------------------------------------------------------------- //
// Exact engine (owner F)
// --------------------------------------------------------------------------- //
export function applyTranslation(p: Point, dx: number, dy: number): Point {
  return [p[0] + dx, p[1] + dy];
}

export function reflectXEqA(p: Point, a: number): Point {
  return [2 * a - p[0], p[1]];
}

export function reflectYEqB(p: Point, b: number): Point {
  return [p[0], 2 * b - p[1]];
}

export function reflectYEqX(p: Point): Point {
  return [p[1], p[0]];
}

export function reflectYEqNegX(p: Point): Point {
  return [-p[1], -p[0]];
}

export function rotateQuarter(p: Point, h: number, k: number, q: number): Point {
  const x = p[0] - h;
  const y = p[1] - k;
  let nx: number;
  let ny: number;
  if (q === 1) {
    nx = -y;
    ny = x;
  } else if (q === 2) {
    nx = -x;
    ny = -y;
  } else if (q === 3) {
    nx = y;
    ny = -x;
  } else {
    throw new Error(`quarterTurnsCCW must be 1, 2, or 3 (got ${q})`);
  }
  return [nx + h, ny + k];
}

export function applyTransform(desc: Json, p: Point): Point {
  const kind = desc.kind;
  if (kind === "translation") {
    const v = desc.vector;
    return applyTranslation(p, v.dx, v.dy);
  }
  if (kind === "reflection") {
    const ax = desc.axis;
    if (ax.kind === "vertical") {
      return reflectXEqA(p, ax.value);
    }
    if (ax.kind === "horizontal") {
      return reflectYEqB(p, ax.value);
    }
    if (ax.kind === "diagonal") {
      return ax.equation === "y=x" ? reflectYEqX(p) : reflectYEqNegX(p);
    }
    throw new Error(`unsupported axis kind ${JSON.stringify(ax.kind)}`);
  }
  if (kind === "rotation") {
    const c = desc.centre;
    return rotateQuarter(p, c.x, c.y, desc.quarterTurnsCCW);
  }
  throw new Error(`unsupported transformation kind ${JSON.stringify(kind)}`);
}

// --------------------------------------------------------------------------- //
// Descriptor constructors + canonicalizer (owner C, I)
// --------------------------------------------------------------------------- //
export function translationDesc(dx: number, dy: number): Json {
  if (dx === 0 && dy === 0) {
    throw new Error("translation vector must be nonzero (owner C)");
  }
  return { kind: "translation", vector: { dx: dx | 0, dy: dy | 0 } };
}

export function reflectionVertical(a: number): Json {
  return { kind: "reflection", axis: { kind: "vertical", value: a | 0 } };
}

export function reflectionHorizontal(b: number): Json {
  return { kind: "reflection", axis: { kind: "horizontal", value: b | 0 } };
}

export function reflectionDiagonal(equation: string): Json {
  if (equation !== "y=x" && equation !== "y=-x") {
    throw new Error("diagonal equation must be 'y=x' or 'y=-x'");
  }
  return { kind: "reflection", axis: { kind: "diagonal", equation } };
}

export function rotationDesc(h: number, k: number, q: number): Json {
  if (q !== 1 && q !== 2 && q !== 3) {
    throw new Error("quarterTurnsCCW must be 1, 2, or 3");
  }
  return { kind: "rotation", centre: { x: h | 0, y: k | 0 }, quarterTurnsCCW: q | 0 };
}

export function canonicalizeDescriptor(desc: Json): Json {
  const kind = desc.kind;
  if (kind === "translation") {
    const v = desc.vector;
    return translationDesc(v.dx, v.dy);
  }
  if (kind === "reflection") {
    const ax = desc.axis;
    if (ax.kind === "vertical") {
      return reflectionVertical(ax.value);
    }
    if (ax.kind === "horizontal") {
      return reflectionHorizontal(ax.value);
    }
    return reflectionDiagonal(ax.equation);
  }
  if (kind === "rotation") {
    const c = desc.centre;
    return rotationDesc(c.x, c.y, desc.quarterTurnsCCW);
  }
  throw new Error(`unsupported kind ${JSON.stringify(kind)}`);
}

/** Structural equality of two canonicalized descriptors (mirror of Python dict ==). */
export function descriptorsEqual(a: Json, b: Json): boolean {
  return deepEqual(canonicalizeDescriptor(a), canonicalizeDescriptor(b));
}

/** Deterministic structural equality used in place of Python's dict/list/tuple ==. */
export function deepEqual(a: Json, b: Json): boolean {
  if (a === b) return true;
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) if (!deepEqual(a[i], b[i])) return false;
    return true;
  }
  if (a && b && typeof a === "object" && typeof b === "object" && !Array.isArray(a) && !Array.isArray(b)) {
    const ka = Object.keys(a);
    const kb = Object.keys(b);
    if (ka.length !== kb.length) return false;
    for (const k of ka) {
      if (!Object.prototype.hasOwnProperty.call(b, k)) return false;
      if (!deepEqual(a[k], b[k])) return false;
    }
    return true;
  }
  return false;
}

// --------------------------------------------------------------------------- //
// Display formatter (owner C, I). ASCII "deg"; the descriptor is the source of truth.
// --------------------------------------------------------------------------- //
export function axisEquation(ax: Json): string {
  if (ax.kind === "vertical") {
    return `x = ${ax.value}`;
  }
  if (ax.kind === "horizontal") {
    return `y = ${ax.value}`;
  }
  return ax.equation === "y=x" ? "y = x" : "y = -x";
}

export function formatDisplay(desc: Json): string {
  const kind = desc.kind;
  if (kind === "translation") {
    const v = desc.vector;
    return `translation by vector (${v.dx}, ${v.dy})`;
  }
  if (kind === "reflection") {
    return `reflection in ${axisEquation(desc.axis)}`;
  }
  if (kind === "rotation") {
    const c = desc.centre;
    const q = desc.quarterTurnsCCW;
    const deg = QUARTER_DEGREES[q];
    const direction = q === 2 ? "" : " anticlockwise";
    return `rotation ${deg} deg${direction} about (${c.x}, ${c.y})`;
  }
  throw new Error(`unsupported kind ${JSON.stringify(kind)}`);
}

export function answerObject(desc: Json): Json {
  const canon = canonicalizeDescriptor(desc);
  return { type: "transformation", canonical: canon, display: formatDisplay(canon) };
}

// --------------------------------------------------------------------------- //
// Anchored parser + canonicalizer (owner I). Finite grammar, NOT free-form NLP.
// --------------------------------------------------------------------------- //
const INT = "[+-]?\\d+";

export function norm(text: string): string {
  let s = text.trim().toLowerCase();
  s = s.replace(/−/g, "-").replace(/–/g, "-").replace(/—/g, "-");
  s = s.replace(/°/g, " deg ");
  s = s.replace(/counterclockwise/g, "anticlockwise").replace(/counter-clockwise/g, "anticlockwise");
  s = s.replace(/anti-clockwise/g, "anticlockwise");
  s = s.replace(/center/g, "centre");
  s = s.replace(/half-turn/g, "half turn");
  s = s.replace(/\bdegrees?\b/g, "deg");
  s = s.replace(/\s+/g, " ").trim();
  return s;
}

function parseVector(s: string): Point | null {
  let m = s.match(new RegExp(`^\\(\\s*(${INT})\\s*,\\s*(${INT})\\s*\\)$`));
  if (m) {
    return [parseInt(m[1] as string, 10), parseInt(m[2] as string, 10)];
  }
  m = s.match(new RegExp(`^\\[\\s*(${INT})\\s*;\\s*(${INT})\\s*\\]$`));
  if (m) {
    return [parseInt(m[1] as string, 10), parseInt(m[2] as string, 10)];
  }
  return null;
}

function parseCentre(sIn: string): Point | null {
  const s = sIn.trim();
  if (s === "the origin" || s === "origin") {
    return [0, 0];
  }
  const m = s.match(new RegExp(`^\\(\\s*(${INT})\\s*,\\s*(${INT})\\s*\\)$`));
  if (m) {
    return [parseInt(m[1] as string, 10), parseInt(m[2] as string, 10)];
  }
  return null;
}

export interface ParseResult {
  descriptor: Json | null;
  code: string | null;
}

export function parseDescriptor(text: string | null | undefined): ParseResult {
  if (text === null || text === undefined || !String(text).trim()) {
    return { descriptor: null, code: "malformed-response" };
  }
  const s = norm(String(text));

  // Contradictory direction (both senses named).
  if (/\bclockwise\b/.test(s) && /\banticlockwise\b/.test(s)) {
    return { descriptor: null, code: "contradictory-description" };
  }

  // --- translation ---
  let m = s.match(/^(?:translation|translate)(?: by)?(?: the column)?(?: vector)?\s*(.*)$/);
  if (m) {
    const rest = (m[1] as string).trim();
    if (!rest) {
      return { descriptor: null, code: "missing-translation-vector" };
    }
    const vec = parseVector(rest);
    if (vec === null) {
      const mv = rest.match(/^(\([^)]*\)|\[[^\]]*\])/);
      if (mv && parseVector(mv[1] as string)) {
        return { descriptor: null, code: "unparsed-trailing-text" };
      }
      return { descriptor: null, code: "missing-translation-vector" };
    }
    if (vec[0] === 0 && vec[1] === 0) {
      return { descriptor: null, code: "contradictory-description" };
    }
    return { descriptor: translationDesc(vec[0], vec[1]), code: null };
  }

  // --- reflection ---
  m = s.match(/^reflection in (?:the )?(.*)$/);
  if (m) {
    const line = (m[1] as string).trim().replace(/\.+$/, "");
    return parseReflectionLine(line);
  }

  // --- rotation / half turn ---
  if (s.startsWith("rotation") || s.startsWith("half turn") || s.startsWith("rotate")) {
    return parseRotation(s);
  }

  return { descriptor: null, code: "malformed-response" };
}

function parseReflectionLine(lineIn: string): ParseResult {
  const line = lineIn.replace(/\s*=\s*/g, "=");
  if (line === "x-axis" || line === "x axis") {
    return { descriptor: reflectionHorizontal(0), code: null };
  }
  if (line === "y-axis" || line === "y axis") {
    return { descriptor: reflectionVertical(0), code: null };
  }
  let m = line.match(new RegExp(`^x=(${INT})$`));
  if (m) {
    return { descriptor: reflectionVertical(parseInt(m[1] as string, 10)), code: null };
  }
  m = line.match(new RegExp(`^y=(${INT})$`));
  if (m) {
    return { descriptor: reflectionHorizontal(parseInt(m[1] as string, 10)), code: null };
  }
  if (line === "y=x") {
    return { descriptor: reflectionDiagonal("y=x"), code: null };
  }
  if (line === "y=-x") {
    return { descriptor: reflectionDiagonal("y=-x"), code: null };
  }
  return { descriptor: null, code: "unsupported-reflection-line" };
}

function parseRotation(s: string): ParseResult {
  const half = s.startsWith("half turn");
  let q: number | null = null;
  if (half) {
    q = 2;
  } else {
    const ma = s.match(new RegExp(`(${INT})\\s*deg`));
    if (ma === null) {
      return { descriptor: null, code: "ambiguous-description" };
    }
    const ang = mod(parseInt(ma[1] as string, 10), 360);
    const cw = /\bclockwise\b/.test(s);
    const acw = /\banticlockwise\b/.test(s);
    if (ang === 180) {
      q = 2;
    } else if (ang === 90) {
      q = cw ? 3 : 1;
    } else if (ang === 270) {
      q = cw ? 1 : 3;
    } else {
      return { descriptor: null, code: "unsupported-angle" };
    }
    if ((ang === 90 || ang === 270) && !cw && !acw) {
      return { descriptor: null, code: "ambiguous-description" };
    }
  }
  const mc = s.match(/about\s+(.*)$/);
  if (mc === null) {
    return { descriptor: null, code: "missing-rotation-centre" };
  }
  const centre = parseCentre((mc[1] as string).trim().replace(/\.+$/, ""));
  if (centre === null) {
    return { descriptor: null, code: "missing-rotation-centre" };
  }
  return { descriptor: rotationDesc(centre[0], centre[1], q as number), code: null };
}

/** Python's % operator (floored, non-negative result for positive modulus). */
export function mod(n: number, m: number): number {
  return ((n % m) + m) % m;
}
