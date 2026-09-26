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
from build_meta import sha256_canonical  # noqa: E402

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
        seen_area = seen_perim = 0
        for seed in range(SWEEP):
            it = M.generate(seed)
            if it["params"]["task"] not in M.COMPOSITE_TASKS:
                continue
            p = it["params"]; shape = M._build_shape(p["task"], p)
            shoe = M._polygon_area_shoelace(shape["vertices"])
            self.assertEqual(shoe, p["W"] * p["H"] - p["a"] * p["b"], f"seed {seed}")
            ok, why = M._is_closed_orthogonal_simple(shape["vertices"])
            self.assertTrue(ok, why)
            if p["task"] == "area_composite":
                seen_area += 1
                self.assertIn("decomposition", shape)
                self.assertEqual(shoe, M._decomposition_area(shape["decomposition"]), f"seed {seed}")
            else:  # perimeter_composite — owner C1: no decomposition
                seen_perim += 1
                self.assertNotIn("decomposition", shape)
                self.assertNotIn("decompMode", p)
        self.assertGreater(seen_area, 0)
        self.assertGreater(seen_perim, 0)

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
                    "decomp:area_composite:additive", "decomp:area_composite:subtractive"):
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


class TestArtifactIdentity(unittest.TestCase):
    """Owner artifact-identity REVISE: the visual audit, browser report, and manifest must all state
    the SAME generator/validator version + build commit; no stale version text; clean tag terminology."""

    @classmethod
    def setUpClass(cls):
        import re
        cls.re = re
        rev = os.path.join(HERE, "..", "..", "docs", "review")
        cls.audit = open(os.path.join(rev, "mensuration_visual_audit.html"), encoding="utf-8").read()
        cls.browser = json.load(open(os.path.join(rev, "mensuration_browser_verification.json"), encoding="utf-8"))
        cls.manifest = json.load(open(os.path.join(rev, "mensuration_manifest.json"), encoding="utf-8"))

    def _attr(self, name):
        m = self.re.search(rf'{name}="([^"]*)"', self.audit)
        return m.group(1) if m else None

    def test_audit_visible_title_matches_generator(self):
        title = self.re.search(r"<title>([^<]+)</title>", self.audit).group(1)
        h1 = self.re.search(r"<h1>([^<]+)</h1>", self.audit).group(1)
        want = f"{M.GENERATOR_ID} v{M.GENERATOR_VERSION}"
        self.assertIn(want, title)
        self.assertIn(want, h1)

    def test_audit_version_matches_generator(self):
        self.assertEqual(self._attr("data-generator-version"), M.GENERATOR_VERSION)
        self.assertEqual(self._attr("data-generator-id"), M.GENERATOR_ID)

    def test_audit_validator_version_matches(self):
        self.assertEqual(self._attr("data-validator-version"), M.VALIDATOR_VERSION)

    def test_audit_commit_matches_build(self):
        self.assertEqual(self._attr("data-git-commit"), self.manifest["gitCommit"])
        self.assertEqual(self._attr("data-git-commit"), self.browser.get("gitCommit"))

    def test_no_stale_version_text(self):
        # the audit (visible text + metadata) must contain no superseded version string
        self.assertNotIn("1.0.0", self.audit, "stale v1.0.0 text in the visual audit")
        self.assertIn(f"v{M.GENERATOR_VERSION}", self.audit)

    def test_browser_report_version_matches_audit(self):
        self.assertEqual(self.browser["generatorVersion"], self._attr("data-generator-version"))
        self.assertEqual(self.browser["generatorVersion"], M.GENERATOR_VERSION)

    def test_manifest_version_matches_audit(self):
        self.assertEqual(self.manifest["generatorVersion"], self._attr("data-generator-version"))
        self.assertEqual(self.manifest["validatorVersion"], self._attr("data-validator-version"))

    def test_manifest_tag_terminology(self):
        vt = self.manifest["versionTags"]
        self.assertEqual(vt["previousVersionTag"], "mensuration-v1.0.0")
        self.assertEqual(vt["currentImplementationTag"], "mensuration-v1.0.1")
        self.assertEqual(vt["approvedTag"], "approved-mensuration-v1.0.1")  # created on final APPROVE
        # the approved tag is the genuine approved reference, never the superseded v1.0.0 implementation tag
        self.assertNotEqual(self.manifest["approval"].get("approvedTag"), "mensuration-v1.0.0")

    def test_manifest_hashes_match_files(self):
        root = os.path.join(HERE, "..", "..")
        for name, a in self.manifest["artifacts"].items():
            self.assertTrue(a["present"], name)
            # canonical (CRLF->LF) hash: identical on a Windows working tree and on the LF bytes git stores
            self.assertEqual(a["sha256"], sha256_canonical(os.path.join(root, a["path"])), f"{name} drift: {a['path']}")


