"""coordinate-lines oracle driver: golden vectors, parity fixture, 10,000-seed sweep,
and the per-task difficulty/answer distribution report the owner requires before fixtures
freeze (owner decision G).

Run:  python oracle/run_coordinate_lines.py
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from spi_oracle import coordinate_lines as cl  # noqa: E402

GOLDEN_DIR = os.path.join(HERE, "golden")
FAIL_DIR = os.path.join(HERE, "failing_seeds")
REVIEW_DIR = os.path.join(ROOT, "docs", "review")
GOLDEN_SEEDS = [1, 42, 123456789, 2147483647]
SWEEP = int(os.environ.get("SPI_SWEEP", "10000"))
PARITY_SEEDS = int(os.environ.get("SPI_PARITY_SEEDS", "150"))


def _attempts(seed: int, interaction: str) -> int:
    """Reproduce generate()'s redraw loop to measure the redraw rate."""
    rng = cl.Mulberry32(seed)
    pool = cl.MC_TASKS if interaction == "multiple-choice" else cl.TASKS
    for a in range(1, cl.MAX_PARAM_ATTEMPTS + 1):
        task = rng.choice(pool)
        drawn = cl._DRAW[task](rng)
        if drawn is None:
            continue
        if cl._acceptable(drawn, interaction) is None:
            continue
        return a
    return cl.MAX_PARAM_ATTEMPTS


def main() -> int:
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    os.makedirs(REVIEW_DIR, exist_ok=True)
    print("=" * 70)
    print("SPI-Math oracle — gen.geometry.coordinate-lines", cl.GENERATOR_VERSION)
    print("=" * 70)

    print("\nGolden items:")
    golden = []
    for s in GOLDEN_SEEDS:
        item = cl.generate(s, {"interactionType": "multiple-choice"})
        result = cl.validate(item)
        golden.append({"seed": s, "serialized": cl.serialize(item), "validation": result["status"]})
        print("-" * 70)
        print(cl.render(item, "full"))
        print(f"[task: {item['params']['task']}]  [validation: {result['status']}]  [band: {item['difficulty']['overallBand']}]")
    with open(os.path.join(GOLDEN_DIR, "coordinate_lines.golden.json"), "w", encoding="utf-8") as fh:
        json.dump(golden, fh, indent=2)

    parity = []
    for s in range(1, PARITY_SEEDS + 1):
        parity.append({"seed": s, "mode": "free-response", "serialized": cl.serialize(cl.generate(s, {"interactionType": "free-response"}))})
        parity.append({"seed": s, "mode": "multiple-choice", "serialized": cl.serialize(cl.generate(s, {"interactionType": "multiple-choice"}))})
    with open(os.path.join(GOLDEN_DIR, "coordinate_lines.parity.json"), "w", encoding="utf-8") as fh:
        json.dump(parity, fh, indent=0)
    print(f"\nParity fixture: {len(parity)} entries written.")

    print("\n" + "=" * 70)
    print(f"Validation sweep + distribution report: {SWEEP} seeds x 2 modes")
    failing = []
    per_task: dict = {t: {"count": 0, "bands": {}} for t in cl.TASKS}
    grad = {"integer": 0, "rational": 0, "positive": 0, "negative": 0, "zero": 0}
    mid = {"integer": 0, "halfInteger": 0}
    for s in range(1, SWEEP + 1):
        it = cl.generate(s, {"interactionType": "free-response"})
        if cl.validate(it)["status"] != "pass":
            failing.append({"seed": s, "mode": "free-response", "task": it["params"]["task"]})
        t = it["params"]["task"]
        b = it["difficulty"]["overallBand"]
        per_task[t]["count"] += 1
        per_task[t]["bands"][b] = per_task[t]["bands"].get(b, 0) + 1
        if t == "gradient_two_points":
            m = cl._solve_gradient(it["params"])
            grad["integer" if m.denominator == 1 else "rational"] += 1
            grad["zero" if m == 0 else ("positive" if m > 0 else "negative")] += 1
        if t == "midpoint":
            mx, my = cl._solve_midpoint(it["params"])
            mid["integer" if (mx.denominator == 1 and my.denominator == 1) else "halfInteger"] += 1
        im = cl.generate(s, {"interactionType": "multiple-choice"})
        if cl.validate(im)["status"] != "pass":
            failing.append({"seed": s, "mode": "multiple-choice", "task": im["params"]["task"]})
        if s <= 200 and cl.serialize(cl.generate(s, {"interactionType": "multiple-choice"})) != cl.serialize(im):
            failing.append({"seed": s, "mode": "reproducibility"})

    # Redraw rate over a sample.
    sample = 2000
    fr_att = sum(_attempts(s, "free-response") for s in range(1, sample + 1)) / sample
    mc_att = sum(_attempts(s, "multiple-choice") for s in range(1, sample + 1)) / sample

    report = {"generatorId": cl.GENERATOR_ID, "generatorVersion": cl.GENERATOR_VERSION,
              "sweep": SWEEP, "invalid": len(failing), "perTask": {}, "gradient": grad,
              "midpoint": mid, "redraw": {"sampleSeeds": sample,
                                          "freeResponseAvgAttempts": round(fr_att, 3),
                                          "multipleChoiceAvgAttempts": round(mc_att, 3)}}
    for t in cl.TASKS:
        info = per_task[t]
        n = info["count"]
        lo, hi = cl.TASK_BANDS[t]
        bands = {b: info["bands"].get(b, 0) for b in range(1, 6) if info["bands"].get(b, 0)}
        pct = {b: round(100.0 * c / n, 1) for b, c in bands.items()} if n else {}
        unreachable = [b for b in range(lo, hi + 1) if info["bands"].get(b, 0) == 0]
        over = [b for b, p in pct.items() if p > 70.0]
        report["perTask"][t] = {"count": n, "objectiveRange": [lo, hi], "bands": bands,
                                "bandPct": pct, "unreachableBands": unreachable, "overConcentratedBands": over}
        print(f"  {t:26s} n={n:5d}  bands%={pct}  unreachable={unreachable}  over={over}")
    print(f"  gradient: {grad}")
    print(f"  midpoint: {mid}")
    print(f"  redraw avg attempts: FR={fr_att:.2f}  MC={mc_att:.2f}")

    with open(os.path.join(REVIEW_DIR, "coordinate_lines_distribution.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    print(f"\n  invalid items     : {len(failing)}")
    if failing:
        os.makedirs(FAIL_DIR, exist_ok=True)
        with open(os.path.join(FAIL_DIR, "coordinate_lines.failing.json"), "w", encoding="utf-8") as fh:
            json.dump({"generatorId": cl.GENERATOR_ID, "failing": failing[:200]}, fh, indent=2)
        print(f"\nRESULT: FAIL — {len(failing)} invalid; first: {failing[:5]}")
        return 1
    print("\nRESULT: PASS — 0 invalid items across the sweep.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
