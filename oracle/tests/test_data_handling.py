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
        self.assertEqual(s["missingCells"], [], f"missing cells: {s['missingCells']}")
        self.assertTrue(s["allValid"])
        self.assertTrue(s["allCovered"])
        self.assertEqual(s["coveredTokens"], s["requiredTokens"])
        self.assertEqual(s["coveredCells"], s["requiredCells"])
        # every registered misconception appears at least once
        self.assertEqual(set(s["misconceptionsShown"]), set(mis.MISCONCEPTIONS))


class TestReviewPackCoverageMatrix(unittest.TestCase):
    """Owner coverage correction — the review pack must exhibit every reachable
    task/interaction/band cell and every realised answer shape; the coverage claim must be honest."""

    @classmethod
    def setUpClass(cls):
        cls.pack = json.load(open(os.path.join(REVIEW, "stats_data_handling_review_pack.json"), encoding="utf-8"))
        cls.dist = json.load(open(os.path.join(REVIEW, "stats_data_handling_distribution.json"), encoding="utf-8"))
        cls.matrix = cls.pack["coverageMatrix"]

    def test_every_reachable_task_band_covered(self):
        for task, t in self.dist["tasks"].items():
            for b in (int(x) for x in t["bandCounts"]):
                cell = self.matrix[task]["bands"][str(b)]
                self.assertTrue(cell["reachable"] and cell["hasExemplar"],
                                f"{task} band {b} reachable but not exemplified")

    def test_every_supported_interaction_covered(self):
        for task, t in self.dist["tasks"].items():
            self.assertTrue(self.matrix[task]["interactions"]["free-response"]["hasExemplar"], f"{task} FR")
            if t["multipleChoice"] > 0:
                self.assertTrue(self.matrix[task]["interactions"]["multiple-choice"]["hasExemplar"], f"{task} MC")
            else:  # genuinely unreachable -> must be documented, not silently omitted
                self.assertFalse(self.matrix[task]["interactions"]["multiple-choice"]["reachable"])
                self.assertNotEqual(self.matrix[task]["interactions"]["multiple-choice"]["note"], "")

    def test_every_task_answer_shape_covered(self):
        for task, t in self.dist["tasks"].items():
            for shape in t["answerTypes"]:
                self.assertTrue(self.matrix[task]["shapes"][shape]["hasExemplar"],
                                f"{task} answer shape {shape} not exemplified")

    def test_coverage_summary_matches_records(self):
        s = self.pack["summary"]
        recs = self.pack["records"]
        self.assertEqual(s["itemCount"], len(recs))
        # every matrix exemplar seed references an actual record of that task
        seeds_by_task = {}
        for r in recs:
            seeds_by_task.setdefault(r["task"], set()).add(r["seed"])
        for task, m in self.matrix.items():
            for fam in ("interactions", "bands", "shapes"):
                for _k, v in m[fam].items():
                    if v.get("hasExemplar"):
                        self.assertIn(v["exemplarSeed"], seeds_by_task.get(task, set()),
                                      f"{task} {fam} exemplar seed {v['exemplarSeed']} not in records")

    def test_required_token_count_derived_from_matrix(self):
        s = self.pack["summary"]
        derived = sum((1 + (1 if t["multipleChoice"] > 0 else 0)) + len(t["bandCounts"]) + len(t["answerTypes"])
                      for t in self.dist["tasks"].values())
        self.assertEqual(s["requiredCells"], derived)
        self.assertEqual(s["derivedRequiredCells"], derived)

    def test_no_false_full_coverage_claim(self):
        s = self.pack["summary"]
        self.assertEqual(s["allCovered"], (not s["missingCells"]) and (not s["missingCoverage"]))


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
        self.assertEqual(manifest["approvalStatus"], "approved")
        self.assertEqual(manifest["objectiveIds"], [dh.OBJECTIVE_BY_TASK[t] for t in dh.TASKS])


class TestUniqueMode(unittest.TestCase):
    def test_unique_mode(self):
        self.assertIsNone(dh.unique_mode([1, 2, 3, 4]))        # all distinct
        self.assertIsNone(dh.unique_mode([1, 1, 2, 2]))        # tie for greatest
        self.assertIsNone(dh.unique_mode([]))
        self.assertEqual(dh.unique_mode([4, 4, 4, 7, 9]), 4)
        self.assertEqual(dh.unique_mode([2, 5, 5, 8]), 5)


