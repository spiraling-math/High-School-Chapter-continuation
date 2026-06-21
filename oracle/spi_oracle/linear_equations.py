"""Linear equations (one variable) generator — oracle reference implementation.

Generator id : gen.algebra.linear-equations
Version      : 1.0.0
Spec         : docs/GENERATOR_SPEC_linear_equations_proposal.md (APPROVED w/ revisions)
Stage        : SPI-Math Middle School -> Algebra -> Linear equations in one variable

Approach (Tier A, oracle-first): equations are constructed BACKWARD from a chosen
exact solution; every side is a linear expression a*x + b over exact rationals
(fractions.Fraction) via the minimal LinExpr algebra (no CAS). The validator
re-derives everything INDEPENDENTLY. Mirrors domains/algebra/linear-equations.ts.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional

from .seeded_random import Mulberry32
from .difficulty import round3, band_from_score
from .linexpr import LinExpr, normalize
from .linear_misconceptions import MISCONCEPTIONS, rules_for

GENERATOR_ID = "gen.algebra.linear-equations"
GENERATOR_VERSION = "1.0.0"

TASKS = ("one_step_add", "one_step_mul", "two_step", "both_sides", "brackets")

NZ = [x for x in range(-9, 10) if x != 0]                 # nonzero integers
A_MUL = [x for x in range(-9, 10) if x not in (-1, 0, 1)]  # |a| >= 2
K_POOL = [x for x in range(-6, 7) if x not in (-1, 0, 1)]  # bracket multiplier, |k| >= 2

MAX_NUM, MAX_DEN, MAX_COEF = 10000, 144, 400
MAX_PARAM_ATTEMPTS = 256
CALCULATOR_POLICY = "calculator-not-required"

OBJECTIVE_BY_TASK = {
    "one_step_add": "SPI.MIDDLE.ALG.LINEQ.ONESTEP_ADD.01",
    "one_step_mul": "SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01",
    "two_step": "SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01",
    "both_sides": "SPI.MIDDLE.ALG.LINEQ.BOTHSIDES.01",
    "brackets": "SPI.MIDDLE.ALG.LINEQ.BRACKETS.01",
}
TASK_BANDS = {"one_step_add": (1, 2), "one_step_mul": (1, 2), "two_step": (2, 3),
              "both_sides": (3, 4), "brackets": (3, 5)}


# --------------------------------------------------------------------------- #
def describe() -> Dict[str, Any]:
    return {
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "title": "Linear Equations (one variable)",
        "description": "Solve linear equations in one variable: one-step, two-step, variables on both sides, and one set of brackets.",
        "status": "in-development",
        "supportedObjectives": sorted(set(OBJECTIVE_BY_TASK.values())),
        "supportedQuestionTypes": ["integer", "exact-rational"],
        "rngAlgorithm": "mulberry32",
        "parameterSpec": {
            "task": {"type": "enum", "enumValues": list(TASKS)},
            "a": {"type": "string", "description": "Leading/variable coefficient as num/den (integer, or unit fraction for two_step)."},
            "b": {"type": "integer", "description": "Constant term (where present)."},
            "c": {"type": "integer", "description": "Right-side coefficient/constant (where present)."},
            "d": {"type": "integer", "description": "Right-side constant (both_sides/brackets)."},
            "k": {"type": "integer", "description": "Bracket multiplier (brackets), |k| >= 2."},
            "p": {"type": "integer", "description": "Inner variable coefficient (brackets)."},
            "q": {"type": "integer", "description": "Inner constant (brackets)."},
        },
        "operations": {"describe": True, "generate": True, "solve": True, "validate": True,
                       "generateDistractors": True, "generateSolution": True, "render": True, "serialize": True},
        "canonicalMethod": "Backward construction from a chosen exact solution; reduce P*x+Q=R*x+T and solve x=(T-Q)/(P-R), P!=R.",
        "independentValidationMethod": "Rebuild both sides as LinExpr, normalize to A*x+B=0, require A!=0, re-solve and substitute.",
        "misconceptionMappings": sorted(k for k in MISCONCEPTIONS if k != "MISC.LINEQ.SIGNED_ARITH_SLIP"),
        "testStrategy": {"seedSweepCount": 10000, "goldenSeeds": [1, 42, 123456789, 2147483647]},
    }


# --------------------------------------------------------------------------- #
def _F(d: Dict[str, int]) -> Fraction:
    return Fraction(d["num"], d["den"])


def _J(value) -> Dict[str, int]:
    f = Fraction(value)
    return {"num": f.numerator, "den": f.denominator}


def _disp(x) -> str:
    f = Fraction(x)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def _terminates(den: int) -> bool:
    d = den
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    return d == 1


def _answer_obj(value: Fraction) -> Dict[str, Any]:
    return {
        "type": "integer" if value.denominator == 1 else "exact-rational",
        "canonical": {"num": value.numerator, "den": value.denominator},
        "display": _disp(value),
        "accepts": {"fraction": True, "decimal": _terminates(value.denominator), "mixed": False},
    }


def _reduced(params: Dict[str, Any]) -> Dict[str, Any]:
    task = params["task"]
    if task == "one_step_add":
        return {"P": Fraction(1), "Q": _F(params["b"]), "R": Fraction(0), "T": _F(params["c"]),
                "kMul": None, "innerP": None, "innerQ": None}
    if task == "one_step_mul":
        return {"P": _F(params["a"]), "Q": Fraction(0), "R": Fraction(0), "T": _F(params["c"]),
                "kMul": None, "innerP": None, "innerQ": None}
    if task == "two_step":
        return {"P": _F(params["a"]), "Q": _F(params["b"]), "R": Fraction(0), "T": _F(params["c"]),
                "kMul": None, "innerP": None, "innerQ": None}
    if task == "both_sides":
        return {"P": _F(params["a"]), "Q": _F(params["b"]), "R": _F(params["c"]), "T": _F(params["d"]),
                "kMul": None, "innerP": None, "innerQ": None}
    # brackets: k(p x + q) = c x + d
    k, p, q = _F(params["k"]), _F(params["p"]), _F(params["q"])
    c, d = _F(params["c"]), _F(params["d"])
    return {"P": k * p, "Q": k * q, "R": c, "T": d, "kMul": k, "innerP": p, "innerQ": q}


def solve(params: Dict[str, Any]) -> Fraction:
    red = _reduced(params)
    if red["P"] == red["R"]:
        raise ValueError("equation does not have a unique solution (P == R)")
    return Fraction(red["T"] - red["Q"], red["P"] - red["R"])


def _build_sides(params: Dict[str, Any]):
    """Rebuild (lhs, rhs) as LinExpr directly from params — independent of solve()."""
    task = params["task"]
    if task == "one_step_add":
        return LinExpr.coef(1, _F(params["b"])), LinExpr.coef(0, _F(params["c"]))
    if task == "one_step_mul":
        return LinExpr.coef(_F(params["a"]), 0), LinExpr.coef(0, _F(params["c"]))
    if task == "two_step":
        return LinExpr.coef(_F(params["a"]), _F(params["b"])), LinExpr.coef(0, _F(params["c"]))
    if task == "both_sides":
        return LinExpr.coef(_F(params["a"]), _F(params["b"])), LinExpr.coef(_F(params["c"]), _F(params["d"]))
    # brackets: expand k*(p x + q) via scale
    lhs = LinExpr.coef(_F(params["p"]), _F(params["q"])).scale(_F(params["k"]))
    rhs = LinExpr.coef(_F(params["c"]), _F(params["d"]))
    return lhs, rhs


def _within_caps(x: Fraction) -> bool:
    return abs(x.numerator) <= MAX_NUM and x.denominator <= MAX_DEN


def _coeffs_within_caps(params: Dict[str, Any]) -> bool:
    red = _reduced(params)
    vals = [red["P"], red["Q"], red["R"], red["T"]]
    for key in ("a", "b", "c", "d", "k", "p", "q"):
        if key in params:
            vals.append(_F(params[key]))
    return all(abs(v.numerator) <= MAX_COEF and v.denominator <= MAX_DEN for v in vals)


# --------------------------------------------------------------------------- #
def generate_distractors(params: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    red = _reduced(params)
    correct = solve(params)
    chosen: List[Dict[str, Any]] = []
    seen = {correct}
    for mid in rules_for(params["task"]):
        w = MISCONCEPTIONS[mid]["wrong"](red)
        if w is None:
            continue
        w = Fraction(w)
        if not _within_caps(w) or w in seen:
            continue
        seen.add(w)
        chosen.append({"value": w, "misconceptionId": mid, "rationale": MISCONCEPTIONS[mid]["observableError"]})
        if len(chosen) == 3:
            break
    return chosen if len(chosen) == 3 else None


# --------------------------------------------------------------------------- #
def _coef_term(a: Fraction) -> str:
    if a == 1:
        return "x"
    if a == -1:
        return "-x"
    if a.denominator == 1:
        return f"{a.numerator}x"
    return f"\\frac{{{a.numerator}}}{{{a.denominator}}}x"


def _signed_const(b: Fraction) -> str:
    if b == 0:
        return ""
    return f" + {_disp(b)}" if b > 0 else f" - {_disp(-b)}"


def _side(a: Fraction, b: Fraction) -> str:
    if a == 0:
        return _disp(b)
    return _coef_term(a) + _signed_const(b)


def _eq(aL: Fraction, bL: Fraction, aR: Fraction, bR: Fraction) -> str:
    return f"{_side(aL, bL)} = {_side(aR, bR)}"


def _equation_latex(params: Dict[str, Any]) -> str:
    task = params["task"]
    if task == "brackets":
        k, p, q = _F(params["k"]), _F(params["p"]), _F(params["q"])
        c, d = _F(params["c"]), _F(params["d"])
        inner = _side(p, q)
        left = f"{_disp(k)}({inner})"
        return f"{left} = {_side(c, d)}"
    red = _reduced(params)
    return _eq(red["P"], red["Q"], red["R"], red["T"])


def _prompt_blocks(params: Dict[str, Any]) -> Dict[str, Any]:
    eq = _equation_latex(params)
    blocks = [
        {"kind": "text", "text": "Solve the equation for x."},
        {"kind": "math", "latex": eq},
    ]
    spoken = f"Solve the equation {eq} for x."
    return {"instruction": "Solve", "blocks": blocks, "_spoken": spoken}


# --------------------------------------------------------------------------- #
def generate_solution(params: Dict[str, Any]) -> Dict[str, Any]:
    red = _reduced(params)
    P, Q, R, T = red["P"], red["Q"], red["R"], red["T"]
    s = solve(params)
    sd = _disp(s)
    steps: List[Dict[str, Any]] = []
    n = [0]

    def add(transformation, intermediate=None, rule=None, explanation=None, marks=None, depends=None):
        n[0] += 1
        st: Dict[str, Any] = {"number": n[0], "transformation": transformation}
        if rule is not None:
            st["ruleOrTheorem"] = rule
        if intermediate is not None:
            st["intermediateResult"] = intermediate
        if explanation is not None:
            st["explanation"] = explanation
        if depends is not None:
            st["dependsOn"] = depends
        if marks is not None:
            st["marks"] = marks
        steps.append(st)
        return n[0]

    prev = None
    aL, bL, aR, bR = P, Q, R, T
    if params["task"] == "brackets":
        prev = add("Expand the brackets", _eq(P, Q, R, T),
                   rule=f"Multiply every term inside the bracket by {_disp(red['kMul'])}.")
    # collect variable terms (only when variables appear on both sides)
    if aR != 0:
        new_aL = aL - aR
        if aR > 0:
            tr = f"Subtract {_coef_term(aR)} from both sides"
        else:
            tr = f"Add {_coef_term(-aR)} to both sides"
        prev = add(tr, _eq(new_aL, bL, Fraction(0), bR),
                   explanation="Collect the variable terms on one side.", depends=[prev] if prev else None)
        aL, aR = new_aL, Fraction(0)
    # collect constants
    if bL != 0:
        new_bR = bR - bL
        if bL > 0:
            tr = f"Subtract {_disp(bL)} from both sides"
        else:
            tr = f"Add {_disp(-bL)} to both sides"
        prev = add(tr, _eq(aL, Fraction(0), Fraction(0), new_bR),
                   explanation="Collect the constants on the other side.", depends=[prev] if prev else None)
        bL, bR = Fraction(0), new_bR
    # divide by the coefficient of x
    if aL != 1:
        prev = add(f"Divide both sides by {_disp(aL)}", f"x = {sd}",
                   explanation="Divide by the coefficient of x.", depends=[prev] if prev else None)
    # state the exact solution
    prev = add("State the exact solution", f"x = {sd}", marks=1, depends=[prev] if prev else None)
    # verify by substitution into the original equation
    lhs, rhs = _build_sides(params)
    lv, rv = lhs.eval(s), rhs.eval(s)
    add("Verify by substitution",
        f"Substitute x = {sd}: \\text{{LHS}} = {_disp(lv)} = \\text{{RHS}}, so x = {sd}.",
        explanation="Both sides are equal, confirming the solution.", depends=[prev])
    return {"steps": steps}


# --------------------------------------------------------------------------- #
def _W():
    return {"numericalComplexity": 0.2, "reasoningSteps": 0.3, "algebraicComplexity": 0.35, "representation": 0.15}


def _step_count(task: str) -> int:
    return {"one_step_add": 1, "one_step_mul": 1, "two_step": 2, "both_sides": 3, "brackets": 4}[task]


def _difficulty(params: Dict[str, Any]) -> Dict[str, Any]:
    red = _reduced(params)
    task = params["task"]
    s = solve(params)
    coef_vals = [red["P"], red["Q"], red["R"], red["T"], s]
    mag = max(abs(v.numerator) + (v.denominator - 1) for v in coef_vals)
    numerical = min(1.0, mag / 12.0)
    reasoning = _step_count(task) / 4.0
    frac_coef = any(_F(params[k]).denominator != 1 for k in ("a", "k", "p") if k in params)
    base_alg = {"one_step_add": 0.1, "one_step_mul": 0.2, "two_step": 0.4, "both_sides": 0.65, "brackets": 0.85}[task]
    algebraic = min(1.0, base_alg + (0.1 if frac_coef else 0.0))
    negatives = any(v < 0 for v in (red["P"], red["Q"], red["R"], red["T"]))
    rationy = s.denominator != 1 or frac_coef
    representation = min(1.0, (0.5 if negatives else 0.15) + (0.25 if rationy else 0.0))
    axes = {"numericalComplexity": round3(numerical), "reasoningSteps": round3(reasoning),
            "algebraicComplexity": round3(algebraic), "representation": round3(representation)}
    w = _W()
    derived = band_from_score(sum(w[k] * axes[k] for k in w))
    lo, hi = TASK_BANDS[task]
    band = max(lo, min(hi, derived))
    return {"overallBand": band, "axes": axes}


# --------------------------------------------------------------------------- #
def _draw_params(rng: Mulberry32, explicit_task) -> Dict[str, Any]:
    task = explicit_task if explicit_task is not None else rng.choice(list(TASKS))
    if task == "one_step_add":
        b = rng.choice(NZ)
        m = rng.next_int(-12, 12)          # solution s = m
        c = m + b
        return {"task": task, "b": _J(b), "c": _J(c)}
    if task == "one_step_mul":
        a = rng.choice(A_MUL)
        m = rng.next_int(-9, 9)            # eq a*x = m, s = m/a
        return {"task": task, "a": _J(a), "c": _J(m)}
    if task == "two_step":
        if rng.next_int(0, 4) == 0:
            a = Fraction(1, rng.choice([2, 3, 4]))   # fractional (unit) coefficient
        else:
            a = Fraction(rng.choice(A_MUL))
        m = rng.next_int(-9, 9)
        b = rng.choice(NZ)
        c = m + b                          # s = (c-b)/a = m/a
        return {"task": task, "a": _J(a), "b": _J(b), "c": _J(c)}
    if task == "both_sides":
        a = rng.choice(NZ)
        c = rng.choice(NZ)
        while c == a:
            c = rng.choice(NZ)
        m = rng.next_int(-9, 9)
        b = rng.choice(NZ)
        d = m + b                          # s = (d-b)/(a-c) = m/(a-c)
        return {"task": task, "a": _J(a), "b": _J(b), "c": _J(c), "d": _J(d)}
    # brackets: k(p x + q) = c x + d
    k = rng.choice(K_POOL)
    p = rng.choice(NZ)
    q = rng.choice(NZ)
    c = rng.next_int(-9, 9)
    while k * p == c:
        c = rng.next_int(-9, 9)
    m = rng.next_int(-9, 9)
    d = m + k * q                          # s = (d - k q)/(k p - c) = m/(k p - c)
    return {"task": task, "k": _J(k), "p": _J(p), "q": _J(q), "c": _J(c), "d": _J(d)}


def _guards_ok(params: Dict[str, Any], red: Dict[str, Any]) -> bool:
    task = params["task"]
    P, Q, R, T = red["P"], red["Q"], red["R"], red["T"]
    if P == R:
        return False
    if task == "one_step_add":
        return Q != 0
    if task == "one_step_mul":
        return P != 0 and P != 1
    if task == "two_step":
        return P != 0 and P != 1 and Q != 0
    if task == "both_sides":
        return _F(params["a"]) != 0 and _F(params["c"]) != 0 and _F(params["a"]) != _F(params["c"])
    if task == "brackets":
        k, p, q = _F(params["k"]), _F(params["p"]), _F(params["q"])
        return k != 0 and k != 1 and p != 0 and q != 0 and (k * p) != _F(params["c"])
    return False


def _acceptable(params: Dict[str, Any], answer_type: str) -> Optional[List[Dict[str, Any]]]:
    red = _reduced(params)
    if not _guards_ok(params, red):
        return None
    try:
        s = solve(params)
    except Exception:
        return None
    if not _within_caps(s) or not _coeffs_within_caps(params):
        return None
    if answer_type == "multiple-choice":
        return generate_distractors(params)
    return []


def generate(seed: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    config = config or {}
    answer_type = config.get("answerType", "integer")  # "integer" == free-response selector
    explicit_task = config.get("task")
    if explicit_task is not None and explicit_task not in TASKS:
        raise ValueError(f"unknown task: {explicit_task}")

    rng = Mulberry32(seed)
    params: Dict[str, Any] = {}
    distractors: Optional[List[Dict[str, Any]]] = None
    ok = False
    for _ in range(MAX_PARAM_ATTEMPTS):
        params = _draw_params(rng, explicit_task)
        result = _acceptable(params, answer_type)
        if result is None:
            continue
        distractors = result
        ok = True
        break
    if not ok:
        raise RuntimeError("could not find acceptable linear-equation parameters")

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
        ds = distractors or []
        item["distractors"] = [
            {"id": f"d{i+1}", "value": {"num": d["value"].numerator, "den": d["value"].denominator},
             "display": _disp(d["value"]), "misconceptionId": d["misconceptionId"], "rationale": d["rationale"]}
            for i, d in enumerate(ds)
        ]
        pool = [{"value": ans, "correct": True, "misconceptionId": None}]
        pool += [{"value": d["value"], "correct": False, "misconceptionId": d["misconceptionId"]} for d in ds]
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
    task = params["task"]
    red = _reduced(params)
    canon = item["answer"]["canonical"]
    ans = Fraction(canon["num"], canon["den"])

    add("params-in-domain", _guards_ok(params, red), f"task={task}")

    typ = item["answer"]["type"]
    add("answer-type-consistency",
        (typ == "integer" and canon["den"] == 1) or (typ == "exact-rational" and canon["den"] >= 1),
        f"type={typ}, den={canon['den']}")
    add("interaction-type", item.get("interactionType") in ("free-response", "multiple-choice"),
        str(item.get("interactionType")))

    # Independent: rebuild both sides, normalize to A*x + B = 0, require unique solution.
    lhs, rhs = _build_sides(params)
    A, B = normalize(lhs, rhs)
    add("equation-is-linear-unique", A != 0, f"A={_disp(A) if A != 0 else 0}")
    add("normalized-form-matches", A == red["P"] - red["R"] and B == red["Q"] - red["T"],
        f"A={_disp(A)}, B={_disp(B)}")

    # Independent solve + substitution into the (expanded) original equation.
    if A != 0:
        s2 = Fraction(-B, A)
        add("solution-satisfies-equation", s2 == ans and lhs.eval(ans) == rhs.eval(ans),
            f"resolved {s2} vs {ans}; LHS({ans})={lhs.eval(ans)}, RHS={rhs.eval(ans)}")
    else:
        add("solution-satisfies-equation", False, "A == 0")

    # Every solution step preserves the solution set: re-simulate the canonical
    # operations independently and check the root is invariant at each stage.
    add("steps-preserve-solution", _steps_preserve(red, ans), "root invariant under each operation")

    last_step = item["solution"]["steps"][-1].get("intermediateResult", "")
    add("answer-solution-agree", item["answer"]["display"] in last_step, f"final step '{last_step}'")

    add("no-answer-leakage", not _explicit_reveal(item), "no explicit 'x = answer' reveal in prompt")

    if "distractors" in item:
        ds = item["distractors"]
        mids = [d.get("misconceptionId") for d in ds]
        add("distractors-distinct-misconceptions", len(set(mids)) == len(mids), str(mids))
        add("min-three-distractors", len(ds) >= 3, f"{len(ds)}")
        for d in ds:
            mid = d.get("misconceptionId")
            m = MISCONCEPTIONS.get(mid)
            add("distractor-misconception-known", m is not None, str(mid))
            if m:
                expected = m["wrong"](red)
                stored = Fraction(d["value"]["num"], d["value"]["den"])
                add("distractor-value-matches-rule", expected is not None and Fraction(expected) == stored,
                    f"{mid}: {expected} vs {stored}")
                add("distractor-rationale-matches", d.get("rationale") == m["observableError"], str(mid))
                add("distractor-feedback-present", bool(m["feedback"]), str(mid))
                add("distractor-not-answer", stored != ans, f"{stored} vs {ans}")

    if "options" in item:
        correct = [o for o in item["options"] if o["correct"]]
        add("exactly-one-correct", len(correct) == 1 and correct[0]["display"] == item["answer"]["display"], "")
        wrong = [o["display"] for o in item["options"] if not o["correct"]]
        add("distractors-unique", len(wrong) == len(set(wrong)), str(wrong))

    add("a11y-fields-present", bool(item.get("accessibility", {}).get("spokenMath")), "spokenMath present")
    prov = item.get("provenance", {})
    add("provenance-complete", bool(prov.get("origin") and prov.get("rightsStatus")), "origin + rightsStatus")
    add("version-fields-present", bool(item.get("generatorId") and item.get("generatorVersion")), "id + version")

    status = "pass" if all(c["result"] == "pass" for c in checks) else "fail"
    return {"status": status, "validatorVersion": "1.0.0", "checks": checks}


def _steps_preserve(red: Dict[str, Any], ans: Fraction) -> bool:
    """Re-run the canonical equivalence-preserving operations; the root must be
    constant and equal to ans at every stage."""
    aL, bL, aR, bR = red["P"], red["Q"], red["R"], red["T"]

    def root(aL, bL, aR, bR):
        if aL - aR == 0:
            return None
        return Fraction(bR - bL, aL - aR)

    stages = [(aL, bL, aR, bR)]
    if aR != 0:
        aL2 = aL - aR
        stages.append((aL2, bL, Fraction(0), bR))
        aL, aR = aL2, Fraction(0)
    if bL != 0:
        bR2 = bR - bL
        stages.append((aL, Fraction(0), Fraction(0), bR2))
        bL, bR = Fraction(0), bR2
    # final isolation
    if aL == 0:
        return False
    final = Fraction(bR - bL, aL - aR)
    for (a1, b1, a2, b2) in stages:
        r = root(a1, b1, a2, b2)
        if r is None or r != ans:
            return False
    return final == ans


def _explicit_reveal(item: Dict[str, Any]) -> bool:
    """Leakage = the prompt explicitly states 'x = <answer>'. Coincidental numeric
    equality between a coefficient and the solution is NOT leakage."""
    disp = re.escape(item["answer"]["display"])
    text = " ".join(b.get("text", "") + " " + b.get("latex", "") for b in item["prompt"]["blocks"])
    text += " " + item.get("accessibility", {}).get("spokenMath", "")
    # A standalone 'x = <answer>' reveal: x must not be part of a coefficient term
    # (e.g. '5x = 0' is the equation, not a reveal of the answer).
    return re.search(r"(?<![A-Za-z0-9])x\s*=\s*" + disp + r"(?![\d/])", text) is not None


# --------------------------------------------------------------------------- #
def render(item: Dict[str, Any], mode: str = "full") -> str:
    lines = []
    for b in item["prompt"]["blocks"]:
        lines.append(b.get("text") or b.get("latex") or "")
    if "options" in item:
        for o in item["options"]:
            lines.append(f"  {o['label']}. {o['display']}")
    if mode == "answer-only":
        return f"Answer: x = {item['answer']['display']}"
    out = list(lines)
    if mode == "full":
        out += ["", "Solution:"]
        for s in item["solution"]["steps"]:
            bit = s.get("intermediateResult") or s.get("ruleOrTheorem") or s.get("transformation", "")
            out.append(f"  {s['number']}. {s.get('transformation', '')}: {bit}")
    out.append(f"Answer: x = {item['answer']['display']}")
    return "\n".join(out)


def serialize(item: Dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
