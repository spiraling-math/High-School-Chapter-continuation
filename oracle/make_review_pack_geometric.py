"""Build the curriculum-review pack for the geometric-sequences generator.

Coverage: >= 3 examples per supported (task, answer type), integer and fractional
ratios, positive and negative ratios and first terms, |r| < 1 and |r| > 1, the
positions/term-counts that occur, every approved misconception rule, and full
reproducibility metadata with distractor calculations.

Run:  python oracle/make_review_pack_geometric.py
Writes: docs/review/geometric_sequences_review_pack.{json,md}
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from spi_oracle import geometric as geo  # noqa: E402
from spi_oracle.geometric_misconceptions import MISCONCEPTIONS  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
SCAN_LIMIT = 60000
COMBOS = [
    ("nth_term", "multiple-choice"), ("nth_term", "integer"),
    ("sum_n", "multiple-choice"), ("sum_n", "integer"),
    ("find_r", "integer"), ("find_n_for_value", "integer"), ("sum_infinite", "integer"),
]


def rdisp(rspec) -> str:
    return str(rspec["num"]) if rspec["den"] == 1 else f"{rspec['num']}/{rspec['den']}"


def pick(task: str, mode: str, target: int = 8) -> list:
    bands, flags = set(), {"rpos": False, "rneg": False, "rfrac": False, "rint": False,
                           "u1pos": False, "u1neg": False, "rlt1": False, "rgt1": False,
                           "ansint": False, "ansfrac": False}
    picked = []
    for seed in range(1, SCAN_LIMIT + 1):
        item = geo.generate(seed, {"task": task, "answerType": mode})
        p = item["params"]
        r = Fraction(p["r"]["num"], p["r"]["den"])
        band = item["difficulty"]["overallBand"]
        ans_int = item["answer"]["canonical"]["den"] == 1
        contrib = (band not in bands
                   or (r > 0 and not flags["rpos"]) or (r < 0 and not flags["rneg"])
                   or (p["r"]["den"] != 1 and not flags["rfrac"]) or (p["r"]["den"] == 1 and not flags["rint"])
                   or (p["u1"] > 0 and not flags["u1pos"]) or (p["u1"] < 0 and not flags["u1neg"])
                   or (abs(r) < 1 and not flags["rlt1"]) or (abs(r) > 1 and not flags["rgt1"])
                   or (ans_int and not flags["ansint"]) or (not ans_int and not flags["ansfrac"]))
        if contrib or len(picked) < 3:
            picked.append((seed, item))
            bands.add(band)
            flags["rpos"] |= r > 0
            flags["rneg"] |= r < 0
            flags["rfrac"] |= p["r"]["den"] != 1
            flags["rint"] |= p["r"]["den"] == 1
            flags["u1pos"] |= p["u1"] > 0
            flags["u1neg"] |= p["u1"] < 0
            flags["rlt1"] |= abs(r) < 1
            flags["rgt1"] |= abs(r) > 1
            flags["ansint"] |= ans_int
            flags["ansfrac"] |= not ans_int
        if (len(picked) >= 3 and len(bands) >= 2 and all(flags.values())) or len(picked) >= target:
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
    v = geo.validate(item)
    calcs = []
    for d in item.get("distractors", []):
        m = MISCONCEPTIONS[d["misconceptionId"]]
        calcs.append({"value": d["display"], "misconceptionId": d["misconceptionId"], "misconception": m["title"],
                      "formula": m["expression"], "rationale": d["rationale"], "feedback": m["feedback"]})
    ans = item["answer"]
    return {"seed": seed, "task": task, "objectiveIds": item["objectiveIds"],
            "interactionType": item["interactionType"], "answerType": ans["type"],
            "canonicalValue": ans["canonical"], "canonicalDisplay": ans["display"],
            "acceptedEquivalentForms": accepted_forms(ans),
            "difficultyProfile": item["difficulty"], "params": item["params"], "calculatorPolicy": item["calculatorPolicy"],
            "prompt": [b.get("text", "") for b in item["prompt"]["blocks"]],
            "workedSolution": item["solution"]["steps"], "distractorCalculations": calcs,
            "validation": v["status"], "validationChecks": [c["name"] for c in v["checks"]],
            "reproduce": {"generatorId": geo.GENERATOR_ID, "generatorVersion": geo.GENERATOR_VERSION,
                          "seed": seed, "config": {"task": task, "answerType": mode}}}


def misconception_examples() -> list:
    out = []
    for mid, m in MISCONCEPTIONS.items():
        task = "sum_n" if mid.startswith("MISC.SERIES") else "nth_term"
        found = None
        for seed in range(1, SCAN_LIMIT + 1):
            item = geo.generate(seed, {"task": task, "answerType": "multiple-choice"})
            for d in item.get("distractors", []):
                if d["misconceptionId"] == mid:
                    found = {"seed": seed, "params": item["params"], "correctAnswer": item["answer"]["display"], "distractorValue": d["display"]}
                    break
            if found:
                break
        out.append({"misconceptionId": mid, "title": m["title"], "formula": m["expression"],
                    "observableError": m["observableError"], "feedback": m["feedback"], "example": found})
    return out


def build() -> None:
    os.makedirs(REVIEW_DIR, exist_ok=True)
    pack = {"generatorId": geo.GENERATOR_ID, "generatorVersion": geo.GENERATOR_VERSION,
            "note": "Representative items for curriculum review. None is approved or published; advancing lifecycle "
                    "state beyond machine-validated is the curriculum authority's decision.",
            "combos": [], "misconceptionCoverage": misconception_examples()}
    for task, mode in COMBOS:
        items = [item_record(s, task, mode, it) for s, it in pick(task, mode)]
        pack["combos"].append({"task": task, "answerType": mode, "count": len(items), "items": items})

    with open(os.path.join(REVIEW_DIR, "geometric_sequences_review_pack.json"), "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)

    L = ["# Curriculum-Review Pack — Geometric Sequences",
         "",
         f"Generator: `{geo.GENERATOR_ID}` v`{geo.GENERATOR_VERSION}`. Generated by `oracle/make_review_pack_geometric.py`.",
         "",
         "> **Review purpose.** Machine-validated items with exact rational answers. Advancing any item to "
         "`curriculum-reviewed` / `approved` / `published` is the curriculum authority's decision. Each "
         "multiple-choice distractor is recomputed from its misconception formula during validation.",
         "",
         "## Misconception rule coverage",
         "",
         "| ID | Misconception | Formula | Example (seed · params → distractor) |",
         "| --- | --- | --- | --- |"]
    for mc in pack["misconceptionCoverage"]:
        ex = mc["example"]
        exs = (f"{ex['seed']} · u1={ex['params']['u1']}, r={rdisp(ex['params']['r'])}, n={ex['params'].get('n','-')} "
               f"→ {ex['distractorValue']} (correct {ex['correctAnswer']})") if ex else "—"
        L.append(f"| `{mc['misconceptionId']}` | {mc['title']} | `{mc['formula']}` | {exs} |")
    L.append("")
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
                  f"- **Reproduce:** `generate({it['seed']}, {json.dumps(it['reproduce']['config'])})` on v`{geo.GENERATOR_VERSION}`",
                  "", "**Question**", ""]
            for p in it["prompt"]:
                L.append(f"> {p}")
            L += ["", f"**Answer:** `{it['canonicalDisplay']}`", "", "**Worked solution**", ""]
            for s in it["workedSolution"]:
                bit = s.get("ruleOrTheorem") or s.get("intermediateResult") or ""
                L.append(f"{s['number']}. {s.get('transformation','')} — `{bit}`")
            L.append("")
            if it["distractorCalculations"]:
                L += ["**Distractor calculations (each a distinct misconception)**", "",
                      "| Value | Formula | Misconception | Rationale | Feedback |", "| --- | --- | --- | --- | --- |"]
                for d in it["distractorCalculations"]:
                    L.append(f"| {d['value']} | `{d['formula']}` | {d['misconception']} (`{d['misconceptionId']}`) | {d['rationale']} | {d['feedback']} |")
                L.append("")
            else:
                L += ["_Free-response: no distractors._", ""]
            L += [f"**Validation:** {it['validation']} — {', '.join('`'+c+'`' for c in it['validationChecks'])}", "",
                  "**Curriculum decision:** ☐ approve  ☐ revise  ☐ reject — notes: ____", "", "---", ""]
    with open(os.path.join(REVIEW_DIR, "geometric_sequences_review_pack.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))

    total = sum(c["count"] for c in pack["combos"])
    print(f"Geometric review pack: {total} items across {len(COMBOS)} combos; {len(pack['misconceptionCoverage'])} rules covered.")


if __name__ == "__main__":
    build()
