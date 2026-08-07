import re
from typing import List, Dict, Any

class FactExtractor:
    def __init__(self):
        # Basic key patterns to identify facts and clean filler words
        self.filler_patterns = [
            r"^(i think|i believe|just so you know|please note that)\s+",
            r"\b(um|uh|like)\b"
        ]

    def extract_facts(self, raw_text: str) -> List[str]:
        """Strips noise and splits text into structured core facts."""
        cleaned = raw_text.strip()
        for pattern in self.filler_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        
        # Split compound sentences into distinct facts
        sentences = [s.strip() for s in re.split(r'[.;!]', cleaned) if s.strip()]
        return sentences if sentences else [raw_text.strip()]

    def resolve_conflicts(self, new_fact: str, existing_memories: List[Dict[str, Any]]) -> List[int]:
        """
        Checks if a new fact contradicts existing memories.
        Returns a list of memory IDs that should be archived or overwritten.
        """
        conflicting_ids = []
        new_words = set(new_fact.lower().split())

        for mem in existing_memories:
            existing_words = set(mem['content'].lower().split())
            # Overlap threshold check for subject/topic collision
            overlap = new_words.intersection(existing_words)
            if len(overlap) >= 3 and ("not" in new_words or "prefer" in new_words or "instead" in new_words):
                conflicting_ids.append(mem['id'])

        return conflicting_ids

