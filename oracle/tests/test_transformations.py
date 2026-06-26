"""gen.geometry.transformations oracle tests — exact engine, parser/checker, the independent
validator, channel + leakage contract, and the owner-O regression battery.

  python oracle/tests/test_transformations.py
"""

from __future__ import annotations

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "oracle"))

import check_conformance as cc  # noqa: E402
from spi_oracle import transformations as T  # noqa: E402
from spi_oracle import transformations_core as TC  # noqa: E402
from spi_oracle import transformations_shapes as TS  # noqa: E402
from spi_oracle import transformations_misconceptions as TM  # noqa: E402
from spi_oracle.transformations_checker import check_description  # noqa: E402

_REG = cc.load_registry()
_ITEM = _REG["https://spi-math.academy/schemas/question-item.schema.json"]


def _conf(item):
    e = []
    cc.check(item, _ITEM, _REG, _ITEM, "item", e)
    return e


class TestEngine(unittest.TestCase):
    def test_exact_engine(self):
        self.assertEqual(TC.rotate_quarter((3, 1), 0, 0, 1), (-1, 3))
        self.assertEqual(TC.rotate_quarter((5, 2), 2, -1, 1), (-1, 2))
        self.assertEqual(TC.reflect_x_eq_a((3, 1), 4), (5, 1))
        self.assertEqual(TC.reflect_y_eq_b((3, 1), 2), (3, 3))
        self.assertEqual(TC.reflect_y_eq_x((3, 1)), (1, 3))
        self.assertEqual(TC.reflect_y_eq_negx((3, 1)), (-1, -3))
        self.assertEqual(TC.apply_translation((3, 1), 3, -2), (6, -1))

    def test_display_ascii_deg(self):
        self.assertEqual(TC.format_display(TC.rotation_desc(2, -1, 3)), "rotation 270 deg anticlockwise about (2, -1)")
        self.assertEqual(TC.format_display(TC.rotation_desc(0, 0, 2)), "rotation 180 deg about (0, 0)")
        self.assertNotIn("°", TC.format_display(TC.rotation_desc(0, 0, 1)))  # never the degree symbol


class TestParserChecker(unittest.TestCase):
    def test_forms_and_variants(self):
        cases = {
            "translation by vector (3, -2)": TC.translation_desc(3, -2),
            "translation by the column vector [3; -2]": TC.translation_desc(3, -2),
            "translate by (3, -2)": TC.translation_desc(3, -2),
            "reflection in x = 4": TC.reflection_vertical(4),
            "reflection in the x-axis": TC.reflection_horizontal(0),
            "reflection in the y-axis": TC.reflection_vertical(0),
            "reflection in y = x": TC.reflection_diagonal("y=x"),
            "reflection in y = -x": TC.reflection_diagonal("y=-x"),
            "rotation 90 deg clockwise about (2, -1)": TC.rotation_desc(2, -1, 3),
            "rotation 270 deg anticlockwise about (2, -1)": TC.rotation_desc(2, -1, 3),
            "rotation 180 deg about the origin": TC.rotation_desc(0, 0, 2),
            "half turn about (2, -1)": TC.rotation_desc(2, -1, 2),
            "rotation 90° counterclockwise about (−2, 1)": TC.rotation_desc(-2, 1, 1),
        }
        for text, want in cases.items():
            self.assertEqual(TC.parse_descriptor(text).descriptor, want, text)

    def test_all_14_result_codes_reachable(self):
        exp_tr, exp_rf, exp_ro = TC.translation_desc(3, -2), TC.reflection_vertical(4), TC.rotation_desc(2, -1, 1)
        probes = [
            (exp_tr, "translation by vector (3, -2)"), (exp_ro, "reflection in x = 4"),
            (exp_tr, "translation by vector (3, 2)"), (exp_rf, "reflection in x = 5"),
            (exp_ro, "rotation 90 deg anticlockwise about (3, -1)"),
            (exp_ro, "rotation 180 deg about (2, -1)"), (exp_ro, "rotation 90 deg about (2, -1)"),
            (exp_ro, "rotation 90 deg clockwise"), (exp_tr, "translation"),
            (exp_rf, "reflection in y = 2x"), (exp_ro, "rotation 45 deg clockwise about (0, 0)"),
            (exp_ro, "rotation 90 deg clockwise and anticlockwise about (0, 0)"),
            (exp_tr, "translation by vector (3, -2) please"), (exp_tr, "move it"),
        ]
        seen = {check_description(e, t) for e, t in probes}
        for code in TC.RESULT_CODES:
            self.assertIn(code, seen, f"result code {code} not reachable")


