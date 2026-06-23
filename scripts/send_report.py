#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
send_report.py — 透過 Gmail SMTP 寄出 HTML 週報。

用法：
  python scripts/send_report.py "<主旨>" <html檔路徑>
  cat report.html | python scripts/send_report.py "<主旨>"

設定讀自專案根目錄的 .env：SMTP_USER / SMTP_PASS / REPORT_TO
（.env 已被 .gitignore 排除，不會進 git。）
"""

import os
import sys
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path):
    env = {}
    if not os.path.exists(path):
        sys.exit(f"找不到 {path}（請建立 .env）")
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def main():
    env = load_env(os.path.join(ROOT, ".env"))
    user = env.get("SMTP_USER")
    pw = env.get("SMTP_PASS")
    to = env.get("REPORT_TO", user)
    if not user or not pw:
        sys.exit(".env 缺少 SMTP_USER 或 SMTP_PASS")

    subject = sys.argv[1] if len(sys.argv) > 1 else "在路上 The Journey 週報"
    if len(sys.argv) > 2:
        html = open(sys.argv[2], encoding="utf-8").read()
    else:
        html = sys.stdin.read()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"在路上 The Journey <{user}>"
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls(context=ctx)
        s.login(user, pw)
        s.sendmail(user, [to], msg.as_string())
    print(f"✅ 已寄出 → {to}")


if __name__ == "__main__":
    main()
