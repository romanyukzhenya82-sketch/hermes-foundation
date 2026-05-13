import math
from datetime import datetime, timezone

from deep_binance_analysis import get_macro_context, scan_market
from exchange_prices import get_price, get_order_book, estimate_slippage
from options_data import get_options_iv

DEFAULT_ACCOUNT_USDT = 10_000
DEFAULT_RISK_PCT = 0.01
DEFAULT_LEVERAGE = 8
MAX_PRIORITIES = 8
MAX_CANDIDATES = 15


class MacroContext:
    def __init__(self, rows):
        self.btc = next((row for row in rows if row['symbol'] == 'BTCUSDT'), None)
        self.eth = next((row for row in rows if row['symbol'] == 'ETHUSDT'), None)
        self.regime = self._build_regime()
        self.summary_text = self._build_summary()

    def _build_regime(self):
        bulls = sum(1 for asset in (self.btc, self.eth) if asset and asset['trend_4h'] == 'bullish')
        bears = sum(1 for asset in (self.btc, self.eth) if asset and asset['trend_4h'] == 'bearish')
        if bulls == 2:
            return 'trend / risk-on'
        if bears == 2:
            return 'trend / risk-off'
        if self.btc and self.eth:
            if abs(self.btc['pct4h']) < 0.5 and abs(self.eth['pct4h']) < 0.5:
                return 'flat / low-volatility'
            return 'mixed / rotation'
        return 'unknown'

    def _build_summary(self):
        parts = ['Macro context:']
        if self.btc:
            parts.append(
                f"BTC 4h={self.btc['trend_4h']} {self.btc['pct4h']:+.2f}% | OI={self.btc['oi_notional'] / 1e6:.1f}M"
            )
        if self.eth:
            parts.append(
                f"ETH 4h={self.eth['trend_4h']} {self.eth['pct4h']:+.2f}% | OI={self.eth['oi_notional'] / 1e6:.1f}M"
            )
        parts.append(f"Regime: {self.regime}")
        return ' | '.join(parts)


class PositionSizer:
    def __init__(self, account_usdt=DEFAULT_ACCOUNT_USDT, risk_pct=DEFAULT_RISK_PCT, leverage=DEFAULT_LEVERAGE):
        self.account_usdt = account_usdt
        self.risk_pct = risk_pct
        self.leverage = leverage

    def size(self, entry, stop):
        risk_per_contract = abs(entry - stop)
        risk_amount = self.account_usdt * self.risk_pct
        if risk_per_contract <= 0:
            return None

        qty = risk_amount / risk_per_contract
        max_notional = self.account_usdt * self.leverage
        notional = qty * entry
        capped = False
        if notional > max_notional:
            capped = True
            qty = max_notional / entry
            notional = qty * entry

        return {
            'qty': round(qty, 4),
            'risk_amount': round(risk_amount, 2),
            'position_notional': round(notional, 2),
            'max_notional': round(max_notional, 2),
            'risk_per_contract': round(risk_per_contract, 6),
            'formula': f"qty = {risk_amount:.0f} / |entry - stop|",
            'capped_by_leverage': capped,
        }


class BaseDirectionalAgent:
    name = 'base'
    direction = None

    def matches(self, row):
        raise NotImplementedError

    def build_signal(self, row, macro, sizer):
        raise NotImplementedError

    def evaluate(self, rows, macro, account_usdt=DEFAULT_ACCOUNT_USDT):
        top_rows = rows[:MAX_CANDIDATES]
        filtered = [row for row in top_rows if self.matches(row)]
        signals = []
        sizer = PositionSizer(account_usdt=account_usdt)
        for row in filtered[:MAX_PRIORITIES]:
            signal = self.build_signal(row, macro, sizer)
            if signal:
                signals.append(signal)
        return signals

    def format_signal(self, signal):
        if signal is None:
            return None
        lines = [
            f"{signal['symbol']} | {signal['direction']} | score={signal['score']:.1f} | category={signal['category']}"
            f" | mode={signal['mode']} | leverage={signal['leverage']}x",
            f"Entry zone: {signal['entry_low']:.6f} - {signal['entry_high']:.6f}",
            f"Stop: {signal['stop']:.6f} | TP1: {signal['tp1']:.6f} | TP2: {signal['tp2']:.6f}",
            f"R:R: {signal['rr1']:.2f} / {signal['rr2']:.2f} | hold: {signal['holding']} | cancel: {signal['cancel_condition']}",
            f"Size: {signal['qty']} contracts | notional={signal['notional']:.2f} USDT | risk={signal['risk_amount']:.0f} USDT",
            f"Formula: {signal['size_formula']} | {signal['risk_note']}",
            f"Reason: {signal['reason']}"
        ]
        return '\n'.join(lines)


