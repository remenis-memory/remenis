from datetime import datetime, timedelta, timezone
from scoring import DeterministicScorer

scorer = DeterministicScorer(decay_lambda=0.01)
now = datetime.now(timezone.utc)

# Test cases comparing identical vector similarity across different ages and importance levels
memories = [
    {"text": "Recent low-importance fact", "similarity": 0.85, "age_hours": 1, "importance": 1.0},
    {"text": "Old high-importance fact", "similarity": 0.85, "age_hours": 100, "importance": 2.0},
    {"text": "Old low-importance fact", "similarity": 0.85, "age_hours": 100, "importance": 1.0},
]

print("--- RUNNING DETERMINISTIC SCORING TESTS ---")
for m in memories:
    ts = now - timedelta(hours=m["age_hours"])
    score = scorer.calculate_score(
        similarity=m["similarity"],
        timestamp=ts,
        importance=m["importance"],
        now=now
    )
    print(f"📊 [{score:.4f}] Memory: '{m['text']}' (Age: {m['age_hours']}h | Importance: {m['importance']})")
