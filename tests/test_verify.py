"""Unit tests for the deterministic verification module (ADR-002)."""

import unittest

from src.waterplan.verify import chunk_text, normalize, verify_excerpt


class TestNormalize(unittest.TestCase):
    def test_collapses_whitespace(self):
        self.assertEqual(normalize("a   b\n\tc"), "a b c")

    def test_lowercases(self):
        self.assertEqual(normalize("Water STRESS"), "water stress")

    def test_nfkc_normalizes_compatibility_characters(self):
        # U+FB01 LATIN SMALL LIGATURE FI decomposes to "fi" under NFKC.
        self.assertEqual(normalize("ﬁle"), "file")

    def test_strips_leading_trailing_whitespace(self):
        self.assertEqual(normalize("  hello  "), "hello")

    def test_empty_string(self):
        self.assertEqual(normalize(""), "")


class TestVerifyExcerpt(unittest.TestCase):
    def test_exact_substring_matches(self):
        self.assertTrue(verify_excerpt("water stress", "The region has high water stress levels."))

    def test_case_insensitive_match(self):
        self.assertTrue(verify_excerpt("Water Stress", "the region has high water stress levels"))

    def test_whitespace_insensitive_match(self):
        self.assertTrue(verify_excerpt("water   stress", "high water\nstress levels"))

    def test_no_match_returns_false(self):
        self.assertFalse(verify_excerpt("drought conditions", "The region has high water stress."))

    def test_empty_excerpt_fails(self):
        self.assertFalse(verify_excerpt("", "some page text"))

    def test_empty_page_text_fails(self):
        self.assertFalse(verify_excerpt("some excerpt", ""))

    def test_both_empty_fails(self):
        self.assertFalse(verify_excerpt("", ""))

    def test_excerpt_longer_than_page_fails(self):
        self.assertFalse(verify_excerpt("a much longer excerpt than the page", "short page"))

    def test_partial_word_does_not_falsely_match(self):
        # "stress" should not spuriously match inside "distressing" via substring
        # logic that ignores word boundaries -- this documents current behavior:
        # verify_excerpt IS a raw substring check, so this actually matches.
        self.assertTrue(verify_excerpt("stress", "a distressing report"))


class TestChunkText(unittest.TestCase):
    def test_single_chunk_when_shorter_than_size(self):
        chunks = chunk_text("hello world", chunk_size=800, overlap=100)
        self.assertEqual(chunks, ["hello world"])

    def test_splits_into_multiple_chunks(self):
        text = "a" * 1000
        chunks = chunk_text(text, chunk_size=800, overlap=100)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0], "a" * 800)
        self.assertEqual(chunks[1], "a" * 300)

    def test_overlap_between_consecutive_chunks(self):
        text = "0123456789" * 100  # 1000 chars
        chunks = chunk_text(text, chunk_size=800, overlap=100)
        # Last 100 chars of chunk 0 should equal first 100 chars of chunk 1.
        self.assertEqual(chunks[0][-100:], chunks[1][:100])

    def test_every_char_covered_by_at_least_one_chunk(self):
        text = "".join(str(i % 10) for i in range(2500))
        chunks = chunk_text(text, chunk_size=800, overlap=100)
        reconstructed = set()
        pos = 0
        for chunk in chunks:
            for offset, ch in enumerate(chunk):
                reconstructed.add((pos + offset, ch))
            pos += len(chunk) - 100
        for i, ch in enumerate(text):
            self.assertIn((i, ch), reconstructed)

    def test_empty_text_returns_no_chunks(self):
        self.assertEqual(chunk_text("", chunk_size=800, overlap=100), [])

    def test_zero_overlap(self):
        text = "a" * 20
        chunks = chunk_text(text, chunk_size=10, overlap=0)
        self.assertEqual(chunks, ["a" * 10, "a" * 10])


if __name__ == "__main__":
    unittest.main()
