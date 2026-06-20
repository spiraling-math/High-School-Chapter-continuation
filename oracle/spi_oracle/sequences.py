"""Arithmetic sequences generator (oracle reference implementation).

Generator id : gen.sequences.arithmetic
Version      : 1.0.1
Spec         : docs/GENERATOR_SPEC_arithmetic_sequences.md

Implements the generator contract from docs/GENERATOR_STANDARD.md:
  describe, generate, solve, validate, generate_distractors,
  generate_solution, render, serialize.

v1.0.1 (curriculum-review corrections):
  * Distractors are DISTINCT misconceptions (no repeated misconception in one
    item); values come from the canonical misconception registry. If a clean set
    of three distinct distractors is not available for the drawn parameters, the
    parameters are deterministically regenerated from the same seed stream.
  * Validator independently recomputes every distractor from its misconception
    formula and checks value/rationale/misconception/feedback agreement.
  * "find term index" wording clarified; calculator policy is explicit
    (calculator-not-required).
"""

from __future__ import annotations

import json
import math
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional

from .seeded_random import Mulberry32
from .misconceptions import MISCONCEPTIONS, rules_for

GENERATOR_ID = "gen.sequences.arithmetic"
GENERATOR_VERSION = "1.1.0"

FORWARD_TASKS = ("nth_term", "sum_n")
REVERSE_TASKS = ("find_d", "find_n_for_value")
ALL_TASKS = FORWARD_TASKS + REVERSE_TASKS

A1_MIN, A1_MAX = -20, 20
D_ABS_MIN, D_ABS_MAX = 1, 12
N_MIN, N_MAX = 3, 40
MAX_PARAM_ATTEMPTS = 64

# v1.1.0: dedicated micro-objectives for the reverse tasks (curriculum-approved).
OBJECTIVE_BY_TASK = {
    "nth_term": "SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01",
    "find_d": "SPI.IBDPAASL.SEQSER.ARITH.COMMON_DIFF.01",
    "find_n_for_value": "SPI.IBDPAASL.SEQSER.ARITH.TERM_INDEX.01",
    "sum_n": "SPI.IBDPAASL.SEQSER.ARITH.SUM_N.01",
}

CALCULATOR_POLICY = "calculator-not-required"


# --------------------------------------------------------------------------- #
# describe()
# --------------------------------------------------------------------------- #
def describe() -> Dict[str, Any]:
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
        "independentValidationMethod": "Iterative term-by-term construction; distractors recomputed from misconception formulas.",
        "misconceptionMappings": sorted(MISCONCEPTIONS.keys()),
        "testStrategy": {"seedSweepCount": 10000, "goldenSeeds": [1, 42, 123456789, 2147483647]},
    }


# --------------------------------------------------------------------------- #
# solve()  -- canonical closed-form mathematics
# --------------------------------------------------------------------------- #
def _nth_term(a1: int, d: int, n: int) -> int:
    return a1 + (n - 1) * d


def _sum_n(a1: int, d: int, n: int) -> int:
    s = Fraction(n, 2) * (2 * a1 + (n - 1) * d)
    assert s.denominator == 1
    return int(s)


def solve(params: Dict[str, Any]) -> int:
    task, a1, d, n = params["task"], params["a1"], params["d"], params["n"]
    if task == "nth_term":
        return _nth_term(a1, d, n)
    if task == "sum_n":
        return _sum_n(a1, d, n)
    if task == "find_d":
        value = _nth_term(a1, d, n)
        rec = Fraction(value - a1, n - 1)
        assert rec.denominator == 1
        return int(rec)
    if task == "find_n_for_value":
        value = _nth_term(a1, d, n)
        rec = Fraction(value - a1, d) + 1
        assert rec.denominator == 1
        return int(rec)
    raise ValueError(f"unknown task: {task}")


def _given_value(params: Dict[str, Any]) -> int:
    return _nth_term(params["a1"], params["d"], params["n"])


