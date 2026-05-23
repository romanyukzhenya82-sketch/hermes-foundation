# Module: Volatility Analysis

## Purpose
Analyze historical and implied volatility across different timeframes

## Functions

### VOLATILITY.historical(symbol, window) -> float
**Description:** Calculate historical volatility (annualized)

**Parameters:**
- symbol: Trading pair
- window: Number of periods (default: 30)

**Returns:** HV percentage

**Example:**
```python
hv = VOLATILITY.historical("BTCUSDT", 30)
# HV: 0.65 (65% annualized)
```

### VOLATILITY.realized(symbol, timeframe) -> dict
**Description:** Calculate realized volatility metrics

**Returns:**
- rv_daily: Daily realized vol
- rv_weekly: Weekly realized vol
- rv_monthly: Monthly realized vol
- parkinson: Parkinson volatility estimator

### VOLATILITY.cone(symbol, windows) -> dict
**Description:** Generate volatility cone for multiple windows

**Parameters:**
- windows: [7, 14, 30, 60, 90] days

**Returns:**
- percentiles: [10, 25, 50, 75, 90]
- current_hv: Current position in cone

### VOLATILITY.compare(symbol, iv_source) -> dict
**Description:** Compare historical vs implied volatility

**Returns:**
- hv: Historical volatility
- iv: Implied volatility from options
- premium: IV - HV (vol premium/discount)
- zscore: Standardized difference

## Config

```yaml
volatility:
  default_window: 30
  annualization_factor: 365
  confidence_levels: [0.1, 0.25, 0.5, 0.75, 0.9]
  min_data_points: 100
```

## Dependencies
- exchange_prices.py (OHLCV data)
- module_options_chain.md (implied vol)
