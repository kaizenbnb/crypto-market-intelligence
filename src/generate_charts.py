"""End to end pipeline that builds the four charts from real Binance data.

This single script is what the GitHub Action runs. It downloads public
Binance kline data, loads it into an in memory DuckDB, runs the analytical
SQL from the sql/ folder and writes the four PNG charts into outputs/charts/.

It uses a 30 day window so the workflow stays fast, while still surfacing
volatility, volume anomalies and session behaviour. No API key is required.
"""

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")  # headless backend for CI
import matplotlib.pyplot as plt
import pandas as pd
import requests

BASE_URL = "https://data-api.binance.vision/api/v3/klines"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
INTERVAL = "1h"
DAYS = 30
MAX_LIMIT = 1000

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "number_of_trades", "taker_buy_base_volume",
    "taker_buy_quote_volume", "ignore",
]

ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = ROOT / "sql"
CHARTS_DIR = ROOT / "outputs" / "charts"

GOLD = "#F0B90B"
GREEN = "#2EBD85"


def to_millis(dt):
    return int(dt.timestamp() * 1000)


def fetch_symbol(symbol, start_ms, end_ms):
    rows, cursor = [], start_ms
    while cursor < end_ms:
        params = {
            "symbol": symbol, "interval": INTERVAL,
            "startTime": cursor, "endTime": end_ms, "limit": MAX_LIMIT,
        }
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        cursor = batch[-1][0] + 1
        time.sleep(0.2)
    frame = pd.DataFrame(rows, columns=KLINE_COLUMNS).drop(columns=["ignore"])
    frame["symbol"] = symbol
    numeric = [
        "open", "high", "low", "close", "volume", "quote_volume",
        "taker_buy_base_volume", "taker_buy_quote_volume",
    ]
    for col in numeric:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame["number_of_trades"] = pd.to_numeric(
        frame["number_of_trades"], errors="coerce"
    )
    frame["open_time"] = pd.to_datetime(frame["open_time"], unit="ms", utc=True)
    frame["close_time"] = pd.to_datetime(frame["close_time"], unit="ms", utc=True)
    return frame.drop_duplicates(["symbol", "open_time"]).sort_values("open_time")


def download():
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=DAYS)
    frames = []
    for symbol in SYMBOLS:
        print(f"Downloading {symbol} ...")
        frames.append(fetch_symbol(symbol, to_millis(start), to_millis(end)))
    market = pd.concat(frames, ignore_index=True)
    print(f"Downloaded {len(market)} rows.")
    return market


def build_db(market):
    con = duckdb.connect(":memory:")
    con.execute((SQL_DIR / "01_create_tables.sql").read_text())
    con.register("market_df", market)
    con.execute(
        """
        INSERT INTO market_klines
        SELECT symbol, open_time, close_time, open, high, low, close,
               volume, quote_volume, number_of_trades,
               taker_buy_base_volume, taker_buy_quote_volume
        FROM market_df;
        """
    )
    return con


def run_file(con, name):
    return con.execute((SQL_DIR / name).read_text()).df()


def chart_volatility(kpis):
    data = kpis.groupby("symbol")["realized_volatility"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    data.plot(kind="barh", color=GOLD, ax=ax)
    ax.set_title("Average realized volatility by asset")
    ax.set_xlabel("Realized volatility (std of hourly log returns)")
    ax.set_ylabel("")
    save(fig, "volatility_by_asset.png")


def chart_anomalies(anomalies):
    fig, ax = plt.subplots(figsize=(9, 5))
    if anomalies.empty:
        ax.text(0.5, 0.5, "No volume anomalies above 3 sigma in this window",
                ha="center", va="center")
        ax.axis("off")
    else:
        top = anomalies.sort_values("volume_z_score", ascending=False).head(15)
        labels = top["symbol"] + "  " + top["open_time"].astype(str).str[:13]
        ax.barh(range(len(top)), top["volume_z_score"], color=GOLD)
        ax.set_yticks(range(len(top)))
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_title("Top volume anomalies by z-score")
        ax.set_xlabel("Volume z-score (7 day rolling baseline)")
    save(fig, "volume_anomaly_score.png")


def chart_sessions(con):
    heat = con.execute(
        """
        SELECT symbol, EXTRACT('hour' FROM open_time) AS utc_hour,
               AVG(quote_volume) AS avg_quote_volume
        FROM market_klines GROUP BY symbol, utc_hour ORDER BY symbol, utc_hour
        """
    ).df()
    pivot = heat.pivot(index="symbol", columns="utc_hour", values="avg_quote_volume")
    fig, ax = plt.subplots(figsize=(12, 4))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrBr")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([int(c) for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Average quote volume by UTC hour")
    ax.set_xlabel("UTC hour")
    fig.colorbar(im, ax=ax, label="avg quote volume")
    save(fig, "session_volume_heatmap.png")


def chart_health(health):
    data = health.sort_values("market_health_score")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(data["symbol"], data["market_health_score"], color=GREEN)
    ax.set_title("Market health score by asset (last 24h)")
    ax.set_xlabel("Score (higher is calmer and more liquid)")
    for i, v in enumerate(data["market_health_score"]):
        ax.text(v + 1, i, f"{v:.0f}", va="center")
    save(fig, "market_health_score.png")


def save(fig, name):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    out = CHARTS_DIR / name
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out}")


def main():
    market = download()
    con = build_db(market)

    kpis = run_file(con, "02_market_kpis.sql")
    anomalies = run_file(con, "03_volume_anomalies.sql")
    health = run_file(con, "06_market_health_score.sql")

    chart_volatility(kpis)
    chart_anomalies(anomalies)
    chart_sessions(con)
    chart_health(health)

    con.close()
    print("All charts generated.")


if __name__ == "__main__":
    main()
