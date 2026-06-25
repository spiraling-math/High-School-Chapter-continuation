"""gen.measurement.mensuration oracle driver: golden vectors, a task-pinned free-response parity
fixture, a 10,000-seed validation sweep, and the per-task distribution report (owner L/M) that
proves every declared band is reachable before fixtures are frozen.

  python oracle/run_mensuration.py             # full run (SPI_SWEEP defaults to 10000)
  SPI_SWEEP=2000 python oracle/run_mensuration.py

Writes:
  oracle/golden/mensuration.golden.json        curated, task-complete golden vectors (FR only)
  oracle/golden/mensuration.parity.json        task-pinned FR parity fixture (8 tasks x 38 seeds)
  docs/review/mensuration_distribution.json     the distribution report
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

from spi_oracle import mensuration as M  # noqa: E402
from spi_oracle import mensuration_units as U  # noqa: E402
from spi_oracle import mensuration_misconceptions as MM  # noqa: E402
from spi_oracle.seeded_random import Mulberry32  # noqa: E402

GOLDEN_DIR = os.path.join(HERE, "golden")
REVIEW_DIR = os.path.join(ROOT, "docs", "review")
PARITY_SEEDS_PER_TASK = int(os.environ.get("SPI_PARITY_SEEDS_PER_TASK", "38"))  # 8*38 = 304
SWEEP = int(os.environ.get("SPI_SWEEP", "10000"))


def _attempts(seed: int, task: str) -> int:
    rng = Mulberry32(seed)
    for a in range(1, M.MAX_PARAM_ATTEMPTS + 1):
        drawn = M._DRAW[task](rng)
        if drawn is None:
            continue
        q = M._solve(task, drawn)
        if not M._is_exact_acceptable(task, drawn, q):
            continue
        return a
    return M.MAX_PARAM_ATTEMPTS


def _orientation(item) -> str:
    p = item["params"]
    if p["kind"] == "rectangle":
        return "landscape" if p["width"] > p["height"] else ("portrait" if p["width"] < p["height"] else "square")
    if p["kind"] == "triangle_base_height":
        return "base>=height" if p["base"] >= p["height"] else "height>base"
    return p["corner"]


# A representative item per task for the structural quantity-checker matrix (owner L).
def _checker_matrix(item):
    ans = M._solve(item["params"]["task"], item["params"])
    val = U.format_value(ans.value)
    other = MM._other_base(ans.baseUnit)
    cases = {
        "equivalentValueCorrectUnit": U.format_quantity(ans),
        "bareNumber": val,
        "wrongBaseUnit": U.format_quantity(type(ans)(ans.dimension, other, ans.exponent, ans.value)),
        "incorrectValueCorrectUnit": U.format_quantity(type(ans)(ans.dimension, ans.baseUnit, ans.exponent, ans.value + 1)),
    }
    if ans.dimension == "area":
        cases["linearForArea"] = U.format_quantity(U.make_length(ans.value, ans.baseUnit))      # wrong-exponent
        cases["wrongDimension"] = U.format_quantity(U.make_length(ans.value, other))            # diff base+power
    else:
        cases["squareForLength"] = U.format_quantity(U.make_area(ans.value, ans.baseUnit))      # wrong-exponent
        cases["wrongDimension"] = U.format_quantity(U.make_area(ans.value, other))              # diff base+power
    return {k: U.check_response(v, ans)["code"] for k, v in cases.items()}


def main() -> int:
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    os.makedirs(REVIEW_DIR, exist_ok=True)

    # 1) Golden vectors — task-complete (seed 7) + a few mixed seeds (FR only, owner C).
    golden = []
    for task in M.TASKS:
        item = M.generate(7, task=task)
        golden.append({"seed": 7, "task": task, "serialized": M.serialize(item),
                       "validation": M.validate(item)["status"]})
    for s in (1, 42, 123456789, 2147483647):
        item = M.generate(s)
        golden.append({"seed": s, "task": None, "serialized": M.serialize(item),
                       "validation": M.validate(item)["status"]})
    with open(os.path.join(GOLDEN_DIR, "mensuration.golden.json"), "w", encoding="utf-8") as fh:
        json.dump(golden, fh, indent=2)
    print(f"Golden vectors: {len(golden)} entries (8 task-complete + 4 mixed).")

    # 2) Task-pinned free-response parity fixture (owner C).
    parity = []
    for task in M.TASKS:
        for s in range(1, PARITY_SEEDS_PER_TASK + 1):
            parity.append({"seed": s, "task": task, "mode": "free-response",
                           "serialized": M.serialize(M.generate(s, task=task))})
    with open(os.path.join(GOLDEN_DIR, "mensuration.parity.json"), "w", encoding="utf-8") as fh:
        json.dump(parity, fh, indent=0)
    print(f"Parity fixture: {len(parity)} entries (task-pinned free-response).")

    # 3) Sweep + distribution report (owner L/M).
    print(f"Validation sweep + distribution report: {SWEEP} seeds (free-response)")
    per = defaultdict(lambda: {"items": 0, "bands": Counter(), "dim": Counter(), "numKind": Counter(),
                               "baseUnit": Counter(), "orientation": Counter(), "decompMode": Counter(),
                               "hidden": Counter()})
    invalid = 0
    failing = []
    mc_rejected = 0
    for task in M.TASKS:
        try:
            M.generate(1, task=task, interaction="multiple-choice")
        except M.UnsupportedInteractionError:
            mc_rejected += 1
    for s in range(1, SWEEP + 1):
        item = M.generate(s)
        v = M.validate(item)
        if v["status"] != "pass":
            invalid += 1
            if len(failing) < 50:
                failing.append({"seed": s, "checks": [c for c in v["checks"] if c["result"] == "fail"]})
        task = item["params"]["task"]
        info = per[task]
        info["items"] += 1
        info["bands"][item["difficulty"]["overallBand"]] += 1
        m = item["answer"]["measure"]
        info["dim"][m["dimension"]] += 1
        info["numKind"]["rational" if item["answer"]["canonical"]["den"] != 1 else "integer"] += 1
        info["baseUnit"][m["baseUnit"]] += 1
        info["orientation"][_orientation(item)] += 1
        if "decompMode" in item["params"]:
            info["decompMode"][item["params"]["decompMode"]] += 1
        if "hidden" in item["params"]:
            info["hidden"][item["params"]["hidden"]] += 1

    sample = min(SWEEP, 1500)
    report = {"generatorId": M.GENERATOR_ID, "generatorVersion": M.GENERATOR_VERSION,
              "validatorVersion": M.VALIDATOR_VERSION, "sweepSeeds": SWEEP, "mode": "free-response",
              "invalid": invalid, "multipleChoiceRejectedTasks": mc_rejected, "tasks": {}}
    for task in M.TASKS:
        info = per[task]
        total = info["items"] or 1
        lo, hi = M.TASK_BANDS[task]
        bands = {b: info["bands"].get(b, 0) for b in range(1, 6) if info["bands"].get(b, 0)}
        band_pct = {b: round(100 * info["bands"].get(b, 0) / total, 1) for b in bands}
        unreachable = [b for b in range(lo, hi + 1) if info["bands"].get(b, 0) == 0]
        att = [_attempts(x, task) for x in range(1, sample + 1)]
        report["tasks"][task] = {
            "objectiveId": M.OBJECTIVE_BY_TASK[task], "items": info["items"],
            "declaredBand": [lo, hi], "bandCounts": bands, "bandPct": band_pct,
            "unreachableBands": unreachable,
            "dimensions": dict(info["dim"]), "numberKinds": dict(info["numKind"]),
            "baseUnits": dict(info["baseUnit"]), "orientations": dict(info["orientation"]),
            "decompositionModes": dict(info["decompMode"]), "hiddenRoles": dict(info["hidden"]),
            "avgDrawAttempts": round(sum(att) / len(att), 3), "maxDrawAttempts": max(att),
        }

    # 4) Structural quantity-checker matrix (owner L): every code reachable + deterministic.
    codes = Counter()
    sample_matrix = {}
    for s in range(1, min(SWEEP, 3000) + 1):
        item = M.generate(s)
        mat = _checker_matrix(item)
        for c in mat.values():
            codes[c] += 1
        t = item["params"]["task"]
        if t not in sample_matrix:
            sample_matrix[t] = {"seed": s, "answer": item["answer"]["display"], "cases": mat}
    report["quantityCheckerMatrix"] = {"codeCounts": dict(codes), "samplesByTask": sample_matrix}
    report["allCheckerCodesReachable"] = set(codes) >= set(U.RESULT_CODES) - {"malformed-response"}

    # 5) Misconception coverage (owner K): every diagnostic exercised + recomputation sound.
    misc_cov = Counter()
    misc_bad = 0
    for s in range(1, min(SWEEP, 4000) + 1):
        item = M.generate(s)
        t = item["params"]["task"]; ans = M._solve(t, item["params"])
        for d in MM.diagnostics_for(t, item["params"], ans):
            misc_cov[d["id"]] += 1
            rule = MM._BY_ID[d["id"]]
            if d["predictedResponse"] is not None and rule["expectedCode"]:
                if U.check_response(d["predictedResponse"], ans)["code"] != rule["expectedCode"]:
                    misc_bad += 1
    report["misconceptionCoverage"] = {"exercised": len(misc_cov), "total": len(MM.MISCONCEPTIONS),
                                        "counts": dict(misc_cov), "recomputationMismatches": misc_bad}

    report["allBandsReachable"] = all(not report["tasks"][t]["unreachableBands"] for t in M.TASKS)
    report["failures"] = failing
    with open(os.path.join(REVIEW_DIR, "mensuration_distribution.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    print(f"Sweep: {SWEEP} items, invalid={invalid}, MC-rejected tasks={mc_rejected}/8.")
    print(f"All declared bands reachable: {report['allBandsReachable']}.")
    print(f"All checker codes reachable: {report['allCheckerCodesReachable']}.")
    print(f"Misconceptions exercised: {len(misc_cov)}/{len(MM.MISCONCEPTIONS)} "
          f"(recomputation mismatches: {misc_bad}).")
    return 0 if invalid == 0 and report["allBandsReachable"] and mc_rejected == 8 else 1


if __name__ == "__main__":
    raise SystemExit(main())
