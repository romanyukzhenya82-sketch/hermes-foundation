import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config_loader import load_config, AppConfig, ScannerConfig, RiskConfig


def test_default_config_loads():
    cfg = load_config()
    assert isinstance(cfg, AppConfig)
    assert isinstance(cfg.scanner, ScannerConfig)
    assert isinstance(cfg.risk, RiskConfig)


def test_scanner_defaults():
    cfg = load_config()
    assert cfg.scanner.scan_limit > 0
    assert cfg.scanner.min_quote_volume > 0
    assert cfg.scanner.min_oi_notional > 0
    assert 1 <= cfg.scanner.scan_workers <= 32


def test_risk_defaults_sane():
    cfg = load_config()
    assert 0 < cfg.risk.default_risk_pct <= 0.05
    assert 1 <= cfg.risk.default_leverage <= 50
    assert cfg.risk.default_account_usdt > 0


def test_config_values_from_yaml():
    # config.yaml exists in project root, values should be loaded
    cfg = load_config()
    # scanner.scan_limit should be 80 as set in config.yaml
    assert cfg.scanner.scan_limit == 80
    # risk account
    assert cfg.risk.default_account_usdt == 10_000


def test_agents_options_underlyings():
    cfg = load_config()
    underlyings = cfg.agents.options.underlyings
    assert 'BTCUSDT' in underlyings
    assert 'ETHUSDT' in underlyings


def test_spot_agent_stop_mult():
    cfg = load_config()
    assert cfg.agents.spot.stop_atr_mult > 0
    assert cfg.agents.spot.tp1_atr_mult > cfg.agents.spot.stop_atr_mult
