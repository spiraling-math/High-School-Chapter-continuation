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
    # Decomposition mode is a task-specific cell ONLY for area_composite (owner C1); perimeter items
    # never satisfy an area-decomposition cell.
    if t == "area_composite" and "decompMode" in p:
        toks.append(f"decomp:area_composite:{p['decompMode']}")
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
        if t == "area_composite":
            for mdl in info["decompositionModes"]:
                req.add(f"decomp:area_composite:{mdl}")
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
    """The shared genuinely-different + malformed evidence matrix (owner C3) — reaches all SEVEN
    codes; the 'equivalent value + correct unit' rows are NOT canonical copies."""
    ans = M._solve(item["params"]["task"], item["params"])
    rows = []
    for e in U.checker_evidence(ans):
        got = U.check_response(e["response"], ans)["code"]
        rows.append({"scenario": e["scenario"], "studentResponse": e["response"], "expectedCode": e["expectedCode"],
                     "actualCode": got, "ok": got == e["expectedCode"], "genuinelyDifferent": e["genuinelyDifferent"]})
    return rows


# Explicit cross-unit non-conversion proofs (owner C3) — answer-independent.
CONVERSION_PROOFS = [
    {"scenario": "100 cm must not be accepted for 1 m", "studentResponse": "100 cm",
     "expected": U.make_length(1, "m"), "expectedCode": "wrong-base-unit"},
    {"scenario": "10000 cm^2 must not be accepted for 1 m^2", "studentResponse": "10000 cm^2",
     "expected": U.make_area(1, "m"), "expectedCode": "wrong-base-unit"},
]


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

    # 3) Per-item records + structural feature proofs (owner C1/C3/C4).
    records = []
    feature_proofs = {"student_vs_answer_key_base_identical": True, "answer_absent_from_student": True,
                      "not_to_scale_on_hidden": True}
    all_valid = True
    area_comp_modes = set()
    perimeter_has_area_decomp_token = False
    coverage_cell_matches_method = True
    all_codes = set()
    matrix_mismatches = 0
    genuinely_diff_accepted = 0
    diag_kinds = {"numeric": set(), "unit": set(), "pedagogical": set()}
    null_numeric_records = 0
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
        for d in diagnostics:
            diag_kinds[d["kind"]].add(d["id"])
            if d["kind"] != "pedagogical" and (d["predictedResponse"] is None or d["resultCode"] is None):
                null_numeric_records += 1
        cm = _checker_matrix(item)
        for row in cm:
            all_codes.add(row["actualCode"])
            if not row["ok"]:
                matrix_mismatches += 1
            if row["genuinelyDifferent"] and row["actualCode"] == "correct":
                genuinely_diff_accepted += 1
        toks = set(_cell_tokens(item))
        if t == "perimeter_composite" and any(x.startswith("decomp:") for x in toks):
            perimeter_has_area_decomp_token = True
        if t == "area_composite":
            mode = item["params"]["decompMode"]; area_comp_modes.add(mode)
            sol = " ".join(s["transformation"] + " " + s["intermediateResult"] for s in item["solution"]["steps"])
            if (mode == "additive") != ("Add the two rectangle areas" in sol) or \
               (mode == "subtractive") != ("Subtract the missing rectangle" in sol):
                coverage_cell_matches_method = False
        records.append({
            "seed": seed, "task": t, "objectiveId": M.OBJECTIVE_BY_TASK[t],
            "interaction": "free-response", "band": item["difficulty"]["overallBand"],
            "answer": item["answer"]["display"], "measure": item["answer"]["measure"],
            "decompMode": item["params"].get("decompMode"),
            "params": item["params"], "prompt": item["prompt"]["instruction"],
            "solution": [f"{s['number']}. {s['transformation']}: {s['intermediateResult']}" for s in item["solution"]["steps"]],
            "diagnostics": [{"id": d["id"], "kind": d["kind"], "predicted": d["predictedResponse"],
                             "code": d["resultCode"], "diagnosticOnly": d.get("diagnosticOnly", False),
                             "observableError": d["observableError"], "feedback": d["feedback"]} for d in diagnostics],
            "checkerMatrix": cm,
            "validation": v["status"], "checks": checks,
            "studentSvg": item["media"][0]["svg"], "answerKeySvg": item["media"][0]["spec"]["answerKeySvg"],
            "notToScale": item["media"][0]["spec"]["notToScale"],
            "reproduce": f"python -c \"import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate({seed},task='{t}')))\"",
        })

    no_conversion = all(U.check_response(c["studentResponse"], c["expected"])["code"] == c["expectedCode"] for c in CONVERSION_PROOFS)
    feature_proofs.update({
        "area_composite_additive_exemplar_present": "additive" in area_comp_modes,
        "area_composite_subtractive_exemplar_present": "subtractive" in area_comp_modes,
        "decomposition_coverage_task_specific": any(c.startswith("decomp:area_composite:") for c in required) and not any(c in ("decomp:additive", "decomp:subtractive") for c in required),
        "perimeter_items_not_in_area_decomposition_cells": not perimeter_has_area_decomp_token,
        "coverage_cell_matches_worked_method": coverage_cell_matches_method,
        "all_seven_checker_codes_reached": set(U.RESULT_CODES) <= all_codes,
        "checker_matrix_no_mismatch": matrix_mismatches == 0,
        "genuinely_different_forms_accepted": genuinely_diff_accepted > 0,
        "no_cross_unit_conversion": no_conversion,
        "no_null_numeric_diagnostic_records": null_numeric_records == 0,
    })

    # 4) Coverage matrix.
    matrix = [{"cell": tok, "covered": (n := sum(1 for (_k, it) in chosen if tok in set(_cell_tokens(it)))) > 0, "items": n}
              for tok in sorted(required)]

    checker_summary = {
        "codesReached": sorted(all_codes), "allSevenReached": set(U.RESULT_CODES) <= all_codes,
        "matrixMismatches": matrix_mismatches, "genuinelyDifferentAccepted": genuinely_diff_accepted,
        "crossUnitConversionPerformed": not no_conversion,
        "conversionProofs": [{"scenario": c["scenario"], "studentResponse": c["studentResponse"],
                              "expected": U.format_quantity(c["expected"]), "expectedCode": c["expectedCode"],
                              "actualCode": U.check_response(c["studentResponse"], c["expected"])["code"]} for c in CONVERSION_PROOFS],
    }
    diagnostic_summary = {"numericRules": sorted(diag_kinds["numeric"]), "unitRules": sorted(diag_kinds["unit"]),
                          "pedagogicalNotes": sorted(diag_kinds["pedagogical"]), "nullNumericRecords": null_numeric_records}

    pack = {
        "generatorId": M.GENERATOR_ID, "generatorVersion": M.GENERATOR_VERSION,
        "validatorVersion": M.VALIDATOR_VERSION, "interaction": "free-response",
        "requiredCells": len(required), "coveredCells": len(covered & required),
        "missingCells": missing, "allCovered": not missing, "allValid": all_valid,
        "items": len(records), "featureProofs": feature_proofs,
        "checkerSummary": checker_summary, "diagnosticSummary": diagnostic_summary,
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
        f"- Decomposition (task-specific, owner C1): additive area_composite exemplar = "
        f"**{feature_proofs['area_composite_additive_exemplar_present']}**; subtractive = "
        f"**{feature_proofs['area_composite_subtractive_exemplar_present']}**; perimeter items NOT counted "
        f"toward area-decomposition cells = **{feature_proofs['perimeter_items_not_in_area_decomposition_cells']}**.",
        f"- Quantity checker (owner C3): all seven codes reached = **{checker_summary['allSevenReached']}** "
        f"({', '.join(checker_summary['codesReached'])}); genuinely-different forms accepted = "
        f"**{checker_summary['genuinelyDifferentAccepted']}**; cross-unit conversion performed = "
        f"**{checker_summary['crossUnitConversionPerformed']}**.",
        f"- Diagnostics (owner C4): numeric {len(diagnostic_summary['numericRules'])}, unit "
        f"{len(diagnostic_summary['unitRules'])}, pedagogical-only {len(diagnostic_summary['pedagogicalNotes'])}; "
        f"null numeric records = **{diagnostic_summary['nullNumericRecords']}**.",
        f"- Render modes / 6000×4200 export / label-collision / student-beside-key: see the visual audit.",
        "",
        "## Coverage matrix", "",
        "| cell | covered | #items |", "| --- | --- | --- |",
    ]
    for row in matrix:
        lines.append(f"| `{row['cell']}` | {'✓' if row['covered'] else '✗ MISSING'} | {row['items']} |")
    if missing:
        lines += ["", f"**MISSING CELLS:** {', '.join('`'+m+'`' for m in missing)}"]

    # Quantity-checker matrix — prefer a RATIONAL answer so the genuinely-different decimal/unreduced
    # forms are visible (owner C3); the canonical-copy row is flagged so it is not the only "equivalent".
    rep = next((r for r in records if "/" in r["answer"]), records[0] if records else None)
    lines += ["", f"## Quantity-checker review matrix (seed {rep['seed']}, answer `{rep['answer']}`)" if rep else "## Quantity-checker review matrix", ""]
    lines += ["| scenario | student response | expected | actual | genuinely different | ok |",
              "| --- | --- | --- | --- | --- | --- |"]
    for r in (rep["checkerMatrix"] if rep else []):
        lines.append(f"| {r['scenario']} | `{r['studentResponse']}` | `{r['expectedCode']}` | `{r['actualCode']}` | "
                     f"{'yes' if r['genuinelyDifferent'] else '—'} | {'✓' if r['ok'] else '✗'} |")
    lines += ["", "### Cross-unit non-conversion proofs", "", "| scenario | response | expected | actual |", "| --- | --- | --- | --- |"]
    for c in checker_summary["conversionProofs"]:
        lines.append(f"| {c['scenario']} | `{c['studentResponse']}` | `{c['expectedCode']}` | `{c['actualCode']}` |")

    lines += ["", "## Selected items", ""]
    for r in records:
        diag_txt = ", ".join((f"{d['id']}(pedagogical-only)" if d["diagnosticOnly"]
                              else f"{d['id']}→`{d['predicted']}`({d['code']})") for d in r["diagnostics"])
        lines += [
            f"### {r['task']} — seed {r['seed']} — band {r['band']} — {r['objectiveId']}",
            f"- Prompt: {r['prompt']}",
            f"- Answer: **{r['answer']}** (measure: {r['measure']['dimension']} {r['measure']['baseUnit']}^{r['measure']['exponent']})"
            + (f"; decomposition: **{r['decompMode']}**" if r["decompMode"] else ""),
            f"- Not to scale: {r['notToScale']}",
            "- Worked solution: " + " | ".join(r["solution"]),
            "- Diagnostics: " + diag_txt,
            f"- Validation: **{r['validation']}** ({sum(1 for v in r['checks'].values() if v=='pass')} checks pass)",
            f"- Reproduce: `{r['reproduce']}`", "",
        ]
    with open(os.path.join(REVIEW_DIR, "mensuration_review_pack.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    fp = feature_proofs
    print(f"Review pack: {len(records)} items; required cells {len(required)}; "
          f"covered {len(covered & required)}; allCovered={pack['allCovered']}; allValid={pack['allValid']}.")
    print(f"  decomposition: additive={fp['area_composite_additive_exemplar_present']} "
          f"subtractive={fp['area_composite_subtractive_exemplar_present']} task-specific={fp['decomposition_coverage_task_specific']} "
          f"perimeter-excluded={fp['perimeter_items_not_in_area_decomposition_cells']} method-match={fp['coverage_cell_matches_worked_method']}")
    print(f"  checker: all7={fp['all_seven_checker_codes_reached']} no-mismatch={fp['checker_matrix_no_mismatch']} "
          f"genuinely-different={fp['genuinely_different_forms_accepted']} no-conversion={fp['no_cross_unit_conversion']}")
    print(f"  diagnostics: no-null-numeric={fp['no_null_numeric_diagnostic_records']}")
    if missing:
        print("MISSING CELLS:", missing)
    return 0 if (pack["allCovered"] and all_valid and all(fp.values())) else 1


if __name__ == "__main__":
    raise SystemExit(main())