class TestGeometryRegression(unittest.TestCase):
    """Owner-O regression battery."""

    def test_symmetric_shape_not_auto_ambiguous(self):
        # A symmetric (isosceles) triangle with FIXED label correspondence has a unique describing
        # reflection — symmetry does NOT create a second labelled mapping (owner D).
        src = [(-2, 0), (2, 0), (0, 3)]  # isosceles about x = 0
        img = [TC.reflect_x_eq_a(p, 4) for p in src]
        cands = TS.reconstruct_reflections(src, img)
        self.assertEqual(len(cands), 1)
        self.assertTrue(TC.descriptors_equal(cands[0], TC.reflection_vertical(4)))

    def test_uniqueness_from_labelled_correspondences(self):
        src = [(1, 1), (4, 1), (1, 3)]
        img = [TC.rotate_quarter(p, 0, 0, 1) for p in src]
        self.assertTrue(TC.descriptors_equal(TS.unique_descriptor("rotation", src, img), TC.rotation_desc(0, 0, 1)))

    def test_task_family_specific_uniqueness(self):
        # A 180 rotation of a point-symmetric quad is also a reflection in some cases; within the
        # EXPECTED family each is independently unique (owner D).
        src = [(1, 1), (3, 1), (3, 2), (1, 2)]
        img = [TC.rotate_quarter(p, 2, 2, 2) for p in src]
        self.assertIsNotNone(TS.unique_descriptor("rotation", src, img))

    def test_fixed_vertex_may_remain_valid(self):
        # A vertex on the mirror line is fixed; the reflection is still uniquely recoverable (owner E).
        src = [(4, 0), (6, 1), (5, 3)]  # vertex (4,0) lies on x = 4
        img = [TC.reflect_x_eq_a(p, 4) for p in src]
        self.assertEqual(img[0], (4, 0))  # fixed point
        self.assertTrue(TC.descriptors_equal(TS.unique_descriptor("reflection", src, img), TC.reflection_vertical(4)))

    def test_unchanged_object_rejected(self):
        src = [(1, 1), (4, 1), (1, 3)]
        self.assertIsNone(TS.unique_descriptor("translation", src, list(src)))

    def test_permuted_label_answer_rejected(self):
        src = [(1, 1), (4, 1), (1, 3)]
        img = [TC.rotate_quarter(p, 0, 0, 1) for p in src]
        permuted = [img[1], img[0], img[2]]
        d = TS.unique_descriptor("rotation", src, permuted)
        self.assertTrue(d is None or not TC.descriptors_equal(d, TC.rotation_desc(0, 0, 1)))

    def test_quadrilateral_pairwise_distances_preserved(self):
        src = [(1, 1), (3, 1), (3, 2), (1, 2)]
        for desc in (TC.translation_desc(2, -3), TC.reflection_diagonal("y=x"), TC.rotation_desc(0, 0, 3)):
            img = [TC.apply_transform(desc, p) for p in src]
            self.assertEqual(sorted(TS._pairwise_sq_dists(src)), sorted(TS._pairwise_sq_dists(img)))

    def test_orientation_preserve_and_reverse(self):
        src = [(0, 0), (3, 0), (0, 2)]
        for desc in (TC.translation_desc(1, 1), TC.rotation_desc(1, 1, 1), TC.rotation_desc(0, 0, 3)):
            img = [TC.apply_transform(desc, p) for p in src]
            self.assertEqual(TS.orientation_sign(src), TS.orientation_sign(img))  # preserved
        for desc in (TC.reflection_vertical(2), TC.reflection_diagonal("y=-x")):
            img = [TC.apply_transform(desc, p) for p in src]
            self.assertEqual(TS.orientation_sign(src), -TS.orientation_sign(img))  # reversed

    def test_canonical_display_cannot_drift(self):
        for s in range(1, 60):
            it = T.generate(s, {"task": "describe_rotation"})
            ans = it["answer"]
            self.assertEqual(ans["display"], TC.format_display(TC.canonicalize_descriptor(ans["canonical"])))

    def test_no_duplicate_descriptor_field(self):
        it = T.generate(3, {"task": "describe_translation"})
        self.assertNotIn("transformation", it["answer"])  # descriptor is answer.canonical, no sibling
        self.assertEqual(set(it["answer"]) - {"type", "canonical", "display"}, set())


