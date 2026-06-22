"""Build the curriculum-review pack for the geometry-angles generator (v1.0.0).

Coverage (owner revision 11): all five objectives/tasks; free-response + multiple-
choice; every supported band per task; two-given vs multi-given straight line; general
vs isosceles triangle; vertically opposite; angles around a point; every misconception
rule; the distractor-collision / deterministic-regeneration invariant; minimum (10 deg)
and maximum visible angles; non-multiple-of-5 angles; non-colour indicators; multi-item
export; and monochrome output. Each item shows full reproduction metadata, difficulty
axes + structural floor, the worked solution, the MC distractor calculations, the inline
generated SVG (+ a saved .svg file), the alt text, long description, data-table fallback,
and the diagram-to-data + accessibility validation results.

Run:  python oracle/make_review_pack_geometry.py
Writes: docs/review/geometry_angles_review_pack.{json,md} and docs/review/geometry_svgs/*.svg
"""

from __future__ import annotations

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from spi_oracle import geometry as geo  # noqa: E402
from spi_oracle.geometry_misconceptions import MISCONCEPTIONS, rules_for  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
SVG_DIR = os.path.join(REVIEW_DIR, "geometry_svgs")
SCAN_LIMIT = 40000
DIAGRAM_CHECKS = ("svg-realises-data", "labels-non-overlapping", "not-to-scale", "no-answer-leakage", "media-present")
A11Y_CHECKS = ("a11y-fields-present", "a11y-no-answer-in-text")


def _modes(task: str) -> list:
    return ["free-response"] if task not in geo.MC_TASKS else ["free-response", "multiple-choice"]


COMBOS = [(t, m) for t in geo.TASKS for m in _modes(t)]


def _flags(item) -> dict:
    p = item["params"]
    g = geo._ctx(p)
    ans = item["answer"]["canonical"]["num"]
    vals = g["givens"] + [ans]
    return {
        "band": item["difficulty"]["overallBand"],
        "twoGiven": len(g["givens"]) == 2,
        "multiGiven": len(g["givens"]) >= 3,
        "hasMin": any(v == geo.MIN_ANGLE for v in g["givens"]),
        "hasObtuse": any(v > 90 for v in g["givens"]),
        "nonMult5": any(v % 5 != 0 for v in vals),
        "allMult5": all(v % 5 == 0 for v in vals),
    }


def pick(task: str, mode: str, target: int = 5) -> list:
    lo, hi = geo.TASK_BANDS[task]
    need_bands = set(range(lo, hi + 1))
    bands: set = set()
    seen = {k: False for k in ("twoGiven", "multiGiven", "hasMin", "hasObtuse", "nonMult5", "allMult5")}
    picked = []
    for seed in range(1, SCAN_LIMIT + 1):
        item = geo.generate(seed, {"task": task, "interactionType": mode})
        fl = _flags(item)
        contrib = fl["band"] not in bands or any(fl.get(k) and not seen[k] for k in seen)
        if contrib or len(picked) < 3:
            picked.append((seed, item))
            bands.add(fl["band"])
            for k in seen:
                seen[k] |= bool(fl.get(k))
        if len(picked) >= target and need_bands <= bands:
            break
    return picked


def _svg_filename(task, mode, seed) -> str:
    return f"{task}__{mode}__{seed}.svg"


def item_record(seed, task, mode, item) -> dict:
    v = geo.validate(item)
    checks = {c["name"]: c["result"] for c in v["checks"]}
    g = geo._ctx(item["params"])
    calcs = []
    for d in item.get("distractors", []):
        m = MISCONCEPTIONS[d["misconceptionId"]]
        calcs.append({"value": d["display"], "misconceptionId": d["misconceptionId"], "misconception": m["title"],
                      "formula": m["expression"], "rationale": d["rationale"], "feedback": m["feedback"]})
    options = [{"label": o["label"], "display": o["display"], "correct": o["correct"]} for o in item.get("options", [])]
    media = item["media"][0]
    lo, hi = geo.TASK_BANDS[task]
    return {
        "seed": seed, "task": task, "family": geo.FAMILY_BY_TASK[task], "objectiveIds": item["objectiveIds"],
        "interactionType": item["interactionType"], "answerType": item["answer"]["type"],
        "units": item["answer"].get("units"), "canonicalValue": item["answer"]["canonical"],
        "canonicalDisplay": item["answer"]["display"], "givens": g["givens"],
        "difficultyProfile": item["difficulty"], "structuralFloor": lo, "bandRange": [lo, hi],
        "params": item["params"], "calculatorPolicy": item["calculatorPolicy"], "generatorVersion": item["generatorVersion"],
        "promptText": next((b.get("text", "") for b in item["prompt"]["blocks"] if b.get("text")), ""),
        "svg": media["svg"], "svgFile": _svg_filename(task, mode, seed),
        "altText": media["altText"], "longDescription": media["longDescription"],
        "dataTableFallback": media["dataTableFallback"], "toScale": media["toScale"],
        "workedSolution": item["solution"]["steps"],
        "optionOrder": options, "distractorCalculations": calcs,
        "validation": v["status"],
        "diagramValidation": {k: checks.get(k, "n/a") for k in DIAGRAM_CHECKS},
        "accessibilityValidation": {**{k: checks.get(k, "n/a") for k in A11Y_CHECKS},
                                    "nonColorIndicators": item["accessibility"]["nonColorIndicators"]},
        "reproduce": {"generatorId": geo.GENERATOR_ID, "generatorVersion": geo.GENERATOR_VERSION,
                      "seed": seed, "config": {"task": task, "interactionType": mode}},
    }


