# Module: Signal Generator

## Purpose
Generate trading signals based on market conditions

## Functions

### SIGNAL.generate(symbol, strategy) -> dict
**Returns:** signal ("BUY"/"SELL"/"HOLD"), strength (0-1), confidence

### SIGNAL.combine(signals, method) -> dict
**Description:** Aggregate multiple signals
**Methods:** weighted_average, voting, ensemble

### SIGNAL.backtest_signal(signal_history, prices) -> dict
**Returns:** win_rate, avg_profit, sharpe

## Config
```yaml
signals:
  min_confidence: 0.6
  combination_method: "weighted_average"
```

## Dependencies
- module_market_regime.md
- module_volatility_analysis.md
