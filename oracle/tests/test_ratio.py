"""gen.proportion.ratio oracle tests — exact math, parser/checkers, the independent validator,
the interaction policy, role-based figure leakage, and the parity-fixture reproducibility.

  python oracle/tests/test_ratio.py
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "oracle"))

import check_conformance as cc  # noqa: E402
from spi_oracle import ratio as R  # noqa: E402
from spi_oracle import ratio_core as RC  # noqa: E402
from spi_oracle import ratio_misconceptions as RM  # noqa: E402

_REG = cc.load_registry()
_ITEM = _REG["https://spi-math.academy/schemas/question-item.schema.json"]


def _conf(item):
    e = []
    cc.check(item, _ITEM, _REG, _ITEM, "item", e)
    return e


def _valid(item):
    v = R.validate(item)
    return (v.get("valid") if isinstance(v, dict) else v), [c["name"] for c in v["checks"] if not c["ok"]]


class TestMath(unittest.TestCase):
    def test_exact_reasoning(self):
        self.assertEqual(RC.simplify_parts([4, 6]), [2, 3])
        self.assertEqual(RC.simplify_parts([6, 4]), [3, 2])
        self.assertTrue(RC.ratios_equal([2, 3], [4, 6]))
        self.assertFalse(RC.ratios_equal([2, 3], [3, 2]))
        self.assertEqual(RC.share(20, [2, 3]), [8, 12])
        self.assertEqual(RC.share(30, [2, 3, 5]), [6, 9, 15])
        self.assertIsNone(RC.share(7, [2, 3]))
        self.assertEqual(RC.missing_part(18, 1, 0, [2, 3]), 12)
        self.assertIsNone(RC.missing_part(10, 1, 0, [2, 3]))
        self.assertEqual(RC.direct_proportion(12, 3, 5), Fraction(20))
        self.assertEqual(RC.unit_rate(12, 4), Fraction(3))
        self.assertEqual(RC.inverse_proportion(4, 6, 3), 8)
        self.assertIsNone(RC.inverse_proportion(5, 6, 4))


class TestCheckers(unittest.TestCase):
    def test_ratio_codes(self):
        self.assertEqual(RC.check_ratio([2, 3], "2:3")["code"], "correct")
        self.assertEqual(RC.check_ratio([2, 3], "4:6")["code"], "equivalent-not-simplified")
        self.assertTrue(RC.check_ratio([2, 3], "4:6")["partial"])
        self.assertEqual(RC.check_ratio([2, 3], "4:6", require_simplest=False)["code"], "correct")
        self.assertEqual(RC.check_ratio([2, 3], "3:2")["code"], "wrong-order")
        self.assertEqual(RC.check_ratio([2, 3], "4:5")["code"], "wrong-ratio")
        self.assertEqual(RC.check_ratio([2, 3], "2:3:5")["code"], "wrong-number-of-parts")
        self.assertEqual(RC.check_ratio([2, 3], "0:3")["code"], "zero-or-negative-part")
        self.assertEqual(RC.check_ratio([2, 3], "2.5:3")["code"], "unsupported-term")
        self.assertEqual(RC.check_ratio([2, 3], "2:3x")["code"], "unparsed-trailing-text")
        self.assertEqual(RC.check_ratio([2, 3], "hello")["code"], "malformed-response")
        self.assertEqual(RC.check_ratio([2, 3, 5], "4:6:10")["code"], "equivalent-not-simplified")

    def test_all_nine_ratio_codes_reachable(self):
        probes = ["2:3", "4:6", "3:2", "4:5", "2:3:5", "0:3", "2.5:3", "2:3x", "hello"]
        seen = {RC.check_ratio([2, 3], p)["code"] for p in probes}
        for code in RC.RATIO_RESULT_CODES:
            self.assertIn(code, seen, f"ratio result code {code} not reachable")

    def test_choice_codes(self):
        self.assertEqual(RC.check_choice("B", "B"), "correct")
        self.assertEqual(RC.check_choice("B", "A"), "wrong-choice")
        self.assertEqual(RC.check_choice("B", "??"), "malformed-response")

    def test_parser_rejections(self):
        for bad in ["2.5:3", "0:3", "-2:3", "2:", "2:3:4:5", "2,3", "2∶3", "two to three", "2 to 3"]:
            parts, code = RC.parse_ratio(bad)
            self.assertIsNone(parts, f"{bad} should not parse")
            self.assertIsNotNone(code)
        for good in ["2:3", "2 : 3", "4:6", "2:3:5", "4 : 6 : 10"]:
            parts, code = RC.parse_ratio(good)
            self.assertIsNotNone(parts, f"{good} should parse")
            self.assertIsNone(code)

    def test_ascii_anchored_no_unicode_or_oversized(self):
        # Regression for the adversarial-review CRITICAL parity break: the ASCII-anchored parser must
        # reject EVERY non-ASCII digit (Arabic-Indic/Persian/Devanagari/Thai/fullwidth/math-bold), any
        # mixed-script term, and any oversized (>12-digit) term as unsupported-term — identically to the
        # TS mirror (domains/proportion/ratio.test.ts pins the SAME corpus + expected codes). Pinning the
        # exact codes here + there asserts Py<->TS agreement on the learner-input GRADING path, which the
        # serialize-only golden/parity fixtures structurally cannot exercise.
        UNSUPPORTED = ["٢:٣", "３:４", "२:३", "𝟚:𝟛", "۲:۳", "๒:๓", "5:３", "２:40", "١٢:٣",
                       "1000000000000000000000:3", "9007199254740993:9007199254740993",
                       "2:33333333333333333333333333", "2∶3", "2 to 3", "2,3", "2.5:3"]
        for s in UNSUPPORTED:
            self.assertEqual(RC.check_ratio([2, 3], s)["code"], "unsupported-term", f"{s!r}")
        # ASCII still grades exactly as before
        self.assertEqual(RC.check_ratio([2, 3], "2:3")["code"], "correct")
        self.assertEqual(RC.check_ratio([2, 3], "4:6")["code"], "equivalent-not-simplified")


class TestGeneratorContract(unittest.TestCase):
    def test_all_tasks_conform_and_validate(self):
        for task in R.RATIO_TASKS:
            for seed in (1, 7, 50, 999):
                it = R.generate(seed, {"task": task})
                self.assertEqual(_conf(it), [], f"{task} seed={seed} conform")
                valid, bad = _valid(it)
                self.assertTrue(valid, f"{task} seed={seed} validate {bad}")

    def test_answer_types_per_task(self):
        want = {"simplify": "ratio", "write_from_quantities": "ratio", "ratio_to_fraction": "exact-rational",
                "fraction_to_ratio": "ratio", "share_two_part": "table-completion",
                "share_three_part": "table-completion", "inverse_proportion": "integer",
                "best_buy": "multiple-choice"}
        for task, atype in want.items():
            self.assertEqual(R.generate(11, {"task": task})["answer"]["type"], atype, task)
        # integer-when-whole tasks emit integer or exact-rational
        for task in ("direct_proportion", "unit_rate", "simple_scale", "missing_part"):
            self.assertIn(R.generate(11, {"task": task})["answer"]["type"], ("integer", "exact-rational"))

    def test_interaction_policy(self):
        # best_buy is MC-only: FR raises; the FR-ineligible tasks raise on MC; MC-eligible accept MC.
        with self.assertRaises(R.InteractionNotSupported):
            R.generate(1, {"task": "best_buy", "interactionType": "free-response"})
        for fr_only in ("write_from_quantities", "share_two_part", "share_three_part", "missing_part", "unit_rate", "simple_scale"):
            with self.assertRaises(R.InteractionNotSupported):
                R.generate(1, {"task": fr_only, "interactionType": "multiple-choice"})
        for mc in ("simplify", "ratio_to_fraction", "fraction_to_ratio", "direct_proportion", "inverse_proportion"):
            it = R.generate(3, {"task": mc, "interactionType": "multiple-choice"})
            self.assertEqual(it["interactionType"], "multiple-choice")
            self.assertTrue(it.get("options"), f"{mc} MC must carry options")

    def test_best_buy_strict_min(self):
        it = R.generate(7, {"task": "best_buy"})
        self.assertEqual(it["answer"]["type"], "multiple-choice")
        valid, bad = _valid(it)
        self.assertTrue(valid, bad)

    def test_role_based_no_leakage(self):
        for task in R.RATIO_TASKS:
            it = R.generate(13, {"task": task})
            v = R.validate(it)
            names = {c["name"]: c["ok"] for c in v["checks"]}
            for chk in ("student-figure-has-no-overlay", "student-unknown-marked-not-valued",
                        "answer-key-overlay-additive", "student-and-key-share-base", "student-a11y-no-result"):
                if chk in names:
                    self.assertTrue(names[chk], f"{task} {chk}")

    def test_reproducible(self):
        for task in R.RATIO_TASKS:
            a = R.serialize(R.generate(321, {"task": task}))
            b = R.serialize(R.generate(321, {"task": task}))
            self.assertEqual(a, b)


class TestDiagnostics(unittest.TestCase):
    def test_registry_conforms(self):
        schema = _REG["https://spi-math.academy/schemas/misconception.schema.json"]
        for m in RM.registry():
            e = []
            cc.check(m, schema, _REG, schema, m["misconceptionId"], e)
            self.assertEqual(e, [], m["misconceptionId"])
        self.assertEqual(len(RM.ALL_IDS), 16)


class TestRegressionDefects(unittest.TestCase):
    """Regression guards for the five confirmed v1.0.0 defects (oracle-first; mirrored in TS)."""

    def test_best_buy_mc_option_displays_pairwise_distinct(self):
        # DEFECT 4: two non-winning options could share a unit rate -> byte-identical displays.
        # Over a wide seed sweep every best_buy MC item must have pairwise-distinct option DISPLAYS,
        # the new mc-option-displays-distinct validator must pass, and the formerly-bad seeds repro clean.
        for seed in range(1, 3001):
            it = R.generate(seed, {"task": "best_buy"})
            disps = [o["display"] for o in it["options"]]
            self.assertEqual(len(set(disps)), len(disps), f"seed {seed} duplicate displays {disps}")
            names = {c["name"]: c["ok"] for c in R.validate(it)["checks"]}
            self.assertTrue(names.get("mc-option-displays-distinct"), f"seed {seed} displays-distinct check")
        for seed in (95, 271, 314, 549, 748, 992):
            it = R.generate(seed, {"task": "best_buy"})
            disps = [o["display"] for o in it["options"]]
            self.assertEqual(len(set(disps)), len(disps), f"formerly-dup seed {seed}: {disps}")

    def test_no_task_free_response_never_raises(self):
        # DEFECT 5: a no-task free-response request must NEVER raise InteractionNotSupported, and must
        # never select an MC-only task (best_buy).
        for seed in range(1, 2501):
            it = R.generate(seed, {"interactionType": "free-response"})
            self.assertEqual(it["interactionType"], "free-response", seed)
            self.assertNotIn(it["params"]["task"], R.MC_ONLY_TASKS, f"seed {seed} picked MC-only task")

    def test_every_declared_band_reachable_per_task(self):
        # DEFECT 6/7: every band in the DECLARED inclusive range [lo,hi] is produced across a seed
        # sweep (the previously-unreachable interior band of the four 3-span tasks now occurs).
        from collections import Counter
        per = {t: Counter() for t in R.RATIO_TASKS}
        for seed in range(1, 6001):
            it = R.generate(seed)
            p = it["params"]
            per[p["task"]][it["difficulty"]["overallBand"]] += 1
        for task in R.RATIO_TASKS:
            lo, hi = R.TASK_BANDS[task]
            for band in range(lo, hi + 1):
                self.assertGreater(per[task][band], 0,
                                   f"{task} band {band} in declared range [{lo},{hi}] is unreachable")

    def test_misconception_reverse_relationships(self):
        # DEFECT 8: the two omitted reverse objectiveRelationships are present.
        by_id = {m["misconceptionId"]: m for m in RM.MISCONCEPTIONS}
        self.assertIn("SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01",
                      by_id["MISC.RATIO.NOT_SIMPLIFIED"]["objectiveRelationships"])
        self.assertIn("SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01",
                      by_id["MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE"]["objectiveRelationships"])


class TestRevisionCorrections(unittest.TestCase):
    """v1.0.1 owner REVISE corrections #3 (context-value compatibility), #4 (best-buy cost-like
    semantics), #5 (simple-scale wording + answer contract), #6 (collided diagnostic dedup)."""

    _COUNT_NOUNS = {"books", "apples", "pencils", "eggs"}

    def test_version_bump(self):
        # decision #8: generator + validator at 1.0.2 (REVISE simple_scale grammar changed canonical
        # bytes; v1.0.1 preserved at tag ratio-v1.0.1). The ITEM SCHEMA version (schemaVersion) stays 1.0.0.
        self.assertEqual(R.GENERATOR_VERSION, "1.0.2")
        self.assertEqual(R.VALIDATOR_VERSION, "1.0.2")
        it = R.generate(1, {"task": "simplify"})
        self.assertEqual(it["schemaVersion"], "1.0.0")        # item schema unchanged
        self.assertEqual(it["generatorVersion"], "1.0.2")     # generator version bumped
        self.assertEqual(R.validate(it)["validatorVersion"], "1.0.2")

    def test_no_fractional_count_noun_in_rate_tasks(self):
        # CORRECTION #3: a direct_proportion / unit_rate item NEVER shows a count noun with a
        # fractional answer; the context-domain validator checks must pass for every item.
        for seed in range(1, 4000):
            for task in ("direct_proportion", "unit_rate"):
                it = R.generate(seed, {"task": task})
                p = it["params"]
                amount = p["givenLabel"] if task == "direct_proportion" else p["amountLabel"]
                f = Fraction(it["answer"]["canonical"]["num"], it["answer"]["canonical"]["den"])
                if amount in self._COUNT_NOUNS:
                    self.assertEqual(f.denominator, 1,
                                     f"{task} seed {seed}: fractional {amount} answer {f}")
                names = {c["name"]: c["ok"] for c in R.validate(it)["checks"]}
                for chk in ("context-answer-compatible", "discrete-count-answer-integer",
                            "rational-answer-uses-continuous-or-average-context",
                            "no-fractional-books-students-sheets-or-people"):
                    self.assertTrue(names.get(chk), f"{task} seed {seed} {chk}")
                if task == "unit_rate":
                    self.assertTrue(names.get("unit-rate-context-allows-rational"))

    def test_context_domain_registry_classifies_every_amount_noun(self):
        # every amount noun used by the rate tasks is classified in the registry.
        used = set()
        for seed in range(1, 2000):
            for task in ("direct_proportion", "unit_rate"):
                p = R.generate(seed, {"task": task})["params"]
                used.add(p["givenLabel"] if task == "direct_proportion" else p["amountLabel"])
        for noun in used:
            self.assertIn(noun, R._CONTEXT_DOMAINS, f"{noun} unclassified")

    def test_best_buy_cost_like_lowest_per_item(self):
        # CORRECTION #4: best_buy marks the lowest-cost-per-item option, cost is in tokens (no currency),
        # and the new validator checks pass.
        for seed in range(1, 3000):
            it = R.generate(seed, {"task": "best_buy"})
            p = it["params"]
            instr = it["prompt"]["instruction"]
            self.assertIn("tokens", instr)
            for sym in ("$", "£", "€", "¥"):
                self.assertNotIn(sym, instr)
            self.assertIn(f"the lowest cost per {p['item']}", instr)
            # the correct option IS the strict-min tokens-per-item
            rates = {o["label"]: Fraction(o["tokenCost"], o["itemCount"]) for o in p["options"]}
            mn = min(rates.values())
            winners = [lab for lab, r in rates.items() if r == mn]
            self.assertEqual(len(winners), 1)
            self.assertEqual(p["correctLabel"], winners[0])
            names = {c["name"]: c["ok"] for c in R.validate(it)["checks"]}
            for chk in ("best-buy-rate-direction-consistent",
                        "best-buy-context-has-cost-like-denominator",
                        "best-buy-strict-minimum-cost-per-unit",
                        "best-buy-prompt-matches-validator",
                        "best-buy-feedback-matches-rate-direction",
                        "no-lowest-product-amount-as-best-value"):
                self.assertTrue(names.get(chk), f"seed {seed} {chk}")

    def test_best_buy_diagnostics_are_wrong_options(self):
        # CORRECTION #4: each best_buy diagnostic predicts a WRONG option (never the correct one) and
        # follows the cost-per-item direction (max raw tokens / min raw tokens).
        for seed in range(1, 1500):
            it = R.generate(seed, {"task": "best_buy"})
            p = it["params"]
            for d in RM.diagnostics_for("best_buy", p):
                self.assertNotEqual(d["predictedResponse"], p["correctLabel"],
                                    f"seed {seed} diagnostic points at correct option")

    def test_simple_scale_dimensionless_grammar(self):
        # CORRECTION #5: no cm/km/m; grammatical singular/plural units; a bare-number answer.
        import re
        for seed in range(1, 4000):
            it = R.generate(seed, {"task": "simple_scale"})
            p = it["params"]
            instr = it["prompt"]["instruction"]
            for tok in ("cm", "km", "centimetre", "kilometre", "metre", " m "):
                self.assertNotIn(tok, instr, f"seed {seed} has measurement unit {tok!r}")
            # never "1 <word>s"
            self.assertIsNone(re.search(r"\b1 (model|plan|drawing|map|real|actual|ground) units\b", instr),
                              f"seed {seed} bad singular: {instr}")
            # answer is a bare rational number = value*num/den
            f = Fraction(it["answer"]["canonical"]["num"], it["answer"]["canonical"]["den"])
            self.assertEqual(f, Fraction(p["value"]) * Fraction(p["factorNum"], p["factorDen"]))
            names = {c["name"]: c["ok"] for c in R.validate(it)["checks"]}
            for chk in ("scale-unit-wording-grammatical", "singular-plural-units-correct",
                        "scale-answer-contract-matches-prompt",
                        "measurement-unit-answer-not-bare-number", "no-cross-unit-conversion-in-v1"):
                self.assertTrue(names.get(chk), f"seed {seed} {chk}")

    def test_simple_scale_singular_unit_is_grammatical(self):
        # spot the singular case: a count of 1 must read "1 <word>" not "1 <word>s".
        seen_singular = False
        for seed in range(1, 5000):
            it = R.generate(seed, {"task": "simple_scale"})
            p = it["params"]
            if 1 in (p["factorNum"], p["factorDen"], p["value"]):
                instr = it["prompt"]["instruction"]
                # the unit word right after a lone " 1 " must be singular
                self.assertNotRegex(instr, r"\b1 \w+ units\b")
                seen_singular = True
        self.assertTrue(seen_singular, "expected at least one scale item with a unit count of 1")

    def test_diagnostic_predictions_distinct_per_item(self):
        # CORRECTION #6: no item returns two diagnostics with the same predicted response counted as
        # exercised; the colliding duplicate is dropped.
        for seed in range(1, 4000):
            it = R.generate(seed)
            p = it["params"]
            preds = [d["predictedResponse"] for d in RM.diagnostics_for(p["task"], p)]
            self.assertEqual(len(preds), len(set(preds)),
                             f"seed {seed} task {p['task']} duplicate predicted responses {preds}")

    def test_diagnostic_collision_not_counted_as_exercised(self):
        # CORRECTION #6: the share_three_part collision (two diagnostics, identical predicted response)
        # now yields a single exercised diagnostic.
        it = R.generate(14, {"task": "share_three_part"})
        p = it["params"]
        ds = RM.diagnostics_for("share_three_part", p)
        preds = [d["predictedResponse"] for d in ds]
        self.assertEqual(len(preds), len(set(preds)))
        # the surviving canonical diagnostic is the FIRST in emit/registry order (WRONG_TOTAL_PARTS).
        self.assertEqual(ds[0]["misconceptionId"], "MISC.RATIO.WRONG_TOTAL_PARTS")

    def _grammar_blob(self, it):
        parts = [it["prompt"]["instruction"]]
        for s in it["solution"]["steps"]:
            parts.append(s["transformation"]); parts.append(s["intermediateResult"])
        for o in it.get("options", []):
            parts.append(str(o.get("display", "")))
        media = it.get("media") or []
        if media:
            m = media[0]
            for row in (m.get("dataTableFallback") or {}).get("rows", []):
                parts.extend(str(c) for c in row)
            for row in ((m.get("spec") or {}).get("answerKeyDataTableFallback") or {}).get("rows", []):
                parts.extend(str(c) for c in row)
        return "  ".join(parts)

    def test_no_grammar_errors_across_all_tasks(self):
        # FOLLOW-UP: ZERO "1 <plural>" and ZERO "per <plural>"/"per shelve" across a 3000-seed sweep of
        # EVERY task; the noun-count-grammatical validator check must pass for every item.
        import re as _re
        one_re = _re.compile(r"\b1 ([a-z]+s)\b")
        per_re = _re.compile(r"\bper ([a-z]+)\b")
        for seed in range(1, 3001):
            for task in R.RATIO_TASKS:
                it = R.generate(seed, {"task": task})
                blob = self._grammar_blob(it)
                for m in one_re.finditer(blob):
                    self.assertNotIn(m.group(1), R._PLURAL_FORMS,
                                     f"{task} seed {seed}: '1 {m.group(1)}'")
                for m in per_re.finditer(blob):
                    self.assertNotIn(m.group(1), R._PLURAL_FORMS,
                                     f"{task} seed {seed}: 'per {m.group(1)}'")
                names = {c["name"]: c["ok"] for c in R.validate(it)["checks"]}
                self.assertTrue(names.get("noun-count-grammatical"),
                                f"{task} seed {seed} noun-count-grammatical")

    def test_count_helper_singular_plural(self):
        # the grammatical helpers produce explicit singular/plural (no naive [:-1]).
        self.assertEqual(R._count(1, "boxes"), "1 box")
        self.assertEqual(R._count(3, "boxes"), "3 boxes")
        self.assertEqual(R._count(1, "shelves"), "1 shelf")
        self.assertEqual(R._count(5, "shelves"), "5 shelves")
        self.assertEqual(R._count(1, "tokens"), "1 token")
        self.assertEqual(R._count(1, "daisies"), "1 daisy")
        self.assertEqual(R._count(2, "daisies"), "2 daisies")
        self.assertEqual(R._singular("shelves"), "shelf")
        self.assertEqual(R._singular("spoons"), "spoon")
        # mass nouns are invariant
        self.assertEqual(R._count(1, "flour"), "1 flour")
        self.assertEqual(R._count(3, "flour"), "3 flour")
        # scale unit words pluralize regularly via the fallback
        self.assertEqual(R._units(1, "model unit"), "1 model unit")
        self.assertEqual(R._units(2, "model unit"), "2 model units")

    def test_grammar_violations_detector(self):
        # the detector flags exactly the bad forms and nothing grammatical.
        self.assertEqual(R._grammar_violations("there are 1 boys here"), ["1 boys"])
        self.assertEqual(R._grammar_violations("how many per shelve"), ["per shelve"])
        self.assertEqual(R._grammar_violations("per shelves now"), ["per shelves"])
        self.assertEqual(R._grammar_violations("1 box and 3 boxes per shelf"), [])
        self.assertEqual(R._grammar_violations("1 flour is uncountable"), [])

    def test_diagnostic_rationale_and_feedback_match_prediction(self):
        # CORRECTION #6: every returned diagnostic carries the rationale + feedback for its own
        # misconception (the registry source of truth), matching its predicted response + error.
        by_id = {m["misconceptionId"]: m for m in RM.MISCONCEPTIONS}
        for seed in range(1, 1500):
            it = R.generate(seed)
            p = it["params"]
            for d in RM.diagnostics_for(p["task"], p):
                reg = by_id[d["misconceptionId"]]
                self.assertEqual(d["observableError"], reg["observableError"])
                self.assertEqual(d["feedback"], reg["feedback"])
                self.assertIsNotNone(d["predictedResponse"])


