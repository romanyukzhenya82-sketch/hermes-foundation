# Module: Risk Metrics

## Purpose
Calculate portfolio risk metrics (VaR, CVaR, Sharpe, Sortino)

## Functions

### RISK.var(returns, confidence) -> float
**Description:** Value at Risk calculation

### RISK.cvar(returns, confidence) -> float
**Description:** Conditional VaR (Expected Shortfall)

### RISK.sharpe_ratio(returns, risk_free) -> float

### RISK.sortino_ratio(returns, target) -> float

### RISK.max_drawdown(equity_curve) -> dict
**Returns:** max_dd, duration, recovery_time

### RISK.beta(asset_returns, market_returns) -> float

## Config
```yaml
risk:
  var_confidence: 0.95
  risk_free_rate: 0.05
```

## Dependencies
- exchange_prices.py
