#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish.py — 一鍵發布：重新產生 feed → 把音檔/封面/feed 上傳到主機。

支援兩種模式（由 publish.yaml 的 mode 決定）：
  - github：音檔上傳到 GitHub Releases，feed + 封面 commit 到 GitHub Pages（docs/）
  - rclone：音檔/封面/feed 全部上傳到 R2/S3（將來搬家用）

上傳後，各 Podcast 平台會定時來抓你的 feed，新集數自動上架。

用法：
  python scripts/publish.py              # 正式發布
  python scripts/publish.py --dry-run     # 只預覽會做哪些動作，不實際執行
"""

import os
import sys
import glob
import shutil
import subprocess

try:
    import yaml
except ImportError:
    sys.exit("缺少 PyYAML，請先執行：python -m pip install -r requirements.txt")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLISH_CFG = os.path.join(ROOT, "publish.yaml")
CONFIG_PATH = os.path.join(ROOT, "config.yaml")
AUDIO_DIR = os.path.join(ROOT, "audio")
DOCS_DIR = os.path.join(ROOT, "docs")
FEED = os.path.join(DOCS_DIR, "feed.xml")

AUDIO_EXTS = ("*.mp3", "*.m4a", "*.mp4", "*.aac", "*.wav", "*.flac", "*.ogg")


def load_yaml(path):
    if not os.path.exists(path):
        sys.exit(f"找不到 {os.path.basename(path)}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def run(cmd, dry, check=True, cwd=None):
    print("   $ " + " ".join(cmd))
    if dry:
        return 0
    rc = subprocess.run(cmd, cwd=cwd).returncode
    if check and rc != 0:
        sys.exit(f"指令失敗（return code {rc}）：{' '.join(cmd)}")
    return rc


def regenerate_feed():
    print("▶ 重新產生 feed")
    rc = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "generate_feed.py")]).returncode
    if rc != 0:
        sys.exit("feed 產生失敗，已中止發布。")


def audio_files():
    files = []
    for ext in AUDIO_EXTS:
        files += glob.glob(os.path.join(AUDIO_DIR, ext))
    return sorted(files)


# ---------------------------------------------------------------------------
# GitHub 模式
# ---------------------------------------------------------------------------
def publish_github(pub, dry):
    if not shutil.which("gh"):
        sys.exit("找不到 gh，請先安裝 GitHub CLI：brew install gh")

    gh = pub.get("github") or {}
    repo = gh.get("repo", "").strip()
    tag = gh.get("release_tag", "episodes").strip()
    if not repo:
        sys.exit("publish.yaml 的 github.repo 沒填（格式 owner/repo）")

    regenerate_feed()

    # 1) 確保 release 存在（存放音檔）
    print(f"\n▶ 1/3 確認 Releases「{tag}」存在")
    exists = subprocess.run(["gh", "release", "view", tag, "-R", repo],
                            capture_output=True).returncode == 0
    if not exists:
        run(["gh", "release", "create", tag, "-R", repo,
             "--title", "Episodes", "--notes", "Podcast 音檔存放區（由 publish.py 自動管理）"], dry)

    # 2) 上傳音檔
    files = audio_files()
    if not files:
        print("   （audio/ 沒有音檔，略過上傳）")
    else:
        print(f"\n▶ 2/3 上傳 {len(files)} 個音檔到 Releases")
        run(["gh", "release", "upload", tag, "-R", repo, "--clobber", *files], dry)

    # 3) commit + push feed/封面到 Pages
    print("\n▶ 3/3 發佈 feed + 封面到 GitHub Pages")
    run(["git", "-C", ROOT, "add", "docs"], dry)
    # 若沒變更就不 commit
    changed = subprocess.run(["git", "-C", ROOT, "diff", "--cached", "--quiet"]).returncode != 0
    if changed or dry:
        run(["git", "-C", ROOT, "commit", "-m", "Publish: 更新 feed 與封面"], dry, check=False)
        run(["git", "-C", ROOT, "push"], dry)
    else:
        print("   （feed 無變更，略過 commit）")


# ---------------------------------------------------------------------------
# rclone 模式（R2/S3，未來搬家用）
# ---------------------------------------------------------------------------
def publish_rclone(pub, dry):
    if not shutil.which("rclone"):
        sys.exit("找不到 rclone，請先安裝：brew install rclone")
    remote = pub.get("rclone_remote", "").strip()
    bucket = pub.get("bucket", "").strip()
    prefix = pub.get("remote_prefix", "").strip().strip("/")
    if not remote or not bucket:
        sys.exit("publish.yaml 缺少 rclone_remote 或 bucket")

    remotes = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True).stdout
    if f"{remote}:" not in remotes:
        sys.exit(f"rclone 還沒有名為「{remote}」的 remote，請先 rclone config。")

    base = f"{remote}:{bucket}" + (f"/{prefix}" if prefix else "")
    regenerate_feed()
    print("\n▶ 上傳音檔")
    cmd = ["rclone", "copy", AUDIO_DIR, f"{base}/audio/", "--progress"]
    for ext in AUDIO_EXTS:
        cmd += ["--include", ext]
    run(cmd, dry)
    print("\n▶ 上傳封面 + feed")
    run(["rclone", "copy", os.path.join(DOCS_DIR, "assets"), f"{base}/assets/", "--progress"], dry, check=False)
    run(["rclone", "copyto", FEED, f"{base}/feed.xml",
         "--header-upload", "Content-Type: application/rss+xml; charset=utf-8", "--progress"], dry)


def main():
    dry = "--dry-run" in sys.argv
    pub = load_yaml(PUBLISH_CFG)
    mode = pub.get("mode", "github").strip()

    if mode == "github":
        publish_github(pub, dry)
    elif mode == "rclone":
        publish_rclone(pub, dry)
    else:
        sys.exit(f"publish.yaml 的 mode 不認得：{mode}（要 github 或 rclone）")

    cfg = load_yaml(CONFIG_PATH)
    feed_url = f"{str(cfg.get('base_url','')).rstrip('/')}/feed.xml"
    print("\n" + ("（dry-run，未實際執行）" if dry else "✅ 發布完成！"))
    print(f"   你的 feed 公開網址：{feed_url}")
    print("   首次上架：把這個網址貼到各平台（見 README.md 的提交清單）。")
    print("   之後每出一集：丟音檔進 audio/、在 episodes.yaml 加一段、再跑一次本指令即可。")


if __name__ == "__main__":
    main()