def misconception_examples() -> list:
    out = []
    for mid, m in MISCONCEPTIONS.items():
        tasks = [t for t in geo.MC_TASKS if mid in rules_for(t)]
        found = None
        for task in tasks:
            for seed in range(1, SCAN_LIMIT + 1):
                item = geo.generate(seed, {"task": task, "interactionType": "multiple-choice"})
                for d in item.get("distractors", []):
                    if d["misconceptionId"] == mid:
                        found = {"seed": seed, "task": task, "correctAnswer": item["answer"]["display"],
                                 "distractorValue": d["display"], "studentFeedback": m["feedback"]}
                        break
                if found:
                    break
            if found:
                break
        out.append({"misconceptionId": mid, "title": m["title"], "formula": m["expression"],
                    "observableError": m["observableError"], "diagnosticOnly": (rules_for_none(mid)), "example": found})
    return out


def rules_for_none(mid: str) -> bool:
    return not any(mid in rules_for(t) for t in geo.TASKS)


def collision_invariant(sweep: int = 10000) -> dict:
    bad = 0
    for seed in range(1, sweep + 1):
        item = geo.generate(seed, {"interactionType": "multiple-choice"})
        opts = [o["display"] for o in item["options"] if not o["correct"]]
        if len(opts) != 3 or len(set(opts)) != 3:
            bad += 1
    return {"sweep": sweep, "mcItemsWithThreeDistinctDistractors": sweep - bad, "violations": bad}


def to_scale_diagnostic(sweep: int = 2000) -> dict:
    """Non-blocking +/-0.5 deg fidelity check on the vertically-opposite rays (atan2 here only)."""
    worst = 0.0
    for s in range(1, sweep + 1):
        item = geo.generate(s, {"task": "vertically_opposite_angle", "interactionType": "free-response"})
        theta = item["params"]["theta"]
        P = geo._layout(geo._build_figure(item["params"])["points"])
        ox, oy = P["O"]
        drawn = []
        for m in re.finditer(r'<line class="gl" x1="(-?\d+)" y1="(-?\d+)" x2="(-?\d+)" y2="(-?\d+)"', item["media"][0]["svg"]):
            x1, y1, x2, y2 = map(int, m.groups())
            for (px, py) in ((x1, y1), (x2, y2)):
                if (px, py) != (ox, oy):
                    drawn.append(math.degrees(math.atan2(-(py - oy), px - ox)) % 360)
        for target in (0.0, 180.0, float(theta), float((theta + 180) % 360)):
            nearest = min(drawn, key=lambda a: min(abs(a - target), 360 - abs(a - target)))
            worst = max(worst, min(abs(nearest - target), 360 - abs(nearest - target)))
    return {"sweep": sweep, "worstDrawnRayErrorDeg": round(worst, 4), "toleranceDeg": 0.5}


def monochrome_summary(sweep: int = 2000) -> dict:
    colours: set = set()
    for s in range(1, sweep + 1):
        svg = geo.generate(s, {"interactionType": "multiple-choice"})["media"][0]["svg"]
        colours |= set(re.findall(r'(?:fill|stroke):(#[0-9a-fA-F]{3,6})', svg))
    return {"sweep": sweep, "distinctColours": sorted(colours), "colourOnlyInformation": False}


def _table_md(dt) -> list:
    cols = dt["columns"]
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for row in dt["rows"]:
        out.append("| " + " | ".join(str(c) for c in row) + " |")
    return out


