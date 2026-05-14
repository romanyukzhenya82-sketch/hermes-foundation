import requests
import statistics
from datetime import datetime, timezone

API = 'https://fapi.binance.com'


def fetch_klines(symbol, interval='15m', limit=500, end_time=None):
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    if end_time:
        params['endTime'] = int(end_time.timestamp() * 1000)
    r = requests.get(API + '/fapi/v1/klines', params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def detect_moonshots(symbol, vol_spike_min=3.0, max_price=5.0, lookahead=6, limit=1000):
    end = datetime.now(timezone.utc)
    klines = fetch_klines(symbol, '15m', limit=limit, end_time=end)
    vols = [float(k[5]) for k in klines]
    res = []
    for i in range(20, len(klines) - lookahead):
        prev_mean = statistics.mean(vols[max(0, i-20):i])
        if prev_mean == 0:
            continue
        spike = vols[i] / prev_mean
        price = float(klines[i][4])
        if spike >= vol_spike_min and price < max_price:
            future_prices = [float(k[4]) for k in klines[i+1:i+1+lookahead]]
            max_future = max(future_prices) if future_prices else price
            min_future = min(future_prices) if future_prices else price
            res.append({'time': klines[i][0], 'price': price, 'spike': spike, 'max_future': max_future, 'min_future': min_future})
    return res


def run_backtest(symbols, vol_spike_min=3.0, max_price=5.0, lookahead=6, win_multiple=5.0):
    summary = {}
    for s in symbols:
        try:
            hits = detect_moonshots(s, vol_spike_min=vol_spike_min, max_price=max_price, lookahead=lookahead)
            wins = sum(1 for h in hits if h['max_future'] >= h['price'] * win_multiple)
            summary[s] = {'signals': len(hits), f'wins_{int(win_multiple)}x': wins}
        except Exception as e:
            summary[s] = {'error': str(e)}
    return summary


if __name__ == '__main__':
    test_syms = ['DOGEUSDT', 'ZECUSDT', 'TRUMPUSDT', 'HYPEUSDT']
    out = run_backtest(test_syms)
    for k, v in out.items():
        print(k, v)
