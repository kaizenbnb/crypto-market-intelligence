# Data

This folder holds the market data used by the project.

- `raw/` contains one CSV per symbol, downloaded from public Binance klines by `src/download_binance_data.py`.
- `processed/` holds the DuckDB database built by `src/load_to_duckdb.py`.

The full datasets and the database are git ignored on purpose, so the repo stays
light and no large binaries are committed. Run the two scripts to rebuild them
locally. Only small sample files are kept in version control.

No private account data, API keys or trading activity are stored here.
