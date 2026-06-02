import yfinance as yf
import json
import os
from datetime import datetime, timezone

COMMON = "005930.KS"
PREF = "005935.KS"

def get_close(ticker: str):
    df = yf.download(ticker, period="10y", interval="1d", auto_adjust=True, progress=False)
    close = df["Close"]
    if hasattr(close, "squeeze"):
        close = close.squeeze()
    return close

common_close = get_close(COMMON)
pref_close   = get_close(PREF)

common_ticker = yf.Ticker(COMMON)
pref_ticker   = yf.Ticker(PREF)

try:
    common_price = float(common_ticker.fast_info.last_price)
    pref_price   = float(pref_ticker.fast_info.last_price)
except Exception:
    common_price = float(common_close.iloc[-1])
    pref_price   = float(pref_close.iloc[-1])

import pandas as pd
df = pd.DataFrame({"common": common_close, "pref": pref_close}).dropna()

gap = (df["common"] - df["pref"]) / df["common"] * 100
df["gap"] = gap

history = []
for date, row in df.iterrows():
    date_str = date.strftime("%Y-%m-%d") if hasattr(date, "strftime") else str(date)[:10]
    history.append({
        "date": date_str,
        "common": int(round(float(row["common"]))),
        "pref":   int(round(float(row["pref"]))),
        "gap":    round(float(row["gap"]), 2),
    })

current_gap = (common_price - pref_price) / common_price * 100

data = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "current": {
        "common": int(round(common_price)),
        "pref":   int(round(pref_price)),
        "gap":    round(current_gap, 2),
    },
    "stats": {
        "gap_min": round(float(df["gap"].min()), 2),
        "gap_max": round(float(df["gap"].max()), 2),
        "gap_avg": round(float(df["gap"].mean()), 2),
    },
    "history": history,
}

os.makedirs("data", exist_ok=True)
with open("data/prices.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(
    f"Updated | 보통주: {common_price:,.0f}원 | 우선주: {pref_price:,.0f}원 | 괴리율: {current_gap:.2f}%"
)
