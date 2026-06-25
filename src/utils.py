"""Shared helpers for the market intelligence notebook and scripts."""

from pathlib import Path

import duckdb

DB_PATH = Path("data/processed/market.duckdb")
SQL_DIR = Path("sql")


def connect(read_only=True):
    """Open a DuckDB connection to the processed database."""
    return duckdb.connect(str(DB_PATH), read_only=read_only)


def run_sql_file(con, filename):
    """Run a SQL file from the sql/ folder and return the result as a DataFrame."""
    path = SQL_DIR / filename
    query = path.read_text()
    return con.execute(query).df()


def run_query(con, query):
    """Run an inline SQL query and return the result as a DataFrame."""
    return con.execute(query).df()


def save_chart(fig, name, charts_dir="outputs/charts"):
    """Save a matplotlib figure as a tight PNG into the charts folder."""
    out_dir = Path(charts_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / name
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    return out_path
