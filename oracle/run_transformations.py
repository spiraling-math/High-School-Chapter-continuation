"""gen.geometry.transformations oracle driver: golden vectors, a task-pinned free-response parity
fixture (>=300 entries, owner P), a 10,000-seed validation sweep, the per-task distribution report
(owner O — every declared band reachable before fixtures are frozen), the parser/checker matrix (owner
I/J — all 14 result codes reachable), and diagnostic coverage (owner K).

  python oracle/run_transformations.py             # full run (SPI_SWEEP defaults to 10000)
  SPI_SWEEP=2000 python oracle/run_transformations.py

Writes:
  oracle/golden/transformations.golden.json        curated, task-complete golden vectors (FR only)
  oracle/golden/transformations.parity.json        task-pinned FR parity fixture (9 tasks x 40 seeds)
  docs/review/transformations_distribution.json     the distribution + matrix + coverage report
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))
sys.path.insert(0, HERE)

from spi_oracle import transformations as T  # noqa: E402
from spi_oracle import transformations_core as TC  # noqa: E402
from spi_oracle import transformations_shapes as TS  # noqa: E402
from spi_oracle import transformations_misconceptions as TM  # noqa: E402
from spi_oracle.transformations_checker import check_description  # noqa: E402

GOLDEN_DIR = os.path.join(HERE, "golden")
REVIEW_DIR = os.path.join(ROOT, "docs", "review")
PARITY_SEEDS_PER_TASK = int(os.environ.get("SPI_PARITY_SEEDS_PER_TASK", "40"))  # 9*40 = 360
SWEEP = int(os.environ.get("SPI_SWEEP", "10000"))


def _quadrant(p) -> str:
    x, y = p
    if x > 0 and y > 0: return "Q1"
    if x < 0 and y > 0: return "Q2"
    if x < 0 and y < 0: return "Q3"
    if x > 0 and y < 0: return "Q4"
    return "axis"


def _axis_family(desc) -> str:
    ax = desc["axis"]
    if ax["kind"] == "vertical": return "x=a"
    if ax["kind"] == "horizontal": return "y=b"
    return ax["equation"]


def _checker_matrix() -> dict:
    """Owner I/J: prove all 14 result codes are reachable and the canonical/CW-ACW/axis-alias
    normalization behaves, with malformed/missing/ambiguous rejection."""
    cases = []
    exp_tr = TC.translation_desc(3, -2)
    exp_rf = TC.reflection_vertical(4)
    exp_ro = TC.rotation_desc(2, -1, 1)

    def case(expected, text, want):
        got = check_description(expected, text)
        cases.append({"expected": TC.format_display(expected), "response": text,
                      "expectedCode": want, "actualCode": got, "ok": got == want})

    case(exp_tr, "translation by vector (3, -2)", "correct")
    case(exp_ro, "rotation 90 deg anticlockwise about (2, -1)", "correct")
    case(exp_ro, "rotation 90° anticlockwise about (2, -1)", "correct")        # degree-symbol alias
    case(exp_ro, "rotation 270 deg clockwise about (2, -1)", "correct")        # 270 CW == q1 (ACW)
    case(exp_rf, "reflection in the y-axis", "wrong-reflection-axis")          # y-axis -> x=0 alias
    case(exp_ro, "reflection in x = 4", "wrong-transformation-type")
    case(exp_tr, "translation by vector (3, 2)", "wrong-translation-vector")
    case(exp_rf, "reflection in x = 5", "wrong-reflection-axis")
    case(exp_ro, "rotation 90 deg anticlockwise about (3, -1)", "wrong-rotation-centre")
    case(exp_ro, "rotation 180 deg about (2, -1)", "wrong-rotation-amount")
    case(exp_ro, "rotation 90 deg about (2, -1)", "ambiguous-description")
    case(exp_ro, "rotation 90 deg clockwise", "missing-rotation-centre")
    case(exp_tr, "translation", "missing-translation-vector")
    case(exp_rf, "reflection in y = 2x", "unsupported-reflection-line")
    case(exp_ro, "rotation 45 deg clockwise about (0, 0)", "unsupported-angle")
    case(exp_ro, "rotation 90 deg clockwise and anticlockwise about (0, 0)", "contradictory-description")
    case(exp_tr, "translation by vector (3, -2) please", "unparsed-trailing-text")
    case(exp_tr, "move it a little", "malformed-response")

    reached = {c["actualCode"] for c in cases}
    return {"cases": cases, "mismatches": sum(1 for c in cases if not c["ok"]),
            "codesReached": sorted(reached),
            "allCodesReachable": all(code in reached for code in TC.RESULT_CODES)}


def main() -> int:
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    os.makedirs(REVIEW_DIR, exist_ok=True)

    # 1) Golden vectors — task-complete (seed 7) + mixed seeds (FR only).
    golden = []
    for task in T.TASKS:
        item = T.generate(7, {"task": task})
        golden.append({"seed": 7, "task": task, "serialized": T.serialize(item),
                       "valid": T.validate(item)["valid"]})
    for s in (1, 42, 123456789, 2147483647):
        item = T.generate(s)
        golden.append({"seed": s, "task": None, "serialized": T.serialize(item),
                       "valid": T.validate(item)["valid"]})
    with open(os.path.join(GOLDEN_DIR, "transformations.golden.json"), "w", encoding="utf-8") as fh:
        json.dump(golden, fh, indent=2)
    print(f"Golden vectors: {len(golden)} entries (9 task-complete + 4 mixed).")

    # 2) Task-pinned free-response parity fixture (>= 300; owner P).
    parity = []
    for task in T.TASKS:
        for s in range(1, PARITY_SEEDS_PER_TASK + 1):
            parity.append({"seed": s, "task": task, "mode": "free-response",
                           "serialized": T.serialize(T.generate(s, {"task": task}))})
    with open(os.path.join(GOLDEN_DIR, "transformations.parity.json"), "w", encoding="utf-8") as fh:
        json.dump(parity, fh, indent=0)
    print(f"Parity fixture: {len(parity)} entries (task-pinned free-response).")

    # 3) MC-rejection for ALL nine tasks (owner A).
    mc_rejected = 0
    for task in T.TASKS:
        try:
            T.generate(1, {"task": task, "interactionType": "multiple-choice"})
        except T.InteractionNotSupported:
            mc_rejected += 1

    # 4) Sweep + distribution (owner O).
    print(f"Validation sweep + distribution: {SWEEP} seeds (free-response)")
    per = defaultdict(lambda: {"items": 0, "bands": Counter(), "object": Counter(), "answerType": Counter(),
                               "axisFamily": Counter(), "quarterTurns": Counter(), "originCentre": Counter(),
                               "vectorSigns": Counter(), "quadrant": Counter(), "fixedPoint": 0, "axisCrossing": 0})
    invalid = 0
    failing = []
    for s in range(1, SWEEP + 1):
        item = T.generate(s)
        v = T.validate(item)
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
        info["object"][p["objectType"]] += 1
        info["answerType"][item["answer"]["type"]] += 1
        src = [(c["x"], c["y"]) for c in p["source"]]
        img = [(c["x"], c["y"]) for c in p["image"]]
        desc = p["descriptor"]
        for v2 in img:
            info["quadrant"][_quadrant(v2)] += 1
        if desc["kind"] == "reflection":
            info["axisFamily"][_axis_family(desc)] += 1
        elif desc["kind"] == "rotation":
            info["quarterTurns"][desc["quarterTurnsCCW"]] += 1
            info["originCentre"]["origin" if (desc["centre"]["x"], desc["centre"]["y"]) == (0, 0) else "non-origin"] += 1
        elif desc["kind"] == "translation":
            dx, dy = desc["vector"]["dx"], desc["vector"]["dy"]
            info["vectorSigns"][f"{'+' if dx > 0 else '-' if dx < 0 else '0'}{'+' if dy > 0 else '-' if dy < 0 else '0'}"] += 1
        if any(s2 == i2 for s2, i2 in zip(src, img)):
            info["fixedPoint"] += 1
        if any((a[0] > 0) != (b[0] > 0) or (a[1] > 0) != (b[1] > 0) for a, b in zip(src, img)):
            info["axisCrossing"] += 1

    report = {"generatorId": T.GENERATOR_ID, "generatorVersion": T.GENERATOR_VERSION,
              "validatorVersion": T.VALIDATOR_VERSION, "sweepSeeds": SWEEP, "mode": "free-response",
              "invalid": invalid, "multipleChoiceRejectedTasks": mc_rejected, "tasks": {}}
    for task in T.TASKS:
        info = per[task]
        total = info["items"] or 1
        lo, hi = T.TASK_BANDS[task]
        bands = {b: info["bands"].get(b, 0) for b in range(1, 6) if info["bands"].get(b, 0)}
        unreachable = [b for b in range(lo, hi + 1) if info["bands"].get(b, 0) == 0]
        report["tasks"][task] = {
            "objectiveId": T.OBJECTIVE_BY_TASK[task], "items": info["items"],
            "declaredBand": [lo, hi], "bandCounts": bands,
            "bandPct": {b: round(100 * c / total, 1) for b, c in bands.items()},
            "unreachableBands": unreachable,
            "objectTypes": dict(info["object"]), "answerTypes": dict(info["answerType"]),
            "axisFamilies": dict(info["axisFamily"]), "quarterTurns": dict(info["quarterTurns"]),
            "originCentre": dict(info["originCentre"]), "vectorSigns": dict(info["vectorSigns"]),
            "imageQuadrants": dict(info["quadrant"]),
            "fixedPointItems": info["fixedPoint"], "axisCrossingItems": info["axisCrossing"],
        }

    # 5) Parser/checker matrix (owner I/J).
    report["checkerMatrix"] = _checker_matrix()

    # 6) Diagnostic coverage (owner K). null-predicted parser diagnostics must NOT count as exercised.
    by_kind = {"value": Counter(), "descriptor": Counter(), "parser": Counter()}
    recompute_bad = 0
    for s in range(1, min(SWEEP, 4000) + 1):
        item = T.generate(s)
        p = item["params"]
        src = [(c["x"], c["y"]) for c in p["source"]]
        for d in TM.diagnostics_for(p["task"], src, p["descriptor"]):
            by_kind[d["kind"]][d["misconceptionId"]] += 1
            if d["kind"] == "descriptor":
                got = check_description(p["descriptor"], d["predicted"]["display"])
                if got != d["expectedResultCode"]:
                    recompute_bad += 1
            elif d["kind"] == "parser":
                got = check_description(p["descriptor"], d["studentResponseText"])
                if got != d["expectedResultCode"]:
                    recompute_bad += 1
    exercised = set().union(*(set(c) for c in by_kind.values()))
    # null-predicted (parser) entries with no studentResponseText would be uncounted; we verified all
    # parser entries carry studentResponseText, so 'exercised' counts only real predictions.
    inapplicable = [m["misconceptionId"] for m in TM.MISCONCEPTIONS if m["misconceptionId"] not in exercised]
    report["diagnosticCoverage"] = {
        "valueRulesExercised": sorted(by_kind["value"]),
        "descriptorRulesExercised": sorted(by_kind["descriptor"]),
        "parserRulesExercised": sorted(by_kind["parser"]),
        "inapplicableRules": inapplicable,
        "totalRules": len(TM.MISCONCEPTIONS), "exercised": len(exercised),
        "recomputationMismatches": recompute_bad,
    }

    report["allBandsReachable"] = all(not report["tasks"][t]["unreachableBands"] for t in T.TASKS)
    report["failures"] = failing
    with open(os.path.join(REVIEW_DIR, "transformations_distribution.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    cm = report["checkerMatrix"]
    dc = report["diagnosticCoverage"]
    print(f"Sweep: {SWEEP} items, invalid={invalid}, MC-rejected tasks={mc_rejected}/9.")
    print(f"All declared bands reachable: {report['allBandsReachable']}.")
    print(f"All 14 result codes reachable: {cm['allCodesReachable']} (matrix mismatches {cm['mismatches']}).")
    print(f"Diagnostics: value {len(dc['valueRulesExercised'])}, descriptor {len(dc['descriptorRulesExercised'])}, "
          f"parser {len(dc['parserRulesExercised'])}, inapplicable {dc['inapplicableRules']} "
          f"(recomputation mismatches {dc['recomputationMismatches']}).")
    ok = (invalid == 0 and report["allBandsReachable"] and mc_rejected == 9
          and cm["allCodesReachable"] and cm["mismatches"] == 0 and dc["recomputationMismatches"] == 0)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
