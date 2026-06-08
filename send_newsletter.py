#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

today = datetime.now().strftime("%Y/%m/%d")

html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>在路上 The Journey 每週週報</title>
</head>
<body style="margin:0;padding:0;background-color:#f5f5f0;font-family:'Helvetica Neue',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f5f0;">
  <tr><td align="center" style="padding:32px 16px;">
    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

      <!-- HEADER -->
      <tr><td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 60%,#0f3460 100%);border-radius:16px 16px 0 0;padding:40px 36px 32px;text-align:center;">
        <p style="margin:0 0 6px;font-size:13px;letter-spacing:3px;color:#a0c4ff;text-transform:uppercase;">Weekly Newsletter</p>
        <h1 style="margin:0 0 8px;font-size:28px;font-weight:700;color:#ffffff;letter-spacing:1px;">在路上 The Journey</h1>
        <p style="margin:0 0 20px;font-size:14px;color:#c0d8ff;">主持：Johnny & Ryan</p>
        <div style="display:inline-block;background:rgba(255,255,255,0.12);border-radius:20px;padding:6px 20px;">
          <span style="font-size:13px;color:#e0eeff;">每週週報 · {today}</span>
        </div>
      </td></tr>

      <!-- SECTION 1：平台狀態 -->
      <tr><td style="background:#ffffff;padding:32px 36px 24px;">
        <h2 style="margin:0 0 20px;font-size:18px;font-weight:700;color:#1a1a2e;border-left:4px solid #0f3460;padding-left:12px;">① 平台上架狀態</h2>
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="padding:4px 0;">
              <table width="100%" cellpadding="10" cellspacing="0" style="background:#f8faff;border-radius:10px;margin-bottom:8px;">
                <tr>
                  <td style="width:32px;font-size:18px;">🎵</td>
                  <td style="font-size:14px;font-weight:600;color:#1a1a2e;">Apple Podcasts</td>
                  <td align="right"><span style="background:#d4edda;color:#155724;font-size:12px;padding:3px 10px;border-radius:12px;font-weight:600;">✓ 上架中</span></td>
                </tr>
              </table>
            </td>
          </tr>
          <tr><td style="padding:4px 0;">
            <table width="100%" cellpadding="10" cellspacing="0" style="background:#f8faff;border-radius:10px;margin-bottom:8px;">
              <tr>
                <td style="width:32px;font-size:18px;">💚</td>
                <td style="font-size:14px;font-weight:600;color:#1a1a2e;">Spotify</td>
                <td align="right"><span style="background:#d4edda;color:#155724;font-size:12px;padding:3px 10px;border-radius:12px;font-weight:600;">✓ 上架中</span></td>
              </tr>
            </table>
          </td></tr>
          <tr><td style="padding:4px 0;">
            <table width="100%" cellpadding="10" cellspacing="0" style="background:#f8faff;border-radius:10px;margin-bottom:8px;">
              <tr>
                <td style="width:32px;font-size:18px;">🎶</td>
                <td style="font-size:14px;font-weight:600;color:#1a1a2e;">KKBOX</td>
                <td align="right"><span style="background:#d4edda;color:#155724;font-size:12px;padding:3px 10px;border-radius:12px;font-weight:600;">✓ 上架中</span></td>
              </tr>
            </table>
          </td></tr>
          <tr><td style="padding:4px 0;">
            <table width="100%" cellpadding="10" cellspacing="0" style="background:#f8faff;border-radius:10px;margin-bottom:8px;">
              <tr>
                <td style="width:32px;font-size:18px;">▶️</td>
                <td style="font-size:14px;font-weight:600;color:#1a1a2e;">YouTube / YouTube Music</td>
                <td align="right"><span style="background:#d4edda;color:#155724;font-size:12px;padding:3px 10px;border-radius:12px;font-weight:600;">✓ 上架中</span></td>
              </tr>
            </table>
          </td></tr>
          <tr><td style="padding:4px 0;">
            <table width="100%" cellpadding="10" cellspacing="0" style="background:#f8faff;border-radius:10px;margin-bottom:8px;">
              <tr>
                <td style="width:32px;font-size:18px;">🎙️</td>
                <td style="font-size:14px;font-weight:600;color:#1a1a2e;">Amazon Music</td>
                <td align="right"><span style="background:#d4edda;color:#155724;font-size:12px;padding:3px 10px;border-radius:12px;font-weight:600;">✓ 上架中</span></td>
              </tr>
            </table>
          </td></tr>
        </table>
        <div style="margin-top:16px;background:#eef3ff;border-radius:10px;padding:12px 16px;text-align:center;">
          <span style="font-size:13px;color:#0f3460;">收聽全平台落地頁：</span>
          <a href="https://the-journey-jnr.vercel.app" style="color:#0f3460;font-weight:700;font-size:13px;">the-journey-jnr.vercel.app</a>
        </div>
      </td></tr>

      <!-- DIVIDER -->
      <tr><td style="background:#ffffff;padding:0 36px;"><hr style="border:none;border-top:1px solid #eef0f5;margin:0;"></td></tr>

      <!-- SECTION 2：數據指標 -->
      <tr><td style="background:#ffffff;padding:24px 36px;">
        <h2 style="margin:0 0 20px;font-size:18px;font-weight:700;color:#1a1a2e;border-left:4px solid #0f3460;padding-left:12px;">② 數據指標（OP3 下載統計）</h2>

        <!-- Show info card -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#eef3ff,#f0f8ff);border-radius:12px;margin-bottom:16px;">
          <tr><td style="padding:20px 24px;">
            <p style="margin:0 0 4px;font-size:12px;color:#6b7a99;letter-spacing:1px;text-transform:uppercase;">已連結 OP3 分析平台</p>
            <p style="margin:0 0 12px;font-size:16px;font-weight:700;color:#1a1a2e;">在路上 The Journey</p>
            <p style="margin:0;font-size:12px;color:#6b7a99;">Show UUID：db2884bf-ddc3-4f27-b1b6-c0409df16eb4</p>
          </td></tr>
        </table>

        <!-- Episode stats -->
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="width:48%;padding-right:8px;">
              <div style="background:#fff8f0;border:1px solid #ffd9a8;border-radius:12px;padding:18px;text-align:center;">
                <p style="margin:0 0 6px;font-size:28px;font-weight:800;color:#e07b00;">1</p>
                <p style="margin:0;font-size:12px;color:#6b4e00;">RSS 已發布集數</p>
              </div>
            </td>
            <td style="width:4%;"></td>
            <td style="width:48%;padding-left:8px;">
              <div style="background:#f0fff8;border:1px solid #a8e6c8;border-radius:12px;padding:18px;text-align:center;">
                <p style="margin:0 0 6px;font-size:20px;font-weight:800;color:#006b3f;">累積中</p>
                <p style="margin:0;font-size:12px;color:#004d2c;">本週下載數</p>
              </div>
            </td>
          </tr>
        </table>

        <!-- EP01 detail -->
        <div style="margin-top:16px;background:#f9f9fb;border-radius:12px;padding:16px 20px;">
          <p style="margin:0 0 6px;font-size:12px;color:#6b7a99;letter-spacing:1px;">最新集數</p>
          <p style="margin:0 0 4px;font-size:14px;font-weight:700;color:#1a1a2e;">EP01｜差點死在北大西洋：6000公里海上漂流</p>
          <p style="margin:0;font-size:12px;color:#6b7a99;">2026/01/06 發布 · 嘉賓：陳懷璞</p>
        </div>

        <div style="margin-top:12px;background:#fff3cd;border-left:3px solid #ffc107;border-radius:0 8px 8px 0;padding:10px 14px;">
          <p style="margin:0;font-size:12px;color:#856404;">📊 OP3 下載數字目前顯示為「資料累積中」，節目上線不久，建議下週再確認數據。OP3 統計頁：<a href="https://op3.dev/show/db2884bfddc34f27b1b6c0409df16eb4" style="color:#856404;">op3.dev/show/...</a></p>
        </div>
      </td></tr>

      <!-- DIVIDER -->
      <tr><td style="background:#ffffff;padding:0 36px;"><hr style="border:none;border-top:1px solid #eef0f5;margin:0;"></td></tr>

      <!-- SECTION 3：本週訪談對象推薦 -->
      <tr><td style="background:#ffffff;padding:24px 36px;">
        <h2 style="margin:0 0 6px;font-size:18px;font-weight:700;color:#1a1a2e;border-left:4px solid #0f3460;padding-left:12px;">③ 本週訪談對象推薦</h2>
        <p style="margin:0 0 20px;font-size:12px;color:#999;padding-left:16px;">⚠️ AI 推薦，聯絡方式請自行查證核實</p>

        <!-- Guest 1 -->
        <div style="background:#ffffff;border:1px solid #e0e6f5;border-radius:12px;padding:20px;margin-bottom:14px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
          <div style="display:flex;align-items:flex-start;">
            <div>
              <div style="margin-bottom:10px;">
                <span style="background:#e8f0ff;color:#1a4fc4;font-size:11px;padding:3px 10px;border-radius:12px;font-weight:600;margin-right:6px;">向內探索</span>
                <span style="background:#fff0e8;color:#c45a1a;font-size:11px;padding:3px 10px;border-radius:12px;font-weight:600;">瑜珈療癒 · 創業</span>
              </div>
              <p style="margin:0 0 6px;font-size:16px;font-weight:800;color:#1a1a2e;">蔡士傑 Janus Tsai</p>
              <p style="margin:0 0 10px;font-size:13px;color:#555;line-height:1.6;">台灣第一位 C-IAYT 認證瑜珈療癒師、Yoga Mindon 創辦人，擁有心理學學士及運動休閒管理碩士，專研「身體記憶創傷」與療癒。跨越學術、創業、身心靈三域，完美契合「向內探索」單元的飲食・睡眠・身心平衡主題，並有創業故事可分享。</p>
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding-right:8px;"><a href="https://www.instagram.com/janus.tsai/" style="background:#f0f4ff;color:#0f3460;font-size:12px;padding:5px 12px;border-radius:8px;text-decoration:none;font-weight:600;">IG @janus.tsai</a></td>
                  <td style="padding-right:8px;"><a href="https://www.facebook.com/IAYTJT/" style="background:#f0f4ff;color:#0f3460;font-size:12px;padding:5px 12px;border-radius:8px;text-decoration:none;font-weight:600;">FB 粉專</a></td>
                </tr>
              </table>
            </div>
          </div>
        </div>

        <!-- Guest 2 -->
        <div style="background:#ffffff;border:1px solid #e0e6f5;border-radius:12px;padding:20px;margin-bottom:14px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
          <div style="margin-bottom:10px;">
            <span style="background:#ffeaea;color:#c41a1a;font-size:11px;padding:3px 10px;border-radius:12px;font-weight:600;margin-right:6px;">向外實踐</span>
            <span style="background:#e8fff0;color:#1a7a3c;font-size:11px;padding:3px 10px;border-radius:12px;font-weight:600;">冒險 · 生死 · 極限</span>
          </div>
          <p style="margin:0 0 6px;font-size:16px;font-weight:800;color:#1a1a2e;">陳彥博 Tommy Chen</p>
          <p style="margin:0 0 10px;font-size:13px;color:#555;line-height:1.6;">台灣極地超馬運動員，首位完成全球七大洲八大站超馬的亞洲人，曾罹患咽喉癌後復出奪冠。2025年以7天23小時完成北極圈617公里長征（亞洲首人）。抗癌、死亡邊緣、夢想追求的真實旅程，與「向外實踐」的生死與生命可能性單元高度契合。</p>
          <table cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding-right:8px;"><a href="https://www.instagram.com/tommychen1986/" style="background:#f0f4ff;color:#0f3460;font-size:12px;padding:5px 12px;border-radius:8px;text-decoration:none;font-weight:600;">IG @tommychen1986</a></td>
              <td style="padding-right:8px;"><span style="background:#f0f4ff;color:#0f3460;font-size:12px;padding:5px 12px;border-radius:8px;font-weight:600;">worldextreme.sport@gmail.com</span></td>
            </tr>
          </table>
        </div>

        <!-- Guest 3 -->
        <div style="background:#ffffff;border:1px solid #e0e6f5;border-radius:12px;padding:20px;margin-bottom:14px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
          <div style="margin-bottom:10px;">
            <span style="background:#e8f0ff;color:#1a4fc4;font-size:11px;padding:3px 10px;border-radius:12px;font-weight:600;margin-right:6px;">向內探索</span>
            <span style="background:#f5e8ff;color:#7a1ac4;font-size:11px;padding:3px 10px;border-radius:12px;font-weight:600;">正念 · 冥想 · 推廣</span>
          </div>
          <p style="margin:0 0 6px;font-size:16px;font-weight:800;color:#1a1a2e;">陳德中</p>
          <p style="margin:0 0 10px;font-size:13px;color:#555;line-height:1.6;">台灣正念工坊執行長，長期推廣正念減壓（MBSR）於台灣企業與學校，著有多本正念相關書籍。以「正念冥想如何在高壓創業環境中救了我」作為切入角度，完美串聯「向內探索」冥想與身心平衡主題，並能分享商業應用的實際案例。</p>
          <table cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding-right:8px;"><span style="background:#f0f4ff;color:#0f3460;font-size:12px;padding:5px 12px;border-radius:8px;font-weight:600;">台灣正念工坊官網查詢</span></td>
            </tr>
          </table>
        </div>

        <!-- Guest 4 -->
        <div style="background:#ffffff;border:1px solid #e0e6f5;border-radius:12px;padding:20px;margin-bottom:4px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
          <div style="margin-bottom:10px;">
            <span style="background:#e8f0ff;color:#1a4fc4;font-size:11px;padding:3px 10px;border-radius:12px;font-weight:600;margin-right:6px;">向外實踐</span>
            <span style="background:#fff0e8;color:#c45a1a;font-size:11px;padding:3px 10px;border-radius:12px;font-weight:600;">創業 · Wellness 品牌</span>
          </div>
          <p style="margin:0 0 6px;font-size:16px;font-weight:800;color:#1a1a2e;">許米恩 Kai Chi</p>
          <p style="margin:0 0 10px;font-size:13px;color:#555;line-height:1.6;">健康保養品牌「可妮絲」創辦人，2013年起投身健康美容創業。以女性創業者身分，分享在建立品牌過程中如何兼顧身心健康。兼具「向外實踐」創業精神與「向內探索」wellness 生活方式，適合聊女性創業者的身心平衡之道。</p>
          <table cellpadding="0" cellspacing="0">
            <tr>
              <td><a href="https://www.instagram.com/kai_chi77/" style="background:#f0f4ff;color:#0f3460;font-size:12px;padding:5px 12px;border-radius:8px;text-decoration:none;font-weight:600;">IG @kai_chi77</a></td>
            </tr>
          </table>
        </div>
      </td></tr>

      <!-- DIVIDER -->
      <tr><td style="background:#ffffff;padding:0 36px;"><hr style="border:none;border-top:1px solid #eef0f5;margin:0;"></td></tr>

      <!-- SECTION 4：行動建議 -->
      <tr><td style="background:#ffffff;padding:24px 36px 32px;">
        <h2 style="margin:0 0 20px;font-size:18px;font-weight:700;color:#1a1a2e;border-left:4px solid #0f3460;padding-left:12px;">④ 本週行動建議</h2>

        <div style="background:#f8faff;border-radius:12px;padding:20px 24px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr><td style="padding:8px 0;border-bottom:1px solid #e8ecf5;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="width:28px;font-size:16px;vertical-align:top;padding-top:1px;">📧</td>
                  <td><p style="margin:0;font-size:13px;color:#1a1a2e;line-height:1.6;"><strong>聯絡陳彥博</strong> — 發信至 worldextreme.sport@gmail.com，提案討論北極長征故事，趁話題熱度最高時接洽。</p></td>
                </tr>
              </table>
            </td></tr>
            <tr><td style="padding:8px 0;border-bottom:1px solid #e8ecf5;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="width:28px;font-size:16px;vertical-align:top;padding-top:1px;">📩</td>
                  <td><p style="margin:0;font-size:13px;color:#1a1a2e;line-height:1.6;"><strong>私訊蔡士傑 IG @janus.tsai</strong> — 以「身體如何記住創傷」為話題切入，強調節目「向內探索」單元的受眾定位。</p></td>
                </tr>
              </table>
            </td></tr>
            <tr><td style="padding:8px 0;border-bottom:1px solid #e8ecf5;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="width:28px;font-size:16px;vertical-align:top;padding-top:1px;">📊</td>
                  <td><p style="margin:0;font-size:13px;color:#1a1a2e;line-height:1.6;"><strong>確認 OP3 數據</strong> — 下週確認 <a href="https://op3.dev/show/db2884bfddc34f27b1b6c0409df16eb4" style="color:#0f3460;">OP3 統計頁</a>，追蹤 EP01 累積下載數與聽眾地區分布。</p></td>
                </tr>
              </table>
            </td></tr>
            <tr><td style="padding:8px 0;border-bottom:1px solid #e8ecf5;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="width:28px;font-size:16px;vertical-align:top;padding-top:1px;">🎙️</td>
                  <td><p style="margin:0;font-size:13px;color:#1a1a2e;line-height:1.6;"><strong>規劃 EP02 發布</strong> — 建議每 2 週一集的節奏維持聽眾黏著度；確認錄音進度，並更新各平台封面描述。</p></td>
                </tr>
              </table>
            </td></tr>
            <tr><td style="padding:8px 0;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="width:28px;font-size:16px;vertical-align:top;padding-top:1px;">🌐</td>
                  <td><p style="margin:0;font-size:13px;color:#1a1a2e;line-height:1.6;"><strong>落地頁流量追蹤</strong> — 確認 <a href="https://the-journey-jnr.vercel.app" style="color:#0f3460;">the-journey-jnr.vercel.app</a> 是否有 analytics 工具，開始記錄每週 UV / 點擊轉換。</p></td>
                </tr>
              </table>
            </td></tr>
          </table>
        </div>
      </td></tr>

      <!-- FOOTER -->
      <tr><td style="background:#1a1a2e;border-radius:0 0 16px 16px;padding:24px 36px;text-align:center;">
        <p style="margin:0 0 8px;font-size:13px;color:#a0c4ff;font-weight:600;">在路上 The Journey</p>
        <p style="margin:0 0 12px;font-size:12px;color:#6b8099;">此週報由 AI 助手自動生成，數據截至 {today}</p>
        <p style="margin:0;font-size:12px;color:#4a6080;">
          <a href="https://the-journey-jnr.vercel.app" style="color:#a0c4ff;text-decoration:none;">收聽落地頁</a>
          &nbsp;·&nbsp;
          <a href="https://op3.dev/show/db2884bfddc34f27b1b6c0409df16eb4" style="color:#a0c4ff;text-decoration:none;">OP3 統計</a>
        </p>
      </td></tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""

# Send email
smtp_user = "ryan181854@gmail.com"
smtp_pass = "ghtiqxwxddeatfme"
to_addr   = "ryan181854@gmail.com"
subject   = f"在路上 The Journey ｜每週週報（{today}）"

msg = MIMEMultipart("alternative")
msg["Subject"] = subject
msg["From"]    = f"在路上 The Journey <{smtp_user}>"
msg["To"]      = to_addr

msg.attach(MIMEText(html, "html", "utf-8"))

import socket

def smtp_send_ipv4():
    """Force IPv4 to avoid EAFNOSUPPORT in IPv6-restricted environments."""
    old_getaddrinfo = socket.getaddrinfo
    def ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return old_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
    socket.getaddrinfo = ipv4_getaddrinfo
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_addr], msg.as_bytes())
    finally:
        socket.getaddrinfo = old_getaddrinfo

smtp_send_ipv4()
print(f"✅ 已寄出 → {to_addr}")
