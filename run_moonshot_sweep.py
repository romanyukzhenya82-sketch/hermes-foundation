import csv
from backtest_moonshot import run_backtest
from deep_binance_analysis import scan_market


def sweep(symbols=None, vol_spike_values=(2.0, 3.0, 4.0), lookahead_values=(6, 12, 24, 96), max_symbols=3):
    if symbols is None:
        rows = scan_market()
        symbols = [r['symbol'] for r in rows][:max_symbols]
    results = []
    for sym in symbols:
        for vs in vol_spike_values:
            for la in lookahead_values:
                stats = run_backtest([sym], vol_spike_min=vs, lookahead=la)
                entry = stats.get(sym, {}) if isinstance(stats, dict) else {}
                # normalise key for csv output regardless of win_multiple
                wins_key = next((k for k in entry if k.startswith('wins_')), None)
                wins = entry.get(wins_key, 0) if wins_key else 0
                results.append({
                    'symbol': sym,
                    'vol_spike': vs,
                    'lookahead': la,
                    'signals': entry.get('signals', 0),
                    'wins_5x': wins,
                    'error': entry.get('error', ''),
                })
    return results


def save_csv(results, out='moonshot_sweep.csv'):
    if not results:
        return
    keys = ['symbol', 'vol_spike', 'lookahead', 'signals', 'wins_5x', 'error']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in results:
            writer.writerow(r)


if __name__ == '__main__':
    res = sweep()
    save_csv(res)
    print('Sweep done. Results saved to moonshot_sweep.csv')