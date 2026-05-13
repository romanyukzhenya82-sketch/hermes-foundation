import deep_binance_analysis as m
import statistics

if __name__ == '__main__':
    tickers = m.get(f'{m.API_BASE}/fapi/v1/ticker/24hr')
    pairs = [t for t in tickers if t['symbol'].endswith('USDT') and 'DOWN' not in t['symbol'] and 'UP' not in t['symbol'] and float(t['quoteVolume']) > m.MIN_QUOTE_VOLUME and float(t['lastPrice']) > m.MIN_PRICE_USDT]
    pairs = sorted(pairs, key=lambda x: float(x['quoteVolume']), reverse=True)[:m.SCAN_LIMIT]
    print('pairs', len(pairs))
    rows = []
    for t in pairs:
        sym = t['symbol']
        price = float(t['lastPrice'])
        k15 = m.get(f'{m.API_BASE}/fapi/v1/klines', {'symbol': sym, 'interval': '15m', 'limit': 30})
        k60 = m.get(f'{m.API_BASE}/fapi/v1/klines', {'symbol': sym, 'interval': '1h', 'limit': 30})
        k240 = m.get(f'{m.API_BASE}/fapi/v1/klines', {'symbol': sym, 'interval': '4h', 'limit': 30})
        funding = m.get(f'{m.API_BASE}/fapi/v1/fundingRate', {'symbol': sym, 'limit': 3})
        depth = m.get(f'{m.API_BASE}/fapi/v1/depth', {'symbol': sym, 'limit': 20})
        close15 = [float(c[4]) for c in k15]
        close60 = [float(c[4]) for c in k60]
        close240 = [float(c[4]) for c in k240]
        vol15 = [float(c[5]) for c in k15]
        oi_info = m.get(f'{m.API_BASE}/fapi/v1/openInterest', {'symbol': sym})
        oi = float(oi_info.get('openInterest', 0))
        avg15 = statistics.mean(vol15[:-1]) if len(vol15) > 1 else vol15[-1]
        vol_spike = vol15[-1] / avg15 if avg15 else 1
        trend4 = m.trend_direction(k240)
        trend1 = m.trend_direction(k60)
        trend15 = m.trend_direction(k15)
        trend_match = len({trend4, trend1, trend15})
        rows.append((sym, float(t['quoteVolume']), vol_spike, oi * price, trend_match, trend4, trend1, trend15))
    print('filtered counts:')
    print('oi>=40M qv>=30M vol>=1.0 trend!=3', sum(1 for r in rows if r[1] >= m.MIN_QUOTE_VOLUME and r[2] >= m.MIN_VOL_SPIKE and r[3] >= m.MIN_OI_NOTIONAL and r[4] != 3))
    print('oi>=40M qv>=30M trend!=3', sum(1 for r in rows if r[1] >= m.MIN_QUOTE_VOLUME and r[3] >= m.MIN_OI_NOTIONAL and r[4] != 3))
    for r in rows[:80]:
        print(r)
