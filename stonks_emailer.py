import json, os, datetime as dt
import yfinance as yf
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

with open("portfolio.json") as f:
    portfolio = json.load(f)

# ── 1. collect data ──────────────────────────────────────────────────────
rows = []
for h in portfolio:
    close_yest, close_today = (
        yf.Ticker(h["symbol"]).history(period="2d")["Close"].iloc[-2:]
    )
    total_gain = float((close_today - h["cost_basis"]) * h["shares"])  # ensure float ✅
    rows.append(
        (
            h["symbol"],          # sym
            h["shares"],          # sh
            h["cost_basis"],      # cb
            close_today,          # price
            close_today - close_yest,  # day
            total_gain            # tot
        )
    )

# ── 2. build the HTML table ──────────────────────────────────────────────
table = "".join(
    f"<tr><td>{sym}</td><td>{sh}</td><td>${cb:,.2f}</td>"
    f"<td>${price:,.2f}</td><td>{day:+.2f}</td><td>${tot:+,.2f}</td></tr>"
    for sym, sh, cb, price, day, tot in rows
)

html = f"""
<h3>{dt.date.today():%b %d %Y} Portfolio</h3>
<table border=1 cellpadding=4>
  <tr>
    <th>Ticker</th><th>Shares</th><th>Cost&nbsp;Basis</th>
    <th>Price</th><th>Day&nbsp;Δ</th><th>Total&nbsp;Δ</th>
  </tr>
  {table}
</table>
"""

msg = MIMEMultipart("alternative")
msg["Subject"] = f"{dt.date.today():%b %d} Portfolio Snapshot"
msg["From"]    = os.environ["GMAIL_USER"]
msg["To"]      = os.environ["TO_EMAIL"]
msg.attach(MIMEText(html, "html"))

context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:  # SSL port 465 :contentReference[oaicite:2]{index=2}
    s.login(os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASS"])
    s.send_message(msg)

print("✅ Gmail email sent")
