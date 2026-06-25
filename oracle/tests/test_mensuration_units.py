"""Oracle test suite for the gen.measurement.mensuration dimensional-quantity contract (owner D).

  python oracle/tests/test_mensuration_units.py

Covers the unit parser / formatter / equivalence checker: equivalent numerical forms with the
correct unit; bare number (missing-unit); wrong base unit (incl. the no-conversion case);
linear-vs-square confusion (wrong-exponent); a different dimensional quantity (wrong-dimension);
incorrect value with the correct unit; malformed input; canonical ASCII formatting; and
Unicode-superscript / Unicode-minus / English-alias acceptance.
"""

from __future__ import annotations

import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spi_oracle"))

import mensuration_units as U  # noqa: E402


def code(s, expected) -> str:
    return U.check_response(s, expected)["code"]


class TestFormatter(unittest.TestCase):
    def test_canonical_ascii(self):
        self.assertEqual(U.format_quantity(U.make_length(Fraction(15, 2), "cm")), "15/2 cm")
        self.assertEqual(U.format_quantity(U.make_area(24, "cm")), "24 cm^2")
        self.assertEqual(U.format_quantity(U.make_length(7, "mm")), "7 mm")

    def test_screen_superscript_variant(self):
        self.assertEqual(U.format_quantity_display(U.make_area(24, "cm")), "24 cm²")
        self.assertEqual(U.format_quantity_display(U.make_length(7, "m")), "7 m")

    def test_encode_answer_shape(self):
        enc = U.encode_quantity_answer(U.make_area(24, "cm"))
        self.assertEqual(enc["type"], "quantity")
        self.assertEqual(enc["canonical"], {"num": 24, "den": 1})
        self.assertEqual(enc["measure"], {"dimension": "area", "baseUnit": "cm", "exponent": 2})
        self.assertEqual(enc["display"], "24 cm^2")
        self.assertNotIn("display", enc["measure"])  # display is not duplicated inside measure


class TestChecker(unittest.TestCase):
    def setUp(self):
        self.L_cm = U.make_length(15, "cm")
        self.A_cm = U.make_area(24, "cm")
        self.Lhalf = U.make_length(Fraction(15, 2), "cm")

    def test_equivalent_value_correct_unit_accepted(self):
        self.assertEqual(code("15 cm", self.L_cm), "correct")
        self.assertEqual(code("30/2 cm", self.L_cm), "correct")
        self.assertEqual(code("24 cm^2", self.A_cm), "correct")
        self.assertEqual(code("30/4 cm", self.Lhalf), "correct")

    def test_correct_number_no_unit_is_missing_unit(self):
        self.assertEqual(code("15", self.L_cm), "missing-unit")
        self.assertEqual(code("24", self.A_cm), "missing-unit")

    def test_correct_number_wrong_base_unit(self):
        self.assertEqual(code("15 m", self.L_cm), "wrong-base-unit")
        self.assertEqual(code("15 mm", self.L_cm), "wrong-base-unit")

    def test_no_cross_unit_conversion(self):
        # 100 cm must NOT be accepted when 1 m is required (owner D): no silent conversion.
        self.assertEqual(code("100 cm", U.make_length(1, "m")), "wrong-base-unit")
        r = U.check_response("100 cm", U.make_length(1, "m"))
        self.assertFalse(r["correct"])
        self.assertIn("metres", r["feedback"])

    def test_linear_instead_of_square(self):
        self.assertEqual(code("24 cm", self.A_cm), "wrong-exponent")

    def test_square_instead_of_linear(self):
        self.assertEqual(code("15 cm^2", self.L_cm), "wrong-exponent")

    def test_wrong_dimension_different_base_and_power(self):
        self.assertEqual(code("24 m^2", self.L_cm), "wrong-dimension")

    def test_incorrect_value_correct_unit(self):
        self.assertEqual(code("16 cm", self.L_cm), "incorrect-value")

    def test_malformed_inputs(self):
        for bad in ["15 cm long", "1e3 cm", "cm", "", "  ", "abc", "15 fathoms"]:
            self.assertEqual(code(bad, self.L_cm), "malformed-response", bad)

    def test_alias_and_unicode_forms(self):
        self.assertEqual(code("12cm", U.make_length(12, "cm")), "correct")
        self.assertEqual(code("3/2 m", U.make_length(Fraction(3, 2), "m")), "correct")
        self.assertEqual(code("1.5 mm", U.make_length(Fraction(3, 2), "mm")), "correct")
        self.assertEqual(code("24 cm²", self.A_cm), "correct")
        self.assertEqual(code("15 centimetres", self.L_cm), "correct")
        self.assertEqual(code("24 square cm", self.A_cm), "correct")
        self.assertEqual(code("24 cm squared", self.A_cm), "correct")

    def test_unicode_minus_normalized(self):
        self.assertEqual(code("−5 cm", U.make_length(-5, "cm")), "correct")

    def test_all_reject_codes_reachable(self):
        seen = {code(s, e) for s, e in [
            ("15 cm", self.L_cm), ("16 cm", self.L_cm), ("15", self.L_cm),
            ("15 m", self.L_cm), ("24 cm", self.A_cm), ("24 m^2", self.L_cm), ("x", self.L_cm),
        ]}
        self.assertEqual(seen, set(U.RESULT_CODES))


