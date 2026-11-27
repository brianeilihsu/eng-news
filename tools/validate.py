"""Validate a daily lesson JSON (data/YYYY-MM-DD.json) before it is built.

validate(data, filename) returns a list of human-readable error strings; an empty
list means the lesson is valid. Usage: python3 tools/validate.py [data/*.json ...]
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from typing import Any, Callable, List

WORD_COUNT = 8
QUIZ_COUNT = 8
BLANK = "___"
PLACEHOLDER = "TODO"  # left in every field of a skeleton made by tools/new_day.py
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MARKER_RE = re.compile(r"\{(\d+)\|([^{}|]+)\}")

TOP_LEVEL_STRINGS = ("date", "date_zh", "topic", "slug", "title", "summary_zh")
SOURCE_FIELDS = ("outlet", "headline", "author", "date", "url")
WORD_STRINGS = ("word", "kk", "pos", "zh", "def", "sentence", "example", "example_src", "related")


def _is_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_text_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0 and all(_is_text(v) for v in value)


def _check_strings(obj: dict, fields: tuple, prefix: str) -> List[str]:
    return [f"{prefix}{f}: missing or empty" for f in fields if not _is_text(obj.get(f))]


def _check_header(d: dict, filename: str) -> List[str]:
    errors = _check_strings(d, TOP_LEVEL_STRINGS, "")
    date = d.get("date")
    if _is_text(date) and not DATE_RE.match(date):
        errors.append(f"date: {date!r} is not YYYY-MM-DD")
    expected = os.path.splitext(os.path.basename(filename))[0]
    if _is_text(date) and date != expected:
        errors.append(f"date: {date!r} does not match filename {expected!r}")
    return errors


def _check_source(d: dict) -> List[str]:
    source = d.get("source")
    if not isinstance(source, dict):
        return ["source: missing or not an object"]
    errors = _check_strings(source, SOURCE_FIELDS, "source.")
    url = source.get("url")
    if _is_text(url) and not re.match(r"^https?://", url):
        errors.append(f"source.url: {url!r} must start with http:// or https://")
    return errors


def _check_paragraph_markers(k: int, paragraph: str) -> List[str]:
    errors = [f"article[{k}]: marker {{{n}|...}} is outside 1–{WORD_COUNT}"
              for n, _ in MARKER_RE.findall(paragraph) if not 1 <= int(n) <= WORD_COUNT]
    leftover = MARKER_RE.sub("", paragraph)
    if "{" in leftover or "}" in leftover:
        errors.append(f"article[{k}]: malformed marker (use {{number|text}})")
    return errors


def _check_article(d: dict) -> List[str]:
    article = d.get("article")
    if not _is_text_list(article):
        return ["article: must be a non-empty list of paragraphs"]
    errors = [e for k, p in enumerate(article, 1) for e in _check_paragraph_markers(k, p)]
    marked = {int(n) for p in article for n, _ in MARKER_RE.findall(p)}
    errors += [f"article: word {i} is never marked as {{{i}|...}}"
               for i in range(1, WORD_COUNT + 1) if i not in marked]

    zh = d.get("article_zh")
    if not _is_text_list(zh):
        return errors + ["article_zh: must be a non-empty list of paragraphs"]
    if len(zh) != len(article):
        errors.append(f"article_zh: has {len(zh)} paragraphs but article has {len(article)}")
    errors += [f"article_zh[{k}]: must be plain text without {{n|...}} markers"
               for k, p in enumerate(zh, 1) if "{" in p or "}" in p]
    return errors


def _check_word(k: int, w: Any) -> List[str]:
    if not isinstance(w, dict):
        return [f"words[{k}]: not an object"]
    errors = _check_strings(w, WORD_STRINGS, f"words[{k}].")
    if not _is_text_list(w.get("collocations")):
        errors.append(f"words[{k}].collocations: must be a non-empty list of strings")
    return errors


def _check_quiz_item(k: int, q: Any) -> List[str]:
    if not isinstance(q, dict):
        return [f"quiz[{k}]: not an object"]
    errors = []
    text = q.get("q")
    if not _is_text(text) or text.count(BLANK) != 1:
        errors.append(f"quiz[{k}].q: must contain exactly one {BLANK}")
    a = q.get("a")
    if not isinstance(a, int) or isinstance(a, bool) or not 1 <= a <= WORD_COUNT:
        errors.append(f"quiz[{k}].a: must be an integer 1–{WORD_COUNT}, got {a!r}")
    if "form" in q and not _is_text(q["form"]):
        errors.append(f"quiz[{k}].form: if present, must be a non-empty string")
    return errors


def _check_list(d: dict, key: str, count: int, check_item: Callable[[int, Any], List[str]]) -> List[str]:
    items = d.get(key)
    if not isinstance(items, list) or len(items) != count:
        size = len(items) if isinstance(items, list) else "none"
        return [f"{key}: expected exactly {count} items, got {size}"]
    return [e for k, item in enumerate(items, 1) for e in check_item(k, item)]


def _find_placeholders(value: Any, path: str = "") -> List[str]:
    """Paths like words[2].related whose string still contains the TODO placeholder."""
    if isinstance(value, str):
        return [path] if PLACEHOLDER in value else []
    if isinstance(value, dict):
        return [p for k, v in value.items() for p in _find_placeholders(v, f"{path}.{k}" if path else k)]
    if isinstance(value, list):
        return [p for i, v in enumerate(value, 1) for p in _find_placeholders(v, f"{path}[{i}]")]
    return []


def validate(data: Any, filename: str) -> List[str]:
    """Return every problem found in one lesson; [] means it is valid. Never mutates data."""
    if not isinstance(data, dict):
        return ["root: must be a JSON object"]
    return ([f"{p}: still contains {PLACEHOLDER}, fill it in" for p in _find_placeholders(data)]
            + _check_header(data, filename)
            + _check_source(data)
            + _check_article(data)
            + _check_list(data, "words", WORD_COUNT, _check_word)
            + _check_list(data, "quiz", QUIZ_COUNT, _check_quiz_item))


def validate_file(path: str) -> List[str]:
    """Load and validate one file; JSON syntax errors are reported, not raised."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return [f"cannot read JSON: {e}"]
    return validate(data, path)


def main(paths: List[str]) -> int:
    failed = 0
    for path in paths:
        errors = validate_file(path)
        if errors:
            failed += 1
            print(f"✗ {path}", file=sys.stderr)
            for e in errors:
                print(f"    - {e}", file=sys.stderr)
    if failed:
        print(f"{failed} file(s) failed validation", file=sys.stderr)
        return 1
    print(f"✓ {len(paths)} file(s) valid")
    return 0


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main(sys.argv[1:] or sorted(glob.glob(os.path.join(root, "data", "*.json")))))
