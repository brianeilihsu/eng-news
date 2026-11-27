# 每日英文單字 eng-news

每天一則英文新聞改寫成 B2–C1 程度的短文，搭配 8 個「7000 單以外」的進階單字，做成可互動的網頁。

**網站：** https://eng-news.brianeilihsu.com/
**單日頁面：** `https://eng-news.brianeilihsu.com/YYYY-MM-DD/`

## 頁面功能

- 文章中的目標單字可以滑過或點擊，跳出中文意思與說明
- 8 張單字卡：KK 音標、詞性、中文、英文解釋、文章句、常見搭配、真實例句（附出處）、近義詞／詞形變化
- 發音：單字與整篇文章朗讀，使用瀏覽器內建的 Web Speech API（`speechSynthesis`），不需音檔或 API key，聲音品質依裝置而定
- 8 題填空小測驗

## 專案結構

```
data/        每天的內容（原始資料），一天一個 YYYY-MM-DD.json
tools/
  build.py           產生網站：data/*.json → docs/
  day.template.html  單日頁面模板
  DAILY_TASK.md      每日排程的完整指示
docs/        build 產生的網站（GitHub Pages 從這裡部署）
  index.html         首頁，列出所有日期
  YYYY-MM-DD/        單日頁面
  CNAME              自訂網域
```

`docs/` 裡的檔案都是產生出來的，不要手動修改；要改內容就改 `data/`，要改版面就改 `tools/`，再重新 build。

## 本機 build

```bash
python3 tools/build.py
```

只需要 Python 3，沒有其他相依套件。在本機預覽：

```bash
python3 -m http.server -d docs 8000
# 打開 http://localhost:8000/
```

## 資料格式

`data/YYYY-MM-DD.json` 的主要欄位：

| 欄位 | 說明 |
|---|---|
| `date`, `date_zh`, `topic`, `slug` | 日期、中文日期、主題、英文代稱 |
| `title` | 文章標題 |
| `source` | 原始新聞（媒體、日期、網址） |
| `article` | 文章段落陣列；目標單字用 `{編號\|單字原文}` 標記，例如 `{5\|tampered with}` |
| `summary_zh` | 中文摘要 |
| `words` | 8 個單字：`word`, `kk`, `pos`, `zh`, `def`, `sentence`, `collocations`, `example`, `example_src`, `related` |
| `quiz` | 8 題填空：`q`（空格寫 `___`）、`a`（單字編號）、`form`（答案形態與原形不同時填實際形態） |

新增一天時，照既有 JSON 的格式寫即可。

## 每日自動更新

每天台北時間 08:13，Claude 的排程會照 [`tools/DAILY_TASK.md`](tools/DAILY_TASK.md) 執行：

1. 從主流英文媒體挑一則最近 24 小時的新聞（主題依星期輪替）
2. 改寫成 350–420 字的文章，選 8 個 7000 單以外的單字
3. 為每個單字找網路上真實存在的例句並標出處
4. 新增 `data/YYYY-MM-DD.json`，執行 `tools/build.py`
5. 用 Playwright 以桌機與手機寬度檢查頁面
6. commit 並 push 到 `main`，GitHub Pages 自動部署

要調整每日流程，直接修改 `tools/DAILY_TASK.md`，排程每次執行都會讀 repo 裡的最新版本。

## 部署

GitHub Pages：Settings → Pages → Deploy from a branch → `main` / `/docs`。
自訂網域 `eng-news.brianeilihsu.com` 由 Cloudflare DNS 設定 CNAME 指向 `brianeilihsu.github.io`（DNS only，不開 proxy）。

## 內容說明

文章為根據新聞內容的改寫，非原文轉載；每篇最多引用原文一句（15 字以內），並附原始新聞連結。單字卡的例句皆來自網路上公開的真實句子，並標註出處。
