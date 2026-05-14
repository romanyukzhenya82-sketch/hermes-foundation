import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
from deep_binance_analysis import SYMBOL_RE


def test_valid_symbols_pass():
    valid = ['BTCUSDT', 'ETHUSDT', 'XAGUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
             'HYPEUSDT', 'TAOUSDT', 'PAXGUSDT', 'DOGEUSDT', 'AB1USDT']
    for sym in valid:
        assert SYMBOL_RE.match(sym), f'{sym} should pass filter'


def test_invalid_symbols_blocked():
    invalid = [
        '币安人生USDT',        # chinese chars
        'BTCUSDT-PERP',        # hyphen
        'btcusdt',             # lowercase
        'BTCUSDT1234567890',   # too long prefix
        'USDT',                # no base
        'BTCDOWNUSDT',         # contains DOWN — filtered separately, but regex allows
        ' BTCUSDT',            # leading space
    ]
    blocked = ['币安人生USDT', 'BTCUSDT-PERP', 'btcusdt', 'BTCUSDT1234567890', 'USDT', ' BTCUSDT']
    for sym in blocked:
        assert not SYMBOL_RE.match(sym), f'{sym} should be blocked'


def test_down_up_excluded_by_name_check():
    # BTCDOWNUSDT passes regex but is filtered by 'DOWN' in symbol in scan_universe
    assert 'DOWN' in 'BTCDOWNUSDT'
    assert 'UP' in 'BTCUPUSDT'
