#!/usr/bin/env python3
"""Create a skeleton lesson file, data/YYYY-MM-DD.json, for the daily task to fill in.

Dates are prefilled; every other field holds TODO (or null for quiz answers), and
tools/validate.py rejects the file until all of them are replaced.
Usage: python3 tools/new_day.py [YYYY-MM-DD]   (default: today in Asia/Taipei)
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

from validate import PLACEHOLDER, QUIZ_COUNT, WORD_COUNT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
PARAGRAPH_SLOTS = 4  # typical length; add or remove paragraphs as needed, keeping article_zh in step
WEEKDAYS_ZH = "一二三四五六日"
TAIPEI = dt.timezone(dt.timedelta(hours=8))
T = PLACEHOLDER


def _word_slot(n: int) -> dict:
    return {
        "word": f"{T}: word {n} (base form)",
        "kk": f"{T}: KK phonetics, e.g. [spet]",
        "pos": f"{T}: n. / v. / adj. / phr. v.",
        "zh": f"{T}: Chinese meaning used in the article",
        "def": f"{T}: short English definition",
        "sentence": f"{T}: the article sentence containing the word",
        "collocations": [f"{T}: collocation 1", f"{T}: collocation 2"],
        "example": f"{T}: real sentence found online (≤15 words)",
        "example_src": f"{T}: outlet・YYYY-MM-DD",
        "related": f"{T}: synonyms / word forms",
    }


def skeleton(date: str) -> dict:
    """Return a new lesson dict for date with every content field set to a placeholder."""
    day = dt.date.fromisoformat(date)  # raises ValueError on a bad date
    return {
        "date": date,
        "date_zh": f"{day.year}年{day.month}月{day.day}日（{WEEKDAYS_ZH[day.weekday()]}）",
        "topic": f"{T}: topic in Chinese, e.g. 科技・資安",
        "slug": f"{T}: short-english-slug",
        "title": f"{T}: article title",
        "source": {
            "outlet": f"{T}: outlet",
            "headline": f"{T}: original headline",
            "author": f"{T}: author",
            "date": f"{T}: YYYY-MM-DD",
            "url": f"{T}: https://...",
        },
        "article": [f"{T}: paragraph {k}; mark target words as {{n|text as written}}"
                    for k in range(1, PARAGRAPH_SLOTS + 1)],
        "article_zh": [f"{T}: Traditional Chinese translation of paragraph {k} (plain text)"
                       for k in range(1, PARAGRAPH_SLOTS + 1)],
        "summary_zh": f"{T}: summary in Chinese",
        "words": [_word_slot(n) for n in range(1, WORD_COUNT + 1)],
        "quiz": [{"q": f"{T}: new sentence with one ___ blank", "a": None}
                 for _ in range(QUIZ_COUNT)],
    }


def create(date: str, data_dir: str = DATA_DIR) -> str:
    """Write the skeleton to data_dir/date.json and return its path; never overwrites."""
    content = json.dumps(skeleton(date), ensure_ascii=False, indent=2) + "\n"
    path = os.path.join(data_dir, f"{date}.json")
    with open(path, "x", encoding="utf-8") as f:  # "x" raises FileExistsError
        f.write(content)
    return path


def main(argv: list) -> int:
    date = argv[0] if argv else dt.datetime.now(TAIPEI).date().isoformat()
    try:
        path = create(date)
    except ValueError:
        print(f"invalid date {date!r}; use YYYY-MM-DD", file=sys.stderr)
        return 2
    except FileExistsError:
        print(f"{os.path.relpath(os.path.join(DATA_DIR, date + '.json'), ROOT)} already exists; not overwriting",
              file=sys.stderr)
        return 1
    print(f"created {os.path.relpath(path, ROOT)}; replace every {PLACEHOLDER} (and quiz \"a\": null), "
          f"then run python3 tools/validate.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
