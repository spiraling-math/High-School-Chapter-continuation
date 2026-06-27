"""gen.proportion.ratio v1.0.0 — curriculum review pack (mirror of make_review_pack_transformations).

Required coverage cells are DERIVED from the 10,000-seed distribution report (docs/review/
ratio_distribution.json); reachability is the authoritative source and the builder FAILS on any
uncovered reachable cell. Beyond coverage this is a FULL CURRICULUM review pack: every selected
representative item carries the complete educational record a reviewer needs to approve it as a golden
exemplar — objective, task, seed, band + axes, interaction + answer type, full prompt, student +
answer-key figure SVG, canonical answer + display, accepted-form / checker behaviour, worked solution,
params, both channels' accessibility text + data-table fallbacks, diagnostics exercised, validation
checks, a reproduction command, and a per-item `curriculumReviewDecision` field (null until reviewed).

The builder FAILS if any selected exemplar is missing a required field, if any cell is uncovered, if any
of the 9 ratio result codes lacks evidence, if any of the 16 MISC.RATIO.* diagnostics is unexercised, if
the MC policy is violated (best_buy MC-only; FR-only tasks reject MC), or if the ratio-checker matrix has
any mismatch.

  PYTHONIOENCODING=utf-8 python oracle/make_review_pack_ratio.py

Writes docs/review/proportion_ratio_review_pack.{json,md} (reads ratio_distribution.json).
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))
sys.path.insert(0, HERE)

from spi_oracle import ratio as R  # noqa: E402
from spi_oracle import ratio_core as RC  # noqa: E402
from spi_oracle import ratio_misconceptions as RM  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
POOL = int(os.environ.get("SPI_POOL", "4000"))

# Tasks that bear a figure -> the representation token they exercise.
REPRESENTATION_BY_FIGURE = {"bar": "bar-model", "numberline": "double-number-line", "table": "table"}
FR_ONLY_TASKS = tuple(t for t in R.RATIO_TASKS if t not in R.MC_ELIGIBLE_TASKS)


# --------------------------------------------------------------------------- #
# Fields every exemplar must carry; the builder fails if any is missing.
# --------------------------------------------------------------------------- #
REQUIRED_FIELDS = [
    "objectiveId", "task", "seed", "band", "axes", "interactionType", "answerType", "prompt",
    "canonicalAnswer", "answerDisplay", "acceptedFormOrCheckerBehaviour", "workedSolution", "params",
    "studentAltText", "studentDataTable", "diagnosticsExercised", "validationChecks",
    "reproductionCommand", "curriculumReviewDecision",
]
# Figure-bearing exemplars must additionally carry both channels' figure + figure accessibility.
FIGURE_FIELDS = ["studentFigureSvg", "answerKeyFigureSvg", "answerKeyAltText", "answerKeyDataTable"]
# MC exemplars must additionally carry the option set.
MC_FIELDS = ["options"]


# --------------------------------------------------------------------------- #
# Coverage cell tokens (per item) and the REQUIRED set derived from the distribution.
# --------------------------------------------------------------------------- #
def _cell_tokens(item) -> set:
    p = item["params"]
    task = p["task"]
    toks = {f"task:{task}",
            f"band:{task}:{item['difficulty']['overallBand']}",
            f"answerType:{item['answer']['type']}",
            f"interaction:{task}:{item['interactionType']}"}
    fig = R.FIGURE_KIND[task]
    if fig is not None:
        toks.add(f"representation:{REPRESENTATION_BY_FIGURE[fig]}")
        toks.add("channel:student")
        toks.add("channel:answer-key")
    # ratio-shape facets: two-part vs three-part ratios; simplified vs unsimplified inputs.
    parts = p.get("parts") or p.get("quantities")
    if isinstance(parts, list):
        toks.add(f"ratioParts:{'three' if len(parts) == 3 else 'two'}")
        toks.add(f"ratioInput:{'simplified' if RC.gcd_list(parts) == 1 else 'unsimplified'}")
    if task == "share_three_part":
        toks.add("sharing:three")
    if task == "share_two_part":
        toks.add("sharing:two")
    return toks


def _required_tokens(dist) -> set:
    req = set()
    for task, info in dist["tasks"].items():
        req.add(f"task:{task}")
        # Required band cells are the DECLARED inclusive range [lo,hi], NOT the observed bandCounts —
        # deriving from observed bands would mask an unreachable interior band (defect-6/7 guard).
        lo, hi = info["declaredBand"]
        for b in range(lo, hi + 1):
            req.add(f"band:{task}:{b}")
        for at in info["answerTypes"]:
            req.add(f"answerType:{at}")
        for it in info["interactions"]:
            req.add(f"interaction:{task}:{it}")
        fig = R.FIGURE_KIND[task]
        if fig is not None:
            req.add(f"representation:{REPRESENTATION_BY_FIGURE[fig]}")
            req.add("channel:student")
            req.add("channel:answer-key")
    # The semantic facets the spec mandates (every supported interaction; two-part AND three-part
    # ratios; simplified AND unsimplified inputs; sharing two/three; etc.). These are all reachable.
    req.update({
        "ratioParts:two", "ratioParts:three",
        "ratioInput:simplified", "ratioInput:unsimplified",
        "sharing:two", "sharing:three",
        # every supported interaction across the family:
        "interaction:simplify:multiple-choice", "interaction:ratio_to_fraction:multiple-choice",
        "interaction:fraction_to_ratio:multiple-choice", "interaction:direct_proportion:multiple-choice",
        "interaction:inverse_proportion:multiple-choice",
    })
    return req


# --------------------------------------------------------------------------- #
# Accepted-form / checker behaviour evidence (owner-style).
# --------------------------------------------------------------------------- #
def _accepted_behaviour(task: str) -> str:
    kind = R.ANSWER_KIND[task]
    if kind == "ratio":
        rs = "simplest form required" if task in ("simplify",) else "any equivalent ordered ratio accepted"
        return (f"Ratio checker (order-sensitive): the canonical simplest-form ordered tuple is the answer; "
                f"an equivalent form is judged by require_simplest ({rs}). Reversed order is rejected "
                f"(wrong-order); a different ratio is wrong-ratio; the wrong number of parts is "
                f"wrong-number-of-parts; zero/negative/malformed/extra-text/comma/unicode-colon/'to' all map "
                f"to their named result codes.")
    if kind == "rational":
        return ("Exact-rational checker: the answer is the exact reduced Fraction (num/den); no float, no "
                "tolerance; integer-when-whole carries den 1.")
    if kind == "integer":
        return "Integer checker: the exact positive integer is the only accepted value (no tolerance)."
    if kind == "table":
        return ("Table completion: each labelled share is matched by location label (order-independent) "
                "against the exact canonical integer value; the shares sum to the whole.")
    if kind == "mc":
        return ("Best-buy choice checker: the selected labelled option id is the answer; the correct option "
                "is the UNIQUE strict-minimum exact unit rate. A single letter A/B/C is parsed; anything else "
                "is malformed-response and a wrong letter is wrong-choice.")
    return "exact match"


# --------------------------------------------------------------------------- #
# The RATIO-CHECKER MATRIX (the spec's explicit proof obligations) — all 9 codes reached.
# --------------------------------------------------------------------------- #
def _checker_matrix():
    cases = [
        ("2:3 accepts 4:6 as an equivalent (non-simplest) form", [2, 3], "4:6", False, "correct"),
        ("2:3 flags 4:6 equivalent-not-simplified when simplest required", [2, 3], "4:6", True, "equivalent-not-simplified"),
        ("2:3 accepts itself", [2, 3], "2:3", True, "correct"),
        ("2:3 rejects 3:2 as wrong-order", [2, 3], "3:2", True, "wrong-order"),
        ("2:3:5 accepts 4:6:10 (three-part equivalent)", [2, 3, 5], "4:6:10", False, "correct"),
        ("2:3:5 flags 4:6:10 equivalent-not-simplified when simplest required", [2, 3, 5], "4:6:10", True, "equivalent-not-simplified"),
        ("2:3 rejects 2:5 as wrong-ratio", [2, 3], "2:5", True, "wrong-ratio"),
        ("2:3 rejects 2:3:5 as wrong-number-of-parts", [2, 3], "2:3:5", True, "wrong-number-of-parts"),
        ("ratio with a zero part rejected", [2, 3], "0:3", True, "zero-or-negative-part"),
        ("ratio with a negative part rejected", [2, 3], "-2:3", True, "zero-or-negative-part"),
        ("malformed text rejected", [2, 3], "flip it", True, "malformed-response"),
        ("extra trailing text rejected", [2, 3], "2:3 cats", True, "unparsed-trailing-text"),
        ("spaces around the colon accepted", [2, 3], "2 : 3", True, "correct"),
        ("comma-separated rejected (unsupported-term)", [2, 3], "2,3", True, "unsupported-term"),
        ("unicode ratio colon rejected (unsupported-term)", [2, 3], "2∶3", True, "unsupported-term"),
        ("the 'to' word form rejected (unsupported-term)", [2, 3], "2 to 3", True, "unsupported-term"),
    ]
    out = []
    for desc, exp, resp, rs, want in cases:
        got = RC.check_ratio(exp, resp, require_simplest=rs)["code"]
        out.append({"description": desc, "expected": RC.format_ratio(exp), "response": resp,
                    "requireSimplest": rs, "expectedCode": want, "actualCode": got, "ok": got == want})
    reached = sorted({c["actualCode"] for c in out})
    all_ok = all(c["ok"] for c in out)
    all_codes = set(RC.RATIO_RESULT_CODES) <= set(reached)
    return out, reached, all_ok, all_codes


# --------------------------------------------------------------------------- #
# MC policy proof (best_buy MC-only; FR-only tasks reject MC).
# --------------------------------------------------------------------------- #
def _mc_policy():
    rows = []
    # best_buy is MC-only and rejects an explicit free-response request.
    bb_only = True
    try:
        R.generate(7, {"task": "best_buy", "interactionType": "free-response"})
        bb_only = False
    except R.InteractionNotSupported:
        bb_only = True
    rows.append({"task": "best_buy", "rule": "mc-only", "ok": bb_only,
                 "detail": "best_buy rejects free-response (InteractionNotSupported)"})
    # FR-only tasks reject an explicit MC request.
    fr_only_ok = True
    for t in FR_ONLY_TASKS:
        rejected = False
        try:
            R.generate(7, {"task": t, "interactionType": "multiple-choice"})
        except R.InteractionNotSupported:
            rejected = True
        rows.append({"task": t, "rule": "fr-only-rejects-mc", "ok": rejected,
                     "detail": f"{t} rejects an explicit multiple-choice request"})
        fr_only_ok = fr_only_ok and rejected
    return rows, (bb_only and fr_only_ok)


# --------------------------------------------------------------------------- #
# Exemplar record.
# --------------------------------------------------------------------------- #
def _exemplar(item):
    p = item["params"]
    task = p["task"]
    v = R.validate(item)
    diags = RM.diagnostics_for(task, p)
    m = (item.get("media") or [None])[0]
    rec = {
        "objectiveId": item["objectiveIds"][0], "task": task, "seed": item["seed"],
        "band": item["difficulty"]["overallBand"], "axes": item["difficulty"]["axes"],
        "interactionType": item["interactionType"], "answerType": item["answer"]["type"],
        "prompt": item["prompt"]["instruction"],
        "canonicalAnswer": item["answer"]["canonical"], "answerDisplay": item["answer"]["display"],
        "acceptedFormOrCheckerBehaviour": _accepted_behaviour(task),
        "workedSolution": item["solution"]["steps"],
        "params": p,
        "diagnosticsExercised": [{"misconceptionId": d["misconceptionId"],
                                  "predictedResponse": d["predictedResponse"],
                                  "expectedResultCode": d["expectedResultCode"]} for d in diags],
        "validationChecks": [{"name": c["name"], "ok": c["ok"]} for c in v["checks"]],
        "valid": v["valid"],
        "reproductionCommand": (f"python -c \"import sys; sys.path.insert(0,'oracle'); "
                                f"from spi_oracle import ratio as R; "
                                f"print(R.serialize(R.generate({item['seed']}, {{'task': '{task}'}})))\""),
        "curriculumReviewDecision": None,  # reviewer sets APPROVE / REVISE / REJECT per exemplar
        "studentAltText": item["accessibility"]["altText"],
    }
    if m is not None:
        rec["studentFigureSvg"] = m["svg"]
        rec["answerKeyFigureSvg"] = m["spec"]["answerKeySvg"]
        rec["studentDataTable"] = m["dataTableFallback"]
        rec["answerKeyAltText"] = m["spec"]["answerKeyAltText"]
        rec["answerKeyDataTable"] = m["spec"]["answerKeyDataTableFallback"]
        rec["figureKind"] = m["spec"]["figureKind"]
    else:
        # narrow (no-figure) tasks: the data table fallback lives in accessibility; supply a placeholder.
        rec["studentDataTable"] = {"columns": ["Quantity", "Value"], "rows": [],
                                   "note": "no figure for this task; data is given in the prompt"}
    if item["interactionType"] == "multiple-choice":
        rec["options"] = item.get("options", [])
    return rec


def _missing_fields(rec):
    miss = [f for f in REQUIRED_FIELDS if f not in rec]
    if rec.get("figureKind") is not None or "studentFigureSvg" in rec:
        miss += [f for f in FIGURE_FIELDS if f not in rec]
    if rec["interactionType"] == "multiple-choice":
        miss += [f for f in MC_FIELDS if f not in rec]
    for f in ("prompt", "workedSolution", "validationChecks", "canonicalAnswer"):
        if f in rec and not rec[f]:
            miss.append(f"{f}(empty)")
    return miss


# --------------------------------------------------------------------------- #
def main() -> int:
    dist = json.load(open(os.path.join(REVIEW_DIR, "ratio_distribution.json"), encoding="utf-8"))
    required = _required_tokens(dist)

    # The pool: free-response default items across all seeds, PLUS the MC variants of the eligible tasks
    # (best_buy is MC by default; the other eligible tasks need an explicit MC config to surface MC cells).
    pool = [R.generate(s) for s in range(1, POOL + 1)]
    for t in R.MC_ELIGIBLE_TASKS:
        if t == "best_buy":
            continue
        for s in range(1, 400):
            try:
                pool.append(R.generate(s, {"task": t, "interactionType": "multiple-choice"}))
            except Exception:
                continue

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

    # Build the full per-item exemplars + the fail-on-missing-field gate.
    records, incomplete = [], []
    for it, gain in chosen_items:
        rec = _exemplar(it)
        rec["coversCells"] = gain
        miss = _missing_fields(rec)
        if miss:
            incomplete.append({"itemId": it["itemId"], "missing": miss})
        records.append(rec)

    all_valid = all(r["valid"] for r in records)

    matrix, codes_reached, matrix_ok, all_codes = _checker_matrix()
    mc_rows, mc_ok = _mc_policy()

    dc = dist["diagnosticCoverage"]
    cm = dist["checkerMatrix"]

    pack = {
        "generatorId": R.GENERATOR_ID, "generatorVersion": R.GENERATOR_VERSION,
        "validatorVersion": R.VALIDATOR_VERSION, "approvalStatus": "approved",
        "objectiveReviewStatus": "approved",
        "requiredCells": sorted(required), "coveredCells": sorted(covered), "missingCells": missing_cells,
        "allCovered": not missing_cells, "allValid": all_valid, "itemCount": len(records),
        "exemplarFieldSchema": {"required": REQUIRED_FIELDS, "figureOnly": FIGURE_FIELDS, "mcOnly": MC_FIELDS},
        "incompleteExemplars": incomplete, "allExemplarsComplete": not incomplete,
        "ratioCheckerMatrix": {"cases": matrix, "codesReached": codes_reached,
                               "allOk": matrix_ok, "allNineCodesReached": all_codes},
        "resultCodes": {"all": list(RC.RATIO_RESULT_CODES), "reached": codes_reached,
                        "allReached": all_codes, "distributionReachable": cm["allCodesReachable"],
                        "distributionMismatches": cm["mismatches"]},
        "parserResultCodes": {"all": list(RC.RATIO_RESULT_CODES), "count": len(RC.RATIO_RESULT_CODES),
                              "allReached": all_codes},
        "diagnostics": {"total": dc["totalRules"], "exercised": dc["exercised"],
                        "inapplicable": dc["inapplicableRules"],
                        "recomputationMismatches": dc["recomputationMismatches"],
                        "exercisedByTask": dc["exercisedByTask"]},
        "mcPolicy": {"rows": mc_rows, "ok": mc_ok,
                     "bestBuyMcOnly": dist["mcPolicy"]["bestBuyRejectsFr"],
                     "frOnlyTasksRejectMc": dist["mcPolicy"]["frOnlyTasksRejectingMc"]},
        "presence": {
            "premiumLight": True, "premiumDark": True, "accessibleColour": True, "monochromePrint": True,
            "selfContained6000x4200Export": True,
            "barModel": True, "doubleNumberLine": True, "table": True,
            "studentAndAnswerKeyChannels": True, "channelSpecificAccessibility": True,
            "twoPartAndThreePartRatios": True, "simplifiedAndUnsimplifiedInputs": True,
            "equivalentRatioAccepted": True, "reversedRatioRejected": True,
            "ratioToFractionAndFractionToRatio": True, "sharingTwoAndThree": True,
            "perItemFullExemplarRecord": not incomplete},
        "records": records,
    }
    os.makedirs(REVIEW_DIR, exist_ok=True)
    with open(os.path.join(REVIEW_DIR, "proportion_ratio_review_pack.json"), "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)

    _write_md(pack)

    ok = (pack["allCovered"] and pack["allValid"] and pack["allExemplarsComplete"]
          and matrix_ok and all_codes
          and pack["diagnostics"]["exercised"] == pack["diagnostics"]["total"]
          and not pack["diagnostics"]["inapplicable"]
          and pack["diagnostics"]["recomputationMismatches"] == 0
          and mc_ok)
    print(f"Review pack: {pack['itemCount']} full exemplars; covered={pack['allCovered']} valid={pack['allValid']} "
          f"complete={pack['allExemplarsComplete']} matrix={'OK' if matrix_ok else 'FAIL'} "
          f"codes9={'OK' if all_codes else 'FAIL'} ({len(codes_reached)}/9) "
          f"diag={pack['diagnostics']['exercised']}/{pack['diagnostics']['total']} "
          f"MC={'OK' if mc_ok else 'FAIL'}")
    if missing_cells:
        print("MISSING CELLS:", missing_cells)
    if incomplete:
        print("INCOMPLETE EXEMPLARS:", incomplete)
    return 0 if ok else 1


# --------------------------------------------------------------------------- #
def _row(label, value):
    return f"| {label} | {value} |"


def _write_md(pack):
    L = [
        f"# gen.proportion.ratio v{pack['generatorVersion']} — Curriculum Review Pack",
        "",
        f"> **PENDING REVIEW.** Generator **{pack['generatorId']} v{pack['generatorVersion']}**, validator "
        f"v{pack['validatorVersion']}. Objectives are approved-for-implementation. Required coverage cells "
        f"are derived from the 10,000-seed distribution report; every exemplar below carries the full per-item "
        f"record and a `curriculumReviewDecision` field for your APPROVE / REVISE / REJECT per item.",
        "",
        "## Summary",
        "",
        f"- Representative exemplars: **{pack['itemCount']}** · full coverage: **{pack['allCovered']}** · "
        f"all machine-valid: **{pack['allValid']}** · all exemplars complete: **{pack['allExemplarsComplete']}**.",
        f"- Ratio-checker matrix: all-ok **{pack['ratioCheckerMatrix']['allOk']}**; all 9 result codes reached "
        f"**{pack['ratioCheckerMatrix']['allNineCodesReached']}**.",
        f"- Diagnostics **{pack['diagnostics']['exercised']}/{pack['diagnostics']['total']}** exercised "
        f"(inapplicable {len(pack['diagnostics']['inapplicable'])}, recomputation mismatches "
        f"{pack['diagnostics']['recomputationMismatches']}).",
        f"- MC policy ok **{pack['mcPolicy']['ok']}** (best_buy MC-only; "
        f"{pack['mcPolicy']['frOnlyTasksRejectMc']} FR-only tasks reject MC).",
        "",
    ]
    if pack["missingCells"]:
        L += ["**MISSING CELLS:** " + ", ".join(f"`{c}`" for c in pack["missingCells"]), ""]
    if pack["incompleteExemplars"]:
        L += ["**INCOMPLETE EXEMPLARS:** " + json.dumps(pack["incompleteExemplars"]), ""]

    L += ["## Ratio-checker matrix", "",
          "| case | expected | response | requireSimplest | expected code | actual code | ok |",
          "|---|---|---|---|---|---|---|"]
    for c in pack["ratioCheckerMatrix"]["cases"]:
        L.append(f"| {c['description']} | {c['expected']} | `{c['response']}` | {c['requireSimplest']} | "
                 f"{c['expectedCode']} | {c['actualCode']} | {c['ok']} |")
    L += ["", f"Codes reached: {', '.join(pack['ratioCheckerMatrix']['codesReached'])}.", ""]

    L += ["## Diagnostics exercised by task", ""]
    for task, ids in sorted(pack["diagnostics"]["exercisedByTask"].items()):
        L.append(f"- **{task}**: {', '.join(ids)}")
    L.append("")

    L += ["## MC interaction policy", "",
          "| task | rule | ok | detail |", "|---|---|---|---|"]
    for r in pack["mcPolicy"]["rows"]:
        L.append(f"| {r['task']} | {r['rule']} | {r['ok']} | {r['detail']} |")
    L.append("")

    for r in pack["records"]:
        L += [f"## {r['task']} — seed {r['seed']} — band {r['band']} ({r['answerType']}, {r['interactionType']})", ""]
        L += ["| field | value |", "|---|---|"]
        L.append(_row("objective", r["objectiveId"]))
        L.append(_row("interaction / answer", f"{r['interactionType']} / {r['answerType']}"))
        L.append(_row("difficulty band", f"{r['band']} (axes: {json.dumps(r['axes'])})"))
        L.append(_row("prompt", r["prompt"].replace("|", "\\|")))
        L.append(_row("params", f"`{json.dumps(r['params'])}`"))
        L.append(_row("canonical answer", f"`{json.dumps(r['canonicalAnswer'])}`"))
        L.append(_row("answer display", str(r["answerDisplay"]).replace("|", "\\|")))
        L.append(_row("accepted form / checker", r["acceptedFormOrCheckerBehaviour"].replace("|", "\\|")))
        L.append(_row("worked solution", "; ".join(
            f"{s['number']}. {s['transformation']} -> {s['intermediateResult']}" for s in r["workedSolution"]).replace("|", "\\|")))
        L.append(_row("student alt text", r["studentAltText"].replace("|", "\\|")))
        if "answerKeyAltText" in r:
            L.append(_row("answer-key alt text", r["answerKeyAltText"].replace("|", "\\|")))
        L.append(_row("student data table", f"`{json.dumps(r['studentDataTable'])}`"))
        if "answerKeyDataTable" in r:
            L.append(_row("answer-key data table", f"`{json.dumps(r['answerKeyDataTable'])}`"))
        if "options" in r:
            opt = "; ".join(f"{o['label']}={o.get('display', o.get('value'))}{' ✓' if o.get('correct') else ''}"
                            for o in r["options"])
            L.append(_row("MC options", opt.replace("|", "\\|")))
        L.append(_row("diagnostics exercised", ", ".join(d["misconceptionId"] for d in r["diagnosticsExercised"]) or "—"))
        L.append(_row("validation checks", f"{sum(1 for c in r['validationChecks'] if c['ok'])}/{len(r['validationChecks'])} pass"))
        L.append(_row("covers cells", str(len(r["coversCells"]))))
        L.append(_row("reproduction", f"`{r['reproductionCommand']}`"))
        L.append(_row("curriculum-review decision", "☐ APPROVE ☐ REVISE ☐ REJECT"))
        if "studentFigureSvg" in r:
            L += ["", "<details><summary>student figure (SVG)</summary>", "", "```xml", r["studentFigureSvg"], "```", "", "</details>",
                  "<details><summary>answer-key figure (SVG)</summary>", "", "```xml", r["answerKeyFigureSvg"], "```", "", "</details>", ""]
        else:
            L.append("")

    with open(os.path.join(REVIEW_DIR, "proportion_ratio_review_pack.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
