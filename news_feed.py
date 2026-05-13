import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


RSS_SOURCES = [
    'https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml',
]


def fetch_rss(url, limit=5):
    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall('.//item')[:limit]:
            title = item.findtext('title') or ''
            link = item.findtext('link') or ''
            pub = item.findtext('pubDate') or ''
            items.append({'title': title, 'link': link, 'pubDate': pub})
        return items
    except Exception:
        return []


def fetch_news(limit_per_source=3):
    out = []
    for src in RSS_SOURCES:
        out.extend(fetch_rss(src, limit=limit_per_source))
    return out


KEYWORDS = ('BTC', 'Bitcoin', 'ETH', 'Ethereum', 'halving', 'regulation', 'ETF', 'CME')


def extract_relevant_events(news_items, keywords=KEYWORDS):
    events = []
    for n in news_items:
        t = n.get('title', '')
        for kw in keywords:
            if kw.lower() in t.lower():
                events.append({'title': t, 'link': n.get('link', ''), 'kw': kw})
                break
    return events


def top_events_summary(limit=3):
    news = fetch_news(limit_per_source=5)
    events = extract_relevant_events(news)
    return events[:limit]


if __name__ == '__main__':
    for e in top_events_summary():
        print(e)