class TestFixedPointLabels(unittest.TestCase):
    """Owner v1.0.2 REVISE: answer-key fixed-point labels must not overlap, verified on the serialized
    SVG. The three cited regression seeds + a describe (source-plus-image) fixed-point case."""

    SEEDS = [("rotate_shape", 3189), ("reflect_shape", 18), ("reflect_shape", 896),
             ("describe_reflection", 8)]

    def _label_coords(self, svg):
        import re
        return {t: (int(x), int(y)) for x, y, t in
                re.findall(r'<text class="tx-lbl" x="(-?\d+)" y="(-?\d+)" text-anchor="\w+">([^<]*)</text>', svg)}

    def test_cited_seeds_have_separated_fixed_point_labels(self):
        for task, seed in self.SEEDS:
            it = T.generate(seed, {"task": task})
            p = it["params"]; obj = p["objectType"]
            src = [(c["x"], c["y"]) for c in p["source"]]
            img = [(c["x"], c["y"]) for c in p["image"]]
            fixed = [i for i in range(len(src)) if src[i] == img[i]]
            self.assertTrue(fixed, f"{task} seed {seed} should have a fixed vertex")
            key = it["media"][0]["spec"]["answerKeySvg"]
            coords = self._label_coords(key)
            for i in fixed:
                s_lab, i_lab = TS.SOURCE_LABELS[obj][i], TS.image_labels(obj)[i]
                self.assertIn(s_lab, coords, f"{task} {seed} source label {s_lab}")
                self.assertIn(i_lab, coords, f"{task} {seed} image label {i_lab}")
                self.assertNotEqual(coords[s_lab], coords[i_lab],
                                    f"{task} seed {seed}: {s_lab} and {i_lab} overlap at {coords[s_lab]}")

    def test_fixed_point_validator_checks(self):
        for task, seed in self.SEEDS:
            v = T.validate(T.generate(seed, {"task": task}))
            self.assertTrue(v["valid"], f"{task} {seed} valid")
            names = {c["name"]: c["ok"] for c in v["checks"]}
            for chk in ("fixed-point-labels-not-overlapped", "source-image-label-bbox-clearance",
                        "answer-key-label-bbox-clearance", "label-bbox-clearance-includes-answer-key-overlay",
                        "fixed-point-marker-readable", "fixed-point-correspondence-readable"):
                self.assertIn(chk, names, f"{task} {seed} missing {chk}")
                self.assertTrue(names[chk], f"{task} {seed} {chk} failed")

    def test_serialized_svg_clearance_catches_overlap(self):
        # a deliberately-overlapping pair of labels must FAIL the serialized-SVG clearance helper.
        good = T.generate(3189, {"task": "rotate_shape"})["media"][0]["spec"]["answerKeySvg"]
        boxes = [b for b, _ in T._svg_label_boxes(good)]
        self.assertTrue(T._boxes_pairwise_clear(boxes))
        clash = ('<text class="tx-lbl" x="100" y="100" text-anchor="start">B</text>'
                 '<text class="tx-lbl" x="100" y="100" text-anchor="start">B′</text>')
        self.assertFalse(T._boxes_pairwise_clear([b for b, _ in T._svg_label_boxes(clash)]))