class TestParityFixture(unittest.TestCase):
    def test_parity_fixture_reproducible(self):
        path = os.path.join(ROOT, "oracle", "golden", "ratio.parity.json")
        if not os.path.exists(path):
            self.skipTest("parity fixture not generated")
        entries = json.load(open(path, encoding="utf-8"))
        self.assertGreaterEqual(len(entries), 300)
        for e in entries[::7]:
            self.assertEqual(R.serialize(R.generate(e["seed"], {"task": e["task"]})), e["serialized"])


class TestManifestIntegrity(unittest.TestCase):
    def test_manifest_hashes_match_disk(self):
        # The review-pack manifest records sha256 of every frozen artifact; an integrity check must be
        # able to re-hash disk and find NO drift. (Caught the re-audit case where the manifest was committed
        # with hashes from an intermediate pre-regeneration state.) make_ratio_manifest.py must be the LAST
        # build step so its recorded hashes + gitCommit match the artifacts the same commit produced.
        import hashlib
        path = os.path.join(ROOT, "docs", "review", "proportion_ratio_manifest.json")
        if not os.path.exists(path):
            self.skipTest("manifest not generated")
        man = json.load(open(path, encoding="utf-8"))
        arts = man.get("artifacts", {})
        self.assertTrue(arts, "manifest has no artifacts")
        for name, meta in arts.items():
            p, want = meta.get("path"), meta.get("sha256")
            if not p or not want:
                continue
            fp = os.path.join(ROOT, p)
            if not os.path.exists(fp):
                self.assertFalse(meta.get("present", True), f"{name}: recorded present but missing on disk")
                continue
            got = hashlib.sha256(open(fp, "rb").read()).hexdigest()
            self.assertEqual(got, want, f"{name} hash drift: {p}")
        self.assertEqual(man.get("approvalStatus"), "pending-review")
        self.assertIs(man.get("hiddenFromNormalStudioAndProduction"), True)


