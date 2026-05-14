import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("healthcheck")

BASE = Path(__file__).parent


def check_bot() -> bool:
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq pythonw.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=10,
        )
        return "pythonw" in out.stdout
    except Exception as exc:
        logger.warning("bot check: %s", exc)
        return False


def check_recent_log(hours: int = 3) -> bool:
    log_dir = BASE / "logs"
    if not log_dir.exists():
        logger.warning("logs dir missing")
        return False
    logs = sorted(log_dir.glob("agents_*.log"))
    if not logs:
        logger.warning("no agent logs found")
        return False
    age = time.time() - logs[-1].stat().st_mtime
    recent = age < hours * 3600
    if not recent:
        logger.warning("last log %.1fh ago", age / 3600)
    return recent


def check_signals() -> bool:
    path = BASE / "signals_log.jsonl"
    if not path.exists():
        logger.warning("signals_log.jsonl missing")
        return False
    count = len(path.read_text(encoding="utf-8").strip().split("\n"))
    logger.info("signals: %d", count)
    return True


def main() -> int:
    bot_ok = check_bot()
    log_ok = check_recent_log()
    sig_ok = check_signals()

    status = (
        f"[{datetime.now(timezone.utc).isoformat()}] "
        f"bot={'OK' if bot_ok else 'FAIL'} "
        f"logs={'OK' if log_ok else 'FAIL'} "
        f"signals={'OK' if sig_ok else 'FAIL'}"
    )
    print(status)

    all_ok = bot_ok and log_ok and sig_ok
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
