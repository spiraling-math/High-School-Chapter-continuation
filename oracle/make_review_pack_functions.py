"""gen.functions.foundations v1.0.0 — curriculum review pack (PENDING-REVIEW; mirror of make_review_pack_ratio).

Required coverage cells are DERIVED from the 10,000-seed distribution report (docs/review/
functions_distribution.json): every task, every DECLARED band per task (the inclusive declared range, never
the observed bands, so an unreachable interior band can never be masked), every rule-kind facet observed per
task, every supported interaction per task and every answer type. Reachability is the authoritative source and
the builder FAILS on any uncovered cell.

Beyond coverage this is a FULL CURRICULUM review pack: every selected representative item carries the complete
educational record a reviewer needs to approve it as a golden exemplar — objective, task, seed, band + axes,
interaction + answer type, the full prompt (text + LaTeX blocks), canonical answer + display, accepted-form /
checker behaviour, worked solution, params, spoken-math text, (multiple-choice) the option set and every
distractor's misconception + student-facing feedback, validation checks, a reproduction command, and a per-item
`curriculumReviewDecision` field (null until reviewed).

The builder FAILS if any cell is uncovered, any exemplar is invalid or missing a required field, any of the 68
MISC.FUNC.* rules is unexercised in the pool, any of the 7 expression-checker / 8 interval-checker result codes
lacks evidence in the answer-contract matrix, or the MC policy is violated (identify_function is multiple-choice
only; every other task serves both interactions).

  PYTHONIOENCODING=utf-8 python oracle/make_review_pack_functions.py

Writes docs/review/functions_review_pack.{json,md} (reads functions_distribution.json).
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))
sys.path.insert(0, HERE)

from spi_oracle import functions as G  # noqa: E402
from spi_oracle import functions_misconceptions as FM  # noqa: E402
from spi_oracle import expression_checker as EC  # noqa: E402
from spi_oracle import interval_checker as IC  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
POOL = int(os.environ.get("SPI_POOL", "3000"))
MC_SEEDS = int(os.environ.get("SPI_MC_SEEDS", "1500"))

REQUIRED_FIELDS = [
    "objectiveId", "task", "seed", "band", "axes", "interactionType", "answerType", "prompt", "promptBlocks",
    "canonicalAnswer", "answerDisplay", "acceptedFormOrCheckerBehaviour", "workedSolution", "params", "spokenMath",
    "validationChecks", "reproductionCommand", "curriculumReviewDecision",
]
MC_FIELDS = ["options", "distractors"]


# --------------------------------------------------------------------------- #
# Coverage cells
# --------------------------------------------------------------------------- #
def _kind_of(item) -> str:
    """The rule-kind facet, identical to oracle/run_functions.py so the cells match the distribution."""
    p = item["params"]
    if "rule" in p:
        return p["rule"]["kind"] + ("_restricted" if "restricted" in p else "")
    if "f" in p:
        return f"{p['f']['kind']}/{p['g']['kind']}:{p['order']}"
    if "form" in p:
        return p["form"]
    return "-"


def _cell_tokens(item) -> set:
    p = item["params"]
    task = p["task"]
    return {f"task:{task}",
            f"band:{task}:{item['difficulty']['overallBand']}",
            f"answerType:{item['answer']['type']}",
            f"interaction:{task}:{item['interactionType']}",
            f"kind:{task}:{_kind_of(item)}"}


def _required_tokens(dist) -> set:
    req = set()
    for task, info in dist["byTask"].items():
        req.add(f"task:{task}")
        lo, hi = dist["declaredBands"][task]
        for b in range(lo, hi + 1):
            req.add(f"band:{task}:{b}")
        for at in info["answerTypes"]:
            req.add(f"answerType:{at}")
        for it in info["interactions"]:
            req.add(f"interaction:{task}:{it}")
        for k in info["kinds"]:
            req.add(f"kind:{task}:{k}")
    return req


# --------------------------------------------------------------------------- #
# Accepted-form / checker behaviour evidence
# --------------------------------------------------------------------------- #
def _accepted_behaviour(task: str, item) -> str:
    fam = G.ANSWER_FAMILY[task]
    if fam == "choice":
        return ("Choice checker: the selected option letter is the answer; exactly one of the four relations has "
                "an input paired with two different outputs. The three distractors are structurally distinct "
                "functions (many-to-one, constant, pattern-free) so each wrong choice diagnoses a named belief.")
    if fam == "number":
        acc = item["answer"]["accepts"]
        return ("Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is "
                f"accepted; a decimal is accepted only when it terminates (accepts.decimal={str(acc['decimal']).lower()}); "
                "mixed numbers are not accepted; no tolerance; integer when den = 1.")
    if fam == "expression":
        return ("Algebraic-expression checker (ASCII-anchored recursive-descent parser, exact rationals): any equivalent "
                "written form of the polynomial in x is accepted — reordered terms, unexpanded brackets and products, "
                "`^` or `**`, implicit multiplication, fractional coefficients as a/b or exact decimals, an optional "
                "`f(x) =` / `(f o g)(x) =` / `y =` prefix. Result codes: correct, wrong-variable, not-polynomial "
                "(division by x), wrong-degree, wrong-coefficients, misconception (a known wrong form), unparseable.")
    return ("Interval checker (ASCII-anchored, exact rationals): inequality notation (`x >= 2`, `2 <= x`), interval "
            "notation (`[2, inf)`), set-builder, the words `all real numbers`, exclusions (`x != 3`), unicode "
            "≥ ≤ ≠ ∞ ℝ and `infinity`/`oo` are accepted. A domain is stated in x and a range in y (also f(x)/g(x)); "
            "the letter is checked (wrong-variable). Result codes: correct, wrong-variable, wrong-kind, "
            "wrong-endpoint, wrong-inclusivity, wrong-direction, misconception, unparseable.")


# --------------------------------------------------------------------------- #
# The ANSWER-CONTRACT MATRIX — every expression / interval result code reached.
# --------------------------------------------------------------------------- #
def _rj(n, d=1):
    return {"num": n, "den": d}


def _expression_matrix():
    canon = {"variable": "x", "coefficients": [_rj(1), _rj(-3), _rj(2)]}  # 2x^2 - 3x + 1
    diag = [{"misconceptionId": "MISC.FUNC.COMP_SQUARE_NO_CROSS_TERM", "coefficients": [_rj(1), _rj(0), _rj(2)]}]
    cases = [
        ("the canonical display", "2x^2 - 3x + 1", "correct"),
        ("reordered terms with ** power", "1 - 3x + 2x**2", "correct"),
        ("unexpanded factored product", "(2x - 1)(x - 1)", "correct"),
        ("an f(x) = prefix and spaces removed", "f(x)=2x^2-3x+1", "correct"),
        ("wrong variable letter", "2y^2 - 3y + 1", "wrong-variable"),
        ("a dropped term", "2x^2 - 3x", "wrong-coefficients"),
        ("wrong degree", "2x^3 - 3x + 1", "wrong-degree"),
        ("division by x is not a polynomial", "1/x + 2", "not-polynomial"),
        ("a known wrong form is diagnosed (square without cross term)", "2x^2 + 1", "misconception"),
        ("dangling operator", "2x^2 - 3x +", "unparseable"),
    ]
    out = []
    for desc, resp, want in cases:
        got = EC.check_expression(resp, canon, diag)["code"]
        out.append({"description": desc, "response": resp, "expectedCode": want, "actualCode": got, "ok": got == want})
    reached = sorted({c["actualCode"] for c in out})
    return {"canonical": canon, "cases": out, "codesReached": reached, "allOk": all(c["ok"] for c in out),
            "allCodesReached": set(EC.CODES) <= set(reached), "codes": list(EC.CODES)}


def _interval_matrix():
    ray = {"kind": "ray", "variable": "x", "endpoint": _rj(2), "inclusive": True, "direction": "ge"}
    flipped = {"kind": "ray", "variable": "x", "endpoint": _rj(2), "inclusive": True, "direction": "le"}
    diag = [{"misconceptionId": "MISC.FUNC.DOMAIN_DIRECTION_FLIPPED", "canonical": flipped}]
    bounded = {"kind": "bounded", "variable": "y", "lo": _rj(-1), "hi": _rj(4), "loInclusive": True, "hiInclusive": True}
    excl = {"kind": "reals-except", "variable": "y", "points": [_rj(3)]}
    reals = {"kind": "reals"}
    cases = [
        ("inequality form", ray, "x >= 2", "correct"),
        ("interval notation", ray, "[2, inf)", "correct"),
        ("reversed inequality order", ray, "2 <= x", "correct"),
        ("unicode >=", ray, "x ≥ 2", "correct"),
        ("range letter y for a domain", ray, "y >= 2", "wrong-variable"),
        ("an exclusion instead of a ray", ray, "x != 2", "wrong-kind"),
        ("wrong endpoint", ray, "x >= 3", "wrong-endpoint"),
        ("strict instead of inclusive", ray, "x > 2", "wrong-inclusivity"),
        ("wrong direction without a diagnostic", ray, "x <= 2", "wrong-direction"),
        ("wrong direction matching a known misconception", ray, "x <= 2", "misconception"),
        ("dangling comparison", ray, "x >=", "unparseable"),
        ("bounded range as a chained inequality", bounded, "-1 <= y <= 4", "correct"),
        ("bounded range in interval notation", bounded, "[-1, 4]", "correct"),
        ("range exclusion", excl, "y != 3", "correct"),
        ("all real numbers in words", reals, "all real numbers", "correct"),
    ]
    out = []
    for desc, canon, resp, want in cases:
        got = IC.check_interval(resp, canon, diag if want == "misconception" else ())["code"]
        out.append({"description": desc, "canonical": canon, "response": resp, "expectedCode": want,
                    "actualCode": got, "ok": got == want})
    reached = sorted({c["actualCode"] for c in out})
    return {"cases": out, "codesReached": reached, "allOk": all(c["ok"] for c in out),
            "allCodesReached": set(IC.CODES) <= set(reached), "codes": list(IC.CODES)}


# --------------------------------------------------------------------------- #
# MC policy proof (identify_function MC-only; every other task serves both interactions).
# --------------------------------------------------------------------------- #
def _mc_policy():
    rows = []
    rejected = False
    try:
        G.generate(7, {"task": "identify_function", "interactionType": "free-response"})
    except G.InteractionNotSupported:
        rejected = True
    rows.append({"task": "identify_function", "rule": "mc-only", "ok": rejected,
                 "detail": "identify_function rejects free-response (InteractionNotSupported)"})
    ok_all = rejected
    for t in G.TASKS:
        if t in G.MC_ONLY_TASKS:
            continue
        fr = G.generate(7, {"task": t, "interactionType": "free-response"})
        mc = G.generate(7, {"task": t, "interactionType": "multiple-choice"})
        ok = fr["interactionType"] == "free-response" and mc["interactionType"] == "multiple-choice" and len(mc["options"]) == 4
        rows.append({"task": t, "rule": "both-interactions", "ok": ok,
                     "detail": f"{t} serves free-response and multiple-choice (4 options, 3 misconception-backed distractors)"})
        ok_all = ok_all and ok
    return rows, ok_all


# --------------------------------------------------------------------------- #
# Exemplar record.
# --------------------------------------------------------------------------- #
def _feedback(mid: str, ctx) -> str:
    m = FM.MISCONCEPTIONS[mid]
    fb = m.get("feedback")
    if callable(fb):
        try:
            text = fb(ctx)
            if text:
                return text
        except Exception:
            pass
    return m["description"]


def _prompt_text(item) -> str:
    parts = [item["prompt"]["instruction"] + ":"]
    for b in item["prompt"]["blocks"]:
        parts.append(b.get("text") or f"$ {b.get('latex')} $")
    return " ".join(parts)


def _exemplar(item):
    p = item["params"]
    task = p["task"]
    v = G.validate(item)
    cfg = {"task": task, "interactionType": item["interactionType"]}
    rec = {
        "objectiveId": item["objectiveIds"][0], "task": task, "seed": item["seed"],
        "band": item["difficulty"]["overallBand"], "axes": item["difficulty"]["axes"],
        "interactionType": item["interactionType"], "answerType": item["answer"]["type"],
        "prompt": _prompt_text(item), "promptBlocks": item["prompt"]["blocks"],
        "canonicalAnswer": item["answer"]["canonical"], "answerDisplay": item["answer"]["display"],
        "acceptedFormOrCheckerBehaviour": _accepted_behaviour(task, item),
        "workedSolution": item["solution"]["steps"],
        "params": p,
        "spokenMath": item["accessibility"]["spokenMath"],
        "validationChecks": [{"name": c["name"], "ok": c["result"] == "pass"} for c in v["checks"]],
        "valid": v["status"] == "pass",
        "reproductionCommand": (f"python -c \"import sys; sys.path.insert(0,'oracle/spi_oracle'); "
                                f"import functions as G; print(G.serialize(G.generate({item['seed']}, "
                                f"{{'task': '{task}', 'interactionType': '{item['interactionType']}'}})))\""),
        "curriculumReviewDecision": None,  # reviewer sets APPROVE / REVISE / REJECT per exemplar
    }
    if item["interactionType"] == "multiple-choice":
        ctx = G._ctx(task, G._internal_params(p))
        rec["options"] = item["options"]
        rec["distractors"] = [{"id": d["id"], "display": d["display"], "misconceptionId": d["misconceptionId"],
                               "rationale": d["rationale"], "feedback": _feedback(d["misconceptionId"], ctx)}
                              for d in item["distractors"]]
    return rec


def _missing_fields(rec):
    miss = [f for f in REQUIRED_FIELDS if f not in rec]
    if rec["interactionType"] == "multiple-choice":
        miss += [f for f in MC_FIELDS if f not in rec]
    for f in ("prompt", "workedSolution", "validationChecks", "canonicalAnswer", "spokenMath"):
        if f in rec and not rec[f]:
            miss.append(f"{f}(empty)")
    return miss


# --------------------------------------------------------------------------- #
def main() -> int:
    dist = json.load(open(os.path.join(REVIEW_DIR, "functions_distribution.json"), encoding="utf-8"))
    required = _required_tokens(dist)

    # The pool: default-interaction items across the seeds (identify_function is MC by default, every other
    # task free-response), PLUS the multiple-choice variants of every MC-eligible task.
    pool = [G.generate(s) for s in range(1, POOL + 1)]
    exercised_by_task: dict = {t: set() for t in G.TASKS}
    for it in pool:
        for o in it.get("options", []):
            if o.get("misconceptionId"):
                exercised_by_task[it["params"]["task"]].add(o["misconceptionId"])
    for t in G.TASKS:
        if t in G.MC_ONLY_TASKS:
            continue
        for s in range(1, MC_SEEDS + 1):
            it = G.generate(s, {"task": t, "interactionType": "multiple-choice"})
            for d in it["distractors"]:
                exercised_by_task[t].add(d["misconceptionId"])
            if s <= 400:
                pool.append(it)

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

    records, incomplete = [], []
    for it, gain in chosen_items:
        rec = _exemplar(it)
        rec["coversCells"] = gain
        miss = _missing_fields(rec)
        if miss:
            incomplete.append({"itemId": it["itemId"], "missing": miss})
        records.append(rec)
    all_valid = all(r["valid"] for r in records)

    expr = _expression_matrix()
    intv = _interval_matrix()
    mc_rows, mc_ok = _mc_policy()

    all_ids = set(FM.MISCONCEPTIONS)
    exercised = set().union(*exercised_by_task.values())
    unexercised = sorted(all_ids - exercised)
    eligible_gaps = {t: sorted(set(FM.rules_for(t)) - exercised_by_task[t]) for t in G.TASKS}
    eligible_gaps = {t: g for t, g in eligible_gaps.items() if g}

    pack = {
        "generatorId": G.GENERATOR_ID, "generatorVersion": G.GENERATOR_VERSION,
        "validatorVersion": G.VALIDATOR_VERSION, "approvalStatus": "pending-review",
        "objectiveReviewStatus": "proposed", "hiddenFromNormalStudioAndProduction": True,
        "requiredCells": sorted(required), "coveredCells": sorted(covered), "missingCells": missing_cells,
        "allCovered": not missing_cells, "allValid": all_valid, "itemCount": len(records),
        "exemplarFieldSchema": {"required": REQUIRED_FIELDS, "mcOnly": MC_FIELDS},
        "incompleteExemplars": incomplete, "allExemplarsComplete": not incomplete,
        "answerContractMatrix": {"expression": expr, "interval": intv},
        "misconceptions": {"total": len(all_ids), "structural": list(FM.STRUCTURAL_ONLY),
                           "exercised": len(exercised), "unexercised": unexercised,
                           "eligibleGapsByTask": eligible_gaps,
                           "exercisedByTask": {t: sorted(v) for t, v in exercised_by_task.items()}},
        "mcPolicy": {"rows": mc_rows, "ok": mc_ok, "mcOnlyTasks": list(G.MC_ONLY_TASKS)},
        "distributionSummary": {"sweepSeeds": dist["sweepSeeds"], "invalidItems": dist["invalidItems"],
                                "unreachableDeclaredBands": dist["unreachableDeclaredBands"],
                                "declaredBands": dist["declaredBands"]},
        "poolSizes": {"defaultInteractionSeeds": POOL, "mcSeedsPerTask": MC_SEEDS, "mcExemplarSeedsPerTask": 400},
        "records": records,
    }
    os.makedirs(REVIEW_DIR, exist_ok=True)
    with open(os.path.join(REVIEW_DIR, "functions_review_pack.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(pack, fh, indent=2, ensure_ascii=False)
    _write_md(pack)

    ok = (pack["allCovered"] and pack["allValid"] and pack["allExemplarsComplete"]
          and expr["allOk"] and expr["allCodesReached"] and intv["allOk"] and intv["allCodesReached"]
          and not unexercised and not eligible_gaps and mc_ok
          and dist["invalidItems"] == 0 and not dist["unreachableDeclaredBands"])
    print(f"Review pack: {pack['itemCount']} full exemplars; covered={pack['allCovered']} valid={pack['allValid']} "
          f"complete={pack['allExemplarsComplete']} expression-matrix={'OK' if expr['allOk'] and expr['allCodesReached'] else 'FAIL'} "
          f"interval-matrix={'OK' if intv['allOk'] and intv['allCodesReached'] else 'FAIL'} "
          f"misconceptions={len(exercised)}/{len(all_ids)} MC={'OK' if mc_ok else 'FAIL'}")
    if missing_cells:
        print("MISSING CELLS:", missing_cells)
    if incomplete:
        print("INCOMPLETE EXEMPLARS:", incomplete)
    if unexercised or eligible_gaps:
        print("UNEXERCISED:", unexercised, eligible_gaps)
    for m, name in ((expr, "expression"), (intv, "interval")):
        for c in m["cases"]:
            if not c["ok"]:
                print(f"MATRIX FAIL ({name}): {c['description']}: {c['response']!r} -> {c['actualCode']} (expected {c['expectedCode']})")
    return 0 if ok else 1


# --------------------------------------------------------------------------- #
def _row(label, value):
    return f"| {label} | {value} |"


def _md(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _write_md(pack):
    expr, intv = pack["answerContractMatrix"]["expression"], pack["answerContractMatrix"]["interval"]
    L = [
        f"# gen.functions.foundations v{pack['generatorVersion']} — Curriculum Review Pack",
        "",
        f"> **PENDING-REVIEW** (machine-validated; NOT curriculum-approved; DECISION_LOG.md #65). Generator "
        f"**{pack['generatorId']} v{pack['generatorVersion']}**, validator v{pack['validatorVersion']}. IB Mathematics: "
        f"Analysis and Approaches SL — Introducing Functions (Oxford chapter 2). The eleven `SPI.IBDPAASL.FUNC.*` "
        f"objectives are `reviewStatus: proposed`; the family is visible only in the Studio's review mode and excluded "
        f"from production exports and samples until the owner approves it. Required coverage cells are derived from "
        f"the {pack['distributionSummary']['sweepSeeds']:,}-seed distribution report; every exemplar below carries the "
        f"full per-item record and a `curriculumReviewDecision` field.",
        "",
        "## What the owner is asked to approve",
        "",
        "1. The eleven proposed objectives (`curriculum/objectives/SPI.IBDPAASL.FUNC.json`) and their task mapping.",
        "2. The two new canonical-first answer contracts: `answer.type: algebraic-expression` (canonical polynomial "
        "coefficient vector in x) and `answer.type: interval` (real-subset descriptor: reals / ray / bounded / "
        "reals-except), with the ASCII-anchored checkers pinned by the cross-engine corpus.",
        "3. The item mathematics, phrasing, difficulty bands, worked solutions, misconception rules + feedback, and the "
        "MC policy (identify_function multiple-choice only), as evidenced by the exemplars below.",
        "4. The controlled-vocabulary extension `FUNC → functions` + strand `introducing-functions` (registry §4.6).",
        "",
        "## Summary",
        "",
        f"- Representative exemplars: **{pack['itemCount']}** · full coverage: **{pack['allCovered']}** · "
        f"all machine-valid: **{pack['allValid']}** · all exemplars complete: **{pack['allExemplarsComplete']}**.",
        f"- 10,000-seed sweep (both interaction pools): invalid items **{pack['distributionSummary']['invalidItems']}**; "
        f"unreachable declared bands **{pack['distributionSummary']['unreachableDeclaredBands'] or 'none'}**.",
        f"- Expression-checker matrix: all-ok **{expr['allOk']}**; all {len(expr['codes'])} result codes reached "
        f"**{expr['allCodesReached']}**. Interval-checker matrix: all-ok **{intv['allOk']}**; all {len(intv['codes'])} "
        f"result codes reached **{intv['allCodesReached']}**.",
        f"- Misconceptions **{pack['misconceptions']['exercised']}/{pack['misconceptions']['total']}** exercised "
        f"(unexercised: {pack['misconceptions']['unexercised'] or 'none'}).",
        f"- MC policy ok **{pack['mcPolicy']['ok']}** (identify_function MC-only; every other task serves both interactions).",
        "",
    ]
    if pack["missingCells"]:
        L += ["**MISSING CELLS:** " + ", ".join(f"`{c}`" for c in pack["missingCells"]), ""]
    if pack["incompleteExemplars"]:
        L += ["**INCOMPLETE EXEMPLARS:** " + json.dumps(pack["incompleteExemplars"]), ""]

    L += ["## Declared difficulty bands", "", "| task | declared bands |", "|---|---|"]
    for t, (lo, hi) in pack["distributionSummary"]["declaredBands"].items():
        L.append(f"| {t} | {lo}–{hi} |")
    L.append("")

    L += ["## Answer-contract matrix — algebraic-expression", "",
          f"Canonical: `{json.dumps(expr['canonical'])}` (2x^2 - 3x + 1).", "",
          "| case | response | expected code | actual code | ok |", "|---|---|---|---|---|"]
    for c in expr["cases"]:
        L.append(f"| {_md(c['description'])} | `{c['response']}` | {c['expectedCode']} | {c['actualCode']} | {c['ok']} |")
    L += ["", f"Codes reached: {', '.join(expr['codesReached'])}.", ""]

    L += ["## Answer-contract matrix — interval", "",
          "| case | canonical | response | expected code | actual code | ok |", "|---|---|---|---|---|---|"]
    for c in intv["cases"]:
        L.append(f"| {_md(c['description'])} | `{json.dumps(c['canonical'])}` | `{c['response']}` | {c['expectedCode']} | {c['actualCode']} | {c['ok']} |")
    L += ["", f"Codes reached: {', '.join(intv['codesReached'])}.", ""]

    L += ["## Misconceptions exercised by task", ""]
    for task, ids in pack["misconceptions"]["exercisedByTask"].items():
        L.append(f"- **{task}** ({len(ids)}): {', '.join(ids)}")
    L.append("")

    L += ["## MC interaction policy", "", "| task | rule | ok | detail |", "|---|---|---|---|"]
    for r in pack["mcPolicy"]["rows"]:
        L.append(f"| {r['task']} | {r['rule']} | {r['ok']} | {_md(r['detail'])} |")
    L.append("")

    L += ["## Exemplars", "",
          "Each exemplar is reproducible from its seed; LaTeX prompt blocks are shown between `$ … $`.", ""]
    for r in pack["records"]:
        L += [f"### {r['task']} — seed {r['seed']} — band {r['band']} ({r['answerType']}, {r['interactionType']})", ""]
        L += ["| field | value |", "|---|---|"]
        L.append(_row("objective", r["objectiveId"]))
        L.append(_row("interaction / answer", f"{r['interactionType']} / {r['answerType']}"))
        L.append(_row("difficulty band", f"{r['band']} (axes: {json.dumps(r['axes'])})"))
        L.append(_row("prompt", _md(r["prompt"])))
        L.append(_row("spoken math", _md(r["spokenMath"])))
        L.append(_row("params", f"`{_md(json.dumps(r['params']))}`"))
        L.append(_row("canonical answer", f"`{_md(json.dumps(r['canonicalAnswer']))}`"))
        L.append(_row("answer display", _md(r["answerDisplay"])))
        L.append(_row("accepted form / checker", _md(r["acceptedFormOrCheckerBehaviour"])))
        L.append(_row("worked solution", _md("; ".join(
            f"{s['number']}. {s['transformation']}" + (f" -> {s['intermediateResult']}" if s.get("intermediateResult") else "")
            for s in r["workedSolution"]))))
        if "options" in r:
            opt = "; ".join(f"{o['label']}={o['display']}{' ✓' if o.get('correct') else ''}" for o in r["options"])
            L.append(_row("MC options", _md(opt)))
            fb = "; ".join(f"{d['misconceptionId']} ({d['display']}): {d['feedback']}" for d in r["distractors"])
            L.append(_row("distractor feedback", _md(fb)))
        L.append(_row("validation checks", f"{sum(1 for c in r['validationChecks'] if c['ok'])}/{len(r['validationChecks'])} pass"))
        L.append(_row("covers cells", ", ".join(f"`{c}`" for c in r["coversCells"])))
        L.append(_row("reproduction", f"`{_md(r['reproductionCommand'])}`"))
        L.append(_row("curriculum-review decision", "☐ APPROVE ☐ REVISE ☐ REJECT"))
        L.append("")

    with open(os.path.join(REVIEW_DIR, "functions_review_pack.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
