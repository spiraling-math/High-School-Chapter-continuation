"""Oracle driver: PRNG anchors, golden vectors, and the 10,000-seed sweep.

Run:  python oracle/run_oracle.py

Writes:
  oracle/golden/prng_anchors.json            (cross-language PRNG anchors)
  oracle/golden/arithmetic_sequences.golden.json  (reviewed golden items)
  oracle/failing_seeds/arithmetic_sequences.failing.json  (only if failures)
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from spi_oracle import sequences as seq          # noqa: E402
from spi_oracle.seeded_random import Mulberry32   # noqa: E402

GOLDEN_DIR = os.path.join(HERE, "golden")
FAIL_DIR = os.path.join(HERE, "failing_seeds")
GOLDEN_SEEDS = [1, 42, 123456789, 2147483647]
SWEEP = int(os.environ.get("SPI_SWEEP", "10000"))


def prng_anchors() -> dict:
    anchors = {}
    for s in (0, 1, 42, 123456789):
        r = Mulberry32(s)
        anchors[str(s)] = [r.next_uint32() for _ in range(5)]
    return anchors


def main() -> int:
    os.makedirs(GOLDEN_DIR, exist_ok=True)

    print("=" * 70)
    print("SPI-Math oracle — gen.sequences.arithmetic", seq.GENERATOR_VERSION)
    print("=" * 70)

    # 1. PRNG anchors (the TypeScript port must reproduce these exactly).
    anchors = prng_anchors()
    with open(os.path.join(GOLDEN_DIR, "prng_anchors.json"), "w", encoding="utf-8") as fh:
        json.dump(anchors, fh, indent=2)
    print("\nPRNG anchors (first 5 uint32):")
    for s, vals in anchors.items():
        print(f"  seed {s:>10}: {vals}")

    # 2. Golden items (rendered) + canonical serialization.
    print("\nGolden items:")
    golden = []
    for s in GOLDEN_SEEDS:
        item = seq.generate(s, {"answerType": "multiple-choice"})
        result = seq.validate(item)
        golden.append({"seed": s, "serialized": seq.serialize(item), "validation": result["status"]})
        print("-" * 70)
        print(seq.render(item, "full"))
        if "options" in item:
            correct = next(o["label"] for o in item["options"] if o["correct"])
            print(f"[correct option: {correct}]  [validation: {result['status']}]"
                  f"  [band: {item['difficulty']['overallBand']}]")
    with open(os.path.join(GOLDEN_DIR, "arithmetic_sequences.golden.json"), "w", encoding="utf-8") as fh:
        json.dump(golden, fh, indent=2)

    # 3. 10,000-seed validation sweep (integer + multiple-choice modes).
    print("\n" + "=" * 70)
    print(f"Validation sweep: {SWEEP} seeds x 2 modes")
    failing = []
    tasks: dict = {}
    bands: dict = {}
    repro_checked = 0
    for s in range(1, SWEEP + 1):
        item_i = seq.generate(s, {"answerType": "integer"})
        if seq.validate(item_i)["status"] != "pass":
            failing.append({"seed": s, "mode": "integer"})
        tasks[item_i["params"]["task"]] = tasks.get(item_i["params"]["task"], 0) + 1
        bands[item_i["difficulty"]["overallBand"]] = bands.get(item_i["difficulty"]["overallBand"], 0) + 1

        item_m = seq.generate(s, {"answerType": "multiple-choice"})
        if seq.validate(item_m)["status"] != "pass":
            failing.append({"seed": s, "mode": "multiple-choice"})

        if s <= 200:  # reproducibility spot-check
            if seq.serialize(seq.generate(s, {"answerType": "multiple-choice"})) != seq.serialize(item_m):
                failing.append({"seed": s, "mode": "reproducibility"})
            repro_checked += 1

    print(f"  invalid items     : {len(failing)}")
    print(f"  reproducibility   : {repro_checked} seeds re-generated identically"
          f" ({'OK' if not any(f['mode']=='reproducibility' for f in failing) else 'FAIL'})")
    print(f"  task distribution : {dict(sorted(tasks.items()))}")
    print(f"  band distribution : {dict(sorted(bands.items()))}")

    if failing:
        os.makedirs(FAIL_DIR, exist_ok=True)
        with open(os.path.join(FAIL_DIR, "arithmetic_sequences.failing.json"), "w", encoding="utf-8") as fh:
            json.dump({"generatorId": seq.GENERATOR_ID, "generatorVersion": seq.GENERATOR_VERSION,
                       "failing": failing}, fh, indent=2)
        print(f"\nRESULT: FAIL — {len(failing)} invalid; recorded to failing_seeds/")
        return 1

    print("\nRESULT: PASS — 0 invalid items across the sweep.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
