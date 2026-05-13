import csv
from backtest_moonshot import run_backtest_for_symbol
from deep_binance_analysis import scan_market


def sweep(vol_spike_values=(2.0, 3.0, 4.0), lookahead=(6, 12)):
    rows = scan_market()
    symbols = [r['symbol'] for r in rows]
    results = []
    for sym in symbols:
        for vs in vol_spike_values:
            for la in lookahead:
                stats = run_backtest_for_symbol(sym, vol_spike_threshold=vs, lookahead_candles=la)
                results.append({'symbol': sym, 'vol_spike': vs, 'lookahead': la, **(stats or {})})
    return results


def save_csv(results, out='moonshot_sweep.csv'):
    if not results:
        return
    keys = sorted(results[0].keys())
    with open(out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in results:
            writer.writerow(r)


if __name__ == '__main__':
    res = sweep()
    save_csv(res)
    print('Sweep done. Results saved to moonshot_sweep.csv')