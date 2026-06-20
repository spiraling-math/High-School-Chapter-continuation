"""Arithmetic sequences generator (oracle reference implementation).

Generator id : gen.sequences.arithmetic
Version      : 1.0.0
Spec         : docs/GENERATOR_SPEC_arithmetic_sequences.md

Implements the generator contract from docs/GENERATOR_STANDARD.md:
  describe, generate, solve, validate, generate_distractors,
  generate_solution, render, serialize.

Design guarantees (all exercised by tests):
  * Determinism: generate(seed, config) is fully seed-determined.
  * Exact arithmetic: integers and fractions.Fraction only; no floats in maths.
  * Independent verification: solve() uses CLOSED FORMS; validate() re-derives
    the answer by ITERATIVE term-by-term construction and requires agreement.
  * Distractors: each maps to a named misconception; none equals the answer;
    all distinct. Multiple-choice is offered for forward tasks; reverse tasks
    are integer free-response.
"""

from __future__ import annotations

import json
import math
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional

from .seeded_random import Mulberry32

GENERATOR_ID = "gen.sequences.arithmetic"
GENERATOR_VERSION = "1.0.0"

FORWARD_TASKS = ("nth_term", "sum_n")
REVERSE_TASKS = ("find_d", "find_n_for_value")
ALL_TASKS = FORWARD_TASKS + REVERSE_TASKS

# Parameter ranges (mirror generator-module.schema.json parameterSpec).
A1_MIN, A1_MAX = -20, 20
D_ABS_MIN, D_ABS_MAX = 1, 12  # |d|, nonzero by construction
N_MIN, N_MAX = 3, 40

OBJECTIVE_BY_TASK = {
    "nth_term": "SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01",
    "find_d": "SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01",
    "find_n_for_value": "SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01",
    "sum_n": "SPI.IBDPAASL.SEQSER.ARITH.SUM_N.01",
}


# --------------------------------------------------------------------------- #
# describe()
# --------------------------------------------------------------------------- #
def describe() -> Dict[str, Any]:
    """Return the generator module descriptor (generator-module.schema.json)."""
    return {
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "title": "Arithmetic Sequences",
        "description": "Arithmetic-sequence items: nth term, sum of first n terms, and reverse tasks.",
        "status": "in-development",
        "supportedObjectives": sorted(set(OBJECTIVE_BY_TASK.values())),
        "supportedQuestionTypes": ["integer", "multiple-choice"],
        "rngAlgorithm": "mulberry32",
        "parameterSpec": {
            "task": {"type": "enum", "enumValues": list(ALL_TASKS)},
            "a1": {"type": "integer", "min": A1_MIN, "max": A1_MAX},
            "d": {"type": "integer", "min": -D_ABS_MAX, "max": D_ABS_MAX, "nonZero": True},
            "n": {"type": "integer", "min": N_MIN, "max": N_MAX},
        },
        "operations": {
            "describe": True, "generate": True, "solve": True, "validate": True,
            "generateDistractors": True, "generateSolution": True, "render": True, "serialize": True,
        },
        "canonicalMethod": "Closed form: u_n = a1 + (n-1)d; S_n = n/2 (2 a1 + (n-1) d).",
        "independentValidationMethod": "Iterative term-by-term construction and comparison.",
        "misconceptionMappings": [
            "MISC.SEQ.OFFBYONE_TERMINDEX", "MISC.SEQ.SIGN_DIFFERENCE",
            "MISC.SEQ.FORGOT_MULTIPLY", "MISC.SERIES.FORGOT_HALF", "MISC.SERIES.CONSTANT_TERMS",
        ],
        "testStrategy": {"seedSweepCount": 10000, "goldenSeeds": [1, 42, 123456789, 2147483647]},
    }