# --------------------------------------------------------------------------- #
# Distractors — distinct misconceptions from the canonical registry
# --------------------------------------------------------------------------- #
def generate_distractors(params: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """Return three DISTINCT-misconception distractors, or None if the drawn
    parameters cannot yield three (the caller regenerates parameters)."""
    task = params["task"]
    rule_ids = rules_for(task)
    if not rule_ids:
        return []  # reverse tasks: integer free-response, no distractors
    correct = solve(params)
    chosen: List[Dict[str, Any]] = []
    seen = {correct}
    for mid in rule_ids:
        m = MISCONCEPTIONS[mid]
        val = m["formula"](params)
        if val in seen:
            continue
        seen.add(val)
        chosen.append({
            "value": int(val),
            "misconceptionId": mid,
            "rationale": m["observableError"],
        })
        if len(chosen) == 3:
            break
    return chosen if len(chosen) == 3 else None


# --------------------------------------------------------------------------- #
# Structured solution
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
        spoken = (f"An arithmetic sequence has first term {a1} and common difference {d}. "
                  f"Find the {_ordinal(n)} term.")
    elif task == "sum_n":
        blocks = [
            {"kind": "text", "text": f"An arithmetic sequence has first term {a1} and common difference {d}."},
            {"kind": "text", "text": f"Find the sum of the first {n} terms of the sequence."},
        ]
        spoken = (f"An arithmetic sequence has first term {a1} and common difference {d}. "
                  f"Find the sum of the first {n} terms.")
    elif task == "find_d":
        value = _given_value(params)
        blocks = [
            {"kind": "text", "text": f"An arithmetic sequence has first term {a1}, and its {_ordinal(n)} term is {value}."},
            {"kind": "text", "text": "Find the common difference of the sequence."},
        ]
        spoken = (f"An arithmetic sequence has first term {a1}, and its {_ordinal(n)} term is {value}. "
                  f"Find the common difference.")
    else:  # find_n_for_value (clarified wording, single approved template)
        value = _given_value(params)
        blocks = [
            {"kind": "text", "text": f"An arithmetic sequence has first term {a1} and common difference {d}."},
            {"kind": "text", "text": f"The nth term of the sequence is {value}. Find the value of n."},
        ]
        spoken = (f"An arithmetic sequence has first term {a1} and common difference {d}. "
                  f"The nth term of the sequence is {value}. Find the value of n.")
    return {"instruction": "Find", "blocks": blocks, "_spoken": spoken}


def _given_integers(params: Dict[str, Any]) -> List[int]:
    task, a1, d, n = params["task"], params["a1"], params["d"], params["n"]
    if task in ("nth_term", "sum_n"):
        return [a1, d, n]
    if task == "find_d":
        return [a1, n, _given_value(params)]
    return [a1, d, _given_value(params)]  # find_n_for_value


# --------------------------------------------------------------------------- #
# Difficulty
# --------------------------------------------------------------------------- #
_DIFFICULTY_WEIGHTS = {"numericalComplexity": 0.30, "reasoningSteps": 0.45, "abstraction": 0.25}


def _round3(x: float):
    v = math.floor(x * 1000 + 0.5) / 1000
    return int(v) if v == int(v) else v


def _difficulty(params: Dict[str, Any]) -> Dict[str, Any]:
    task, a1, d, n = params["task"], params["a1"], params["d"], params["n"]
    magnitude = (abs(a1) / A1_MAX + abs(d) / D_ABS_MAX + n / N_MAX) / 3.0
    numerical = min(1.0, magnitude + (0.1 if d < 0 else 0.0))
    steps = {"nth_term": 0.2, "sum_n": 0.5, "find_d": 0.7, "find_n_for_value": 0.7}[task]
    abstraction = 0.6 if task in REVERSE_TASKS else 0.1
    axes = {"numericalComplexity": _round3(numerical), "reasoningSteps": steps, "abstraction": abstraction}
    score = sum(_DIFFICULTY_WEIGHTS[k] * axes[k] for k in _DIFFICULTY_WEIGHTS)
    score = max(0.0, min(1.0, score))
    band = min(5, 1 + int(score * 5))
    return {"overallBand": band, "axes": axes}


# --------------------------------------------------------------------------- #
# generate()
# --------------------------------------------------------------------------- #
def _draw_params(rng: Mulberry32, explicit_task, answer_type) -> Dict[str, Any]:
    if explicit_task is not None:
        task = explicit_task
    else:
        pool = FORWARD_TASKS if answer_type == "multiple-choice" else ALL_TASKS
        task = rng.choice(pool)
    a1 = rng.next_int(A1_MIN, A1_MAX)
    d_mag = rng.next_int(D_ABS_MIN, D_ABS_MAX)
    d = d_mag if rng.next_float() < 0.5 else -d_mag
    n = rng.next_int(N_MIN, N_MAX)
    return {"task": task, "a1": a1, "d": d, "n": n}


def generate(seed: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    config = config or {}
    answer_type = config.get("answerType", "integer")
    explicit_task = config.get("task")
    if explicit_task is not None and explicit_task not in ALL_TASKS:
        raise ValueError(f"unknown task: {explicit_task}")
    if answer_type == "multiple-choice" and explicit_task in REVERSE_TASKS:
        raise ValueError("multiple-choice is only offered for forward tasks")

    rng = Mulberry32(seed)
    distractors: Optional[List[Dict[str, Any]]] = None
    params: Dict[str, Any] = {}
    for _ in range(MAX_PARAM_ATTEMPTS):
        params = _draw_params(rng, explicit_task, answer_type)
        if answer_type == "multiple-choice":
            distractors = generate_distractors(params)
            if distractors is None:
                continue  # regenerate parameters: no clean distinct distractor set
        break
    else:
        raise RuntimeError("could not find parameters yielding three distinct distractors")

    task = params["task"]
    answer_value = solve(params)
    prompt = _prompt_blocks(params)
    spoken = prompt.pop("_spoken")

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
        "solution": generate_solution(params),
        "difficulty": _difficulty(params),
        "calculatorPolicy": CALCULATOR_POLICY,
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
        item["distractors"] = [
            {"id": f"d{i+1}", "value": dd["value"], "display": str(dd["value"]),
             "misconceptionId": dd["misconceptionId"], "rationale": dd["rationale"]}
            for i, dd in enumerate(distractors or [])
        ]
        pool = [{"value": answer_value, "correct": True, "misconceptionId": None}]
        pool += [{"value": dd["value"], "correct": False, "misconceptionId": dd["misconceptionId"]}
                 for dd in (distractors or [])]
        shuffled = rng.shuffle(pool)
        labels = ["A", "B", "C", "D", "E"]
        item["options"] = [
            {"label": labels[i], "value": o["value"], "display": str(o["value"]),
             "correct": o["correct"], **({"misconceptionId": o["misconceptionId"]} if o["misconceptionId"] else {})}
            for i, o in enumerate(shuffled)
        ]
    return item


# --------------------------------------------------------------------------- #
# validate()  -- INDEPENDENT verification + semantic distractor agreement
# --------------------------------------------------------------------------- #
def _iterative_terms(a1: int, d: int, count: int) -> List[int]:
    terms, t = [], a1
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

    add("params-in-domain",
        A1_MIN <= a1 <= A1_MAX and 1 <= abs(d) <= D_ABS_MAX and d != 0 and N_MIN <= n <= N_MAX,
        f"a1={a1}, d={d}, n={n}")

    if task == "find_n_for_value":
        value = _given_value(params)
        terms = _iterative_terms(a1, d, answer)
        add("arith-iterative-agreement",
            len(terms) == answer and terms[-1] == value and value not in terms[:-1],
            f"index {answer} is first with value {value}")
    elif task == "find_d":
        value = _given_value(params)
        terms = _iterative_terms(a1, answer, n)
        add("arith-iterative-agreement", terms[-1] == value, f"rebuilt nth term {terms[-1]} vs {value}")
    else:
        terms = _iterative_terms(a1, d, n)
        if task == "nth_term":
            add("arith-iterative-agreement", terms[-1] == answer, f"iter {terms[-1]} vs answer {answer}")
        else:
            add("arith-iterative-agreement", sum(terms) == answer, f"iter sum {sum(terms)} vs answer {answer}")

    last_step = item["solution"]["steps"][-1]["intermediateResult"]
    add("answer-solution-agree", str(answer) in last_step, f"final step '{last_step}'")

    prompt_text = " ".join(b.get("text", "") for b in item["prompt"]["blocks"])
    prompt_ints = [int(x) for x in re.findall(r"-?\d+", prompt_text)]
    givens = set(_given_integers(params))
    add("no-answer-leakage", all(i in givens for i in prompt_ints),
        f"prompt ints {prompt_ints} subset of givens {sorted(givens)}")

    # Selected-response + distractor semantic agreement
    if "distractors" in item:
        ds = item["distractors"]
        mids = [d_.get("misconceptionId") for d_ in ds]
        add("distractors-distinct-misconceptions", len(set(mids)) == len(mids), str(mids))
        add("min-three-distractors", len(ds) >= 3, f"{len(ds)} distractors")
        for d_ in ds:
            mid = d_.get("misconceptionId")
            m = MISCONCEPTIONS.get(mid)
            add("distractor-misconception-known", m is not None, str(mid))
            if m:
                add("distractor-value-matches-rule", int(m["formula"](params)) == d_["value"],
                    f"{mid}: rule {int(m['formula'](params))} vs stored {d_['value']}")
                add("distractor-rationale-matches", d_.get("rationale") == m["observableError"], str(mid))
                add("distractor-feedback-present", bool(m["feedback"]), str(mid))
            add("distractor-not-answer", d_["value"] != answer, f"{d_['value']} vs {answer}")

    if "options" in item:
        correct_vals = [o["value"] for o in item["options"] if o["correct"]]
        add("exactly-one-correct", len(correct_vals) == 1 and correct_vals[0] == answer, f"{correct_vals}")
        wrong = [o["value"] for o in item["options"] if not o["correct"]]
        add("distractors-unique", len(wrong) == len(set(wrong)), f"{wrong}")

    add("a11y-fields-present", bool(item.get("accessibility", {}).get("spokenMath")), "spokenMath present")

    status = "pass" if all(c["result"] == "pass" for c in checks) else "fail"
    return {"status": status, "validatorVersion": "1.1.0", "checks": checks}


# --------------------------------------------------------------------------- #
# render() and serialize()
# --------------------------------------------------------------------------- #
def render(item: Dict[str, Any], mode: str = "full") -> str:
    lines = [b.get("text", "") for b in item["prompt"]["blocks"]]
    if "options" in item:
        for o in item["options"]:
            lines.append(f"  {o['label']}. {o['display']}")
    if mode == "answer-only":
        return f"Answer: {item['answer']['display']}"
    out = list(lines)
    if mode == "full":
        out.append("")
        out.append("Solution:")
        for s in item["solution"]["steps"]:
            bit = s.get("ruleOrTheorem") or s.get("intermediateResult") or s.get("transformation", "")
            out.append(f"  {s['number']}. {s.get('transformation','')}: {bit}")
    out.append(f"Answer: {item['answer']['display']}")
    return "\n".join(out)


def serialize(item: Dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
