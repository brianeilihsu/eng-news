# eng-news — Daily English Vocabulary

English | [繁體中文](README.zh-TW.md)

Every day, one English news story is rewritten as a short B2–C1 level article, paired with 8 advanced words that go beyond Taiwan's 7,000-word high school vocabulary list, and published as an interactive web page.

**Site:** https://eng-news.brianeilihsu.com/
**Daily pages:** `https://eng-news.brianeilihsu.com/YYYY-MM-DD/`

## Features

- Target words in the article show a popup with the Chinese meaning and a short definition on hover or tap
- 8 word cards: KK phonetics, part of speech, Chinese meaning, English definition, sentence from the article, common collocations, a real-world example sentence (with source), and synonyms / word forms
- Pronunciation for each word and read-aloud for the whole article, using the browser's built-in Web Speech API (`speechSynthesis`) — no audio files or API keys; voice quality depends on the device
- A collapsible Chinese translation under each paragraph
- 8-question fill-in-the-blank quiz

## Project structure

```
data/        Daily content (source data), one YYYY-MM-DD.json per day
tools/
  new_day.py         Creates a skeleton data/YYYY-MM-DD.json full of TODOs to fill in
  validate.py        Checks data/*.json (run automatically by build.py)
  build.py           Builds the site: data/*.json → docs/
  day.template.html  HTML template for a daily page
  static/            Copied into docs/ as-is
    assets/          base.css (shared), day.css, day.js (daily page behaviour)
  test_*.py          Tests: python3 -m unittest discover -s tools
  DAILY_TASK.md      Full instructions for the daily scheduled task
docs/        Generated site (served by GitHub Pages)
  index.html         Home page listing all days
  assets/            CSS/JS copied from tools/static/assets/
  YYYY-MM-DD/        Daily pages
  CNAME              Custom domain
```

Everything in `docs/` is generated — don't edit it by hand. Change content in `data/` or layout in `tools/`, then rebuild.

## Build locally

```bash
python3 tools/build.py
```

Only Python 3 is required; there are no other dependencies. The build validates every `data/*.json` first and stops without touching `docs/` if any file is invalid. CSS/JS URLs carry a `?v=` content hash, so browsers pick up changes right away. To preview locally:

```bash
python3 -m http.server -d docs 8000
# open http://localhost:8000/
```

## Data format

Main fields in `data/YYYY-MM-DD.json`:

| Field | Description |
|---|---|
| `date`, `date_zh`, `topic`, `slug` | Date, date in Chinese, topic, short English slug |
| `title` | Article title |
| `source` | Original news story (outlet, date, URL) |
| `article` | Array of paragraphs; target words are marked as `{number\|original text}`, e.g. `{5\|tampered with}` |
| `article_zh` | Chinese translation of each paragraph (same order and length as `article`), shown as a collapsible “中文翻譯” under each paragraph |
| `summary_zh` | Summary in Chinese |
| `words` | 8 words: `word`, `kk`, `pos`, `zh`, `def`, `sentence`, `collocations`, `example`, `example_src`, `related` |
| `quiz` | 8 questions: `q` (blank written as `___`), `a` (word number), `form` (the actual form when it differs from the base word) |

To add a day, run `python3 tools/new_day.py YYYY-MM-DD` (default: today in Taipei) to get a correctly shaped skeleton, replace every `TODO` and each quiz `"a": null`, then run `python3 tools/validate.py`. The validator reports anything still missing or malformed with its exact path, e.g. `words[3].kk`.

## Daily updates

Every day at 09:00 Taipei time, a Claude scheduled task follows [`tools/DAILY_TASK.md`](tools/DAILY_TASK.md):

1. Pick a story from the last 24 hours in a major English outlet (topic rotates by weekday)
2. Rewrite it as a 350–420 word article and choose 8 words beyond the 7,000-word list
3. Find a real example sentence online for each word and cite its source
4. Create the skeleton with `tools/new_day.py`, fill it in, then run `tools/validate.py` and `tools/build.py`
5. Check the page at desktop and mobile widths with Playwright
6. Commit and push to `main`; GitHub Pages deploys automatically

To change the daily workflow, edit `tools/DAILY_TASK.md` — the task reads the latest version from the repo on every run.

## Deployment

GitHub Pages: Settings → Pages → Deploy from a branch → `main` / `/docs`.
The custom domain `eng-news.brianeilihsu.com` is a Cloudflare DNS CNAME record pointing to `brianeilihsu.github.io` (DNS only, proxy off).

## About the content

Articles are rewritten from the original news, not reproduced; each quotes at most one sentence (under 15 words) from the source and links to the original story. Example sentences on the word cards are real, publicly available sentences, each with its source cited.