# --------------------------------------------------------------------------- #
# Parameter selection
# --------------------------------------------------------------------------- #
def _choose_params(rng: Mulberry32, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    config = config or {}
    answer_type = config.get("answerType", "integer")

    if "task" in config and config["task"] is not None:
        task = config["task"]
        if task not in ALL_TASKS:
            raise ValueError(f"unknown task: {task}")
        if answer_type == "multiple-choice" and task in REVERSE_TASKS:
            raise ValueError("multiple-choice is only offered for forward tasks")
    else:
        pool = FORWARD_TASKS if answer_type == "multiple-choice" else ALL_TASKS
        task = rng.choice(pool)

    a1 = rng.next_int(A1_MIN, A1_MAX)
    d_mag = rng.next_int(D_ABS_MIN, D_ABS_MAX)
    d = d_mag if rng.next_float() < 0.5 else -d_mag  # nonzero by construction
    n = rng.next_int(N_MIN, N_MAX)
    return {"task": task, "a1": a1, "d": d, "n": n, "answerType": answer_type}


# --------------------------------------------------------------------------- #
# solve()  -- canonical closed-form mathematics
# --------------------------------------------------------------------------- #
def _nth_term(a1: int, d: int, n: int) -> int:
    return a1 + (n - 1) * d


def _sum_n(a1: int, d: int, n: int) -> int:
    s = Fraction(n, 2) * (2 * a1 + (n - 1) * d)
    assert s.denominator == 1, "arithmetic series sum of integers must be integer"
    return int(s)


def solve(params: Dict[str, Any]) -> int:
    """Compute the canonical integer answer for the task via closed forms."""
    task, a1, d, n = params["task"], params["a1"], params["d"], params["n"]
    if task == "nth_term":
        return _nth_term(a1, d, n)
    if task == "sum_n":
        return _sum_n(a1, d, n)
    if task == "find_d":
        # Given a1, the value of the nth term, and n -> recover d.
        value = _nth_term(a1, d, n)
        rec = Fraction(value - a1, n - 1)
        assert rec.denominator == 1
        return int(rec)
    if task == "find_n_for_value":
        # Given a1, d, and a term value -> recover its index n.
        value = _nth_term(a1, d, n)
        rec = Fraction(value - a1, d) + 1
        assert rec.denominator == 1
        return int(rec)
    raise ValueError(f"unknown task: {task}")


def _given_value(params: Dict[str, Any]) -> int:
    """The term value presented to the student for reverse tasks."""
    return _nth_term(params["a1"], params["d"], params["n"])


# --------------------------------------------------------------------------- #
# Distractors (forward tasks only)
# --------------------------------------------------------------------------- #
def generate_distractors(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    task, a1, d, n = params["task"], params["a1"], params["d"], params["n"]
    correct = solve(params)
    candidates: List[Dict[str, Any]] = []

    if task == "nth_term":
        candidates = [
            {"value": a1 + n * d, "misconceptionId": "MISC.SEQ.OFFBYONE_TERMINDEX"},
            {"value": a1 - (n - 1) * d, "misconceptionId": "MISC.SEQ.SIGN_DIFFERENCE"},
            {"value": a1 + (n - 1), "misconceptionId": "MISC.SEQ.FORGOT_MULTIPLY"},
            {"value": a1 + (n + 1) * d, "misconceptionId": "MISC.SEQ.OFFBYONE_TERMINDEX"},
        ]
    elif task == "sum_n":
        u_n = _nth_term(a1, d, n)
        v = Fraction(n, 2) * (2 * a1 + (n + 1) * d)  # off-by-one last term; always integer
        s_np1 = correct + (a1 + n * d)               # summed one extra term (S_{n+1})
        s_nm1 = correct - u_n                        # summed one fewer term (S_{n-1})
        candidates = [
            {"value": n * (2 * a1 + (n - 1) * d), "misconceptionId": "MISC.SERIES.FORGOT_HALF"},
            {"value": n * u_n, "misconceptionId": "MISC.SERIES.CONSTANT_TERMS"},
            {"value": n * a1, "misconceptionId": "MISC.SERIES.CONSTANT_TERMS"},
            {"value": int(v), "misconceptionId": "MISC.SEQ.OFFBYONE_TERMINDEX"},
            {"value": s_np1, "misconceptionId": "MISC.SEQ.OFFBYONE_TERMINDEX"},
            {"value": s_nm1, "misconceptionId": "MISC.SEQ.OFFBYONE_TERMINDEX"},
        ]
    else:
        return []  # reverse tasks are integer free-response

    chosen: List[Dict[str, Any]] = []
    seen = {correct}
    for cand in candidates:
        val = cand["value"]
        if val in seen:
            continue
        seen.add(val)
        chosen.append({"value": int(val), "misconceptionId": cand["misconceptionId"]})
        if len(chosen) == 3:
            break
    return chosen


# --------------------------------------------------------------------------- #
# Solution (structured)
# --------------------------------------------------------------------------- #
def generate_solution(params: Dict[str, Any]) -> Dict[str, Any]:
    task, a1, d, n = params["task"], params["a1"], params["d"], params["n"]
    answer = solve(params)
    if task == "nth_term":
        steps = [
            {"number": 1, "transformation": "State the formula", "ruleOrTheorem": "u_n = u_1 + (n - 1)d"},
            {"number": 2, "transformation": "Substitute",
             "intermediateResult": f"u_{{{n}}} = {a1} + ({n} - 1)\\times({d})", "dependsOn": [1]},
            {"number": 3, "transformation": "Evaluate", "intermediateResult": f"u_{{{n}}} = {answer}",
             "dependsOn": [2], "marks": 1},
        ]
    elif task == "sum_n":
        steps = [
            {"number": 1, "transformation": "State the formula", "ruleOrTheorem": "S_n = n/2 (2u_1 + (n - 1)d)"},
            {"number": 2, "transformation": "Substitute",
             "intermediateResult": f"S_{{{n}}} = \\frac{{{n}}}{{2}}(2\\times{a1} + ({n} - 1)\\times({d}))", "dependsOn": [1]},
            {"number": 3, "transformation": "Evaluate", "intermediateResult": f"S_{{{n}}} = {answer}",
             "dependsOn": [2], "marks": 1},
        ]
    elif task == "find_d":
        value = _given_value(params)
        steps = [
            {"number": 1, "transformation": "State the formula", "ruleOrTheorem": "u_n = u_1 + (n - 1)d"},
            {"number": 2, "transformation": "Rearrange for d",
             "intermediateResult": f"d = \\frac{{u_n - u_1}}{{n - 1}} = \\frac{{{value} - {a1}}}{{{n} - 1}}", "dependsOn": [1]},
            {"number": 3, "transformation": "Evaluate", "intermediateResult": f"d = {answer}", "dependsOn": [2], "marks": 1},
        ]
    else:  # find_n_for_value
        value = _given_value(params)
        steps = [
            {"number": 1, "transformation": "State the formula", "ruleOrTheorem": "u_n = u_1 + (n - 1)d"},
            {"number": 2, "transformation": "Rearrange for n",
             "intermediateResult": f"n = \\frac{{u_n - u_1}}{{d}} + 1 = \\frac{{{value} - {a1}}}{{{d}}} + 1", "dependsOn": [1]},
            {"number": 3, "transformation": "Evaluate", "intermediateResult": f"n = {answer}", "dependsOn": [2], "marks": 1},
        ]
    return {"steps": steps}


# --------------------------------------------------------------------------- #
# Prompt construction
# --------------------------------------------------------------------------- #
def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _prompt_blocks(params: Dict[str, Any]) -> Dict[str, Any]:
    task, a1, d, n = params["task"], params["a1"], params["d"], params["n"]
    if task == "nth_term":
        blocks = [
            {"kind": "text", "text": f"An arithmetic sequence has first term {a1} and common difference {d}."},
            {"kind": "text", "text": f"Find the {_ordinal(n)} term of the sequence."},
        ]
        instruction = "Find"
        spoken = (f"An arithmetic sequence has first term {a1} and common difference {d}. "
                  f"Find the {_ordinal(n)} term.")
    elif task == "sum_n":
        blocks = [
            {"kind": "text", "text": f"An arithmetic sequence has first term {a1} and common difference {d}."},
            {"kind": "text", "text": f"Find the sum of the first {n} terms of the sequence."},
        ]
        instruction = "Find"
        spoken = (f"An arithmetic sequence has first term {a1} and common difference {d}. "
                  f"Find the sum of the first {n} terms.")
    elif task == "find_d":
        value = _given_value(params)
        blocks = [
            {"kind": "text", "text": f"An arithmetic sequence has first term {a1}, and its {_ordinal(n)} term is {value}."},
            {"kind": "text", "text": "Find the common difference of the sequence."},
        ]
        instruction = "Find"
        spoken = (f"An arithmetic sequence has first term {a1}, and its {_ordinal(n)} term is {value}. "
                  f"Find the common difference.")
    else:  # find_n_for_value
        value = _given_value(params)
        blocks = [
            {"kind": "text", "text": f"An arithmetic sequence has first term {a1} and common difference {d}."},
            {"kind": "text", "text": f"One term of the sequence is {value}. Find which term this is."},
        ]
        instruction = "Find"
        spoken = (f"An arithmetic sequence has first term {a1} and common difference {d}. "
                  f"One term is {value}. Find which term it is.")
    return {"instruction": instruction, "blocks": blocks, "_spoken": spoken}


def _given_integers(params: Dict[str, Any]) -> List[int]:
    """Integers that legitimately appear in the prompt (the 'givens')."""
    task, a1, d, n = params["task"], params["a1"], params["d"], params["n"]
    if task == "nth_term":
        return [a1, d, n]
    if task == "sum_n":
        return [a1, d, n]
    if task == "find_d":
        return [a1, n, _given_value(params)]
    if task == "find_n_for_value":
        return [a1, d, _given_value(params)]
    return [a1, d, n]


# --------------------------------------------------------------------------- #
# Difficulty
# --------------------------------------------------------------------------- #
_DIFFICULTY_WEIGHTS = {
    "numericalComplexity": 0.30,
    "reasoningSteps": 0.45,
    "abstraction": 0.25,
}


def _round3(x: float):
    """Portable round-half-up to 3 decimals; collapses integral results to int.

    Implemented identically in TypeScript (Math.floor(x*1000 + 0.5)/1000 with an
    integer collapse) so the serialized difficulty values match byte-for-byte
    across languages. Python's json renders float 1.0 as "1.0" but int 1 as "1";
    JS has no such distinction, so integral results are stored as int on both
    sides.
    """
    v = math.floor(x * 1000 + 0.5) / 1000
    return int(v) if v == int(v) else v


def _difficulty(params: Dict[str, Any]) -> Dict[str, Any]:
    task, a1, d, n = params["task"], params["a1"], params["d"], params["n"]
    magnitude = (abs(a1) / A1_MAX + abs(d) / D_ABS_MAX + n / N_MAX) / 3.0
    numerical = min(1.0, magnitude + (0.1 if d < 0 else 0.0))
    steps = {"nth_term": 0.2, "sum_n": 0.5, "find_d": 0.7, "find_n_for_value": 0.7}[task]
    abstraction = 0.6 if task in REVERSE_TASKS else 0.1
    axes = {"numericalComplexity": _round3(numerical),
            "reasoningSteps": steps, "abstraction": abstraction}
    score = sum(_DIFFICULTY_WEIGHTS[k] * axes[k] for k in _DIFFICULTY_WEIGHTS)
    score = max(0.0, min(1.0, score))
    band = min(5, 1 + int(score * 5))
    return {"overallBand": band, "axes": axes}


# --------------------------------------------------------------------------- #
# generate()
# --------------------------------------------------------------------------- #
def generate(seed: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    rng = Mulberry32(seed)
    params = _choose_params(rng, config)
    answer_type = params.pop("answerType")
    task = params["task"]
    answer_value = solve(params)

    prompt = _prompt_blocks(params)
    spoken = prompt.pop("_spoken")
    solution = generate_solution(params)

    item: Dict[str, Any] = {
        "itemId": f"ITEM-{GENERATOR_ID.replace('.', '-')}-{seed}-{task}",
        "schemaVersion": "1.0.0",
        "objectiveIds": [OBJECTIVE_BY_TASK[task]],
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "seed": seed,
        "params": dict(params),
        "prompt": prompt,
        "answer": {"type": "integer", "canonical": answer_value, "display": str(answer_value)},
        "solution": solution,
        "difficulty": _difficulty(params),
        "calculatorPolicy": "either",
        "accessibility": {"spokenMath": spoken, "nonColorIndicators": True},
        "provenance": {
            "origin": "generated",
            "rightsStatus": "academy-owned",
            "originalityNote": "Original parameterized item; structure abstracted from curriculum.",
        },
        "lifecycle": {"state": "generated"},
    }

    if answer_type == "multiple-choice":
        item["answer"]["type"] = "multiple-choice"
        distractors = generate_distractors(params)
        item["distractors"] = [
            {"id": f"d{i+1}", "value": dd["value"], "display": str(dd["value"]),
             "misconceptionId": dd["misconceptionId"]}
            for i, dd in enumerate(distractors)
        ]
        # Deterministic option order using the SAME rng stream.
        pool = [{"value": answer_value, "correct": True, "misconceptionId": None}]
        pool += [{"value": dd["value"], "correct": False, "misconceptionId": dd["misconceptionId"]}
                 for dd in distractors]
        shuffled = rng.shuffle(pool)
        labels = ["A", "B", "C", "D", "E"]
        item["options"] = [
            {"label": labels[i], "value": o["value"], "display": str(o["value"]),
             "correct": o["correct"], **({"misconceptionId": o["misconceptionId"]} if o["misconceptionId"] else {})}
            for i, o in enumerate(shuffled)
        ]
    return item


# --------------------------------------------------------------------------- #
# validate()  -- INDEPENDENT verification + structural checks
# --------------------------------------------------------------------------- #
def _iterative_terms(a1: int, d: int, count: int) -> List[int]:
    """Independent construction: build the sequence term by term."""
    terms = []
    t = a1
    for _ in range(count):
        terms.append(t)
        t += d
    return terms


def validate(item: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "result": "pass" if ok else "fail", "detail": detail})

    params = item["params"]
    task, a1, d, n = params["task"], params["a1"], params["d"], params["n"]
    answer = item["answer"]["canonical"]

    # 1. params-in-domain
    add("params-in-domain",
        A1_MIN <= a1 <= A1_MAX and 1 <= abs(d) <= D_ABS_MAX and d != 0 and N_MIN <= n <= N_MAX,
        f"a1={a1}, d={d}, n={n}")

    # 2. INDEPENDENT verification by iterative construction
    if task == "find_n_for_value":
        value = _given_value(params)
        # Build terms up to the claimed n and confirm it is the FIRST hit (d != 0 => unique).
        terms = _iterative_terms(a1, d, answer)
        indep_ok = (len(terms) == answer and terms[-1] == value
                    and value not in terms[:-1])
        add("arith-iterative-agreement", indep_ok, f"index {answer} is first with value {value}")
    elif task == "find_d":
        value = _given_value(params)
        terms = _iterative_terms(a1, answer, n)  # rebuild with the found d
        add("arith-iterative-agreement", terms[-1] == value, f"rebuilt nth term {terms[-1]} vs {value}")
    else:
        terms = _iterative_terms(a1, d, n)
        if task == "nth_term":
            add("arith-iterative-agreement", terms[-1] == answer, f"iter {terms[-1]} vs answer {answer}")
        else:  # sum_n
            add("arith-iterative-agreement", sum(terms) == answer, f"iter sum {sum(terms)} vs answer {answer}")

    # 3. answer-solution-agree (final solution step equals the answer)
    last_step = item["solution"]["steps"][-1]["intermediateResult"]
    add("answer-solution-agree", str(answer) in last_step, f"final step '{last_step}'")

    # 4. no-answer-leakage: every integer printed in the prompt is a declared given
    prompt_text = " ".join(b.get("text", "") for b in item["prompt"]["blocks"])
    prompt_ints = [int(x) for x in re.findall(r"-?\d+", prompt_text)]
    givens = set(_given_integers(params))
    add("no-answer-leakage", all(i in givens for i in prompt_ints),
        f"prompt ints {prompt_ints} subset of givens {sorted(givens)}")

    # 5. selected-response checks (only when options present)
    if "options" in item:
        opts = item["options"]
        correct_vals = [o["value"] for o in opts if o["correct"]]
        add("exactly-one-correct", len(correct_vals) == 1 and correct_vals[0] == answer,
            f"correct values {correct_vals}")
        wrong_vals = [o["value"] for o in opts if not o["correct"]]
        add("distractors-unique", len(wrong_vals) == len(set(wrong_vals)), f"{wrong_vals}")
        add("distractor-not-answer", answer not in wrong_vals, f"answer {answer}, wrong {wrong_vals}")
        add("distractor-misconception",
            all(o.get("misconceptionId") for o in opts if not o["correct"]),
            "every distractor maps to a misconception")
        add("min-three-distractors", len(wrong_vals) >= 3, f"{len(wrong_vals)} distractors")

    # 6. accessibility fields present
    add("a11y-fields-present", bool(item.get("accessibility", {}).get("spokenMath")), "spokenMath present")

    status = "pass" if all(c["result"] == "pass" for c in checks) else "fail"
    return {"status": status, "validatorVersion": "1.0.0", "checks": checks}


# --------------------------------------------------------------------------- #
# render() and serialize()
# --------------------------------------------------------------------------- #
def render(item: Dict[str, Any], mode: str = "full") -> str:
    """Render a plain-text view (the oracle renderer; production uses KaTeX/HTML)."""
    lines = [b.get("text", "") for b in item["prompt"]["blocks"]]
    if "options" in item:
        for o in item["options"]:
            lines.append(f"  {o['label']}. {o['display']}")
    if mode == "answer-only":
        return f"Answer: {item['answer']['display']}"
    if mode in ("full", "concise"):
        out = list(lines)
        if mode == "full":
            out.append("")
            out.append("Solution:")
            for s in item["solution"]["steps"]:
                bit = s.get("ruleOrTheorem") or s.get("intermediateResult") or s.get("transformation", "")
                out.append(f"  {s['number']}. {s.get('transformation','')}: {bit}")
        out.append(f"Answer: {item['answer']['display']}")
        return "\n".join(out)
    return "\n".join(lines)


def serialize(item: Dict[str, Any]) -> str:
    """Canonical JSON serialization (stable key order, UTF-8)."""
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
