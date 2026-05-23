# Module: Portfolio Optimizer

## Purpose
Optimize portfolio allocation and position sizing

## Functions

### PORTFOLIO.optimize(assets, constraints) -> dict
**Description:** Mean-variance optimization

**Returns:** optimal_weights, expected_return, risk

### PORTFOLIO.kelly_criterion(win_rate, win_loss_ratio) -> float
**Description:** Calculate Kelly position size

### PORTFOLIO.risk_parity(assets) -> dict
**Description:** Equal risk contribution allocation

### PORTFOLIO.efficient_frontier(assets) -> pd.DataFrame
**Returns:** risk/return combinations

## Config
```yaml
portfolio:
  max_position: 0.20
  min_position: 0.05
```

## Dependencies
- module_risk_metrics.md
- scipy.optimize
