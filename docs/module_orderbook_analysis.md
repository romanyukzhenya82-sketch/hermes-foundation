# Module: Orderbook Analysis

## Purpose
Deep analysis of order book dynamics and patterns

## Functions

### ORDERBOOK.walls(symbol, threshold) -> dict
**Description:** Detect buy/sell walls in order book

**Parameters:**
- threshold: Minimum size to be considered a wall (BTC or USD)

**Returns:**
- buy_walls: [{price, size, distance_from_mid}]
- sell_walls: [{price, size, distance_from_mid}]
- largest_wall: Biggest wall detected

### ORDERBOOK.spoofing_detect(symbol) -> dict
**Description:** Detect potential spoofing/layering patterns

**Returns:**
- suspicious_orders: Large orders that appear/disappear
- pattern_score: 0-1 (likelihood of manipulation)
- frequency: How often orders are cancelled

### ORDERBOOK.cumulative_delta(symbol, window) -> float
**Description:** Calculate cumulative volume delta

**Returns:** Net buying/selling pressure over period

### ORDERBOOK.bid_ask_ratio(symbol, levels) -> dict
**Description:** Analyze bid/ask volume ratio at different depths

**Returns:**
- level_1: Top of book ratio
- level_5: Top 5 levels
- level_10: Top 10 levels
- trend: "bullish" | "bearish" | "neutral"

### ORDERBOOK.support_resistance(symbol) -> dict
**Description:** Identify S/R levels from order book

**Returns:**
- support_levels: [price, strength]
- resistance_levels: [price, strength]
- confidence: How reliable these levels are

### ORDERBOOK.snapshot_diff(symbol, interval) -> dict
**Description:** Compare order book state over time

**Returns:**
- added_volume: New orders
- removed_volume: Cancelled orders
- price_shift: Mid-price movement

## Config

```yaml
orderbook:
  update_frequency: 0.5  # seconds
  depth_levels: 50
  wall_threshold_btc: 5.0
  spoofing_window: 60  # seconds
  min_wall_distance: 0.5  # % from mid
```

## Dependencies
- exchange_orderbook.py (L2/L3 data)
- module_liquidity_monitor.md
