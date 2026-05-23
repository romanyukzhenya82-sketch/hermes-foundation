# Module: Greeks Calculator

## Purpose
Calculate option Greeks (Delta, Gamma, Vega, Theta, Rho)

## Functions

### GREEKS.calculate(option_params) -> dict
**Description:** Calculate all Greeks for an option

**Parameters:**
- spot: Current underlying price
- strike: Strike price
- time_to_expiry: Years until expiration
- volatility: Implied volatility
- risk_free_rate: Risk-free rate
- option_type: "call" or "put"

**Returns:**
- delta: Price sensitivity
- gamma: Delta sensitivity
- vega: Volatility sensitivity
- theta: Time decay
- rho: Interest rate sensitivity

### GREEKS.portfolio(positions) -> dict
**Description:** Calculate net Greeks for portfolio

**Parameters:**
- positions: [{option, quantity}, ...]

**Returns:** Aggregated Greeks

### GREEKS.hedge_ratio(position, underlying) -> float
**Description:** Calculate delta hedge ratio

**Returns:** Number of underlying contracts needed

## Config

```yaml
greeks:
  risk_free_rate: 0.05
  calculation_method: "black_scholes"
```

## Dependencies
- module_options_chain.md
- scipy.stats (normal distribution)
