"""Oracle test suite for gen.functions.foundations v1.0.0 (pending-review).

  python oracle/tests/test_functions.py

Covers: schema conformance + machine validity of every task in every supported interaction; answer
types per task; the interaction policy (identify_function is MC-only, an unsupported request raises,
a no-task request never raises); reproducibility; every declared band reachable per task; every
eligible misconception rule exercised as a distractor with clean feedback; the JSON registry in sync
with the code registry; objective IDs resolve; the objective->task map matches the TS single source;
golden / parity fixtures reproducible; manifest integrity (canonical hashes) once frozen.
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "oracle", "spi_oracle"))
sys.path.insert(0, os.path.join(ROOT, "oracle"))

from build_meta import sha256_canonical  # noqa: E402
import check_conformance as cc  # noqa: E402
import functions as G  # noqa: E402
import functions_core as C  # noqa: E402
import functions_misconceptions as FM  # noqa: E402
from expression_checker import check_expression  # noqa: E402
from interval_checker import check_interval  # noqa: E402

_REG = cc.load_registry()
_SCHEMA = _REG["https://spi-math.academy/schemas/question-item.schema.json"]
SWEEP = int(os.environ.get("SPI_SWEEP", "400"))


def _valid(item) -> bool:
    errors: list = []
    cc.check(item, _SCHEMA, _REG, _SCHEMA, "item", errors)
    return not errors


class TestGeneratorContract(unittest.TestCase):
    def test_all_tasks_conform_and_validate(self):
        for task in G.TASKS:
            for inter in G.supported_interactions(task):
                for seed in range(1, 26):
                    item = G.generate(seed, {"task": task, "interactionType": inter})
                    self.assertTrue(_valid(item), f"{task}/{inter}/{seed} schema")
                    v = G.validate(item)
                    self.assertEqual(v["status"], "pass", f"{task}/{inter}/{seed}: " + ", ".join(c["name"] + ":" + c["detail"] for c in v["checks"] if c["result"] == "fail"))

    def test_answer_types_per_task(self):
        expected = {"choice": {"multiple-choice"}, "number": {"integer", "exact-rational"},
                    "expression": {"algebraic-expression"}, "interval": {"interval"}}
        for task in G.TASKS:
            fam = G.ANSWER_FAMILY[task]
            for seed in range(1, 16):
                item = G.generate(seed, {"task": task})
                self.assertIn(item["answer"]["type"], expected[fam], task)

    def test_interaction_policy(self):
        self.assertEqual(G.supported_interactions("identify_function"), ["multiple-choice"])
        with self.assertRaises(G.InteractionNotSupported):
            G.generate(1, {"task": "identify_function", "interactionType": "free-response"})
        with self.assertRaises(G.InteractionNotSupported):
            G.generate(1, {"task": "evaluate_function", "interactionType": "matching"})
        with self.assertRaises(ValueError):
            G.generate(1, {"task": "nope"})
        self.assertEqual(G.generate(3, {"task": "identify_function"})["interactionType"], "multiple-choice")
        self.assertEqual(G.generate(3, {"task": "evaluate_function"})["interactionType"], "free-response")
        # the legacy answerType selector is NOT consulted (ratio v1.0.2 precedent): default interaction per task,
        # so a legacy sweep exercises every task (identify_function stays MC) and never raises
        self.assertEqual(G.generate(3, {"task": "evaluate_function", "answerType": "multiple-choice"})["interactionType"], "free-response")
        self.assertEqual(G.generate(3, {"task": "identify_function", "answerType": "integer"})["interactionType"], "multiple-choice")
        self.assertEqual(G.serialize(G.generate(5, {"answerType": "integer"})), G.serialize(G.generate(5, {})))

    def test_no_task_request_never_raises_and_respects_pool(self):
        for seed in range(1, 200):
            fr = G.generate(seed, {"interactionType": "free-response"})
            self.assertEqual(fr["interactionType"], "free-response")
            self.assertNotEqual(fr["params"]["task"], "identify_function")
            mc = G.generate(seed, {"interactionType": "multiple-choice"})
            self.assertEqual(mc["interactionType"], "multiple-choice")
            G.generate(seed)

    def test_reproducible(self):
        for seed in (1, 7, 42, 999, 123456789):
            for inter in ("free-response", "multiple-choice"):
                a = G.serialize(G.generate(seed, {"interactionType": inter}))
                b = G.serialize(G.generate(seed, {"interactionType": inter}))
                self.assertEqual(a, b)

    def test_every_declared_band_reachable_per_task(self):
        for task, (lo, hi) in G.TASK_BANDS.items():
            seen = set()
            for seed in range(1, SWEEP + 1):
                seen.add(G.generate(seed, {"task": task})["difficulty"]["overallBand"])
                if seen >= set(range(lo, hi + 1)):
                    break
            self.assertTrue(seen >= set(range(lo, hi + 1)), f"{task}: bands seen {sorted(seen)} of declared {lo}-{hi}")
            self.assertTrue(seen <= set(range(lo, hi + 1)), f"{task}: band outside the declared range: {sorted(seen)}")

    def test_objective_map_and_registry(self):
        objs = json.load(open(os.path.join(ROOT, "curriculum", "objectives", "SPI.IBDPAASL.FUNC.json"), encoding="utf-8"))
        ids = {o["objectiveId"] for o in objs}
        self.assertEqual(set(G.OBJECTIVE_BY_TASK.values()), ids)
        self.assertEqual(len(G.TASKS), 11)
        for o in objs:
            self.assertEqual(o["reviewStatus"], "proposed")
            for mid in o.get("commonMisconceptions", []):
                self.assertIn(mid, FM.MISCONCEPTIONS, f"{o['objectiveId']} cites unknown {mid}")
        ts = open(os.path.join(ROOT, "core", "curriculum", "functions-objective-ids.ts"), encoding="utf-8").read()
        for task, oid in G.OBJECTIVE_BY_TASK.items():
            self.assertIn(f'{task}: "{oid}"', ts, "TS single-source map must list the same task -> objective pairs")

    def test_describe_conforms(self):
        d = G.describe()
        gen_schema = _REG["https://spi-math.academy/schemas/generator-module.schema.json"]
        errors: list = []
        cc.check(d, gen_schema, _REG, gen_schema, "describe", errors)
        self.assertEqual(errors, [])
        self.assertEqual(set(d["supportedObjectives"]), set(G.OBJECTIVE_BY_TASK.values()))


class TestMathematics(unittest.TestCase):
    def test_solutions_are_exact_and_independent_checks_hold(self):
        # composite of a quadratic outer with a linear inner expands correctly and the inverse round-trips
        item = G.generate(3, {"task": "composite_expression"})
        v = G.validate(item)
        self.assertEqual(v["status"], "pass")
        inv = G.generate(5, {"task": "inverse_expression"})
        a, b = C.rat_from_json(inv["params"]["a"]), C.rat_from_json(inv["params"]["b"])
        stored = G.Poly.from_json(inv["answer"]["canonical"])
        self.assertTrue(G.Poly.linear(a, b).compose(stored).equals(G.Poly.x()))

    def test_displays_reparse_through_the_family_checkers(self):
        for task in G.TASKS:
            if G.ANSWER_FAMILY[task] not in ("expression", "interval"):
                continue
            for seed in range(1, 40):
                ans = G.generate(seed, {"task": task})["answer"]
                if G.ANSWER_FAMILY[task] == "expression":
                    self.assertEqual(check_expression(ans["display"], ans["canonical"])["code"], "correct", ans["display"])
                else:
                    self.assertEqual(check_interval(ans["display"], ans["canonical"])["code"], "correct", ans["display"])

    def test_domain_and_range_variables(self):
        for seed in range(1, 40):
            d = G.generate(seed, {"task": "domain_of_function"})["answer"]["canonical"]
            self.assertTrue(d["kind"] == "reals" or d["variable"] == "x")
            r = G.generate(seed, {"task": "range_of_function"})["answer"]["canonical"]
            self.assertTrue(r["kind"] == "reals" or r["variable"] == "y")

    def test_sqrt_inputs_always_perfect_squares_and_reciprocal_never_at_pole(self):
        for seed in range(1, 300):
            it = G.generate(seed, {"task": "evaluate_function"})
            rule = C.rule_from_json(it["params"]["rule"])
            p = C.rat_from_json(it["params"]["p"])
            self.assertIsNotNone(C.eval_rule(rule, p))


class TestMisconceptions(unittest.TestCase):
    def test_every_eligible_rule_exercised_with_clean_feedback(self):
        for task in G.TASKS:
            if task in G.MC_ONLY_TASKS:
                continue
            eligible = set(FM.rules_for(task))
            seen = set()
            for seed in range(1, 3001):
                it = G.generate(seed, {"task": task, "interactionType": "multiple-choice"})
                for d in it.get("distractors", []):
                    seen.add(d["misconceptionId"])
                if seen >= eligible:
                    break
            self.assertEqual(seen, eligible, f"{task}: never exercised {sorted(eligible - seen)}")

    def test_identify_function_options_structure(self):
        for seed in range(1, 200):
            it = G.generate(seed, {"task": "identify_function"})
            opts = it["options"]
            self.assertEqual(len(opts), 4)
            wrong_ids = sorted(o["misconceptionId"] for o in opts if not o["correct"])
            self.assertEqual(wrong_ids, sorted(FM.STRUCTURAL_ONLY))
            self.assertEqual(sum(1 for o in opts if not G._is_function_relation(o["value"])), 1)

    def test_json_registry_in_sync(self):
        path = os.path.join(ROOT, "core", "misconceptions", "functions.json")
        recs = json.load(open(path, encoding="utf-8"))
        self.assertEqual({r["misconceptionId"] for r in recs}, set(FM.MISCONCEPTIONS))
        for r in recs:
            m = FM.MISCONCEPTIONS[r["misconceptionId"]]
            self.assertEqual(r["title"], m["title"])
            self.assertEqual(r["observableError"], m["observableError"])
            self.assertEqual(r["validRange"]["levels"], ["ibdp-aasl"])
        self.assertEqual(recs, FM.registry_records(), "core/misconceptions/functions.json must be regenerated (make_functions_misconceptions.py)")

    def test_placeholder_detector(self):
        self.assertTrue(G._has_placeholder("Divide by a then subtract b"))
        self.assertFalse(G._has_placeholder("a constant that is added must be subtracted"))
        self.assertFalse(G._has_placeholder("The axis of symmetry is x = -b/(2a)."))
        self.assertTrue(G._has_placeholder("substitute p into the rule"))


class TestFixtures(unittest.TestCase):
    def test_golden_reproducible(self):
        path = os.path.join(ROOT, "oracle", "golden", "functions.golden.json")
        if not os.path.exists(path):
            self.skipTest("golden not generated (run oracle/run_functions.py)")
        for g in json.load(open(path, encoding="utf-8")):
            cfg = {}
            if g.get("task"):
                cfg["task"] = g["task"]
            if g.get("interaction"):
                cfg["interactionType"] = g["interaction"]
            item = G.generate(g["seed"], cfg)
            self.assertEqual(G.serialize(item), g["serialized"], f"golden seed {g['seed']} {g.get('task')}")
            self.assertEqual(G.validate(item)["status"] == "pass", g["valid"])

    def test_parity_reproducible(self):
        path = os.path.join(ROOT, "oracle", "golden", "functions.parity.json")
        if not os.path.exists(path):
            self.skipTest("parity not generated")
        entries = json.load(open(path, encoding="utf-8"))
        self.assertGreaterEqual(len(entries), 400)
        for e in entries:
            self.assertEqual(G.serialize(G.generate(e["seed"], {"task": e["task"], "interactionType": e["interaction"]})), e["serialized"])


class TestManifestIntegrity(unittest.TestCase):
    def test_manifest_canonical_hashes_match_disk(self):
        path = os.path.join(ROOT, "docs", "review", "functions_manifest.json")
        if not os.path.exists(path):
            self.skipTest("manifest not generated (run oracle/make_functions_manifest.py)")
        man = json.load(open(path, encoding="utf-8"))
        self.assertEqual(man["approvalStatus"], "pending-review")
        self.assertTrue(man["hiddenFromNormalStudioAndProduction"])
        for name, a in man["artifacts"].items():
            if not a.get("present", True):
                continue
            self.assertEqual(sha256_canonical(os.path.join(ROOT, a["path"])), a["sha256"], f"{name} drift: {a['path']}")
        self.assertEqual(man["generatorVersion"], G.GENERATOR_VERSION)


if __name__ == "__main__":
    unittest.main(verbosity=2)
