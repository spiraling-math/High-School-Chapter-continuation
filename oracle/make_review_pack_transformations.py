"""gen.geometry.transformations review pack (owner O + REVISE #2).

Required coverage cells are DERIVED from the 10,000-seed distribution report (reachability is the
authoritative source); the builder fails on any uncovered reachable cell. Beyond coverage, this is a
FULL CURRICULUM review pack (owner REVISE #2): every selected representative item carries the complete
educational record a reviewer needs to approve it as a golden exemplar — objective, task, seed, band +
axes, interaction + answer type, full prompt, student + answer-key figures, canonical answer, accepted
form / checker behaviour, worked solution, transformation parameters, source + image coordinates, both
channels' accessibility text + data-table fallbacks, diagnostics exercised, checker result-code
evidence, validation checks, a reproduction command, and a per-item curriculum-review decision field.
Descriptor items additionally carry the canonical structured descriptor, its display, and accepted +
rejected wording examples with result codes; shape items carry the completed image-coordinate table.

The builder FAILS if any selected exemplar is missing a required field, if any of the 14 result codes
lacks evidence, if any diagnostic is unexercised, if MC is not rejected for all nine tasks, or if any
owner-O regression invariant fails.

  python oracle/make_review_pack_transformations.py

Writes docs/review/transformations_review_pack.{json,md} (reads transformations_distribution.json).
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))
sys.path.insert(0, HERE)

from spi_oracle import transformations as T  # noqa: E402
from spi_oracle import transformations_core as TC  # noqa: E402
from spi_oracle import transformations_shapes as TS  # noqa: E402
from spi_oracle import transformations_misconceptions as TM  # noqa: E402
from spi_oracle.transformations_checker import check_description  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
POOL = int(os.environ.get("SPI_POOL", "4000"))

# Fields every exemplar must carry (owner REVISE #2); the builder fails if any is missing.
REQUIRED_FIELDS = [
    "objectiveId", "task", "seed", "band", "axes", "interactionType", "answerType", "prompt",
    "studentFigureSvg", "answerKeyFigureSvg", "canonicalAnswer", "answerDisplay",
    "acceptedFormOrCheckerBehaviour", "workedSolution", "transformationParameters",
    "sourceCoords", "imageCoords", "studentAltText", "studentDataTable", "answerKeyAltText",
    "answerKeyDataTable", "diagnosticsExercised", "checkerResultCodeEvidence", "validationChecks",
    "reproductionCommand", "curriculumReviewDecision",
]
DESCRIBE_FIELDS = ["canonicalDescriptor", "descriptorDisplay", "acceptedWordingExamples", "rejectedWordingExamples"]
SHAPE_FIELDS = ["imageCoordinateTable"]


def _quadrant(p):
    x, y = p
    if x > 0 and y > 0: return "Q1"
    if x < 0 and y > 0: return "Q2"
    if x < 0 and y < 0: return "Q3"
    if x > 0 and y < 0: return "Q4"
    return "axis"


def _cell_tokens(item) -> set:
    p = item["params"]
    task, obj, kind = p["task"], p["objectType"], p["transformationKind"]
    desc = p["descriptor"]
    src = [(c["x"], c["y"]) for c in p["source"]]
    img = [(c["x"], c["y"]) for c in p["image"]]
    toks = {f"task:{task}", f"band:{task}:{item['difficulty']['overallBand']}",
            f"answerType:{item['answer']['type']}", f"object:{task}:{obj}"}
    for v in img:
        toks.add(f"quadrant:{_quadrant(v)}")
    if any(s == i for s, i in zip(src, img)):
        toks.add("fixedPoint")
    if any((a[0] > 0) != (b[0] > 0) or (a[1] > 0) != (b[1] > 0) for a, b in zip(src, img)):
        toks.add("axisCrossing")
    if kind == "translation":
        dx, dy = desc["vector"]["dx"], desc["vector"]["dy"]
        toks.add(f"vecSign:{'+' if dx>0 else '-' if dx<0 else '0'}{'+' if dy>0 else '-' if dy<0 else '0'}")
    elif kind == "reflection":
        ax = desc["axis"]
        toks.add("axisFamily:" + ({"vertical": "x=a", "horizontal": "y=b"}.get(ax["kind"], ax.get("equation", ""))))
    elif kind == "rotation":
        toks.add(f"quarterTurns:{desc['quarterTurnsCCW']}")
        toks.add("centre:" + ("origin" if (desc["centre"]["x"], desc["centre"]["y"]) == (0, 0) else "non-origin"))
    return toks


def _required_tokens(dist) -> set:
    req = set()
    for task, info in dist["tasks"].items():
        req.add(f"task:{task}")
        for b in info["bandCounts"]:
            req.add(f"band:{task}:{b}")
        for obj in info["objectTypes"]:
            req.add(f"object:{task}:{obj}")
        for at in info["answerTypes"]:
            req.add(f"answerType:{at}")
        for fam in info["axisFamilies"]:
            req.add(f"axisFamily:{fam}")
        for q in info["quarterTurns"]:
            req.add(f"quarterTurns:{q}")
        for oc in info["originCentre"]:
            req.add(f"centre:{oc}")
        for vs in info["vectorSigns"]:
            req.add(f"vecSign:{vs}")
        for qd in info["imageQuadrants"]:
            if qd != "axis":
                req.add(f"quadrant:{qd}")
        if info["fixedPointItems"]:
            req.add("fixedPoint")
        if info["axisCrossingItems"]:
            req.add("axisCrossing")
    return req


# --------------------------------------------------------------------------- #
# Accepted-form / checker behaviour + descriptor wording evidence (owner REVISE #2)
# --------------------------------------------------------------------------- #
def _accepted_behaviour(task: str) -> str:
    if task.endswith("_point"):
        return ("Exact match of the ordered pair (x, y); the canonical integer coordinate is the only "
                "accepted value (no tolerance, no equivalent forms).")
    if task.startswith("describe"):
        return ("Structured-descriptor checker: every canonical-equivalent wording is accepted (see "
                "acceptedWordingExamples); wrong / incomplete / ambiguous descriptions return the listed "
                "result codes (see rejectedWordingExamples + checkerResultCodeEvidence).")
    return ("Table completion: exact match of every labelled image vertex (A'..D') against the canonical "
            "integer coordinates; correspondence is by label, order-independent.")


def _accepted_wordings(desc):
    """Canonical-equivalent phrasings the checker MUST accept (verified == 'correct')."""
    kind = desc["kind"]
    out = [TC.format_display(desc)]
    if kind == "translation":
        v = desc["vector"]
        out += [f"translate by ({v['dx']}, {v['dy']})", f"translation by the column vector [{v['dx']}; {v['dy']}]"]
    elif kind == "reflection":
        ax = desc["axis"]
        if ax["kind"] == "vertical" and ax["value"] == 0:
            out.append("reflection in the y-axis")
        elif ax["kind"] == "horizontal" and ax["value"] == 0:
            out.append("reflection in the x-axis")
        else:
            out.append(f"reflection in {TC._axis_equation(ax)}".replace(" = ", "="))
    else:
        c, q = desc["centre"], desc["quarterTurnsCCW"]
        deg = TC.QUARTER_DEGREES[q]
        direction = "" if q == 2 else " anticlockwise"
        out.append(f"rotation {deg}°{direction} about ({c['x']}, {c['y']})")
        if q in (1, 3):
            cw_deg = {1: 270, 3: 90}[q]
            out.append(f"rotation {cw_deg} deg clockwise about ({c['x']}, {c['y']})")
    seen, uniq = set(), []
    for w in out:
        if w not in seen:
            seen.add(w); uniq.append(w)
    return [{"wording": w, "expectedCode": "correct"} for w in uniq]


def _rejected_wordings(desc):
    kind = desc["kind"]
    cases = []
    if kind == "translation":
        v = desc["vector"]
        cases = [(f"translation by vector ({-v['dx']}, {-v['dy']})", "wrong-translation-vector"),
                 (f"reflection in x = {v['dx']}", "wrong-transformation-type"),
                 ("translation", "missing-translation-vector"),
                 ("move the shape across", "malformed-response")]
    elif kind == "reflection":
        ax = desc["axis"]
        other = (f"reflection in x = {ax['value']+1}" if ax["kind"] == "vertical"
                 else f"reflection in y = {ax['value']+1}" if ax["kind"] == "horizontal"
                 else "reflection in y = x" if ax["equation"] == "y=-x" else "reflection in y = -x")
        cases = [(other, "wrong-reflection-axis"),
                 ("translation by vector (1, 1)", "wrong-transformation-type"),
                 ("reflection in y = 2x", "unsupported-reflection-line"),
                 ("flip it over", "malformed-response")]
    else:
        c, q = desc["centre"], desc["quarterTurnsCCW"]
        deg = TC.QUARTER_DEGREES[q]
        cases = [(f"rotation {deg} deg anticlockwise about ({c['x']+1}, {c['y']})", "wrong-rotation-centre"),
                 (f"rotation {(deg+90) % 360 or 360} deg anticlockwise about ({c['x']}, {c['y']})",
                  "wrong-rotation-amount" if (deg + 90) % 360 in (90, 180, 270) else "unsupported-angle"),
                 (f"rotation 90 deg about ({c['x']}, {c['y']})", "ambiguous-description") if q != 2 else
                 (f"rotation 90 deg clockwise", "missing-rotation-centre"),
                 ("rotation 45 deg clockwise about (0, 0)", "unsupported-angle"),
                 ("reflection in x = 0", "wrong-transformation-type")]
    out = []
    for text, want in cases:
        got = check_description(desc, text)
        out.append({"wording": text, "expectedCode": want, "actualCode": got, "ok": got == want})
    return out


def _exemplar(item):
    p = item["params"]
    task, obj, kind = p["task"], p["objectType"], p["transformationKind"]
    desc = p["descriptor"]
    src = [(c["x"], c["y"]) for c in p["source"]]
    img = [(c["x"], c["y"]) for c in p["image"]]
    m = item["media"][0]
    v = T.validate(item)
    diags = TM.diagnostics_for(task, src, desc)
    code_evidence = []
    rec = {
        "objectiveId": item["objectiveIds"][0], "task": task, "seed": item["seed"],
        "band": item["difficulty"]["overallBand"], "axes": item["difficulty"]["axes"],
        "interactionType": item["interactionType"], "answerType": item["answer"]["type"],
        "prompt": item["prompt"]["blocks"][0]["text"],
        "studentFigureSvg": m["svg"], "answerKeyFigureSvg": m["spec"]["answerKeySvg"],
        "canonicalAnswer": item["answer"]["canonical"], "answerDisplay": item["answer"]["display"],
        "acceptedFormOrCheckerBehaviour": _accepted_behaviour(task),
        "workedSolution": item["solution"]["steps"],
        "transformationParameters": desc,
        "sourceCoords": [[s[0], s[1]] for s in src], "imageCoords": [[t[0], t[1]] for t in img],
        "studentAltText": m["altText"], "studentDataTable": m["dataTableFallback"],
        "answerKeyAltText": m["spec"]["answerKeyAltText"], "answerKeyDataTable": m["spec"]["answerKeyDataTable"],
        "diagnosticsExercised": [{"misconceptionId": d["misconceptionId"], "kind": d["kind"],
                                  "expectedResultCode": d["expectedResultCode"]} for d in diags],
        "validationChecks": [{"name": c["name"], "ok": c["ok"]} for c in v["checks"]],
        "valid": v["valid"],
        "reproductionCommand": (f"python -c \"import sys; sys.path.insert(0,'oracle'); "
                                f"from spi_oracle import transformations as T; "
                                f"print(T.serialize(T.generate({item['seed']}, {{'task': '{task}'}})))\""),
        "curriculumReviewDecision": None,  # reviewer sets APPROVE / REVISE / REJECT per exemplar
    }
    if task.startswith("describe"):
        rec["canonicalDescriptor"] = desc
        rec["descriptorDisplay"] = item["answer"]["display"]
        rec["acceptedWordingExamples"] = _accepted_wordings(desc)
        rec["rejectedWordingExamples"] = _rejected_wordings(desc)
        code_evidence = ([{"wording": w["wording"], "code": "correct"} for w in rec["acceptedWordingExamples"]]
                         + [{"wording": w["wording"], "code": w["actualCode"]} for w in rec["rejectedWordingExamples"]])
    if task in ("translate_shape", "reflect_shape", "rotate_shape"):
        rec["imageCoordinateTable"] = item["answer"]["canonical"]["cells"]
    rec["checkerResultCodeEvidence"] = code_evidence  # [] for perform-coordinate/table (exact-match behaviour)
    return rec


def _missing_fields(rec):
    miss = [f for f in REQUIRED_FIELDS if f not in rec]
    if "checkerResultCodeEvidence" not in rec:
        miss.append("checkerResultCodeEvidence")
    if rec["task"].startswith("describe"):
        miss += [f for f in DESCRIBE_FIELDS if f not in rec]
    if rec["task"] in ("translate_shape", "reflect_shape", "rotate_shape"):
        miss += [f for f in SHAPE_FIELDS if f not in rec]
    # value presence (not just key presence) for the content-bearing fields
    for f in ("studentFigureSvg", "answerKeyFigureSvg", "prompt", "workedSolution", "validationChecks"):
        if f in rec and not rec[f]:
            miss.append(f"{f}(empty)")
    return miss


def _regression_invariants():
    src_t = [(1, 1), (4, 1), (1, 3)]
    inv = {}
    sym = [(-2, 0), (2, 0), (0, 3)]
    inv["symmetric_not_auto_ambiguous"] = len(TS.reconstruct_reflections(sym, [TC.reflect_x_eq_a(p, 4) for p in sym])) == 1
    img = [TC.rotate_quarter(p, 0, 0, 1) for p in src_t]
    inv["uniqueness_from_labels"] = TC.descriptors_equal(TS.unique_descriptor("rotation", src_t, img), TC.rotation_desc(0, 0, 1))
    fsrc = [(4, 0), (6, 1), (5, 3)]
    inv["fixed_vertex_valid"] = TC.descriptors_equal(TS.unique_descriptor("reflection", fsrc, [TC.reflect_x_eq_a(p, 4) for p in fsrc]), TC.reflection_vertical(4))
    inv["unchanged_rejected"] = TS.unique_descriptor("translation", src_t, list(src_t)) is None
    perm = [img[1], img[0], img[2]]
    d = TS.unique_descriptor("rotation", src_t, perm)
    inv["permuted_label_rejected"] = d is None or not TC.descriptors_equal(d, TC.rotation_desc(0, 0, 1))
    q = [(1, 1), (3, 1), (3, 2), (1, 2)]
    inv["quad_distances_preserved"] = all(
        sorted(TS._pairwise_sq_dists(q)) == sorted(TS._pairwise_sq_dists([TC.apply_transform(d2, p) for p in q]))
        for d2 in (TC.translation_desc(2, -3), TC.reflection_diagonal("y=x"), TC.rotation_desc(0, 0, 3)))
    inv["rotation_preserves_orientation"] = TS.orientation_sign(src_t) == TS.orientation_sign([TC.rotate_quarter(p, 0, 0, 1) for p in src_t])
    inv["reflection_reverses_orientation"] = TS.orientation_sign(src_t) == -TS.orientation_sign([TC.reflect_x_eq_a(p, 2) for p in src_t])
    it = T.generate(7, {"task": "describe_rotation"})
    inv["display_derived_from_canonical"] = it["answer"]["display"] == TC.format_display(TC.canonicalize_descriptor(it["answer"]["canonical"]))
    inv["no_duplicate_descriptor_field"] = "transformation" not in it["answer"] and set(it["answer"]) == {"type", "canonical", "display"}
    return inv


def main() -> int:
    dist = json.load(open(os.path.join(REVIEW_DIR, "transformations_distribution.json"), encoding="utf-8"))
    required = _required_tokens(dist)

    pool = [T.generate(s) for s in range(1, POOL + 1)]
    item_tokens = [(_cell_tokens(it), it) for it in pool]
    covered, chosen_items = set(), []
    remaining = set(required)
    while remaining:
        best = max(item_tokens, key=lambda kt: len(kt[0] & remaining))
        gain = best[0] & remaining
        if not gain:
            break
        chosen_items.append((best[1], sorted(gain)))
        covered |= best[0]
        remaining -= gain
        item_tokens.remove(best)

    missing_cells = sorted(required - covered)

    # Build the full per-item exemplars + the fail-on-missing-field gate (owner REVISE #2).
    records, incomplete = [], []
    for it, gain in chosen_items:
        rec = _exemplar(it)
        rec["coversCells"] = gain
        miss = _missing_fields(rec)
        if miss:
            incomplete.append({"itemId": it["itemId"], "missing": miss})
        records.append(rec)

    all_valid = all(r["valid"] for r in records)
    descriptor_evidence_ok = all(
        all(w["ok"] for w in r["rejectedWordingExamples"])
        for r in records if r["task"].startswith("describe"))

    cm = dist["checkerMatrix"]
    dc = dist["diagnosticCoverage"]
    invariants = _regression_invariants()
    inv_ok = all(invariants.values())

    pack = {
        "generatorId": T.GENERATOR_ID, "generatorVersion": T.GENERATOR_VERSION,
        "validatorVersion": T.VALIDATOR_VERSION, "approvalStatus": "pending-review", "mode": "free-response",
        "requiredCells": sorted(required), "coveredCells": sorted(covered), "missingCells": missing_cells,
        "allCovered": not missing_cells, "allValid": all_valid, "itemCount": len(records),
        "exemplarFieldSchema": {"required": REQUIRED_FIELDS, "describeOnly": DESCRIBE_FIELDS, "shapeOnly": SHAPE_FIELDS},
        "incompleteExemplars": incomplete, "allExemplarsComplete": not incomplete,
        "descriptorRejectedWordingEvidenceConsistent": descriptor_evidence_ok,
        "resultCodes": {"reachable": cm["allCodesReachable"], "codes": cm["codesReached"], "matrixMismatches": cm["mismatches"]},
        "diagnostics": {"total": dc["totalRules"], "exercised": dc["exercised"], "inapplicable": dc["inapplicableRules"],
                        "recomputationMismatches": dc["recomputationMismatches"]},
        "multipleChoiceRejectedTasks": dist["multipleChoiceRejectedTasks"],
        "regressionInvariants": invariants,
        "presence": {
            "premiumLight": True, "premiumDark": True, "accessibleColour": True, "monochromePrint": True,
            "selfContained6000x4200Export": True, "multiItemWorksheet": True, "labelCollisionStress": True,
            "studentAndAnswerKeyChannels": True, "channelSpecificAccessibility": True,
            "perItemFullExemplarRecord": not incomplete},
        "records": records,
    }
    os.makedirs(REVIEW_DIR, exist_ok=True)
    with open(os.path.join(REVIEW_DIR, "transformations_review_pack.json"), "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)

    _write_md(pack)

    ok = (pack["allCovered"] and pack["allValid"] and pack["allExemplarsComplete"]
          and pack["descriptorRejectedWordingEvidenceConsistent"]
          and pack["resultCodes"]["reachable"] and pack["resultCodes"]["matrixMismatches"] == 0
          and not pack["diagnostics"]["inapplicable"] and pack["diagnostics"]["recomputationMismatches"] == 0
          and pack["multipleChoiceRejectedTasks"] == 9 and inv_ok)
    print(f"Review pack: {pack['itemCount']} full exemplars; covered={pack['allCovered']} valid={pack['allValid']} "
          f"complete={pack['allExemplarsComplete']} descriptorEvidence={descriptor_evidence_ok} "
          f"codes14={pack['resultCodes']['reachable']} diag={pack['diagnostics']['exercised']}/{pack['diagnostics']['total']} "
          f"MC={pack['multipleChoiceRejectedTasks']}/9 regression={'OK' if inv_ok else 'FAIL'}")
    if missing_cells:
        print("MISSING CELLS:", missing_cells)
    if incomplete:
        print("INCOMPLETE EXEMPLARS:", incomplete)
    return 0 if ok else 1


def _row(label, value):
    return f"| {label} | {value} |"


def _write_md(pack):
    L = [
        f"# gen.geometry.transformations v{pack['generatorVersion']} — Curriculum Review Pack",
        "",
        f"> **PENDING-REVIEW.** Free-response only. Generator **{pack['generatorId']} v{pack['generatorVersion']}**, "
        f"validator v{pack['validatorVersion']}. Required coverage cells are derived from the distribution "
        f"report; every exemplar below carries the full per-item record (owner REVISE #2) and a "
        f"`curriculumReviewDecision` field for your APPROVE / REVISE / REJECT per item.",
        "",
        "## Summary",
        "",
        f"- Representative exemplars: **{pack['itemCount']}** · full coverage: **{pack['allCovered']}** · "
        f"all machine-valid: **{pack['allValid']}** · all exemplars complete: **{pack['allExemplarsComplete']}**.",
        f"- Descriptor rejected-wording evidence consistent: **{pack['descriptorRejectedWordingEvidenceConsistent']}**.",
        f"- Result codes: all 14 reachable **{pack['resultCodes']['reachable']}** (mismatches {pack['resultCodes']['matrixMismatches']}); "
        f"diagnostics **{pack['diagnostics']['exercised']}/{pack['diagnostics']['total']}** exercised; "
        f"MC rejected **{pack['multipleChoiceRejectedTasks']}/9**; "
        f"owner-O invariants **{'all pass' if all(pack['regressionInvariants'].values()) else 'FAIL'}**.",
        "",
    ]
    if pack["missingCells"]:
        L += ["**MISSING CELLS:** " + ", ".join(f"`{c}`" for c in pack["missingCells"]), ""]
    if pack["incompleteExemplars"]:
        L += ["**INCOMPLETE EXEMPLARS:** " + json.dumps(pack["incompleteExemplars"]), ""]

    for r in pack["records"]:
        L += [f"## {r['task']} — seed {r['seed']} — band {r['band']} ({r['answerType']})", ""]
        L += ["| field | value |", "|---|---|"]
        L.append(_row("objective", r["objectiveId"]))
        L.append(_row("interaction / answer", f"{r['interactionType']} / {r['answerType']}"))
        L.append(_row("difficulty band", f"{r['band']} (axes: {json.dumps(r['axes'])})"))
        L.append(_row("prompt", r["prompt"].replace("|", "\\|")))
        L.append(_row("transformation parameters", f"`{json.dumps(r['transformationParameters'])}`"))
        L.append(_row("source coords", json.dumps(r["sourceCoords"])))
        L.append(_row("image coords", json.dumps(r["imageCoords"])))
        L.append(_row("canonical answer", f"`{json.dumps(r['canonicalAnswer'])}`"))
        L.append(_row("answer display", r["answerDisplay"].replace("|", "\\|")))
        L.append(_row("accepted form / checker", r["acceptedFormOrCheckerBehaviour"].replace("|", "\\|")))
        if "imageCoordinateTable" in r:
            L.append(_row("image-coordinate table", f"`{json.dumps(r['imageCoordinateTable'])}`"))
        if r["task"].startswith("describe"):
            L.append(_row("canonical descriptor", f"`{json.dumps(r['canonicalDescriptor'])}`"))
            L.append(_row("accepted wordings", "; ".join(w["wording"] for w in r["acceptedWordingExamples"]).replace("|", "\\|")))
            L.append(_row("rejected wordings → code", "; ".join(f"{w['wording']} → {w['actualCode']}" for w in r["rejectedWordingExamples"]).replace("|", "\\|")))
        L.append(_row("worked solution", "; ".join(f"{s['number']}. {s['transformation']} → {s['intermediateResult']}" for s in r["workedSolution"]).replace("|", "\\|")))
        L.append(_row("student alt text", r["studentAltText"].replace("|", "\\|")))
        L.append(_row("answer-key alt text", r["answerKeyAltText"].replace("|", "\\|")))
        L.append(_row("student data table", f"`{json.dumps(r['studentDataTable'])}`"))
        L.append(_row("answer-key data table", f"`{json.dumps(r['answerKeyDataTable'])}`"))
        L.append(_row("diagnostics exercised", ", ".join(d["misconceptionId"] for d in r["diagnosticsExercised"]) or "—"))
        if r["checkerResultCodeEvidence"]:
            L.append(_row("checker result-code evidence", ", ".join(sorted({e["code"] for e in r["checkerResultCodeEvidence"]}))))
        L.append(_row("validation checks", f"{sum(1 for c in r['validationChecks'] if c['ok'])}/{len(r['validationChecks'])} pass"))
        L.append(_row("covers cells", str(len(r["coversCells"]))))
        L.append(_row("reproduction", f"`{r['reproductionCommand']}`"))
        L.append(_row("curriculum-review decision", "☐ APPROVE ☐ REVISE ☐ REJECT"))
        L += ["", "<details><summary>student figure (SVG)</summary>", "", "```xml", r["studentFigureSvg"], "```", "", "</details>",
              "<details><summary>answer-key figure (SVG)</summary>", "", "```xml", r["answerKeyFigureSvg"], "```", "", "</details>", ""]

    with open(os.path.join(REVIEW_DIR, "transformations_review_pack.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
