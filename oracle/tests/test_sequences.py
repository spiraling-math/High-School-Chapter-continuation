"""Tests for the arithmetic-sequences oracle generator.

Run:  python oracle/tests/test_sequences.py
   or python -m unittest -v   (from the oracle/ directory)

Covers: known values, reproducibility, invalid parameters, distractor
invariants, and a 10,000-seed property sweep that must yield ZERO invalid items.
"""

from __future__ import annotations

import os
import sys
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spi_oracle import sequences as seq          # noqa: E402
from spi_oracle.seeded_random import Mulberry32   # noqa: E402
from spi_oracle.misconceptions import MISCONCEPTIONS  # noqa: E402

SWEEP = int(os.environ.get("SPI_SWEEP", "10000"))


class TestPRNG(unittest.TestCase):
    def test_determinism(self):
        a = Mulberry32(123456789)
        b = Mulberry32(123456789)
        self.assertEqual([a.next_uint32() for _ in range(20)],
                         [b.next_uint32() for _ in range(20)])

    def test_uint32_range(self):
        r = Mulberry32(1)
        for _ in range(1000):
            v = r.next_uint32()
            self.assertTrue(0 <= v <= 0xFFFFFFFF)

    def test_float_range(self):
        r = Mulberry32(7)
        for _ in range(1000):
            f = r.next_float()
            self.assertTrue(0.0 <= f < 1.0)

    def test_next_int_inclusive_and_in_range(self):
        r = Mulberry32(99)
        seen = set()
        for _ in range(5000):
            v = r.next_int(3, 8)
            self.assertTrue(3 <= v <= 8)
            seen.add(v)
        self.assertEqual(seen, {3, 4, 5, 6, 7, 8})  # full range reachable


class TestKnownValues(unittest.TestCase):
    def test_nth_term(self):
        self.assertEqual(seq.solve({"task": "nth_term", "a1": 4, "d": 3, "n": 10}), 31)

    def test_nth_term_negative_d(self):
        self.assertEqual(seq.solve({"task": "nth_term", "a1": 20, "d": -3, "n": 7}), 2)

    def test_sum_n(self):
        # 1 + 3 + 5 + ... (a1=1, d=2), first 10 terms = 100
        self.assertEqual(seq.solve({"task": "sum_n", "a1": 1, "d": 2, "n": 10}), 100)

    def test_sum_matches_iterative(self):
        params = {"task": "sum_n", "a1": -5, "d": 4, "n": 13}
        terms = [(-5) + 4 * k for k in range(13)]
        self.assertEqual(seq.solve(params), sum(terms))

    def test_find_d(self):
        # nth term 31 from a1=4, n=10 -> d = (31-4)/9 = 3
        self.assertEqual(seq.solve({"task": "find_d", "a1": 4, "d": 3, "n": 10}), 3)

    def test_find_n(self):
        self.assertEqual(seq.solve({"task": "find_n_for_value", "a1": 4, "d": 3, "n": 10}), 10)


class TestReproducibility(unittest.TestCase):
    def test_same_seed_identical_serialization(self):
        for s in (1, 42, 123456789, 2147483647, 555):
            a = seq.serialize(seq.generate(s, {"answerType": "multiple-choice"}))
            b = seq.serialize(seq.generate(s, {"answerType": "multiple-choice"}))
            self.assertEqual(a, b, f"non-reproducible for seed {s}")

    def test_same_seed_identical_integer_mode(self):
        for s in (2, 17, 9999):
            a = seq.serialize(seq.generate(s, {"answerType": "integer"}))
            b = seq.serialize(seq.generate(s, {"answerType": "integer"}))
            self.assertEqual(a, b)


