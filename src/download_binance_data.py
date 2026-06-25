"""Download public Binance spot kline (candlestick) data.

This script uses the public market data endpoint, so no API key is needed.
It downloads 1 hour candles for a set of major pairs over a recent window
and writes one CSV per symbol into data/raw/.

Reference: GET /api/v3/klines on the public market data domain.
"""

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

# Public market data only domain. No authentication required.
BASE_URL = "https://data-api.binance.vision/api/v3/klines"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
INTERVAL = "1h"
DAYS = 90
MAX_LIMIT = 1000  # Binance hard cap per request

# Column names as returned by the klines endpoint.
KLINE_COLUMNS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "number_of_trades",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "ignore",
]

RAW_DIR = Path("data/raw")


def to_millis(dt):
    """Convert a timezone aware datetime to milliseconds since epoch."""
    return int(dt.timestamp() * 1000)


def fetch_klines(symbol, start_ms, end_ms):
    """Page through the klines endpoint until the window is covered."""
    rows = []
    cursor = start_ms
    while cursor < end_ms:
        params = {
            "symbol": symbol,
            "interval": INTERVAL,
            "startTime": cursor,
            "endTime": end_ms,
            "limit": MAX_LIMIT,
        }
        response = requests.get(BASE_URL, params=params, timeout=20)
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        rows.extend(batch)
        # Advance the cursor one millisecond past the last open time.
        cursor = batch[-1][0] + 1
        # Be polite with the public endpoint.
        time.sleep(0.25)
    return rows


def clean_frame(rows, symbol):
    """Turn raw rows into a typed, tidy DataFrame."""
    frame = pd.DataFrame(rows, columns=KLINE_COLUMNS)
    frame = frame.drop(columns=["ignore"])
    frame["symbol"] = symbol

    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_volume",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
    ]
    for col in numeric_cols:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")

    frame["number_of_trades"] = pd.to_numeric(
        frame["number_of_trades"], errors="coerce"
    ).astype("Int64")

    frame["open_time"] = pd.to_datetime(frame["open_time"], unit="ms", utc=True)
    frame["close_time"] = pd.to_datetime(frame["close_time"], unit="ms", utc=True)

    frame = frame.drop_duplicates(subset=["symbol", "open_time"])
    frame = frame.sort_values("open_time").reset_index(drop=True)
    return frame


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=DAYS)
    start_ms, end_ms = to_millis(start), to_millis(end)

    for symbol in SYMBOLS:
        print(f"Downloading {symbol} {INTERVAL} for {DAYS} days ...")
        rows = fetch_klines(symbol, start_ms, end_ms)
        frame = clean_frame(rows, symbol)
        out_path = RAW_DIR / f"{symbol}.csv"
        frame.to_csv(out_path, index=False)
        print(f"  saved {len(frame)} rows to {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