class TestContextDomains(unittest.TestCase):
    def test_no_negative_in_count_context(self):
        # full sweep: any list/frequency context with a negative value must be signed/context-free.
        for seed in range(1, 3001):
            for cfg in ({}, {"interactionType": "multiple-choice"}):
                it = dh.generate(seed, cfg)
                ds = it["params"]["dataset"]
                vals = ds.get("values") if "values" in ds else ds.get("frequencies", [])
                if any(v < 0 for v in vals):
                    dom = dh.CONTEXT_DOMAINS.get(ds.get("title"))
                    self.assertIn(dom, ("signed", "context-free"),
                                  f"negative value in non-signed context {ds.get('title')!r} (seed {seed})")

    def test_regression_mean_seeds_3_and_6(self):
        for seed in (3, 6):
            for cfg in ({}, {"interactionType": "multiple-choice", "task": "mean_from_list"}):
                it = dh.generate(seed, cfg if "task" in cfg else {"task": "mean_from_list"})
                self.assertEqual(dh.validate(it)["status"], "pass", f"mean seed {seed} must be valid")
                ds = it["params"]["dataset"]
                if any(v < 0 for v in ds["values"]):
                    self.assertIn(dh.CONTEXT_DOMAINS.get(ds["title"]), ("signed", "context-free"))


class TestModeDistractor(unittest.TestCase):
    def test_avg_uses_mode_only_with_unique_mode(self):
        for seed in range(1, 3001):
            it = dh.generate(seed, {"interactionType": "multiple-choice"})
            mids = [o.get("misconceptionId") for o in it.get("options", [])]
            if "MISC.STAT.AVG_USES_MODE" in mids:
                self.assertIsNotNone(dh.unique_mode(it["params"]["dataset"]["values"]),
                                     f"AVG_USES_MODE used without a unique mode (seed {seed})")


