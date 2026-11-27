"""Render a lesson (data/YYYY-MM-DD.json) into its daily page HTML.

All content is rendered here at build time, so pages are readable without JavaScript;
tools/static/assets/day.js only adds interaction (speech, word popover, quiz checking).
"""
from __future__ import annotations

import json
import re
from typing import Dict, List

from validate import BLANK, MARKER_RE

PLACEHOLDER_RE = re.compile(r"__([A-Z_]+)__")
_ESCAPES = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}


def esc(s: object) -> str:
    return re.sub(r'[&<>"]', lambda m: _ESCAPES[m.group()], str(s))


def fill(template: str, values: Dict[str, str]) -> str:
    """Replace each __NAME__ in one pass, so inserted text is never re-expanded."""
    return PLACEHOLDER_RE.sub(lambda m: values[m.group(1)], template)


def page_title(d: dict) -> str:
    m, dd = d["date"].split("-")[1:]
    return f"{int(m)}/{int(dd)} {d['title']}｜Daily Vocab"


def js_safe(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def mark(sentence: str, word: str) -> str:
    """Escape sentence and bold the first (possibly inflected) occurrence of word."""
    parts = [re.escape(p) for p in word.split()]
    pattern = r"\b(" + parts[0] + r"\w*" + "".join(r"\s+" + p for p in parts[1:]) + ")"
    return re.sub(pattern, r"<b>\1</b>", esc(sentence), count=1, flags=re.IGNORECASE | re.ASCII)


def _word_span(m: re.Match) -> str:
    i, text = m.group(1), m.group(2)
    return f'<span class="vw" tabindex="0" data-i="{i}">{text}<sup>{i}</sup></span>'


def render_article(d: dict) -> str:
    zh = d.get("article_zh") or []
    out = []
    for k, p in enumerate(d["article"]):
        out.append("<p>" + MARKER_RE.sub(_word_span, esc(p)) + "</p>")
        if k < len(zh) and zh[k]:
            out.append(f'<details class="tr"><summary>中文翻譯</summary><div class="tr-body">{esc(zh[k])}</div></details>')
    return "\n    ".join(out)


def render_source(d: dict) -> str:
    s = d["source"]
    return (f"原始新聞：{esc(s['outlet'])}〈{esc(s['headline'])}〉{esc(s['author'])}，{esc(s['date'])}"
            f'<br><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["url"])}</a>')


def _card(k: int, w: dict) -> str:
    word = esc(w["word"])
    return f'''<div class="card" id="w{k}">
      <div class="word"><span class="n">{k}</span><span class="w en">{word}</span>
        <button class="say" title="發音" aria-label="播放發音" data-say="{word}">🔊</button>
        <button class="say" title="慢速" aria-label="慢速發音" data-say="{word}" data-rate="0.55">🐢</button>
        <span class="r">{esc(w["kk"])}</span><span class="pos">{esc(w["pos"])}</span><span class="m">{esc(w["zh"])}</span></div>
      <div class="row"><span class="k">英文解釋</span><span class="en">{esc(w["def"])}</span></div>
      <div class="row"><span class="k">文章句</span><span class="en">{mark(w["sentence"], w["word"])}</span></div>
      <div class="row"><span class="k">常見搭配</span><span class="en">{" ／ ".join(esc(c) for c in w["collocations"])}</span></div>
      <div class="row"><span class="k">真實例句</span><span><span class="en">{mark(w["example"], w["word"])}</span><button class="say sm" aria-label="播放例句" data-say="{esc(w["example"])}">🔊</button><br><span class="src">出處：{esc(w["example_src"])}</span></span></div>
      <div class="row"><span class="k">近義・詞形</span><span class="en">{esc(w["related"])}</span></div>
    </div>'''


def render_cards(d: dict) -> str:
    return "\n    ".join(_card(k, w) for k, w in enumerate(d["words"], 1))


def _quiz_options(words: List[dict]) -> str:
    # fixed pseudo-shuffle so option order doesn't give away the answer order
    order = sorted(range(1, len(words) + 1), key=lambda i: (i * 7 + 3) % 11)
    return '<option value="">— 選 —</option>' + "".join(
        f'<option value="{i}">{esc(words[i - 1]["word"])}</option>' for i in order)


def render_quiz(d: dict) -> str:
    opts = _quiz_options(d["words"])
    return "\n      ".join(
        f'<li data-a="{q["a"]}" data-form="{esc(q.get("form") or d["words"][q["a"] - 1]["word"])}">'
        + esc(q["q"]).replace(BLANK, f'<select aria-label="第 {k} 題">{opts}</select>', 1)
        + '<span class="fb"></span></li>'
        for k, q in enumerate(d["quiz"], 1))


def render_day(template: str, d: dict, version: str) -> str:
    return fill(template, {
        "TITLE": esc(page_title(d)),
        "DESC": esc("今日單字：" + "、".join(w["word"] for w in d["words"])),
        "ASSET_V": version,
        "META": esc(f"{d['date_zh']}｜{d['topic']}｜改寫自 {d['source']['outlet']}"),
        "HEADING": esc(d["title"]),
        "ARTICLE": render_article(d),
        "SUMMARY": esc(d["summary_zh"]),
        "SOURCE": render_source(d),
        "CARDS": render_cards(d),
        "QUIZ": render_quiz(d),
        "DATA": js_safe(d),
    })