class LongAgent(BaseDirectionalAgent):
    name = 'long'
    direction = 'LONG'

    def matches(self, row):
        bull_count = sum(1 for trend in [row['trend_4h'], row['trend_1h'], row['trend_15m']] if trend == 'bullish')
        return (
            bull_count >= 2
            and row['trend_4h'] == 'bullish'
            and row['oi_notional'] >= 45_000_000
            and row['vol_spike'] >= 1.1
            and row['spread_pct'] < 0.003
        )

    def build_signal(self, row, macro, sizer):
        support = max(row['support_15m'], row['support_1h'])
        atr = row['atr15']
        entry_low = support + atr * 0.15
        entry_high = support + atr * 0.45
        entry = min(max(row['price'], entry_low), entry_high)
        stop = support - atr * 0.35
        tp1 = entry + max(atr * 2.0, (entry - stop) * 1.6)
        tp2 = entry + max(atr * 3.0, (entry - stop) * 2.5)
        rr1 = (tp1 - entry) / (entry - stop) if entry > stop else 0
        rr2 = (tp2 - entry) / (entry - stop) if entry > stop else 0
        sizing = sizer.size(entry, stop)
        risk_note = 'normal risk' if sizing and sizing['risk_amount'] <= sizer.account_usdt * 0.02 else 'aggressive, consider lower risk' if sizing else 'invalid sizing'
        if rr1 < 1.5:
            risk_note = 'low R:R, wait for cleaner structure or smaller position'

        return {
            'symbol': row['symbol'],
            'category': row['category'],
            'direction': self.direction,
            'score': row['score'],
            'mode': 'futures',
            'leverage': sizer.leverage,
            'entry_low': entry_low,
            'entry_high': entry_high,
            'stop': stop,
            'tp1': tp1,
            'tp2': tp2,
            'rr1': rr1,
            'rr2': rr2,
            'qty': sizing['qty'] if sizing else 0,
            'notional': sizing['position_notional'] if sizing else 0,
            'risk_amount': sizing['risk_amount'] if sizing else 0,
            'size_formula': sizing['formula'] if sizing else '',
            'risk_note': risk_note,
            'holding': '15m-1h structure, intra-day/swing',
            'cancel_condition': 'close below 1h support or macro risk-off',
            'reason': 'trend alignment, liquidity, funding and capital flow',
        }


class ShortAgent(BaseDirectionalAgent):
    name = 'short'
    direction = 'SHORT'

    def matches(self, row):
        bear_count = sum(1 for trend in [row['trend_4h'], row['trend_1h'], row['trend_15m']] if trend == 'bearish')
        return (
            bear_count >= 2
            and row['trend_4h'] == 'bearish'
            and row['oi_notional'] >= 40_000_000
            and row['vol_spike'] >= 1.1
            and row['spread_pct'] < 0.003
        )

    def build_signal(self, row, macro, sizer):
        resistance = min(row['resistance_15m'], row['resistance_1h'])
        atr = row['atr15']
        entry_high = resistance - atr * 0.15
        entry_low = resistance - atr * 0.45
        entry = max(min(row['price'], entry_high), entry_low)
        stop = resistance + atr * 0.35
        tp1 = entry - max(atr * 2.0, (stop - entry) * 1.6)
        tp2 = entry - max(atr * 3.0, (stop - entry) * 2.5)
        rr1 = (entry - tp1) / (stop - entry) if stop > entry else 0
        rr2 = (entry - tp2) / (stop - entry) if stop > entry else 0
        sizing = sizer.size(entry, stop)
        risk_note = 'normal risk' if sizing and sizing['risk_amount'] <= sizer.account_usdt * 0.02 else 'aggressive, consider lower risk' if sizing else 'invalid sizing'
        if rr1 < 1.5:
            risk_note = 'low R:R, wait for cleaner structure or smaller position'

        return {
            'symbol': row['symbol'],
            'category': row['category'],
            'direction': self.direction,
            'score': row['score'],
            'mode': 'futures',
            'leverage': sizer.leverage,
            'entry_low': entry_low,
            'entry_high': entry_high,
            'stop': stop,
            'tp1': tp1,
            'tp2': tp2,
            'rr1': rr1,
            'rr2': rr2,
            'qty': sizing['qty'] if sizing else 0,
            'notional': sizing['position_notional'] if sizing else 0,
            'risk_amount': sizing['risk_amount'] if sizing else 0,
            'size_formula': sizing['formula'] if sizing else '',
            'risk_note': risk_note,
            'holding': '15m-1h structure, intra-day/swing',
            'cancel_condition': 'close above 1h resistance or macro risk-on',
            'reason': 'trend alignment, liquidity, funding and capital flow',
        }


