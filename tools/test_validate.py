"""Tests for tools/validate.py. Run: python3 -m unittest discover -s tools"""
import copy
import json
import os
import unittest

from validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_PATH = os.path.join(ROOT, "data", "2026-11-27.json")


def load_sample():
    with open(SAMPLE_PATH, encoding="utf-8") as f:
        return json.load(f)


def with_change(data, fn):
    """Return a deep copy of data with fn applied, leaving the original untouched."""
    changed = copy.deepcopy(data)
    fn(changed)
    return changed


class ValidateTest(unittest.TestCase):
    def setUp(self):
        self.good = load_sample()
        self.name = "2026-11-27.json"

    def assert_error(self, data, fragment, name=None):
        errors = validate(data, name or self.name)
        self.assertTrue(any(fragment in e for e in errors),
                        f"expected an error containing {fragment!r}, got {errors}")

    def test_real_sample_has_no_errors(self):
        self.assertEqual(validate(self.good, self.name), [])

    def test_reports_missing_top_level_field(self):
        self.assert_error(with_change(self.good, lambda d: d.pop("summary_zh")), "summary_zh")

    def test_reports_non_object_root(self):
        self.assert_error([], "JSON object")

    def test_reports_bad_date_format(self):
        self.assert_error(with_change(self.good, lambda d: d.update(date="2026/11/27")), "date")

    def test_reports_date_not_matching_filename(self):
        self.assert_error(self.good, "filename", name="2026-11-28.json")

    def test_reports_missing_source_field(self):
        self.assert_error(with_change(self.good, lambda d: d["source"].pop("url")), "source.url")

    def test_reports_non_http_source_url(self):
        self.assert_error(with_change(self.good, lambda d: d["source"].update(url="javascript:alert(1)")),
                          "source.url")

    def test_reports_translation_length_mismatch(self):
        self.assert_error(with_change(self.good, lambda d: d["article_zh"].pop()), "article_zh")

    def test_reports_wrong_word_count(self):
        self.assert_error(with_change(self.good, lambda d: d["words"].pop()), "words")

    def test_reports_empty_word_field(self):
        self.assert_error(with_change(self.good, lambda d: d["words"][2].update(kk="")), "words[3].kk")

    def test_reports_empty_collocations(self):
        self.assert_error(with_change(self.good, lambda d: d["words"][0].update(collocations=[])),
                          "words[1].collocations")

    def test_reports_marker_number_out_of_range(self):
        self.assert_error(with_change(self.good, lambda d: d["article"].__setitem__(0, d["article"][0] + " {9|extra}")),
                          "9")

    def test_reports_malformed_marker(self):
        self.assert_error(with_change(self.good, lambda d: d["article"].__setitem__(0, d["article"][0] + " {3 lax}")),
                          "article[1]")

    def test_reports_word_never_marked_in_article(self):
        def drop_word_one(d):
            d["article"][0] = d["article"][0].replace("{1|spate}", "spate")
        self.assert_error(with_change(self.good, drop_word_one), "word 1")

    def test_reports_marker_in_translation(self):
        self.assert_error(with_change(self.good, lambda d: d["article_zh"].__setitem__(0, "{1|一連串}")),
                          "article_zh[1]")

    def test_reports_wrong_quiz_count(self):
        self.assert_error(with_change(self.good, lambda d: d["quiz"].pop()), "quiz")

    def test_reports_quiz_without_blank(self):
        self.assert_error(with_change(self.good, lambda d: d["quiz"][0].update(q="No blank here.")), "quiz[1]")

    def test_reports_quiz_answer_out_of_range(self):
        self.assert_error(with_change(self.good, lambda d: d["quiz"][4].update(a=0)), "quiz[5].a")

    def test_reports_quiz_answer_not_integer(self):
        self.assert_error(with_change(self.good, lambda d: d["quiz"][4].update(a="3")), "quiz[5].a")

    def test_reports_empty_quiz_form(self):
        self.assert_error(with_change(self.good, lambda d: d["quiz"][0].update(form="")), "quiz[1].form")

    def test_reports_leftover_placeholder_with_its_path(self):
        self.assert_error(with_change(self.good, lambda d: d["words"][1].update(related="TODO")),
                          "words[2].related")

    def test_does_not_mutate_input(self):
        snapshot = copy.deepcopy(self.good)
        validate(self.good, self.name)
        self.assertEqual(self.good, snapshot)


if __name__ == "__main__":
    unittest.main()
