import requests
import statistics
from datetime import datetime, timezone

API_BASE = 'https://fapi.binance.com'
DEPOSIT_USDT = 1000.0
RISK_PCT = 1.0
MAX_LEVERAGE = 10.0
MIN_QTY = 1


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


def swing_levels(candles):
    closes = [float(c[4]) for c in candles]
    highs = [float(c[2]) for c in candles]
    lows = [float(c[3]) for c in candles]
    last = closes[-1]
    high = max(highs[-8:])
    low = min(lows[-8:])
    pivot_high = highs[-5:]
    pivot_low = lows[-5:]
    return {
        'last': last,
        'high': high,
        'low': low,
        'range': high - low,
        'r1': lows[-4],
        's1': highs[-4],
        'latest_close': closes[-1],
        'prev_close': closes[-2],
    }


def orderbook_pressure(sym):
    depth = get(f'{API_BASE}/fapi/v1/depth', {'symbol': sym, 'limit': 20})
    bids = [(float(p), float(q)) for p, q in depth['bids'][:10]]
    asks = [(float(p), float(q)) for p, q in depth['asks'][:10]]
    bid_qty = sum(q for p, q in bids)
    ask_qty = sum(q for p, q in asks)
    return {
        'best_bid': bids[0][0],
        'best_ask': asks[0][0],
        'bid_qty': bid_qty,
        'ask_qty': ask_qty,
        'imbalance': ask_qty / bid_qty if bid_qty else float('inf'),
    }


def print_brief(symbol):
    funding = get(f'{API_BASE}/fapi/v1/fundingRate', {'symbol': symbol, 'limit': 3})
    oi_info = get(f'{API_BASE}/fapi/v1/openInterest', {'symbol': symbol})
    k15 = get(f'{API_BASE}/fapi/v1/klines', {'symbol': symbol, 'interval': '15m', 'limit': 30})
    k60 = get(f'{API_BASE}/fapi/v1/klines', {'symbol': symbol, 'interval': '1h', 'limit': 30})
    k240 = get(f'{API_BASE}/fapi/v1/klines', {'symbol': symbol, 'interval': '4h', 'limit': 30})
    price = float(k15[-1][4])
    last_15m = int(k15[-1][0])
    trend_4h = 'bullish' if float(k240[-1][4]) > float(k240[0][1]) else 'bearish'
    trend_1h = 'bullish' if float(k60[-1][4]) > float(k60[0][1]) else 'bearish'
    trend_15m = 'bullish' if float(k15[-1][4]) > float(k15[0][1]) else 'bearish'
    s4h = swing_levels(k240)
    s1h = swing_levels(k60)
    s15 = swing_levels(k15)
    book = orderbook_pressure(symbol)
    funding_rate = float(funding[-1]['fundingRate']) if funding else 0.0
    oi = float(oi_info.get('openInterest', 0))
    print('---')
    print(f'PAIR: {symbol}')
    print(f'PRICE: {price:.6f}')
    print(f'TRENDS: 4h={trend_4h} 1h={trend_1h} 15m={trend_15m}')
    print(f"4h RANGE: {s4h['low']:.6f} - {s4h['high']:.6f} ({s4h['range']:.6f})")
    print(f"1h RANGE: {s1h['low']:.6f} - {s1h['high']:.6f} ({s1h['range']:.6f})")
    print(f"15m RANGE: {s15['low']:.6f} - {s15['high']:.6f} ({s15['range']:.6f})")
    print(f'ATR: 4h={atr(k240):.6f} 1h={atr(k60):.6f} 15m={atr(k15):.6f}')
    print(f'FUNDING: {funding_rate:.6f}  OI: {oi:.0f}')
    print(f"ORDERBOOK: bid={book['best_bid']:.6f} ask={book['best_ask']:.6f} imbalance={book['imbalance']:.2f}")
    print(f'15m last candle UTC: {datetime.fromtimestamp(last_15m/1000, timezone.utc).isoformat()}')
    print('TRADE IDEA:')
    support_zone = max(s15['low'], s1h['low'])
    resistance_zone = min(s15['high'], s1h['high'])
    entry_zone_low = support_zone + atr(k15) * 0.2
    entry_zone_high = support_zone + atr(k15) * 0.5
    if trend_4h == 'bullish' and trend_1h == 'bullish' and trend_15m == 'bullish':
        if price > entry_zone_high:
            print('  No clean long entry: price is too far from the support control zone.')
            print(f'  Watch: support {support_zone:.6f}, pullback zone {entry_zone_low:.6f}-{entry_zone_high:.6f}')
        else:
            entry = max(price, entry_zone_low)
            stop = support_zone - atr(k15) * 0.4
            if stop < 0:
                stop = support_zone - atr(k15) * 0.2
            risk = entry - stop
            risk_amount = DEPOSIT_USDT * RISK_PCT / 100.0
            qty = int(risk_amount / risk) if risk > 0 else 0
            if qty < MIN_QTY:
                qty = 0
            notional = qty * entry
            margin = notional / MAX_LEVERAGE if qty > 0 else 0.0
            target = entry + risk * 1.5
            print('  Direction: LONG')
            print(f'  Entry: {entry:.6f}')
            print(f'  Stop: {stop:.6f}')
            print(f'  Target: {target:.6f}')
            print(f'  Risk: {risk:.6f}  RR ~1.5')
            print(f'  Risk per trade: {risk_amount:.2f} USDT ({RISK_PCT:.1f}% депо)')
            if qty == 0:
                print('  Position size below minimum; лучше ждать более близкий вход или меньший стоп.')
            else:
                print(f'  Qty: {qty} контрактов / Notional: {notional:.2f} USDT')
                print(f'  Margin @ {MAX_LEVERAGE:.0f}x: {margin:.2f} USDT')
    elif trend_4h == 'bullish' and trend_1h == 'bullish' and trend_15m == 'bearish':
        support = support_zone
        print('  Direction: BULLISH WATCH (pullback)')
        print(f'  Wait for a controlled dip to support near {support:.6f}')
        print(f'  Prefer long only if 15m candles hold above support and volume/flow confirm')
        print(f'  Stop: below {support - atr(k15) * 0.4:.6f}')
    else:
        print('  No clean same-direction multi-timeframe edge; keep pair on watchlist or trade only with very tight risk.')
    print('  Sources: Binance /fapi/v1/klines 15m/1h/4h, /fapi/v1/fundingRate, /fapi/v1/openInterest, /fapi/v1/depth')
    print('')


def main():
    print('TIME', datetime.now(timezone.utc).isoformat())
    print('SOURCE: Binance Futures API')
    for symbol in ['SAGAUSDT', 'XRPUSDT']:
        print_brief(symbol)

if __name__ == '__main__':
    main()
