"""
Backtest for LongAgent/ShortAgent on historical 15m klines.

Usage:
  python backtest_directional.py
  python backtest_directional.py --days 60 --syms BTCUSDT ETHUSDT SOLUSDT
  python backtest_directional.py --days 30 --json bt_results.json
"""

import argparse
import json
import logging
import statistics
from datetime import datetime, timezone
from typing import Any

import requests

from config_loader import cfg

logger = logging.getLogger(__name__)

API = 'https://fapi.binance.com'
MAX_HOLD_BARS = cfg.backtest.max_hold_bars
MIN_RR = cfg.backtest.min_rr
LOOKBACK_DAYS_DEFAULT = cfg.backtest.lookback_days_default
DEFAULT_SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT',
    'XRPUSDT', 'DOGEUSDT', 'HYPEUSDT', 'XAGUSDT',
]


def safe_get(url: str, params: dict[str, Any] | None = None, timeout: int = 12) -> Any:
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        logger.debug("safe_get failed: %s %s", url, exc)
        return None


def fetch_klines_full(symbol: str, interval: str, lookback_days: int) -> list:
    bars_per_day = {'15m': 96, '1h': 24, '4h': 6}
    limit_per_req = 1500
    total_bars = bars_per_day.get(interval, 96) * lookback_days
    all_klines: list = []
    end_ms: int | None = None
    while len(all_klines) < total_bars:
        params: dict[str, Any] = {'symbol': symbol, 'interval': interval, 'limit': min(limit_per_req, total_bars - len(all_klines))}
        if end_ms:
            params['endTime'] = end_ms
        data = safe_get(f'{API}/fapi/v1/klines', params)
        if not data:
            break
        all_klines = data + all_klines
        end_ms = int(data[0][0]) - 1
        if len(data) < limit_per_req:
            break
    return all_klines[-total_bars:] if len(all_klines) > total_bars else all_klines


def build_indicator_window(klines15: list, klines60: list, klines240: list, i: int, window: int = 30) -> dict[str, Any] | None:
    """Строит row-объект для свечи i (индекс в klines15), аналогичный scan_market."""
    if i < window:
        return None
    k15 = klines15[max(0, i - window):i + 1]
    # найти соответствующие свечи 1h и 4h по времени
    ts15 = int(klines15[i][0])

    def last_before(klines, ts):
        for k in reversed(klines):
            if int(k[0]) <= ts:
                return k
        return klines[-1]

    # approximate 1h / 4h windows: last 30 candles ending at/before ts15
    k60_end = [k for k in klines60 if int(k[0]) <= ts15][-min(30, len(klines60)):]
    k240_end = [k for k in klines240 if int(k[0]) <= ts15][-min(30, len(klines240)):]
    if not k60_end or not k240_end or len(k15) < 10:
        return None

    def trend(candles):
        return 'bullish' if float(candles[-1][4]) > float(candles[0][1]) else 'bearish'

    def atr(candles):
        return statistics.mean(
            max(float(h) - float(l), abs(float(h) - float(c)), abs(float(l) - float(c)))
            for _, o, h, l, c, *_ in candles
        )

    def pct_change(candles):
        if len(candles) < 2:
            return 0.0
        return 100.0 * (float(candles[-1][4]) / float(candles[-2][4]) - 1)

    vols = [float(c[5]) for c in k15]
    avg_vol = statistics.mean(vols[:-1]) if len(vols) > 1 else vols[-1]
    vol_spike = vols[-1] / avg_vol if avg_vol else 1.0
    price = float(k15[-1][4])

    # approximate OI notional (unavailable in historical klines — use fixed flag)
    # we set a liberal threshold to not over-filter in backtest
    oi_notional_approx = 50_000_000  # assume passes filter

    row = {
        'price': price,
        'trend_15m': trend(k15),
        'trend_1h': trend(k60_end),
        'trend_4h': trend(k240_end),
        'pct15': pct_change(k15),
        'pct1h': pct_change(k60_end),
        'pct4h': pct_change(k240_end),
        'atr15': atr(k15),
        'atr1h': atr(k60_end),
        'atr4h': atr(k240_end),
        'vol_spike': vol_spike,
        'oi_notional': oi_notional_approx,
        'quote_volume': 500_000_000,    # assume passes filter
        'spread_pct': 0.0001,           # assume tight spread
        'ask_bid_imbalance': 1.0,
        'funding': 0.0,
        'support_15m': min(float(c[3]) for c in k15[-5:]),
        'resistance_15m': max(float(c[2]) for c in k15[-5:]),
        'support_1h': min(float(c[3]) for c in k60_end[-5:]),
        'resistance_1h': max(float(c[2]) for c in k60_end[-5:]),
        'fresh_15m': True,
        'fresh_1h': True,
        'fresh_4h': True,
        'score': 100.0,  # assume passes universe filter
        'category': 'major',
        'symbol': 'SYM',
    }
    return row


