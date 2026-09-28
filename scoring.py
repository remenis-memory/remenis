import math
from datetime import datetime, timezone

class DeterministicScorer:
    def __init__(self, decay_lambda: float = 0.001):
        # decay_lambda controls how fast older memories drop in rank over time
        self.decay_lambda = decay_lambda

    def calculate_score(
        self, 
        similarity: float, 
        timestamp: datetime, 
        importance: float = 1.0, 
        now: datetime = None
    ) -> float:
        """
        Calculates a deterministic memory retrieval score based on vector similarity,
        time decay, and human/system assigned importance weight.
        """
        if now is None:
            now = datetime.now(timezone.utc)
            
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # Calculate time difference in hours
        delta_seconds = max(0, (now - timestamp).total_seconds())
        delta_hours = delta_seconds / 3600.0

        # Time decay multiplier: 1 / (1 + lambda * delta_hours)
        recency_factor = 1.0 / (1.0 + (self.decay_lambda * delta_hours))

        # Final Score calculation
        final_score = similarity * recency_factor * importance
        return round(final_score, 6)

if __name__ == "__main__":
    scorer = DeterministicScorer()
    print("Deterministic Scorer initialized.")
