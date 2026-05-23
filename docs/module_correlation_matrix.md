# Module: Correlation Matrix

## Purpose
Analyze price correlations between multiple assets

## Functions

### CORRELATION.matrix(symbols, window) -> pd.DataFrame
**Description:** Calculate correlation matrix for multiple symbols

**Parameters:**
- symbols: List of trading pairs
- window: Rolling window (default: 30 days)

**Returns:** Correlation matrix (values -1 to 1)

**Example:**
```python
matrix = CORRELATION.matrix(["BTCUSDT", "ETHUSDT", "BNBUSDT"], 30)
# Matrix:
#          BTC    ETH    BNB
# BTC     1.00   0.85   0.72
# ETH     0.85   1.00   0.68
# BNB     0.72   0.68   1.00
```

### CORRELATION.rolling(symbol1, symbol2, window) -> pd.Series
**Description:** Calculate rolling correlation between two assets

**Returns:** Time series of correlation values

### CORRELATION.heatmap(symbols, window) -> dict
**Description:** Generate correlation heatmap data

**Returns:**
- matrix: Correlation values
- clusters: Identified correlation clusters
- outliers: Assets with low correlation

### CORRELATION.lead_lag(symbol1, symbol2, max_lag) -> dict
**Description:** Analyze lead-lag relationships

**Returns:**
- best_lag: Optimal lag period
- correlation_at_lag: Correlation value
- direction: Which symbol leads

### CORRELATION.breakdown_by_regime(symbols, regimes) -> dict
**Description:** Correlation analysis by market regime

**Returns:** Correlation matrices for each regime (trending, ranging, volatile)

## Config

```yaml
correlation:
  default_window: 30
  min_correlation: 0.3
  rolling_windows: [7, 14, 30, 60]
  clustering_threshold: 0.7
```

## Dependencies
- exchange_prices.py (price data)
- module_market_regime.md (regime detection)
