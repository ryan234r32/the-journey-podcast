# Podcast 自動上架工具 — 進度

## 方案決策
- 主機方案：**① 靜態檔 + 自寫 RSS 腳本**（近乎零成本、最自動化、feed 完全自有）
- 目標平台：Apple Podcasts、Spotify、YouTube Music、KKBOX、Amazon、iHeart
- 音檔主機：Cloudflare R2（10GB 免費 + 零出站流量費），透過 rclone 上傳

## 已完成 ✅
- [x] 專案骨架（config.yaml / episodes.yaml / publish.yaml / 目錄 / .gitignore）
- [x] `scripts/generate_feed.py`：完整 iTunes + Podcasting 2.0 標籤；ffprobe 自動算時長、
      os.stat 自動算 enclosure 大小、依檔名產生永久 GUID、產出前合規檢查
- [x] `scripts/publish.py`：rclone 一鍵上傳音檔/封面/feed，host-agnostic，含 dry-run 與引導
- [x] Python venv + PyYAML、requirements.txt
- [x] README：設定流程 + R2 步驟 + 6 平台中文提交清單 + 注意事項
- [x] 驗證：用測試音檔產出 feed，xmllint 通過、無重複 xmlns、時長/大小自動帶入
- [x] 修掉重複 xmlns 屬性的 bug（手動宣告 + ET 自動宣告衝突）

## 等使用者提供 / 決定 ⏳
- [ ] 真實 `owner.email`（平台驗證用）
- [ ] 真實音檔放進 audio/、封面換成正式版、episodes.yaml 填正式文案
- [ ] Cloudflare R2 帳號 + bucket +（建議）自訂網域 → 決定 base_url
- [ ] rclone config 設定 R2 remote
- [ ] 首次到 6 平台各提交一次 feed 網址

## Review
整套已可端到端運作，唯一缺的是使用者的真實素材與 R2 帳號設定。
測試用的 audio/EP01.mp3 與 assets/cover.jpg 為佔位檔，使用者用正式檔覆蓋即可。