class TestArtifactIdentity(unittest.TestCase):
    """Owner REVISE #1: the manifest + visual audit + browser-verification + review pack must all identify
    ONE generator version + ONE git commit; no stale commit/version text. (The submitted v1.0.0 package had
    the manifest on one commit and the audit/browser report on another.)"""

    def setUp(self):
        import re as _re
        RD = os.path.join(ROOT, "docs", "review")
        for f in ("proportion_ratio_manifest.json", "proportion_ratio_browser_verification.json",
                  "proportion_ratio_review_pack.json", "proportion_ratio_visual_audit.html"):
            if not os.path.exists(os.path.join(RD, f)):
                self.skipTest(f"{f} not generated")
        self._re = _re
        self.man = json.load(open(os.path.join(RD, "proportion_ratio_manifest.json"), encoding="utf-8"))
        self.brv = json.load(open(os.path.join(RD, "proportion_ratio_browser_verification.json"), encoding="utf-8"))
        self.pack = json.load(open(os.path.join(RD, "proportion_ratio_review_pack.json"), encoding="utf-8"))
        self.audit = open(os.path.join(RD, "proportion_ratio_visual_audit.html"), encoding="utf-8").read()

    def _audit_attr(self, name):
        m = self._re.search(rf'{name}="([^"]+)"', self.audit)
        return m.group(1) if m else None

    def test_manifest_commit_matches_audit(self):
        self.assertEqual(self.man.get("gitCommit"), self._audit_attr("data-git-commit"))

    def test_manifest_commit_matches_browser_report(self):
        self.assertEqual(self.man.get("gitCommit"), self.brv.get("gitCommit"))

    def test_review_pack_version_matches_generator(self):
        self.assertEqual(self.pack.get("generatorVersion") or self.pack.get("version"), R.GENERATOR_VERSION)

    def test_audit_version_matches_generator(self):
        self.assertEqual(self._audit_attr("data-generator-version"), R.GENERATOR_VERSION)

    def test_browser_report_version_matches_audit(self):
        self.assertEqual(self.brv.get("generatorVersion"), self._audit_attr("data-generator-version"))

    def test_no_stale_commit_text(self):
        # the audit must not embed any commit other than the manifest's build commit.
        commit = self.man.get("gitCommit", "")
        hexes = set(self._re.findall(r"\b[0-9a-f]{12,40}\b", self.audit))
        stale = [h for h in hexes if not commit.startswith(h) and not h.startswith(commit[:12])]
        self.assertEqual(stale, [], f"stale commit hashes in audit: {stale}")
        # and no stale generator version string.
        self.assertNotIn("v1.0.0", self.audit.replace("ratio-v1.0.0", ""))

    def test_real_browser_styles_present_and_passing(self):
        # Owner REVISE #2: the browser report must carry REAL captured computed styles + pass every check.
        self.assertIsNotNone(self.brv.get("realBrowserComputedStyles"), "realBrowserComputedStyles is null")
        for m in ("premium", "premium-dark", "accessible", "print"):
            self.assertIn(m, self.brv["realBrowserComputedStyles"])
        names = {c["name"]: c["ok"] for c in self.brv["checks"]}
        for req in ("real-browser-computed-styles-present", "premium-computed-styles-match",
                    "premium-dark-computed-styles-match", "accessible-computed-styles-match",
                    "print-computed-styles-match", "unknown-marker-visible-in-every-mode",
                    "dark-mode-readable", "print-mode-authoritative-captured"):
            self.assertTrue(names.get(req), f"browser check failed/missing: {req}")
        self.assertTrue(self.brv.get("allPassed"))


