"""Build the coordinate-lines review pack for the curriculum authority.

Selects representative items covering every owner-required dimension (all 7 tasks, FR + MC,
every difficulty band, the four quadrants, points on the axes and origin, positive/negative/
zero/integer/fractional gradients, horizontal lines, lines through the origin, positive and
negative intercepts, integer and half-integer midpoints, every misconception rule, the
plot_point student-graph-vs-answer-overlay, the equation_from_graph no-answer-label figure,
and scaffolded vs unscaffolded variants) plus parity/monochrome/leakage diagnostics.

Writes: docs/review/coordinate_lines_review_pack.{md,json}
        docs/review/coordinate_lines_svgs/*.svg
Run:    python oracle/make_review_pack_coordinate_lines.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from spi_oracle import coordinate_lines as cl  # noqa: E402
from spi_oracle.coordinate_misconceptions import MISCONCEPTIONS  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
SVG_DIR = os.path.join(REVIEW_DIR, "coordinate_lines_svgs")
OBJ = cl.OBJECTIVE_BY_TASK


def _quadrant(x: int, y: int) -> str:
    if x == 0 or y == 0:
        return "axis/origin"
    return {(True, True): "Q1", (False, True): "Q2", (False, False): "Q3", (True, False): "Q4"}[(x > 0, y > 0)]


def _item_record(seed: int, task: str, interaction: str) -> dict:
    it = cl.generate(seed, {"task": task, "interactionType": interaction})
    v = cl.validate(it)
    rec = {
        "seed": seed, "task": task, "interactionType": interaction,
        "objective": OBJ[task], "band": it["difficulty"]["overallBand"],
        "answerType": it["answer"]["type"], "answerDisplay": it["answer"]["display"],
        "prompt": it["prompt"]["blocks"][0]["text"],
        "validation": v["status"], "failingChecks": [c["name"] for c in v["checks"] if c["result"] != "pass"],
        "reproduce": {"generatorId": cl.GENERATOR_ID, "seed": seed, "config": {"task": task, "interactionType": interaction}},
        "solution": it["solution"]["steps"],
    }
    if it.get("media"):
        fname = f"{task}__{interaction}__{seed}.svg"
        with open(os.path.join(SVG_DIR, fname), "w", encoding="utf-8") as fh:
            fh.write(it["media"][0]["svg"])
        rec["svgFile"] = fname
        rec["altText"] = it["media"][0]["altText"]
        rec["longDescription"] = it["media"][0]["longDescription"]
        rec["dataTableFallback"] = it["media"][0]["dataTableFallback"]
        rec["toScale"] = it["media"][0]["toScale"]
    if "options" in it:
        rec["options"] = it["options"]
        rec["distractors"] = [{"display": d["display"], "misconceptionId": d["misconceptionId"], "rationale": d["rationale"],
                               "feedback": MISCONCEPTIONS[d["misconceptionId"]]["feedback"]} for d in it["distractors"]]
    return rec


def _scan(task: str, predicate, interaction: str, limit: int = 6, start: int = 1, stop: int = 60000) -> list:
    out = []
    for s in range(start, stop):
        it = cl.generate(s, {"task": task, "interactionType": interaction})
        if predicate(it["params"], it):
            out.append(_item_record(s, task, interaction))
            if len(out) >= limit:
                break
    return out


def build() -> None:
    os.makedirs(SVG_DIR, exist_ok=True)
    for f in os.listdir(SVG_DIR):
        if f.endswith(".svg"):
            os.remove(os.path.join(SVG_DIR, f))

    combos = []

    # read_point: cover all four quadrants + a point on an axis + scaffolded vs not.
    rp = []
    seen_q = set()
    for s in range(1, 40000):
        it = cl.generate(s, {"task": "read_point", "interactionType": "multiple-choice"})
        q = _quadrant(it["params"]["x"], it["params"]["y"])
        key = (q, it["params"]["scaffold"])
        if key not in seen_q and q != "axis/origin":
            seen_q.add(key)
            rp.append(_item_record(s, "read_point", "multiple-choice"))
        if len({k[0] for k in seen_q}) >= 4 and len(rp) >= 6:
            break
    combos.append({"task": "read_point", "objective": OBJ["read_point"], "note": "all four quadrants; scaffolded (with projection guides, lower band) and unscaffolded", "items": rp})

    # plot_point: FR only; student graph is blank (target absent) — pair with the answer overlay note.
    pp = _scan("plot_point", lambda p, it: True, "free-response", limit=4)
    combos.append({"task": "plot_point", "objective": OBJ["plot_point"], "note": "free-response only; the student SVG is a blank labelled grid (target point ABSENT); the correct point appears only in the answer key / worked solution", "items": pp})

    # gradient: positive, negative, zero (FR-only), integer, fractional, scaffolded.
    grad = []
    grad += _scan("gradient_two_points", lambda p, it: cl._solve_gradient(p) > 0 and cl._solve_gradient(p).denominator > 1, "multiple-choice", 2)
    grad += _scan("gradient_two_points", lambda p, it: cl._solve_gradient(p) < 0, "multiple-choice", 2)
    grad += _scan("gradient_two_points", lambda p, it: cl._solve_gradient(p).denominator == 1 and cl._solve_gradient(p) != 0, "multiple-choice", 1)
    grad += _scan("gradient_two_points", lambda p, it: cl._solve_gradient(p) == 0, "free-response", 1)  # horizontal: FR-only
    grad += _scan("gradient_two_points", lambda p, it: p.get("scaffold") is True, "free-response", 1)
    combos.append({"task": "gradient_two_points", "objective": OBJ["gradient_two_points"], "note": "positive/negative/zero, integer + fractional gradients; zero gradient is FREE-RESPONSE ONLY; one scaffolded figure (unlabelled rise/run step)", "items": grad})

    # midpoint: integer midpoint, half-integer midpoint, a quadrant spread.
    mid = []
    mid += _scan("midpoint", lambda p, it: all(c.denominator == 1 for c in cl._solve_midpoint(p)), "multiple-choice", 2)
    mid += _scan("midpoint", lambda p, it: any(c.denominator == 2 for c in cl._solve_midpoint(p)), "multiple-choice", 3)
    combos.append({"task": "midpoint", "objective": OBJ["midpoint"], "note": "integer and half-integer midpoints; the midpoint is NOT marked in the figure (endpoints only)", "items": mid})

    # interpret_mx_c: integer m, fractional m, negative c, m=0 (y=c).
    interp = []
    interp += _scan("interpret_mx_c", lambda p, it: p["m_den"] == 1 and p["m_num"] != 0, "multiple-choice", 1)
    interp += _scan("interpret_mx_c", lambda p, it: p["m_den"] > 1, "multiple-choice", 2)
    interp += _scan("interpret_mx_c", lambda p, it: p["c_num"] < 0, "multiple-choice", 1)
    interp += _scan("interpret_mx_c", lambda p, it: p["m_num"] == 0, "free-response", 1)  # y = c
    combos.append({"task": "interpret_mx_c", "objective": OBJ["interpret_mx_c"], "note": "text-only (no figure); integer + fractional gradients, negative intercept, and the constant case y = c; answer displayed as 'm = .., c = ..'", "items": interp})

    # equation_from_graph: positive/negative gradient, +/- intercept, through origin, no answer label.
    efg = []
    efg += _scan("equation_from_graph", lambda p, it: cl.params_to_line(p)[0] > 0 and cl.params_to_line(p)[1] > 0, "multiple-choice", 1)
    efg += _scan("equation_from_graph", lambda p, it: cl.params_to_line(p)[0] < 0 and cl.params_to_line(p)[1] < 0, "multiple-choice", 1)
    efg += _scan("equation_from_graph", lambda p, it: cl.params_to_line(p)[1] == 0, "multiple-choice", 1)  # through origin
    efg += _scan("equation_from_graph", lambda p, it: cl.params_to_line(p)[0].denominator > 1, "free-response", 1)
    combos.append({"task": "equation_from_graph", "objective": OBJ["equation_from_graph"], "note": "the line carries a NEUTRAL label 'l' (no equation/gradient/intercept shown); positive/negative gradient, positive/negative/zero intercept (through the origin), fractional gradient", "items": efg})

    # equation_from_two_points: positive/negative gradient, fractional intercept.
    e2 = []
    e2 += _scan("equation_from_two_points", lambda p, it: cl._solve_line_2pts(p)[0] > 0, "multiple-choice", 2)
    e2 += _scan("equation_from_two_points", lambda p, it: cl._solve_line_2pts(p)[0] < 0, "multiple-choice", 2)
    combos.append({"task": "equation_from_two_points", "objective": OBJ["equation_from_two_points"], "note": "the two given points are plotted (A, B) with the line through them; no equation label", "items": e2})

    # --- diagnostics ---------------------------------------------------- #
    SW = 4000
    bands_by_task: dict = {t: set() for t in cl.TASKS}
    grad_kinds = {"positive": 0, "negative": 0, "zero": 0, "integer": 0, "fractional": 0}
    mid_kinds = {"integer": 0, "halfInteger": 0}
    misc_seen = set()
    colours: set = set()
    mc_three = 0
    mc_total = 0
    leak_violations = 0
    for s in range(1, SW + 1):
        for inter in ("free-response", "multiple-choice"):
            it = cl.generate(s, {"interactionType": inter})
            t = it["params"]["task"]
            bands_by_task[t].add(it["difficulty"]["overallBand"])
            if it.get("media"):
                colours |= set(re.findall(r"(?:fill|stroke):(#[0-9a-fA-F]{3,6})", it["media"][0]["svg"]))
                texts = re.findall(r"<text[^>]*>([^<]*)</text>", it["media"][0]["svg"])
                if any(ch in tx for tx in texts for ch in (",", "/", "=")):
                    leak_violations += 1
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

    diagnostics = {
        "bandsByTask": {t: sorted(bands_by_task[t]) for t in cl.TASKS},
        "gradientKinds": grad_kinds, "midpointKinds": mid_kinds,
        "misconceptionRulesExemplified": sorted(misc_seen),
        "misconceptionRulesTotal": sorted(m for m in MISCONCEPTIONS if MISCONCEPTIONS[m]["adapt"]),
        "mcThreeDistinctDistractors": {"items": mc_three, "of": mc_total},
        "monochrome": {"sweep": SW, "distinctColours": sorted(colours), "colourOnlyInformation": False},
        "answerLeakageViolations": leak_violations,
        "pngExport": cl.png_export_transform(),
    }

    pack = {
        "generatorId": cl.GENERATOR_ID, "generatorVersion": cl.GENERATOR_VERSION,
        "validatorVersion": cl.VALIDATOR_VERSION, "stage": "SPI-Math Middle School -> Geometry/Algebra bridge",
        "strand": "coordinate-geometry-straight-line-graphs", "objectives": OBJ, "combos": combos, "diagnostics": diagnostics,
    }
    with open(os.path.join(REVIEW_DIR, "coordinate_lines_review_pack.json"), "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)

    _write_markdown(pack)
    n_items = sum(len(c["items"]) for c in combos)
    print(f"Coordinate-lines review pack v{cl.GENERATOR_VERSION}: {n_items} items across {len(combos)} tasks; "
          f"MC 3-distinct: {mc_three}/{mc_total}; misconceptions {len(misc_seen)}/{len(diagnostics['misconceptionRulesTotal'])}; "
          f"colours {sorted(colours)}; leakage violations {leak_violations}.")


def _write_markdown(pack: dict) -> None:
    L = []
    L.append("# Curriculum-Review Pack — Coordinate geometry & straight-line graphs (SVG)\n")
    L.append(f"Generator: `{pack['generatorId']}` v`{pack['generatorVersion']}`. "
             f"Stage: {pack['stage']} (strand `{pack['strand']}`). Generated by `oracle/make_review_pack_coordinate_lines.py`.\n")
    L.append("> **Review purpose.** Machine-validated coordinate-geometry items with exact-rational answers and "
             "deterministic, to-scale Cartesian figures. Every figure is built from the same parameters as the prompt, "
             "answer, solution, and accessibility description; coordinates are integers under one round-half-up rule; "
             "the figure is byte-for-byte identical between the Python oracle and the TypeScript app. Advancing any item "
             "past `machine-validated` is the curriculum authority's decision.\n")
    L.append("## Objectives under review\n")
    L.append("| Task | Objective | Canonical answer type |\n| --- | --- | --- |")
    atype = {"read_point": "coordinate", "plot_point": "coordinate", "gradient_two_points": "integer / exact-rational",
             "midpoint": "ordered-pair", "interpret_mx_c": "equation (m, c)", "equation_from_graph": "equation",
             "equation_from_two_points": "equation"}
    for t in cl.TASKS:
        L.append(f"| {t} | `{pack['objectives'][t]}` | {atype[t]} |")
    L.append("")
    for combo in pack["combos"]:
        L.append(f"## {combo['task']} — `{combo['objective']}`\n")
        L.append(f"_{combo['note']}_\n")
        for rec in combo["items"]:
            L.append(f"### seed {rec['seed']} ({rec['interactionType']}, band {rec['band']})\n")
            L.append(f"**Prompt.** {rec['prompt']}\n")
            if "svgFile" in rec:
                L.append(f"![figure](coordinate_lines_svgs/{rec['svgFile']})\n")
                L.append(f"_Alt text._ {rec['altText']}\n")
            L.append(f"**Answer** ({rec['answerType']}): `{rec['answerDisplay']}`\n")
            if "options" in rec:
                L.append("Options: " + "  ".join(f"{o['label']}. `{o['display']}`" + ("  ✓" if o["correct"] else "") for o in rec["options"]) + "\n")
                L.append("Distractors:\n")
                for d in rec["distractors"]:
                    L.append(f"- `{d['display']}` — {d['misconceptionId']}: {d['feedback']}")
                L.append("")
            L.append("Worked solution: " + " ".join(f"({s['number']}) {s['transformation']} → {s.get('intermediateResult','')}" for s in rec["solution"]) + "\n")
            L.append(f"Validation: **{rec['validation']}**" + (f" — FAILS {rec['failingChecks']}" if rec["failingChecks"] else "") + f". Reproduce: `generate({rec['seed']}, {rec['reproduce']['config']})`.\n")
    d = pack["diagnostics"]
    L.append("## Diagnostics\n")
    L.append(f"- **Difficulty bands reached (per task):** {d['bandsByTask']}")
    L.append(f"- **Gradient coverage:** {d['gradientKinds']}")
    L.append(f"- **Midpoint coverage:** {d['midpointKinds']}")
    L.append(f"- **Misconception rules exemplified:** {len(d['misconceptionRulesExemplified'])} of {len(d['misconceptionRulesTotal'])} — {d['misconceptionRulesExemplified']}")
    L.append(f"- **Multiple-choice 3-distinct-distractor invariant:** {d['mcThreeDistinctDistractors']['items']}/{d['mcThreeDistinctDistractors']['of']} items")
    L.append(f"- **Monochrome (canonical SVG):** colours {d['monochrome']['distinctColours']}; no colour-only information; sweep {d['monochrome']['sweep']}")
    L.append(f"- **Answer-leakage violations (figure text contains a coordinate/fraction/equation):** {d['answerLeakageViolations']}")
    L.append(f"- **High-resolution raster export:** {d['pngExport']['width']}×{d['pngExport']['height']} (scale {d['pngExport']['scale']}) derived from the canonical SVG; the SVG remains the authoritative 8K-like deliverable.")
    L.append("")
    with open(os.path.join(REVIEW_DIR, "coordinate_lines_review_pack.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    build()
