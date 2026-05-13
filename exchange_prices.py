import requests


def safe_get(url, params=None, timeout=6):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def get_binance_price(symbol):
    data = safe_get('https://api.binance.com/api/v3/ticker/price', {'symbol': symbol})
    if not data:
        return None
    try:
        return float(data.get('price'))
    except Exception:
        return None


def get_bybit_price(symbol):
    # Bybit public tickers v2
    data = safe_get('https://api.bybit.com/v2/public/tickers', {'symbol': symbol})
    if not data or 'result' not in data:
        return None
    res = data.get('result')
    if isinstance(res, list) and res:
        try:
            return float(res[0].get('last_price'))
        except Exception:
            return None
    return None


def get_mexc_price(symbol):
    # MEXC public API
    data = safe_get('https://www.mexc.com/api/v3/ticker/price', {'symbol': symbol})
    if not data:
        return None
    try:
        return float(data.get('price'))
    except Exception:
        return None


def get_price(exchange, symbol):
    exchange = exchange.lower()
    if exchange == 'binance':
        return get_binance_price(symbol)
    if exchange == 'bybit':
        return get_bybit_price(symbol)
    if exchange == 'mexc':
        return get_mexc_price(symbol)
    return None


def get_order_book(exchange, symbol, limit=50):
    """Return order book levels for the given exchange and symbol.

    Returns dict: {'bids': [(price, qty), ...], 'asks': [(price, qty), ...]} or None
    """
    exchange = (exchange or '').lower()
    try:
        if exchange == 'binance':
            data = safe_get('https://api.binance.com/api/v3/depth', {'symbol': symbol, 'limit': limit})
            if not data:
                return None
            bids = [(float(p), float(q)) for p, q in data.get('bids', [])]
            asks = [(float(p), float(q)) for p, q in data.get('asks', [])]
            return {'bids': bids, 'asks': asks}
        # For other exchanges, best-effort: try fetching a simple ticker/orderbook endpoint
        if exchange == 'bybit':
            data = safe_get('https://api.bybit.com/v2/public/orderBook/L2', {'symbol': symbol})
            # Bybit L2 returns list-like; fallback to None for now
            return None
        if exchange == 'mexc':
            data = safe_get('https://www.mexc.com/api/v3/depth', {'symbol': symbol, 'limit': limit})
            if not data:
                return None
            bids = [(float(p), float(q)) for p, q in data.get('bids', [])]
            asks = [(float(p), float(q)) for p, q in data.get('asks', [])]
            return {'bids': bids, 'asks': asks}
    except Exception:
        return None
    return None


def estimate_slippage(levels, qty_needed, reference_price=None):
    """Estimate slippage (as fraction of reference_price) to fill qty_needed using given book levels.

    levels: list of (price, qty) ordered from best->worse for the side being taken.
    reference_price: mid or top-of-book price to normalise slippage. If None, uses first level price.
    Returns slippage_pct (float) or None if insufficient depth.
    """
    if not levels or qty_needed <= 0:
        return 0.0
    remaining = qty_needed
    accum_cost = 0.0
    accum_qty = 0.0
    for price, q in levels:
        take = min(remaining, q)
        accum_cost += take * price
        accum_qty += take
        remaining -= take
        if remaining <= 1e-12:
            break
    if remaining > 1e-6:
        # insufficient depth
        return None
    avg_price = accum_cost / accum_qty if accum_qty > 0 else None
    if avg_price is None:
        return None
    ref = reference_price or levels[0][0]
    if ref == 0:
        return None
    return (avg_price - ref) / ref
