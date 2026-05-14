from datetime import datetime, timezone

from fastapi import FastAPI

from deep_binance_analysis import scan_market, get_macro_context
from directional_binance_agents import (
    LongAgent, ShortAgent, SpotAgent, ArbAgent, OptionsAgent, MoonshotAgent,
    run_agents,
)

app = FastAPI(title="Hermes Foundation API", version="0.2.0")


@app.get("/health")
def health():
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}


@app.get("/scan")
def scan(limit: int = 15):
    rows = scan_market()[:limit]
    macro = get_macro_context(rows) if rows else {}
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "macro": macro,
        "candidates": [
            {
                "symbol": r["symbol"],
                "score": round(r["score"], 1),
                "price": r["price"],
                "trend_4h": r["trend_4h"],
                "trend_1h": r["trend_1h"],
                "vol_spike": round(r["vol_spike"], 2),
                "oi_notional_m": round(r["oi_notional"] / 1e6, 1),
                "funding": round(r["funding"], 6),
            }
            for r in rows
        ],
    }


@app.get("/signals")
def signals(account_usdt: float = 10_000):
    rows = scan_market()
    macro = get_macro_context(rows) if rows else {}
    result = {"ts": datetime.now(timezone.utc).isoformat(), "macro": macro, "signals": {}}

    agents = {
        "long": LongAgent(),
        "short": ShortAgent(),
        "spot": SpotAgent(),
        "arb": ArbAgent(),
    }

    for name, agent in agents.items():
        sigs = agent.evaluate(rows, macro, account_usdt=account_usdt)
        result["signals"][name] = [
            {
                "symbol": s["symbol"],
                "direction": s["direction"],
                "entry_low": s["entry_low"],
                "entry_high": s["entry_high"],
                "stop": s["stop"],
                "tp1": s["tp1"],
                "tp2": s["tp2"],
                "rr1": round(s.get("rr1", 0), 2),
                "reason": s.get("reason", ""),
                "risk_note": s.get("risk_note", ""),
            }
            for s in sigs
        ]

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
