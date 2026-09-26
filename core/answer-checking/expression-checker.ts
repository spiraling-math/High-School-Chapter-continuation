/**
 * Algebraic-expression answer checker — the `algebraic-expression` answer type.
 *
 * Parses a learner's single-variable expression into an exact `Poly` with an ASCII-anchored finite
 * grammar (a handful of unicode conveniences are normalised first), then compares the canonical
 * coefficient vector exactly. Never floats. Byte-for-byte counterpart of
 * oracle/spi_oracle/expression_checker.py — the two must accept and reject identically (pinned by
 * oracle/golden/functions_checker_corpus.json).
 *
 * Grammar (after normalisation: lower-case, no whitespace, `**`->`^`, unicode superscripts expanded,
 * an optional leading `y=` / `f(x)=` / `f^-1(x)=` / `(fog)(x)=` / `f(g(x))=` prefix stripped):
 *
 *     expr   := term (('+'|'-') term)*
 *     term   := factor (('*' | implicit) factor | '/' constant-factor)*
 *     factor := ['+'|'-'] base ('^' natural)?          // natural may be wrapped in { } or ( )
 *     base   := number | 'x' | '(' expr ')'
 *     number := digits ['.' digits] ['/' digits]       // 'a/b' directly before 'x' or '(' is a coefficient
 *
 * Result codes: correct | unparseable | wrong-variable | not-polynomial | wrong-degree |
 * wrong-coefficients | misconception (with the matched misconceptionId).
 */

import { Rational, rat } from "../exact-math/rational.ts";
import { Poly, type PolyJson, type RatJson } from "../exact-math/polynomial.ts";

export type ExpressionCode =
  | "correct" | "unparseable" | "wrong-variable" | "not-polynomial" | "wrong-degree" | "wrong-coefficients" | "misconception";
export const EXPRESSION_CODES: readonly ExpressionCode[] = [
  "correct", "unparseable", "wrong-variable", "not-polynomial", "wrong-degree", "wrong-coefficients", "misconception",
];
export interface ExpressionResult { code: ExpressionCode; misconceptionId?: string }
export interface ExpressionDiagnostic { misconceptionId: string; coefficients: RatJson[] }

const MAX_INPUT_LENGTH = 200;
const MAX_DEGREE = 6;
const MAX_DIGITS = 12;

const UNICODE: ReadonlyArray<[string, string]> = [
  ["²", "^2"], ["³", "^3"], ["⁰", "^0"], ["¹", "^1"], ["⁴", "^4"],
  ["⁻¹", "^-1"], ["×", "*"], ["·", "*"], ["∙", "*"], ["−", "-"],
  ["–", "-"], ["—", "-"], ["∘", "o"],
];
const PREFIX = /^(\(?[a-z](o[a-z])?\)?(\^\{?-1\}?)?\(x\)|[a-z]\([a-z]\(x\)\)|y)=/;
const DIGITS = "0123456789";
/** The whitespace class stripped before parsing — spelled out so Python and TypeScript agree exactly. */
export const WHITESPACE = new RegExp("[ \\t\\n\\r\\f\\v\\u00a0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000\\ufeff]+", "g");

class Unparseable extends Error {}
class NotPolynomial extends Error {}
class WrongVariable extends Error {}

/** Lower-case, strip whitespace, normalise unicode, drop a leading name prefix; null if too long. */
export function normalizeExpression(raw: string): string | null {
  let s = raw.trim();
  if (s.length > MAX_INPUT_LENGTH) return null;
  for (const [a, b] of UNICODE) s = s.split(a).join(b);
  s = s.replace(WHITESPACE, "").toLowerCase().split("**").join("^");
  const m = PREFIX.exec(s);
  if (m) s = s.slice(m[0].length);
  return s;
}

const isDigit = (ch: string): boolean => ch !== "" && DIGITS.includes(ch);
const isAlpha = (ch: string): boolean => /^[a-z]$/.test(ch);

function capped(p: Poly): Poly {
  if (p.degree() > MAX_DEGREE) throw new Unparseable();
  return p;
}

class Parser {
  private i = 0;
  private readonly s: string;
  constructor(s: string) { this.s = s; }

  get pos(): number { return this.i; }
  peek(): string { return this.i < this.s.length ? this.s[this.i]! : ""; }
  take(): string { const ch = this.peek(); this.i += 1; return ch; }

  // expr := term (('+'|'-') term)*
  expr(): Poly {
    let p = this.term();
    while (this.peek() === "+" || this.peek() === "-") {
      const op = this.take();
      const q = this.term();
      p = op === "+" ? p.add(q) : p.sub(q);
    }
    return p;
  }

