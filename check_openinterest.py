import requests

resp = requests.get('https://fapi.binance.com/fapi/v1/ticker/24hr', timeout=10).json()
for t in resp[:10]:
    print(t['symbol'], 'openInterest' in t, t.get('openInterest', None), list(t.keys())[:12])