class SpotAgent(BaseDirectionalAgent):
    name = 'spot'
    direction = 'LONG_SPOT'

    def matches(self, row):
        # simple spot candidate: strong 4h trend + good volume
        return row['trend_4h'] == 'bullish' and row['quote_volume'] > 50_000_000 and row['spread_pct'] < 0.002

    def build_signal(self, row, macro, sizer):
        # spot sizing uses no leverage and smaller risk per trade
        entry = row['price']
        stop = entry - row['atr15'] * 1.0
        tp1 = entry + row['atr15'] * 1.8
        sizing = sizer.__class__(account_usdt=sizer.account_usdt, risk_pct=0.005, leverage=1).size(entry, stop)
        return {
            'symbol': row['symbol'],
            'category': row['category'],
            'direction': 'SPOT_LONG',
            'score': row['score'],
            'mode': 'spot',
            'leverage': 1,
            'entry_low': entry,
            'entry_high': entry,
            'stop': stop,
            'tp1': tp1,
            'tp2': tp1 * 1.02,
            'rr1': (tp1 - entry) / (entry - stop) if entry > stop else 0,
            'rr2': 0,
            'qty': sizing['qty'] if sizing else 0,
            'notional': sizing['position_notional'] if sizing else 0,
            'risk_amount': sizing['risk_amount'] if sizing else 0,
            'size_formula': sizing['formula'] if sizing else '',
            'risk_note': 'spot conservative',
            'holding': 'multi-day',
            'cancel_condition': 'price closes below 4h support',
            'reason': 'spot trend + liquidity',
        }


