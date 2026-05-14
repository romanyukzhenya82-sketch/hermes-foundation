import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from deep_binance_analysis import scan_market, get_macro_context
from directional_binance_agents import (
    LongAgent, ShortAgent, SpotAgent, ArbAgent,
    DEFAULT_ACCOUNT_USDT,
)
from exchange_prices import get_price
from trade_brief import print_brief

logger = logging.getLogger(__name__)

API_BASE = "https://api.telegram.org/bot{token}"
POLL_INTERVAL = 5
AUTO_ALERT_INTERVAL = 3600

_dotenv_path = Path(__file__).parent / ".env"
if _dotenv_path.exists():
    with open(_dotenv_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID: int | None = None
_last_auto_ts: float = 0.0

_known_commands = """
/scan — top candidates
/signals — Long/Short/Spot/Arb signals
/brief SYMBOL — trade brief for symbol (e.g. /brief BTCUSDT)
/evaluate — show evaluation summary
/help — this message
"""


def _api(method: str, payload: dict | None = None) -> dict[str, Any] | None:
    if not BOT_TOKEN:
        return None
    try:
        r = requests.post(
            API_BASE.format(token=BOT_TOKEN) + f"/{method}",
            json=payload or {},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        logger.debug("telegram api error %s: %s", method, exc)
        return None


def send_message(text: str, chat_id: int | None = None) -> None:
    cid = chat_id or CHAT_ID
    if not cid or not BOT_TOKEN:
        return
    _api("sendMessage", {"chat_id": cid, "text": text, "parse_mode": "HTML"})


def _cmd_start(chat_id: int) -> None:
    global CHAT_ID
    CHAT_ID = chat_id
    send_message(
        f"Hermes Foundation active.\n{_known_commands}", chat_id=chat_id
    )


def _cmd_scan() -> str:
    rows = scan_market()[:10]
    if not rows:
        return "No candidates."
    macro = get_macro_context(rows)
    lines = [
        f"<b>MACRO:</b> {macro.get('summary', '')}",
        "",
        "<b>TOP 10:</b>",
        "sym score vs OI$M fund trend4h",
    ]
    for r in rows:
        lines.append(
            f"{r['symbol']} {r['score']:.0f} {r['vol_spike']:.1f}x "
            f"{r['oi_notional']/1e6:.0f} {r['funding']:.4f}% {r['trend_4h']}"
        )
    return "\n".join(lines)


def _cmd_signals() -> str:
    rows = scan_market()
    if not rows:
        return "No market data."
    macro = get_macro_context(rows)

    agents: dict[str, Any] = {
        "LONG": LongAgent(),
        "SHORT": ShortAgent(),
        "SPOT": SpotAgent(),
        "ARB": ArbAgent(),
    }

    out = [f"<b>Signals — {macro.get('regime', '?')}</b>", ""]
    any_signal = False
    for name, agent in agents.items():
        sigs = agent.evaluate(rows, macro, account_usdt=DEFAULT_ACCOUNT_USDT)
        if not sigs:
            continue
        any_signal = True
        for s in sigs[:3]:
            rr = s.get("rr1", 0) or 0
            out.append(
                f"{s['symbol']} {s['direction']} "
                f"entry={s['entry_low']:.6f} stop={s['stop']:.6f} "
                f"tp1={s['tp1']:.6f} rr={rr:.1f}"
            )
        out.append("")

    if not any_signal:
        out.append("No actionable signals.")
    return "\n".join(out)


def _cmd_brief(symbol: str) -> str:
    try:
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            print_brief(symbol)
        text = buf.getvalue()
        return f"<pre>{text[:3000]}</pre>"
    except Exception as exc:
        return f"Brief failed: {exc}"


def _cmd_evaluate() -> str:
    from evaluate_signals import load_log, group_by, summarise_group

    records = load_log()
    if not records:
        return "No evaluated signals yet."
    closed = [
        r
        for r in records
        if r.get("outcome") and r["outcome"] not in ("OPEN", None, "DATA_ERROR", "UNKNOWN_DIR")
    ]
    if not closed:
        return "No closed signals."

    overall = summarise_group("", closed)
    if not overall:
        return "No data."
    return (
        f"<b>Evaluation</b> ({overall['closed']} closed)\n"
        f"Winrate: {overall['winrate_pct']}%\n"
        f"Expectancy: {overall['expectancy_R']}R\n"
        f"Profit Factor: {overall['profit_factor']}\n"
        f"Avg hold: {overall['avg_hold_bars']} bars"
    )


def _dispatch(text: str, chat_id: int) -> None:
    text = text.strip()
    if text == "/start":
        return _cmd_start(chat_id)
    if text == "/scan":
        return send_message(_cmd_scan())
    if text == "/signals":
        return send_message(_cmd_signals())
    if text == "/evaluate":
        return send_message(_cmd_evaluate())
    if text == "/help":
        return send_message(_known_commands)
    if text.startswith("/brief "):
        sym = text.split(" ", 1)[1].strip().upper()
        return send_message(_cmd_brief(sym))
    if text.startswith("/"):
        return send_message(f"Unknown: {text}\n{_known_commands}")


def _auto_alert() -> None:
    global _last_auto_ts
    now = time.time()
    if now - _last_auto_ts < AUTO_ALERT_INTERVAL:
        return
    _last_auto_ts = now
    text = _cmd_signals()
    if "No actionable" not in text:
        send_message(text)


def poll() -> None:
    offset = 0
    while True:
        try:
            updates = _api("getUpdates", {"offset": offset, "timeout": 30})
            if updates and updates.get("ok") and updates.get("result"):
                for upd in updates["result"]:
                    offset = upd["update_id"] + 1
                    msg = upd.get("message") or upd.get("callback_query", {}).get("message", {})
                    text = msg.get("text", "")
                    cid = msg.get("chat", {}).get("id")
                    if cid:
                        _dispatch(text, cid)
            _auto_alert()
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            break
        except Exception as exc:
            logger.debug("poll error: %s", exc)
            time.sleep(POLL_INTERVAL * 2)


def main() -> None:
    if not BOT_TOKEN:
        print("Set TELEGRAM_BOT_TOKEN env var")
        return
    print(f"Bot polling... chat_id={CHAT_ID}")
    poll()


if __name__ == "__main__":
    main()
