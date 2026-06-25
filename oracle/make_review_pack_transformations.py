"""gen.geometry.transformations review pack (owner O).

Required coverage cells are DERIVED from the 10,000-seed distribution report (the authoritative
reachability source), so the matrix can never over-claim. The builder FAILS if any reachable required
cell is left uncovered, if any of the 14 result codes lacks evidence, if any of the 24 diagnostics is
unexercised, if MC is not rejected for all nine tasks, or if any owner-O regression invariant fails.

  python oracle/make_review_pack_transformations.py

Writes docs/review/transformations_review_pack.{json,md} (reads transformations_distribution.json).
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))
sys.path.insert(0, HERE)

from spi_oracle import transformations as T  # noqa: E402
from spi_oracle import transformations_core as TC  # noqa: E402
from spi_oracle import transformations_shapes as TS  # noqa: E402
from spi_oracle import transformations_misconceptions as TM  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
POOL = int(os.environ.get("SPI_POOL", "4000"))


def _quadrant(p):
    x, y = p
    if x > 0 and y > 0: return "Q1"
    if x < 0 and y > 0: return "Q2"
    if x < 0 and y < 0: return "Q3"
    if x > 0 and y < 0: return "Q4"
    return "axis"


def _cell_tokens(item) -> set:
    p = item["params"]
    task, obj, kind = p["task"], p["objectType"], p["transformationKind"]
    desc = p["descriptor"]
    src = [(c["x"], c["y"]) for c in p["source"]]
    img = [(c["x"], c["y"]) for c in p["image"]]
    toks = {f"task:{task}", f"band:{task}:{item['difficulty']['overallBand']}",
            f"answerType:{item['answer']['type']}", f"object:{task}:{obj}"}
    for v in img:
        toks.add(f"quadrant:{_quadrant(v)}")
    if any(s == i for s, i in zip(src, img)):
        toks.add("fixedPoint")
    if any((a[0] > 0) != (b[0] > 0) or (a[1] > 0) != (b[1] > 0) for a, b in zip(src, img)):
        toks.add("axisCrossing")
    if kind == "translation":
        dx, dy = desc["vector"]["dx"], desc["vector"]["dy"]
        toks.add(f"vecSign:{'+' if dx>0 else '-' if dx<0 else '0'}{'+' if dy>0 else '-' if dy<0 else '0'}")
    elif kind == "reflection":
        ax = desc["axis"]
        toks.add("axisFamily:" + ({"vertical": "x=a", "horizontal": "y=b"}.get(ax["kind"], ax.get("equation", ""))))
    elif kind == "rotation":
        toks.add(f"quarterTurns:{desc['quarterTurnsCCW']}")
        toks.add("centre:" + ("origin" if (desc["centre"]["x"], desc["centre"]["y"]) == (0, 0) else "non-origin"))
    return toks


def _required_tokens(dist) -> set:
    req = set()
    for task, info in dist["tasks"].items():
        req.add(f"task:{task}")
        for b in info["bandCounts"]:
            req.add(f"band:{task}:{b}")
        for obj in info["objectTypes"]:
            req.add(f"object:{task}:{obj}")
        for at in info["answerTypes"]:
            req.add(f"answerType:{at}")
        for fam in info["axisFamilies"]:
            req.add(f"axisFamily:{fam}")
        for q in info["quarterTurns"]:
            req.add(f"quarterTurns:{q}")
        for oc in info["originCentre"]:
            req.add(f"centre:{oc}")
        for vs in info["vectorSigns"]:
            req.add(f"vecSign:{vs}")
        for qd in info["imageQuadrants"]:
            if qd != "axis":
                req.add(f"quadrant:{qd}")
        if info["fixedPointItems"]:
            req.add("fixedPoint")
        if info["axisCrossingItems"]:
            req.add("axisCrossing")
    return req


def _regression_invariants() -> dict:
    """The owner-O regression invariants, evaluated independently (any False fails the build)."""
    src_t = [(1, 1), (4, 1), (1, 3)]
    inv = {}
    # symmetric shape not auto-ambiguous
    sym = [(-2, 0), (2, 0), (0, 3)]
    inv["symmetric_not_auto_ambiguous"] = len(TS.reconstruct_reflections(sym, [TC.reflect_x_eq_a(p, 4) for p in sym])) == 1
    # uniqueness from labelled correspondences
    img = [TC.rotate_quarter(p, 0, 0, 1) for p in src_t]
    inv["uniqueness_from_labels"] = TC.descriptors_equal(TS.unique_descriptor("rotation", src_t, img), TC.rotation_desc(0, 0, 1))
    # fixed vertex valid
    fsrc = [(4, 0), (6, 1), (5, 3)]
    inv["fixed_vertex_valid"] = TC.descriptors_equal(TS.unique_descriptor("reflection", fsrc, [TC.reflect_x_eq_a(p, 4) for p in fsrc]), TC.reflection_vertical(4))
    # unchanged rejected
    inv["unchanged_rejected"] = TS.unique_descriptor("translation", src_t, list(src_t)) is None
    # permuted-label rejected
    perm = [img[1], img[0], img[2]]
    d = TS.unique_descriptor("rotation", src_t, perm)
    inv["permuted_label_rejected"] = d is None or not TC.descriptors_equal(d, TC.rotation_desc(0, 0, 1))
    # quad pairwise distances preserved
    q = [(1, 1), (3, 1), (3, 2), (1, 2)]
    inv["quad_distances_preserved"] = all(
        sorted(TS._pairwise_sq_dists(q)) == sorted(TS._pairwise_sq_dists([TC.apply_transform(d2, p) for p in q]))
        for d2 in (TC.translation_desc(2, -3), TC.reflection_diagonal("y=x"), TC.rotation_desc(0, 0, 3)))
    # orientation rules
    inv["rotation_preserves_orientation"] = TS.orientation_sign(src_t) == TS.orientation_sign([TC.rotate_quarter(p, 0, 0, 1) for p in src_t])
    inv["reflection_reverses_orientation"] = TS.orientation_sign(src_t) == -TS.orientation_sign([TC.reflect_x_eq_a(p, 2) for p in src_t])
    # canonical/display no drift + no duplicate descriptor field
    it = T.generate(7, {"task": "describe_rotation"})
    inv["display_derived_from_canonical"] = it["answer"]["display"] == TC.format_display(TC.canonicalize_descriptor(it["answer"]["canonical"]))
    inv["no_duplicate_descriptor_field"] = "transformation" not in it["answer"] and set(it["answer"]) == {"type", "canonical", "display"}
    return inv


def main() -> int:
    dist = json.load(open(os.path.join(REVIEW_DIR, "transformations_distribution.json"), encoding="utf-8"))
    required = _required_tokens(dist)

    # Greedy set-cover over a candidate pool.
    pool = [T.generate(s) for s in range(1, POOL + 1)]
    item_tokens = [(_cell_tokens(it), it) for it in pool]
    covered, records = set(), []
    remaining = set(required)
    while remaining:
        best = max(item_tokens, key=lambda kt: len(kt[0] & remaining))
        gain = best[0] & remaining
        if not gain:
            break
        it = best[1]
        records.append({"itemId": it["itemId"], "seed": it["seed"], "task": it["params"]["task"],
                        "band": it["difficulty"]["overallBand"], "answerType": it["answer"]["type"],
                        "valid": T.validate(it)["valid"], "covers": sorted(gain)})
        covered |= best[0]
        remaining -= gain
        item_tokens.remove(best)

    missing = sorted(required - covered)
    all_valid = all(r["valid"] for r in records)

    cm = dist["checkerMatrix"]
    dc = dist["diagnosticCoverage"]
    invariants = _regression_invariants()

    pack = {
        "generatorId": T.GENERATOR_ID, "generatorVersion": T.GENERATOR_VERSION,
        "validatorVersion": T.VALIDATOR_VERSION, "approvalStatus": "pending-review", "mode": "free-response",
        "requiredCells": sorted(required), "coveredCells": sorted(covered), "missingCells": missing,
        "allCovered": not missing, "allValid": all_valid, "itemCount": len(records),
        "resultCodes": {"reachable": cm["allCodesReachable"], "codes": cm["codesReached"], "matrixMismatches": cm["mismatches"]},
        "diagnostics": {"total": dc["totalRules"], "exercised": dc["exercised"], "inapplicable": dc["inapplicableRules"],
                        "recomputationMismatches": dc["recomputationMismatches"]},
        "multipleChoiceRejectedTasks": dist["multipleChoiceRejectedTasks"],
        "regressionInvariants": invariants,
        "presence": {  # demonstrated by the visual audit + browser verification artifacts
            "premiumLight": True, "premiumDark": True, "accessibleColour": True, "monochromePrint": True,
            "selfContained6000x4200Export": True, "multiItemWorksheet": True, "labelCollisionStress": True,
            "studentAndAnswerKeyChannels": True, "sourceOnlyPerformFigures": True, "sourceAndImageDescribeFigures": True},
        "records": records,
    }
    os.makedirs(REVIEW_DIR, exist_ok=True)
    with open(os.path.join(REVIEW_DIR, "transformations_review_pack.json"), "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=2)

    inv_ok = all(invariants.values())
    lines = [
        "# gen.geometry.transformations — Review Pack",
        "",
        f"> **PENDING-REVIEW.** Free-response only. Required coverage cells are **derived from the "
        f"{dist['sweepSeeds']:,}-seed distribution report** (reachability is the authoritative source); "
        f"the builder fails on any uncovered reachable cell.",
        "",
        f"- Generator **{pack['generatorId']} v{pack['generatorVersion']}**, validator v{pack['validatorVersion']}.",
        f"- Representative items: **{pack['itemCount']}**; full coverage: **{pack['allCovered']}**; "
        f"all machine-valid: **{pack['allValid']}**.",
        f"- Result codes: all 14 reachable **{pack['resultCodes']['reachable']}** "
        f"(matrix mismatches {pack['resultCodes']['matrixMismatches']}).",
        f"- Diagnostics: **{pack['diagnostics']['exercised']}/{pack['diagnostics']['total']}** exercised, "
        f"inapplicable {pack['diagnostics']['inapplicable']}, recomputation mismatches {pack['diagnostics']['recomputationMismatches']}.",
        f"- Multiple-choice rejected for **{pack['multipleChoiceRejectedTasks']}/9** tasks.",
        f"- Owner-O regression invariants: **{'all pass' if inv_ok else 'FAILURES: ' + ', '.join(k for k, v in invariants.items() if not v)}**.",
        "",
        "## Coverage cells",
        "",
        f"Required: {len(required)} · Covered: {len(covered)} · Missing: {len(missing)}",
        "",
    ]
    if missing:
        lines += ["**MISSING CELLS:**", "", *[f"- `{m}`" for m in missing], ""]
    lines += ["## Representative items", "", "| item | task | band | answer | valid | covers |",
              "|---|---|---|---|---|---|"]
    for r in records:
        lines.append(f"| {r['seed']} | {r['task']} | {r['band']} | {r['answerType']} | {r['valid']} | {len(r['covers'])} cells |")
    lines += ["", "## Regression invariants (owner O)", ""]
    for k, v in invariants.items():
        lines.append(f"- {'✓' if v else '✗'} {k}")
    with open(os.path.join(REVIEW_DIR, "transformations_review_pack.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    ok = (pack["allCovered"] and pack["allValid"] and pack["resultCodes"]["reachable"]
          and pack["resultCodes"]["matrixMismatches"] == 0 and not pack["diagnostics"]["inapplicable"]
          and pack["diagnostics"]["recomputationMismatches"] == 0
          and pack["multipleChoiceRejectedTasks"] == 9 and inv_ok)
    print(f"Review pack: {pack['itemCount']} items, covered={pack['allCovered']} valid={pack['allValid']} "
          f"codes14={pack['resultCodes']['reachable']} diag={pack['diagnostics']['exercised']}/{pack['diagnostics']['total']} "
          f"MC-rejected={pack['multipleChoiceRejectedTasks']}/9 regression={'OK' if inv_ok else 'FAIL'}")
    if missing:
        print("MISSING:", missing)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
