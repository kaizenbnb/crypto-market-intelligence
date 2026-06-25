-- 03_volume_anomalies.sql
-- Flag hours where quote volume is far above each asset's recent baseline.
-- A 7 day rolling window (168 hourly candles) gives mean and standard
-- deviation, and the z-score measures how unusual the current hour is.
-- Anything above 3 standard deviations is treated as an anomaly worth a look.

WITH hourly AS (
    SELECT
        symbol,
        open_time,
        quote_volume,
        number_of_trades,
        ABS(LN(close / NULLIF(LAG(close) OVER (
            PARTITION BY symbol ORDER BY open_time
        ), 0))) AS abs_return
    FROM market_klines
),

baseline AS (
    SELECT
        symbol,
        open_time,
        quote_volume,
        number_of_trades,
        abs_return,
        AVG(quote_volume) OVER (
            PARTITION BY symbol
            ORDER BY open_time
            ROWS BETWEEN 168 PRECEDING AND 1 PRECEDING
        ) AS avg_volume_7d,
        STDDEV(quote_volume) OVER (
            PARTITION BY symbol
            ORDER BY open_time
            ROWS BETWEEN 168 PRECEDING AND 1 PRECEDING
        ) AS std_volume_7d
    FROM hourly
)

SELECT
    symbol,
    open_time,
    quote_volume,
    avg_volume_7d,
    ROUND((quote_volume - avg_volume_7d) / NULLIF(std_volume_7d, 0), 2) AS volume_z_score,
    abs_return,
    number_of_trades
FROM baseline
WHERE std_volume_7d IS NOT NULL
  AND (quote_volume - avg_volume_7d) / NULLIF(std_volume_7d, 0) > 3
ORDER BY volume_z_score DESC;
