#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
weekly_report.py — 產生「在路上 The Journey」每週各平台聽眾週報，並寄到你的 Email。

重點是「各平台有多少人在聽/看」，不是下載量。各平台 API 現實：
  - YouTube：訂閱數、觀看數是公開的 → 自動爬取（含每週成長）✅
  - Apple / Spotify / KKBOX：刻意不開放 podcast 數據 API，數字只在各自登入後台
        → 週報放「一鍵直達後台」連結，你 2 分鐘自己讀數字 ✅
  - OP3 下載：只能看到部分 RSS App 的下載（Spotify/YouTube 站內播放抓不到），
        所以降為次要的小註腳，不當主指標。

用法：
  python scripts/weekly_report.py                # 產生週報並寄出
  python scripts/weekly_report.py --no-send      # 只產生 HTML、不寄信（預覽）

資料來源設定見 config.yaml 的 platforms: 區塊；寄信設定見 .env。
"""

import os
import re
import sys
import json
import html
import subprocess
import datetime as dt
import urllib.parse
import urllib.request

try:
    import yaml
except ImportError:
    sys.exit("缺少 PyYAML，請先執行：python -m pip install -r requirements.txt")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config.yaml")
EPISODES_PATH = os.path.join(ROOT, "episodes.yaml")
REPORTS_DIR = os.path.join(ROOT, "reports")
STATE_PATH = os.path.join(REPORTS_DIR, "state.json")   # 存歷史快照，算每週成長
SEND_SCRIPT = os.path.join(ROOT, "scripts", "send_report.py")

TZ_TW = dt.timezone(dt.timedelta(hours=8))
OP3_API = "https://op3.dev/api/1"
DEFAULT_OP3_TOKEN = "preview07ce"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36"


# ---------------------------------------------------------------------------
# 基礎工具
# ---------------------------------------------------------------------------
def load_yaml(path):
    if not os.path.exists(path):
        sys.exit(f"找不到設定檔：{path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_env(path):
    env = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def fetch(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def parse_count(s):
    """'11' '1.2萬' '3.4K' '12,345' '33次' → int。失敗回 None。"""
    if s is None:
        return None
    s = s.strip().replace(",", "")
    m = re.search(r"([\d\.]+)\s*([萬億KMB]?)", s)
    if not m:
        return None
    num = float(m.group(1))
    mult = {"": 1, "K": 1e3, "M": 1e6, "B": 1e9, "萬": 1e4, "億": 1e8}[m.group(2)]
    return int(round(num * mult))


def fmt(n):
    return "—" if n is None else f"{n:,}"


# ---------------------------------------------------------------------------
# YouTube 公開數據爬取
# ---------------------------------------------------------------------------
def fetch_youtube(channel_id):
    """爬頻道頁，回傳 {subs, views, videos}。任何欄位抓不到就 None。"""
    if not channel_id:
        return None
    try:
        h = fetch(f"https://www.youtube.com/channel/{channel_id}",
                  headers={"User-Agent": UA, "Accept-Language": "zh-TW"})
    except Exception as e:
        print(f"  ⚠️  YouTube 爬取失敗：{e}", file=sys.stderr)
        return None

    def grab(pats):
        for p in pats:
            m = re.search(p, h)
            if m:
                return m.group(1)
        return None

    subs = grab([r"([\d,\.]+\s*[萬億KMB]?)\s*(?:位訂閱者|subscribers)"])
    views = grab([r"觀看次數：([\d,\.]+\s*[萬億]?)\s*次",
                  r"([\d,\.]+\s*[萬億KMB]?)\s*(?:views|次觀看)"])
    videos = grab([r"([\d,\.]+)\s*(?:部影片|個影片|videos)"])
    return {"subs": parse_count(subs), "views": parse_count(views),
            "videos": parse_count(videos)}


# ---------------------------------------------------------------------------
# OP3 下載（次要指標）
# ---------------------------------------------------------------------------
def op3_prefix(cfg):
    base = str(cfg.get("audio_base_url") or cfg.get("base_url") or "").rstrip("/")
    return "https://op3.dev/e/" + re.sub(r"^https?://", "", base) if base else None


def op3_week_downloads(cfg, token, start, end):
    prefix = op3_prefix(cfg)
    if not prefix:
        return 0
    params = {
        "url": prefix,
        "start": start.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "end": end.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "limit": "1000", "format": "json",
    }
    try:
        data = json.loads(fetch(f"{OP3_API}/hits?" + urllib.parse.urlencode(params),
                                headers={"Authorization": f"Bearer {token}"}))
    except Exception:
        return 0
    seen = set()
    for h in data.get("rows", []):
        if h.get("method", "GET").upper() != "GET":
            continue
        key = (h.get("hashedIpAddress"), (h.get("url") or "").split("?")[0], (h.get("time") or "")[:10])
        seen.add(key)
    return len(seen)


# ---------------------------------------------------------------------------
# 歷史快照（算每週成長）
# ---------------------------------------------------------------------------
def load_state():
    if os.path.exists(STATE_PATH):
        try:
            return json.load(open(STATE_PATH, encoding="utf-8"))
        except Exception:
            pass
    return {"snapshots": []}


def save_state(state):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    json.dump(state, open(STATE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def delta_badge(cur, prev):
    """回傳本週成長的 HTML 小標。"""
    if cur is None:
        return '<span style="color:#b4aaa0;">—</span>'
    if prev is None:
        return '<span style="color:#8a8178;font-size:12px;">首次記錄</span>'
    d = cur - prev
    if d == 0:
        return '<span style="color:#8a8178;font-size:13px;">本週持平</span>'
    color = "#16a34a" if d > 0 else "#dc2626"
    sign = "+" if d > 0 else ""
    return f'<span style="color:{color};font-weight:700;font-size:14px;">本週 {sign}{d:,}</span>'


# ---------------------------------------------------------------------------
# HTML 組裝
# ---------------------------------------------------------------------------
def build_html(c):
    p = c["platforms"]
    yt = c["youtube"] or {}
    prev = c["prev_youtube"] or {}

    # YouTube 大卡（真實自動數字）
    yt_card = f"""
    <div style="background:#fff;border:1px solid #ece7df;border-radius:16px;padding:20px;margin-bottom:12px;">
      <div style="display:flex;align-items:center;margin-bottom:14px;">
        <span style="font-size:18px;font-weight:700;color:#2b2620;">▶ YouTube</span>
        <span style="margin-left:auto;font-size:12px;color:#16a34a;background:#eaf7ee;padding:3px 9px;border-radius:999px;">自動更新</span>
      </div>
      <table style="width:100%;border-collapse:collapse;"><tr>
        <td style="width:50%;vertical-align:top;padding-right:8px;">
          <div style="font-size:12px;color:#8a8178;">訂閱人數</div>
          <div style="font-size:32px;font-weight:800;color:#2b2620;line-height:1.15;">{fmt(yt.get('subs'))}</div>
          <div style="margin-top:2px;">{delta_badge(yt.get('subs'), prev.get('subs'))}</div>
        </td>
        <td style="width:50%;vertical-align:top;padding-left:8px;border-left:1px solid #f0ece4;">
          <div style="font-size:12px;color:#8a8178;">總觀看次數</div>
          <div style="font-size:32px;font-weight:800;color:#2b2620;line-height:1.15;">{fmt(yt.get('views'))}</div>
          <div style="margin-top:2px;">{delta_badge(yt.get('views'), prev.get('views'))}</div>
        </td>
      </tr></table>
      <a href="{p['youtube_url']}" style="display:inline-block;margin-top:14px;font-size:13px;color:#8a8178;text-decoration:none;">前往頻道 →</a>
    </div>"""

    # Apple / Spotify / KKBOX：一鍵直達後台
    def link_card(name, mark, desc, url, btn):
        return f"""
      <div style="background:#fff;border:1px solid #ece7df;border-radius:14px;padding:16px 18px;margin-bottom:10px;">
        <div style="display:flex;align-items:center;">
          <div>
            <div style="font-size:16px;font-weight:700;color:#2b2620;">{mark} {name}</div>
            <div style="font-size:12px;color:#8a8178;margin-top:2px;">{desc}</div>
          </div>
          <a href="{url}" style="margin-left:auto;white-space:nowrap;background:#2b2620;color:#f6f1e8;font-size:13px;
             text-decoration:none;padding:9px 16px;border-radius:10px;font-weight:600;">{btn} →</a>
        </div>
      </div>"""

    apple = link_card("Apple Podcasts", "", "聽眾數 / 追蹤數 / 消費率在後台",
                      "https://podcastsconnect.apple.com/analytics", "看後台")
    spotify = link_card("Spotify", "", "聽眾數 / 追蹤數 / 串流數在後台",
                        "https://creators.spotify.com/", "看後台")
    kkbox = link_card("KKBOX", "", "於公開頁查看（KKBOX 無創作者數據後台）",
                      p.get("kkbox_url", "#"), "看頻道")

    coaching = "".join(
        f'<li style="margin:0 0 10px;line-height:1.65;color:#3a342c;">{t}</li>' for t in c["coaching"]
    )

    op3_note = (
        f'RSS 直接下載（OP3 偵測，<b>不含</b> Spotify / YouTube 站內播放）：'
        f'本週 <b>{c["op3_week"]}</b> 次'
    )

    period = f'{c["start"].strftime("%Y/%m/%d")} – {(c["end"] - dt.timedelta(days=1)).strftime("%m/%d")}'

    return f"""<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#faf7f1;font-family:'Noto Sans TC',-apple-system,'PingFang TC','Microsoft JhengHei',sans-serif;color:#2b2620;">