class TestGeneratorContract(unittest.TestCase):
    def test_all_tasks_generate_conform_validate(self):
        for task in T.TASKS:
            for seed in (1, 7, 50, 999):
                it = T.generate(seed, {"task": task})
                self.assertEqual(_conf(it), [], f"{task} seed={seed} conform")
                self.assertTrue(T.validate(it)["valid"], f"{task} seed={seed} validate")

    def test_mc_rejected_all_tasks(self):
        for task in T.TASKS:
            with self.assertRaises(T.InteractionNotSupported):
                T.generate(1, {"task": task, "interactionType": "multiple-choice"})

    def test_answer_types_per_task(self):
        want = {"translate_point": "coordinate", "reflect_point": "coordinate", "rotate_point": "coordinate",
                "translate_shape": "table-completion", "reflect_shape": "table-completion", "rotate_shape": "table-completion",
                "describe_translation": "transformation", "describe_reflection": "transformation", "describe_rotation": "transformation"}
        for task, atype in want.items():
            self.assertEqual(T.generate(11, {"task": task})["answer"]["type"], atype)

    def test_shape_image_labels_use_prime(self):
        it = T.generate(5, {"task": "translate_shape"})
        for cell in it["answer"]["canonical"]["cells"]:
            self.assertIn("′", cell["location"])  # U+2032 PRIME

    def test_channels_base_identical_and_additive(self):
        # The shared <g class="tx-base"> geometry group is byte-identical across channels; the channel
        # a11y <title>/<desc> and the key-only overlay differ (owner N + #3 + #4).
        for task in T.TASKS:
            it = T.generate(13, {"task": task})
            m = it["media"][0]
            student, key = m["svg"], m["spec"]["answerKeySvg"]
            self.assertEqual(T._tx_base(student), T._tx_base(key), f"{task} base identical")
            self.assertNotEqual(T._tx_base(student), "", f"{task} has a base group")
            self.assertGreater(len(key), len(student), f"{task} key additive")
            self.assertIn('<g class="tx-overlay">', key, f"{task} key has overlay")

    def test_answer_key_a11y_channel_specific(self):
        # owner #3: answer-key <desc> describes the image + overlay and never says "image not shown".
        import re
        for task in T.TASKS:
            it = T.generate(21, {"task": task})
            m = it["media"][0]
            s = re.search(r"<desc>([^<]*)</desc>", m["svg"]).group(1)
            k = re.search(r"<desc>([^<]*)</desc>", m["spec"]["answerKeySvg"]).group(1)
            self.assertNotEqual(s, k, f"{task} channel-specific desc")
            self.assertNotIn("not shown", k.lower(), f"{task} key must not say image hidden")
            self.assertNotIn("not shown", m["spec"]["answerKeyAltText"].lower(), f"{task} key alt")

    def test_no_duplicate_svg_ids_and_marker_refs_resolve(self):
        # owner #4: per-SVG unique ids; every url(#id) resolves within its own SVG.
        import re
        for task in T.TASKS:
            it = T.generate(21, {"task": task})
            m = it["media"][0]
            for svg in (m["svg"], m["spec"]["answerKeySvg"]):
                ids = re.findall(r'id="([^"]+)"', svg)
                self.assertEqual(len(ids), len(set(ids)), f"{task} duplicate ids")
                for ref in re.findall(r"url\(#([^)]+)\)", svg):
                    self.assertIn(ref, set(ids), f"{task} dangling ref {ref}")

    def test_perform_hides_image_describe_shows_both(self):
        perf = T.generate(2, {"task": "rotate_shape"})["media"][0]["svg"]
        self.assertNotIn('<rect class="tx-img-open"', perf)  # image marker absent in perform student channel
        desc = T.generate(2, {"task": "describe_rotation"})["media"][0]["svg"]
        self.assertIn('<rect class="tx-img-open"', desc)     # both figures shown in describe student channel

    def test_describe_student_does_not_name_transformation(self):
        for task in ("describe_translation", "describe_reflection", "describe_rotation"):
            it = T.generate(8, {"task": task})
            disp = TC.format_display(it["params"]["descriptor"])
            self.assertNotIn(disp, it["media"][0]["svg"])

    def test_reproducible(self):
        for task in T.TASKS:
            a = T.serialize(T.generate(321, {"task": task}))
            b = T.serialize(T.generate(321, {"task": task}))
            self.assertEqual(a, b)