class ArbAgent(BaseDirectionalAgent):
    name = 'arb'
    direction = 'ARBITRAGE'

    def matches(self, row):
        # live arbitrage: check prices across exchanges for the same symbol
        sym = row['symbol']
        try:
            p_bin = get_price('binance', sym)
            p_byb = get_price('bybit', sym)
            p_mex = get_price('mexc', sym)
        except Exception:
            return False

        prices = [("binance", p_bin), ("bybit", p_byb), ("mexc", p_mex)]
        prices = [p for p in prices if p[1] is not None]
        if len(prices) < 2:
            return False
        prices_sorted = sorted(prices, key=lambda x: x[1])
        low_name, low_p = prices_sorted[0]
        high_name, high_p = prices_sorted[-1]
        spread = (high_p - low_p) / low_p if low_p else 0.0

        # estimate practical profit after fees + slippage using a small notional
        try:
            desired_notional = min(10_000, max(2_000, int(row.get('quote_volume', 0) * 0.001)))
            base_qty = desired_notional / low_p if low_p else 0
            book_buy = get_order_book(low_name, sym, limit=50)
            book_sell = get_order_book(high_name, sym, limit=50)
            if not book_buy or not book_sell:
                return False
            slippage_buy = estimate_slippage(book_buy.get('asks', []), base_qty, reference_price=low_p)
            slippage_sell = estimate_slippage(book_sell.get('bids', []), base_qty, reference_price=high_p)
            # if insufficient depth, skip
            if slippage_buy is None or slippage_sell is None:
                return False
            taker_fee = 0.0004  # default taker fee per side (0.04%)
            fees_total = taker_fee * 2
            effective_profit = spread - fees_total - abs(slippage_buy) - abs(slippage_sell)
        except Exception:
            return False

        # require a minimum practical profit (e.g., 0.4%) and some liquidity
        return effective_profit >= 0.004 and row.get('quote_volume', 0) > 5_000_000

    def build_signal(self, row, macro, sizer):
        sym = row['symbol']
        p_bin = get_price('binance', sym)
        p_byb = get_price('bybit', sym)
        p_mex = get_price('mexc', sym)
        prices = [("binance", p_bin), ("bybit", p_byb), ("mexc", p_mex)]
        prices = [p for p in prices if p[1] is not None]
        if len(prices) < 2:
            return None
        prices_sorted = sorted(prices, key=lambda x: x[1])
        buy_ex, buy_p = prices_sorted[0]
        sell_ex, sell_p = prices_sorted[-1]
        spread = (sell_p - buy_p) / buy_p if buy_p else 0.0
        entry = buy_p
        stop = entry * 0.995
        # estimate slippage and fees for suggested notional
        desired_notional = min(10_000, max(2_000, int(row.get('quote_volume', 0) * 0.001)))
        base_qty = desired_notional / buy_p if buy_p else 0
        book_buy = get_order_book(buy_ex, sym, limit=50)
        book_sell = get_order_book(sell_ex, sym, limit=50)
        slippage_buy = estimate_slippage(book_buy.get('asks', []), base_qty, reference_price=buy_p) if book_buy else None
        slippage_sell = estimate_slippage(book_sell.get('bids', []), base_qty, reference_price=sell_p) if book_sell else None
        taker_fee = 0.0004
        fees_total = taker_fee * 2
        est_effective = None
        if slippage_buy is not None and slippage_sell is not None:
            est_effective = spread - fees_total - abs(slippage_buy) - abs(slippage_sell)

        sizing = sizer.__class__(account_usdt=sizer.account_usdt, risk_pct=0.005, leverage=1).size(entry, stop)

        return {
            'symbol': sym,
            'category': row.get('category', 'alt'),
            'direction': 'ARB',
            'score': row['score'],
            'mode': 'arb',
            'buy_exchange': buy_ex,
            'sell_exchange': sell_ex,
            'buy_price': buy_p,
            'sell_price': sell_p,
            'spread': spread,
            'est_slippage_buy': slippage_buy,
            'est_slippage_sell': slippage_sell,
            'est_fees': fees_total,
            'est_effective_profit': est_effective,
            'entry_low': entry,
            'entry_high': entry,
            'stop': stop,
            'tp1': sell_p,
            'tp2': sell_p * 1.001,
            'qty': sizing['qty'] if sizing else 0,
            'notional': sizing['position_notional'] if sizing else 0,
            'risk_amount': sizing['risk_amount'] if sizing else 0,
            'size_formula': sizing['formula'] if sizing else '',
            'risk_note': 'arb small allocation; account for fees and slippage',
            'holding': 'minutes',
            'cancel_condition': 'exchange liquidity changes or price convergence',
            'reason': f'arbitrage {buy_ex}->{sell_ex} spread {spread:.3%}',
        }


class OptionsAgent(BaseDirectionalAgent):
    name = 'options'
    direction = 'OPTIONS'

    def matches(self, row):
        # placeholder: flag when funding extreme or high implied move suspected
        return abs(row.get('funding', 0.0)) >= 0.05 or abs(row.get('pct4h', 0)) >= 8

    def build_signal(self, row, macro, sizer):
        # try to fetch ATM IV and include in the alert
        iv = get_options_iv(row['symbol'])
        note = 'options alert: extreme funding or move'
        if iv:
            note = f'options alert: ATM IV ~ {iv:.2f}'

        return {
            'symbol': row['symbol'],
            'category': row.get('category', 'alt'),
            'direction': 'OPTIONS_ALERT',
            'score': row['score'],
            'mode': 'options',
            'entry_low': row['price'],
            'entry_high': row['price'],
            'stop': row['price'],
            'tp1': row['price'],
            'tp2': row['price'],
            'qty': 0,
            'notional': 0,
            'risk_amount': 0,
            'size_formula': '',
            'risk_note': 'options: use IV and chain to size',
            'holding': 'short-term',
            'cancel_condition': 'no options data or illiquid chain',
            'reason': note,
            'atm_iv': iv,
        }


