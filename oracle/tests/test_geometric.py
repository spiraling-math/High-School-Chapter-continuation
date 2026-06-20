"""Tests for the geometric-sequences oracle generator.

Run:  python oracle/tests/test_geometric.py
"""

from __future__ import annotations

import os
import sys
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spi_oracle import geometric as geo  # noqa: E402
from spi_oracle.geometric_misconceptions import MISCONCEPTIONS  # noqa: E402

SWEEP = int(os.environ.get("SPI_SWEEP", "10000"))


def P(task, u1, rnum, rden, **kw):
    p = {"task": task, "u1": u1, "r": {"num": rnum, "den": rden}}
    p.update(kw)
    return p


class TestKnownValues(unittest.TestCase):
    def test_nth_term(self):
        self.assertEqual(geo.solve(P("nth_term", 2, 3, 1, n=4)), Fraction(54))

    def test_nth_term_fraction(self):
        self.assertEqual(geo.solve(P("nth_term", 9, -2, 3, n=3)), Fraction(4))

    def test_sum_n(self):
        self.assertEqual(geo.solve(P("sum_n", 1, 2, 1, n=4)), Fraction(15))

    def test_sum_infinite(self):
        self.assertEqual(geo.solve(P("sum_infinite", 6, 1, 2)), Fraction(12))

    def test_sum_infinite_fraction(self):
        self.assertEqual(geo.solve(P("sum_infinite", 5, 1, 3)), Fraction(15, 2))

    def test_find_r(self):
        self.assertEqual(geo.solve(P("find_r", 2, 3, 1, k=2)), Fraction(3))

    def test_find_r_cube_root(self):
        self.assertEqual(geo.solve(P("find_r", 2, 1, 2, k=4)), Fraction(1, 2))

    def test_find_n(self):
        self.assertEqual(geo.solve(P("find_n_for_value", 2, 3, 1, n=4)), 4)


class TestReproducibility(unittest.TestCase):
    def test_same_seed_identical(self):
        for s in (1, 42, 123456789, 2147483647, 555):
            for at in ("integer", "multiple-choice"):
                a = geo.serialize(geo.generate(s, {"answerType": at}))
                b = geo.serialize(geo.generate(s, {"answerType": at}))
                self.assertEqual(a, b, f"seed {s} {at}")


class TestInvalidParameters(unittest.TestCase):
    def test_unknown_task(self):
        with self.assertRaises(ValueError):
            geo.generate(1, {"task": "bogus"})

    def test_mc_for_free_task(self):
        with self.assertRaises(ValueError):
            geo.generate(1, {"task": "sum_infinite", "answerType": "multiple-choice"})

    def test_validator_catches_corrupt_answer(self):
        item = geo.generate(1, {"task": "nth_term", "answerType": "integer"})
        item["answer"]["canonical"]["num"] += 1
        self.assertEqual(geo.validate(item)["status"], "fail")


class TestPropertySweep(unittest.TestCase):
    def test_sweep_zero_invalid(self):
        failing = []
        tasks = set()
        for s in range(1, SWEEP + 1):
            it = geo.generate(s, {"answerType": "integer"})
            if geo.validate(it)["status"] != "pass":
                failing.append((s, "integer"))
            tasks.add(it["params"]["task"])
            im = geo.generate(s, {"answerType": "multiple-choice"})
            if geo.validate(im)["status"] != "pass":
                failing.append((s, "mc"))
        self.assertEqual(failing, [], f"{len(failing)} invalid; first {failing[:1]}")
        self.assertEqual(tasks, set(geo.ALL_TASKS), f"task coverage {tasks}")

    def test_mc_distractor_semantics(self):
        for s in range(1, min(SWEEP, 3000) + 1):
            item = geo.generate(s, {"answerType": "multiple-choice"})
            ds = item["distractors"]
            mids = [d["misconceptionId"] for d in ds]
            self.assertEqual(len(set(mids)), len(mids), f"repeated misconception seed {s}")
            u1, r, n = item["params"]["u1"], Fraction(item["params"]["r"]["num"], item["params"]["r"]["den"]), item["params"]["n"]
            for d in ds:
                expected = Fraction(MISCONCEPTIONS[d["misconceptionId"]]["formula"](u1, r, n))
                stored = Fraction(d["value"]["num"], d["value"]["den"])
                self.assertEqual(expected, stored, f"rule mismatch seed {s}")

    def test_regression_seeds(self):
        for s in (1, 2, 3, 86):
            for task in ("nth_term", "sum_n"):
                item = geo.generate(s, {"task": task, "answerType": "multiple-choice"})
                self.assertEqual(geo.validate(item)["status"], "pass", f"seed {s} {task}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