class TestDiagnostics(unittest.TestCase):
    def test_descriptor_ids_exact_and_no_desc_prefix(self):
        for needed in ("MISC.TRANS.RIGHT_TYPE_WRONG_VECTOR", "MISC.TRANS.RIGHT_REFLECTION_WRONG_AXIS",
                       "MISC.TRANS.RIGHT_ANGLE_MISSING_CENTRE", "MISC.TRANS.RIGHT_CENTRE_WRONG_DIRECTION",
                       "MISC.TRANS.NAMES_REFLECTION_FOR_ROTATION"):
            self.assertIn(needed, TM.ALL_IDS)
        self.assertFalse(any("DESC_" in m for m in TM.ALL_IDS))

    def test_registry_conforms(self):
        schema = _REG["https://spi-math.academy/schemas/misconception.schema.json"]
        for m in TM.registry():
            e = []
            cc.check(m, schema, _REG, schema, m["misconceptionId"], e)
            self.assertEqual(e, [], m["misconceptionId"])

    def test_no_null_predicted_counted_as_exercised(self):
        # parser-kind diagnostics carry studentResponseText (not a null/invalid canonical) and a
        # result code; predicted is None but they are classified parser, not counted as value/descriptor.
        dr = TM.diagnostics_for("describe_rotation", [(1, 1), (4, 1), (1, 3)], TC.rotation_desc(2, -1, 1))
        nulls = [d for d in dr if d["predicted"] is None]
        self.assertTrue(all(d["kind"] == "parser" and d.get("studentResponseText") for d in nulls))
        self.assertTrue(all(d["expectedResultCode"] in TC.RESULT_CODES for d in nulls))

    def test_diagnostic_recomputation(self):
        for s in range(1, 80):
            for task in T.TASKS:
                it = T.generate(s, {"task": task})
                p = it["params"]
                src = [(c["x"], c["y"]) for c in p["source"]]
                for d in TM.diagnostics_for(task, src, p["descriptor"]):
                    if d["kind"] == "descriptor":
                        self.assertEqual(check_description(p["descriptor"], d["predicted"]["display"]), d["expectedResultCode"])
                    elif d["kind"] == "parser":
                        self.assertEqual(check_description(p["descriptor"], d["studentResponseText"]), d["expectedResultCode"])


_REVIEW = os.path.join(ROOT, "docs", "review")


def _read(name):
    p = os.path.join(_REVIEW, name)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