def simulate_trade(
    klines15: list, entry_idx: int, entry: float, stop: float, tp1: float, max_hold: int = MAX_HOLD_BARS
) -> tuple[str, int, float]:
    for j in range(1, max_hold + 1):
        if entry_idx + j >= len(klines15):
            break
        high = float(klines15[entry_idx + j][2])
        low = float(klines15[entry_idx + j][3])
        if stop < entry:
            if low <= stop:
                return 'SL', j, stop
            if high >= tp1:
                return 'TP1', j, tp1
        else:
            if high >= stop:
                return 'SL', j, stop
            if low <= tp1:
                return 'TP1', j, tp1
    last_close = float(klines15[min(entry_idx + max_hold, len(klines15) - 1)][4])
    return 'EXPIRED', max_hold, last_close


def run_backtest_for_symbol(symbol: str, lookback_days: int, agent_direction: str, verbose: bool = False) -> list[dict[str, Any]] | None:
    """Прогоняет backtest для одного символа."""
    # Import agents here to avoid circular issues
    from directional_binance_agents import LongAgent, ShortAgent, PositionSizer

    if verbose:
        print(f'  Fetching {symbol} klines...', end=' ', flush=True)

    k15 = fetch_klines_full(symbol, '15m', lookback_days)
    k60 = fetch_klines_full(symbol, '1h', lookback_days)
    k240 = fetch_klines_full(symbol, '4h', lookback_days)

    if not k15 or len(k15) < 50:
        if verbose:
            print('insufficient data')
        return None

    if verbose:
        print(f'{len(k15)} bars')

    agent = LongAgent() if agent_direction == 'LONG' else ShortAgent()
    sizer = PositionSizer(account_usdt=cfg.risk.default_account_usdt, risk_pct=cfg.risk.default_risk_pct, leverage=cfg.risk.default_leverage)

    results = []
    for i in range(30, len(k15) - MAX_HOLD_BARS - 1):
        row = build_indicator_window(k15, k60, k240, i)
        if row is None:
            continue
        row['symbol'] = symbol

        if not agent.matches(row):
            continue

        signal = agent.build_signal(row, {}, sizer)
        if signal is None:
            continue

        entry = (signal['entry_low'] + signal['entry_high']) / 2
        stop = signal['stop']
        tp1 = signal['tp1']
        rr1 = signal['rr1']

        if rr1 < MIN_RR:
            continue
        if abs(entry - stop) < 1e-10:
            continue

        outcome, hold_bars, exit_price = simulate_trade(k15, i, entry, stop, tp1)
        risk = abs(entry - stop)
        pnl_r = (exit_price - entry) / risk if agent_direction == 'LONG' else (entry - exit_price) / risk

        results.append({
            'symbol': symbol,
            'direction': agent_direction,
            'ts': int(k15[i][0]),
            'entry': entry,
            'stop': stop,
            'tp1': tp1,
            'rr1': rr1,
            'outcome': outcome,
            'hold_bars': hold_bars,
            'pnl_r': round(pnl_r, 4),
        })

    return results


