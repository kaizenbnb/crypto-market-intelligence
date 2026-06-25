# Crypto Market Intelligence

A lightweight market intelligence project built with public Binance market data.

The goal is to detect abnormal market activity across major crypto pairs using SQL, Python and visual analytics. The project focuses on volatility, volume anomalies, trading session behaviour and a simple market health scoring framework.

## Why this project matters

Crypto markets run 24/7, which makes anomaly detection, liquidity monitoring and fast reporting especially important. This project simulates the type of analysis that supports Risk, Market Operations, Growth and Business Intelligence teams inside a crypto exchange.

The question it answers is simple:

> Which assets show unusual activity, volatility expansion or liquidity stress compared with their recent baseline?

## What it does

- Pulls public 1 hour candlestick (kline) data for five major pairs.
- Loads everything into a local DuckDB database.
- Runs analytical SQL to build KPIs, volatility measures and a rolling volume baseline.
- Flags abnormal volume using a 7 day rolling z-score.
- Breaks activity down by trading session (Asia, Europe, US).
- Produces a simple market health score per asset.
- Writes a short summary report aimed at a non technical reader.

## Assets and timeframe

| Pair | Why it is here |
| --- | --- |
| BTCUSDT | Blue chip reference |
| ETHUSDT | Blue chip reference |
| BNBUSDT | Binance ecosystem |
| SOLUSDT | High beta asset |
| XRPUSDT | Retail heavy asset |

Timeframe: 1 hour candles over roughly 90 days. Enough to surface hourly patterns, volatility regimes, volume outliers and session behaviour without building a monster.

## Skills demonstrated

- SQL data modelling and analytical queries (window functions, rolling baselines, ratios).
- Python data cleaning and feature engineering.
- Time series analysis and realized volatility.
- Market microstructure intuition (liquidity, taker flow, sessions).
- Statistical anomaly detection.
- Data visualization and clear business reporting.
- Reproducible project structure.

## Data source

This project uses public Binance market data, including kline / candlestick data and aggregate trade data. No private account data, API keys or trading activity are used. Public market data endpoints are reached through the market data only domain, so no authentication is required.

## Project structure

```text
crypto-market-intelligence/
.
README.md
requirements.txt
.gitignore

data/
  raw/                 sample only, full data is git ignored
  processed/

sql/
  01_create_tables.sql
  02_market_kpis.sql
  03_volume_anomalies.sql
  04_volatility_regimes.sql
  05_session_analysis.sql
  06_market_health_score.sql

src/
  download_binance_data.py
  load_to_duckdb.py
  utils.py

notebooks/
  01_market_intelligence_analysis.ipynb

outputs/
  charts/
    volatility_by_asset.png
    volume_anomaly_score.png
    session_volume_heatmap.png
    market_health_score.png
  summary_report.md
```

## How to run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download public Binance kline data
python src/download_binance_data.py

# 3. Load the data into DuckDB
python src/load_to_duckdb.py

# 4. Open the notebook and run all cells to build the charts
jupyter notebook notebooks/01_market_intelligence_analysis.ipynb
```

The four charts in `outputs/charts/` are generated when you run the notebook against fresh data, so the figures always match the period you downloaded.

## Charts produced

| Chart | What it shows |
| --- | --- |
| volatility_by_asset.png | Realized volatility per asset |
| volume_anomaly_score.png | Pairs ranked by volume z-score |
| session_volume_heatmap.png | Volume by UTC hour and symbol |
| market_health_score.png | Composite health score per asset |

## Market health score

A simple, explainable score per asset. It is not meant to be perfect, it is meant to be transparent:

```text
market_health_score =
    100
    - volatility_penalty
    - abnormal_volume_penalty
    - low_liquidity_penalty
    + trade_activity_score
```

The reasoning behind each component is documented in the notebook and in the summary report.

## Scope and limitations

- This is market intelligence, not trading advice.
- The sample is a fixed historical window, so results describe that period only.
- The health score is a heuristic, useful for monitoring and triage rather than prediction.

## Author

Built by Oliver Arjonilla as part of a data analytics portfolio focused on crypto markets, risk and operations.
