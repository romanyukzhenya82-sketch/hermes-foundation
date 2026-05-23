# Module: Backtest Engine

## Purpose
Backtest trading strategies on historical data

## Functions

### BACKTEST.run(strategy, start_date, end_date) -> dict
**Returns:** total_return, sharpe, max_dd, trades, equity_curve

### BACKTEST.walk_forward(strategy, train_period, test_period) -> dict
**Description:** Walk-forward optimization

### BACKTEST.monte_carlo(strategy, simulations) -> dict
**Returns:** Distribution of possible outcomes

## Config
```yaml
backtest:
  initial_capital: 10000
  commission: 0.001
  slippage: 0.0005
```

## Dependencies
- exchange_prices.py
- module_risk_metrics.md