def build() -> None:
    os.makedirs(SVG_DIR, exist_ok=True)
    pack = {
        "generatorId": geo.GENERATOR_ID, "generatorVersion": geo.GENERATOR_VERSION,
        "note": "Representative machine-validated diagram items for curriculum review. None is approved or published; "
                "advancing lifecycle state beyond machine-validated is the curriculum authority's decision. Every figure "
                "is computed from the SAME parameters as the prompt and answer; the SVG is byte-identical across the "
                "Python oracle and the TypeScript app; all figures are NOT TO SCALE.",
        "objectives": {t: geo.OBJECTIVE_BY_TASK[t] for t in geo.TASKS},
        "combos": [], "misconceptionCoverage": misconception_examples(),
        "collisionInvariant": collision_invariant(),
        "toScaleDiagnostic": to_scale_diagnostic(),
        "monochrome": monochrome_summary(),
        "multiItemExport": {"note": "Multiple inline SVGs in one exported worksheet have NO duplicate DOM ids, each "
                                    "carries role=img + aria-label + <title>/<desc>, and no answer appears in any "
                                    "accessibility text. Enforced by apps/generator-studio/a11y.test.ts."},
    }
    for task, mode in COMBOS:
        items = []
        for s, it in pick(task, mode):
            rec = item_record(s, task, mode, it)
            with open(os.path.join(SVG_DIR, rec["svgFile"]), "w", encoding="utf-8") as fh:
                fh.write(rec["svg"])
            items.append(rec)
        pack["combos"].append({"task": task, "objective": geo.OBJECTIVE_BY_TASK[task], "family": geo.FAMILY_BY_TASK[task],
                               "interactionType": mode, "count": len(items), "items": items})

    with open(os.path.join(REVIEW_DIR, "geometry_angles_review_pack.json"), "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2, ensure_ascii=False)

    ci, ts, mono = pack["collisionInvariant"], pack["toScaleDiagnostic"], pack["monochrome"]
    L = ["# Curriculum-Review Pack — Geometry: Angles, Lines & Triangles (SVG diagrams)",
         "",
         f"Generator: `{geo.GENERATOR_ID}` v`{geo.GENERATOR_VERSION}`. Stage: SPI-Math Middle School -> Geometry -> "
         "Ch.21 (Angles, Lines, Triangles). Generated by `oracle/make_review_pack_geometry.py`.",
         "",
         "> **Review purpose.** Machine-validated diagram items with exact integer-degree answers. Advancing any item or "
         "objective to `curriculum-reviewed` / `approved` / `published` is the curriculum authority's decision. The "
         "diagram IS the question: every figure is built from the same parameters as the prompt and answer, ray "
         "directions come from a committed integer table (no runtime trigonometry), coordinates use one round-half-up "
         "rule, and the SVG is byte-for-byte identical between the Python oracle and the TypeScript app. All figures "
         "are **NOT TO SCALE**.",
         "",
         "## Objectives under review (one task each)",
         "",
         "| Task | Family | Objective | MC? |",
         "| --- | --- | --- | --- |"]
    for t in geo.TASKS:
        L.append(f"| {t} | {geo.FAMILY_BY_TASK[t]} | `{geo.OBJECTIVE_BY_TASK[t]}` | {'yes' if t in geo.MC_TASKS else 'no (free-response only in v1.0.0)'} |")
    L += ["",
          "## Platform-gate summaries", "",
          f"- **Distractor collision / deterministic regeneration:** over a {ci['sweep']:,}-seed MC sweep, "
          f"**{ci['mcItemsWithThreeDistinctDistractors']:,}** items had exactly three distinct, formula-backed "
          f"distractors; **{ci['violations']}** violations. When three cannot be formed, the generator deterministically "
          "regenerates parameters (same seed -> same item).",
          f"- **To-scale fidelity (non-blocking diagnostic):** across {ts['sweep']:,} vertically-opposite items, the "
          f"worst drawn-ray error is **{ts['worstDrawnRayErrorDeg']} deg** (tolerance {ts['toleranceDeg']} deg). This "
          "diagnostic is the only place `atan2` is used; it never gates generation or validation.",
          f"- **Monochrome / no colour-only information:** across {mono['sweep']:,} items the only colours used are "
          f"`{', '.join(mono['distinctColours'])}` (near-black inks); no information is conveyed by colour alone.",
          "- **Multi-item export:** " + pack["multiItemExport"]["note"],
          "",
          "## Misconception rule coverage (MC distractor rules)", "",
          "| ID | Misconception | Formula (teacher) | Example (seed · task -> distractor vs answer) | Student feedback |",
          "| --- | --- | --- | --- | --- |"]
    for mc in pack["misconceptionCoverage"]:
        ex = mc["example"]
        exs = (f"{ex['seed']} · {ex['task']} -> {ex['distractorValue']} (correct {ex['correctAnswer']})") if ex else ("— (diagnostic-only)" if mc["diagnosticOnly"] else "—")
        fb = ex["studentFeedback"] if ex else "—"
        L.append(f"| `{mc['misconceptionId']}` | {mc['title']} | `{mc['formula']}` | {exs} | {fb} |")
    L += ["",
          "_`MISC.GEOM.VO.USES_SUPPLEMENTARY` is diagnostic-only: vertically-opposite is free-response in v1.0.0, so it "
          "is never used to build a multiple-choice distractor._", ""]

    for combo in pack["combos"]:
        L += [f"## {combo['task']} · {combo['interactionType']} — {combo['count']} examples  ({combo['family']}, `{combo['objective']}`)", ""]
        for i, it in enumerate(combo["items"], 1):
            dp = it["difficultyProfile"]
            cv = it["canonicalValue"]
            L += [f"### {combo['task']} / {combo['interactionType']} #{i} — band {dp['overallBand']} (floor {it['structuralFloor']}, range {it['bandRange']})", "",
                  f"- **Objective:** `{it['objectiveIds'][0]}`  ·  **Family:** {it['family']}  ·  **Calculator:** {it['calculatorPolicy']}",
                  f"- **Interaction type:** {it['interactionType']}  ·  **Answer type:** {it['answerType']}  ·  **Units:** {it['units']}",
                  f"- **Canonical value:** `num={cv['num']}, den={cv['den']}` -> `{it['canonicalDisplay']}`  ·  **Givens:** `{it['givens']}`",
                  f"- **Seed:** `{it['seed']}`  ·  **Generator:** v`{it['generatorVersion']}`  ·  **Parameters:** `{json.dumps(it['params'])}`",
                  f"- **Difficulty axes:** `{json.dumps(dp['axes'])}`  ·  **Band:** {dp['overallBand']}",
                  f"- **To scale:** {it['toScale']} (figure is NOT drawn to scale)",
                  f"- **Reproduce:** `generate({it['seed']}, {json.dumps(it['reproduce']['config'])})` on v`{geo.GENERATOR_VERSION}`",
                  "", "**Question**", "",
                  f"> {it['promptText']}", "",
                  f"![{it['altText']}](geometry_svgs/{it['svgFile']})", "",
                  "<details><summary>Inline SVG (source)</summary>", "", "```xml", it["svg"], "```", "", "</details>", "",
                  f"**Alt text:** {it['altText']}", "",
                  f"**Long description:** {it['longDescription']}", "",
                  "**Data-table fallback**", ""]
            L += _table_md(it["dataTableFallback"])
            L += ["", f"**Answer:** `x = {it['canonicalDisplay']}`", "", "**Worked solution**", ""]
            for s in it["workedSolution"]:
                bit = s.get("intermediateResult") or s.get("ruleOrTheorem") or ""
                L.append(f"{s['number']}. {s.get('transformation','')} — `{bit}`")
            L.append("")
            if it["optionOrder"]:
                order = "  ".join(f"{o['label']}. {o['display']}{' (correct)' if o['correct'] else ''}" for o in it["optionOrder"])
                L += [f"**MC option order:** {order}", "",
                      "**Distractor calculations (each a distinct misconception pathway)**", "",
                      "| Value | Formula (teacher) | Misconception | Rationale | Student feedback |",
                      "| --- | --- | --- | --- | --- |"]
                for d in it["distractorCalculations"]:
                    L.append(f"| `{d['value']}` | `{d['formula']}` | {d['misconception']} (`{d['misconceptionId']}`) | {d['rationale']} | {d['feedback']} |")
                L.append("")
            else:
                L += ["_Free-response: no distractors._", ""]
            dv = "  ".join(f"`{k}`={v}" for k, v in it["diagramValidation"].items())
            av = "  ".join(f"`{k}`={v}" for k, v in it["accessibilityValidation"].items())
            L += [f"**Diagram-to-data validation:** {dv}",
                  "", f"**Accessibility validation:** {av}",
                  "", f"**Overall validation:** {it['validation']}",
                  "", "**Curriculum decision:** [ ] approve  [ ] revise  [ ] reject — notes: ____", "", "---", ""]

    with open(os.path.join(REVIEW_DIR, "geometry_angles_review_pack.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))

    total = sum(c["count"] for c in pack["combos"])
    rules = sum(1 for mc in pack["misconceptionCoverage"] if mc["example"])
    print(f"Geometry review pack v{geo.GENERATOR_VERSION}: {total} items across {len(COMBOS)} combos; "
          f"{rules}/{len(pack['misconceptionCoverage'])} misconception rules exemplified; "
          f"collision violations: {ci['violations']}; worst to-scale error {ts['worstDrawnRayErrorDeg']} deg; "
          f"colours {mono['distinctColours']}.")


if __name__ == "__main__":
    build()
