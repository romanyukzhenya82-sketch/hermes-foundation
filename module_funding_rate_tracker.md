# Module: Funding Rate Tracker

## Purpose
Monitor perpetual futures funding rates across exchanges

## Functions

### FUNDING.current(symbol, exchange) -> dict
**Description:** Get current funding rate

**Returns:**
- funding_rate: Current rate (%)
- next_funding_time: When next payment occurs
- funding_interval: 8h/4h/1h
- annualized_rate: APR equivalent

**Example:**
```python
rate = FUNDING.current("BTCUSDT", "binance")
# funding_rate: 0.01% (positive = longs pay shorts)
# next_funding_time: "2026-05-23 12:00:00 UTC"
# annualized_rate: 10.95%
```

### FUNDING.history(symbol, exchange, period) -> pd.DataFrame
**Description:** Historical funding rates

**Returns:** Timeseries of funding rates

### FUNDING.compare_exchanges(symbol) -> pd.DataFrame
**Description:** Compare funding across exchanges

**Returns:** Table with current rates per exchange

### FUNDING.arbitrage_opportunities(threshold) -> list
**Description:** Find funding rate arbitrage opportunities

**Parameters:**
- threshold: Minimum rate differential (%)

**Returns:**
- symbol: Trading pair
- long_exchange: Where to go long
- short_exchange: Where to go short
- rate_differential: Profit potential

### FUNDING.prediction(symbol, exchange) -> dict
**Description:** Predict next funding rate based on mark/index spread

**Returns:**
- predicted_rate: Estimated next rate
- confidence: Prediction confidence
- current_premium: Mark vs index

## Config

```yaml
funding:
  update_frequency: 60  # seconds
  tracked_symbols: ["BTCUSDT", "ETHUSDT"]
  alert_threshold: 0.1  # %
  arbitrage_min_diff: 0.05  # %
```

## Dependencies
- exchange_futures.py (funding data)
- exchange_prices.py
