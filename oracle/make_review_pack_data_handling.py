"""Build the gen.stats.data-handling review pack (owner decision O).

Coverage-driven selection over seeds: greedily collect items until every required
dimension is covered — all 11 tasks, both interactions, every realised band, every answer
type, every approved misconception rule, every chart/table representation, vertical
bar-chart scales {1,2,5,10}, whole + half pictograms, odd + even medians, integer +
fractional means, a unique mode, range = 0 and positive ranges, negative list values,
P = 0 / 1 / 1/2 / other, and blank-vs-completed frequency tables.

Writes:
  docs/review/stats_data_handling_review_pack.md
  docs/review/stats_data_handling_review_pack.json
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

from spi_oracle import data_handling as dh  # noqa: E402
from spi_oracle import data_handling_misconceptions as mis  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
MAX_SEED = 6000
GATHER_SEEDS = 500   # per task per interaction — enough to surface every reachable cell


def _axis_step(item) -> int | None:
    task = item["params"]["task"]
    ds = item["params"]["dataset"]
    if task == "read_bar_chart":
        return dh._axis_step_and_max(max(ds["frequencies"]))[0]
    return None


def _features(item):
    """Return the set of coverage tokens an item satisfies."""
    task = item["params"]["task"]
    ds = item["params"]["dataset"]
    it = item["interactionType"]
    toks = {f"task:{task}", f"interaction:{task}:{it}", f"band:{task}:{item['difficulty']['overallBand']}",
            f"answer:{item['answer']['type']}"}
    for o in item.get("options", []):
        if o.get("misconceptionId"):
            toks.add(f"misc:{o['misconceptionId']}")
    if task in ("read_bar_chart", "read_line_graph"):
        vals = ds.get("values") or ds["frequencies"]
        major, minor, _ymax = dh._chart_scale(vals)
        q = vals[item["params"]["queryIndex"]]
        if task == "read_bar_chart":
            toks.add(f"barscale:{major}")
        if minor < major and q % major != 0:               # queried value resolved by a minor subdivision
            toks.add(f"{'bar' if task == 'read_bar_chart' else 'line'}:minor-subdiv")
    if task == "read_pictogram":
        key = ds["pictogramKey"]
        anyhalf = any((f % key) == (key // 2) and key % 2 == 0 for f in ds["frequencies"])
        toks.add("picto:half" if anyhalf else "picto:whole")
    if task == "median_from_list":
        toks.add("median:odd" if len(ds["values"]) % 2 else "median:even")
    if task == "mean_from_list":
        f = dh._solve(task, item["params"])
        toks.add("mean:frac" if (isinstance(f, Fraction) and f.denominator > 1) else "mean:int")
    if task == "range_from_list":
        toks.add("range:zero" if dh._solve(task, item["params"]) == 0 else "range:pos")
    if task in ("mean_from_list", "median_from_list", "mode_from_list", "range_from_list"):
        if any(v < 0 for v in ds["values"]):
            toks.add("list:negative")
            dom = dh.CONTEXT_DOMAINS.get(ds.get("title"))
            if dom in ("signed", "context-free"):
                toks.add("list:signed-context-free")     # a negative list in a permitted context (#1/#11)
        # an averages MC item demonstrates mode-distractor handling (#2/#11)
        if task in ("mean_from_list", "median_from_list", "range_from_list") and it == "multiple-choice":
            mids = [o.get("misconceptionId") for o in item.get("options", [])]
            if "MISC.STAT.AVG_USES_MODE" in mids:
                toks.add("misc-mode-valid")             # a valid unique-mode distractor
            elif dh.unique_mode(ds["values"]) is None:
                toks.add("no-mode-rejected")            # no-mode dataset, mode distractor correctly NOT used
    if task == "single_event_probability":
        f = dh._solve(task, item["params"])
        toks.add("prob:0" if f == 0 else "prob:1" if f == 1 else "prob:half" if f == Fraction(1, 2) else "prob:other")
    if task == "complete_frequency_table":
        toks.add("table:total" if item["params"]["blank"]["kind"] == "total" else "table:freqcell")
    if (ds.get("categories") and len(ds["categories"]) >= 5) or (ds.get("values") and len(ds["values"]) >= 6):
        toks.add("dense")
    toks |= _cell_tokens(item)
    return toks


def _cell_tokens(item):
    """The systematic curriculum-review CELLS an item satisfies (owner coverage correction):
    its task x interaction, its task x difficulty-band, and its task x answer-shape."""
    task = item["params"]["task"]
    return {
        f"cell:{task}:inter:{item['interactionType']}",
        f"cell:{task}:band:{item['difficulty']['overallBand']}",
        f"cell:{task}:shape:{item['answer']['type']}",
    }


def _reachability():
    """Per-task reachable {interactions, difficulty bands, answer shapes}, derived from the
    distribution report (the authoritative reachability artifact, owner requirement #2)."""
    dist = json.load(open(os.path.join(REVIEW_DIR, "stats_data_handling_distribution.json"), encoding="utf-8"))
    reach = {}
    for task, t in dist["tasks"].items():
        inter = {"free-response"}
        if t["multipleChoice"] > 0:
            inter.add("multiple-choice")
        reach[task] = {"interactions": inter,
                       "bands": {int(b) for b in t["bandCounts"]},
                       "shapes": set(t["answerTypes"])}
    return reach


def _required_tokens(reach):
    """Required review dimensions. The BACKBONE is the systematic cells derived from reachability:
    for every task, EVERY supported interaction, EVERY reachable difficulty band, and EVERY
    realised answer shape must have an exemplar (owner requirement #1). Plus the misconception
    registry and the extra qualitative dimensions."""
    req = set()
    for task, r in reach.items():
        for i in r["interactions"]:
            req.add(f"cell:{task}:inter:{i}")
        for b in r["bands"]:
            req.add(f"cell:{task}:band:{b}")
        for s in r["shapes"]:
            req.add(f"cell:{task}:shape:{s}")
    for t, ids in mis.RULES_BY_TASK.items():
        if t in dh.FREE_RESPONSE_ONLY:
            continue
        for mid in ids:
            req.add(f"misc:{mid}")
    req |= {"barscale:1", "barscale:2", "barscale:5", "barscale:10",
            "picto:whole", "picto:half", "median:odd", "median:even", "mean:int", "mean:frac",
            "range:zero", "range:pos", "list:negative", "prob:0", "prob:1", "prob:half", "prob:other",
            "table:total", "table:freqcell", "dense",
            "list:signed-context-free", "misc-mode-valid", "no-mode-rejected",
            "bar:minor-subdiv", "line:minor-subdiv"}
    return req


def _pitfalls(task, params):
    """Misconception pitfalls to display — blank-kind-specific for frequency tables (owner #4):
    a missing TOTAL only attaches addition-side diagnostics; a missing FREQUENCY only attaches
    the subtraction-side diagnostics. Probability shows the unreduced-fraction feedback rule."""
    out = []
    extra = []
    if task == "complete_frequency_table":
        if params["blank"]["kind"] == "total":
            extra = ["MISC.STAT.FREQ_TOTAL_OMITS_CATEGORY", "MISC.STAT.FREQ_TOTAL_COPIES_ONE"]
        else:
            extra = ["MISC.STAT.FREQ_SUBTRACT_WRONG_WAY", "MISC.STAT.FREQ_IGNORES_TOTAL"]
    if task == "single_event_probability":
        extra = ["MISC.STAT.PROB_UNREDUCED"]
    for mid in extra:
        m = mis.MISCONCEPTIONS[mid]
        out.append({"misconceptionId": mid, "title": m["title"], "observableError": m["observableError"],
                    "feedback": m["feedback"], "blankKind": params.get("blank", {}).get("kind")})
    return out


def _coverage_matrix(reach, chosen):
    """Explicit coverage matrix (owner requirement #2): for every task, the reachability and
    exemplar status of each interaction, difficulty band, and answer shape, plus the flat list
    of (task, interaction, band, answerType) cells the chosen exemplars realise."""
    cell_seed = {}
    for seed, _cfg, item in chosen:
        for tk in _cell_tokens(item):
            cell_seed.setdefault(tk, seed)
    matrix = {}
    for task, r in reach.items():
        m = {"interactions": {}, "bands": {}, "shapes": {}}
        for i in ("free-response", "multiple-choice"):
            reachable = i in r["interactions"]
            seed = cell_seed.get(f"cell:{task}:inter:{i}")
            m["interactions"][i] = {"reachable": reachable, "hasExemplar": seed is not None,
                                    "exemplarSeed": seed,
                                    "note": "" if reachable else "unreachable per distribution report (no items)"}
        for b in range(1, 6):
            reachable = b in r["bands"]
            seed = cell_seed.get(f"cell:{task}:band:{b}")
            if reachable or seed is not None:
                m["bands"][b] = {"reachable": reachable, "hasExemplar": seed is not None, "exemplarSeed": seed}
        for s in sorted(r["shapes"]):
            seed = cell_seed.get(f"cell:{task}:shape:{s}")
            m["shapes"][s] = {"reachable": True, "hasExemplar": seed is not None, "exemplarSeed": seed}
        matrix[task] = m
    flat = []
    for seed, _cfg, item in chosen:
        flat.append({"task": item["params"]["task"], "interaction": item["interactionType"],
                     "band": item["difficulty"]["overallBand"], "answerType": item["answer"]["type"],
                     "seed": seed, "reachable": True, "hasExemplar": True})
    return matrix, flat


def main() -> int:
    os.makedirs(REVIEW_DIR, exist_ok=True)
    reach = _reachability()
    required = _required_tokens(reach)

    # 1) Targeted candidate gathering — task-pinned over both supported interactions, so EVERY
    #    reachable cell (incl. rare ones like read_pictogram band 1, mode_from_list MC) has
    #    candidates. Each candidate carries its full token set.
    candidates = []  # (seed, config, item, tokens)
    for task in dh.TASKS:
        interactions = ["free-response"] + (["multiple-choice"] if "multiple-choice" in reach[task]["interactions"] else [])
        for inter in interactions:
            cfg = {"interactionType": inter, "task": task}
            for seed in range(1, GATHER_SEEDS + 1):
                try:
                    item = dh.generate(seed, cfg)
                except Exception:
                    continue
                candidates.append((seed, cfg, item, _features(item)))

    # 2) Greedy set-cover: repeatedly pick the candidate adding the most still-uncovered REQUIRED
    #    tokens (reusing one item across several cells where it is a genuine exemplar).
    covered, chosen, seen = set(), [], set()
    while True:
        best, best_new = None, set()
        for seed, cfg, item, toks in candidates:
            key = (cfg["task"], cfg["interactionType"], seed)
            if key in seen:
                continue
            new = (toks & required) - covered
            if len(new) > len(best_new):
                best, best_new, best_key = (seed, cfg, item), new, key
        if best is None or not best_new:
            break
        seen.add(best_key)
        chosen.append(best)
        covered |= _features(best[2])

    missing = sorted(required - covered)
    required_cells = {t for t in required if t.startswith("cell:")}
    missing_cells = sorted(required_cells - covered)
    matrix, flat = _coverage_matrix(reach, chosen)

    records = []
    for seed, cfg, item in chosen:
        task = item["params"]["task"]
        v = dh.validate(item)
        media = item["media"][0]
        fig = media.get("svg") or (media.get("spec") or {}).get("html") or ""
        records.append({
            "objectiveId": item["objectiveIds"][0], "task": task, "interaction": item["interactionType"],
            "answerType": item["answer"]["type"], "band": item["difficulty"]["overallBand"], "seed": seed,
            "config": cfg, "params": item["params"], "dataset": item["params"]["dataset"],
            "prompt": item["prompt"]["instruction"], "mediaKind": media["kind"], "figure": fig,
            "answer": item["answer"]["display"], "answerCanonical": item["answer"]["canonical"],
            "solution": item["solution"]["steps"], "distractors": item.get("distractors", []),
            "accessibility": {"spokenMath": item["accessibility"]["spokenMath"], "dataTable": media.get("dataTableFallback")},
            "difficulty": item["difficulty"], "validation": v["status"],
            "validationChecks": [c["name"] for c in v["checks"]], "pitfalls": _pitfalls(task, item["params"]),
            "cells": sorted(_cell_tokens(item)),
            "reproduce": f"python -c \"import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate({seed},{json.dumps(cfg)})))\"",
        })

    # The required cell count must DERIVE from the matrix (reachability), not a hand-set number.
    derived_required_cells = sum(len(r["interactions"]) + len(r["bands"]) + len(r["shapes"]) for r in reach.values())
    summary = {
        "generatorId": dh.GENERATOR_ID, "generatorVersion": dh.GENERATOR_VERSION,
        "validatorVersion": dh.VALIDATOR_VERSION, "itemCount": len(records),
        "svgItems": sum(1 for r in records if r["mediaKind"] == "svg"),
        "tableItems": sum(1 for r in records if r["mediaKind"] == "table"),
        "tasksCovered": sorted({r["task"] for r in records}),
        "answerTypes": sorted({r["answerType"] for r in records}),
        "misconceptionsShown": sorted({d["misconceptionId"] for r in records for d in r["distractors"]}
                                      | {p["misconceptionId"] for r in records for p in r["pitfalls"]}),
        "requiredCells": len(required_cells), "coveredCells": len(required_cells & covered),
        "derivedRequiredCells": derived_required_cells, "missingCells": missing_cells,
        "requiredTokens": len(required), "coveredTokens": len(required & covered),
        "missingCoverage": missing,
        "allCovered": not missing,            # honest full-coverage flag (owner: no false claim)
        "allValid": all(r["validation"] == "pass" for r in records),
    }
    pack = {"summary": summary, "coverageMatrix": matrix, "coverageCells": flat, "records": records}
    with open(os.path.join(REVIEW_DIR, "stats_data_handling_review_pack.json"), "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)

    _write_md(pack)
    print(f"Review pack: {len(records)} items; cells {summary['coveredCells']}/{summary['requiredCells']} "
          f"(derived {derived_required_cells}); tokens {summary['coveredTokens']}/{summary['requiredTokens']}.")
    if missing:
        print("MISSING COVERAGE:", missing)
    print("misconceptions shown:", len(summary["misconceptionsShown"]), "/", len(mis.MISCONCEPTIONS))
    ok = (not missing) and summary["allValid"] and (len(required_cells) == derived_required_cells)
    return 0 if ok else 1


def _write_md(pack) -> None:
    s = pack["summary"]
    lines = [f"# Review pack — `{s['generatorId']}` v{s['generatorVersion']}", "",
             f"Validator v{s['validatorVersion']}. **{s['itemCount']} items** "
             f"({s['svgItems']} chart SVGs + {s['tableItems']} semantic tables). "
             f"**Curriculum-review cells: {s['coveredCells']}/{s['requiredCells']}** "
             f"(derived from the distribution report: every task × supported interaction, × reachable "
             f"difficulty band, × realised answer shape); extra dimensions {s['coveredTokens']}/{s['requiredTokens']}; "
             f"misconceptions {len(s['misconceptionsShown'])}/" + str(len(mis.MISCONCEPTIONS)) + ". "
             f"Full coverage: **{s['allCovered']}**; all items machine-valid: **{s['allValid']}**.", ""]
    if s["missingCells"]:
        lines += ["> **Missing required cells:** " + ", ".join(s["missingCells"]), ""]
    if s["missingCoverage"]:
        lines += ["> **Missing coverage:** " + ", ".join(s["missingCoverage"]), ""]
    lines += ["Status: **PENDING REVIEW** — gated out of normal Studio + production until owner approval.",
              "Objectives are `approved-for-implementation`; items are machine-validated, never auto-published.", ""]
    # Explicit coverage matrix (owner requirement #2).
    lines += ["## Coverage matrix (task × interaction / band / answer shape)", "",
              "| Task | Interactions (reachable→seed) | Bands (reachable→seed) | Answer shapes (→seed) |",
              "| --- | --- | --- | --- |"]
    for task, m in pack["coverageMatrix"].items():
        def _cells(d, keyfmt):
            parts = []
            for k, v in d.items():
                if v.get("reachable"):
                    parts.append(f"{keyfmt(k)}→{v['exemplarSeed']}" if v["hasExemplar"] else f"{keyfmt(k)}→MISSING")
                elif v.get("note"):
                    parts.append(f"{keyfmt(k)}=n/a")
            return ", ".join(parts)
        inter = _cells(m["interactions"], lambda k: {"free-response": "FR", "multiple-choice": "MC"}[k])
        bands = _cells(m["bands"], str)
        shapes = ", ".join(f"{sh}→{v['exemplarSeed']}" if v["hasExemplar"] else f"{sh}→MISSING" for sh, v in m["shapes"].items())
        lines.append(f"| `{task}` | {inter} | {bands} | {shapes} |")
    lines.append("")
    for i, r in enumerate(pack["records"], 1):
        lines += [f"## {i}. {r['task']} ({r['interaction']}) — band {r['difficulty']['overallBand']}", "",
                  f"- **Objective:** `{r['objectiveId']}`", f"- **Answer type:** {r['answerType']}",
                  f"- **Seed:** {r['seed']}", f"- **Prompt:** {r['prompt']}",
                  f"- **Canonical answer:** `{r['answer']}`", ""]
        if r["mediaKind"] == "svg":
            lines += ["<details><summary>figure (canonical SVG)</summary>", "", "```svg", r["figure"][:1600], "```", "", "</details>", ""]
        else:
            lines += ["<details><summary>figure (semantic HTML table)</summary>", "", r["figure"], "", "</details>", ""]
        lines += ["**Worked solution:**"]
        for st in r["solution"]:
            lines.append(f"  {st['number']}. {st.get('transformation','')}: {st.get('intermediateResult','')}")
        if r["distractors"]:
            lines += ["", "**Distractors (misconception-backed):**"]
            for d in r["distractors"]:
                lines.append(f"  - `{d['display']}` — {d['misconceptionId']}: {d['rationale']}")
        if r["pitfalls"]:
            lines += ["", "**Common-error notes:**"]
            for p in r["pitfalls"]:
                lines.append(f"  - {p['misconceptionId']}: {p['observableError']} → _{p['feedback']}_")
        lines += ["", f"- **Accessibility (spoken):** {r['accessibility']['spokenMath']}",
                  f"- **Difficulty axes:** {r['difficulty']['axes']}",
                  f"- **Reproduce:** `{r['reproduce']}`", "", "---", ""]
    with open(os.path.join(REVIEW_DIR, "stats_data_handling_review_pack.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