<div style="max-width:600px;margin:0 auto;padding:28px 18px 40px;">

  <div style="text-align:center;margin-bottom:8px;">
    <div style="font-size:13px;color:#a89f95;letter-spacing:3px;">在路上 THE JOURNEY</div>
    <h1 style="font-size:23px;margin:6px 0 2px;color:#2b2620;">各平台聽眾週報</h1>
    <div style="font-size:13px;color:#8a8178;">{period}（台灣時間）</div>
  </div>

  <div style="background:#2b2620;color:#f6f1e8;border-radius:16px;padding:18px 20px;margin:18px 0;font-size:15px;line-height:1.6;">
    {c['headline']}
  </div>

  <h2 style="font-size:14px;color:#8a8178;letter-spacing:1px;margin:24px 0 10px;">📺 自動追蹤的平台</h2>
  {yt_card}

  <h2 style="font-size:14px;color:#8a8178;letter-spacing:1px;margin:24px 0 10px;">🔑 一鍵看後台（沒有公開 API，數字只在這些後台）</h2>
  {apple}{spotify}{kkbox}

  <h2 style="font-size:14px;color:#8a8178;letter-spacing:1px;margin:24px 0 8px;">🧭 本週下一步行動</h2>
  <ol style="margin:0;padding-left:20px;font-size:14px;">{coaching}</ol>

  <h2 style="font-size:14px;color:#8a8178;letter-spacing:1px;margin:26px 0 8px;">✅ 進後台時順手看這 3 個（最能反映內容好不好）</h2>
  <div style="background:#fff;border:1px solid #ece7df;border-radius:14px;padding:14px 18px;">
    <ul style="margin:0;padding-left:18px;font-size:14px;color:#3a342c;">
      <li style="margin:0 0 9px;line-height:1.6;"><b>消費率 / 完成率</b> — 目標 75%+。低於 70% 就把開場剪短、鉤子提到前 30 秒。</li>
      <li style="margin:0 0 9px;line-height:1.6;"><b>追蹤者淨增</b> — 上榜與被推薦的領先指標。每集結尾都要有一句「按追蹤」。</li>
      <li style="margin:0 0 9px;line-height:1.6;"><b>流失點</b>（Spotify）— 聽眾在第幾分鐘離開，那段就是下次要改的地方。</li>
    </ul>
  </div>

  <div style="text-align:center;margin-top:26px;font-size:12px;color:#b4aaa0;line-height:1.7;">
    {op3_note}<br>
    YouTube 數字自動爬取 · Apple/Spotify/KKBOX 無公開 API 故附後台連結<br>
    每週一早上自動寄出 · 想調整內容回覆即可
  </div>

