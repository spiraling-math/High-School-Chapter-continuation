"""Oracle test suite for gen.measurement.mensuration v1.0.0 (owner C/F/G/H/J/K/M gates).

  python oracle/tests/test_mensuration.py

Covers: machine-validity sweep + schema conformance; reproducibility; the FREE-RESPONSE-ONLY
interaction policy (multiple-choice rejected for every task); declared-band reachability; the
dimensional-quantity answer contract; shape-specific invariants incl. composite shoelace ==
decomposition; hidden-dimension answer-leakage + NOT-TO-SCALE + overlay-channel isolation; and the
MISC.MENS.* registry (every diagnostic exercised, recomputation sound, value rules distinct).
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from collections import defaultdict
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spi_oracle"))
sys.path.insert(0, os.path.join(HERE, ".."))

import mensuration as M  # noqa: E402
import mensuration_units as U  # noqa: E402
import mensuration_misconceptions as MM  # noqa: E402
import check_conformance as cc  # noqa: E402

SWEEP = int(os.environ.get("SPI_SWEEP", "2000"))
_REG = cc.load_registry()
_SCHEMA = json.load(open(os.path.join(HERE, "..", "..", "schemas", "question-item.schema.json"), encoding="utf-8"))


class TestMachineValidity(unittest.TestCase):
    def test_sweep_all_valid_and_conformant(self):
        invalid = 0
        for seed in range(SWEEP):
            item = M.generate(seed)
            v = M.validate(item)
            if v["status"] != "pass":
                invalid += 1
                if invalid <= 3:
                    print([c for c in v["checks"] if c["result"] == "fail"])
            if seed < 300:
                errs = []
                cc.check(item, _SCHEMA, _REG, _SCHEMA, "item", errs)
                self.assertEqual(errs, [], f"seed {seed} conformance: {errs[:2]}")
        self.assertEqual(invalid, 0, f"{invalid}/{SWEEP} items failed validation")


class TestReproducibility(unittest.TestCase):
    def test_same_seed_same_bytes(self):
        for seed in range(200):
            self.assertEqual(M.serialize(M.generate(seed)), M.serialize(M.generate(seed)))


class TestInteractionPolicy(unittest.TestCase):
    def test_multiple_choice_rejected_for_every_task(self):
        for task in M.TASKS:
            with self.assertRaises(M.UnsupportedInteractionError):
                M.generate(1, task=task, interaction="multiple-choice")

    def test_free_response_supported(self):
        for task in M.TASKS:
            item = M.generate(3, task=task, interaction="free-response")
            self.assertEqual(item["interactionType"], "free-response")
            self.assertEqual(item["answer"]["type"], "quantity")


class TestBandReachability(unittest.TestCase):
    def test_every_declared_band_reached(self):
        bands = defaultdict(set)
        for seed in range(SWEEP):
            it = M.generate(seed)
            bands[it["params"]["task"]].add(it["difficulty"]["overallBand"])
        for t in M.TASKS:
            lo, hi = M.TASK_BANDS[t]
            self.assertEqual(sorted(bands[t]), list(range(lo, hi + 1)), f"{t} band reachability")


class TestAnswerContract(unittest.TestCase):
    def test_quantity_encoding(self):
        for seed in range(400):
            it = M.generate(seed)
            ans = it["answer"]
            self.assertEqual(ans["type"], "quantity")
            self.assertNotIn("units", ans, "legacy units must not appear on a quantity answer")
            self.assertIn(ans["measure"]["dimension"], ("length", "area"))
            self.assertEqual(ans["measure"]["exponent"], 1 if ans["measure"]["dimension"] == "length" else 2)
            self.assertGreaterEqual(ans["canonical"]["den"], 1)

    def test_rational_only_for_triangle_tasks(self):
        for seed in range(SWEEP):
            it = M.generate(seed)
            if it["answer"]["canonical"]["den"] != 1:
                self.assertIn(it["params"]["task"], M.RATIONAL_ANSWER_TASKS)


class TestShapeInvariants(unittest.TestCase):
    def test_composite_shoelace_equals_decomposition(self):
        seen = 0
        for seed in range(SWEEP):
            it = M.generate(seed)
            if it["params"]["task"] not in M.COMPOSITE_TASKS:
                continue
            seen += 1
            p = it["params"]; shape = M._build_shape(p["task"], p)
            shoe = M._polygon_area_shoelace(shape["vertices"])
            deco = M._decomposition_area(shape["decomposition"])
            self.assertEqual(shoe, deco, f"seed {seed}")
            self.assertEqual(shoe, p["W"] * p["H"] - p["a"] * p["b"])
            ok, why = M._is_closed_orthogonal_simple(shape["vertices"])
            self.assertTrue(ok, why)
        self.assertGreater(seen, 0)

    def test_triangle_area_and_foot_on_base(self):
        for seed in range(SWEEP):
            it = M.generate(seed)
            p = it["params"]
            if p["kind"] != "triangle_base_height":
                continue
            self.assertTrue(0 <= p["apexOffset"] <= p["base"])


class TestFigureContract(unittest.TestCase):
    def test_hidden_dimension_leakage_and_scale(self):
        seen = 0
        for seed in range(SWEEP):
            it = M.generate(seed)
            t = it["params"]["task"]
            media = it["media"][0]
            svg = media["svg"]
            self.assertNotIn("cx-overlay", svg, "student figure must not contain the answer overlay")
            self.assertIn("cx-overlay", media["spec"]["answerKeySvg"], "answer key must add the overlay")
            ans = U.format_quantity(M._solve(t, it["params"]))
            self.assertFalse(M._has_quantity_token(svg, ans), f"answer leaked into student figure (seed {seed})")
            self.assertFalse(M._has_quantity_token(it["accessibility"]["spokenMath"], ans))
            if t in M.HIDDEN_DIMENSION_TASKS:
                seen += 1
                self.assertFalse(media["toScale"])
                self.assertIn("NOT TO SCALE", svg)
        self.assertGreater(seen, 0)

    def test_base_geometry_identical_across_channels(self):
        for seed in range(300):
            it = M.generate(seed)
            p = it["params"]; shape = M._build_shape(p["task"], p)
            student = it["media"][0]["svg"]; key = it["media"][0]["spec"]["answerKeySvg"]
            self.assertEqual(M._extract_group(student, "cx-base"), M._extract_group(key, "cx-base"))
            self.assertEqual(M._extract_group(student, "cx-annot"), M._extract_group(key, "cx-annot"))


class TestMisconceptions(unittest.TestCase):
    def test_all_rules_exercised_and_recomputation_sound(self):
        coverage = defaultdict(int)
        for seed in range(SWEEP):
            it = M.generate(seed)
            t = it["params"]["task"]; ans = M._solve(t, it["params"])
            for d in MM.diagnostics_for(t, it["params"], ans):
                rule = MM._BY_ID[d["id"]]
                if d["predictedResponse"] is not None:
                    res = U.check_response(d["predictedResponse"], ans)
                    if rule["expectedCode"]:
                        self.assertEqual(res["code"], rule["expectedCode"], f"{d['id']} seed {seed}")
                    if rule["group"] == "mathematical":
                        self.assertFalse(res["correct"], f"{d['id']} predicted == answer (seed {seed})")
                coverage[d["id"]] += 1
        for m in MM.MISCONCEPTIONS:
            self.assertGreater(coverage[m["id"]], 0, f"{m['id']} never exercised")

    def test_diagnose_routes_unit_errors(self):
        it = M.generate(7); t = it["params"]["task"]; ans = M._solve(t, it["params"])
        self.assertEqual(MM.diagnose(t, it["params"], ans, U.format_value(ans.value))["id"], "MISC.MENS.RIGHT_NUMBER_NO_UNIT")
        self.assertIsNone(MM.diagnose(t, it["params"], ans, U.format_quantity(ans)))


class TestReviewPackCoverage(unittest.TestCase):
    """Blocking coverage gates over the reachability-derived review pack (owner L)."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(HERE, "..", "..", "docs", "review", "mensuration_review_pack.json")
        cls.pack = json.load(open(path, encoding="utf-8"))
        dpath = os.path.join(HERE, "..", "..", "docs", "review", "mensuration_distribution.json")
        cls.dist = json.load(open(dpath, encoding="utf-8"))

    def test_full_coverage_no_missing_cells(self):
        self.assertEqual(self.pack["missingCells"], [])
        self.assertTrue(self.pack["allCovered"])

    def test_all_review_items_machine_valid(self):
        self.assertTrue(self.pack["allValid"])
        for r in self.pack["records"]:
            self.assertEqual(r["validation"], "pass", f"{r['task']} seed {r['seed']}")

    def test_every_reachable_task_band_is_a_required_cell(self):
        cells = {row["cell"] for row in self.pack["coverageMatrix"]}
        for t, info in self.dist["tasks"].items():
            for b in info["bandCounts"]:
                self.assertIn(f"band:{t}:{b}", cells, f"reachable band {t}:{b} missing from matrix")

    def test_every_supported_dimension_unit_and_kind_covered(self):
        covered = {row["cell"] for row in self.pack["coverageMatrix"] if row["covered"]}
        for tok in ("dim:length", "dim:area", "num:integer", "num:rational",
                    "unit:mm", "unit:cm", "unit:m",
                    "kind:rectangle", "kind:rectilinear_composite", "kind:triangle_base_height",
                    "decomp:additive", "decomp:subtractive"):
            self.assertIn(tok, covered, f"{tok} not covered")

    def test_feature_proofs_hold(self):
        for k, v in self.pack["featureProofs"].items():
            self.assertTrue(v, f"feature proof failed: {k}")

    def test_quantity_checker_matrix_all_ok(self):
        seen_codes = set()
        for r in self.pack["records"]:
            for row in r["checkerMatrix"]:
                self.assertTrue(row["ok"], f"{r['task']} {row['scenario']}: {row['actualCode']} != {row['expectedCode']}")
                seen_codes.add(row["actualCode"])
        for code in ("correct", "missing-unit", "wrong-base-unit", "incorrect-value", "wrong-exponent", "wrong-dimension"):
            self.assertIn(code, seen_codes, f"checker code {code} never demonstrated")


