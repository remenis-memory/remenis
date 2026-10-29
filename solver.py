import math

class MemorySolver:
    def __init__(self, decay_lambda=0.05):
        self.decay_lambda = decay_lambda

    def evaluate_and_rank(self, memories: list) -> list:
        current_time = max([m.get('timestamp', 0) for m in memories]) if memories else 0
        scored = []
        for mem in memories:
            age_seconds = current_time - mem.get('timestamp', current_time)
            age_days = age_seconds / 86400.0
            weight = math.exp(-self.decay_lambda * age_days)
            scored.append({
                "content": mem['content'],
                "score": weight
            })
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored
