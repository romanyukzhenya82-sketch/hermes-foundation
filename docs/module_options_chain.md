# Module: Options Chain

## Purpose
Retrieve and analyze crypto options data (Deribit, OKX, Binance)

## Functions

### OPTIONS.chain(underlying, expiry) -> pd.DataFrame
**Description:** Get complete options chain

**Parameters:**
- underlying: "BTC", "ETH"
- expiry: "2026-05-29" or "nearest"

**Returns:** Table with strike, type, bid, ask, IV, volume, OI

### OPTIONS.atm_strike(underlying) -> float
**Description:** Get at-the-money strike price

### OPTIONS.implied_volatility_surface(underlying) -> dict
**Description:** Build IV surface across strikes and expirations

**Returns:**
- strikes: Strike prices
- expiries: Expiration dates
- iv_matrix: 2D array of IV values

### OPTIONS.volume_by_strike(underlying, expiry) -> dict
**Description:** Volume analysis by strike

**Returns:**
- call_volume: Per strike
- put_volume: Per strike
- put_call_ratio: Volume ratio

### OPTIONS.open_interest(underlying, expiry) -> dict
**Description:** Open interest analysis

**Returns:**
- max_pain: Price with max OI pain
- call_oi: OI by strike
- put_oi: OI by strike

## Config

```yaml
options:
  default_exchange: "deribit"
  supported_underlyings: ["BTC", "ETH"]
  update_frequency: 5  # seconds
```

## Dependencies
- exchange_options.py (Deribit API)
- module_greeks_calculator.md
