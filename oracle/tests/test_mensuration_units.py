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


if __name__ == "__main__":
    unittest.main(verbosity=2)
