"""Geometry-angles oracle driver: golden vectors, parity fixture, 10,000-seed sweep.

Run:  python oracle/run_geometry_angles.py
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from spi_oracle import geometry as geo  # noqa: E402

GOLDEN_DIR = os.path.join(HERE, "golden")
FAIL_DIR = os.path.join(HERE, "failing_seeds")
GOLDEN_SEEDS = [1, 42, 123456789, 2147483647]
SWEEP = int(os.environ.get("SPI_SWEEP", "10000"))
PARITY_SEEDS = int(os.environ.get("SPI_PARITY_SEEDS", "150"))


def main() -> int:
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    print("=" * 70)
    print("SPI-Math oracle — gen.geometry.angles-figures", geo.GENERATOR_VERSION)
    print("=" * 70)

    print("\nGolden items:")
    golden = []
    for s in GOLDEN_SEEDS:
        item = geo.generate(s, {"interactionType": "multiple-choice"})
        result = geo.validate(item)
        golden.append({"seed": s, "serialized": geo.serialize(item), "validation": result["status"]})
        print("-" * 70)
        print(geo.render(item, "full"))
        print(f"[task: {item['params']['task']}]  [validation: {result['status']}]  [band: {item['difficulty']['overallBand']}]")
    with open(os.path.join(GOLDEN_DIR, "geometry_angles.golden.json"), "w", encoding="utf-8") as fh:
        json.dump(golden, fh, indent=2)

    parity = []
    for s in range(1, PARITY_SEEDS + 1):
        parity.append({"seed": s, "mode": "free-response", "serialized": geo.serialize(geo.generate(s, {"interactionType": "free-response"}))})
        parity.append({"seed": s, "mode": "multiple-choice", "serialized": geo.serialize(geo.generate(s, {"interactionType": "multiple-choice"}))})
    with open(os.path.join(GOLDEN_DIR, "geometry_angles.parity.json"), "w", encoding="utf-8") as fh:
        json.dump(parity, fh, indent=0)
    print(f"\nParity fixture: {len(parity)} entries written.")

    print("\n" + "=" * 70)
    print(f"Validation sweep: {SWEEP} seeds x 2 modes")
    failing = []
    tasks: dict = {}
    bands: dict = {}
    for s in range(1, SWEEP + 1):
        it = geo.generate(s, {"interactionType": "free-response"})
        if geo.validate(it)["status"] != "pass":
            failing.append({"seed": s, "mode": "free-response", "task": it["params"]["task"]})
        tasks[it["params"]["task"]] = tasks.get(it["params"]["task"], 0) + 1
        bands[it["difficulty"]["overallBand"]] = bands.get(it["difficulty"]["overallBand"], 0) + 1
        im = geo.generate(s, {"interactionType": "multiple-choice"})
        if geo.validate(im)["status"] != "pass":
            failing.append({"seed": s, "mode": "multiple-choice", "task": im["params"]["task"]})
        if s <= 200 and geo.serialize(geo.generate(s, {"interactionType": "multiple-choice"})) != geo.serialize(im):
            failing.append({"seed": s, "mode": "reproducibility"})

    print(f"  invalid items     : {len(failing)}")
    print(f"  task distribution : {dict(sorted(tasks.items()))}")
    print(f"  band distribution : {dict(sorted(bands.items()))}")
    if failing:
        os.makedirs(FAIL_DIR, exist_ok=True)
        with open(os.path.join(FAIL_DIR, "geometry_angles.failing.json"), "w", encoding="utf-8") as fh:
            json.dump({"generatorId": geo.GENERATOR_ID, "failing": failing[:200]}, fh, indent=2)
        print(f"\nRESULT: FAIL — {len(failing)} invalid; first: {failing[:5]}")
        return 1
    print("\nRESULT: PASS — 0 invalid items across the sweep.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
