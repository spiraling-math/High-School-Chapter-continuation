"""Geometric sequences generator (oracle reference implementation).

Generator id : gen.sequences.geometric
Version      : 1.1.0  (v1.0.0 preserved unchanged in git history)
Spec         : docs/GENERATOR_SPEC_geometric_sequences_PROPOSAL.md (approved)

v1.1.0 curriculum-review corrections:
  * Separated interaction type (free-response / multiple-choice) from the
    mathematical answer type. answer.type is now 'integer' or 'exact-rational';
    canonical is always a normalized {num, den} (den >= 1). An integer is den=1.
    `answer.accepts` declares equivalent input forms (fraction always; decimal
    when the value terminates; mixed off by default).
  * Sum-to-infinity uses geometric SERIES terminology.
  * find_n worked solutions show the exponent reasoning step by step.
  * Validator adds answer-type/value consistency, find_r real-solution-set
    uniqueness, and term-index uniqueness.

Exact rational arithmetic (fractions.Fraction). Mirrors domains/sequences/geometric.ts.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from .seeded_random import Mulberry32
from .difficulty import round3, band_from_score
from .geometric_misconceptions import MISCONCEPTIONS, rules_for
from .geometric_uniqueness import real_ratio_solutions, term_index_solutions

GENERATOR_ID = "gen.sequences.geometric"
GENERATOR_VERSION = "1.1.0"

FORWARD_MC_TASKS = ("nth_term", "sum_n")
FREE_TASKS = ("find_r", "find_n_for_value", "sum_infinite")
ALL_TASKS = ("nth_term", "sum_n", "find_r", "find_n_for_value", "sum_infinite")

R_FINITE = [(2, 1), (-2, 1), (3, 1), (-3, 1), (1, 2), (-1, 2), (1, 3), (-1, 3), (2, 3), (-2, 3), (3, 2), (-3, 2)]
R_INFINITE = [(1, 2), (-1, 2), (1, 3), (-1, 3), (2, 3), (-2, 3), (1, 4), (-1, 4), (3, 4), (-3, 4)]
U1_CHOICES = [u for u in range(-9, 10) if u != 0]
N_MIN, N_MAX = 2, 6
FIND_R_POSITIONS = [2, 4]  # k-1 odd => unique real (k-1)th root
MAX_NUM, MAX_DEN = 20000, 256
MAX_PARAM_ATTEMPTS = 256

OBJECTIVE_BY_TASK = {
    "nth_term": "SPI.IBDPAASL.SEQSER.GEO.NTH_TERM.01",
    "sum_n": "SPI.IBDPAASL.SEQSER.GEO.SUM_N.01",
    "find_r": "SPI.IBDPAASL.SEQSER.GEO.COMMON_RATIO.01",
    "find_n_for_value": "SPI.IBDPAASL.SEQSER.GEO.TERM_INDEX.01",
    "sum_infinite": "SPI.IBDPAASL.SEQSER.GEO.SUM_INFINITE.01",
}
CALCULATOR_POLICY = "calculator-not-required"


def describe() -> Dict[str, Any]:
    return {
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "title": "Geometric Sequences",
        "description": "Geometric-sequence items: nth term, sum of n terms, common ratio, term index, and sum to infinity.",
        "status": "in-development",
        "supportedObjectives": sorted(set(OBJECTIVE_BY_TASK.values())),
        "supportedQuestionTypes": ["integer", "exact-rational"],
        "rngAlgorithm": "mulberry32",
        "parameterSpec": {
            "task": {"type": "enum", "enumValues": list(ALL_TASKS)},
            "u1": {"type": "integer", "min": -9, "max": 9, "nonZero": True},
            "r": {"type": "string", "description": "Exact common ratio as num/den (r != 0, 1, -1)."},
            "n": {"type": "integer", "min": N_MIN, "max": N_MAX},
            "k": {"type": "enum", "enumValues": FIND_R_POSITIONS, "description": "Position of the given term (find_r)."},
        },
        "operations": {
            "describe": True, "generate": True, "solve": True, "validate": True,
            "generateDistractors": True, "generateSolution": True, "render": True, "serialize": True,
        },
        "canonicalMethod": "Closed forms: u_n = u_1 r^(n-1); S_n = u_1 (r^n - 1)/(r - 1); S_inf = u_1/(1 - r).",
        "independentValidationMethod": "Iterative construction; real-solution-set checks for find_r and term-index uniqueness.",
        "misconceptionMappings": sorted(MISCONCEPTIONS.keys()),
        "testStrategy": {"seedSweepCount": 10000, "goldenSeeds": [1, 42, 123456789, 2147483647]},
    }


# --------------------------------------------------------------------------- #
def _frac(rspec: Tuple[int, int]) -> Fraction:
    return Fraction(rspec[0], rspec[1])


def _r_of(params: Dict[str, Any]) -> Fraction:
    return Fraction(params["r"]["num"], params["r"]["den"])


def _disp(x) -> str:
    if isinstance(x, Fraction):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def _terminates(den: int) -> bool:
    d = den
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    return d == 1


def _answer_obj(value: Fraction) -> Dict[str, Any]:
    num, den = value.numerator, value.denominator
    return {
        "type": "integer" if den == 1 else "exact-rational",
        "canonical": {"num": num, "den": den},
        "display": _disp(value),
        "accepts": {"fraction": True, "decimal": _terminates(den), "mixed": False},
    }


def _iroot(x: int, m: int) -> int:
    if x == 0:
        return 0
    r = round(x ** (1.0 / m))
    for cand in (r - 1, r, r + 1):
        if cand >= 0 and cand ** m == x:
            return cand
    raise ValueError(f"no exact integer {m}th root of {x}")


def _rational_root(q: Fraction, m: int) -> Fraction:
    if q == 0:
        return Fraction(0)
    sign = 1 if q > 0 else -1
    return Fraction(sign * _iroot(abs(q.numerator), m), _iroot(q.denominator, m))


def _within_caps(x: Fraction) -> bool:
    return abs(x.numerator) <= MAX_NUM and x.denominator <= MAX_DEN


# --------------------------------------------------------------------------- #
def _nth(u1: int, r: Fraction, n: int) -> Fraction:
    return u1 * r ** (n - 1)


def _sum_n(u1: int, r: Fraction, n: int) -> Fraction:
    return u1 * (r ** n - 1) / (r - 1)


def solve(params: Dict[str, Any]) -> Fraction:
    task, u1, r = params["task"], params["u1"], _r_of(params)
    if task == "nth_term":
        return _nth(u1, r, params["n"])
    if task == "sum_n":
        return _sum_n(u1, r, params["n"])
    if task == "sum_infinite":
        return Fraction(u1) / (1 - r)
    if task == "find_r":
        k = params["k"]
        value = _nth(u1, r, k)
        return _rational_root(Fraction(value, u1), k - 1)
    if task == "find_n_for_value":
        n = params["n"]
        value = _nth(u1, r, n)
        t, k = Fraction(u1), 1
        while k <= 64:
            if t == value:
                return Fraction(k)
            t *= r
            k += 1
        raise RuntimeError("term index not found")
    raise ValueError(f"unknown task: {task}")


def _given_value(params: Dict[str, Any]) -> Fraction:
    pos = params["k"] if params["task"] == "find_r" else params["n"]
    return _nth(params["u1"], _r_of(params), pos)


# --------------------------------------------------------------------------- #
def generate_distractors(params: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    task = params["task"]
    rule_ids = rules_for(task)
    if not rule_ids:
        return []
    u1, r, n = params["u1"], _r_of(params), params["n"]
    correct = solve(params)
    chosen: List[Dict[str, Any]] = []
    seen = {correct}
    for mid in rule_ids:
        m = MISCONCEPTIONS[mid]
        val = Fraction(m["formula"](u1, r, n))
        if not _within_caps(val) or val in seen:
            continue
        seen.add(val)
        chosen.append({"value": val, "misconceptionId": mid, "rationale": m["observableError"]})
        if len(chosen) == 3:
            break
    return chosen if len(chosen) == 3 else None


# --------------------------------------------------------------------------- #
def generate_solution(params: Dict[str, Any]) -> Dict[str, Any]:
    task, u1 = params["task"], params["u1"]
    r = _r_of(params)
    rd = _disp(r)
    ans = solve(params)
    if task == "nth_term":
        n = params["n"]
        steps = [
            {"number": 1, "transformation": "State the formula", "ruleOrTheorem": "u_n = u_1 r^{n-1}"},
            {"number": 2, "transformation": "Substitute", "intermediateResult": f"u_{{{n}}} = {u1}\\times({rd})^{{{n}-1}}", "dependsOn": [1]},
            {"number": 3, "transformation": "Evaluate", "intermediateResult": f"u_{{{n}}} = {_disp(ans)}", "dependsOn": [2], "marks": 1},
        ]
    elif task == "sum_n":
        n = params["n"]
        steps = [
            {"number": 1, "transformation": "State the formula", "ruleOrTheorem": "S_n = u_1 (r^n - 1)/(r - 1)"},
            {"number": 2, "transformation": "Substitute", "intermediateResult": f"S_{{{n}}} = {u1}\\times\\frac{{({rd})^{{{n}}} - 1}}{{({rd}) - 1}}", "dependsOn": [1]},
            {"number": 3, "transformation": "Evaluate", "intermediateResult": f"S_{{{n}}} = {_disp(ans)}", "dependsOn": [2], "marks": 1},
        ]
    elif task == "sum_infinite":
        steps = [
            {"number": 1, "transformation": "Check convergence", "ruleOrTheorem": "|r| < 1 so the series converges"},
            {"number": 2, "transformation": "State the formula", "ruleOrTheorem": "S_\\infty = u_1/(1 - r)"},
            {"number": 3, "transformation": "Substitute and evaluate", "intermediateResult": f"S_\\infty = \\frac{{{u1}}}{{1 - ({rd})}} = {_disp(ans)}", "dependsOn": [2], "marks": 1},
        ]
    elif task == "find_r":
        k = params["k"]
        value = _given_value(params)
        steps = [
            {"number": 1, "transformation": "State the formula", "ruleOrTheorem": "u_k = u_1 r^{k-1}"},
            {"number": 2, "transformation": "Rearrange for r", "intermediateResult": f"r^{{{k}-1}} = \\frac{{u_k}}{{u_1}} = \\frac{{{_disp(value)}}}{{{u1}}}", "dependsOn": [1]},
            {"number": 3, "transformation": "Take the root", "intermediateResult": f"r = {_disp(ans)}", "dependsOn": [2], "marks": 1},
        ]
    else:  # find_n_for_value — show the exponent reasoning step by step
        n = params["n"]
        value = _given_value(params)
        q = value / u1            # = r^(n-1)
        m = n - 1
        step4: Dict[str, Any] = {"number": 4, "transformation": "Write both sides with base r",
                                 "intermediateResult": f"({rd})^{{n-1}} = ({rd})^{{{m}}}", "dependsOn": [3]}
        if r < 0:
            step4["explanation"] = ("Since the common ratio is negative, the sign of the term confirms the exponent (n - 1) is "
                                    + ("odd" if m % 2 == 1 else "even") + ".")
        steps = [
            {"number": 1, "transformation": "State the formula", "ruleOrTheorem": "u_n = u_1 r^{n-1}"},
            {"number": 2, "transformation": "Substitute", "intermediateResult": f"{u1}\\times({rd})^{{n-1}} = {_disp(value)}", "dependsOn": [1]},
            {"number": 3, "transformation": "Isolate the power", "intermediateResult": f"({rd})^{{n-1}} = {_disp(q)}", "dependsOn": [2]},
            step4,
            {"number": 5, "transformation": "Equate exponents", "intermediateResult": f"n - 1 = {m}", "dependsOn": [4]},
            {"number": 6, "transformation": "Solve for n", "intermediateResult": f"n = {n}", "dependsOn": [5], "marks": 1},
        ]
    return {"steps": steps}


# --------------------------------------------------------------------------- #
def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _prompt_blocks(params: Dict[str, Any]) -> Dict[str, Any]:
    task, u1 = params["task"], params["u1"]
    rd = _disp(_r_of(params))
    if task == "nth_term":
        n = params["n"]
        blocks = [{"kind": "text", "text": f"A geometric sequence has first term {u1} and common ratio {rd}."},
                  {"kind": "text", "text": f"Find the {_ordinal(n)} term of the sequence."}]
        spoken = f"A geometric sequence has first term {u1} and common ratio {rd}. Find the {_ordinal(n)} term."
    elif task == "sum_n":
        n = params["n"]
        blocks = [{"kind": "text", "text": f"A geometric series has first term {u1} and common ratio {rd}."},
                  {"kind": "text", "text": f"Find the sum of the first {n} terms of the series."}]
        spoken = f"A geometric series has first term {u1} and common ratio {rd}. Find the sum of the first {n} terms."
    elif task == "sum_infinite":
        blocks = [{"kind": "text", "text": f"A geometric series has first term {u1} and common ratio {rd}, with |r| < 1."},
                  {"kind": "text", "text": "Find the sum to infinity of the series."}]
        spoken = f"A geometric series has first term {u1} and common ratio {rd}, with absolute value of r less than 1. Find the sum to infinity."
    elif task == "find_r":
        k = params["k"]
        value = _disp(_given_value(params))
        blocks = [{"kind": "text", "text": f"A geometric sequence has first term {u1}, and its {_ordinal(k)} term is {value}."},
                  {"kind": "text", "text": "Find the common ratio of the sequence."}]
        spoken = f"A geometric sequence has first term {u1}, and its {_ordinal(k)} term is {value}. Find the common ratio."
    else:  # find_n_for_value
        value = _disp(_given_value(params))
        blocks = [{"kind": "text", "text": f"A geometric sequence has first term {u1} and common ratio {rd}."},
                  {"kind": "text", "text": f"The nth term of the sequence is {value}. Find the value of n."}]
        spoken = f"A geometric sequence has first term {u1} and common ratio {rd}. The nth term of the sequence is {value}. Find the value of n."
    return {"instruction": "Find", "blocks": blocks, "_spoken": spoken}


def _given_ints(params: Dict[str, Any]) -> set:
    text = " ".join(b.get("text", "") for b in _prompt_blocks(params)["blocks"])
    return set(int(x) for x in re.findall(r"-?\d+", text))


# --------------------------------------------------------------------------- #
_W = {"numericalComplexity": 0.25, "reasoningSteps": 0.4, "abstraction": 0.2, "exactVsApproximate": 0.15}


def _difficulty(params: Dict[str, Any]) -> Dict[str, Any]:
    task, u1 = params["task"], params["u1"]
    r = _r_of(params)
    frac_ratio = r.denominator != 1
    mag = (abs(u1) / 9 + (abs(r.numerator) + r.denominator) / 7 + params.get("n", params.get("k", 3)) / N_MAX) / 3.0
    numerical = min(1.0, mag)
    steps = {"nth_term": 0.25, "sum_n": 0.5, "find_r": 0.7, "find_n_for_value": 0.7, "sum_infinite": 0.6}[task]
    abstraction = 0.7 if task == "sum_infinite" else (0.5 if task in ("find_r", "find_n_for_value") else 0.15)
    exact = 0.7 if frac_ratio else 0.1
    axes = {"numericalComplexity": round3(numerical), "reasoningSteps": steps, "abstraction": abstraction, "exactVsApproximate": exact}
    band = band_from_score(sum(_W[k] * axes[k] for k in _W))
    return {"overallBand": band, "axes": axes}


# --------------------------------------------------------------------------- #
def _draw_params(rng: Mulberry32, explicit_task, answer_type) -> Dict[str, Any]:
    if explicit_task is not None:
        task = explicit_task
    else:
        pool = FORWARD_MC_TASKS if answer_type == "multiple-choice" else ALL_TASKS
        task = rng.choice(pool)
    u1 = rng.choice(U1_CHOICES)
    rspec = rng.choice(R_INFINITE if task == "sum_infinite" else R_FINITE)
    params: Dict[str, Any] = {"task": task, "u1": u1, "r": {"num": rspec[0], "den": rspec[1]}}
    if task == "find_r":
        params["k"] = rng.choice(FIND_R_POSITIONS)
    elif task != "sum_infinite":
        params["n"] = rng.next_int(N_MIN, N_MAX)
    return params


def _acceptable(params: Dict[str, Any], answer_type: str) -> Optional[List[Dict[str, Any]]]:
    try:
        ans = solve(params)
    except Exception:
        return None
    if not _within_caps(ans):
        return None
    if params["task"] in ("find_r", "find_n_for_value") and not _within_caps(_given_value(params)):
        return None
    if answer_type == "multiple-choice":
        return generate_distractors(params)
    return []


def generate(seed: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    config = config or {}
    answer_type = config.get("answerType", "integer")  # interaction selector: "integer" == free-response
    explicit_task = config.get("task")
    if explicit_task is not None and explicit_task not in ALL_TASKS:
        raise ValueError(f"unknown task: {explicit_task}")
    if answer_type == "multiple-choice" and explicit_task is not None and explicit_task not in FORWARD_MC_TASKS:
        raise ValueError("multiple-choice is only offered for nth_term and sum_n")

    rng = Mulberry32(seed)
    params: Dict[str, Any] = {}
    distractors: Optional[List[Dict[str, Any]]] = None
    ok = False
    for _ in range(MAX_PARAM_ATTEMPTS):
        params = _draw_params(rng, explicit_task, answer_type)
        result = _acceptable(params, answer_type)
        if result is None:
            continue
        distractors = result
        ok = True
        break
    if not ok:
        raise RuntimeError("could not find acceptable geometric parameters")

    task = params["task"]
    ans = solve(params)
    prompt = _prompt_blocks(params)
    spoken = prompt.pop("_spoken")
    interaction = "multiple-choice" if answer_type == "multiple-choice" else "free-response"

    item: Dict[str, Any] = {
        "itemId": f"ITEM-{GENERATOR_ID.replace('.', '-')}-{seed}-{task}",
        "schemaVersion": "1.0.0",
        "objectiveIds": [OBJECTIVE_BY_TASK[task]],
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "seed": seed,
        "params": dict(params),
        "interactionType": interaction,
        "prompt": prompt,
        "answer": _answer_obj(ans),
        "solution": generate_solution(params),
        "difficulty": _difficulty(params),
        "calculatorPolicy": CALCULATOR_POLICY,
        "accessibility": {"spokenMath": spoken, "nonColorIndicators": True},
        "provenance": {"origin": "generated", "rightsStatus": "academy-owned",
                       "originalityNote": "Original parameterized item; structure abstracted from curriculum."},
        "lifecycle": {"state": "generated"},
    }

    if answer_type == "multiple-choice":
        item["distractors"] = [
            {"id": f"d{i+1}", "value": {"num": dd["value"].numerator, "den": dd["value"].denominator},
             "display": _disp(dd["value"]), "misconceptionId": dd["misconceptionId"], "rationale": dd["rationale"]}
            for i, dd in enumerate(distractors or [])
        ]
        pool = [{"value": ans, "correct": True, "misconceptionId": None}]
        pool += [{"value": dd["value"], "correct": False, "misconceptionId": dd["misconceptionId"]} for dd in (distractors or [])]
        shuffled = rng.shuffle(pool)
        labels = ["A", "B", "C", "D", "E"]
        item["options"] = [
            {"label": labels[i], "value": {"num": o["value"].numerator, "den": o["value"].denominator},
             "display": _disp(o["value"]), "correct": o["correct"],
             **({"misconceptionId": o["misconceptionId"]} if o["misconceptionId"] else {})}
            for i, o in enumerate(shuffled)
        ]
    return item


# --------------------------------------------------------------------------- #
def validate(item: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "result": "pass" if ok else "fail", "detail": detail})

    params = item["params"]
    task, u1 = params["task"], params["u1"]
    r = _r_of(params)
    canon = item["answer"]["canonical"]
    ans = Fraction(canon["num"], canon["den"])

    add("params-in-domain",
        u1 != 0 and -9 <= u1 <= 9 and r != 0 and r != 1 and r != -1 and item["params"]["r"]["den"] >= 1,
        f"u1={u1}, r={_disp(r)}")

    # answer-type / value consistency
    typ = item["answer"]["type"]
    add("answer-type-consistency",
        (typ == "integer" and canon["den"] == 1) or (typ == "exact-rational" and canon["den"] >= 1),
        f"type={typ}, den={canon['den']}")
    add("interaction-type", item.get("interactionType") in ("free-response", "multiple-choice"), str(item.get("interactionType")))

    # Independent verification by iterative construction.
    if task == "nth_term":
        t = Fraction(u1)
        for _ in range(params["n"] - 1):
            t *= r
        add("geo-iterative-agreement", t == ans, f"iter {t} vs {ans}")
    elif task == "sum_n":
        t, s = Fraction(u1), Fraction(0)
        for _ in range(params["n"]):
            s += t
            t *= r
        add("geo-iterative-agreement", s == ans, f"iter sum {s} vs {ans}")
    elif task == "sum_infinite":
        add("geo-iterative-agreement", abs(r) < 1 and ans * (1 - r) == u1, "S_inf*(1-r) == u1; |r|<1")
    elif task == "find_r":
        value = _given_value(params)
        t = Fraction(u1)
        for _ in range(params["k"] - 1):
            t *= ans
        add("geo-iterative-agreement", t == value, f"rebuilt term {t} vs {value}")
        sols = real_ratio_solutions(u1, value, params["k"])
        add("find_r-unique-real-ratio", len(sols) == 1 and sols[0] == ans, f"real solutions {[_disp(s) for s in sols]}")
    else:  # find_n_for_value
        n_ans = canon["num"]
        value = _given_value(params)
        terms = []
        t = Fraction(u1)
        for _ in range(n_ans):
            terms.append(t)
            t *= r
        add("geo-iterative-agreement", len(terms) == n_ans and terms[-1] == value, f"term {terms[-1] if terms else None} vs {value}")
        idx = term_index_solutions(u1, r, value)
        add("term-index-unique", idx == [n_ans], f"indices {idx}")

    last_step = item["solution"]["steps"][-1].get("intermediateResult", "")
    add("answer-solution-agree", item["answer"]["display"] in last_step, f"final step '{last_step}'")

    prompt_text = " ".join(b.get("text", "") for b in item["prompt"]["blocks"])
    prompt_ints = [int(x) for x in re.findall(r"-?\d+", prompt_text)]
    add("no-answer-leakage", all(i in _given_ints(params) for i in prompt_ints), f"prompt ints {prompt_ints}")

    if "distractors" in item:
        ds = item["distractors"]
        mids = [d.get("misconceptionId") for d in ds]
        add("distractors-distinct-misconceptions", len(set(mids)) == len(mids), str(mids))
        add("min-three-distractors", len(ds) >= 3, f"{len(ds)}")
        u1v, rv, nv = params["u1"], r, params["n"]
        for d in ds:
            mid = d.get("misconceptionId")
            m = MISCONCEPTIONS.get(mid)
            add("distractor-misconception-known", m is not None, str(mid))
            if m:
                expected = Fraction(m["formula"](u1v, rv, nv))
                stored = Fraction(d["value"]["num"], d["value"]["den"])
                add("distractor-value-matches-rule", expected == stored, f"{mid}: {expected} vs {stored}")
                add("distractor-rationale-matches", d.get("rationale") == m["observableError"], str(mid))
                add("distractor-feedback-present", bool(m["feedback"]), str(mid))

    if "options" in item:
        correct = [o for o in item["options"] if o["correct"]]
        add("exactly-one-correct", len(correct) == 1 and correct[0]["display"] == item["answer"]["display"], "")
        wrong = [o["display"] for o in item["options"] if not o["correct"]]
        add("distractors-unique", len(wrong) == len(set(wrong)), str(wrong))

    add("a11y-fields-present", bool(item.get("accessibility", {}).get("spokenMath")), "spokenMath present")

    status = "pass" if all(c["result"] == "pass" for c in checks) else "fail"
    return {"status": status, "validatorVersion": "1.1.0", "checks": checks}


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
        out += ["", "Solution:"]
        for s in item["solution"]["steps"]:
            bit = s.get("ruleOrTheorem") or s.get("intermediateResult") or s.get("transformation", "")
            out.append(f"  {s['number']}. {s.get('transformation','')}: {bit}")
    out.append(f"Answer: {item['answer']['display']}")
    return "\n".join(out)


def serialize(item: Dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