def summarise(results: list[dict[str, Any]], label: str) -> dict[str, Any]:
    if not results:
        return {'label': label, 'signals': 0}
    n = len(results)
    wins = [r for r in results if r['outcome'] == 'TP1']
    losses = [r for r in results if r['outcome'] == 'SL']
    expired = [r for r in results if r['outcome'] == 'EXPIRED']
    pnl_rs = [r['pnl_r'] for r in results]
    winrate = len(wins) / n * 100
    expectancy = statistics.mean(pnl_rs) if pnl_rs else 0
    win_rs = [r['pnl_r'] for r in wins] or [0]
    loss_rs = [abs(r['pnl_r']) for r in losses] or [1]
    profit_factor = sum(win_rs) / max(sum(loss_rs), 1e-9)
    avg_hold = statistics.mean(r['hold_bars'] for r in results) if results else 0
    return {
        'label': label,
        'signals': n,
        'wins': len(wins),
        'losses': len(losses),
        'expired': len(expired),
        'winrate_pct': round(winrate, 1),
        'expectancy_R': round(expectancy, 3),
        'profit_factor': round(profit_factor, 2),
        'avg_hold_bars': round(avg_hold, 1),
    }


def print_summary(s):
    if s['signals'] == 0:
        print(f"  {s['label']}: no signals")
        return
    print(
        f"  {s['label']}: {s['signals']} signals | "
        f"WR={s['winrate_pct']}% | E={s['expectancy_R']}R | "
        f"PF={s['profit_factor']} | avg_hold={s['avg_hold_bars']}bars | "
        f"W/L/X={s['wins']}/{s['losses']}/{s['expired']}"
    )


def main():
    parser = argparse.ArgumentParser(description='Directional agent backtest')
    parser.add_argument('--days', type=int, default=LOOKBACK_DAYS_DEFAULT)
    parser.add_argument('--syms', nargs='+', default=DEFAULT_SYMBOLS)
    parser.add_argument('--json', type=str, default=None, help='Save results to JSON file')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    print(f'Backtest: {len(args.syms)} symbols x {args.days} days | min_rr={MIN_RR} | max_hold={MAX_HOLD_BARS} bars (15m)')
    print(f'Timestamp: {datetime.now(timezone.utc).isoformat()}')
    print()

    all_long, all_short = [], []
    sym_summaries = []

    for sym in args.syms:
        print(f'{sym}:')
        long_res = run_backtest_for_symbol(sym, args.days, 'LONG', verbose=args.verbose)
        short_res = run_backtest_for_symbol(sym, args.days, 'SHORT', verbose=args.verbose)

        if long_res is not None:
            all_long.extend(long_res)
            s = summarise(long_res, f'{sym} LONG')
            print_summary(s)
            sym_summaries.append(s)

        if short_res is not None:
            all_short.extend(short_res)
            s = summarise(short_res, f'{sym} SHORT')
            print_summary(s)
            sym_summaries.append(s)

    print()
    print('AGGREGATE:')
    print_summary(summarise(all_long, 'ALL LONG'))
    print_summary(summarise(all_short, 'ALL SHORT'))
    combined = all_long + all_short
    print_summary(summarise(combined, 'COMBINED'))

    if args.json:
        out = {
            'meta': {
                'symbols': args.syms,
                'lookback_days': args.days,
                'min_rr': MIN_RR,
                'max_hold_bars': MAX_HOLD_BARS,
                'run_at': datetime.now(timezone.utc).isoformat(),
            },
            'by_symbol': sym_summaries,
            'aggregate_long': summarise(all_long, 'ALL LONG'),
            'aggregate_short': summarise(all_short, 'ALL SHORT'),
            'aggregate_combined': summarise(combined, 'COMBINED'),
            'raw_signals': combined,
        }
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f'\nSaved to {args.json}')


if __name__ == '__main__':
    main()