</div></body></html>"""


# ---------------------------------------------------------------------------
# 教練建議
# ---------------------------------------------------------------------------
def build_coaching(yt, prev, total_eps):
    tips = []
    subs = (yt or {}).get("subs")
    psubs = (prev or {}).get("subs")
    if total_eps <= 1:
        tips.append("目前只有 1 集 — 對剛起步的頻道，<b>把 EP02 的發布日定下來</b>比任何數字都重要。穩定更新是平台演算法與聽眾建立信任的基礎。")
    if subs is not None and psubs is not None:
        d = subs - psubs
        if d > 0:
            tips.append(f"YouTube 本週 <b>+{d} 訂閱</b> — 回想這週做了什麼（哪支影片、哪則貼文帶來的），把有效動作固定下來。")
        elif d == 0:
            tips.append("YouTube 訂閱本週持平 — 試著在影片結尾加明確「訂閱」CTA，並把節目精華剪成 Shorts 導流。")
    elif subs is not None:
        tips.append(f"已開始記錄 YouTube（目前 {subs} 訂閱）— 下週起就能看到每週成長數字。")
    tips.append("Apple / Spotify 的聽眾數點上方按鈕花 2 分鐘讀一下 — 這兩家通常是 podcast 最大的聽眾來源，但只能登入後台看。")
    return tips


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    no_send = "--no-send" in sys.argv

    cfg = load_yaml(CONFIG_PATH)
    episodes = (load_yaml(EPISODES_PATH).get("episodes") or [])
    env = load_env(os.path.join(ROOT, ".env"))
    token = env.get("OP3_TOKEN") or DEFAULT_OP3_TOKEN
    platforms = cfg.get("platforms") or {}

    now = dt.datetime.now(TZ_TW)
    this_monday = (now - dt.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    end = this_monday
    start = end - dt.timedelta(days=7)

    # YouTube 現況 + 上週快照（算成長）。比較對象要排除「本週自己」的快照，
    # 否則同一週跑兩次會把成長誤算成持平。
    youtube = fetch_youtube(platforms.get("youtube_channel_id"))
    state = load_state()
    this_date = end.strftime("%Y-%m-%d")
    prev_snaps = [s for s in state["snapshots"] if s.get("date") != this_date]
    prev_snap = prev_snaps[-1] if prev_snaps else None
    prev_youtube = (prev_snap or {}).get("youtube")

    op3_week = op3_week_downloads(cfg, token, start, end)

    coaching = build_coaching(youtube, prev_youtube, len(episodes))

    if youtube and youtube.get("subs") is not None:
        grow = ""
        if prev_youtube and prev_youtube.get("subs") is not None:
            d = youtube["subs"] - prev_youtube["subs"]
            grow = f"（本週 {'+' if d >= 0 else ''}{d}）" if d else "（本週持平）"
        headline = f"YouTube 目前 {youtube['subs']} 訂閱、{youtube.get('views','?')} 次觀看{grow}。Apple / Spotify 的聽眾數請點下方按鈕進後台看 — 那才是 podcast 的主場。"
    else:
        headline = "本週各平台現況如下。YouTube 數字自動更新，Apple / Spotify / KKBOX 請點按鈕進後台查看聽眾數。"

    ctx = {
        "start": start, "end": end,
        "platforms": platforms,
        "youtube": youtube, "prev_youtube": prev_youtube,
        "op3_week": op3_week,
        "headline": headline,
        "coaching": coaching,
    }
    html_out = build_html(ctx)

    # 存本週快照（供下週算成長）；同一週只保留一筆，重跑就覆蓋
    state["snapshots"] = [s for s in state["snapshots"] if s.get("date") != this_date]
    state["snapshots"].append({
        "date": this_date,
        "youtube": youtube,
        "op3_week": op3_week,
    })
    state["snapshots"] = state["snapshots"][-60:]  # 最多留 60 週
    save_state(state)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    out_path = os.path.join(REPORTS_DIR, f"weekly-{end.strftime('%Y%m%d')}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    ys = youtube.get("subs") if youtube else None
    print(f"✅ 已產生週報：{os.path.relpath(out_path, ROOT)}（YouTube {ys} 訂閱 / OP3 下載 {op3_week}）")

    if no_send:
        print("   (--no-send 模式，未寄出。用瀏覽器打開上面的檔案即可預覽)")
        return

    subject = f"📺 在路上 The Journey 各平台週報 · {start.strftime('%m/%d')}–{(end - dt.timedelta(days=1)).strftime('%m/%d')}"
    res = subprocess.run([sys.executable, SEND_SCRIPT, subject, out_path])
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
