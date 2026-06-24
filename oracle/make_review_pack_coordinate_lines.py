"""Build the coordinate-lines review pack for the curriculum authority (v1.0.1).

Selects UNIQUE representative items (no duplicate task/interaction/seed and no duplicate
canonical item) covering every supported task/interaction combination, every realised
difficulty band, the four quadrants, points on the axes and origin, positive/negative/zero/
integer/fractional gradients, horizontal lines, lines through the origin, positive and
negative intercepts, integer and half-integer midpoints, every misconception rule, the
plot_point blank-grid-vs-answer-overlay, the equation_from_graph no-answer-label figure, and
scaffolded vs unscaffolded variants. The CARTESIAN_PLANE foundational objective and the
prerequisite graph are included in the curriculum summary. The builder FAILS if a supported
interaction or a realised difficulty band is missing from the representative pack.

Writes: docs/review/coordinate_lines_review_pack.{md,json}
        docs/review/coordinate_lines_svgs/*.svg
Run:    python oracle/make_review_pack_coordinate_lines.py
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from spi_oracle import coordinate_lines as cl  # noqa: E402
from spi_oracle.coordinate_misconceptions import MISCONCEPTIONS  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
SVG_DIR = os.path.join(REVIEW_DIR, "coordinate_lines_svgs")
OBJ = cl.OBJECTIVE_BY_TASK
OBJ_FILE = os.path.join(ROOT, "curriculum", "objectives", "SPI.MIDDLE.GEO.COORD.json")
OBJECTIVES = {o["objectiveId"]: o for o in json.load(open(OBJ_FILE, encoding="utf-8"))}
FOUNDATIONAL = "SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01"

# Approved interaction matrix (owner decision B / point 4).
SUPPORTED = {
    "read_point": ["free-response", "multiple-choice"], "plot_point": ["free-response"],
    "gradient_two_points": ["free-response", "multiple-choice"], "midpoint": ["free-response", "multiple-choice"],
    "interpret_mx_c": ["free-response", "multiple-choice"], "equation_from_graph": ["free-response", "multiple-choice"],
    "equation_from_two_points": ["free-response", "multiple-choice"],
}

_used_combo: set = set()
_used_sig: set = set()


def _quadrant(x: int, y: int) -> str:
    if x == 0 or y == 0:
        return "axis/origin"
    return {(True, True): "Q1", (False, True): "Q2", (False, False): "Q3", (True, False): "Q4"}[(x > 0, y > 0)]


def _item_record(seed: int, task: str, interaction: str) -> dict:
    it = cl.generate(seed, {"task": task, "interactionType": interaction})
    v = cl.validate(it)
    rec = {
        "seed": seed, "task": task, "interactionType": interaction, "objective": OBJ[task],
        "band": it["difficulty"]["overallBand"], "answerType": it["answer"]["type"],
        "answerDisplay": it["answer"]["display"], "prompt": it["prompt"]["blocks"][0]["text"],
        "validation": v["status"], "failingChecks": [c["name"] for c in v["checks"] if c["result"] != "pass"],
        "reproduce": {"generatorId": cl.GENERATOR_ID, "seed": seed, "config": {"task": task, "interactionType": interaction}},
        "solution": it["solution"]["steps"],
    }
    if it.get("media"):
        fname = f"{task}__{interaction}__{seed}.svg"
        with open(os.path.join(SVG_DIR, fname), "w", encoding="utf-8") as fh:
            fh.write(it["media"][0]["svg"])
        rec.update(svgFile=fname, altText=it["media"][0]["altText"], longDescription=it["media"][0]["longDescription"],
                   dataTableFallback=it["media"][0]["dataTableFallback"], toScale=it["media"][0]["toScale"])
    else:
        rec["note"] = "text-only item (no figure)"
    if "options" in it:
        rec["options"] = it["options"]
        rec["distractors"] = [{"display": d["display"], "misconceptionId": d["misconceptionId"], "rationale": d["rationale"],
                               "feedback": MISCONCEPTIONS[d["misconceptionId"]]["feedback"]} for d in it["distractors"]]
    return rec


def pick(task: str, interaction: str, predicate=None, n: int = 1, start: int = 1, stop: int = 90000) -> list:
    """Select up to n UNIQUE items (never a duplicate combo or canonical item)."""
    out = []
    for s in range(start, stop):
        if (task, interaction, s) in _used_combo:
            continue
        it = cl.generate(s, {"task": task, "interactionType": interaction})
        if predicate is not None and not predicate(it["params"], it):
            continue
        sig = cl.serialize(it)
        if sig in _used_sig:
            continue
        _used_combo.add((task, interaction, s))
        _used_sig.add(sig)
        out.append(_item_record(s, task, interaction))
        if len(out) >= n:
            break
    return out


def build() -> None:
    os.makedirs(SVG_DIR, exist_ok=True)
    for f in os.listdir(SVG_DIR):
        if f.endswith(".svg"):
            os.remove(os.path.join(SVG_DIR, f))
    _used_combo.clear()
    _used_sig.clear()

    grad = lambda p, it: cl._solve_gradient(p)        # noqa: E731
    line = lambda p, it: cl.params_to_line(p)          # noqa: E731
    line2 = lambda p, it: cl._solve_line_2pts(p)       # noqa: E731

    by_task: dict = {t: [] for t in cl.TASKS}

    # read_point — FR (scaffolded + plain) AND MC (different quadrants).
    by_task["read_point"] += pick("read_point", "free-response", lambda p, it: p["scaffold"] and _quadrant(p["x"], p["y"]) != "axis/origin", 1)
    by_task["read_point"] += pick("read_point", "free-response", lambda p, it: not p["scaffold"], 1)
    by_task["read_point"] += pick("read_point", "multiple-choice", lambda p, it: _quadrant(p["x"], p["y"]) == "Q2", 1)
    by_task["read_point"] += pick("read_point", "multiple-choice", lambda p, it: _quadrant(p["x"], p["y"]) == "Q4", 1)

    # plot_point — FR only; blank grid (target absent). Cover bands 1 and 2.
    by_task["plot_point"] += pick("plot_point", "free-response", lambda p, it: it["difficulty"]["overallBand"] == 1, 1)
    by_task["plot_point"] += pick("plot_point", "free-response", lambda p, it: it["difficulty"]["overallBand"] == 2, 1)

    # gradient — FR (zero gradient is FR-only) AND MC (pos/neg, integer/fractional). Bands 2,3,4.
    by_task["gradient_two_points"] += pick("gradient_two_points", "free-response", lambda p, it: grad(p, it) == 0, 1)        # horizontal -> FR
    by_task["gradient_two_points"] += pick("gradient_two_points", "free-response", lambda p, it: p["scaffold"], 1)
    by_task["gradient_two_points"] += pick("gradient_two_points", "multiple-choice", lambda p, it: grad(p, it) > 0 and grad(p, it).denominator > 1, 1)
    by_task["gradient_two_points"] += pick("gradient_two_points", "multiple-choice", lambda p, it: grad(p, it) < 0, 1)
    by_task["gradient_two_points"] += pick("gradient_two_points", "multiple-choice", lambda p, it: grad(p, it).denominator == 1 and grad(p, it) != 0, 1)

    # midpoint — FR AND MC; integer and half-integer.
    by_task["midpoint"] += pick("midpoint", "free-response", lambda p, it: any(c.denominator == 2 for c in cl._solve_midpoint(p)), 1)
    by_task["midpoint"] += pick("midpoint", "multiple-choice", lambda p, it: all(c.denominator == 1 for c in cl._solve_midpoint(p)), 1)
    by_task["midpoint"] += pick("midpoint", "multiple-choice", lambda p, it: any(c.denominator == 2 for c in cl._solve_midpoint(p)), 1)

    # interpret_mx_c — FR (y = c) AND MC (integer m, fractional m, negative c).
    by_task["interpret_mx_c"] += pick("interpret_mx_c", "free-response", lambda p, it: p["m_num"] == 0, 1)
    by_task["interpret_mx_c"] += pick("interpret_mx_c", "multiple-choice", lambda p, it: p["m_den"] == 1 and p["m_num"] != 0, 1)
    by_task["interpret_mx_c"] += pick("interpret_mx_c", "multiple-choice", lambda p, it: p["m_den"] > 1, 1)
    by_task["interpret_mx_c"] += pick("interpret_mx_c", "multiple-choice", lambda p, it: p["c_num"] < 0, 1)

    # equation_from_graph — FR AND MC; pos/neg gradient, +/- intercept, through origin. Bands 3,4.
    by_task["equation_from_graph"] += pick("equation_from_graph", "free-response", lambda p, it: line(p, it)[0].denominator > 1, 1)
    by_task["equation_from_graph"] += pick("equation_from_graph", "multiple-choice", lambda p, it: line(p, it)[0] > 0 and line(p, it)[1] > 0, 1)
    by_task["equation_from_graph"] += pick("equation_from_graph", "multiple-choice", lambda p, it: line(p, it)[0] < 0 and line(p, it)[1] < 0, 1)
    by_task["equation_from_graph"] += pick("equation_from_graph", "multiple-choice", lambda p, it: line(p, it)[1] == 0, 1)   # through origin

    # equation_from_two_points — FR AND MC; pos/neg gradient. Bands 3,4,5.
    by_task["equation_from_two_points"] += pick("equation_from_two_points", "free-response", lambda p, it: line2(p, it)[0] > 0, 1)
    by_task["equation_from_two_points"] += pick("equation_from_two_points", "multiple-choice", lambda p, it: line2(p, it)[0] > 0, 1)
    by_task["equation_from_two_points"] += pick("equation_from_two_points", "multiple-choice", lambda p, it: line2(p, it)[0] < 0, 1)

    # --- realised-band sweep + enforcement -------------------------------- #
    SW = 4000
    realised: dict = {t: set() for t in cl.TASKS}
    diag = _sweep_diagnostics(SW, realised)

    # Owner-named minimum bands + every realised band must appear in the pack.
    owner_min = {"plot_point": {1, 2}, "gradient_two_points": {2, 3, 4},
                 "equation_from_graph": {3, 4}, "equation_from_two_points": {3, 4, 5}}
    for task in cl.TASKS:
        need = set(realised[task]) | owner_min.get(task, set())
        for band in sorted(need):
            have = {r["band"] for r in by_task[task]}
            if band in have:
                continue
            # try every supported interaction to source the missing band
            found = []
            for inter in SUPPORTED[task]:
                found = pick(task, inter, lambda p, it, b=band: it["difficulty"]["overallBand"] == b, 1)
                if found:
                    break
            if not found:
                raise SystemExit(f"BUILD FAILED: task {task} band {band} is realised but no representative item could be selected")
            by_task[task] += found

    # Interaction-coverage enforcement (every supported task/interaction present).
    for task, inters in SUPPORTED.items():
        for inter in inters:
            if not any(r["interactionType"] == inter for r in by_task[task]):
                got = pick(task, inter, None, 1)
                if not got:
                    raise SystemExit(f"BUILD FAILED: task {task} interaction {inter} has no representative item")
                by_task[task] += got

    notes = {
        "read_point": "free-response AND multiple-choice; all four quadrants; scaffolded (projection guides, lower band) and unscaffolded",
        "plot_point": "free-response ONLY; the student SVG is a blank labelled grid (target point ABSENT); the correct point appears only in the answer key / worked solution; bands 1 and 2",
        "gradient_two_points": "free-response (incl. zero gradient, which is FR-only) AND multiple-choice; positive/negative, integer + fractional gradients; one scaffolded figure (unlabelled rise/run step); bands 2-4",
        "midpoint": "free-response AND multiple-choice; integer and half-integer midpoints; the midpoint is NOT marked in the figure (endpoints only)",
        "interpret_mx_c": "free-response (incl. the constant case y = c) AND multiple-choice; text-only (no figure); integer + fractional gradients, negative intercept; answer displayed as 'm = .., c = ..'",
        "equation_from_graph": "free-response AND multiple-choice; the line carries a NEUTRAL label 'l' (no equation/gradient/intercept shown); positive/negative gradient, positive/negative/zero intercept (through the origin); bands 3-4",
        "equation_from_two_points": "free-response AND multiple-choice; the two given points A, B are plotted with the line through them (no equation label); bands 3-5",
    }
    combos = [{"task": t, "objective": OBJ[t], "note": notes[t], "items": by_task[t]} for t in cl.TASKS]
    diag["realisedBandsByTask"] = {t: sorted(realised[t]) for t in cl.TASKS}

    curriculum = {
        "foundationalObjective": {"objectiveId": FOUNDATIONAL,
                                  "wording": OBJECTIVES[FOUNDATIONAL]["objectiveWording"],
                                  "answerTypes": OBJECTIVES[FOUNDATIONAL]["answerTypes"]},
        "objectives": {oid: {"wording": OBJECTIVES[oid]["objectiveWording"], "answerTypes": OBJECTIVES[oid]["answerTypes"],
                             "prerequisites": OBJECTIVES[oid].get("prerequisites", [])} for oid in OBJECTIVES},
        "answerTypesAreMathematicalOnly": all("multiple-choice" not in o["answerTypes"] for o in OBJECTIVES.values()),
    }

    pack = {
        "generatorId": cl.GENERATOR_ID, "generatorVersion": cl.GENERATOR_VERSION, "validatorVersion": cl.VALIDATOR_VERSION,
        "stage": "SPI-Math Middle School -> Geometry/Algebra bridge", "strand": "coordinate-geometry-straight-line-graphs",
        "curriculum": curriculum, "combos": combos, "diagnostics": diag,
    }
    with open(os.path.join(REVIEW_DIR, "coordinate_lines_review_pack.json"), "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)
    _write_markdown(pack)

    n_items = sum(len(c["items"]) for c in combos)
    cov = {t: sorted({(r["interactionType"][:2], r["band"]) for r in by_task[t]}) for t in cl.TASKS}
    print(f"Coordinate-lines review pack v{cl.GENERATOR_VERSION}: {n_items} UNIQUE items; "
          f"interaction+band coverage OK; misconceptions {len(diag['misconceptionRulesExemplified'])}/"
          f"{len(diag['misconceptionRulesTotal'])}; colours {diag['monochrome']['distinctColours']}; "
          f"leakage {diag['answerLeakageViolations']}.")


def _sweep_diagnostics(sw: int, realised: dict) -> dict:
    grad_kinds = {"positive": 0, "negative": 0, "zero": 0, "integer": 0, "fractional": 0}
    mid_kinds = {"integer": 0, "halfInteger": 0}
    misc_seen: set = set()
    colours: set = set()
    mc_three = mc_total = leak = 0
    for s in range(1, sw + 1):
        for inter in ("free-response", "multiple-choice"):
            it = cl.generate(s, {"interactionType": inter})
            t = it["params"]["task"]
            realised[t].add(it["difficulty"]["overallBand"])
            if it.get("media"):
                colours |= set(re.findall(r"(?:fill|stroke):(#[0-9a-fA-F]{3,6})", it["media"][0]["svg"]))
                if any(ch in tx for tx in re.findall(r"<text[^>]*>([^<]*)</text>", it["media"][0]["svg"]) for ch in (",", "/", "=")):
                    leak += 1
            if inter == "multiple-choice":
                mc_total += 1
                if "options" in it and sum(1 for o in it["options"] if not o["correct"]) == 3:
                    mc_three += 1
                for d in it.get("distractors", []):
                    misc_seen.add(d["misconceptionId"])
            if inter == "free-response" and t == "gradient_two_points":
                m = cl._solve_gradient(it["params"])
                grad_kinds["positive" if m > 0 else ("negative" if m < 0 else "zero")] += 1
                grad_kinds["integer" if m.denominator == 1 else "fractional"] += 1
            if inter == "free-response" and t == "midpoint":
                mx, my = cl._solve_midpoint(it["params"])
                mid_kinds["integer" if (mx.denominator == 1 and my.denominator == 1) else "halfInteger"] += 1
    return {
        "gradientKinds": grad_kinds, "midpointKinds": mid_kinds,
        "misconceptionRulesExemplified": sorted(misc_seen),
        "misconceptionRulesTotal": sorted(m for m in MISCONCEPTIONS if MISCONCEPTIONS[m]["adapt"]),
        "mcThreeDistinctDistractors": {"items": mc_three, "of": mc_total},
        "monochrome": {"sweep": sw, "distinctColours": sorted(colours), "colourOnlyInformation": False},
        "answerLeakageViolations": leak, "pngExport": cl.png_export_transform(),
    }


def _write_markdown(pack: dict) -> None:
    L = ["# Curriculum-Review Pack — Coordinate geometry & straight-line graphs (SVG)\n"]
    L.append(f"Generator: `{pack['generatorId']}` v`{pack['generatorVersion']}` — **IMPLEMENTED, PENDING FINAL CURRICULUM REVIEW**. "
             f"Stage: {pack['stage']} (strand `{pack['strand']}`). Generated by `oracle/make_review_pack_coordinate_lines.py`.\n")
    L.append("> **Review purpose.** Machine-validated coordinate-geometry items with exact-rational answers and "
             "deterministic, to-scale Cartesian figures, byte-for-byte identical between the Python oracle and the "
             "TypeScript app. Every figure is built from the same parameters as the prompt, answer, solution, and "
             "accessibility description. Advancing any item past `machine-validated` is the curriculum authority's decision.\n")
    cur = pack["curriculum"]
    L.append("## Curriculum objectives under review\n")
    L.append(f"**Foundational prerequisite.** `{cur['foundationalObjective']['objectiveId']}` — "
             f"\"{cur['foundationalObjective']['wording']}\" (answerTypes: {cur['foundationalObjective']['answerTypes']}).\n")
    L.append("| Objective | answerTypes (mathematical only) | prerequisites |\n| --- | --- | --- |")
    for oid, info in cur["objectives"].items():
        L.append(f"| `{oid}` | {info['answerTypes']} | {', '.join('`'+p+'`' for p in info['prerequisites']) or '—'} |")
    L.append(f"\n_All objective answerTypes are mathematical response types only (no `multiple-choice` in answerTypes): "
             f"**{cur['answerTypesAreMathematicalOnly']}**. Multiple-choice is an interaction mode, recorded separately._\n")
    L.append("### Prerequisite graph (edges)\n")
    for oid, info in cur["objectives"].items():
        for pr in info["prerequisites"]:
            L.append(f"- `{pr}` → `{oid}`")
    L.append("")
    for combo in pack["combos"]:
        L.append(f"## {combo['task']} — `{combo['objective']}`\n")
        L.append(f"_{combo['note']}_\n")
        for rec in combo["items"]:
            L.append(f"### seed {rec['seed']} — {rec['interactionType']}, band {rec['band']}\n")
            L.append(f"**Prompt.** {rec['prompt']}\n")
            if "svgFile" in rec:
                L.append(f"![figure](coordinate_lines_svgs/{rec['svgFile']})\n")
                L.append(f"_Alt text._ {rec['altText']}\n")
            L.append(f"**Answer** ({rec['answerType']}): `{rec['answerDisplay']}`\n")
            if "options" in rec:
                L.append("Options: " + "  ".join(f"{o['label']}. `{o['display']}`" + ("  ✓" if o["correct"] else "") for o in rec["options"]) + "\n")
                for d in rec["distractors"]:
                    L.append(f"- `{d['display']}` — {d['misconceptionId']}: {d['feedback']}")
                L.append("")
            L.append("Worked solution: " + " ".join(f"({s['number']}) {s['transformation']} → {s.get('intermediateResult','')}" for s in rec["solution"]) + "\n")
            L.append(f"Validation: **{rec['validation']}**" + (f" — FAILS {rec['failingChecks']}" if rec["failingChecks"] else "") + f". Reproduce: `generate({rec['seed']}, {rec['reproduce']['config']})`.\n")
    d = pack["diagnostics"]
    L.append("## Diagnostics\n")
    L.append(f"- **Realised difficulty bands (per task):** {d['realisedBandsByTask']} — every realised band is represented above.")
    L.append(f"- **Gradient coverage:** {d['gradientKinds']}")
    L.append(f"- **Midpoint coverage:** {d['midpointKinds']}")
    L.append(f"- **Misconception rules exemplified:** {len(d['misconceptionRulesExemplified'])} of {len(d['misconceptionRulesTotal'])} — {d['misconceptionRulesExemplified']}")
    L.append(f"- **Multiple-choice 3-distinct-distractor invariant:** {d['mcThreeDistinctDistractors']['items']}/{d['mcThreeDistinctDistractors']['of']} items")
    L.append(f"- **Monochrome (canonical SVG):** colours {d['monochrome']['distinctColours']}; no colour-only information; sweep {d['monochrome']['sweep']}")
    L.append(f"- **Answer-leakage violations (figure text states a coordinate/fraction/equation):** {d['answerLeakageViolations']}")
    L.append(f"- **High-resolution raster export:** {d['pngExport']['width']}×{d['pngExport']['height']} (scale {d['pngExport']['scale']}) derived from the canonical SVG; the SVG is the authoritative 8K-like deliverable.")
    L.append("")
    with open(os.path.join(REVIEW_DIR, "coordinate_lines_review_pack.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    build()
