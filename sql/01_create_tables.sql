-- 01_create_tables.sql
-- Explicit schema for the raw market data loaded from Binance klines.
-- Keeping the schema in SQL makes the data contract obvious to any reviewer.

CREATE TABLE IF NOT EXISTS market_klines (
    symbol                  VARCHAR      NOT NULL,
    open_time               TIMESTAMP    NOT NULL,
    close_time              TIMESTAMP    NOT NULL,
    open                    DOUBLE,
    high                    DOUBLE,
    low                     DOUBLE,
    close                   DOUBLE,
    volume                  DOUBLE,       -- base asset volume
    quote_volume            DOUBLE,       -- quote asset volume (USDT)
    number_of_trades        BIGINT,
    taker_buy_base_volume   DOUBLE,
    taker_buy_quote_volume  DOUBLE,
    PRIMARY KEY (symbol, open_time)
);