class MoonshotAgent(BaseDirectionalAgent):
    name = 'moonshot'
    direction = 'MOONSHOT'

    def matches(self, row):
        # target explosive moves: low liquidity / low price tokens with extreme recent spikes
        low_notional = row['oi_notional'] < 10_000_000
        low_price = row['price'] < 1.0
        huge_spike = row['vol_spike'] >= 3.0 or abs(row['pct15']) >= 20 or abs(row.get('pct5m', 0)) >= 10
        meme_flag = row.get('category') == 'meme'
        return (huge_spike and (low_notional or low_price or meme_flag))

    def build_signal(self, row, macro, sizer):
        entry = row['price']
        atr = row.get('atr5', row.get('atr15', 0.0))
        stop = max(0.0, entry - max(atr * 0.8, entry * 0.05))
        # speculative targets: 5x and 10x (highly speculative)
        tp1 = entry * 5.0
        tp2 = entry * 10.0
        # tiny risk allocation
        sizing = sizer.__class__(account_usdt=sizer.account_usdt, risk_pct=0.002, leverage=1).size(entry, stop)

        return {
            'symbol': row['symbol'],
            'category': row['category'],
            'direction': self.direction,
            'score': row['score'],
            'mode': 'futures/spot-hybrid',
            'leverage': 1,
            'entry_low': entry,
            'entry_high': entry,
            'stop': stop,
            'tp1': tp1,
            'tp2': tp2,
            'rr1': (tp1 - entry) / (entry - stop) if entry > stop and stop > 0 else 0,
            'rr2': (tp2 - entry) / (entry - stop) if entry > stop and stop > 0 else 0,
            'qty': sizing['qty'] if sizing else 0,
            'notional': sizing['position_notional'] if sizing else 0,
            'risk_amount': sizing['risk_amount'] if sizing else 0,
            'size_formula': sizing['formula'] if sizing else '',
            'risk_note': 'highly speculative; tiny allocation only',
            'holding': 'swing / lottery',
            'cancel_condition': 'sudden reversal / news negative',
            'reason': 'low liquidity + extreme spike / meme pattern',
        }


def print_section(title, lines):
    print('=' * 72)
    print(title)
    print('=' * 72)
    for line in lines:
        if line is None:
            continue
        text = line if isinstance(line, str) else str(line)
        # sanitize for consoles with limited encodings
        try:
            print(text)
        except UnicodeEncodeError:
            print(text.encode('ascii', 'replace').decode('ascii'))
    print()


def run_agents(account_usdt=DEFAULT_ACCOUNT_USDT):
    rows = scan_market()
    macro = MacroContext(rows)
    long_agent = LongAgent()
    short_agent = ShortAgent()
    spot_agent = SpotAgent()
    arb_agent = ArbAgent()

    long_signals = long_agent.evaluate(rows, macro, account_usdt=account_usdt)
    short_signals = short_agent.evaluate(rows, macro, account_usdt=account_usdt)
    spot_signals = spot_agent.evaluate(rows, macro, account_usdt=account_usdt)
    arb_signals = arb_agent.evaluate(rows, macro, account_usdt=account_usdt)

    print('TIME', datetime.now(timezone.utc).isoformat())
    print('SOURCE: directional_binance_agents')
    print()
    print_section('MACRO CONTEXT', [macro.summary_text])

    if not rows:
        print('No market candidates available.')
        return

    print_section('PRIORITY UNIVERSE', [f"Top {min(len(rows), MAX_CANDIDATES)} candidates by score: {', '.join(r['symbol'] for r in rows[:MAX_CANDIDATES])}"])
    print_section('LONG SIGNALS', [long_agent.format_signal(s) for s in long_signals] if long_signals else ['No long signals at this time.'])
    print_section('SHORT SIGNALS', [short_agent.format_signal(s) for s in short_signals] if short_signals else ['No short signals at this time.'])
    print_section('SPOT SIGNALS', [spot_agent.format_signal(s) for s in spot_signals] if spot_signals else ['No spot signals at this time.'])
    print_section('ARB SIGNALS', [arb_agent.format_signal(s) for s in arb_signals] if arb_signals else ['No arb signals at this time.'])


if __name__ == '__main__':
    run_agents()
