"""Unit tests for ordinal-scale contradiction detection (ADR-003)."""

import unittest

from src.waterplan.contradictions import contradicts, _position_from_text


class TestPositionFromText(unittest.TestCase):
    def test_recognizes_label_low(self):
        self.assertEqual(_position_from_text("The water stress level is Low."), 0)

    def test_recognizes_label_extremely_high(self):
        self.assertEqual(_position_from_text("Rated Extremely High risk."), 4)

    def test_recognizes_score_out_of_five(self):
        self.assertEqual(_position_from_text("WRI Aqueduct score: 4/5"), 3)

    def test_recognizes_decimal_score(self):
        self.assertEqual(_position_from_text("score 3.6/5"), 3)

    def test_score_rounds_to_nearest(self):
        # 2.4 rounds to 2 -> position 1
        self.assertEqual(_position_from_text("2.4/5"), 1)

    def test_no_recognizable_scale_returns_none(self):
        self.assertIsNone(_position_from_text("There was a protest over water rights."))

    def test_label_match_is_case_insensitive(self):
        self.assertEqual(_position_from_text("MEDIUM-HIGH water stress"), 2)

    def test_score_out_of_range_is_clamped(self):
        # 6/5 shouldn't happen in practice, but clamp defensively.
        self.assertEqual(_position_from_text("6/5"), 4)


class TestContradicts(unittest.TestCase):
    def test_same_position_is_not_contradictory(self):
        self.assertFalse(contradicts("Low water stress (1/5)", "Rated Low"))

    def test_adjacent_positions_not_contradictory(self):
        self.assertFalse(contradicts("Low water stress", "Low-Medium water stress"))

    def test_far_apart_positions_are_contradictory(self):
        self.assertTrue(contradicts("Low water stress", "Extremely High water stress"))

    def test_exactly_two_apart_is_contradictory(self):
        self.assertTrue(contradicts("1/5", "3/5"))

    def test_unrecognized_claim_returns_none(self):
        self.assertIsNone(contradicts("Low water stress", "A strike happened last year."))

    def test_both_unrecognized_returns_none(self):
        self.assertIsNone(contradicts("no scale here", "nor here"))


if __name__ == "__main__":
    unittest.main()
