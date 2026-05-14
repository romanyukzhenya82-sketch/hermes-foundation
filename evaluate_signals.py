"""
Оценщик сигналов по signals_log.jsonl.

Для каждой записи с outcome=None догоняет цену через 1h/4h/24h по Binance fapi klines,
определяет исход (HIT_TP1, HIT_TP2, HIT_SL, OPEN) и записывает обратно.
Затем выводит сводную таблицу: winrate, expectancy, profit_factor по direction/regime/category.

Запуск:
  python evaluate_signals.py                  # обработать все незакрытые
  python evaluate_signals.py --lookback 7     # только записи за последние 7 дней
  python evaluate_signals.py --dry-run        # только вывод, без перезаписи файла
"""

import argparse
import json
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

API = 'https://fapi.binance.com'
SIGNALS_LOG = Path(__file__).parent / 'signals_log.jsonl'
METRICS_HISTORY = Path(__file__).parent / 'metrics_history.jsonl'
CLOSE_HORIZON_HOURS = 24


def safe_get(url, params=None, timeout=12):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def fetch_klines_after(symbol, start_ts_ms, limit=200):
    """Загружает klines 15m начиная с start_ts_ms + 1."""
    data = safe_get(f'{API}/fapi/v1/klines', {
        'symbol': symbol,
        'interval': '15m',
        'startTime': start_ts_ms + 1,
        'limit': limit,
    })
    return data or []


def determine_outcome(signal, klines):
    """
    Проходит по свечам после сигнала и определяет первый выход.
    Возвращает (outcome, exit_price, bars_held).
    """
    entry = signal.get('entry')
    stop = signal.get('stop')
    tp1 = signal.get('tp1')
    tp2 = signal.get('tp2')
    direction = signal.get('direction', '')

    if entry is None or stop is None or tp1 is None:
        return 'DATA_ERROR', None, 0

    is_long = direction in ('LONG', 'SPOT_LONG')
    is_short = direction == 'SHORT'
    if not is_long and not is_short:
        return 'UNKNOWN_DIR', None, 0

    for i, k in enumerate(klines):
        high = float(k[2])
        low = float(k[3])
        close = float(k[4])

        if is_long:
            if low <= stop:
                return 'HIT_SL', stop, i + 1
            if tp2 and high >= tp2:
                return 'HIT_TP2', tp2, i + 1
            if high >= tp1:
                return 'HIT_TP1', tp1, i + 1
        elif is_short:
            if high >= stop:
                return 'HIT_SL', stop, i + 1
            if tp2 and low <= tp2:
                return 'HIT_TP2', tp2, i + 1
            if low <= tp1:
                return 'HIT_TP1', tp1, i + 1

    # не закрылось в пределах klines: последняя цена
    if klines:
        return 'EXPIRED', float(klines[-1][4]), len(klines)
    return 'OPEN', None, 0


def ts_to_ms(ts_str):
    """ISO timestamp → milliseconds."""
    dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    return int(dt.timestamp() * 1000)


