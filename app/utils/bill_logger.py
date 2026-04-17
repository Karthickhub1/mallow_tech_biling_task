import logging
from datetime import datetime
from pathlib import Path

_loggers: dict[str, logging.Logger] = {}


def get_bill_logger() -> logging.Logger:
    """Return a logger that writes to logs/generate_bill/YYYY/MM/DD.log."""
    now = datetime.now()
    date_key = now.strftime("%Y-%m-%d")

    cached = _loggers.get(date_key)
    if cached is not None:
        return cached

    log_dir = Path("logs") / "generate_bill" / now.strftime("%Y") / now.strftime("%m")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{now.strftime('%d')}.log"

    logger = logging.getLogger(f"generate_bill.{date_key}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logger.addHandler(handler)

    _loggers[date_key] = logger
    return logger
