# 🎙️ Podcast 靜態發布工具

把音檔自動發布到 **Apple Podcasts、Spotify、YouTube Music、KKBOX、Amazon Music、iHeartRadio** 等所有平台。

## 運作原理（重要觀念）

Podcast 平台**不存你的音檔**。它們吃的是一條 **RSS feed 網址**。

```
音檔 + metadata  →  產生 feed.xml  →  上傳到你的主機  →  各平台定時來抓
                                                          (首次需各提交一次)
```

- **首次**：把 feed 網址貼到每個平台一次（要收驗證信）。
- **之後**：每出一集，丟音檔 + 跑一行指令，**所有平台自動更新**。

---

## 🚀 快速開始（首次設定）

### 1. 填節目資訊
編輯 [config.yaml](config.yaml)：節目名稱、簡介、作者、分類，以及 ⚠️ **`owner.email`（必須是你收得到信的信箱，平台靠它驗證）**。

### 2. 放素材
- 音檔放進 [audio/](audio/)（例如 `EP01.mp3`）
- 封面放 [assets/cover.jpg](assets/)（正方形 1400~3000px）
- 在 [episodes.yaml](episodes.yaml) 為每集填 `file / title / description / pub_date`
  （檔案大小、時長、GUID 都會自動算，不用管）

### 3. 產生 feed
```bash
.venv/bin/python scripts/generate_feed.py
```
> 想先檢查有沒有缺東西：加 `--check`

### 4. 設定主機（Cloudflare R2，免出流量費）
見下方「[設定 Cloudflare R2](#-設定-cloudflare-r2)」。設好後把 [publish.yaml](publish.yaml) 與 `config.yaml` 的 `base_url` 填好。

### 5. 發布
```bash
.venv/bin/python scripts/publish.py          # 正式上傳
.venv/bin/python scripts/publish.py --dry-run # 先預覽
```

### 6. 首次提交到各平台
見下方「[各平台首次提交清單](#-各平台首次提交清單)」。

---

## 🔁 日常：每出一集只要 3 步

1. 音檔丟進 `audio/`
2. `episodes.yaml` 最上面加一段（4 個欄位）
3. `.venv/bin/python scripts/publish.py`

完成。所有平台幾小時內自動出現新集數。

---

## ☁️ 設定 Cloudflare R2

R2 的好處：**儲存 10GB 免費、流量出站完全不收費**（Podcast 最怕的就是流量費）。

1. 註冊 [Cloudflare](https://dash.cloudflare.com) → 左側 **R2** → 建立一個 bucket（例如 `podcast-media`）。
2. bucket → **Settings** → 開啟 **Public access**，或綁一個**自訂網域**（建議，例如 `media.yourdomain.com`）。
   - 拿到的公開網址就是你 `config.yaml` 的 `base_url`。
   - feed 最終網址 = `base_url/feed.xml`
3. R2 → **Manage API Tokens** → 建一組 Access Key（給 rclone 用）。
4. 設定 rclone：
   ```bash
   rclone config
   # n) 新增 → 名稱填 r2 → 類型選 "Amazon S3" → provider 選 "Cloudflare"
   # 貼上 Access Key / Secret，endpoint 填 R2 給你的 S3 API 網址
   ```
5. 把 [publish.yaml](publish.yaml) 的 `rclone_remote`、`bucket` 填好。
6. 測試：`rclone lsd r2:` 能列出 bucket 就成功。

> 沒有網域也行：R2 的 `*.r2.dev` 公開網址可直接當 `base_url`（適合先試水溫）。

---

## 📋 各平台首次提交清單

> 全部都是「貼同一條 feed 網址 → 收驗證信 → 等上線」。驗證信都寄到 `config.yaml` 裡的 `owner.email`。

| 平台 | 提交入口 | 重點 | 上線時間 |
|------|---------|------|:---:|
| **Apple Podcasts** | [podcastsconnect.apple.com](https://podcastsconnect.apple.com) | 用 Apple ID 登入 → 貼 feed → 驗證 → 送審 | 數小時~1天 |
| **Spotify** | [creators.spotify.com](https://creators.spotify.com) | 「Add your podcast」貼 feed → 驗證信 | 幾分鐘 |
| **YouTube Music** | [studio.youtube.com](https://studio.youtube.com) | Podcasts → 用 RSS 建立。⚠️ **此功能按地區開放，台灣帳號可能無此選項**；沒有就先跳過或改用上傳影片版 | 視帳號 |
| **KKBOX** | [podcast.kkbox.com/podcasters](https://podcast.kkbox.com/podcasters) | 台灣原生支援。KK ID 登入 → 貼 feed → 選最多 3 分類 → 驗證信。⚠️ **feed 網址一旦提交不能改，只能重新提交，所以網址要一次定好** | 24 小時內 |
| **Amazon Music / Audible** | [podcasters.amazon.com](https://podcasters.amazon.com) | Amazon 帳號 → 貼 feed → 確認 | 數小時 |
| **iHeartRadio** | [iheart.com/podcasters](https://www.iheart.com/podcasters/) | 貼 feed → 驗證 | 數天 |

### 🆓 不用提交、自動出現的 App
上了 **Apple Podcasts** 後，以下會自動同步、**你什麼都不用做**：
**Overcast、Pocket Casts、Castro、Podcast Addict、AntennaPod、Podverse…**（幾十個 App）

---

## ⚠️ 重要注意事項

- **`owner.email` 一定要填真的** — 6 個平台全靠它寄驗證碼。
- **音檔檔名定了就別改** — GUID 是依檔名產生的，改名會讓該集在聽眾的 App 裡「重複出現一集新的」。要改內容請換掉檔案、保留檔名。
- **`base_url` 一旦上架就別改** — KKBOX 等平台不能改 feed 網址。建議用自訂網域（即使將來換主機，網域指向新位置即可，feed 網址不變）。
- **封面規格** — 正方形、1400×1400 ~ 3000×3000、JPG/PNG、RGB。太小 Apple 會退件。

---

## 📁 檔案結構

```
Podcast/
├── config.yaml          # 節目層級設定（填一次）
├── episodes.yaml        # 每集 metadata（每集加一段）
├── publish.yaml         # 上傳目的地（rclone remote + bucket）
├── audio/               # 你的來源音檔
├── assets/cover.jpg     # 封面
├── public/feed.xml      # ← 產出的 RSS（提交給平台的就是它）
├── scripts/
│   ├── generate_feed.py # 產生 feed
│   └── publish.py       # 上傳音檔 + feed
└── .venv/               # Python 環境
```