def load_log():
    if not SIGNALS_LOG.exists():
        return []
    with open(SIGNALS_LOG, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def save_log(records):
    with open(SIGNALS_LOG, 'w', encoding='utf-8') as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def pnl_r(signal, exit_price):
    """Возвращает P&L в единицах R (риск = 1R = |entry - stop|)."""
    entry = signal.get('entry', 0)
    stop = signal.get('stop', 0)
    risk = abs(entry - stop)
    if risk < 1e-10:
        return 0.0
    direction = signal.get('direction', '')
    if direction in ('LONG', 'SPOT_LONG'):
        return (exit_price - entry) / risk
    elif direction == 'SHORT':
        return (entry - exit_price) / risk
    return 0.0


def evaluate(records, dry_run=False, lookback_days=None, min_closed_age_hours=1):
    """Обновляет outcome для незакрытых записей."""
    now = datetime.now(timezone.utc)
    cutoff_ms = int((now - timedelta(days=lookback_days)).timestamp() * 1000) if lookback_days else None
    horizon_bars = CLOSE_HORIZON_HOURS * 4  # 15m → bars per hour = 4

    updated = 0
    for rec in records:
        # skip already closed
        if rec.get('outcome') and rec['outcome'] not in ('OPEN', None):
            continue
        ts_ms = ts_to_ms(rec['ts'])
        # skip too recent — wait at least min_closed_age_hours
        if (now.timestamp() * 1000 - ts_ms) < min_closed_age_hours * 3600 * 1000:
            continue
        if cutoff_ms and ts_ms < cutoff_ms:
            continue

        sym = rec.get('symbol')
        if not sym:
            continue

        klines = fetch_klines_after(sym, ts_ms, limit=horizon_bars)
        if not klines:
            continue

        outcome, exit_price, bars = determine_outcome(rec, klines)
        if outcome == 'OPEN':
            continue

        rec['outcome'] = outcome
        rec['exit_price'] = exit_price
        rec['bars_held'] = bars
        rec['pnl_r'] = round(pnl_r(rec, exit_price) if exit_price else 0, 4) if exit_price else None
        rec['evaluated_at'] = now.isoformat()
        updated += 1
        print(f"  {rec['symbol']} {rec['direction']} {rec['ts'][:16]} -> {outcome} pnl={rec['pnl_r']}R")

    if not dry_run and updated:
        save_log(records)
        print(f'\n[signals_log] Updated {updated} records.')
    elif dry_run:
        print(f'\n[dry-run] Would update {updated} records.')
    return records


def group_by(records, key):
    groups = {}
    for r in records:
        k = r.get(key, 'unknown')
        groups.setdefault(k, []).append(r)
    return groups


def summarise_group(label, recs):
    closed = [r for r in recs if r.get('outcome') and r['outcome'] not in ('OPEN', None, 'DATA_ERROR', 'UNKNOWN_DIR')]
    if not closed:
        return None
    pnls = [r['pnl_r'] for r in closed if r.get('pnl_r') is not None]
    if not pnls:
        return None
    wins = [p for p in pnls if p > 0]
    losses = [abs(p) for p in pnls if p < 0]
    winrate = len(wins) / len(pnls) * 100
    expectancy = statistics.mean(pnls)
    pf = sum(wins) / max(sum(losses), 1e-9)
    tp1_hits = sum(1 for r in closed if r['outcome'] in ('HIT_TP1', 'HIT_TP2'))
    sl_hits = sum(1 for r in closed if r['outcome'] == 'HIT_SL')
    expired = sum(1 for r in closed if r['outcome'] == 'EXPIRED')
    avg_hold = statistics.mean(r.get('bars_held', 0) for r in closed)
    return {
        'label': label,
        'total': len(recs),
        'closed': len(closed),
        'open': len(recs) - len(closed),
        'winrate_pct': round(winrate, 1),
        'expectancy_R': round(expectancy, 3),
        'profit_factor': round(pf, 2),
        'tp1_hits': tp1_hits,
        'sl_hits': sl_hits,
        'expired': expired,
        'avg_hold_bars': round(avg_hold, 1),
    }


def print_table(rows):
    if not rows:
        print('  No closed signals to report.')
        return
    header = f"{'Label':<30} {'Total':>6} {'Closed':>7} {'WR%':>6} {'E(R)':>7} {'PF':>5} {'TP1':>5} {'SL':>5} {'Exp':>5} {'Hold':>6}"
    print(header)
    print('-' * len(header))
    for r in rows:
        print(
            f"{r['label']:<30} {r['total']:>6} {r['closed']:>7} {r['winrate_pct']:>6.1f} "
            f"{r['expectancy_R']:>7.3f} {r['profit_factor']:>5.2f} {r['tp1_hits']:>5} {r['sl_hits']:>5} "
            f"{r['expired']:>5} {r['avg_hold_bars']:>6.1f}"
        )


def save_metrics_snapshot(records: list[dict]) -> dict | None:
    closed = [r for r in records if r.get('outcome') and r['outcome'] not in ('OPEN', None, 'DATA_ERROR', 'UNKNOWN_DIR')]
    if not closed:
        return None
    overall = summarise_group('', closed)
    if not overall:
        return None

    regimes = [r.get('regime', 'unknown') for r in closed if r.get('regime')]
    top_regime = max(set(regimes), key=regimes.count) if regimes else 'unknown'

    snapshot = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'regime': top_regime,
        'total_signals': overall['total'],
        'closed': overall['closed'],
        'open': overall['open'],
        'winrate_pct': overall['winrate_pct'],
        'expectancy_R': overall['expectancy_R'],
        'profit_factor': overall['profit_factor'],
        'avg_hold_bars': overall['avg_hold_bars'],
    }
    try:
        with open(METRICS_HISTORY, 'a', encoding='utf-8') as f:
            f.write(json.dumps(snapshot, ensure_ascii=False) + '\n')
    except Exception as exc:
        print(f'[metrics_history] write error: {exc}')
    return snapshot


