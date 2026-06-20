"""Build the revised curriculum-review pack for the arithmetic-sequences generator.

Coverage (per the curriculum-review requirements):
  * at least three examples for every supported (task, answer type),
  * the difficulty bands that occur, positive and negative common differences,
    positive and negative first terms, and small and large term indices,
  * a section exercising every approved misconception rule, and
  * for each item: objective, task, difficulty profile, seed, parameters, prompt,
    answer, worked solution, distractor calculations (formula + value +
    misconception + rationale + feedback), and validation result.

Run:  python oracle/make_review_pack.py
Writes: docs/review/arithmetic_sequences_review_pack.{json,md}
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from spi_oracle import sequences as seq  # noqa: E402
from spi_oracle.misconceptions import MISCONCEPTIONS  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
SCAN_LIMIT = 60000

COMBOS = [
    ("nth_term", "multiple-choice"), ("nth_term", "integer"),
    ("sum_n", "multiple-choice"), ("sum_n", "integer"),
    ("find_d", "integer"), ("find_n_for_value", "integer"),
]


def pick_for_combo(task: str, mode: str, target: int = 6) -> list:
    bands: set = set()
    flags = {"dpos": False, "dneg": False, "a1pos": False, "a1neg": False, "nsmall": False, "nlarge": False}
    picked = []
    for seed in range(1, SCAN_LIMIT + 1):
        item = seq.generate(seed, {"task": task, "answerType": mode})
        p = item["params"]
        band = item["difficulty"]["overallBand"]
        contributes = (
            band not in bands
            or (p["d"] > 0 and not flags["dpos"]) or (p["d"] < 0 and not flags["dneg"])
            or (p["a1"] > 0 and not flags["a1pos"]) or (p["a1"] < 0 and not flags["a1neg"])
            or (p["n"] <= 12 and not flags["nsmall"]) or (p["n"] >= 30 and not flags["nlarge"])
        )
        if contributes or len(picked) < 3:
            picked.append((seed, item))
            bands.add(band)
            if p["d"] > 0:
                flags["dpos"] = True
            elif p["d"] < 0:
                flags["dneg"] = True
            if p["a1"] > 0:
                flags["a1pos"] = True
            elif p["a1"] < 0:
                flags["a1neg"] = True
            if p["n"] <= 12:
                flags["nsmall"] = True
            if p["n"] >= 30:
                flags["nlarge"] = True
        diverse = (len(picked) >= 3 and len(bands) >= 2 and all(flags.values()))
        if diverse or len(picked) >= target:
            break
    return picked


def distractor_calcs(item: dict) -> list:
    calcs = []
    for d in item.get("distractors", []):
        m = MISCONCEPTIONS[d["misconceptionId"]]
        calcs.append({
            "value": d["value"],
            "misconceptionId": d["misconceptionId"],
            "misconception": m["title"],
            "formula": m["expression"],
            "rationale": d["rationale"],
            "feedback": m["feedback"],
        })
    return calcs


def item_record(seed: int, task: str, mode: str, item: dict) -> dict:
    validation = seq.validate(item)
    return {
        "seed": seed,
        "task": task,
        "answerType": mode,
        "objectiveIds": item["objectiveIds"],
        "difficultyProfile": item["difficulty"],
        "params": item["params"],
        "calculatorPolicy": item["calculatorPolicy"],
        "prompt": [b.get("text", "") for b in item["prompt"]["blocks"]],
        "answer": item["answer"]["canonical"],
        "workedSolution": item["solution"]["steps"],
        "distractorCalculations": distractor_calcs(item),
        "validation": validation["status"],
        "validationChecks": [c["name"] for c in validation["checks"]],
        "reproduce": {"generatorId": seq.GENERATOR_ID, "generatorVersion": seq.GENERATOR_VERSION,
                      "seed": seed, "config": {"task": task, "answerType": mode}},
    }


def misconception_examples() -> list:
    """One concrete worked example per approved misconception rule."""
    out = []
    for mid, m in MISCONCEPTIONS.items():
        task = "sum_n" if mid.startswith("MISC.SERIES") else "nth_term"
        found = None
        for seed in range(1, SCAN_LIMIT + 1):
            item = seq.generate(seed, {"task": task, "answerType": "multiple-choice"})
            for d in item.get("distractors", []):
                if d["misconceptionId"] == mid:
                    found = {"seed": seed, "params": item["params"],
                             "correctAnswer": item["answer"]["canonical"], "distractorValue": d["value"]}
                    break
            if found:
                break
        out.append({"misconceptionId": mid, "title": m["title"], "formula": m["expression"],
                    "observableError": m["observableError"], "feedback": m["feedback"], "example": found})
    return out


def build() -> None:
    os.makedirs(REVIEW_DIR, exist_ok=True)
    pack = {
        "generatorId": seq.GENERATOR_ID,
        "generatorVersion": seq.GENERATOR_VERSION,
        "note": "Representative items for curriculum review. None is approved or published; advancing "
                "lifecycle state beyond machine-validated is the curriculum authority's decision.",
        "combos": [],
        "misconceptionCoverage": misconception_examples(),
    }
    for task, mode in COMBOS:
        items = [item_record(s, task, mode, it) for s, it in pick_for_combo(task, mode)]
        pack["combos"].append({"task": task, "answerType": mode, "count": len(items), "items": items})

    json_path = os.path.join(REVIEW_DIR, "arithmetic_sequences_review_pack.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)

    # ---- Markdown ----
    L = [
        "# Curriculum-Review Pack — Arithmetic Sequences (revised)",
        "",
        f"Generator: `{seq.GENERATOR_ID}` v`{seq.GENERATOR_VERSION}`. Generated by `oracle/make_review_pack.py`.",
        "",
        "> **Review purpose.** These items are machine-validated. Advancing any item to "
        "`curriculum-reviewed` / `approved` / `published` is the curriculum authority's decision; this tool "
        "never does so. Each multiple-choice distractor is recomputed from its misconception formula and "
        "checked for value / rationale / feedback agreement during validation.",
        "",
        "## Misconception rule coverage",
        "",
        "| ID | Misconception | Formula | Example (seed · params → distractor) |",
        "| --- | --- | --- | --- |",
    ]
    for mc in pack["misconceptionCoverage"]:
        ex = mc["example"]
        exs = (f"{ex['seed']} · a1={ex['params']['a1']}, d={ex['params']['d']}, n={ex['params']['n']} "
               f"→ {ex['distractorValue']} (correct {ex['correctAnswer']})") if ex else "—"
        L.append(f"| `{mc['misconceptionId']}` | {mc['title']} | `{mc['formula']}` | {exs} |")
    L.append("")

    for combo in pack["combos"]:
        L.append(f"## {combo['task']} · {combo['answerType']} — {combo['count']} examples")
        L.append("")
        for i, it in enumerate(combo["items"], 1):
            dp = it["difficultyProfile"]
            L += [
                f"### {combo['task']}/{combo['answerType']} #{i} — band {dp['overallBand']}",
                "",
                f"- **Objective:** `{it['objectiveIds'][0]}`  ·  **Calculator:** {it['calculatorPolicy']}",
                f"- **Seed:** `{it['seed']}`  ·  **Parameters:** `{json.dumps(it['params'])}`",
                f"- **Difficulty axes:** `{json.dumps(dp['axes'])}`",
                f"- **Reproduce:** `generate({it['seed']}, {json.dumps(it['reproduce']['config'])})` on v`{seq.GENERATOR_VERSION}`",
                "",
                "**Question**", "",
            ]
            for p in it["prompt"]:
                L.append(f"> {p}")
            L += ["", f"**Answer:** `{it['answer']}`", "", "**Worked solution**", ""]
            for s in it["workedSolution"]:
                bit = s.get("ruleOrTheorem") or s.get("intermediateResult") or ""
                L.append(f"{s['number']}. {s.get('transformation','')} — `{bit}`")
            L.append("")
            if it["distractorCalculations"]:
                L += ["**Distractor calculations (each a distinct misconception)**", "",
                      "| Value | Formula | Misconception | Rationale | Feedback |",
                      "| --- | --- | --- | --- | --- |"]
                for d in it["distractorCalculations"]:
                    L.append(f"| {d['value']} | `{d['formula']}` | {d['misconception']} (`{d['misconceptionId']}`) "
                             f"| {d['rationale']} | {d['feedback']} |")
                L.append("")
            else:
                L += ["_Integer free-response: no distractors._", ""]
            L += [f"**Validation:** {it['validation']} — {', '.join('`'+c+'`' for c in it['validationChecks'])}", "",
                  "**Curriculum decision:** ☐ approve  ☐ revise  ☐ reject — notes: ____", "", "---", ""]

    md_path = os.path.join(REVIEW_DIR, "arithmetic_sequences_review_pack.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))

    total = sum(c["count"] for c in pack["combos"])
    print(f"Review pack: {total} items across {len(COMBOS)} (task, answerType) combinations; "
          f"{len(pack['misconceptionCoverage'])} misconception rules covered.")
    print(f"  {os.path.relpath(json_path, ROOT)}")
    print(f"  {os.path.relpath(md_path, ROOT)}")


if __name__ == "__main__":
    build()