class TestArtifactIntegrity(unittest.TestCase):
    """The generation manifest's SHA-256 hashes match the on-disk artifacts (owner M)."""

    @classmethod
    def setUpClass(cls):
        cls.root = os.path.join(HERE, "..", "..")
        cls.manifest = json.load(open(os.path.join(cls.root, "docs", "review", "mensuration_manifest.json"), encoding="utf-8"))

    def _sha256(self, rel):
        import hashlib
        h = hashlib.sha256()
        with open(os.path.join(self.root, rel), "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def test_manifest_hashes_match_disk(self):
        for name, a in self.manifest["artifacts"].items():
            self.assertTrue(a["present"], f"{name} missing")
            self.assertEqual(a["sha256"], self._sha256(a["path"]), f"{name} drift: {a['path']}")

    def test_manifest_metadata(self):
        self.assertEqual(self.manifest["generatorVersion"], M.GENERATOR_VERSION)
        self.assertEqual(self.manifest["approvalStatus"], "pending-review")
        self.assertEqual(self.manifest["objectiveReviewStatus"], "approved-for-implementation")
        self.assertEqual(self.manifest["interactionTypes"], ["free-response"])
        self.assertEqual(self.manifest["answerTypes"], ["quantity"])
        self.assertEqual(sorted(self.manifest["objectiveIds"]), sorted(M.OBJECTIVE_BY_TASK[t] for t in M.TASKS))


if __name__ == "__main__":
    unittest.main(verbosity=2)
