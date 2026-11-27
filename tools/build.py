#!/usr/bin/env python3
"""Build the site: data/YYYY-MM-DD.json -> docs/YYYY-MM-DD/index.html, plus docs/index.html.
GitHub Pages serves the docs/ folder (Settings -> Pages -> main /docs).
Usage: python3 tools/build.py   (run from the repo root)
"""
import glob, html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
TPL = open(os.path.join(ROOT, "tools", "day.template.html"), encoding="utf-8").read()


def js_safe(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


days = []
for path in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
    d = json.load(open(path, encoding="utf-8"))
    out_dir = os.path.join(OUT, d["date"])
    os.makedirs(out_dir, exist_ok=True)
    page = (TPL.replace("__TITLE__", html.escape(f'{d["title"]}｜每日英文單字 {d["date"]}'))
               .replace("__DESC__", html.escape("今日單字：" + "、".join(w["word"] for w in d["words"])))
               .replace("__DATA__", js_safe(d)))
    open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(page)
    days.append(d)

days.sort(key=lambda d: d["date"], reverse=True)
items = "\n".join(
    f'''<a class="item" href="{d["date"]}/">
      <div class="d">{html.escape(d["date_zh"])}<span class="tp">{html.escape(d["topic"])}</span></div>
      <div class="t en">{html.escape(d["title"])}</div>
      <div class="ws en">{" ・ ".join(html.escape(w["word"]) for w in d["words"])}</div>
    </a>''' for d in days)

INDEX = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>每日英文單字</title>
<meta name="description" content="從每日英文新聞學 7000 單以外的單字">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&family=Noto+Serif:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root{{--main:#1E3A5F;--accent:#E07A3F;--soft:#F4F1EA;--line:#D9D3C7;--ink:#222;--mute:#6B6B6B;color-scheme:light}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:"Noto Sans TC","Noto Sans CJK TC","PingFang TC",sans-serif;color:var(--ink);background:#fff;line-height:1.6}}
  .en{{font-family:"Noto Serif","DejaVu Serif",Georgia,serif}}
  .topbar{{height:10px;background:var(--main);position:relative}}
  .topbar::after{{content:"";position:absolute;left:0;bottom:-3px;width:140px;height:3px;background:var(--accent)}}
  .wrap{{max-width:760px;margin:0 auto;padding:26px 16px 48px}}
  .kicker{{font-size:12px;letter-spacing:.15em;color:var(--accent);font-weight:700}}
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
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(INDEX)
print(f"built {len(days)} day page(s) + index.html in docs/")
