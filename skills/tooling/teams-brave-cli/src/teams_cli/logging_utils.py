from __future__ import annotations

import logging
import re
import stat
from logging.handlers import RotatingFileHandler
from pathlib import Path

from teams_cli.config import LOG_BACKUP_COUNT, LOG_MAX_BYTES

LOGGER_NAME = "teams_cli"
LOG_DIR = Path.home() / ".config" / "teams-cli" / "logs"
LOG_FILE = LOG_DIR / "teams-cli.log"

_SECRET_PATTERN = re.compile(
    r"(?i)(skypetoken|authtoken|authorization|authentication|access_token|"
    r"refresh_token|client_secret|password)\s*[:=]\s*[^\s,;]+"
)
_JWT_PATTERN = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")


def redact_credentials(message: str) -> str:
    """Remove common credential formats from a log message."""
    redacted = _SECRET_PATTERN.sub(lambda match: f"{match.group(1)}=[REDACTED]", message)
    return _JWT_PATTERN.sub("[REDACTED_JWT]", redacted)


class SafeFormatter(logging.Formatter):
    """Format records after removing credential-shaped values."""

    def format(self, record: logging.LogRecord) -> str:
        return redact_credentials(super().format(record))


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger in the Teams CLI namespace."""
    return logging.getLogger(f"{LOGGER_NAME}.{name}" if name else LOGGER_NAME)


def configure_logging(verbose: bool = False) -> logging.Logger:
    """Configure persistent file logging and warning-level console logging."""
    logger = get_logger()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    formatter = SafeFormatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    persistent_handler_added = False
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
        LOG_DIR.chmod(stat.S_IRWXU)
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        LOG_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)
        persistent_handler_added = True
    except OSError as error:
        logger.warning("Persistent log setup failed: %s", error)

    if not persistent_handler_added:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    logger.info("Logging configured; persistent_log=%s", LOG_FILE)
    return logger
