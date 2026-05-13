# Hermes Foundation — Market Scanning & Agents

This repository contains market scanning and directional agents focused on Binance futures/spot, with additional helpers for arbitrage, options alerts, and a Moonshot backtester.

What's included in this branch (`feature/options-moonshot-ci`):

- `deep_binance_analysis.py` — market scanner and shortlist builder
- `directional_binance_agents.py` — agents: Long, Short, Spot, Arb, Moonshot, Options
- `exchange_prices.py` — live price helpers, order book fetch, slippage estimator
- `options_data.py` — best-effort IV accessor (Deribit)
- `backtest_moonshot.py` + `run_moonshot_sweep.py` — moonshot detector and parameter sweep runner
- `tests/` — lightweight pytest tests (PositionSizer, slippage)
- `.github/workflows/ci.yml` — CI to run `py_compile` and `pytest`

Quick start
------------

1. Create a Python 3.11+ virtualenv and install deps:

```bash
python -m pip install -r requirements.txt
```

2. Run the agents locally (prints shortlist & signals):

```bash
python directional_binance_agents.py
```

3. Run unit tests:

```bash
pytest -q
```

4. Run a quick Moonshot sweep (fast mode, 3 symbols):

```bash
python run_moonshot_sweep.py
# output: moonshot_sweep.csv
```

Notes & next steps
------------------
- `ArbAgent` now estimates slippage and fees via order book sampling; production usage requires exchange API keys and careful execution logic.
- `OptionsAgent` is a lightweight alerting skeleton; integrate options chains / IV surfaces (Deribit, Binance Options) to enable sizing and trade generation.
- The Moonshot backtest is intentionally conservative; extend to larger universes off-line.

To publish changes and create a PR (example):

```bash
git remote add origin git@github.com:youruser/yourrepo.git
git push -u origin feature/options-moonshot-ci
# then create PR on GitHub or use `gh` cli: gh pr create --fill
```

If you want, I can push this branch to a remote and open a PR — grant the repo/remote or provide the URL.

---
Generated changes summary: options integration, arb hardening (slippage/fees/depth), moonshot sweep runner, tests, CI workflow.
