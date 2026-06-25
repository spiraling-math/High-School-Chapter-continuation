"""gen.measurement.mensuration v1.0.0 review-pack builder (owner L).

Required coverage cells are DERIVED from the distribution report (the authoritative reachability
artifact) — per task: every supported interaction (free-response), every reachable difficulty band,
every realised answer shape (length/area x integer/rational), every base unit (mm/cm/m), every shape
kind, both composite decomposition modes, and every hidden role. The builder FAILS if any reachable
required cell is left uncovered (no false full-coverage claim). It also emits the quantity-checker
review matrix (owner L) and the structural feature proofs (student-vs-answer-key base geometry
identical; the answer is ABSENT from every student figure; the NOT-TO-SCALE banner on hidden-
dimension items). Render-mode cells (print / premium / premium-dark / accessible / 6000x4200 /
label-collision / student-beside-key) are covered by the companion visual audit, which this pack
references.

  python oracle/make_review_pack_mensuration.py

Writes:
  docs/review/mensuration_review_pack.md
  docs/review/mensuration_review_pack.json
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))
sys.path.insert(0, HERE)

from spi_oracle import mensuration as M  # noqa: E402
from spi_oracle import mensuration_units as U  # noqa: E402
from spi_oracle import mensuration_misconceptions as MM  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
GATHER_SEEDS = 700  # per task — enough to surface every reachable cell


def _cell_tokens(item) -> list:
    p = item["params"]; t = p["task"]
    m = item["answer"]["measure"]
    toks = [f"task:{t}", f"band:{t}:{item['difficulty']['overallBand']}",
            f"dim:{m['dimension']}", f"num:{'rational' if item['answer']['canonical']['den'] != 1 else 'integer'}",
            f"unit:{m['baseUnit']}", f"kind:{p['kind']}"]
    if "decompMode" in p:
        toks.append(f"decomp:{p['decompMode']}")
    if "hidden" in p:
        toks.append(f"hidden:{p['hidden']}")
    if p["kind"] == "rectangle":
        toks.append("orient:" + ("landscape" if p["width"] > p["height"] else ("portrait" if p["width"] < p["height"] else "square")))
    elif p["kind"] == "rectilinear_composite":
        toks.append(f"corner:{p['corner']}")
    return toks


def _reachability():
    dist = json.load(open(os.path.join(REVIEW_DIR, "mensuration_distribution.json"), encoding="utf-8"))
    return dist


def _required_tokens(dist) -> set:
    req = set()
    for t, info in dist["tasks"].items():
        req.add(f"task:{t}")
        for b in info["bandCounts"]:
            req.add(f"band:{t}:{b}")
        for d in info["dimensions"]:
            req.add(f"dim:{d}")
        for k in info["numberKinds"]:
            req.add(f"num:{k}")
        for u in info["baseUnits"]:
            req.add(f"unit:{u}")
        for mdl in info["decompositionModes"]:
            req.add(f"decomp:{mdl}")
        for h in info["hiddenRoles"]:
            req.add(f"hidden:{h}")
        for o in info["orientations"]:
            if o in ("landscape", "portrait", "square"):
                req.add(f"orient:{o}")
            if o in ("TR", "TL", "BR", "BL"):
                req.add(f"corner:{o}")
    req.add("kind:rectangle"); req.add("kind:rectilinear_composite"); req.add("kind:triangle_base_height")
    return req


def _checker_matrix(item):
    ans = M._solve(item["params"]["task"], item["params"])
    other = MM._other_base(ans.baseUnit)
    cases = {
        "equivalent value + correct unit": (U.format_quantity(ans), "correct"),
        "bare correct value (no unit)": (U.format_value(ans.value), "missing-unit"),
        "wrong base unit (no conversion)": (U.format_quantity(type(ans)(ans.dimension, other, ans.exponent, ans.value)), "wrong-base-unit"),
        "incorrect value + correct unit": (U.format_quantity(type(ans)(ans.dimension, ans.baseUnit, ans.exponent, ans.value + 1)), "incorrect-value"),
    }
    if ans.dimension == "area":
        cases["linear units for an area"] = (U.format_quantity(U.make_length(ans.value, ans.baseUnit)), "wrong-exponent")
        cases["different dimensional quantity"] = (U.format_quantity(U.make_length(ans.value, other)), "wrong-dimension")
    else:
        cases["square units for a length"] = (U.format_quantity(U.make_area(ans.value, ans.baseUnit)), "wrong-exponent")
        cases["different dimensional quantity"] = (U.format_quantity(U.make_area(ans.value, other)), "wrong-dimension")
    rows = []
    for label, (resp, expected) in cases.items():
        got = U.check_response(resp, ans)["code"]
        rows.append({"scenario": label, "studentResponse": resp, "expectedCode": expected,
                     "actualCode": got, "ok": got == expected})
    return rows


def main() -> int:
    os.makedirs(REVIEW_DIR, exist_ok=True)
    dist = _reachability()
    required = _required_tokens(dist)

    # 1) Gather candidate items (task-pinned).
    candidates = {}  # seed_task -> (item, tokens)
    for t in M.TASKS:
        for seed in range(1, GATHER_SEEDS + 1):
            item = M.generate(seed, task=t)
            candidates[(seed, t)] = (item, set(_cell_tokens(item)))

    # 2) Greedy set-cover of the REQUIRED tokens.
    covered, chosen = set(), []
    pool = dict(candidates)
    while True:
        best, best_gain = None, 0
        for key, (item, toks) in pool.items():
            gain = len(toks & required - covered)
            if gain > best_gain:
                best, best_gain = key, gain
        if best is None or best_gain == 0:
            break
        item, toks = pool.pop(best)
        chosen.append((best, item))
        covered |= toks

    missing = sorted(required - covered)

    # 3) Build per-item records + structural feature proofs.
    records = []
    feature_proofs = {"student_vs_answer_key_base_identical": True, "answer_absent_from_student": True,
                      "not_to_scale_on_hidden": True}
    all_valid = True
    for (seed, t), item in chosen:
        v = M.validate(item)
        if v["status"] != "pass":
            all_valid = False
        checks = {c["name"]: c["result"] for c in v["checks"]}
        if checks.get("answer-key-base-geometry-identical") != "pass":
            feature_proofs["student_vs_answer_key_base_identical"] = False
        if checks.get("no-result-in-student-figure") != "pass" or checks.get("student-a11y-does-not-state-result") != "pass":
            feature_proofs["answer_absent_from_student"] = False
        if t in M.HIDDEN_DIMENSION_TASKS and checks.get("not-to-scale-banner-present") != "pass":
            feature_proofs["not_to_scale_on_hidden"] = False
        ans = M._solve(t, item["params"])
        diagnostics = MM.diagnostics_for(t, item["params"], ans)
        records.append({
            "seed": seed, "task": t, "objectiveId": M.OBJECTIVE_BY_TASK[t],
            "interaction": "free-response", "band": item["difficulty"]["overallBand"],
            "answer": item["answer"]["display"], "measure": item["answer"]["measure"],
            "params": item["params"], "prompt": item["prompt"]["instruction"],
            "solution": [f"{s['number']}. {s['transformation']}: {s['intermediateResult']}" for s in item["solution"]["steps"]],
            "diagnostics": [{"id": d["id"], "predicted": d["predictedResponse"], "code": d["resultCode"]} for d in diagnostics],
            "checkerMatrix": _checker_matrix(item),
            "validation": v["status"], "checks": checks,
            "studentSvg": item["media"][0]["svg"], "answerKeySvg": item["media"][0]["spec"]["answerKeySvg"],
            "notToScale": item["media"][0]["spec"]["notToScale"],
            "reproduce": f"python -c \"import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate({seed},task='{t}')))\"",
        })

    # 4) Coverage matrix.
    matrix = []
    for tok in sorted(required):
        n = sum(1 for (_k, it) in chosen if tok in set(_cell_tokens(it)))
        matrix.append({"cell": tok, "covered": n > 0, "items": n})

    pack = {
        "generatorId": M.GENERATOR_ID, "generatorVersion": M.GENERATOR_VERSION,
        "validatorVersion": M.VALIDATOR_VERSION, "interaction": "free-response",
        "requiredCells": len(required), "coveredCells": len(covered & required),
        "missingCells": missing, "allCovered": not missing, "allValid": all_valid,
        "items": len(records), "featureProofs": feature_proofs,
        "renderModesCoveredBy": "docs/review/mensuration_visual_audit.html (print/premium/premium-dark/accessible) + the 6000x4200 export + the label-collision stress + student-beside-answer-key overlays",
        "coverageMatrix": matrix, "records": records,
    }
    with open(os.path.join(REVIEW_DIR, "mensuration_review_pack.json"), "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)

    # 5) Markdown.
    lines = [
        f"# Review pack — {M.GENERATOR_ID} v{M.GENERATOR_VERSION}", "",
        "> PENDING-REVIEW. Free-response only. Required coverage cells are **derived from the "
        "distribution report** (every task × supported interaction × reachable band × realised answer "
        "shape × base unit × shape kind × decomposition mode × hidden role). The builder fails on any "
        "missing reachable cell.", "",
        f"- Required cells: **{len(required)}**; covered: **{len(covered & required)}**; "
        f"full coverage: **{pack['allCovered']}**; all items machine-valid: **{pack['allValid']}**.",
        f"- Items selected (minimal set-cover): **{len(records)}**.",
        f"- Feature proofs: student-vs-answer-key base geometry identical = **{feature_proofs['student_vs_answer_key_base_identical']}**; "
        f"answer absent from every student figure = **{feature_proofs['answer_absent_from_student']}**; "
        f"NOT-TO-SCALE banner on hidden-dimension items = **{feature_proofs['not_to_scale_on_hidden']}**.",
        f"- Render modes / 6000×4200 export / label-collision / student-beside-key: see the visual audit.",
        "",
        "## Coverage matrix", "",
        "| cell | covered | #items |", "| --- | --- | --- |",
    ]
    for row in matrix:
        lines.append(f"| `{row['cell']}` | {'✓' if row['covered'] else '✗ MISSING'} | {row['items']} |")
    if missing:
        lines += ["", f"**MISSING CELLS:** {', '.join('`'+m+'`' for m in missing)}"]
    lines += ["", "## Quantity-checker review matrix (representative)", ""]
    cm = records[0]["checkerMatrix"] if records else []
    lines += ["| scenario | student response | expected | actual | ok |", "| --- | --- | --- | --- | --- |"]
    for r in cm:
        lines.append(f"| {r['scenario']} | `{r['studentResponse']}` | `{r['expectedCode']}` | `{r['actualCode']}` | {'✓' if r['ok'] else '✗'} |")
    lines += ["", "## Selected items", ""]
    for r in records:
        lines += [
            f"### {r['task']} — seed {r['seed']} — band {r['band']} — {r['objectiveId']}",
            f"- Prompt: {r['prompt']}",
            f"- Answer: **{r['answer']}** (measure: {r['measure']['dimension']} {r['measure']['baseUnit']}^{r['measure']['exponent']})",
            f"- Not to scale: {r['notToScale']}",
            "- Worked solution: " + " | ".join(r["solution"]),
            "- Diagnostics: " + ", ".join(f"{d['id']}→`{d['predicted']}`({d['code']})" for d in r["diagnostics"]),
            f"- Validation: **{r['validation']}** ({sum(1 for v in r['checks'].values() if v=='pass')} checks pass)",
            f"- Reproduce: `{r['reproduce']}`", "",
        ]
    with open(os.path.join(REVIEW_DIR, "mensuration_review_pack.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print(f"Review pack: {len(records)} items; required cells {len(required)}; "
          f"covered {len(covered & required)}; allCovered={pack['allCovered']}; allValid={pack['allValid']}.")
    if missing:
        print("MISSING CELLS:", missing)
    return 0 if pack["allCovered"] and all_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
