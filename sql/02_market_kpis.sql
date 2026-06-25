-- 02_market_kpis.sql
-- Daily KPIs per asset from hourly candles.
-- Shows aggregation, window functions, ratios, division-by-zero control
-- and a financial reading of the data (realized volatility, taker buy ratio).

WITH hourly AS (
    SELECT
        symbol,
        open_time,
        open,
        high,
        low,
        close,
        volume,
        quote_volume,
        number_of_trades,
        taker_buy_quote_volume,
        -- hourly log return, used to build realized volatility
        LN(close / NULLIF(LAG(close) OVER (
            PARTITION BY symbol ORDER BY open_time
        ), 0)) AS log_return
    FROM market_klines
)

SELECT
    symbol,
    DATE_TRUNC('day', open_time)                       AS trading_day,
    COUNT(*)                                            AS candles,
    MIN(low)                                            AS daily_low,
    MAX(high)                                           AS daily_high,
    FIRST(open ORDER BY open_time)                      AS daily_open,
    LAST(close ORDER BY open_time)                      AS daily_close,
    SUM(volume)                                         AS base_volume,
    SUM(quote_volume)                                   AS quote_volume,
    SUM(number_of_trades)                               AS trades,
    -- share of quote volume that came from aggressive buyers
    SUM(taker_buy_quote_volume) / NULLIF(SUM(quote_volume), 0) AS taker_buy_ratio,
    -- realized volatility as the standard deviation of hourly log returns
    STDDEV(log_return)                                  AS realized_volatility
FROM hourly
GROUP BY symbol, trading_day
ORDER BY trading_day DESC, quote_volume DESC;
