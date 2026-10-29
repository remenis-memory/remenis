import time
from typing import List, Dict, Any

class MemoryRetriever:
    """Handles semantic retrieval with time-decay entropy scoring to keep token usage lean."""
    def __init__(self, decay_lambda: float = 0.01):
        # Lambda controls how fast old memories lose weight over time (seconds/hours)
        self.decay_lambda = decay_lambda

    def compute_decayed_score(self, base_similarity: float, timestamp: float) -> float:
        """Applies exponential time-decay to a similarity score based on its age."""
        age_seconds = max(0.0, time.time() - timestamp)
        # Exponential decay factor: e^(-lambda * age)
        import math
        decay_factor = math.exp(-self.decay_lambda * (age_seconds / 3600.0)) # Decaying per hour
        return base_similarity * decay_factor

    def rank_memories(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranks retrieved memory frames by combining semantic similarity and time-decay."""
        ranked = []
        for cand in candidates:
            base_sim = cand.get("similarity", 1.0)
            timestamp = cand.get("timestamp", time.time())
            decayed_score = self.compute_decayed_score(base_sim, timestamp)
            
            cand_copy = dict(cand)
            cand_copy["decayed_score"] = decayed_score
            ranked.append(cand_copy)
            
        # Sort descending by final decayed score
        ranked.sort(key=lambda x: x["decayed_score"], reverse=True)
        return ranked