class TestScaleGrammar(unittest.TestCase):
    """Owner REVISE (v1.0.2): simple_scale subject-verb agreement + the false-pass fix. The verb must agree
    with the subject count ("1 plan unit represents" / "2 plan units represent") on every rendered surface,
    and the validator must INSPECT the rendered text (the v1.0.1 check passed "1 plan unit represent")."""

    NAMED = ("scale-singular-represents", "scale-plural-represent", "scale-prompt-grammar-valid",
             "scale-a11y-grammar-valid", "scale-svg-desc-grammar-valid",
             "scale-unit-wording-grammatical-inspects-rendered-text",
             "singular-plural-units-correct-inspects-rendered-text",
             "scale-unit-wording-grammatical", "singular-plural-units-correct")

    def test_grammar_predicate_catches_the_exact_bad_wording(self):
        # the owner's exact example must be flagged; the corrected forms must be clean.
        self.assertEqual(RC_scale("On a plan, 1 plan unit represent 2 actual units."), False)
        self.assertEqual(RC_scale("On a plan, 1 plan unit represents 2 actual units."), True)
        self.assertEqual(RC_scale("On a map, 2 map units represent 3 ground units."), True)
        self.assertEqual(RC_scale("On a map, 2 map units represents 3 ground units."), False)

    def test_validator_fails_the_bad_wording(self):
        # tamper a valid item's rendered prompt to the bad wording -> scale-prompt-grammar-valid must FAIL.
        it = R.generate(13, {"task": "simple_scale"})  # factorDen == 1
        it["prompt"]["instruction"] = it["prompt"]["instruction"].replace("represents", "represent", 1)
        names = {c["name"]: c["ok"] for c in R.validate(it)["checks"]}
        self.assertFalse(names["scale-prompt-grammar-valid"])
        self.assertFalse(names["scale-unit-wording-grammatical"])
        self.assertFalse(names["scale-singular-represents"])

    def test_all_named_checks_pass_for_real_items(self):
        seen_sing = seen_plur = False
        for s in list(range(1, 1201)) + [4]:
            it = R.generate(s, {"task": "simple_scale"})
            names = {c["name"]: c["ok"] for c in R.validate(it)["checks"]}
            for n in self.NAMED:
                self.assertTrue(names.get(n), f"seed {s}: {n} failed")
            instr = it["prompt"]["instruction"]
            if it["params"]["factorDen"] == 1:
                seen_sing = True
                self.assertIn(" unit represents ", instr)
            else:
                seen_plur = True
                self.assertIn(" units represent ", instr)
        self.assertTrue(seen_sing and seen_plur, "did not exercise both singular and plural subjects")

    def test_seed_4_regression(self):
        it = R.generate(4, {"task": "simple_scale"})
        self.assertTrue(R.validate(it)["valid"])


def RC_scale(text):
    """True iff `text` has no scale count/verb-agreement violation (helper for the grammar test)."""
    return R._grammar_violations(text) == []


if __name__ == "__main__":
    unittest.main(verbosity=2)
