import os
import re

POINTER_REGEX = re.compile(r"0x[0-9a-fA-F]{8,16}")
# Added support for sk-proj-, sk-admin-, standard sk-, ghp_, and ENV_VAR assignments
ENV_KEY_REGEX = re.compile(r"(sk-(?:proj-|admin-)?[a-zA-Z0-9_-]{20,}|ghp_[a-zA-Z0-9]{36}|[A-Z0-9_]{10,}=)")

class RingContextGuard:
    def __init__(self, allowed_env_vars: list[str] = None):
        """
        Creates an isolated environment view for Ring-2 processes.
        """
        self.allowed_vars = allowed_env_vars or ["PATH", "LANG"]

    def get_isolated_env(self) -> dict:
        """
        Returns a stripped environment dictionary containing ONLY safe execution variables.
        Ring-0 secret keys, database paths, and API tokens are omitted.
        """
        return {
            key: val for key, val in os.environ.items()
            if key in self.allowed_vars
        }

    def sanitize_output(self, response_text: str) -> str:
        """
        Redacts any raw memory addresses or leaked environment patterns
        from the output string before sending to client/stream.
        """
        clean_text = POINTER_REGEX.sub("[RING_0_PTR_BLOCKED]", response_text)
        clean_text = ENV_KEY_REGEX.sub("[RING_0_ENV_BLOCKED]", clean_text)
        return clean_text