def load_metrics_history(limit: int = 30) -> list[dict]:
    if not METRICS_HISTORY.exists():
        return []
    with open(METRICS_HISTORY, 'r', encoding='utf-8') as f:
        lines = [line for line in f if line.strip()]
    result = [json.loads(line) for line in lines[-limit:]]
    return result


def print_trend(limit: int = 14) -> None:
    snapshots = load_metrics_history(limit=limit)
    if not snapshots:
        print('  No metrics history.')
        return
    print(f'  Metrics trend (last {len(snapshots)} snapshots):')
    print(f"  {'Date':<18} {'WR%':>6} {'E(R)':>7} {'PF':>5} {'Hold':>5} {'Regime'}")
    print(f"  {'-'*56}")
    for s in snapshots:
        dt = s.get('ts', '')[:13]
        wr = s.get('winrate_pct', 0)
        er = s.get('expectancy_R', 0)
        pf = s.get('profit_factor', 0)
        hold = s.get('avg_hold_bars', 0)
        regime = s.get('regime', '?')[:16]
        print(f"  {dt:<18} {wr:>6.1f} {er:>7.3f} {pf:>5.2f} {hold:>5.1f} {regime}")


def main():
    parser = argparse.ArgumentParser(description='Evaluate signals from signals_log.jsonl')
    parser.add_argument('--lookback', type=int, default=None, help='Only evaluate signals from last N days')
    parser.add_argument('--dry-run', action='store_true', help='Do not update the log file')
    parser.add_argument('--skip-fetch', action='store_true', help='Skip fetching new outcomes (only show stats)')
    parser.add_argument('--auto', action='store_true', help='Auto mode: evaluate + save metrics snapshot')
    parser.add_argument('--trend', type=int, nargs='?', const=14, default=None, help='Show metrics trend (last N snapshots)')
    args = parser.parse_args()

    if args.trend:
        print_trend(limit=args.trend)
        return

    records = load_log()
    if not records:
        print('signals_log.jsonl is empty or missing.')
        return

    if not args.skip_fetch:
        records = evaluate(records, dry_run=args.dry_run, lookback_days=args.lookback)

    if args.auto:
        snapshot = save_metrics_snapshot(records)
        if snapshot:
            gate = snapshot['winrate_pct'] >= 52 and snapshot['expectancy_R'] > 0 if snapshot['closed'] >= 20 else None
            gate_str = f" | GATE={'PASS' if gate else 'FAIL'}" if gate is not None else ''
            print(f"[auto] WR={snapshot['winrate_pct']}% E={snapshot['expectancy_R']}R PF={snapshot['profit_factor']} closed={snapshot['closed']}{gate_str}")
        else:
            print('[auto] no closed signals to evaluate')
        return

    if args.lookback:
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.lookback)
        records = [r for r in records if datetime.fromisoformat(r['ts'].replace('Z', '+00:00')) >= cutoff]

    closed = [r for r in records if r.get('outcome') and r['outcome'] not in ('OPEN', None, 'DATA_ERROR', 'UNKNOWN_DIR')]
    print(f'\nStats window: {len(records)} signals, {len(closed)} closed\n')

    rows = []
    for label, group in group_by(closed, 'direction').items():
        s = summarise_group(label, group)
        if s:
            rows.append(s)
    for label, group in group_by(closed, 'regime').items():
        s = summarise_group(f'regime:{label}', group)
        if s:
            rows.append(s)
    s = summarise_group('OVERALL', closed)
    if s:
        rows.append(s)

    rows.sort(key=lambda x: x['label'])
    print_table(rows)

    overall = summarise_group('OVERALL', closed)
    if overall and overall['closed'] >= 20:
        print()
        wr = overall['winrate_pct']
        exp = overall['expectancy_R']
        gate = wr >= 52 and exp > 0
        print(f"GATE CHECK (>=20 signals): WR={wr}% E={exp}R → {'PASS ✓' if gate else 'FAIL ✗ — tune before release'}")


if __name__ == '__main__':
    main()
