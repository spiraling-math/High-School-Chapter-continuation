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
    if task == "read_bar_chart":
        toks.add(f"barscale:{_axis_step(item)}")
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
    if task == "single_event_probability":
        f = dh._solve(task, item["params"])
        toks.add("prob:0" if f == 0 else "prob:1" if f == 1 else "prob:half" if f == Fraction(1, 2) else "prob:other")
    if task == "complete_frequency_table":
        toks.add("table:total" if item["params"]["blank"]["kind"] == "total" else "table:freqcell")
    if (ds.get("categories") and len(ds["categories"]) >= 5) or (ds.get("values") and len(ds["values"]) >= 6):
        toks.add("dense")
    return toks


def _required_tokens():
    req = set()
    for t in dh.TASKS:
        req.add(f"task:{t}")
        req.add(f"interaction:{t}:free-response")
        if t in dh.MC_TASKS:
            req.add(f"interaction:{t}:multiple-choice")
    for t, ids in mis.RULES_BY_TASK.items():
        if t in dh.FREE_RESPONSE_ONLY:
            continue
        for mid in ids:
            req.add(f"misc:{mid}")
    req |= {"answer:integer", "answer:exact-rational", "answer:fraction", "answer:table-completion"}
    req |= {"barscale:1", "barscale:2", "barscale:5", "barscale:10"}
    req |= {"picto:whole", "picto:half", "median:odd", "median:even", "mean:int", "mean:frac",
            "range:zero", "range:pos", "list:negative", "prob:0", "prob:1", "prob:half", "prob:other",
            "table:total", "table:freqcell", "dense"}
    return req


def _pitfalls(task, params):
    """Misconception pitfalls to display (covers FR-only freq-table rules + unreduced-probability)."""
    out = []
    correct = dh._solve(task, params)
    c = dh._ctx(task, params, correct)
    if task == "complete_frequency_table":
        c["otherSum"] = sum(params["dataset"]["frequencies"]) - dh._complete_value(params) if params["blank"]["kind"] != "total" else None
        c["total"] = sum(params["dataset"]["frequencies"])
    extra = []
    if task == "complete_frequency_table":
        extra = ["MISC.STAT.FREQ_SUBTRACT_WRONG_WAY", "MISC.STAT.FREQ_IGNORES_TOTAL"]
    if task == "single_event_probability":
        extra = ["MISC.STAT.PROB_UNREDUCED"]
    for mid in extra:
        m = mis.MISCONCEPTIONS[mid]
        out.append({"misconceptionId": mid, "title": m["title"], "observableError": m["observableError"],
                    "feedback": m["feedback"]})
    return out


def main() -> int:
    os.makedirs(REVIEW_DIR, exist_ok=True)
    required = _required_tokens()
    covered = set()
    chosen = []
    seen_keys = set()

    # Greedy coverage pass over seeds (FR then MC), preferring items that add new tokens.
    for seed in range(1, MAX_SEED + 1):
        if required <= covered:
            break
        for mode in ("free-response", "multiple-choice"):
            try:
                item = dh.generate(seed, {"interactionType": mode})
            except Exception:
                continue
            toks = _features(item)
            new = toks - covered
            if not (new & required):
                continue
            key = (item["params"]["task"], item["interactionType"], item["seed"])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            chosen.append((seed, mode, item))
            covered |= toks

    missing = sorted(required - covered)
    # Build records.
    records = []
    for seed, mode, item in chosen:
        task = item["params"]["task"]
        v = dh.validate(item)
        media = item["media"][0]
        fig = media.get("svg") or (media.get("spec") or {}).get("html") or ""
        rec = {
            "objectiveId": item["objectiveIds"][0], "task": task, "interaction": item["interactionType"],
            "answerType": item["answer"]["type"], "seed": seed, "params": item["params"],
            "dataset": item["params"]["dataset"], "prompt": item["prompt"]["instruction"],
            "mediaKind": media["kind"], "figure": fig, "answer": item["answer"]["display"],
            "answerCanonical": item["answer"]["canonical"],
            "solution": item["solution"]["steps"], "distractors": item.get("distractors", []),
            "accessibility": {"spokenMath": item["accessibility"]["spokenMath"],
                              "dataTable": media.get("dataTableFallback")},
            "difficulty": item["difficulty"], "validation": v["status"],
            "validationChecks": [c["name"] for c in v["checks"]],
            "pitfalls": _pitfalls(task, item["params"]),
            "reproduce": f"python -c \"import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate({seed},{{'interactionType':'{mode}'}})))\"",
        }
        records.append(rec)

    summary = {
        "generatorId": dh.GENERATOR_ID, "generatorVersion": dh.GENERATOR_VERSION,
        "validatorVersion": dh.VALIDATOR_VERSION, "itemCount": len(records),
        "svgItems": sum(1 for r in records if r["mediaKind"] == "svg"),
        "tableItems": sum(1 for r in records if r["mediaKind"] == "table"),
        "tasksCovered": sorted({r["task"] for r in records}),
        "answerTypes": sorted({r["answerType"] for r in records}),
        "misconceptionsShown": sorted({d["misconceptionId"] for r in records for d in r["distractors"]}
                                      | {p["misconceptionId"] for r in records for p in r["pitfalls"]}),
        "requiredTokens": len(required), "coveredTokens": len(required & covered),
        "missingCoverage": missing, "allValid": all(r["validation"] == "pass" for r in records),
    }
    pack = {"summary": summary, "records": records}
    with open(os.path.join(REVIEW_DIR, "stats_data_handling_review_pack.json"), "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)

    _write_md(pack)
    print(f"Review pack: {len(records)} items, {summary['coveredTokens']}/{summary['requiredTokens']} tokens covered.")
    if missing:
        print("MISSING COVERAGE:", missing)
    print("misconceptions shown:", len(summary["misconceptionsShown"]), "/", len(mis.MISCONCEPTIONS))
    return 0 if not missing and summary["allValid"] else 1


def _write_md(pack) -> None:
    s = pack["summary"]
    lines = [f"# Review pack — `{s['generatorId']}` v{s['generatorVersion']}", "",
             f"Validator v{s['validatorVersion']}. **{s['itemCount']} items** "
             f"({s['svgItems']} chart SVGs + {s['tableItems']} semantic tables). "
             f"Coverage: {s['coveredTokens']}/{s['requiredTokens']} required dimensions; "
             f"misconceptions shown: {len(s['misconceptionsShown'])}/" + str(len(mis.MISCONCEPTIONS)) + ". "
             f"All items machine-valid: **{s['allValid']}**.", ""]
    if s["missingCoverage"]:
        lines += ["> **Missing coverage:** " + ", ".join(s["missingCoverage"]), ""]
    lines += ["Status: **PENDING REVIEW** — gated out of normal Studio + production until owner approval.",
              "Objectives are `approved-for-implementation`; items are machine-validated, never auto-published.", ""]
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