class TestArtifactIdentity(unittest.TestCase):
    """Owner REVISE #1: every approval artifact must identify the SAME generator/validator version and
    the SAME build commit; nothing stale; manifest hashes match the files on disk."""

    @classmethod
    def setUpClass(cls):
        import re
        cls.re = re
        cls.audit = _read("transformations_visual_audit.html")
        cls.manifest = json.loads(_read("transformations_manifest.json") or "{}")
        cls.browser = json.loads(_read("transformations_browser_verification.json") or "{}")
        cls.pack = json.loads(_read("transformations_review_pack.json") or "{}")

    def _attr(self, name):
        m = self.re.search(rf'{name}="([^"]*)"', self.audit)
        return m.group(1) if m else None

    def _present(self):
        if not (self.audit and self.manifest and self.browser and self.pack):
            self.skipTest("review artifacts not generated yet (run the make_* scripts)")

    def test_audit_version_matches_generator(self):
        self._present()
        self.assertEqual(self._attr("data-generator-version"), T.GENERATOR_VERSION)
        self.assertEqual(self._attr("data-generator-id"), T.GENERATOR_ID)
        title = self.re.search(r"<title>([^<]+)</title>", self.audit).group(1)
        h1 = self.re.search(r"<h1>([^<]+)</h1>", self.audit).group(1)
        self.assertIn(f"v{T.GENERATOR_VERSION}", title)
        self.assertIn(f"v{T.GENERATOR_VERSION}", h1)

    def test_audit_validator_version_matches(self):
        self._present()
        self.assertEqual(self._attr("data-validator-version"), T.VALIDATOR_VERSION)

    def test_audit_commit_matches_manifest(self):
        self._present()
        self.assertEqual(self._attr("data-git-commit"), self.manifest["gitCommit"])
        self.assertEqual(self._attr("data-git-commit"), self.browser["gitCommit"])

    def test_no_stale_commit_or_version_text(self):
        self._present()
        self.assertNotIn("1.0.0", self.audit, "stale v1.0.0 text in the visual audit")
        self.assertIn(f"v{T.GENERATOR_VERSION}", self.audit)

    def test_browser_report_version_matches_audit(self):
        self._present()
        self.assertEqual(self.browser["generatorVersion"], self._attr("data-generator-version"))
        self.assertEqual(self.browser["generatorVersion"], T.GENERATOR_VERSION)

    def test_review_pack_version_matches_generator(self):
        self._present()
        self.assertEqual(self.pack["generatorVersion"], T.GENERATOR_VERSION)
        self.assertEqual(self.pack["validatorVersion"], T.VALIDATOR_VERSION)

    def test_manifest_version_matches_audit(self):
        self._present()
        self.assertEqual(self.manifest["generatorVersion"], self._attr("data-generator-version"))
        self.assertEqual(self.manifest["validatorVersion"], self._attr("data-validator-version"))

    def test_manifest_tag_terminology(self):
        self._present()
        vt = self.manifest["versionTags"]
        self.assertEqual(vt["previousVersionTag"], "transformations-v1.0.0")
        self.assertEqual(vt["currentImplementationTag"], "transformations-v1.0.1")
        self.assertIsNone(vt["approvedTag"])  # created only on owner APPROVE

    def test_manifest_hashes_match_files(self):
        self._present()
        import hashlib
        for name, a in self.manifest["artifacts"].items():
            if not a["present"]:
                continue
            h = hashlib.sha256()
            with open(os.path.join(ROOT, a["path"]), "rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    h.update(chunk)
            self.assertEqual(a["sha256"], h.hexdigest(), f"{name} drift: {a['path']}")

    def test_no_duplicate_svg_ids_in_audit(self):
        self._present()
        ids = self.re.findall(r'id="([^"]+)"', self.audit)
        self.assertEqual(len(ids), len(set(ids)), "duplicate inline SVG ids in the audit DOM")


class TestVisualModes(unittest.TestCase):
    """Owner REVISE #5: real, readable, isolated presentation modes; computed styles verified."""

    @classmethod
    def setUpClass(cls):
        cls.browser = json.loads(_read("transformations_browser_verification.json") or "{}")

    def _present(self):
        if not self.browser:
            self.skipTest("browser verification not generated yet")

    def test_all_visual_mode_checks_pass(self):
        self._present()
        bad = [c["name"] for c in self.browser["checks"] if not c["ok"]]
        self.assertEqual(bad, [], f"failing visual-mode checks: {bad}")

    def test_real_browser_computed_styles_match_baked(self):
        self._present()
        real = self.browser.get("realBrowserComputedStyles")
        self.assertIsNotNone(real, "real-browser getComputedStyle capture missing")
        self.assertEqual(real["mismatchesVsBakedTheme"], 0)
        self.assertGreaterEqual(real["figuresCaptured"], 8)

    def test_required_mode_invariants_present(self):
        self._present()
        names = {c["name"] for c in self.browser["checks"]}
        for required in ("four-modes-genuinely-different", "source-image-distinction-not-colour-only",
                         "dark-mode-grid-and-labels-readable", "print-mode-authoritative",
                         "mode-order-does-not-change-styles", "mixed-mode-multi-svg-isolation",
                         "no-duplicate-svg-ids-in-audit", "self-contained-6000x4200-export"):
            self.assertIn(required, names, f"missing visual-mode check {required}")


class TestParityFixture(unittest.TestCase):
    def test_parity_fixture_reproducible(self):
        path = os.path.join(ROOT, "oracle", "golden", "transformations.parity.json")
        if not os.path.exists(path):
            self.skipTest("parity fixture not generated")
        entries = json.load(open(path, encoding="utf-8"))
        self.assertGreaterEqual(len(entries), 300)
        for e in entries[::7]:  # sample for speed
            self.assertEqual(T.serialize(T.generate(e["seed"], {"task": e["task"]})), e["serialized"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
