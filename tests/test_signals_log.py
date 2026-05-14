import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_append_signals_log_writes_records(tmp_path):
    import directional_binance_agents as da
    log_path = tmp_path / 'test_signals.jsonl'

    with patch.object(da, 'SIGNALS_LOG', log_path):
        da.append_signals_log([
            {'symbol': 'BTCUSDT', 'direction': 'LONG', 'entry_low': 80000, 'stop': 79500,
             'tp1': 81000, 'tp2': 82000, 'score': 120, 'mode': 'futures', 'rr1': 2.0},
            {'symbol': 'ETHUSDT', 'direction': 'SHORT', 'entry_low': 2300, 'stop': 2350,
             'tp1': 2200, 'tp2': 2100, 'score': 95, 'mode': 'futures', 'rr1': 2.5},
        ], regime='flat / low-volatility')

    lines = log_path.read_text(encoding='utf-8').strip().split('\n')
    assert len(lines) == 2
    rec0 = json.loads(lines[0])
    assert rec0['symbol'] == 'BTCUSDT'
    assert rec0['direction'] == 'LONG'
    assert rec0['regime'] == 'flat / low-volatility'
    assert rec0['outcome'] is None
    assert 'ts' in rec0


def test_append_signals_log_appends_multiple_runs(tmp_path):
    import directional_binance_agents as da
    log_path = tmp_path / 'test_signals.jsonl'

    sig = {'symbol': 'SOLUSDT', 'direction': 'LONG', 'entry_low': 100, 'stop': 95,
           'tp1': 110, 'tp2': 120, 'score': 80, 'mode': 'futures', 'rr1': 2.0}

    with patch.object(da, 'SIGNALS_LOG', log_path):
        da.append_signals_log([sig], 'regime_a')
        da.append_signals_log([sig], 'regime_b')

    lines = log_path.read_text(encoding='utf-8').strip().split('\n')
    assert len(lines) == 2
