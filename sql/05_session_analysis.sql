-- 05_session_analysis.sql
-- Break activity down by global trading session using the UTC hour.
-- Crypto trades 24/7, but liquidity and flow still follow the rhythm of
-- the Asia, Europe and US working hours. This is useful for operations
-- and risk teams planning coverage and monitoring windows.

WITH sessionized AS (
    SELECT
        symbol,
        open_time,
        quote_volume,
        number_of_trades,
        ABS(LN(close / NULLIF(LAG(close) OVER (
            PARTITION BY symbol ORDER BY open_time
        ), 0))) AS abs_return,
        CASE
            WHEN EXTRACT('hour' FROM open_time) BETWEEN 0 AND 7  THEN 'Asia'
            WHEN EXTRACT('hour' FROM open_time) BETWEEN 8 AND 15 THEN 'Europe'
            ELSE 'US'
        END AS trading_session
    FROM market_klines
)

SELECT
    symbol,
    trading_session,
    COUNT(*)                  AS hours,
    AVG(quote_volume)         AS avg_quote_volume,
    AVG(number_of_trades)     AS avg_trades,
    AVG(abs_return)           AS avg_abs_return
FROM sessionized
GROUP BY symbol, trading_session
ORDER BY symbol, avg_quote_volume DESC;