class TestArtifactIntegrity(unittest.TestCase):
    """The generation manifest's SHA-256 hashes match the on-disk artifacts (owner M)."""

    @classmethod
    def setUpClass(cls):
        cls.root = os.path.join(HERE, "..", "..")
        cls.manifest = json.load(open(os.path.join(cls.root, "docs", "review", "mensuration_manifest.json"), encoding="utf-8"))

    def _sha256(self, rel):
        # canonical (CRLF->LF) hash: identical on a Windows working tree and on the LF bytes git stores
        return sha256_canonical(os.path.join(self.root, rel))

    def test_manifest_hashes_match_disk(self):
        for name, a in self.manifest["artifacts"].items():
            self.assertTrue(a["present"], f"{name} missing")
            self.assertEqual(a["sha256"], self._sha256(a["path"]), f"{name} drift: {a['path']}")

    def test_manifest_metadata(self):
        self.assertEqual(self.manifest["generatorVersion"], M.GENERATOR_VERSION)
        self.assertEqual(self.manifest["approvalStatus"], "approved")
        self.assertEqual(self.manifest["objectiveReviewStatus"], "approved")
        self.assertEqual(self.manifest["interactionTypes"], ["free-response"])
        self.assertEqual(self.manifest["answerTypes"], ["quantity"])
        self.assertEqual(sorted(self.manifest["objectiveIds"]), sorted(M.OBJECTIVE_BY_TASK[t] for t in M.TASKS))


class TestCompositePerimeterSolution(unittest.TestCase):
    """Owner C2: the perimeter_composite worked solution is numerically complete."""

    def _named(self, item):
        return {c["name"]: c["result"] for c in M.validate(item)["checks"]}

    def test_named_checks_pass_for_every_composite_perimeter(self):
        seen = 0
        for s in range(SWEEP):
            it = M.generate(s)
            if it["params"]["task"] != "perimeter_composite":
                continue
            seen += 1
            n = self._named(it)
            for name in ("composite-perimeter-derives-missing-edges", "composite-perimeter-lists-complete-boundary",
                         "composite-perimeter-sum-produces-answer", "no-internal-edge-in-perimeter-sum",
                         "worked-solution-is-numerically-complete"):
                self.assertEqual(n.get(name), "pass", f"{name} seed {s}")
            if seen > 60:
                break
        self.assertGreater(seen, 0)

    def test_no_placeholder_and_full_trace(self):
        it = next(M.generate(s) for s in range(SWEEP) if M.generate(s)["params"]["task"] == "perimeter_composite")
        joined = " ".join(st["intermediateResult"] for st in it["solution"]["steps"])
        self.assertNotIn("part", joined)
        self.assertIn(" + ", joined)  # an explicit boundary trace


class TestDiagnosticStructure(unittest.TestCase):
    """Owner C4: no null numeric diagnostics; pedagogical rules labelled; inapplicable rules omitted."""

    def test_numeric_and_unit_diagnostics_are_non_null_and_pedagogical_labelled(self):
        for s in range(SWEEP):
            it = M.generate(s); t = it["params"]["task"]; ans = M._solve(t, it["params"])
            for d in MM.diagnostics_for(t, it["params"], ans):
                self.assertEqual(d["appliesTo"], t)
                self.assertTrue(d["feedback"])
                self.assertTrue(d["observableError"])
                if d["kind"] == "pedagogical":
                    self.assertTrue(d["diagnosticOnly"])
                    self.assertIsNone(d["predictedResponse"])
                else:
                    self.assertFalse(d["diagnosticOnly"])
                    self.assertIsNotNone(d["predictedResponse"], f"{d['id']} {t}")
                    self.assertIsNotNone(d["resultCode"], f"{d['id']} {t}")

    def test_inapplicable_rules_not_emitted_for_inverse_tasks(self):
        for task in ("missing_length_perimeter", "missing_dimension_area"):
            it = M.generate(next(s for s in range(SWEEP) if M.generate(s)["params"]["task"] == task), task=task)
            ids = {d["id"] for d in MM.diagnostics_for(task, it["params"], M._solve(task, it["params"]))}
            self.assertNotIn("MISC.MENS.USES_AREA_FOR_PERIMETER", ids)
            self.assertNotIn("MISC.MENS.USES_PERIMETER_FOR_AREA", ids)

    def test_uses_sloping_side_is_diagnostic_only(self):
        it = M.generate(next(s for s in range(SWEEP) if M.generate(s)["params"]["task"] == "area_triangle"), task="area_triangle")
        d = next(x for x in MM.diagnostics_for("area_triangle", it["params"], M._solve("area_triangle", it["params"])) if x["id"] == "MISC.MENS.USES_SLOPING_SIDE")
        self.assertTrue(d["diagnosticOnly"])
        self.assertIsNone(d["predictedResponse"])


