import requests
import statistics
from datetime import datetime, timedelta

API = 'https://fapi.binance.com'


def fetch_klines(symbol, interval='15m', limit=500, end_time=None):
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    if end_time:
        params['endTime'] = int(end_time.timestamp() * 1000)
    r = requests.get(API + '/fapi/v1/klines', params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def detect_moonshots(symbol, lookback_days=7):
    end = datetime.utcnow()
    klines = fetch_klines(symbol, '15m', limit=1000, end_time=end)
    vols = [float(k[5]) for k in klines]
    res = []
    for i in range(20, len(klines)-6):
        prev_mean = statistics.mean(vols[max(0, i-20):i])
        if prev_mean == 0:
            continue
        spike = vols[i] / prev_mean
        price = float(klines[i][4])
        # detect moonshot-style spike
        if spike >= 3.0 and price < 5.0:
            # check next 6 candles for max
            future_prices = [float(k[4]) for k in klines[i+1:i+7]]
            max_future = max(future_prices) if future_prices else price
            min_future = min(future_prices) if future_prices else price
            res.append({'time': klines[i][0], 'price': price, 'spike': spike, 'max_future': max_future, 'min_future': min_future})
    return res


def run_backtest(symbols):
    summary = {}
    for s in symbols:
        try:
            hits = detect_moonshots(s)
            wins = sum(1 for h in hits if h['max_future'] >= h['price'] * 5)
            summary[s] = {'signals': len(hits), 'wins_5x': wins}
        except Exception as e:
            summary[s] = {'error': str(e)}
    return summary


if __name__ == '__main__':
    test_syms = ['DOGEUSDT', 'ZECUSDT', 'TRUMPUSDT', 'HYPEUSDT']
    out = run_backtest(test_syms)
    for k, v in out.items():
        print(k, v)