class TestInvalidParameters(unittest.TestCase):
    def test_reject_unknown_task(self):
        with self.assertRaises(ValueError):
            seq.generate(1, {"task": "bogus"})

    def test_reject_mc_for_reverse_task(self):
        with self.assertRaises(ValueError):
            seq.generate(1, {"task": "find_d", "answerType": "multiple-choice"})

    def test_validator_catches_out_of_domain(self):
        item = seq.generate(1, {"task": "nth_term", "answerType": "integer"})
        item["params"]["d"] = 0  # corrupt to an invalid common difference
        result = seq.validate(item)
        self.assertEqual(result["status"], "fail")
        names = {c["name"]: c["result"] for c in result["checks"]}
        self.assertEqual(names["params-in-domain"], "fail")

    def test_validator_catches_wrong_answer(self):
        item = seq.generate(1, {"task": "nth_term", "answerType": "integer"})
        item["answer"]["canonical"] += 1  # corrupt the answer
        result = seq.validate(item)
        self.assertEqual(result["status"], "fail")


class TestPropertySweep(unittest.TestCase):
    def test_sweep_zero_invalid(self):
        failing = []
        tasks = {}
        bands = {}
        for s in range(1, SWEEP + 1):
            # Integer mode (any task)
            item_i = seq.generate(s, {"answerType": "integer"})
            r_i = seq.validate(item_i)
            if r_i["status"] != "pass":
                failing.append((s, "integer", r_i))
            tasks[item_i["params"]["task"]] = tasks.get(item_i["params"]["task"], 0) + 1
            b = item_i["difficulty"]["overallBand"]
            bands[b] = bands.get(b, 0) + 1

            # Multiple-choice mode (forward tasks) — exercises distractors
            item_m = seq.generate(s, {"answerType": "multiple-choice"})
            r_m = seq.validate(item_m)
            if r_m["status"] != "pass":
                failing.append((s, "multiple-choice", r_m))

        self.assertEqual(failing, [], f"{len(failing)} invalid items; first: {failing[:1]}")
        # Variety sanity: every task type appears, more than one band appears.
        self.assertEqual(set(tasks.keys()), set(seq.ALL_TASKS), f"task coverage {tasks}")
        self.assertGreater(len(bands), 1, f"band variety {bands}")

    def test_mc_distractor_invariants(self):
        for s in range(1, min(SWEEP, 3000) + 1):
            item = seq.generate(s, {"answerType": "multiple-choice"})
            answer = item["answer"]["canonical"]
            wrong = [o["value"] for o in item["options"] if not o["correct"]]
            self.assertNotIn(answer, wrong, f"distractor==answer at seed {s}")
            self.assertEqual(len(wrong), len(set(wrong)), f"dup distractor at seed {s}")
            self.assertGreaterEqual(len(wrong), 3, f"<3 distractors at seed {s}")
            self.assertEqual(sum(1 for o in item["options"] if o["correct"]), 1)
            # Distinct misconceptions (no repeated error pathway in one item).
            mids = [d["misconceptionId"] for d in item["distractors"]]
            self.assertEqual(len(set(mids)), len(mids), f"repeated misconception at seed {s}")
            # Each distractor equals its misconception formula (semantic agreement).
            for d in item["distractors"]:
                rule = MISCONCEPTIONS[d["misconceptionId"]]["formula"]
                self.assertEqual(int(rule(item["params"])), d["value"], f"rule mismatch seed {s}")

    def test_distractor_semantic_agreement_regression(self):
        # Required regression seeds from the curriculum review.
        for s in (1, 2, 3, 86):
            for task in ("nth_term", "sum_n"):
                item = seq.generate(s, {"task": task, "answerType": "multiple-choice"})
                self.assertEqual(seq.validate(item)["status"], "pass", f"seed {s} {task}")
                for d in item["distractors"]:
                    m = MISCONCEPTIONS[d["misconceptionId"]]
                    self.assertEqual(int(m["formula"](item["params"])), d["value"])
                    self.assertEqual(d["rationale"], m["observableError"])
                    self.assertTrue(m["feedback"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
