"""Contract + artifact-integrity tests for gen.geometry.coordinate-lines v1.0.0.

Covers the owner's leakage rules (D), the interaction rules (B), the vertical-line
exclusion (F), the PNG envelope (I.8), and a blocking artifact-integrity gate confirming
the review pack + visual audit carry the current generator version + a consistent build
commit and match the manifest hashes.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))

from spi_oracle import coordinate_lines as cl  # noqa: E402
from spi_oracle.coordinate_misconceptions import MISCONCEPTIONS  # noqa: E402

# Patterns that assign a coordinate to the WRONG axis (a reversed axis-coordinate mapping).
# The v1.0.0 read_point solution ("Read across to the y-axis for x, then up or down to the
# x-axis for y") did exactly this; v1.0.1 corrects it.
_REVERSED = [
    re.compile(r"y[-\s]?axis\s+for\s+(the\s+)?x\b", re.I),
    re.compile(r"x[-\s]?axis\s+for\s+(the\s+)?y\b", re.I),
    re.compile(r"across\s+to\s+the\s+y[-\s]?axis", re.I),
    re.compile(r"up\s+or\s+down\s+to\s+the\s+x[-\s]?axis", re.I),
    re.compile(r"x[-\s]?coordinate\s+(from|on|along|up|down|vertical)", re.I),
    re.compile(r"y[-\s]?coordinate\s+(across|along\s+the\s+horizontal)", re.I),
    re.compile(r"read\s+(the\s+)?x[-\s]?coordinate\s+(up|down|vertical)", re.I),
    re.compile(r"read\s+(the\s+)?y[-\s]?coordinate\s+(across|horizontal)", re.I),
]


def reverses_axes(text: str) -> bool:
    return any(p.search(text) for p in _REVERSED)


class TestExplanationSemantics(unittest.TestCase):
    def _solution_text(self, item) -> str:
        return " ".join(f"{s.get('transformation','')} {s.get('intermediateResult','')}" for s in item["solution"]["steps"])

    def test_detector_rejects_the_old_wording(self):
        self.assertTrue(reverses_axes("Read across to the y-axis for x, then up or down to the x-axis for y"))
        self.assertFalse(reverses_axes("Read the horizontal position for the x-coordinate, then the vertical position for the y-coordinate."))

    def test_no_read_point_solution_reverses_axes(self):
        saw_scaffold, saw_plain = False, False
        for s in range(1, 600):
            it = cl.generate(s, {"task": "read_point", "interactionType": "free-response"})
            txt = self._solution_text(it)
            self.assertFalse(reverses_axes(txt), f"seed {s} reverses axes: {txt!r}")
            if it["params"]["scaffold"]:
                saw_scaffold = True
                self.assertIn("Project the point vertically to the x-axis", txt)
            else:
                saw_plain = True
                self.assertIn("horizontal position for the x-coordinate", txt)
        self.assertTrue(saw_scaffold and saw_plain, "both scaffolded and unscaffolded read_point solutions exercised")

    def test_misconception_text_does_not_reverse_axes(self):
        for mid, m in MISCONCEPTIONS.items():
            self.assertFalse(reverses_axes(m["feedback"]), f"{mid} feedback reverses axes: {m['feedback']!r}")
            self.assertFalse(reverses_axes(m["observableError"]), f"{mid} rationale reverses axes")

    def test_all_distractor_rationales_clean(self):
        for s in range(1, 400):
            it = cl.generate(s, {"interactionType": "multiple-choice"})
            for d in it.get("distractors", []):
                self.assertFalse(reverses_axes(d["rationale"]), f"seed {s} distractor reverses axes")


_PACK = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "review", "coordinate_lines_review_pack.json")


@unittest.skipUnless(os.path.exists(_PACK), "review pack not built")
class TestReviewPackCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(_PACK, encoding="utf-8") as fh:
            cls.pack = json.load(fh)
        cls.items = [it for combo in cls.pack["combos"] for it in combo["items"]]

    def test_no_duplicate_task_interaction_seed(self):
        keys = [(it["task"], it["interactionType"], it["seed"]) for it in self.items]
        dups = sorted({k for k in keys if keys.count(k) > 1})
        self.assertEqual(dups, [], f"duplicate (task,interaction,seed): {dups}")

    def test_no_duplicate_canonical_items(self):
        sigs = [cl.serialize(cl.generate(it["seed"], {"task": it["task"], "interactionType": it["interactionType"]})) for it in self.items]
        self.assertEqual(len(sigs), len(set(sigs)), "duplicate canonical items in the pack")

    def test_interaction_coverage(self):
        supported = {
            "read_point": {"free-response", "multiple-choice"}, "plot_point": {"free-response"},
            "gradient_two_points": {"free-response", "multiple-choice"}, "midpoint": {"free-response", "multiple-choice"},
            "interpret_mx_c": {"free-response", "multiple-choice"}, "equation_from_graph": {"free-response", "multiple-choice"},
            "equation_from_two_points": {"free-response", "multiple-choice"},
        }
        present = {t: set() for t in supported}
        for it in self.items:
            present[it["task"]].add(it["interactionType"])
        for t, modes in supported.items():
            self.assertTrue(modes.issubset(present[t]), f"{t} missing interactions {modes - present[t]}")

    def test_band_coverage(self):
        required = {"plot_point": {1, 2}, "gradient_two_points": {2, 3, 4},
                    "equation_from_graph": {3, 4}, "equation_from_two_points": {3, 4, 5}}
        present = {t: set() for t in required}
        for it in self.items:
            if it["task"] in required:
                present[it["task"]].add(it["band"])
        for t, bands in required.items():
            self.assertTrue(bands.issubset(present[t]), f"{t} missing bands {bands - present[t]}")

    def test_cartesian_plane_objective_present(self):
        self.assertIn("SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01", json.dumps(self.pack))


class TestInteractionRules(unittest.TestCase):
    def test_plot_point_rejects_multiple_choice(self):
        with self.assertRaises(ValueError):
            cl.generate(5, {"task": "plot_point", "interactionType": "multiple-choice"})

    def test_explicit_interaction_is_honored(self):
        # An explicit MC request never silently returns free-response.
        it = cl.generate(3, {"task": "gradient_two_points", "interactionType": "multiple-choice"})
        self.assertEqual(it["interactionType"], "multiple-choice")
        self.assertEqual(len(it["distractors"]), 3)

    def test_every_task_validates_both_modes(self):
        for task in cl.TASKS:
            for inter in ("free-response", "multiple-choice"):
                if inter == "multiple-choice" and task == "plot_point":
                    continue
                it = cl.generate(11, {"task": task, "interactionType": inter})
                self.assertEqual(cl.validate(it)["status"], "pass", f"{task}/{inter}")


class TestLeakageRules(unittest.TestCase):
    def test_plot_point_target_absent(self):
        for s in range(1, 400):
            svg = cl.generate(s, {"task": "plot_point", "interactionType": "free-response"})["media"][0]["svg"]
            self.assertNotIn("<circle", svg, f"plot_point seed {s} must not draw the target point")

    def test_no_figure_text_states_an_answer(self):
        for s in range(1, 600):
            it = cl.generate(s, {"interactionType": "free-response"})
            if not it.get("media"):
                continue
            texts = re.findall(r"<text[^>]*>([^<]*)</text>", it["media"][0]["svg"])
            for t in texts:
                self.assertFalse(any(ch in t for ch in (",", "/", "=")),
                                 f"seed {s}: figure text {t!r} would leak a coordinate/fraction/equation")

    def test_equation_from_graph_has_neutral_label_only(self):
        it = cl.generate(11, {"task": "equation_from_graph", "interactionType": "free-response"})
        labels = re.findall(r'<text class="cx-lbl"[^>]*>([^<]*)</text>', it["media"][0]["svg"])
        self.assertIn("l", labels)
        self.assertNotIn(it["answer"]["display"], it["media"][0]["svg"])

    def test_vertical_lines_excluded_from_finite_gradient_tasks(self):
        for task in ("gradient_two_points", "equation_from_graph", "equation_from_two_points"):
            for s in range(1, 500):
                p = cl.generate(s, {"task": task, "interactionType": "free-response"})["params"]
                self.assertNotEqual(p["x1"], p["x2"], f"{task} seed {s} produced a vertical configuration")


class TestExportContract(unittest.TestCase):
    def test_png_envelope_is_6000x4200(self):
        t = cl.png_export_transform()
        self.assertEqual((t["scale"], t["width"], t["height"]), (6, 6000, 4200))


class TestArtifactIntegrity(unittest.TestCase):
    MANIFEST = "docs/review/coordinate_lines_manifest.json"
    AUDIT = "docs/review/coordinate_lines_visual_audit.html"
    PACK_MD = "docs/review/coordinate_lines_review_pack.md"
    PACK_JSON = "docs/review/coordinate_lines_review_pack.json"

    def _read(self, rel):
        with open(os.path.join(ROOT, rel.replace("/", os.sep)), encoding="utf-8") as fh:
            return fh.read()

    def setUp(self):
        if not os.path.exists(os.path.join(ROOT, self.MANIFEST)):
            self.skipTest("manifest not generated (run oracle/make_coordinate_lines_manifest.py)")

    def test_audit_version_matches_generator(self):
        man = json.loads(self._read(self.MANIFEST))
        self.assertEqual(man["generatorVersion"], cl.GENERATOR_VERSION)
        ver = re.search(r'data-generator-version="([^"]+)"', self._read(self.AUDIT)).group(1)
        self.assertEqual(ver, cl.GENERATOR_VERSION)
        self.assertIn(cl.GENERATOR_VERSION, self._read(self.PACK_MD))

    def test_audit_commit_matches_build(self):
        man = json.loads(self._read(self.MANIFEST))
        com = re.search(r'data-git-commit="([^"]+)"', self._read(self.AUDIT)).group(1)
        self.assertEqual(com, man["gitCommit"])
        self.assertRegex(com, r"^[0-9a-f]{7,40}$")

    def test_no_other_generator_version_text(self):
        # The artifacts reference only the CURRENT version; the superseded v1.0.0 and other
        # families' versions must not appear.
        for rel in (self.AUDIT, self.PACK_MD):
            txt = self._read(rel)
            self.assertIn(cl.GENERATOR_VERSION, txt, f"{rel} must state the current version")
            for stale in ("1.0.0", "1.1.0", "1.2.0", "1.2.1", "1.2.2", "1.2.3"):
                self.assertNotIn(stale, txt, f"unexpected version {stale} in {rel}")

    def test_manifest_hashes_match_files(self):
        man = json.loads(self._read(self.MANIFEST))
        for key, rel in {"reviewPackMd": self.PACK_MD, "reviewPackJson": self.PACK_JSON, "visualAudit": self.AUDIT,
                         "goldenFixture": "oracle/golden/coordinate_lines.golden.json",
                         "parityFixture": "oracle/golden/coordinate_lines.parity.json"}.items():
            with open(os.path.join(ROOT, rel.replace("/", os.sep)), "rb") as fh:
                digest = hashlib.sha256(fh.read()).hexdigest()
            self.assertEqual(digest, man["sha256"][key], f"manifest hash stale for {rel}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