  // term := factor (('*' | implicit) factor | '/' constant-factor)*
  term(): Poly {
    let p = this.factor();
    for (;;) {
      const ch = this.peek();
      if (ch === "*") {
        this.take();
        p = capped(p.mul(this.factor()));
      } else if (ch === "/") {
        this.take();
        const q = this.factor();
        if (!q.isConstant()) throw new NotPolynomial();
        if (q.isZero()) throw new Unparseable();
        p = p.scale(rat(1).div(q.c[0]!));
      } else if (ch !== "" && (isDigit(ch) || ch === "x" || ch === "(")) {
        p = capped(p.mul(this.factor()));
      } else {
        return p;
      }
    }
  }

  // factor := ['+'|'-'] base ('^' natural)?
  factor(): Poly {
    const ch = this.peek();
    if (ch === "-") { this.take(); return this.factor().neg(); }
    if (ch === "+") { this.take(); return this.factor(); }
    let p = this.base();
    if (this.peek() === "^") {
      this.take();
      const n = this.natural();
      p = capped(p.pow(n));
    }
    return p;
  }

  natural(): number {
    let wrapped = "";
    if (this.peek() === "{" || this.peek() === "(") wrapped = this.take() === "{" ? "}" : ")";
    if (this.peek() === "-") throw new NotPolynomial(); // negative exponent
    const digits = this.digits();
    if (digits === "") throw new Unparseable();
    if (wrapped) { if (this.take() !== wrapped) throw new Unparseable(); }
    const n = Number(digits);
    if (n > MAX_DEGREE) throw new Unparseable();
    return n;
  }

  private digits(): string {
    let j = this.i;
    while (j < this.s.length && isDigit(this.s[j]!)) j += 1;
    const out = this.s.slice(this.i, j);
    this.i = j;
    return out;
  }

  // base := number | 'x' | '(' expr ')'
  base(): Poly {
    const ch = this.peek();
    if (ch === "(") {
      this.take();
      const p = this.expr();
      if (this.take() !== ")") throw new Unparseable();
      return p;
    }
    if (ch === "x") { this.take(); return Poly.x(); }
    if (isDigit(ch)) return Poly.const(this.number());
    if (isAlpha(ch)) throw new WrongVariable();
    throw new Unparseable();
  }

  number(): Rational {
    const ip = this.digits();
    let fp = "";
    if (this.peek() === ".") {
      this.take();
      fp = this.digits();
      if (fp === "") throw new Unparseable();
    }
    if (ip.length + fp.length > MAX_DIGITS) throw new Unparseable();
    let value = new Rational(Number(ip + fp), 10 ** fp.length);
    // 'a/b' directly followed by 'x' or '(' is a coefficient literal (the coordinate-checker convention).
    if (this.peek() === "/") {
      const j = this.i + 1;
      let k = j;
      while (k < this.s.length && isDigit(this.s[k]!)) k += 1;
      if (k > j && k < this.s.length && (this.s[k] === "x" || this.s[k] === "(")) {
        const den = Number(this.s.slice(j, k));
        if (den === 0 || k - j > MAX_DIGITS) throw new Unparseable();
        this.i = k;
        value = value.div(rat(den));
      }
    }
    return value;
  }
}

/** Parse a learner expression; code is "correct" when the parse succeeded (equivalence judged later). */
export function parseExpression(raw: string): { code: ExpressionCode; poly: Poly | null } {
  const s = normalizeExpression(raw);
  if (s === null || s === "") return { code: "unparseable", poly: null };
  if (s.includes("=")) return { code: "unparseable", poly: null };
  for (const ch of s) {
    if (isAlpha(ch) && ch !== "x") return { code: "wrong-variable", poly: null };
    if (!"0123456789x+-*/^().{}".includes(ch)) return { code: "unparseable", poly: null };
  }
  const parser = new Parser(s);
  try {
    const p = parser.expr();
    if (parser.pos !== s.length) return { code: "unparseable", poly: null };
    return { code: "correct", poly: p };
  } catch (e) {
    if (e instanceof NotPolynomial) return { code: "not-polynomial", poly: null };
    if (e instanceof WrongVariable) return { code: "wrong-variable", poly: null };
    return { code: "unparseable", poly: null };
  }
}

/**
 * Grade a learner input against a canonical polynomial answer. `canonical` is the answer.canonical
 * object ({variable, coefficients}); `diagnostics` lists the wrong forms the item knows about.
 */
export function checkExpression(raw: string, canonical: PolyJson, diagnostics: readonly ExpressionDiagnostic[] = []): ExpressionResult {
  const { code, poly } = parseExpression(raw);
  if (poly === null) return { code };
  const target = Poly.fromJson(canonical);
  if (poly.equals(target)) return { code: "correct" };
  for (const d of diagnostics) {
    if (poly.equals(new Poly(d.coefficients.map((t) => new Rational(t.num, t.den))))) {
      return { code: "misconception", misconceptionId: d.misconceptionId };
    }
  }
  if (poly.degree() !== target.degree()) return { code: "wrong-degree" };
  return { code: "wrong-coefficients" };
}
