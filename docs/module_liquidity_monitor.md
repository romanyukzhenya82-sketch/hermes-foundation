# Module: Liquidity Monitor

## Purpose
Track market liquidity and depth across exchanges

## Functions

### LIQUIDITY.depth(symbol, levels) -> dict
**Description:** Get market depth for specific price levels

**Parameters:**
- symbol: Trading pair
- levels: Number of price levels (default: 20)

**Returns:**
- bids: [[price, size], ...]
- asks: [[price, size], ...]
- bid_volume: Total bid volume
- ask_volume: Total ask volume
- spread_pct: Bid-ask spread %

**Example:**
```python
depth = LIQUIDITY.depth("BTCUSDT", 10)
# bid_volume: 125.5 BTC
# ask_volume: 98.2 BTC
# spread_pct: 0.02%
```

### LIQUIDITY.impact(symbol, size, side) -> dict
**Description:** Calculate price impact for given order size

**Parameters:**
- side: "buy" or "sell"

**Returns:**
- avg_fill_price: Average execution price
- slippage_pct: Price impact %
- liquidity_consumed: How many levels needed

### LIQUIDITY.score(symbol) -> float
**Description:** Calculate overall liquidity score (0-100)

**Factors:**
- Order book depth
- Bid-ask spread
- Volume consistency
- Price stability

### LIQUIDITY.imbalance(symbol) -> dict
**Description:** Measure orderbook imbalance

**Returns:**
- ratio: bid_volume / ask_volume
- direction: "buy_pressure" | "sell_pressure" | "neutral"
- strength: Imbalance magnitude (0-1)

### LIQUIDITY.compare_exchanges(symbol, exchanges) -> pd.DataFrame
**Description:** Compare liquidity across exchanges

**Returns:** Table with depth, spread, and score per exchange

## Config

```yaml
liquidity:
  default_levels: 20
  update_frequency: 1  # seconds
  min_spread_alert: 0.1  # %
  min_depth_alert: 10000  # USD
```

## Dependencies
- exchange_orderbook.py (real-time data)
- exchange_prices.py (price data)
