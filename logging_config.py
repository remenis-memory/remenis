import logging
import re

class StreamSanitizingFormatter(logging.Formatter):
    """Sanitizes terminal output for live streaming honeypot logs."""

    PATTERNS = [
        (r"/home/[a-zA-Z0-9_-]+", "/home/[REDACTED_USER]"),
        (r"sk-[a-zA-Z0-9_-]{20,}", "[REDACTED_API_KEY]"),
        (r"ghp_[a-zA-Z0-9]{36}", "[REDACTED_GITHUB_TOKEN]"),
        (r"0x[a-fA-F0-9]{8,16}", "[RING_0_PTR_BLOCKED]"),
    ]

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        sanitized = original
        for pattern, replacement in self.PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

def setup_stream_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(
        StreamSanitizingFormatter("[%(asctime)s] [%(levelname)s] %(message)s")
    )
    logger = logging.getLogger("remenis")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
