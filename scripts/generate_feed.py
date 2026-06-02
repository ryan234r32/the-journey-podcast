#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_feed.py — 從 config.yaml + episodes.yaml 產生合規的 Podcast RSS feed。

特色：
  - 自動用 ffprobe 偵測每集時長
  - 自動讀取音檔大小 (enclosure length，bytes，Apple 要求正確)
  - 每集自動產生「永久不變」的 GUID（依檔名決定，換主機也不會讓舊集數重複出現）
  - 完整 iTunes 標籤 + Podcasting 2.0 namespace
  - 產出前做合規檢查，缺什麼會清楚告訴你

用法：
  python scripts/generate_feed.py            # 產生 public/feed.xml
  python scripts/generate_feed.py --check     # 只檢查不產生
"""

import os
import sys
import uuid
import html
import re
import shutil
import subprocess
import datetime as dt
import xml.etree.ElementTree as ET

try:
    import yaml
except ImportError:
    sys.exit("缺少 PyYAML，請先執行：python -m pip install -r requirements.txt")

# --- 路徑設定 ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config.yaml")
EPISODES_PATH = os.path.join(ROOT, "episodes.yaml")
AUDIO_DIR = os.path.join(ROOT, "audio")
DOCS_DIR = os.path.join(ROOT, "docs")            # GitHub Pages 服務目錄（feed + 封面）
FEED_OUT = os.path.join(DOCS_DIR, "feed.xml")

# --- 命名空間 ---
NS = {
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "atom": "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "podcast": "https://podcastindex.org/namespace/1.0",
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

# 用於產生穩定 GUID 的固定 namespace（請勿更動，動了所有 GUID 會變）
GUID_NS = uuid.UUID("6f9b2c3a-7d41-4e2b-9c8a-1f0e5d6a7b8c")

# 台灣時區 +08:00
TZ_TW = dt.timezone(dt.timedelta(hours=8))

MIME = {
    ".mp3": "audio/mpeg",
    ".m4a": "audio/x-m4a",
    ".mp4": "audio/mp4",
    ".aac": "audio/aac",
    ".wav": "audio/wav",
    ".flac": "audio/flac",
    ".ogg": "audio/ogg",
}


def q(prefix, tag):
    """產生命名空間限定名，例如 q('itunes','author')。"""
    return f"{{{NS[prefix]}}}{tag}"


def load_yaml(path):
    if not os.path.exists(path):
        sys.exit(f"找不到設定檔：{path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def ffprobe_duration(path):
    """回傳音檔秒數 (int)，失敗回 None。"""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-of", "csv=p=0",
             "-show_entries", "format=duration", path],
            capture_output=True, text=True, check=True,
        )
        return int(round(float(out.stdout.strip())))
    except Exception:
        return None


def fmt_duration(seconds):
    if seconds is None:
        return None
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"


def parse_pubdate(value):
    """接受 'YYYY-MM-DD' 或 'YYYY-MM-DD HH:MM' (台灣時間)。"""
    s = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            d = dt.datetime.strptime(s, fmt)
            return d.replace(tzinfo=TZ_TW)
        except ValueError:
            continue
    return None


def rfc822(d):
    # 例：Sun, 01 Jun 2026 20:00:00 +0800
    return d.strftime("%a, %d %b %Y %H:%M:%S %z")


def stable_guid(filename):
    return f"urn:uuid:{uuid.uuid5(GUID_NS, filename)}"


def sub(parent, tag, text=None, **attrs):
    el = ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})
    if text is not None:
        el.text = str(text)
    return el


def text_to_html(text):
    """純文字（含換行/空行）→ HTML 段落，給 description / content:encoded，讓各平台正確換行。"""
    text = (text or "").strip()
    blocks = []
    for para in re.split(r"\n\s*\n", text):
        lines = [html.escape(ln.strip()) for ln in para.split("\n") if ln.strip()]
        if lines:
            blocks.append("<p>" + "<br />".join(lines) + "</p>")
    return "".join(blocks)


# ---------------------------------------------------------------------------
# 合規檢查
# ---------------------------------------------------------------------------
def validate(cfg, episodes):
    errors, warnings = [], []

    def need(key, val):
        if not val or str(val).strip() == "":
            errors.append(f"config.yaml 缺少必填欄位：{key}")

    need("title", cfg.get("title"))
    need("description", cfg.get("description"))
    need("author", cfg.get("author"))
    need("language", cfg.get("language"))
    need("category", cfg.get("category"))

    owner = cfg.get("owner") or {}
    if not owner.get("email"):
        errors.append("config.yaml 缺少 owner.email（平台驗證必須）")
    elif "example.com" in str(owner.get("email")):
        warnings.append("owner.email 仍是範例值 example.com — 上架前務必改成你真實收得到的信箱")

    base = str(cfg.get("base_url", ""))
    if not base or "example.com" in base:
        warnings.append("base_url 仍是範例值 — 決定主機/網域後要改成真實公開網址")

    cover = os.path.join(ROOT, cfg.get("cover_image", "assets/cover.jpg"))
    if not os.path.exists(cover):
        warnings.append(f"找不到封面圖：{cfg.get('cover_image')}（Apple 要求 1400~3000px 正方形）")

    if not episodes:
        errors.append("episodes.yaml 沒有任何集數")

    for i, ep in enumerate(episodes, 1):
        fn = ep.get("file")
        if not fn:
            errors.append(f"第 {i} 集缺少 file 欄位")
            continue
        if not os.path.exists(os.path.join(AUDIO_DIR, fn)):
            errors.append(f"找不到音檔：audio/{fn}")
        if not ep.get("title"):
            errors.append(f"音檔 {fn} 缺少 title")
        if not parse_pubdate(ep.get("pub_date", "")):
            errors.append(f"音檔 {fn} 的 pub_date 格式錯誤（要 YYYY-MM-DD 或 YYYY-MM-DD HH:MM）")

    return errors, warnings


# ---------------------------------------------------------------------------
# 產生 feed
# ---------------------------------------------------------------------------
def build_feed(cfg, episodes):
    base = str(cfg.get("base_url", "")).rstrip("/")
    audio_base = str(cfg.get("audio_base_url", "")).rstrip("/")
    feed_url = f"{base}/feed.xml"
    cover_name = os.path.basename(cfg.get("cover_image", "assets/cover.jpg"))
    cover_url = f"{base}/assets/{cover_name}"
    website = cfg.get("website") or base
    author = cfg.get("author", "")
    owner = cfg.get("owner") or {}
    explicit_show = "true" if cfg.get("explicit") else "false"
    copyright_ = cfg.get("copyright") or f"© {dt.datetime.now(TZ_TW).year} {author}"

    rss = ET.Element("rss", {"version": "2.0"})
    # itunes / atom / content 命名空間會在使用到時由 ElementTree 自動宣告，
    # 不可在此重複手動宣告（否則 <rss> 會出現重複 xmlns 屬性，導致不合法 XML）。
    channel = sub(rss, "channel")

    cdata_map = {}
    def cdata(parent, tag, raw):
        el = ET.SubElement(parent, tag)
        token = f"@@CDATA{len(cdata_map)}@@"
        cdata_map[token] = text_to_html(raw)
        el.text = token
        return el

    sub(channel, "title", cfg.get("title"))
    sub(channel, "link", website)
    sub(channel, "language", cfg.get("language"))
    cdata(channel, "description", cfg.get("description"))
    sub(channel, "copyright", copyright_)
    sub(channel, "generator", "podcast-static-publisher")
    sub(channel, "lastBuildDate", rfc822(dt.datetime.now(TZ_TW)))

    # atom:link rel=self（RSS 規範要求）
    sub(channel, q("atom", "link"), rel="self", type="application/rss+xml", href=feed_url)

    # iTunes 標籤
    sub(channel, q("itunes", "author"), author)
    sub(channel, q("itunes", "summary"), cfg.get("description"))
    sub(channel, q("itunes", "type"), cfg.get("podcast_type", "episodic"))
    sub(channel, q("itunes", "explicit"), explicit_show)
    sub(channel, q("itunes", "image"), href=cover_url)

    own = sub(channel, q("itunes", "owner"))
    sub(own, q("itunes", "name"), owner.get("name", author))
    sub(own, q("itunes", "email"), owner.get("email", ""))

    # iTunes 分類要的是 text 屬性，不是元素內文（寫錯 Apple 會退件）
    cat = ET.SubElement(channel, q("itunes", "category"), {"text": str(cfg.get("category"))})
    if cfg.get("subcategory"):
        ET.SubElement(cat, q("itunes", "category"), {"text": str(cfg.get("subcategory"))})

    # 標準 RSS image
    img = sub(channel, "image")
    sub(img, "url", cover_url)
    sub(img, "title", cfg.get("title"))
    sub(img, "link", website)

    # --- 每一集 ---
    for ep in episodes:
        fn = ep["file"]
        path = os.path.join(AUDIO_DIR, fn)
        size = os.path.getsize(path)
        ext = os.path.splitext(fn)[1].lower()
        mime = MIME.get(ext, "audio/mpeg")
        dur = ffprobe_duration(path)
        pub = parse_pubdate(ep.get("pub_date"))
        guid = ep.get("guid") or stable_guid(fn)
        audio_url = f"{audio_base}/{fn}" if audio_base else f"{base}/audio/{fn}"
        ep_explicit = "true" if ep.get("explicit", cfg.get("explicit")) else "false"

        item = sub(channel, "item")
        sub(item, "title", ep.get("title"))
        sub(item, "link", audio_url)
        cdata(item, "description", ep.get("description", ""))
        cdata(item, q("content", "encoded"), ep.get("description", ""))
        sub(item, "enclosure", url=audio_url, length=size, type=mime)
        sub(item, "guid", guid, isPermaLink="false")
        if pub:
            sub(item, "pubDate", rfc822(pub))
        if dur:
            sub(item, q("itunes", "duration"), fmt_duration(dur))
        sub(item, q("itunes", "explicit"), ep_explicit)
        sub(item, q("itunes", "image"), href=cover_url)
        sub(item, q("itunes", "episodeType"), "full")
        if ep.get("episode_number"):
            sub(item, q("itunes", "episode"), ep["episode_number"])
        if ep.get("season"):
            sub(item, q("itunes", "season"), ep["season"])

    return rss, cdata_map


def main():
    check_only = "--check" in sys.argv

    cfg = load_yaml(CONFIG_PATH)
    eps_doc = load_yaml(EPISODES_PATH)
    episodes = eps_doc.get("episodes") or []

    errors, warnings = validate(cfg, episodes)

    for w in warnings:
        print(f"  ⚠️  {w}")
    if errors:
        print("\n❌ 發現問題，無法產生 feed：")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)

    if check_only:
        print("\n✅ 檢查通過，可以產生 feed。")
        return

    rss, cdata_map = build_feed(cfg, episodes)
    ET.indent(rss, space="  ")
    xml_str = ET.tostring(rss, encoding="unicode")
    for token, html_block in cdata_map.items():
        xml_str = xml_str.replace(token, f"<![CDATA[{html_block}]]>")
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(FEED_OUT, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(xml_str + "\n")

    # 把封面複製進 docs/assets/，讓 GitHub Pages 一起服務
    cover_src = os.path.join(ROOT, cfg.get("cover_image", "assets/cover.jpg"))
    if os.path.exists(cover_src):
        dst_dir = os.path.join(DOCS_DIR, "assets")
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(cover_src, os.path.join(dst_dir, os.path.basename(cover_src)))

    n = len(episodes)
    print(f"\n✅ 已產生 feed：{os.path.relpath(FEED_OUT, ROOT)}（{n} 集）")
    feed_url = f"{str(cfg.get('base_url','')).rstrip('/')}/feed.xml"
    print(f"   發布後的 feed 公開網址會是：{feed_url}")
    print(f"   下一步：python scripts/publish.py  把音檔與 feed 上傳到主機")


if __name__ == "__main__":
    main()