class TestWordingAccessibility(unittest.TestCase):
    """Owner C5: prompt + accessibility wording polish; canonical units stay ASCII."""

    def test_prompt_no_redundant_sentence(self):
        leads = {"missing_length_perimeter": "This rectangle has a perimeter of",
                 "missing_dimension_area": "This rectangle has an area of",
                 "missing_triangle_base_height": "This triangle has an area of"}
        for task, lead in leads.items():
            it = M.generate(next(s for s in range(SWEEP) if M.generate(s)["params"]["task"] == task), task=task)
            instr = it["prompt"]["instruction"]
            self.assertTrue(instr.startswith(lead), instr)
            self.assertNotIn("is given. The", instr)
            self.assertNotIn("is given. Work", instr)

    def test_accessibility_description_grammatical(self):
        saw_tri = saw_comp = False
        for s in range(SWEEP):
            it = M.generate(s); spoken = it["accessibility"]["spokenMath"]
            self.assertNotIn("A L-shaped", spoken)
            if it["params"]["task"] in ("area_composite", "perimeter_composite"):
                self.assertIn("An L-shaped composite rectilinear shape measured in", spoken); saw_comp = True
            if it["params"]["kind"] == "triangle_base_height":
                self.assertRegex(spoken, r"A triangle measured in \w+, with its perpendicular height marked\."); saw_tri = True
            if saw_tri and saw_comp:
                break
        self.assertTrue(saw_tri and saw_comp)

    def test_canonical_unit_display_remains_ascii(self):
        for s in range(400):
            it = M.generate(s)
            self.assertNotIn("²", it["answer"]["display"])
            if it["answer"]["measure"]["exponent"] == 2:
                self.assertIn("^2", it["answer"]["display"])
            self.assertNotIn("²", it["prompt"]["instruction"])

    def test_unit_display_human_readable_in_a11y(self):
        for task in ("missing_dimension_area", "missing_triangle_base_height"):
            it = M.generate(next(s for s in range(SWEEP) if M.generate(s)["params"]["task"] == task), task=task)
            rows = it["media"][0]["dataTableFallback"]["rows"]
            area_row = next(r for r in rows if "area (given)" in r[0])
            self.assertIn("squared", area_row[1])
            self.assertNotIn("^2", area_row[1])


class TestDecompositionCoverage(unittest.TestCase):
    """Owner C1: decomposition coverage is task-specific; perimeter items excluded; both modes present."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(HERE, "..", "..", "docs", "review", "mensuration_review_pack.json")
        cls.pack = json.load(open(path, encoding="utf-8"))

    def test_feature_proofs(self):
        fp = self.pack["featureProofs"]
        for k in ("area_composite_additive_exemplar_present", "area_composite_subtractive_exemplar_present",
                  "decomposition_coverage_task_specific", "perimeter_items_not_in_area_decomposition_cells",
                  "coverage_cell_matches_worked_method", "all_seven_checker_codes_reached",
                  "genuinely_different_forms_accepted", "no_cross_unit_conversion", "no_null_numeric_diagnostic_records",
                  "checker_matrix_no_mismatch"):
            self.assertTrue(fp.get(k), f"feature proof failed: {k}")

    def test_no_false_decomposition_coverage_claim(self):
        cells = {row["cell"] for row in self.pack["coverageMatrix"]}
        self.assertIn("decomp:area_composite:additive", cells)
        self.assertIn("decomp:area_composite:subtractive", cells)
        self.assertNotIn("decomp:additive", cells)
        self.assertNotIn("decomp:subtractive", cells)
        # no perimeter_composite record carries an area-decomposition token
        for r in self.pack["records"]:
            if r["task"] == "perimeter_composite":
                self.assertIsNone(r["decompMode"])

    def test_coverage_cell_matches_worked_method(self):
        for r in self.pack["records"]:
            if r["task"] != "area_composite":
                continue
            sol = " ".join(r["solution"])
            if r["decompMode"] == "additive":
                self.assertIn("Add the two rectangle areas", sol)
            else:
                self.assertIn("Subtract the missing rectangle", sol)

    def test_checker_summary_all_seven(self):
        cs = self.pack["checkerSummary"]
        self.assertTrue(cs["allSevenReached"])
        self.assertEqual(cs["matrixMismatches"], 0)
        self.assertFalse(cs["crossUnitConversionPerformed"])
        self.assertGreater(cs["genuinelyDifferentAccepted"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
