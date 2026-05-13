# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-05-13

### Added
- `options_data.py` — basic ATM IV accessor (Deribit) for OptionsAgent alerts.
- `exchange_prices.py` enhancements: `get_order_book`, `estimate_slippage` for depth-aware arb checks.
- `directional_binance_agents.py` — ArbAgent hardened (slippage, fees, depth), OptionsAgent integrates IV when available.
- `run_moonshot_sweep.py` — parameter sweep runner for Moonshot backtest.
- `tests/test_sizing_slippage.py` — pytest tests for sizing and slippage estimation.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) to run `py_compile` and `pytest`.

### Changed
- Relaxed candidate filtering and improved console encoding handling.

### Notes
- Moonshot sweep and OptionsAgent are initial implementations; production use requires further validation and exchange API credentials for order execution.
