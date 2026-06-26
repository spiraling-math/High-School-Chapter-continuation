"""gen.proportion.ratio oracle driver: golden vectors (12 task-complete seed-7 + a few mixed), a
task-pinned parity fixture (12 tasks x >=26 seeds = >=312), a 10,000-seed validation sweep + per-task
distribution report (every declared band reachable before fixtures are frozen), the RATIO-CHECKER MATRIX
(all 9 ratio result codes reachable; the accept/reject policy proved), the MC-policy counts
(FR-ineligible tasks reject MC; best_buy rejects FR), and diagnostic coverage.

  python oracle/run_ratio.py                 # full run (SPI_SWEEP defaults to 10000)
  SPI_SWEEP=2000 python oracle/run_ratio.py

Writes:
  oracle/golden/ratio.golden.json            curated, task-complete golden vectors
  oracle/golden/ratio.parity.json            task-pinned parity fixture (12 tasks x >=26 seeds)
  docs/review/ratio_distribution.json        the distribution + checker matrix + coverage report

Exit 0 iff invalid==0 AND every declared band reachable AND all 9 ratio codes reachable AND the MC
policy is correct (FR-ineligible tasks reject MC; best_buy rejects FR; all MC-eligible accept MC) AND
the generator is reproducible (generate twice -> identical serialize).
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))
sys.path.insert(0, HERE)

from spi_oracle import ratio as R  # noqa: E402
from spi_oracle import ratio_core as RC  # noqa: E402
from spi_oracle import ratio_misconceptions as RM  # noqa: E402

GOLDEN_DIR = os.path.join(HERE, "golden")
REVIEW_DIR = os.path.join(ROOT, "docs", "review")
PARITY_SEEDS_PER_TASK = int(os.environ.get("SPI_PARITY_SEEDS_PER_TASK", "30"))   # 12*30 = 360 >= 312
SWEEP = int(os.environ.get("SPI_SWEEP", "10000"))


def _cfg(task: str) -> dict:
    cfg = {"task": task}
    if task in R.MC_ONLY_TASKS:
        cfg["interactionType"] = "multiple-choice"
    return cfg


def _checker_matrix() -> dict:
    """Owner I/J: prove all 9 ratio result codes are reachable, with the accept/reject policy:
    2:3 accepts 4:6 (equivalent), rejects 3:2 (order); 2:3:5 accepts 4:6:10; unsimplified is
    accepted or flagged per the require_simplest policy; zero/negative/malformed/extra-text rejected;
    spaces accepted."""
    cases = []

    def case(expected, text, require_simplest, want):
        got = RC.check_ratio(expected, text, require_simplest=require_simplest)["code"]
        cases.append({"expected": RC.format_ratio(expected), "response": text,
                      "requireSimplest": require_simplest, "expectedCode": want,
                      "actualCode": got, "ok": got == want})

    case([2, 3], "2:3", True, "correct")
    case([2, 3], "4:6", True, "equivalent-not-simplified")     # SIMPLIFY policy flags unsimplified
    case([2, 3], "4:6", False, "correct")                      # equivalence policy accepts it
    case([2, 3], "3:2", True, "wrong-order")                   # order-sensitive
    case([2, 3, 5], "4:6:10", False, "correct")                # three-part equivalence accepted
    case([2, 3, 5], "4:6:10", True, "equivalent-not-simplified")
    case([2, 3], "2:5", True, "wrong-ratio")
    case([2, 3], "2:3:5", True, "wrong-number-of-parts")       # extra part
    case([2, 3], "0:3", True, "zero-or-negative-part")
    case([2, 3], "-2:3", True, "zero-or-negative-part")
    case([2, 3], "2 : 3", True, "correct")                     # spaces accepted
    case([2, 3], "2:3 cats", True, "unparsed-trailing-text")   # extra text rejected
    case([2, 3], "2 to 3", True, "unsupported-term")           # word form rejected
    case([2, 3], "", True, "malformed-response")               # empty rejected
    case([2, 3], "2,3", True, "unsupported-term")              # comma-separated rejected

    reached = {c["actualCode"] for c in cases}
    return {"cases": cases, "mismatches": sum(1 for c in cases if not c["ok"]),
            "codesReached": sorted(reached),
            "allCodesReachable": all(code in reached for code in RC.RATIO_RESULT_CODES),
            "ratioCodes": list(RC.RATIO_RESULT_CODES)}


def _band_lever(task: str, params: dict) -> bool:
    return R._is_high_complexity(task, params)


def main() -> int:
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    os.makedirs(REVIEW_DIR, exist_ok=True)

    # 1) Golden vectors — task-complete (seed 7) + a few mixed.
    golden = []
    for task in R.RATIO_TASKS:
        item = R.generate(7, _cfg(task))
        golden.append({"seed": 7, "task": task, "interaction": item["interactionType"],
                       "serialized": R.serialize(item), "valid": R.validate(item)["valid"]})
    for s in (1, 42, 123456789, 2147483647):
        item = R.generate(s)
        golden.append({"seed": s, "task": None, "interaction": item["interactionType"],
                       "serialized": R.serialize(item), "valid": R.validate(item)["valid"]})
    with open(os.path.join(GOLDEN_DIR, "ratio.golden.json"), "w", encoding="utf-8") as fh:
        json.dump(golden, fh, indent=2)
    print(f"Golden vectors: {len(golden)} entries (12 task-complete + 4 mixed).")

    # 2) Task-pinned parity fixture (12 tasks x >=26 seeds = >=312; owner P).
    parity = []
    for task in R.RATIO_TASKS:
        cfg = _cfg(task)
        for s in range(1, PARITY_SEEDS_PER_TASK + 1):
            parity.append({"seed": s, "task": task, "interaction": cfg.get("interactionType", "free-response"),
                           "serialized": R.serialize(R.generate(s, cfg))})
    with open(os.path.join(GOLDEN_DIR, "ratio.parity.json"), "w", encoding="utf-8") as fh:
        json.dump(parity, fh, indent=0)
    print(f"Parity fixture: {len(parity)} entries (task-pinned; {PARITY_SEEDS_PER_TASK}/task).")

    # 3) MC policy: FR-ineligible tasks reject MC; best_buy rejects FR; all MC-eligible accept MC.
    mc_rejected_fr_only = 0       # FR-only tasks that correctly reject an MC request
    mc_accepted_eligible = 0      # MC-eligible (non-best_buy) tasks that accept an MC request
    best_buy_rejects_fr = False
    for task in R.RATIO_TASKS:
        if task in R.MC_ONLY_TASKS:
            try:
                R.generate(1, {"task": task, "interactionType": "free-response"})
            except R.InteractionNotSupported:
                best_buy_rejects_fr = True
        elif task in R.MC_ELIGIBLE_TASKS:
            try:
                it = R.generate(1, {"task": task, "interactionType": "multiple-choice"})
                if it["interactionType"] == "multiple-choice":
                    mc_accepted_eligible += 1
            except R.InteractionNotSupported:
                pass
        else:
            try:
                R.generate(1, {"task": task, "interactionType": "multiple-choice"})
            except R.InteractionNotSupported:
                mc_rejected_fr_only += 1
    fr_only_tasks = [t for t in R.RATIO_TASKS if t not in R.MC_ELIGIBLE_TASKS]
    mc_eligible_non_best = [t for t in R.MC_ELIGIBLE_TASKS if t not in R.MC_ONLY_TASKS]
    mc_policy_ok = (mc_rejected_fr_only == len(fr_only_tasks)
                    and mc_accepted_eligible == len(mc_eligible_non_best)
                    and best_buy_rejects_fr)

    # 4) Sweep + distribution (owner O). Reproducibility: generate twice -> identical serialize.
    print(f"Validation sweep + distribution: {SWEEP} seeds")
    per = defaultdict(lambda: {"items": 0, "bands": Counter(), "answerType": Counter(),
                               "interaction": Counter(), "high": 0, "low": 0,
                               "fractionResult": 0, "edgeFixed": 0})
    invalid = 0
    nonreproducible = 0
    failing = []
    for s in range(1, SWEEP + 1):
        item = R.generate(s)
        if R.serialize(item) != R.serialize(R.generate(s)):
            nonreproducible += 1
        v = R.validate(item)
        if not v["valid"]:
            invalid += 1
            if len(failing) < 50:
                failing.append({"seed": s, "task": item["params"]["task"],
                                "checks": [c for c in v["checks"] if not c["ok"]]})
        p = item["params"]
        task = p["task"]
        info = per[task]
        info["items"] += 1
        info["bands"][item["difficulty"]["overallBand"]] += 1
        info["answerType"][item["answer"]["type"]] += 1
        info["interaction"][item["interactionType"]] += 1
        if _band_lever(task, p):
            info["high"] += 1
        else:
            info["low"] += 1
        sol = R._solve(task, p)
        if isinstance(sol, Fraction) and sol.denominator > 1:
            info["fractionResult"] += 1
        # an "edge" instance: a unit-scale (one part value 1) or a fixed coincidence in sharing
        if task in ("share_two_part", "share_three_part") and min(p["parts"]) == 1:
            info["edgeFixed"] += 1

    report = {"generatorId": R.GENERATOR_ID, "generatorVersion": R.GENERATOR_VERSION,
              "validatorVersion": R.VALIDATOR_VERSION, "sweepSeeds": SWEEP,
              "invalid": invalid, "nonreproducible": nonreproducible,
              "mcPolicy": {"frOnlyTasksRejectingMc": mc_rejected_fr_only,
                           "frOnlyTaskCount": len(fr_only_tasks),
                           "mcEligibleAcceptingMc": mc_accepted_eligible,
                           "mcEligibleNonBestBuyCount": len(mc_eligible_non_best),
                           "bestBuyRejectsFr": best_buy_rejects_fr,
                           "ok": mc_policy_ok},
              "tasks": {}}
    for task in R.RATIO_TASKS:
        info = per[task]
        total = info["items"] or 1
        lo, hi = R.TASK_BANDS[task]
        bands = {b: info["bands"].get(b, 0) for b in range(1, 6) if info["bands"].get(b, 0)}
        unreachable = [b for b in (lo, hi) if info["bands"].get(b, 0) == 0]
        report["tasks"][task] = {
            "objectiveId": R.OBJECTIVE_BY_TASK[task], "items": info["items"],
            "declaredBand": [lo, hi], "bandCounts": bands,
            "bandPct": {b: round(100 * c / total, 1) for b, c in bands.items()},
            "unreachableDeclaredBands": unreachable,
            "answerTypes": dict(info["answerType"]), "interactions": dict(info["interaction"]),
            "highComplexity": info["high"], "lowComplexity": info["low"],
            "fractionResultItems": info["fractionResult"], "edgeItems": info["edgeFixed"],
        }

    # 5) Ratio-checker matrix (owner I/J).
    report["checkerMatrix"] = _checker_matrix()

    # 6) Diagnostic coverage (owner K). Each diagnostic's predicted response is independently
    # recomputed; for ratio tasks the expected checker code must match check_ratio.
    by_task = defaultdict(Counter)
    exercised = set()
    recompute_bad = 0
    for s in range(1, min(SWEEP, 4000) + 1):
        item = R.generate(s)
        p = item["params"]
        task = p["task"]
        for d in RM.diagnostics_for(task, p):
            by_task[task][d["misconceptionId"]] += 1
            exercised.add(d["misconceptionId"])
            # recompute the expected result code for ratio-answer tasks using the diagnostic's own
            # declared require_simplest policy (the single source of truth).
            if R.ANSWER_KIND[task] == "ratio":
                correct = RC.simplify_parts(R._solve(task, p))
                got = RC.check_ratio(correct, d["predictedResponse"],
                                     require_simplest=d.get("requireSimplest", True))["code"]
                if got != d["expectedResultCode"]:
                    recompute_bad += 1
    inapplicable = [m["misconceptionId"] for m in RM.MISCONCEPTIONS if m["misconceptionId"] not in exercised]
    report["diagnosticCoverage"] = {
        "exercisedByTask": {t: sorted(c) for t, c in by_task.items()},
        "totalRules": len(RM.MISCONCEPTIONS), "exercised": len(exercised),
        "inapplicableRules": inapplicable, "recomputationMismatches": recompute_bad,
    }

    report["allBandsReachable"] = all(not report["tasks"][t]["unreachableDeclaredBands"] for t in R.RATIO_TASKS)
    report["failures"] = failing
    with open(os.path.join(REVIEW_DIR, "ratio_distribution.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    cm = report["checkerMatrix"]
    dc = report["diagnosticCoverage"]
    print(f"Sweep: {SWEEP} items, invalid={invalid}, nonreproducible={nonreproducible}.")
    print(f"All declared bands reachable: {report['allBandsReachable']}.")
    print(f"All 9 ratio codes reachable: {cm['allCodesReachable']} (matrix mismatches {cm['mismatches']}).")
    print(f"MC policy correct: {mc_policy_ok} "
          f"(FR-only reject MC {mc_rejected_fr_only}/{len(fr_only_tasks)}, "
          f"MC-eligible accept MC {mc_accepted_eligible}/{len(mc_eligible_non_best)}, "
          f"best_buy rejects FR {best_buy_rejects_fr}).")
    print(f"Diagnostics exercised {dc['exercised']}/{dc['totalRules']} "
          f"(inapplicable {dc['inapplicableRules']}, recomputation mismatches {dc['recomputationMismatches']}).")

    ok = (invalid == 0 and nonreproducible == 0 and report["allBandsReachable"]
          and cm["allCodesReachable"] and cm["mismatches"] == 0
          and mc_policy_ok and dc["recomputationMismatches"] == 0)
    print("RESULT:", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
