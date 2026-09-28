import json
import re
from pathlib import Path

class SecurityViolationError(Exception):
    """Raised when a memory payload violates defined guardrails."""
    pass

class GuardrailEngine:
    def __init__(self, config_path="guardrails.json"):
        self.config_path = Path(config_path)
        self.rules = self._load_rules()

    def _load_rules(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Guardrails file missing: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def validate_memory(self, fact_text: str, category: str = "general") -> bool:
        """
        Inspects fact_text against rules.
        Returns True if clean, raises SecurityViolationError if unsafe.
        """
        # 1. Category Check
        if category in self.rules.get("blocked_categories", []):
            raise SecurityViolationError(
                f"[BLOCK] Category '{category}' is restricted by state isolation rules."
            )

        # 2. Keyword Check
        for kw in self.rules.get("blocked_keywords", []):
            if kw.lower() in fact_text.lower():
                raise SecurityViolationError(
                    f"[BLOCK] Memory contains restricted trigger phrase: '{kw}'"
                )

        # 3. Regex Pattern Check (Code execution / API Keys / Password patterns)
        for pattern in self.rules.get("forbidden_patterns", []):
            if re.search(pattern, fact_text):
                raise SecurityViolationError(
                    f"[BLOCK] Memory pattern matches forbidden security rule: '{pattern}'"
                )

        return True

if __name__ == "__main__":
    # Quick sanity test
    engine = GuardrailEngine()
    print("Guardrail Engine Initialized Successfully.")
