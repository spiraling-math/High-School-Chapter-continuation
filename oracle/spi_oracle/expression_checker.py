"""Algebraic-expression answer checker (oracle reference) — the `algebraic-expression` answer type.

Parses a learner's single-variable expression into an exact ``Poly`` with an ASCII-anchored finite
grammar (a handful of unicode conveniences are normalised first), then compares the canonical
coefficient vector exactly. Never floats. Byte-for-byte counterpart of
core/answer-checking/expression-checker.ts — the two must accept and reject identically (pinned by
oracle/golden/functions_checker_corpus.json).

Grammar (after normalisation: lower-case, no whitespace, ``**``->``^``, unicode superscripts
expanded, an optional leading ``y=`` / ``f(x)=`` / ``f^-1(x)=`` / ``(fog)(x)=`` / ``f(g(x))=`` prefix
stripped):

    expr   := term (('+'|'-') term)*
    term   := factor (('*' | implicit) factor | '/' constant-factor)*
    factor := ['+'|'-'] base ('^' natural)?          # natural may be wrapped in { } or ( )
    base   := number | 'x' | '(' expr ')'
    number := digits ['.' digits] ['/' digits]       # 'a/b' directly before 'x' or '(' is a coefficient

Result codes: correct | unparseable | wrong-variable | not-polynomial | wrong-degree |
wrong-coefficients | misconception (with the matched misconceptionId).
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Tuple

from polynomial import Poly

CODES = ("correct", "unparseable", "wrong-variable", "not-polynomial", "wrong-degree", "wrong-coefficients", "misconception")
MAX_INPUT_LENGTH = 200
MAX_DEGREE = 6
MAX_DIGITS = 12

_UNICODE = (
    ("²", "^2"), ("³", "^3"), ("⁰", "^0"), ("¹", "^1"), ("⁴", "^4"),
    ("⁻¹", "^-1"), ("×", "*"), ("·", "*"), ("∙", "*"), ("−", "-"),
    ("–", "-"), ("—", "-"), ("∘", "o"),
)
_PREFIX = re.compile(r"^(\(?[a-z](o[a-z])?\)?(\^\{?-1\}?)?\(x\)|[a-z]\([a-z]\(x\)\)|y)=", re.ASCII)
# The whitespace class stripped before parsing — spelled out so Python and TypeScript agree exactly.
WHITESPACE = re.compile("[ \t\n\r\f\v   -     　﻿]+")
_ASCII_LETTERS = "abcdefghijklmnopqrstuvwxyz"


class _Unparseable(Exception):
    pass


class _NotPolynomial(Exception):
    pass


class _WrongVariable(Exception):
    pass


def normalize_expression(raw: str) -> Optional[str]:
    """Lower-case, strip whitespace, normalise unicode, drop a leading name prefix; None if too long."""
    s = raw.strip()
    if len(s) > MAX_INPUT_LENGTH:
        return None
    for a, b in _UNICODE:
        s = s.replace(a, b)
    s = WHITESPACE.sub("", s).lower().replace("**", "^")
    m = _PREFIX.match(s)
    if m:
        s = s[m.end():]
    return s


class _Parser:
    def __init__(self, s: str) -> None:
        self.s = s
        self.i = 0

    def peek(self) -> str:
        return self.s[self.i] if self.i < len(self.s) else ""

    def take(self) -> str:
        ch = self.peek()
        self.i += 1
        return ch

    # expr := term (('+'|'-') term)*
    def expr(self) -> Poly:
        p = self.term()
        while self.peek() in ("+", "-") and self.peek() != "":
            op = self.take()
            q = self.term()
            p = p.add(q) if op == "+" else p.sub(q)
        return p

    # term := factor (('*' | implicit) factor | '/' constant-factor)*
    def term(self) -> Poly:
        p = self.factor()
        while True:
            ch = self.peek()
            if ch == "*":
                self.take()
                p = _capped(p.mul(self.factor()))
            elif ch == "/":
                self.take()
                q = self.factor()
                if not q.is_constant():
                    raise _NotPolynomial()
                if q.is_zero():
                    raise _Unparseable()
                p = p.scale(Fraction(1) / q.c[0])
            elif ch != "" and (ch.isdigit() or ch == "x" or ch == "("):
                p = _capped(p.mul(self.factor()))
            else:
                return p

    # factor := ['+'|'-'] base ('^' natural)?
    def factor(self) -> Poly:
        ch = self.peek()
        if ch == "-":
            self.take()
            return self.factor().neg()
        if ch == "+":
            self.take()
            return self.factor()
        p = self.base()
        if self.peek() == "^":
            self.take()
            n = self.natural()
            p = _capped(p.pow(n))
        return p

    def natural(self) -> int:
        wrapped = ""
        if self.peek() in ("{", "("):
            wrapped = "}" if self.take() == "{" else ")"
        if self.peek() == "-":
            raise _NotPolynomial()  # negative exponent
        digits = self._digits()
        if digits == "":
            raise _Unparseable()
        if wrapped:
            if self.take() != wrapped:
                raise _Unparseable()
        n = int(digits)
        if n > MAX_DEGREE:
            raise _Unparseable()
        return n

    def _digits(self) -> str:
        j = self.i
        while j < len(self.s) and self.s[j] in "0123456789":  # ASCII digits only (never str.isdigit)
            j += 1
        out = self.s[self.i:j]
        self.i = j
        return out

    # base := number | 'x' | '(' expr ')'
    def base(self) -> Poly:
        ch = self.peek()
        if ch == "(":
            self.take()
            p = self.expr()
            if self.take() != ")":
                raise _Unparseable()
            return p
        if ch == "x":
            self.take()
            return Poly.x()
        if ch != "" and ch in "0123456789":
            return Poly.const(self.number())
        if ch != "" and ch in _ASCII_LETTERS:
            raise _WrongVariable()
        raise _Unparseable()

    def number(self) -> Fraction:
        ip = self._digits()
        fp = ""
        if self.peek() == ".":
            self.take()
            fp = self._digits()
            if fp == "":
                raise _Unparseable()
        if len(ip) + len(fp) > MAX_DIGITS:
            raise _Unparseable()
        value = Fraction(int(ip + fp), 10 ** len(fp))
        # 'a/b' directly followed by 'x' or '(' is a coefficient literal (the coordinate-checker convention).
        if self.peek() == "/":
            j = self.i + 1
            k = j
            while k < len(self.s) and self.s[k] in "0123456789":
                k += 1
            if k > j and k < len(self.s) and self.s[k] in ("x", "("):
                den = int(self.s[j:k])
                if den == 0 or k - j > MAX_DIGITS:
                    raise _Unparseable()
                self.i = k
                value = value / den
        return value


def _capped(p: Poly) -> Poly:
    if p.degree() > MAX_DEGREE:
        raise _Unparseable()
    return p


def parse_expression(raw: str) -> Tuple[str, Optional[Poly]]:
    """Return (code, Poly) — code is 'correct' when the parse succeeded (equivalence is judged later)."""
    s = normalize_expression(raw)
    if s is None or s == "":
        return ("unparseable", None)
    if "=" in s:
        return ("unparseable", None)
    for ch in s:
        if ch in _ASCII_LETTERS and ch != "x":
            return ("wrong-variable", None)
        if not (ch in "0123456789x+-*/^().{}"):
            return ("unparseable", None)
    parser = _Parser(s)
    try:
        p = parser.expr()
        if parser.i != len(s):
            return ("unparseable", None)
        return ("correct", p)
    except _NotPolynomial:
        return ("not-polynomial", None)
    except _WrongVariable:
        return ("wrong-variable", None)
    except (_Unparseable, RecursionError, ValueError, ZeroDivisionError):
        return ("unparseable", None)


def check_expression(raw: str, canonical: Dict[str, Any], diagnostics: Sequence[Dict[str, Any]] = ()) -> Dict[str, Any]:
    """Grade a learner input against a canonical polynomial answer.

    ``canonical`` is the answer.canonical object ({variable, coefficients}); ``diagnostics`` is an
    optional list of {misconceptionId, coefficients} wrong forms the item knows about.
    """
    code, p = parse_expression(raw)
    if p is None:
        return {"code": code}
    target = Poly.from_json(canonical)
    if p.equals(target):
        return {"code": "correct"}
    for d in diagnostics:
        if p.equals(Poly([Fraction(t["num"], t["den"]) for t in d["coefficients"]])):
            return {"code": "misconception", "misconceptionId": d["misconceptionId"]}
    if p.degree() != target.degree():
        return {"code": "wrong-degree"}
    return {"code": "wrong-coefficients"}


def coefficients_of(p: Poly) -> List[Dict[str, int]]:
    return [{"num": v.numerator, "den": v.denominator} for v in p.c]
