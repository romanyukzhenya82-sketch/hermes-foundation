import requests
import statistics
from datetime import datetime, timezone


def get(url, params=None):
    return requests.get(url, params=params, timeout=10).json()


def atr(candles):
    return statistics.mean(
        [
            max(
                float(h) - float(l),
                abs(float(h) - float(c)),
                abs(float(l) - float(c)),
            )
            for _, o, h, l, c, *_ in candles
        ]
    )


tickers = get('https://fapi.binance.com/fapi/v1/ticker/24hr')
usdt = [t for t in tickers if t['symbol'].endswith('USDT')]
top = sorted(usdt, key=lambda x: float(x['quoteVolume']), reverse=True)[:12]

print('TIME', datetime.now(timezone.utc).isoformat())
print('PAIR,PRICE,15mΔ%,1hΔ%,VOL_SPIKE,ATR15,FUNDING,LAST_FUND_TIME,TREND,COMMENT')
for t in top:
    sym = t['symbol']
    price = float(t['lastPrice'])
    k15 = get('https://fapi.binance.com/fapi/v1/klines', {'symbol': sym, 'interval': '15m', 'limit': 20})
    funding = get('https://fapi.binance.com/fapi/v1/fundingRate', {'symbol': sym, 'limit': 3})
    close15 = [float(c[4]) for c in k15]
    vol15 = [float(c[5]) for c in k15]
    pct15 = 100 * (close15[-1] / close15[-2] - 1) if len(close15) > 1 else 0
    pct1h = 100 * (close15[-1] / close15[-4] - 1) if len(close15) > 4 else 0
    avg15 = statistics.mean(vol15[:-1]) if len(vol15) > 1 else vol15[-1]
    spike = vol15[-1] / avg15 if avg15 else 1
    trend = 'bullish' if close15[-1] > close15[0] else 'bearish'
    fund = funding[-1]['fundingRate'] if funding else None
    fund_time = funding[-1]['fundingTime'] if funding else None
    mode = 'flow' if spike > 1.5 else 'watch'
    print(
        f'{sym},{price:.4f},{pct15:.2f},{pct1h:.2f},{spike:.2f},{atr(k15):.4f},{fund},{fund_time},{trend},{mode}'
    )
