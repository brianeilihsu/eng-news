"""Tests for tools/new_day.py. Run: python3 -m unittest discover -s tools"""
import os
import tempfile
import unittest

from new_day import create, skeleton
from validate import PLACEHOLDER, validate


class SkeletonTest(unittest.TestCase):
    def test_prefills_date_fields(self):
        s = skeleton("2026-11-30")
        self.assertEqual(s["date"], "2026-11-30")
        self.assertEqual(s["date_zh"], "2026年11月30日（一）")

    def test_has_eight_words_and_eight_quiz_items(self):
        s = skeleton("2026-11-30")
        self.assertEqual(len(s["words"]), 8)
        self.assertEqual(len(s["quiz"]), 8)

    def test_translation_slots_match_paragraph_slots(self):
        s = skeleton("2026-11-30")
        self.assertEqual(len(s["article"]), len(s["article_zh"]))

    def test_unfilled_skeleton_fails_validation_with_placeholder_errors(self):
        errors = validate(skeleton("2026-11-30"), "2026-11-30.json")
        self.assertTrue(any(PLACEHOLDER in e for e in errors), errors)
        self.assertTrue(any("quiz[1].a" in e for e in errors), errors)

    def test_rejects_bad_date(self):
        with self.assertRaises(ValueError):
            skeleton("2026-13-01")


class CreateTest(unittest.TestCase):
    def test_writes_file_named_after_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = create("2026-11-30", tmp)
            self.assertEqual(path, os.path.join(tmp, "2026-11-30.json"))
            self.assertTrue(os.path.exists(path))

    def test_refuses_to_overwrite_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            create("2026-11-30", tmp)
            with self.assertRaises(FileExistsError):
                create("2026-11-30", tmp)


if __name__ == "__main__":
    unittest.main()