class TestCheckerEvidence(unittest.TestCase):
    """Owner C3: genuinely-different equivalent forms, all seven codes, and no cross-unit conversion."""

    def setUp(self):
        self.rat_area = U.make_area(Fraction(105, 2), "mm")   # 105/2 mm^2 -> 52.5
        self.int_len = U.make_length(15, "cm")

    def test_all_declared_checker_codes_reached(self):
        codes = set()
        for ans in (self.rat_area, self.int_len, U.make_area(24, "cm")):
            for e in U.checker_evidence(ans):
                codes.add(U.check_response(e["response"], ans)["code"])
        self.assertEqual(codes, set(U.RESULT_CODES))

    def test_evidence_matches_expected_codes(self):
        for ans in (self.rat_area, self.int_len):
            for e in U.checker_evidence(ans):
                self.assertEqual(U.check_response(e["response"], ans)["code"], e["expectedCode"], e["scenario"])

    def test_equivalent_form_is_not_canonical_copy(self):
        ev = U.checker_evidence(self.rat_area)
        diff = [e for e in ev if e["genuinelyDifferent"] and U.check_response(e["response"], self.rat_area)["code"] == "correct"]
        self.assertGreaterEqual(len(diff), 3)
        for e in diff:
            self.assertNotEqual(e["response"], U.format_quantity(self.rat_area))

    def test_equivalent_rational_form_accepted(self):
        self.assertEqual(U.check_response("210/4 mm^2", self.rat_area)["code"], "correct")

    def test_equivalent_decimal_form_accepted(self):
        self.assertEqual(U.check_response("52.5 mm^2", self.rat_area)["code"], "correct")
        self.assertEqual(U.format_decimal(Fraction(105, 2)), "52.5")

    def test_unicode_superscript_accepted(self):
        self.assertEqual(U.check_response("105/2 mm²", self.rat_area)["code"], "correct")

    def test_no_space_unit_form_accepted(self):
        self.assertEqual(U.check_response("15cm", self.int_len)["code"], "correct")

    def test_malformed_response_reachable(self):
        for bad in ["15e2 cm", "15 cm long", "15 cm mm", "15/ cm", "15 cm^3", "15 cm/s", "", "15 cm 15 cm"]:
            self.assertEqual(U.check_response(bad, self.int_len)["code"], "malformed-response", bad)

    def test_scientific_notation_rejected(self):
        self.assertEqual(U.check_response("1e3 cm", self.int_len)["code"], "malformed-response")

    def test_trailing_text_rejected(self):
        self.assertEqual(U.check_response("15 cm long", self.int_len)["code"], "malformed-response")

    def test_conflicting_units_rejected(self):
        self.assertEqual(U.check_response("15 cm mm", self.int_len)["code"], "malformed-response")

    def test_cross_unit_conversion_not_performed(self):
        self.assertEqual(U.check_response("100 cm", U.make_length(1, "m"))["code"], "wrong-base-unit")
        self.assertEqual(U.check_response("10000 cm^2", U.make_area(1, "m"))["code"], "wrong-base-unit")


if __name__ == "__main__":
    unittest.main(verbosity=2)
