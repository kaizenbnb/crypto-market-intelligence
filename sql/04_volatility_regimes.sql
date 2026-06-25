-- 04_volatility_regimes.sql
-- Classify each asset's current volatility against its own recent history.
-- Rolling realized volatility over 24 hours is compared with the median of
-- the trailing 30 day window, so each asset is judged on its own baseline
-- rather than against the others.

WITH returns AS (
    SELECT
        symbol,
        open_time,
        LN(close / NULLIF(LAG(close) OVER (
            PARTITION BY symbol ORDER BY open_time
        ), 0)) AS log_return
    FROM market_klines
),

rolling AS (
    SELECT
        symbol,
        open_time,
        STDDEV(log_return) OVER (
            PARTITION BY symbol
            ORDER BY open_time
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) AS vol_24h
    FROM returns
),

baseline AS (
    SELECT
        symbol,
        open_time,
        vol_24h,
        MEDIAN(vol_24h) OVER (
            PARTITION BY symbol
            ORDER BY open_time
            ROWS BETWEEN 720 PRECEDING AND 1 PRECEDING
        ) AS vol_median_30d
    FROM rolling
)

SELECT
    symbol,
    open_time,
    vol_24h,
    vol_median_30d,
    ROUND(vol_24h / NULLIF(vol_median_30d, 0), 2) AS vol_ratio,
    CASE
        WHEN vol_24h / NULLIF(vol_median_30d, 0) >= 1.5 THEN 'expansion'
        WHEN vol_24h / NULLIF(vol_median_30d, 0) <= 0.6 THEN 'compression'
        ELSE 'normal'
    END AS volatility_regime
FROM baseline
WHERE vol_median_30d IS NOT NULL
ORDER BY symbol, open_time;
