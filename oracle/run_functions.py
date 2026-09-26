"""gen.functions.foundations oracle driver: golden vectors, task-pinned parity fixture, the 10,000-seed
validation sweep, and the task x band x kind distribution report.

Run:  python oracle/run_functions.py
Writes: oracle/golden/functions.golden.json, oracle/golden/functions.parity.json,
        docs/review/functions_distribution.json
Env:    SPI_SWEEP (default 10000), SPI_PARITY_SEEDS (default 20)
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))
sys.path.insert(0, HERE)

import functions as G  # noqa: E402
import functions_core as C  # noqa: E402

GOLDEN_DIR = os.path.join(HERE, "golden")
REVIEW_DIR = os.path.join(ROOT, "docs", "review")
FAIL_DIR = os.path.join(HERE, "failing_seeds")
GOLDEN_SEEDS = [1, 42, 123456789, 2147483647]
SWEEP = int(os.environ.get("SPI_SWEEP", "10000"))
PARITY_SEEDS = int(os.environ.get("SPI_PARITY_SEEDS", "20"))


def _kind_of(item: dict) -> str:
    p = item["params"]
    if "rule" in p:
        k = p["rule"]["kind"]
        return k + ("_restricted" if "restricted" in p else "")
    if "f" in p:
        return f"{p['f']['kind']}/{p['g']['kind']}:{p['order']}"
    if "form" in p:
        return p["form"]
    return "-"


def main() -> int:
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    os.makedirs(REVIEW_DIR, exist_ok=True)
    print("=" * 70)
    print("SPI-Math oracle — gen.functions.foundations", G.GENERATOR_VERSION)
    print("=" * 70)

    # 1. Golden vectors: the default-interaction no-task draw at the four golden seeds, then every task at
    #    seed 1 (default interaction) and, where eligible, in multiple-choice at seed 2.
    golden = []

    def add_golden(seed: int, cfg: dict) -> None:
        item = G.generate(seed, cfg)
        v = G.validate(item)
        golden.append({"seed": seed, "task": cfg.get("task"), "interaction": cfg.get("interactionType"),
                       "serialized": G.serialize(item), "valid": v["status"] == "pass"})
        print("-" * 70)
        print(f"[seed {seed} | {cfg.get('task') or 'auto'} | {item['interactionType']} | band {item['difficulty']['overallBand']} | validation {v['status']}]")
        print(G.render(item, "full"))

    for s in GOLDEN_SEEDS:
        add_golden(s, {})
    for t in G.TASKS:
        add_golden(1, {"task": t})
        if t not in G.MC_ONLY_TASKS:
            add_golden(2, {"task": t, "interactionType": "multiple-choice"})
    with open(os.path.join(GOLDEN_DIR, "functions.golden.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(golden, fh, indent=2, ensure_ascii=False)
    print(f"\nGolden vectors: {len(golden)} written ({sum(1 for g in golden if g['valid'])} valid).")

    # 2. Task-pinned parity fixture (both interactions where supported).
    parity = []
    for s in range(1, PARITY_SEEDS + 1):
        for t in G.TASKS:
            for inter in G.supported_interactions(t):
                parity.append({"seed": s, "task": t, "interaction": inter,
                               "serialized": G.serialize(G.generate(s, {"task": t, "interactionType": inter}))})
    with open(os.path.join(GOLDEN_DIR, "functions.parity.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(parity, fh, indent=0, ensure_ascii=False)
    print(f"Parity fixture: {len(parity)} entries written.")

    # 3. Validation sweep + distribution.
    print("\n" + "=" * 70)
    print(f"Validation sweep: {SWEEP} seeds x 2 interaction pools")
    failing = []
    by_task: dict = {}
    codes_seen: dict = {}
    for s in range(1, SWEEP + 1):
        for inter in ("free-response", "multiple-choice"):
            it = G.generate(s, {"interactionType": inter})
            v = G.validate(it)
            task = it["params"]["task"]
            if v["status"] != "pass":
                failing.append({"seed": s, "interaction": inter, "task": task,
                                "checks": [c["name"] for c in v["checks"] if c["result"] == "fail"]})
            rec = by_task.setdefault(task, {"count": 0, "bands": {}, "kinds": {}, "interactions": {}, "answerTypes": {}, "misconceptions": {}})
            rec["count"] += 1
            band = it["difficulty"]["overallBand"]
            rec["bands"][str(band)] = rec["bands"].get(str(band), 0) + 1
            k = _kind_of(it)
            rec["kinds"][k] = rec["kinds"].get(k, 0) + 1
            rec["interactions"][inter] = rec["interactions"].get(inter, 0) + 1
            at = it["answer"]["type"]
            rec["answerTypes"][at] = rec["answerTypes"].get(at, 0) + 1
            for d in it.get("distractors", []):
                rec["misconceptions"][d["misconceptionId"]] = rec["misconceptions"].get(d["misconceptionId"], 0) + 1
            if s <= 200 and G.serialize(G.generate(s, {"interactionType": inter})) != G.serialize(it):
                failing.append({"seed": s, "interaction": inter, "task": task, "checks": ["reproducibility"]})

    # every declared band reachable per task (range-based coverage gate)
    unreachable = {}
    for t, (lo, hi) in G.TASK_BANDS.items():
        seen = set(int(b) for b in by_task.get(t, {}).get("bands", {}))
        missing = [b for b in range(lo, hi + 1) if b not in seen]
        if missing:
            unreachable[t] = missing

    distribution = {
        "generatorId": G.GENERATOR_ID, "generatorVersion": G.GENERATOR_VERSION, "sweepSeeds": SWEEP,
        "interactionPools": ["free-response", "multiple-choice"],
        "declaredBands": {t: list(G.TASK_BANDS[t]) for t in G.TASKS},
        "unreachableDeclaredBands": unreachable,
        "invalidItems": len(failing),
        "byTask": {t: by_task[t] for t in G.TASKS if t in by_task},
    }
    with open(os.path.join(REVIEW_DIR, "functions_distribution.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(distribution, fh, indent=2, ensure_ascii=False)

    print(f"  invalid items      : {len(failing)}")
    for t in G.TASKS:
        rec = by_task.get(t, {"count": 0, "bands": {}})
        print(f"  {t:26s} n={rec['count']:5d} bands={dict(sorted(rec['bands'].items()))}")
    print(f"  unreachable bands  : {unreachable or 'none'}")
    if failing or unreachable:
        os.makedirs(FAIL_DIR, exist_ok=True)
        with open(os.path.join(FAIL_DIR, "functions.failing.json"), "w", encoding="utf-8") as fh:
            json.dump({"generatorId": G.GENERATOR_ID, "failing": failing[:200], "unreachable": unreachable}, fh, indent=2)
        print(f"\nRESULT: FAIL — {len(failing)} invalid; unreachable {unreachable}; first: {failing[:3]}")
        return 1
    print("\nRESULT: PASS — 0 invalid items across the sweep; every declared band reachable per task.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
