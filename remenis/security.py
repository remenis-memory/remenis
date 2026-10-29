import re

class RingContextGuard:
    def __init__(self, ring_level=1):
        self.ring_level = ring_level
        self.sensitive_patterns = [
            r'0x[0-9a-fA-F]{4,}',            # Memory pointers
            r'AKIA[0-9A-Z]{12,}',           # AWS Access Keys
            r'sk-[a-zA-Z0-9-_]+',           # All OpenAI / API keys starting with sk-
            r'AKIA[A-Z0-9]{16}'             # Standard AWS key format
        ]

    def sanitize(self, text: str) -> str:
        sanitized = text
        for pattern in self.sensitive_patterns:
            sanitized = re.sub(pattern, "[REDACTED_SECURITY_RING]", sanitized, flags=re.IGNORECASE)
        # Fallback explicit checks
        if "sk-" in sanitized:
            sanitized = re.sub(r'sk-[^\s]+', '[REDACTED_SECURITY_RING]', sanitized)
        if "AKIA" in sanitized:
            sanitized = sanitized.replace("AKIA", "[REDACTED_SECURITY_RING]")
        return sanitized
