"""Load the raw Binance CSVs into a DuckDB database.

It reads every CSV in data/raw/, stacks them into a single market_klines
table and runs the create-tables SQL so the schema is explicit and typed.
DuckDB is used because it runs in process, needs no server and is fast on
analytical queries over a few hundred thousand rows.
"""

from pathlib import Path

import duckdb
import pandas as pd

RAW_DIR = Path("data/raw")
DB_PATH = Path("data/processed/market.duckdb")
SQL_CREATE = Path("sql/01_create_tables.sql")


def read_all_raw():
    """Read and concatenate every symbol CSV in data/raw/."""
    frames = []
    for csv_path in sorted(RAW_DIR.glob("*.csv")):
        frame = pd.read_csv(csv_path, parse_dates=["open_time", "close_time"])
        frames.append(frame)
    if not frames:
        raise FileNotFoundError(
            "No CSV files found in data/raw. Run download_binance_data.py first."
        )
    return pd.concat(frames, ignore_index=True)


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    market = read_all_raw()
    print(f"Loaded {len(market)} rows across {market['symbol'].nunique()} symbols.")

    con = duckdb.connect(str(DB_PATH))

    # Apply the explicit schema if the SQL file is present.
    if SQL_CREATE.exists():
        con.execute(SQL_CREATE.read_text())

    # Register the DataFrame and persist it as a physical table.
    con.register("market_df", market)
    con.execute("DELETE FROM market_klines;")
    con.execute(
        """
        INSERT INTO market_klines
        SELECT
            symbol,
            open_time,
            close_time,
            open,
            high,
            low,
            close,
            volume,
            quote_volume,
            number_of_trades,
            taker_buy_base_volume,
            taker_buy_quote_volume
        FROM market_df;
        """
    )

    count = con.execute("SELECT COUNT(*) FROM market_klines;").fetchone()[0]
    print(f"market_klines now holds {count} rows in {DB_PATH}.")
    con.close()


if __name__ == "__main__":
    main()
