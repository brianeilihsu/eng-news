"""Tests for tools/render.py. Run: python3 -m unittest discover -s tools"""
import copy
import json
import os
import unittest

from render import fill, mark, render_article, render_day, render_quiz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "data", "2026-11-27.json"), encoding="utf-8") as f:
    SAMPLE = json.load(f)


class MarkTest(unittest.TestCase):
    def test_bolds_inflected_form(self):
        self.assertEqual(mark("Systems were tampered with.", "tamper with"),
                         "Systems were <b>tampered with</b>.")

    def test_is_case_insensitive_and_only_marks_first(self):
        self.assertEqual(mark("Havoc and havoc.", "havoc"), "<b>Havoc</b> and havoc.")

    def test_escapes_html(self):
        self.assertEqual(mark("<i>lax</i> rules", "lax"), "&lt;i&gt;<b>lax</b>&lt;/i&gt; rules")

    def test_leaves_sentence_without_word_unchanged(self):
        self.assertEqual(mark("Nothing here.", "spate"), "Nothing here.")


class ArticleTest(unittest.TestCase):
    def test_turns_markers_into_word_spans(self):
        d = {"article": ["A {1|spate} of <b>news</b>."], "article_zh": ["一連串"]}
        out = render_article(d)
        self.assertIn('<span class="vw" tabindex="0" data-i="1">spate<sup>1</sup></span>', out)
        self.assertIn("&lt;b&gt;news&lt;/b&gt;", out)
        self.assertIn('<details class="tr"><summary>中文翻譯</summary><div class="tr-body">一連串</div></details>', out)

    def test_omits_translation_when_missing(self):
        out = render_article({"article": ["One.", "Two."], "article_zh": ["一"]})
        self.assertEqual(out.count("<details"), 1)


class QuizTest(unittest.TestCase):
    def test_replaces_blank_with_select_listing_every_word(self):
        out = render_quiz(SAMPLE)
        self.assertEqual(out.count("<select"), 8)
        self.assertEqual(out.count("<option"), 8 * 9)
        self.assertNotIn("___", out)

    def test_uses_form_when_given(self):
        d = copy.deepcopy(SAMPLE)
        d["quiz"][0]["form"] = "spates"
        self.assertIn('data-form="spates"', render_quiz(d))


class FillTest(unittest.TestCase):
    def test_does_not_expand_placeholders_inside_inserted_values(self):
        self.assertEqual(fill("<p>__A__</p><p>__B__</p>", {"A": "__B__", "B": "x"}),
                         "<p>__B__</p><p>x</p>")

    def test_rejects_unknown_placeholder(self):
        with self.assertRaises(KeyError):
            fill("__MISSING__", {})


class RenderDayTest(unittest.TestCase):
    def test_page_contains_content_without_running_js(self):
        with open(os.path.join(ROOT, "tools", "day.template.html"), encoding="utf-8") as f:
            page = render_day(f.read(), SAMPLE, "v1")
        self.assertIn(SAMPLE["title"], page)
        self.assertIn("perpetrator<sup>3</sup>", page)
        self.assertEqual(page.count('class="card"'), 8)
        self.assertNotRegex(page, r"__[A-Z_]+__")

    def test_does_not_mutate_input(self):
        snapshot = copy.deepcopy(SAMPLE)
        with open(os.path.join(ROOT, "tools", "day.template.html"), encoding="utf-8") as f:
            render_day(f.read(), SAMPLE, "v1")
        self.assertEqual(SAMPLE, snapshot)


if __name__ == "__main__":
    unittest.main()
