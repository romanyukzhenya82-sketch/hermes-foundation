# MODULE: MARKET REGIME DETECTOR
# v1.0.0 | 2026-05-23

## НАЗНАЧЕНИЕ
Определяет режим рынка: trend / range / chop / breakout.

## PROTOCOL

### REGIME.detect(symbol, timeframe) → str

Индикаторы:
- ADX: > 25 = trend, < 20 = range/chop
- BB Width: > avg * 1.5 = breakout
- OI delta trend: confirms direction

Returns:
- "uptrend" | "downtrend" | "range" | "chop" | "breakout_up" | "breakout_down"

## CONFIG

```yaml
market_regime:
  adx_trend_threshold: 25
  adx_range_threshold: 20
  bb_width_mult: 1.5
  lookback_candles: 14
```

## DEPENDENCIES
- exchange_prices.py (ADX, BB)
- config.yaml [market_regime]

## CHANGELOG
v1.0.0: ADX + BB Width regime detection
