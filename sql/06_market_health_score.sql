-- 06_market_health_score.sql
-- A simple, explainable health score per asset for the most recent day.
-- The score is a heuristic for monitoring and triage, not a prediction.
-- Each component is normalised across the five assets so they are comparable,
-- then combined into a 0 to 100 score. Higher means calmer and more liquid.

WITH hourly AS (
    SELECT
        symbol,
        open_time,
        quote_volume,
        number_of_trades,
        LN(close / NULLIF(LAG(close) OVER (
            PARTITION BY symbol ORDER BY open_time
        ), 0)) AS log_return
    FROM market_klines
),

last_day AS (
    SELECT
        symbol,
        MAX(open_time) AS last_ts,
        MAX(open_time) - INTERVAL 24 HOUR AS window_start
    FROM hourly
    GROUP BY symbol
),

recent AS (
    SELECT h.*
    FROM hourly h
    JOIN last_day d
      ON h.symbol = d.symbol
     AND h.open_time > d.window_start
),

per_asset AS (
    SELECT
        symbol,
        STDDEV(log_return)                AS volatility,
        AVG(quote_volume)                 AS avg_quote_volume,
        AVG(number_of_trades)             AS avg_trades,
        MAX(ABS(log_return))              AS max_abs_return
    FROM recent
    GROUP BY symbol
),

-- normalise each metric to a 0..1 range across the five assets
ranges AS (
    SELECT
        MIN(volatility) AS vol_min, MAX(volatility) AS vol_max,
        MIN(avg_quote_volume) AS liq_min, MAX(avg_quote_volume) AS liq_max,
        MIN(avg_trades) AS trd_min, MAX(avg_trades) AS trd_max
    FROM per_asset
),

scored AS (
    SELECT
        p.symbol,
        p.volatility,
        p.avg_quote_volume,
        p.avg_trades,
        (p.volatility - r.vol_min) / NULLIF(r.vol_max - r.vol_min, 0)          AS volatility_norm,
        (p.avg_quote_volume - r.liq_min) / NULLIF(r.liq_max - r.liq_min, 0)    AS liquidity_norm,
        (p.avg_trades - r.trd_min) / NULLIF(r.trd_max - r.trd_min, 0)          AS activity_norm
    FROM per_asset p
    CROSS JOIN ranges r
)

SELECT
    symbol,
    ROUND(volatility, 5)        AS volatility,
    ROUND(avg_quote_volume, 0)  AS avg_quote_volume,
    ROUND(
        100
        - 40 * volatility_norm            -- volatility penalty
        + 20 * liquidity_norm             -- liquidity reward
        + 20 * activity_norm              -- trade activity reward
    , 1) AS market_health_score
FROM scored
ORDER BY market_health_score DESC;