class TestPictogram(unittest.TestCase):
    def test_exact_symbol_and_distinct_half_rules(self):
        for seed in range(1, 2000):
            it = dh.generate(seed, {"interactionType": "multiple-choice", "task": "read_pictogram"})
            ds = it["params"]["dataset"]; key = ds["pictogramKey"]
            fr = ds["frequencies"][it["params"]["queryIndex"]]
            unit = key // 2 if key % 2 == 0 else key
            self.assertEqual(fr % unit, 0, "queried symbol count must be exact")
            half = (fr % key) == (key // 2) and key % 2 == 0
            mids = [o.get("misconceptionId") for o in it["options"]]
            if half:  # owner #3: no exact-whole-count distractor when a half symbol is shown
                self.assertNotIn("MISC.STAT.PICTO_COUNTS_SYMBOLS", mids)


class TestFreqDiagnostics(unittest.TestCase):
    def test_blank_kind_solution_operation(self):
        for seed in range(1, 3001):
            it = dh.generate(seed, {"task": "complete_frequency_table"})
            kind = it["params"]["blank"]["kind"]
            first = it["solution"]["steps"][0]["transformation"].lower()
            if kind == "total":
                self.assertIn("add", first)
                self.assertNotIn("subtract", first)
            else:
                self.assertIn("subtract", first)

    def test_regression_seeds_14_and_21(self):
        for seed in (14, 21):
            it = dh.generate(seed, {"task": "complete_frequency_table"})
            self.assertEqual(dh.validate(it)["status"], "pass")


class TestMedianSolution(unittest.TestCase):
    def test_even_length_shows_average(self):
        seen_even = False
        for seed in range(1, 2000):
            it = dh.generate(seed, {"task": "median_from_list"})
            v = it["params"]["dataset"]["values"]
            text = " ".join(s.get("transformation", "") + " " + s.get("intermediateResult", "") for s in it["solution"]["steps"]).lower()
            if len(v) % 2 == 0:
                seen_even = True
                self.assertIn("two middle values", text)
                self.assertIn("average", text)
            else:
                self.assertIn("single middle value", text)
        self.assertTrue(seen_even, "an even-length median example must occur")


class TestSignedDisplay(unittest.TestCase):
    def test_signed_sum_expression(self):
        self.assertEqual(dh._sum_expr([8, -5, -6]), "8 − 5 − 6")
        self.assertEqual(dh._sum_expr([-1, -4, 13, 6, 15]), "-1 − 4 + 13 + 6 + 15")


class TestReconciliation(unittest.TestCase):
    """Owner #7 — a single authoritative source for difficulty ranges + misconception IDs."""

    def test_ranges_single_source(self):
        objs = {o["objectiveId"]: o for o in json.load(open(os.path.join(ROOT, "curriculum", "objectives", "SPI.MIDDLE.STAT.json"), encoding="utf-8"))}
        desc = dh.describe()
        for task, band in dh.TASK_BANDS.items():
            oid = dh.OBJECTIVE_BY_TASK[task]
            o = objs[oid]
            self.assertEqual([o["difficultyRange"]["min"], o["difficultyRange"]["max"]], list(band), f"objective range {oid}")
            self.assertEqual(desc["difficultyRanges"][oid], list(band), f"descriptor range {oid}")

    def test_review_ranges_match_objective(self):
        pack = json.load(open(os.path.join(REVIEW, "stats_data_handling_review_pack.json"), encoding="utf-8"))
        for r in pack["records"]:
            lo, hi = dh.TASK_BANDS[r["task"]]
            self.assertTrue(lo <= r["difficulty"]["overallBand"] <= hi, f"{r['task']} band out of declared range")

    def test_misconception_ids_resolve_no_stale(self):
        objs = json.load(open(os.path.join(ROOT, "curriculum", "objectives", "SPI.MIDDLE.STAT.json"), encoding="utf-8"))
        for o in objs:
            for mid in o["commonMisconceptions"]:
                self.assertIn(mid, mis.MISCONCEPTIONS, f"stale misconception id {mid} in {o['objectiveId']}")


class TestDirectReadScale(unittest.TestCase):
    """Owner v1.0.2 — every queried bar/line value must land on a visible scale mark."""

    def _mark_ys(self, svg):
        return dh._grid_tick_ys(svg)

    def test_every_queried_value_on_a_visible_mark(self):
        off = 0
        for seed in range(1, 4001):
            for task in ("read_bar_chart", "read_line_graph"):
                it = dh.generate(seed, {"task": task, "interactionType": "free-response"})
                self.assertEqual(dh.validate(it)["status"], "pass")
                ds = it["params"]["dataset"]
                vals = ds.get("values") or ds["frequencies"]
                major, minor, ymax = dh._chart_scale(vals)
                q = vals[it["params"]["queryIndex"]]
                self.assertEqual(q % minor, 0, f"queried {q} not on the minor grid (seed {seed} {task})")
                svg = it["media"][0]["svg"]
                self.assertIn(dh._py(ymax, q), self._mark_ys(svg), f"queried y not on a visible mark (seed {seed} {task})")
                if q % major != 0:
                    off += 1  # resolved by a minor subdivision (acceptable)
        self.assertGreater(off, 0, "some queried values should exercise the minor subdivision grid")

    def test_minor_step_divides_major_and_not_overloaded(self):
        for seed in range(1, 3001):
            for task in ("read_bar_chart", "read_line_graph"):
                it = dh.generate(seed, {"task": task})
                vals = it["params"]["dataset"].get("values") or it["params"]["dataset"]["frequencies"]
                major, minor, ymax = dh._chart_scale(vals)
                self.assertEqual(major % minor, 0)
                self.assertLessEqual(ymax // minor, dh.MAX_MINOR_LINES)
                self.assertGreaterEqual(dh._subdiv_px(minor, ymax), dh.MIN_SUBDIV_PX)

    def test_named_regression_seeds_19_35_39(self):
        # The owner's seeds 19/35/39: in v1.0.2 every read_bar_chart item is exactly readable.
        for seed in (19, 35, 39):
            it = dh.generate(seed, {"task": "read_bar_chart", "interactionType": "free-response"})
            self.assertEqual(dh.validate(it)["status"], "pass", f"seed {seed} must be valid")
            ds = it["params"]["dataset"]
            major, minor, ymax = dh._chart_scale(ds["frequencies"])
            q = ds["frequencies"][it["params"]["queryIndex"]]
            self.assertEqual(q % minor, 0, f"seed {seed} queried value must sit on a visible mark")
            self.assertIn(dh._py(ymax, q), self._mark_ys(it["media"][0]["svg"]))

    def test_readability_distribution_zero_off_grid(self):
        rep = json.load(open(os.path.join(REVIEW, "stats_data_handling_distribution.json"), encoding="utf-8"))
        for task, a in rep["directReadAudit"].items():
            self.assertEqual(a["queriedOffGrid"], 0, f"{task} has off-grid queried values")
            self.assertEqual(a["itemsRequiringVisualEstimation"], 0)


if __name__ == "__main__":
    print("OK" if unittest.main(exit=False, verbosity=1).result.wasSuccessful() else "FAIL")
