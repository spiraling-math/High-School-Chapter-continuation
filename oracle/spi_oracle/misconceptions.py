"""Canonical arithmetic-sequence misconception registry (oracle).

This is the SINGLE SOURCE OF TRUTH for distractor values and their rationale and
feedback. Each entry provides:
  - formula(params) -> int  : the deterministic incorrect value the misconception
                              produces,
  - expression              : a human-readable formula (uses u_1, u_n, d, S_n),
  - title, description, observableError, feedback.

The generator builds distractors from these formulas; the validator independently
recomputes each distractor's value from the same formula and checks that the
stored value, rationale, misconception, and feedback all agree (semantic
agreement). The TypeScript registry (domains/sequences/misconceptions.ts) mirrors
this file exactly so the two implementations stay byte-for-byte in parity.
"""

from __future__ import annotations

from typing import Any, Callable, Dict


def _u_n(p: Dict[str, Any]) -> int:
    return p["a1"] + (p["n"] - 1) * p["d"]


MISCONCEPTIONS: Dict[str, Dict[str, Any]] = {
    # ---- nth-term misconceptions -------------------------------------------
    "MISC.SEQ.OFFBYONE_TERMINDEX": {
        "formula": (lambda p: p["a1"] + p["n"] * p["d"]),
        "expression": "u_1 + n*d",
        "title": "Off-by-one in term index",
        "description": "Uses n steps of the common difference instead of (n - 1).",
        "observableError": "Answer is exactly one common difference too large.",
        "feedback": "Reaching the nth term takes (n - 1) steps of the common difference, not n.",
    },
    "MISC.SEQ.SIGN_DIFFERENCE": {
        "formula": (lambda p: p["a1"] - (p["n"] - 1) * p["d"]),
        "expression": "u_1 - (n-1)*d",
        "title": "Sign error on the common difference",
        "description": "Subtracts the common difference instead of adding it.",
        "observableError": "Answer reflects the wrong direction of change.",
        "feedback": "Add the common difference (which may be negative); check whether the sequence increases or decreases.",
    },
    "MISC.SEQ.FORGOT_MULTIPLY": {
        "formula": (lambda p: p["a1"] + (p["n"] - 1)),
        "expression": "u_1 + (n-1)",
        "title": "Forgot to multiply by the common difference",
        "description": "Adds the number of steps but omits multiplying by d.",
        "observableError": "Answer adds (n - 1) rather than (n - 1)*d.",
        "feedback": "Each step changes the term by d, so multiply the (n - 1) steps by the common difference.",
    },
    "MISC.SEQ.FORGOT_FIRST_TERM": {
        "formula": (lambda p: (p["n"] - 1) * p["d"]),
        "expression": "(n-1)*d",
        "title": "Omitted the first term",
        "description": "Computes (n - 1)*d but forgets to add the first term u_1.",
        "observableError": "Answer is the change from u_1, not the term value itself.",
        "feedback": "Add the first term u_1 to (n - 1)*d to get the nth term.",
    },
    # ---- series (sum) misconceptions ---------------------------------------
    "MISC.SERIES.FORGOT_HALF": {
        "formula": (lambda p: p["n"] * (2 * p["a1"] + (p["n"] - 1) * p["d"])),
        "expression": "n*(2*u_1 + (n-1)*d)",
        "title": "Omitted the one-half in the sum formula",
        "description": "Uses n*(2u_1 + (n-1)d) without dividing by 2.",
        "observableError": "Sum is exactly twice the correct value.",
        "feedback": "The sum formula has a factor of one half: S_n = (n/2)(2u_1 + (n - 1)d).",
    },
    "MISC.SERIES.CONSTANT_LAST_TERM": {
        "formula": (lambda p: p["n"] * _u_n(p)),
        "expression": "n*u_n  (= n*(u_1 + (n-1)*d))",
        "title": "Treats every term as equal to the last term",
        "description": "Multiplies the number of terms by the last (nth) term.",
        "observableError": "Sum equals n multiplied by the nth term.",
        "feedback": "The terms change by the common difference; do not multiply the number of terms by only the last term.",
    },
    "MISC.SERIES.CONSTANT_FIRST_TERM": {
        "formula": (lambda p: p["n"] * p["a1"]),
        "expression": "n*u_1",
        "title": "Treats every term as equal to the first term",
        "description": "Multiplies the number of terms by the first term.",
        "observableError": "Sum equals n multiplied by the first term.",
        "feedback": "The terms change by the common difference. Do not multiply the number of terms by only the first term.",
    },
}

# Distractor rule order per task. Each id is a DISTINCT error pathway; the
# generator never reuses a misconception within one item, and regenerates the
# parameters if a clean set of three is not available.
NTH_TERM_RULES = [
    "MISC.SEQ.OFFBYONE_TERMINDEX",
    "MISC.SEQ.SIGN_DIFFERENCE",
    "MISC.SEQ.FORGOT_MULTIPLY",
    "MISC.SEQ.FORGOT_FIRST_TERM",
]
SUM_N_RULES = [
    "MISC.SERIES.FORGOT_HALF",
    "MISC.SERIES.CONSTANT_LAST_TERM",
    "MISC.SERIES.CONSTANT_FIRST_TERM",
]


def rules_for(task: str):
    if task == "nth_term":
        return NTH_TERM_RULES
    if task == "sum_n":
        return SUM_N_RULES
    return []
