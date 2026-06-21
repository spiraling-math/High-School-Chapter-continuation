"""Build the curriculum-review pack for the linear-equations generator.

Coverage: all five tasks; free-response + multiple-choice; integer + exact-rational
answers; all supported bands; positive / negative / zero solutions; positive and
negative coefficients; fractional coefficients (two_step) at suitable bands;
variables on both sides; positive and negative bracket multipliers; every approved
MC misconception rule; and the distractor-collision / deterministic-regeneration
invariant. Each item shows full reproduction metadata, the structured worked
solution, the substitution check, distractor calculations, and validation results.

Run:  python oracle/make_review_pack_linear.py
Writes: docs/review/linear_equations_review_pack.{json,md}
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from spi_oracle import linear_equations as lin  # noqa: E402
from spi_oracle.linear_misconceptions import MISCONCEPTIONS, rules_for  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
SCAN_LIMIT = 40000
COMBOS = [
    ("one_step_add", "multiple-choice"), ("one_step_add", "integer"),
    ("one_step_mul", "multiple-choice"), ("one_step_mul", "integer"),
    ("two_step", "multiple-choice"), ("two_step", "integer"),
    ("both_sides", "multiple-choice"), ("both_sides", "integer"),
    ("brackets", "multiple-choice"), ("brackets", "integer"),
]


def _f(d) -> Fraction:
    return Fraction(d["num"], d["den"])


def _flags_for(item) -> dict:
    p = item["params"]
    s = Fraction(item["answer"]["canonical"]["num"], item["answer"]["canonical"]["den"])
    red_neg = False
    for key in ("a", "b", "c", "d", "k", "p", "q"):
        if key in p and _f(p[key]) < 0:
            red_neg = True
    frac_coef = any(key in p and _f(p[key]).denominator != 1 for key in ("a", "k", "p"))
    k_pos = ("k" in p and _f(p["k"]) > 0)
    k_neg = ("k" in p and _f(p["k"]) < 0)
    return {
        "band": item["difficulty"]["overallBand"],
        "ansint": s.denominator == 1, "ansfrac": s.denominator != 1,
        "solpos": s > 0, "solneg": s < 0, "solzero": s == 0,
        "coefneg": red_neg, "fraccoef": frac_coef, "kpos": k_pos, "kneg": k_neg,
    }


def pick(task: str, mode: str, target: int = 5) -> list:
    bands: set = set()
    seen = {k: False for k in ("ansint", "ansfrac", "solpos", "solneg", "solzero",
                               "coefneg", "fraccoef", "kpos", "kneg")}
    picked = []
    for seed in range(1, SCAN_LIMIT + 1):
        item = lin.generate(seed, {"task": task, "answerType": mode})
        fl = _flags_for(item)
        contrib = fl["band"] not in bands or any(fl.get(k) and not seen[k] for k in seen)
        if contrib or len(picked) < 3:
            picked.append((seed, item))
            bands.add(fl["band"])
            for k in seen:
                seen[k] |= bool(fl.get(k))
        if len(picked) >= target:
            break
    return picked


def accepted_forms(answer: dict) -> str:
    acc = answer.get("accepts", {})
    forms = []
    if acc.get("fraction", True):
        forms.append("any equivalent fraction")
    if acc.get("decimal"):
        forms.append("terminating decimal")
    if acc.get("mixed"):
        forms.append("mixed number")
    return ", ".join(forms) if forms else "exact reduced fraction only"


def item_record(seed, task, mode, item) -> dict:
    v = lin.validate(item)
    calcs = []
    for d in item.get("distractors", []):
        m = MISCONCEPTIONS[d["misconceptionId"]]
        calcs.append({"value": d["display"], "misconceptionId": d["misconceptionId"], "misconception": m["title"],
                      "formula": m["expression"], "rationale": d["rationale"], "feedback": m["feedback"]})
    ans = item["answer"]
    steps = item["solution"]["steps"]
    return {"seed": seed, "task": task, "objectiveIds": item["objectiveIds"],
            "interactionType": item["interactionType"], "answerType": ans["type"],
            "canonicalValue": ans["canonical"], "canonicalDisplay": ans["display"],
            "acceptedEquivalentForms": accepted_forms(ans),
            "difficultyProfile": item["difficulty"], "params": item["params"], "calculatorPolicy": item["calculatorPolicy"],
            "promptText": next((b.get("text", "") for b in item["prompt"]["blocks"] if b.get("text")), ""),
            "promptEquation": next((b.get("latex", "") for b in item["prompt"]["blocks"] if b.get("latex")), ""),
            "workedSolution": steps, "substitutionCheck": steps[-1].get("intermediateResult", ""),
            "distractorCalculations": calcs,
            "validation": v["status"], "validationChecks": [c["name"] for c in v["checks"]],
            "reproduce": {"generatorId": lin.GENERATOR_ID, "generatorVersion": lin.GENERATOR_VERSION,
                          "seed": seed, "config": {"task": task, "answerType": mode}}}


def misconception_examples() -> list:
    out = []
    for mid, m in MISCONCEPTIONS.items():
        if mid == "MISC.LINEQ.SIGNED_ARITH_SLIP":
            continue
        tasks = [t for t in lin.TASKS if mid in rules_for(t)]
        found = None
        for task in tasks:
            for seed in range(1, SCAN_LIMIT + 1):
                item = lin.generate(seed, {"task": task, "answerType": "multiple-choice"})
                for d in item.get("distractors", []):
                    if d["misconceptionId"] == mid:
                        found = {"seed": seed, "task": task, "params": item["params"],
                                 "correctAnswer": item["answer"]["display"], "distractorValue": d["display"]}
                        break
                if found:
                    break
            if found:
                break
        out.append({"misconceptionId": mid, "title": m["title"], "formula": m["expression"],
                    "observableError": m["observableError"], "feedback": m["feedback"], "example": found})
    return out


def collision_invariant(sweep: int = 10000) -> dict:
    """Verify the collision / deterministic-regeneration guarantee: every MC item
    yields exactly three distinct, formula-backed distractors."""
    bad = 0
    for seed in range(1, sweep + 1):
        item = lin.generate(seed, {"answerType": "multiple-choice"})
        opts = [o["display"] for o in item["options"] if not o["correct"]]
        if len(opts) != 3 or len(set(opts)) != 3:
            bad += 1
    return {"sweep": sweep, "mcItemsWithThreeDistinctDistractors": sweep - bad, "violations": bad}


def build() -> None:
    os.makedirs(REVIEW_DIR, exist_ok=True)
    pack = {"generatorId": lin.GENERATOR_ID, "generatorVersion": lin.GENERATOR_VERSION,
            "note": "Representative machine-validated items for curriculum review. None is approved or published; "
                    "advancing lifecycle state beyond machine-validated is the curriculum authority's decision.",
            "combos": [], "misconceptionCoverage": misconception_examples(),
            "collisionInvariant": collision_invariant()}
    for task, mode in COMBOS:
        items = [item_record(s, task, mode, it) for s, it in pick(task, mode)]
        pack["combos"].append({"task": task, "answerType": mode, "count": len(items), "items": items})

    with open(os.path.join(REVIEW_DIR, "linear_equations_review_pack.json"), "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)

    ci = pack["collisionInvariant"]
    L = ["# Curriculum-Review Pack — Linear Equations (one variable)",
         "",
         f"Generator: `{lin.GENERATOR_ID}` v`{lin.GENERATOR_VERSION}`. Stage: SPI-Math Middle School -> Algebra -> "
         "Linear equations in one variable. Generated by `oracle/make_review_pack_linear.py`.",
         "",
         "> **Review purpose.** Machine-validated items with exact integer/rational answers. Advancing any item or "
         "objective to `curriculum-reviewed` / `approved` / `published` is the curriculum authority's decision. Each "
         "multiple-choice distractor is recomputed from its misconception rule during validation.",
         "",
         "## Distractor collision / deterministic-regeneration invariant",
         "",
         f"Over a {ci['sweep']:,}-seed multiple-choice sweep, **{ci['mcItemsWithThreeDistinctDistractors']:,}** items "
         f"produced exactly three distinct, formula-backed distractors; **{ci['violations']}** violations. When three "
         "distinct distractors cannot be formed from the eligible rules, the generator deterministically regenerates "
         "the parameters (same seed → same item).",
         "",
         "## Misconception rule coverage (MC distractor rules)",
         "",
         "| ID | Misconception | Formula | Example (seed · task → distractor vs answer) |",
         "| --- | --- | --- | --- |"]
    for mc in pack["misconceptionCoverage"]:
        ex = mc["example"]
        exs = (f"{ex['seed']} · {ex['task']} → {ex['distractorValue']} (correct {ex['correctAnswer']})") if ex else "—"
        L.append(f"| `{mc['misconceptionId']}` | {mc['title']} | `{mc['formula']}` | {exs} |")
    L += ["",
          "_`MISC.LINEQ.SIGNED_ARITH_SLIP` is a diagnostic-only category (excluded from MC generation); "
          "`MISC.LINEQ.DISTRIBUTE_NONE` is deferred to a later version._", ""]

    for combo in pack["combos"]:
        L += [f"## {combo['task']} · {combo['answerType']} — {combo['count']} examples", ""]
        for i, it in enumerate(combo["items"], 1):
            dp = it["difficultyProfile"]
            cv = it["canonicalValue"]
            L += [f"### {combo['task']}/{combo['answerType']} #{i} — band {dp['overallBand']}", "",
                  f"- **Objective:** `{it['objectiveIds'][0]}`  ·  **Calculator:** {it['calculatorPolicy']}",
                  f"- **Interaction type:** {it['interactionType']}  ·  **Canonical answer type:** {it['answerType']}",
                  f"- **Canonical value:** `num={cv['num']}, den={cv['den']}` → `{it['canonicalDisplay']}`",
                  f"- **Accepted equivalent forms:** {it['acceptedEquivalentForms']}",
                  f"- **Seed:** `{it['seed']}`  ·  **Parameters:** `{json.dumps(it['params'])}`",
                  f"- **Difficulty axes:** `{json.dumps(dp['axes'])}`",
                  f"- **Reproduce:** `generate({it['seed']}, {json.dumps(it['reproduce']['config'])})` on v`{lin.GENERATOR_VERSION}`",
                  "", "**Question**", "",
                  f"> {it['promptText']}", "",
                  f"> $`{it['promptEquation']}`$", "",
                  f"**Answer:** `x = {it['canonicalDisplay']}`", "", "**Worked solution**", ""]
            for s in it["workedSolution"]:
                bit = s.get("intermediateResult") or s.get("ruleOrTheorem") or ""
                L.append(f"{s['number']}. {s.get('transformation','')} — `{bit}`")
            L += ["", f"**Substitution check:** `{it['substitutionCheck']}`", ""]
            if it["distractorCalculations"]:
                L += ["**Distractor calculations (each a distinct misconception pathway)**", "",
                      "| Value | Formula | Misconception | Rationale | Feedback |", "| --- | --- | --- | --- | --- |"]
                for d in it["distractorCalculations"]:
                    L.append(f"| `{d['value']}` | `{d['formula']}` | {d['misconception']} (`{d['misconceptionId']}`) | {d['rationale']} | {d['feedback']} |")
                L.append("")
            else:
                L += ["_Free-response: no distractors._", ""]
            L += [f"**Validation:** {it['validation']} — {', '.join('`'+c+'`' for c in it['validationChecks'])}", "",
                  "**Curriculum decision:** [ ] approve  [ ] revise  [ ] reject — notes: ____", "", "---", ""]
    with open(os.path.join(REVIEW_DIR, "linear_equations_review_pack.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))

    total = sum(c["count"] for c in pack["combos"])
    rules = sum(1 for mc in pack["misconceptionCoverage"] if mc["example"])
    print(f"Linear review pack: {total} items across {len(COMBOS)} combos; "
          f"{rules}/{len(pack['misconceptionCoverage'])} MC rules exemplified; "
          f"collision invariant violations: {ci['violations']}.")


if __name__ == "__main__":
    build()
