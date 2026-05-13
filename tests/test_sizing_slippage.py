import math
import os
import sys

# ensure project root is importable when running pytest from tests/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from directional_binance_agents import PositionSizer
from exchange_prices import estimate_slippage


def test_position_sizer_basic():
    s = PositionSizer(account_usdt=10000, risk_pct=0.01, leverage=10)
    entry = 100.0
    stop = 95.0
    result = s.size(entry, stop)
    assert result is not None
    assert result['risk_amount'] == 100.0
    assert result['qty'] > 0


def test_estimate_slippage_fill():
    # simple book: 3 levels
    levels = [(100.0, 1.0), (101.0, 2.0), (102.0, 5.0)]
    # need 2.5 qty -> fills at avg price = (1*100 + 1.5*101)/2.5
    sl = estimate_slippage(levels, 2.5, reference_price=100.0)
    assert sl is not None
    # average price should be > 100, so slippage positive
    assert sl > 0
