#!/usr/bin/env python3
"""Build the site: data/YYYY-MM-DD.json -> docs/YYYY-MM-DD/index.html, plus docs/index.html.
GitHub Pages serves the docs/ folder (Settings -> Pages -> main /docs).
Every data file is validated first; if any is invalid, nothing is written.
Usage: python3 tools/build.py   (run from the repo root)
"""
from __future__ import annotations

import glob
import hashlib
import html
import json
import os
import shutil
import sys
from typing import List

from render import render_day
from validate import validate_file

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
STATIC = os.path.join(ROOT, "tools", "static")
TEMPLATE = os.path.join(ROOT, "tools", "day.template.html")
ASSET_HASH_LEN = 10


def asset_version() -> str:
    """Short hash of tools/static/assets/*, appended as ?v= so browsers refetch after changes."""
    h = hashlib.sha256()
    for path in sorted(glob.glob(os.path.join(STATIC, "assets", "*"))):
        h.update(os.path.basename(path).encode())
        with open(path, "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:ASSET_HASH_LEN]


def load_lessons(paths: List[str]) -> List[dict]:
    """Validate every file and exit with a report if any is invalid."""
    report = [(p, validate_file(p)) for p in paths]
    bad = [(p, errs) for p, errs in report if errs]
    if bad:
        for path, errs in bad:
            print(f"✗ {os.path.relpath(path, ROOT)}", file=sys.stderr)
            for e in errs:
                print(f"    - {e}", file=sys.stderr)
        sys.exit(f"build aborted: {len(bad)} invalid data file(s); docs/ was not changed")
    lessons = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            lessons.append(json.load(f))
    return lessons


def render_index(days: List[dict], version: str) -> str:
    items = "\n".join(
        f'''<a class="item" href="{d["date"]}/">
      <div class="d">{html.escape(d["date_zh"])}<span class="tp">{html.escape(d["topic"])}</span></div>
      <div class="t en">{html.escape(d["title"])}</div>
      <div class="ws en">{" ・ ".join(html.escape(w["word"]) for w in d["words"])}</div>
    </a>''' for d in sorted(days, key=lambda d: d["date"], reverse=True))
    return f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Daily Vocab｜每日英文單字</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="description" content="從每日英文新聞學 7000 單以外的單字">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&family=Noto+Serif:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/base.css?v={version}">
<style>
  .wrap{{padding-top:26px}}
  h1{{font-size:30px;color:var(--main);margin:4px 0 6px}}
  .sub{{color:var(--mute);font-size:14px;margin-bottom:22px}}
  .item{{display:block;text-decoration:none;color:inherit;border:1px solid var(--line);border-left:6px solid var(--main);border-radius:6px;padding:12px 16px;margin-bottom:12px;transition:border-color .15s,background .15s}}
  .item:hover{{border-color:var(--accent);background:#FFFBF7}}
  .d{{font-size:13px;color:var(--mute)}}
  .tp{{margin-left:8px;font-size:12px;background:var(--soft);color:var(--main);border-radius:4px;padding:0 6px}}
  .t{{font-size:20px;font-weight:700;color:var(--main);margin:2px 0 4px}}
  .ws{{font-size:14px;color:var(--accent)}}
</style>
</head>
<body>
<div class="topbar"></div>
<main class="wrap">
  <div class="kicker">DAILY VOCAB</div>
  <h1>每日英文單字</h1>
  <div class="sub">每天一則英文新聞改寫，8 個 7000 單以外的單字。</div>
  {items}
</main>
</body>
</html>
'''


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main() -> None:
    days = load_lessons(sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))))
    with open(TEMPLATE, encoding="utf-8") as f:
        template = f.read()
    version = asset_version()

    # static files (favicon, assets/*.css|js) -> docs/
    shutil.copytree(STATIC, OUT, dirs_exist_ok=True)
    for d in days:
        write(os.path.join(OUT, d["date"], "index.html"), render_day(template, d, version))
    write(os.path.join(OUT, "index.html"), render_index(days, version))
    print(f"built {len(days)} day page(s) + index.html in docs/ (assets v={version})")


if __name__ == "__main__":
    main()
