"""Oracle test suite for gen.stats.data-handling (owner P gates).

  python oracle/tests/test_data_handling.py

Covers: machine-validity sweep, reproducibility, interaction policy (free-response-only +
probability MC eligibility), fixture self-parity (golden + parity), review-pack coverage,
distribution band-reachability, misconception-registry shape, and artifact integrity (the
manifest SHA-256 hashes match the on-disk artifacts).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ORACLE = os.path.dirname(HERE)
ROOT = os.path.dirname(ORACLE)
sys.path.insert(0, os.path.join(ORACLE, "spi_oracle"))
sys.path.insert(0, ORACLE)

import data_handling as dh  # noqa: E402
import data_handling_misconceptions as mis  # noqa: E402

GOLDEN = os.path.join(ORACLE, "golden")
REVIEW = os.path.join(ROOT, "docs", "review")


class TestValidity(unittest.TestCase):
    def test_sweep_all_valid(self):
        bad = 0
        for seed in range(1, 1201):
            for cfg in ({}, {"interactionType": "multiple-choice"}):
                item = dh.generate(seed, cfg)
                dh.serialize(item)
                if dh.validate(item)["status"] != "pass":
                    bad += 1
        self.assertEqual(bad, 0, f"{bad} invalid items in sweep")

    def test_reproducible(self):
        for seed in (1, 7, 42, 999, 123456):
            for cfg in ({}, {"interactionType": "multiple-choice"}):
                self.assertEqual(dh.serialize(dh.generate(seed, cfg)), dh.serialize(dh.generate(seed, cfg)))


class TestInteractionPolicy(unittest.TestCase):
    def test_free_response_only_rejects_mc(self):
        with self.assertRaises(ValueError):
            dh.generate(1, {"interactionType": "multiple-choice", "task": "complete_frequency_table"})

    def test_complete_frequency_table_one_blank(self):
        it = dh.generate(3, {"task": "complete_frequency_table"})
        html = it["media"][0]["spec"]["html"]
        self.assertEqual(html.count('class="cx-blank"'), 1)
        self.assertIn("<input", html)

    def test_probability_mc_proper_only(self):
        n = 0
        for seed in range(1, 1500):
            try:
                it = dh.generate(seed, {"interactionType": "multiple-choice", "task": "single_event_probability"})
            except Exception:
                continue
            n += 1
            f = Fraction(it["answer"]["canonical"]["num"], it["answer"]["canonical"]["den"])
            self.assertNotIn(f, (Fraction(0), Fraction(1), Fraction(1, 2)))
            for o in it["options"]:
                if isinstance(o["value"], dict) and "num" in o["value"]:
                    p = Fraction(o["value"]["num"], o["value"]["den"])
                    self.assertTrue(0 <= p <= 1, f"prob option {p} out of range")
        self.assertGreater(n, 100)

    def test_unique_mode_only(self):
        from collections import Counter
        for seed in range(1, 800):
            it = dh.generate(seed, {"task": "mode_from_list"})
            c = Counter(it["params"]["dataset"]["values"]).most_common()
            self.assertTrue(len(c) >= 2 and c[0][1] != c[1][1], "mode must be unique")


class TestFixtureParity(unittest.TestCase):
    def test_golden_self_parity(self):
        golden = json.load(open(os.path.join(GOLDEN, "data_handling.golden.json"), encoding="utf-8"))
        for entry in golden:
            item = dh.generate(entry["seed"], entry["config"])
            self.assertEqual(dh.serialize(item), entry["serialized"], f"golden drift seed={entry['seed']}")
            self.assertEqual(dh.validate(item)["status"], entry["validation"])

    def test_parity_self_parity(self):
        parity = json.load(open(os.path.join(GOLDEN, "data_handling.parity.json"), encoding="utf-8"))
        for entry in parity:
            item = dh.generate(entry["seed"], {"interactionType": entry["mode"]})
            self.assertEqual(dh.serialize(item), entry["serialized"], f"parity drift seed={entry['seed']} {entry['mode']}")


class TestReviewPackCoverage(unittest.TestCase):
    def test_full_coverage(self):
        pack = json.load(open(os.path.join(REVIEW, "stats_data_handling_review_pack.json"), encoding="utf-8"))
        s = pack["summary"]
        self.assertEqual(s["missingCoverage"], [], f"missing: {s['missingCoverage']}")
        self.assertTrue(s["allValid"])
        self.assertEqual(s["coveredTokens"], s["requiredTokens"])
        # every registered misconception appears at least once
        self.assertEqual(set(s["misconceptionsShown"]), set(mis.MISCONCEPTIONS))


class TestDistribution(unittest.TestCase):
    def test_bands_reachable_and_valid(self):
        rep = json.load(open(os.path.join(REVIEW, "stats_data_handling_distribution.json"), encoding="utf-8"))
        self.assertEqual(rep["invalid"], 0)
        for task, info in rep["tasks"].items():
            self.assertEqual(info["unreachableBands"], [], f"{task} has unreachable bands {info['unreachableBands']}")


class TestMisconceptionRegistry(unittest.TestCase):
    def test_shape(self):
        for mid, m in mis.MISCONCEPTIONS.items():
            for f in ("id", "title", "formula", "description", "observableError", "feedback", "adapter"):
                self.assertIn(f, m)
            self.assertEqual(m["id"], mid)
            # observableError + feedback must not leak internal symbols
            for field in ("observableError", "feedback"):
                self.assertNotIn("c[", m[field])

    def test_distractors_distinct_and_recompute(self):
        for seed in range(1, 600):
            it = dh.generate(seed, {"interactionType": "multiple-choice"})
            if "options" not in it:
                continue
            vals = [json.dumps(o["value"], sort_keys=True) for o in it["options"]]
            self.assertEqual(len(set(vals)), len(vals), "options must be distinct")


class TestArtifactIntegrity(unittest.TestCase):
    """The manifest SHA-256 hashes must match the on-disk artifacts (no silent regeneration)."""

    def test_manifest_hashes(self):
        manifest = json.load(open(os.path.join(REVIEW, "stats_data_handling_manifest.json"), encoding="utf-8"))
        for name, a in manifest["artifacts"].items():
            if not a["present"]:
                continue
            full = os.path.join(ROOT, a["path"])
            self.assertTrue(os.path.exists(full), f"{name} missing: {a['path']}")
            h = hashlib.sha256()
            with open(full, "rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    h.update(chunk)
            self.assertEqual(h.hexdigest(), a["sha256"], f"{name} hash drift ({a['path']})")

    def test_manifest_metadata(self):
        manifest = json.load(open(os.path.join(REVIEW, "stats_data_handling_manifest.json"), encoding="utf-8"))
        self.assertEqual(manifest["generatorVersion"], dh.GENERATOR_VERSION)
        self.assertEqual(manifest["approvalStatus"], "pending-review")
        self.assertEqual(manifest["objectiveIds"], [dh.OBJECTIVE_BY_TASK[t] for t in dh.TASKS])


if __name__ == "__main__":
    print("OK" if unittest.main(exit=False, verbosity=1).result.wasSuccessful() else "FAIL")
