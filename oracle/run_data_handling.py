"""gen.stats.data-handling oracle driver: golden vectors, parity fixture, a 10,000-seed
validation sweep, and the per-task distribution report the owner requires (decision M)
before fixtures are frozen.

  python oracle/run_data_handling.py            # full run (SPI_SWEEP defaults to 10000)
  SPI_SWEEP=2000 python oracle/run_data_handling.py

Writes:
  oracle/golden/data_handling.golden.json       curated, task-complete golden vectors
  oracle/golden/data_handling.parity.json        150 seeds x 2 interactions (Py/TS parity)
  docs/review/stats_data_handling_distribution.json   the distribution report
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

from spi_oracle import data_handling as dh  # noqa: E402

GOLDEN_DIR = os.path.join(HERE, "golden")
REVIEW_DIR = os.path.join(ROOT, "docs", "review")
PARITY_SEEDS = int(os.environ.get("SPI_PARITY_SEEDS", "150"))
SWEEP = int(os.environ.get("SPI_SWEEP", "10000"))


def _mode_for(task: str) -> str:
    return "free-response" if task in dh.FREE_RESPONSE_ONLY else "multiple-choice"


def _attempts(seed: int, interaction: str, task: str | None = None) -> int:
    from spi_oracle.seeded_random import Mulberry32
    rng = Mulberry32(seed)
    pool = dh.MC_TASKS if (interaction == "multiple-choice" and task is None) else (dh.TASKS if task is None else (task,))
    for a in range(1, dh.MAX_PARAM_ATTEMPTS + 1):
        t = task if task is not None else pool[dh._n(rng, len(pool))]
        drawn = dh._DRAW[t](rng)
        if drawn is None:
            continue
        if dh._acceptable(drawn, interaction) is None:
            continue
        return a
    return dh.MAX_PARAM_ATTEMPTS


def _answer_kind(item) -> str:
    return item["answer"]["type"]


def _is_rational_result(item) -> bool:
    return item["answer"]["type"] == "exact-rational"


def main() -> int:
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    os.makedirs(REVIEW_DIR, exist_ok=True)

    # 1) Golden vectors — task-complete + a few mixed seeds.
    golden = []
    for task in dh.TASKS:
        cfg = {"interactionType": _mode_for(task), "task": task}
        item = dh.generate(7, cfg)
        golden.append({"seed": 7, "config": cfg, "serialized": dh.serialize(item),
                       "validation": dh.validate(item)["status"]})
    for s in (1, 42, 123456789, 2147483647):
        for cfg in ({"interactionType": "free-response"}, {"interactionType": "multiple-choice"}):
            item = dh.generate(s, cfg)
            golden.append({"seed": s, "config": cfg, "serialized": dh.serialize(item),
                           "validation": dh.validate(item)["status"]})
    with open(os.path.join(GOLDEN_DIR, "data_handling.golden.json"), "w", encoding="utf-8") as fh:
        json.dump(golden, fh, indent=2)
    print(f"Golden vectors: {len(golden)} entries (11 task-complete + 8 mixed).")

    # 2) Parity fixture — 150 seeds x 2 interactions.
    parity = []
    for s in range(1, PARITY_SEEDS + 1):
        for mode in ("free-response", "multiple-choice"):
            parity.append({"seed": s, "mode": mode,
                           "serialized": dh.serialize(dh.generate(s, {"interactionType": mode}))})
    with open(os.path.join(GOLDEN_DIR, "data_handling.parity.json"), "w", encoding="utf-8") as fh:
        json.dump(parity, fh, indent=0)
    print(f"Parity fixture: {len(parity)} entries.")

    # 3) Sweep + distribution report (decision M).
    print(f"Validation sweep + distribution report: {SWEEP} seeds x 2 modes")
    per = defaultdict(lambda: {
        "items": 0, "fr": 0, "mc": 0, "bands": Counter(), "answerTypes": Counter(),
        "intResults": 0, "ratResults": 0, "oddLen": 0, "evenLen": 0,
        "scaffolded": 0, "unscaffolded": 0, "wholePicto": 0, "halfPicto": 0,
        "probEndpoint": 0, "probInterior": 0,
    })
    failing = []
    invalid = 0
    for s in range(1, SWEEP + 1):
        for mode in ("free-response", "multiple-choice"):
            try:
                item = dh.generate(s, {"interactionType": mode})
            except Exception as e:  # pragma: no cover
                failing.append({"seed": s, "mode": mode, "error": repr(e)})
                continue
            v = dh.validate(item)
            if v["status"] != "pass":
                invalid += 1
                if len(failing) < 200:
                    failing.append({"seed": s, "mode": mode, "checks": [c for c in v["checks"] if c["result"] == "fail"]})
            task = item["params"]["task"]
            p = per[task]
            p["items"] += 1
            p["fr" if item["interactionType"] == "free-response" else "mc"] += 1
            p["bands"][item["difficulty"]["overallBand"]] += 1
            p["answerTypes"][item["answer"]["type"]] += 1
            if item["answer"]["type"] == "exact-rational":
                p["ratResults"] += 1
            elif item["answer"]["type"] in ("integer", "fraction", "table-completion"):
                p["intResults"] += 1
            ds = item["params"]["dataset"]
            vals = ds.get("values") or ds.get("frequencies") or []
            if task in ("mean_from_list", "median_from_list", "mode_from_list", "range_from_list"):
                (p["oddLen" if len(vals) % 2 else "evenLen"]).__class__  # noqa
                p["oddLen" if len(vals) % 2 else "evenLen"] += 1
            p["scaffolded" if item["params"].get("scaffold") else "unscaffolded"] += 1
            if task == "read_pictogram":
                key = ds["pictogramKey"]
                anyhalf = any((f % key) == (key // 2) and key % 2 == 0 for f in ds["frequencies"])
                p["halfPicto" if anyhalf else "wholePicto"] += 1
            if task == "single_event_probability":
                f = Fraction(item["answer"]["canonical"]["num"], item["answer"]["canonical"]["den"])
                p["probEndpoint" if f in (Fraction(0), Fraction(1), Fraction(1, 2)) else "probInterior"] += 1

    report = {"generatorId": dh.GENERATOR_ID, "generatorVersion": dh.GENERATOR_VERSION,
              "sweepSeeds": SWEEP, "modes": ["free-response", "multiple-choice"],
              "invalid": invalid, "tasks": {}}
    sample = min(SWEEP, 1500)
    for task in dh.TASKS:
        info = per[task]
        total = info["items"] or 1
        lo, hi = dh.TASK_BANDS[task]
        bands = {b: info["bands"].get(b, 0) for b in range(1, 6) if info["bands"].get(b, 0)}
        band_pct = {b: round(100 * info["bands"].get(b, 0) / total, 1) for b in bands}
        unreachable = [b for b in range(lo, hi + 1) if info["bands"].get(b, 0) == 0]
        over = [b for b, pct in band_pct.items() if pct >= 85.0]
        fr_att = [_attempts(x, "free-response", task) for x in range(1, sample + 1)] if task not in dh.FREE_RESPONSE_ONLY else []
        mc_att = [_attempts(x, "multiple-choice", task) for x in range(1, sample + 1)] if task in dh.MC_TASKS else []
        report["tasks"][task] = {
            "objectiveId": dh.OBJECTIVE_BY_TASK[task], "items": info["items"],
            "freeResponse": info["fr"], "multipleChoice": info["mc"],
            "declaredBand": [lo, hi], "bandCounts": bands, "bandPct": band_pct,
            "unreachableBands": unreachable, "overConcentratedBands": sorted(over),
            "answerTypes": dict(info["answerTypes"]),
            "integerResults": info["intResults"], "rationalResults": info["ratResults"],
            "oddListLengths": info["oddLen"], "evenListLengths": info["evenLen"],
            "scaffolded": info["scaffolded"], "unscaffolded": info["unscaffolded"],
            "wholePictograms": info["wholePicto"], "halfPictograms": info["halfPicto"],
            "probabilityEndpoint": info["probEndpoint"], "probabilityInterior": info["probInterior"],
            "avgDrawAttemptsFR": round(sum(fr_att) / len(fr_att), 3) if fr_att else None,
            "avgDrawAttemptsMC": round(sum(mc_att) / len(mc_att), 3) if mc_att else None,
            "maxDrawAttemptsMC": max(mc_att) if mc_att else None,
        }
    # Direct-chart-readability audit (owner v1.0.2 #5): sweep read_bar_chart + read_line_graph.
    read_audit = {}
    for task in ("read_bar_chart", "read_line_graph"):
        on_major = on_minor = off_grid = 0
        smallest_minor = 10 ** 9
        min_sep = 10 ** 9
        from spi_oracle.seeded_random import Mulberry32
        redraws = 0
        for s in range(1, SWEEP + 1):
            # count readability-driven redraws by replaying the draw loop
            rng = Mulberry32(s)
            for _ in range(dh.MAX_PARAM_ATTEMPTS):
                drawn = dh._DRAW[task](rng)
                if drawn is not None and dh._acceptable(drawn, "free-response") is not None:
                    break
                redraws += 1
            item = dh.generate(s, {"task": task, "interactionType": "free-response"})
            ds = item["params"]["dataset"]
            vals = ds.get("values") or ds["frequencies"]
            major, minor, ymax = dh._chart_scale(vals)
            q = vals[item["params"]["queryIndex"]]
            if q % major == 0:
                on_major += 1
            elif q % minor == 0:
                on_minor += 1
            else:
                off_grid += 1
            smallest_minor = min(smallest_minor, minor)
            min_sep = min(min_sep, dh._subdiv_px(minor, ymax))
        read_audit[task] = {
            "items": SWEEP, "queriedOnMajorTick": on_major, "queriedOnMinorTick": on_minor,
            "queriedOffGrid": off_grid, "smallestRenderedSubdivision": smallest_minor,
            "minPixelDistanceBetweenSubdivisions": min_sep,
            "readabilityRedraws": redraws, "itemsRequiringVisualEstimation": off_grid,
        }
    report["directReadAudit"] = read_audit

    with open(os.path.join(REVIEW_DIR, "stats_data_handling_distribution.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    if failing:
        with open(os.path.join(REVIEW_DIR, "stats_data_handling_failing.json"), "w", encoding="utf-8") as fh:
            json.dump({"generatorId": dh.GENERATOR_ID, "failing": failing[:200]}, fh, indent=2)

    print(f"\nDistribution report written. invalid={invalid}")
    print("Per-task bands (declared -> realised):")
    for task in dh.TASKS:
        t = report["tasks"][task]
        flag = " UNREACHABLE:" + str(t["unreachableBands"]) if t["unreachableBands"] else ""
        flag += " OVER:" + str(t["overConcentratedBands"]) if t["overConcentratedBands"] else ""
        print(f"  {task:26s} {t['declaredBand']} -> {dict(sorted(t['bandPct'].items()))}{flag}")
    print("Direct-read readability audit:")
    for task, a in read_audit.items():
        print(f"  {task:16s} major {a['queriedOnMajorTick']} / minor {a['queriedOnMinorTick']} / "
              f"OFF-GRID {a['queriedOffGrid']} | minSubdiv {a['smallestRenderedSubdivision']} "
              f"minSep {a['minPixelDistanceBetweenSubdivisions']}px | redraws {a['readabilityRedraws']}")
    return 0 if invalid == 0 and all(a["queriedOffGrid"] == 0 for a in read_audit.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
