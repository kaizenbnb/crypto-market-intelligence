# Summary Report

> This report is filled in after running the notebook against a fresh data pull.
> The placeholders in brackets are replaced with the real numbers from the run,
> so the report always describes the actual period analysed.

## Period and scope

- Pairs: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT
- Interval: 1 hour candles
- Window: [start date] to [end date]
- Source: public Binance market data (klines)

## What changed

A short, plain language paragraph describing the headline movements in the
window: which assets were calm, which expanded in volatility, and whether
volume was broadly rising or falling. Written for a reader who does not work
with data every day.

## Which assets showed abnormal activity

The volume anomaly query flagged [N] hours above three standard deviations from
the 7 day baseline. The most notable were:

- [SYMBOL] at [timestamp], z-score [value], during [context if known].
- [SYMBOL] at [timestamp], z-score [value].

These are not signals to act on. They are points that a human should look at,
because something moved away from the asset's normal behaviour.

## Volatility regimes

A note on which assets sat in expansion, compression or normal regimes across
the window, and whether any of them flipped regime during the period.

## Session behaviour

A short observation on how activity shifted across the Asia, Europe and US
sessions, and whether any asset was unusually concentrated in one session.

## Market health score

The current ranking, highest to lowest:

1. [SYMBOL] [score]
2. [SYMBOL] [score]
3. [SYMBOL] [score]
4. [SYMBOL] [score]
5. [SYMBOL] [score]

## What a risk or operations team should monitor

- The pairs with the lowest health score and the reason behind it.
- Any asset showing repeated volume anomalies in a short window.
- Sessions where liquidity thins out, which matters for execution and coverage.

## Limitations

- Fixed historical window, so results describe that period only.
- The health score is a transparent heuristic, useful for triage, not prediction.
- Public market data only. No order book depth or off exchange flow is included.
